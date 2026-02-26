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

# ensure a local copy of cluster centers for easier access
import shutil

local_centers = Path(__file__).parent / "cluster_centers.csv"
if not local_centers.exists():
    # try to copy from project data folder
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    src_centers = PROJECT_ROOT / "data" / "processed" / "cluster_centers.csv"
    if src_centers.exists():
        try:
            shutil.copy(src_centers, local_centers)
        except Exception as e:
            st.warning(f"Unable to copy cluster_centers.csv to app directory: {e}")

# Load model and config
@st.cache_resource
def load_model():
    APP_ROOT = Path(__file__).resolve().parents[1]

    model_path = APP_ROOT / "models" / "multinomial_logreg_lifestyle_cluster.pkl"
    config_path = APP_ROOT / "models" / "model_config.json"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    predictor = StressPredictor(model_path=str(model_path), config=config)
    return predictor, config

predictor, config = load_model()

# Input section
st.header("Enter Your Lifestyle Information")
st.markdown("Provide the factors used by the clustering model.  All inputs are automatically encoded and scaled before prediction.")

# raw user inputs
sleep_hours = st.number_input("Sleep (hours per day)", min_value=0.0, max_value=24.0, value=7.0, step=0.25)
work_hours = st.number_input("Work (hours per week)", min_value=0.0, max_value=168.0, value=40.0, step=1.0)
physical_hours = st.number_input("Physical Activity (hours per week)", min_value=0.0, max_value=168.0, value=5.0, step=0.5)
social_media = st.number_input("Social Media Usage (hours per day)", min_value=0.0, max_value=24.0, value=2.0, step=0.25)

diet_quality = st.selectbox("Diet Quality", options=["Healthy", "Average", "Unhealthy"])
smoking_habit = st.selectbox("Smoking Habit", options=["Non-Smoker", "Occasional Smoker", "Regular Smoker", "Heavy Smoker"])
alcohol_consumption = st.selectbox("Alcohol Consumption", options=["Non-Drinker", "Social Drinker", "Regular Drinker", "Heavy Drinker"])

# perform prediction
if st.button("Assign Cluster", type="primary"):
    # validate raw inputs
    from src.utils.data_processing import validate_lifestyle_input, encode_and_scale_lifestyle

    raw = {
        "sleep_hours": sleep_hours,
        "work_hours": work_hours,
        "physical_activity_hours": physical_hours,
        "social_media_hours": social_media,
    }
    errors = validate_lifestyle_input(raw)
    if errors:
        for err in errors:
            st.error(err)
    else:
        features = encode_and_scale_lifestyle(
            sleep_hours,
            work_hours,
            physical_hours,
            social_media,
            diet_quality,
            smoking_habit,
            alcohol_consumption,
        )
        # automatically determine nearest cluster using precomputed centers
        from src.utils.data_processing import assign_cluster
        # locate the center CSV by walking upward; handles cases where __file__ is relative
        def find_centers_file(start: Path) -> Path:
            # prefer a copy stored alongside the app
            local = Path(__file__).parent / "cluster_centers.csv"
            if local.exists():
                return local.resolve()
            curr = start
            for _ in range(6):  # avoid infinite loop
                candidate = curr / "data" / "processed" / "cluster_centers.csv"
                if candidate.exists():
                    return candidate.resolve()
                curr = curr.parent
            raise FileNotFoundError("Could not locate cluster_centers.csv in parent directories")

        try:
            base_dir = Path(__file__).parent
            centers_path = find_centers_file(base_dir)
            cluster_id = assign_cluster(features, str(centers_path))
        except FileNotFoundError as e:
            st.error(f"Cluster centers file not found: {e}")
            cluster_id = None
        except Exception as e:
            st.error(f"Error assigning cluster: {e}")
            cluster_id = None

        if cluster_id is not None:
            st.write(f"#### Assigned cluster: **{cluster_id}**")
        else:
            st.warning("Cluster assignment failed.")

        # add cluster value for stress model inputs
        features["Cluster"] = cluster_id
        try:
            prediction = predictor.predict(features)
            st.success(f"**Stress level prediction: {prediction}**")
        except Exception as e:
            st.warning(f"Stress prediction skipped ({e})")

        # optionally display classes if available
        if config and 'classes' in config:
            st.info(f"Classes: {', '.join(config['classes'])}")