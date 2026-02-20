import streamlit as st
from model.predictor import Predictor
from utils.data_processing import prepare_input

def main():
    st.title("Stress Prediction App")
    st.write("This application predicts stress levels based on user input.")

    # User input fields
    user_input = {}
    user_input['feature1'] = st.number_input("Feature 1", min_value=0.0, max_value=100.0)
    user_input['feature2'] = st.number_input("Feature 2", min_value=0.0, max_value=100.0)
    user_input['feature3'] = st.number_input("Feature 3", min_value=0.0, max_value=100.0)

    if st.button("Predict Stress Level"):
        # Prepare input for prediction
        prepared_input = prepare_input(user_input)
        
        # Load model and make prediction
        predictor = Predictor()
        prediction = predictor.predict(prepared_input)

        st.success(f"Predicted Stress Level: {prediction}")

if __name__ == "__main__":
    main()