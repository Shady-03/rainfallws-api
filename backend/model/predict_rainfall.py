# backend/model/predict_rainfall.py
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import numpy as np
import pandas as pd
import joblib
import difflib
import os
from keras.models import load_model

# Get base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR)
# Robust absolute path regardless of how the file is imported
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'Rain_data.csv')




def predict_next_rainfall(subdivision: str):
    subdivision = subdivision.strip().upper()
    model_name = subdivision.replace(' ', '_')

    model_path = os.path.join(MODEL_DIR, f"{model_name}_lstm.keras")
    scaler_path = os.path.join(MODEL_DIR, f"{model_name}_scaler.pkl")

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Model or scaler not found for subdivision: {subdivision}")

    # Load model and scaler
    model = load_model(model_path)
    scaler = joblib.load(scaler_path)

    # Load rainfall data
    df = pd.read_csv(DATA_PATH)
    df["SUBDIVISION"] = df["SUBDIVISION"].str.strip().str.upper()

    # Match closest subdivision name
    all_subdivisions = df["SUBDIVISION"].unique()
    closest = difflib.get_close_matches(subdivision, all_subdivisions, n=1, cutoff=0.6)
    if not closest:
        raise ValueError(f"Subdivision '{subdivision}' not found")

    matched = closest[0]
    data = df[df["SUBDIVISION"] == matched].sort_values("YEAR")
    last_5_values = data["ANNUAL"].values[-5:]

    if len(last_5_values) < 5:
        raise ValueError("Not enough data for prediction")

    # Prepare input for prediction
    scaled_input = scaler.transform(np.array(last_5_values).reshape(-1, 1))
    X_input = scaled_input.reshape(1, 5, 1)
    pred_scaled = model.predict(X_input)
    prediction = float(scaler.inverse_transform(pred_scaled)[0][0])

    return round(prediction, 2)


if __name__ == "__main__":
    test_subdivision = "HARYANA_DELHI_&_CHANDIGARH"  # Example subdivision
    try:
        result = predict_next_rainfall(test_subdivision)
        print(f"Predicted rainfall for {test_subdivision}: {result} mm")
    except Exception as e:
        print("❌", str(e))
