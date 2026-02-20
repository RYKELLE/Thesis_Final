import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model.predictor import StressPredictor

st.set_page_config(page_title="Stress Predictor", layout="wide")

st.title("🧠 Stress Level Prediction")
st.markdown("Predict stress levels using machine learning")

# Load model and config
@st.cache_resource
def load_model():
    model_path = Path(__file__).parent.parent.parent / "models" / "multinomial_logreg_lifestyle_cluster.pkl"
    config_path = Path(__file__).parent.parent.parent / "models" / "model_config.json"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    predictor = StressPredictor(model_path=str(model_path), config=config)
    return predictor, config

predictor, config = load_model()

# Input section
st.header("Enter Your Data")
st.markdown("Provide your lifestyle metrics and cluster assignment")

col1, col2 = st.columns(2)

with col1:
    sleep_hours_scaled = st.slider("Sleep Hours (Scaled)", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
    exercise_mins_scaled = st.slider("Exercise Minutes (Scaled)", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
    water_intake_scaled = st.slider("Water Intake (Scaled)", min_value=0.0, max_value=1.0, value=0.5, step=0.01)

with col2:
    meditation_mins_scaled = st.slider("Meditation Minutes (Scaled)", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
    social_interaction_scaled = st.slider("Social Interaction (Scaled)", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
    work_hours_scaled = st.slider("Work Hours (Scaled)", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
    nutrition_score_scaled = st.slider("Nutrition Score (Scaled)", min_value=0.0, max_value=1.0, value=0.5, step=0.01)

cluster = st.selectbox("Cluster", options=[0, 1, 2, 3])

# Predict button
if st.button("Predict Stress Level", type="primary"):
    input_data = {
        "Sleep_Hours_Scaled": sleep_hours_scaled,
        "Exercise_Minutes_Scaled": exercise_mins_scaled,
        "Water_Intake_Scaled": water_intake_scaled,
        "Meditation_Minutes_Scaled": meditation_mins_scaled,
        "Social_Interaction_Scaled": social_interaction_scaled,
        "Work_Hours_Scaled": work_hours_scaled,
        "Nutrition_Score_Scaled": nutrition_score_scaled,
        "Cluster": cluster
    }
    
    prediction = predictor.predict(input_data)
    
    st.success(f"**Predicted Stress Level: {prediction}**")
    st.info(f"Classes: {', '.join(config['classes'])}")