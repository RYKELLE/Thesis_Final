import numpy as np
import pandas as pd

def preprocess_input(input_data):
    """
    Preprocess raw input data for model prediction
    
    Args:
        input_data (dict): Raw input features
        
    Returns:
        dict: Preprocessed features
    """
    processed = input_data.copy()
    
    # Normalize heart rate (example: 0-200 range)
    if 'heart_rate' in processed:
        processed['heart_rate'] = (processed['heart_rate'] - 60) / 100
    
    # Normalize sleep hours (0-12 range)
    if 'sleep_hours' in processed:
        processed['sleep_hours'] = processed['sleep_hours'] / 12
    
    # Anxiety already 0-10 scale
    # Exercise minutes - normalize if needed
    if 'exercise_mins' in processed:
        processed['exercise_mins'] = processed['exercise_mins'] / 300
    
    return processed

def validate_input(input_data):
    """Validate input data ranges"""
    errors = []
    
    if 'heart_rate' in input_data and not (40 <= input_data['heart_rate'] <= 200):
        errors.append("Heart rate must be between 40-200 bpm")
    
    if 'sleep_hours' in input_data and not (0 <= input_data['sleep_hours'] <= 12):
        errors.append("Sleep hours must be between 0-12")
    
    if 'anxiety_level' in input_data and not (1 <= input_data['anxiety_level'] <= 10):
        errors.append("Anxiety level must be between 1-10")
    
    if 'exercise_mins' in input_data and input_data['exercise_mins'] < 0:
        errors.append("Exercise minutes cannot be negative")
    
    return errors