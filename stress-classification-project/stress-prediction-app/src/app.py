import streamlit as st
from model.predictor import Predictor
from utils.data_processing import prepare_input

def main():
    st.title("Stress Prediction App")
    st.write("A simple interface for assigning a cluster/stress level from lifestyle factors.")
    st.write("_This module is kept for backwards compatibility; the primary entrypoint is `app/streamlit_app.py`._")

    # replicate same fields as the main UI so that alternate imports still work
    sleep_hours = st.number_input("Sleep (hours per day)", min_value=0.0, max_value=24.0, value=7.0, step=0.25)
    work_hours = st.number_input("Work (hours per week)", min_value=0.0, max_value=168.0, value=40.0, step=1.0)
    physical_hours = st.number_input("Physical Activity (hours per week)", min_value=0.0, max_value=168.0, value=5.0, step=0.5)
    social_media = st.number_input("Social Media Usage (hours per day)", min_value=0.0, max_value=24.0, value=2.0, step=0.25)

    diet_quality = st.selectbox("Diet Quality", options=["Healthy", "Average", "Unhealthy"])
    smoking_habit = st.selectbox("Smoking Habit", options=["Non-Smoker", "Occasional Smoker", "Regular Smoker", "Heavy Smoker"])
    alcohol_consumption = st.selectbox("Alcohol Consumption", options=["Non-Drinker", "Social Drinker", "Regular Drinker", "Heavy Drinker"])

    if st.button("Assign Cluster"):
        from utils.data_processing import encode_and_scale_lifestyle, validate_lifestyle_input

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
            predictor = Predictor()
            prediction = predictor.predict(features)
            st.success(f"Model output: {prediction}")

if __name__ == "__main__":
    main()