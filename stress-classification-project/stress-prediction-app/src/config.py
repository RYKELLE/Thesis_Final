# Configuration settings for the stress prediction application

MODEL_PATH = 'models/stress_model.pkl'
PREDICTION_THRESHOLD = 0.5
INPUT_FEATURES = ['feature1', 'feature2', 'feature3']  # Replace with actual feature names used in the model
OUTPUT_LABELS = ['Low Stress', 'Moderate Stress', 'High Stress']  # Adjust based on model output classes