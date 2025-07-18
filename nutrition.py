

import streamlit as st
from PIL import Image
import openai
import io
import base64
import re
import plotly.express as px

openai.api_key = "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"


st.set_page_config(page_title="SnapNutrition", layout="centered")
st.markdown("""
    <style>
    .card {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.1);
        text-align: center;
        margin-top: 20px;
    }
    .macro-box {
        display: flex;
        justify-content: space-around;
        margin-top: 20px;
        font-size: 16px;
    }
    .macro-box div {
        background: #f4f4f4;
        border-radius: 12px;
        padding: 10px 15px;
        min-width: 80px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍽️ SnapNutrition")
st.caption("Upload or take a picture of your meal. AI will estimate your nutrition instantly.")

# --- Image input ---
method = st.radio("Input method", ["📤 Upload", "📸 Camera"], horizontal=True)
image_input = st.file_uploader("Upload your meal photo", type=["jpg", "jpeg", "png"]) if method == "📤 Upload" else st.camera_input("Take a photo")

if image_input:
    image = Image.open(image_input).convert("RGB")
    st.image(image, caption="Your Meal", use_column_width=True)

    # Convert to base64
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    image_url = f"data:image/png;base64,{img_base64}"

    with st.spinner("Analyzing your meal... 🍱"):
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You're a certified nutritionist. Describe the meal and estimate Calories, Protein (g), Carbs (g), Fats (g), and Fiber (g). Keep it accurate and readable."},
                {"role": "user", "content": [
                    {"type": "text", "text": "Analyze the following meal:"},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]}
            ],
            max_tokens=600
        )

    raw_output = response.choices[0].message.content
    st.success("✅ Analysis complete!")

    # --- Extract + fallback ---
    def extract_macro(label, default=0):
        match = re.search(fr"{label}[^:\d]*[:\-]?\s*(\d+)(?:\s*[-–]\s*(\d+))?", raw_output, re.IGNORECASE)
        if match:
            if match.group(2):
                return round((float(match.group(1)) + float(match.group(2))) / 2, 1)
            return round(float(match.group(1)), 1)
        return default

    calories = extract_macro("calories", 250)
    protein = extract_macro("protein", 10)
    carbs = extract_macro("carbs", 30)
    fats = extract_macro("fat", 10)
    fiber = extract_macro("fiber", 5)

    # --- Creative Card Display ---
    st.markdown(f"""
        <div class="card">
            <h3>Estimated Nutrition</h3>
            <p style="font-size: 28px; margin: 10px 0;"><strong>{calories} kcal</strong></p>
            <div class="macro-box">
                <div><strong>{protein} g</strong><br>Protein</div>
                <div><strong>{carbs} g</strong><br>Carbs</div>
                <div><strong>{fats} g</strong><br>Fats</div>
                <div><strong>{fiber} g</strong><br>Fiber</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- Pie chart ---
    st.markdown("### 🧬 Macro Breakdown")
    fig = px.pie(
        names=["Protein", "Carbs", "Fats", "Fiber"],
        values=[protein, carbs, fats, fiber],
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig, use_container_width=True)

    # Debug output (optional)
    with st.expander("🧠 Full AI Output"):
        st.text(raw_output)
