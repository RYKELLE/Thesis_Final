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


def assign_cluster(features: dict, centers_path: str) -> int:
    """Determine the nearest cluster for a scaled feature dictionary.

    Args:
        features: dictionary containing the seven scaled numeric features
                  (no Cluster key).
        centers_path: path to a CSV file containing cluster center values with
                      the same column names in the same order.

    Returns:
        int: index of the closest cluster (0-based)
    """
    import pandas as pd
    import numpy as np

    # read the csv of cluster centers; propagate FileNotFoundError
    centers = pd.read_csv(centers_path)
    # ensure columns match expectation
    cols = centers.columns.tolist()
    try:
        vec = np.array([features[c] for c in cols])
    except KeyError as ke:
        raise KeyError(f"Feature {ke} missing when computing distances")
    dists = np.linalg.norm(centers.values - vec, axis=1)
    return int(np.argmin(dists))


def encode_and_scale_lifestyle(sleep_hours: float,
                                work_hours: float,
                                physical_activity_hours: float,
                                social_media_hours: float,
                                diet_quality: str,
                                smoking_habit: str,
                                alcohol_consumption: str) -> dict:
    """Encode categorical variables and min‑max scale all inputs as expected by the model.

    Scaling assumptions mirror those used during training.
    """
    features = {
        "Sleep_Hours_Scaled": sleep_hours / 24.0,
        "Work_Hours_Scaled": work_hours / 168.0,
        "Physical_Activity_Hours_Scaled": physical_activity_hours / 168.0,
        "Social_Media_Usage_Scaled": social_media_hours / 24.0,
    }

    diet_map = {"Unhealthy": 0, "Average": 1, "Healthy": 2}
    smoking_map = {
        "Non-Smoker": 0,
        "Occasional Smoker": 1,
        "Regular Smoker": 2,
        "Heavy Smoker": 3,
    }
    alcohol_map = {
        "Non-Drinker": 0,
        "Social Drinker": 1,
        "Regular Drinker": 2,
        "Heavy Drinker": 3,
    }

    features["Diet_Quality_Encoded_Scaled"] = diet_map.get(diet_quality, 0) / 2.0
    features["Smoking_Habit_Encoded_Scaled"] = smoking_map.get(smoking_habit, 0) / 3.0
    features["Alcohol_Consumption_Encoded_Scaled"] = alcohol_map.get(alcohol_consumption, 0) / 3.0

    return features


def validate_lifestyle_input(input_data: dict) -> list:
    """Validate ranges for the lifestyle inputs supplied by the user."""
    errors = []
    if not (0 <= input_data.get("sleep_hours", 0) <= 24):
        errors.append("Sleep hours must be between 0 and 24 per day")
    if not (0 <= input_data.get("work_hours", 0) <= 168):
        errors.append("Work hours must be between 0 and 168 per week")
    if not (0 <= input_data.get("physical_activity_hours", 0) <= 168):
        errors.append("Physical activity hours must be between 0 and 168 per week")
    if not (0 <= input_data.get("social_media_hours", 0) <= 24):
        errors.append("Social media usage must be between 0 and 24 hours per day")
    return errors