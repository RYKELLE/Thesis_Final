# Stress Prediction App

This project is a stress prediction application that utilizes a pre-trained machine learning model to predict stress levels based on user input. The application is built using Streamlit, providing an interactive web interface for users.

## Project Structure

```
stress-prediction-app
├── src
│   ├── app.py                # Main entry point of the application
│   ├── model
│   │   └── predictor.py      # Contains the Predictor class for model predictions
│   ├── utils
│   │   └── data_processing.py # Utility functions for data preprocessing
│   └── config.py             # Configuration settings for the application
├── models
│   └── stress_model.pkl       # Serialized pre-trained model for stress prediction
├── requirements.txt           # List of dependencies required to run the application
└── README.md                  # Documentation for the project
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd stress-prediction-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   streamlit run src/app.py
   ```

## Usage Guidelines

- Open the application in your web browser.
- Input the required data in the provided fields.
- Click on the "Predict" button to receive a stress prediction based on your input.

## Overview of Functionality

The application allows users to input various parameters related to their lifestyle and mental health. The `Predictor` class in `src/model/predictor.py` loads the pre-trained model and makes predictions based on the processed input data. The utility functions in `src/utils/data_processing.py` ensure that the input data is cleaned and formatted correctly before prediction.

This project aims to provide users with insights into their stress levels and promote mental well-being through data-driven predictions.