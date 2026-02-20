import joblib
import numpy as np
import pandas as pd
from pathlib import Path

class StressPredictor:
    def __init__(self, model_path, config=None):
        """Load the trained stress prediction model"""
        self.model_path = Path(model_path)
        self.config = config
        self.model = self._load_model()
    
    def _load_model(self):
        """Load joblib model from disk"""
        try:
            model = joblib.load(self.model_path)
            return model
        except FileNotFoundError:
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        except Exception as e:
            raise Exception(f"Error loading model: {str(e)}")
    
    def predict(self, input_data):
        """
        Make prediction on input data
        
        Args:
            input_data (dict): Dictionary with feature keys
            
        Returns:
            str: Stress level prediction (Low, Medium, High)
        """
        try:
            # Create DataFrame from input
            df = pd.DataFrame([input_data])
            
            # Predict
            prediction = self.model.predict(df)
            return prediction[0]
        except Exception as e:
            raise Exception(f"Error making prediction: {str(e)}")