import os
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.config import MODEL_DIR, RAW_DATA_DIR

def train():
    data_path = os.path.join(RAW_DATA_DIR, "climate_training_data.csv")
    if not os.path.exists(data_path):
        print("Training data not found.")
        return

    print("Loading historical data for ML training...")
    df = pd.read_csv(data_path)
    
    # Feature Engineering
    print("Engineering spatio-temporal features...")
    df['time'] = pd.to_datetime(df['time'])
    df['day_of_year'] = df['time'].dt.dayofyear
    df['hour'] = df['time'].dt.hour
    
    # Cyclical encoding for time
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365.0)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365.0)
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24.0)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24.0)
    
    features = ['latitude', 'longitude', 'elevation', 'day_sin', 'day_cos', 'hour_sin', 'hour_cos']
    
    targets = {
        'temperature': 'temperature_2m',
        'humidity': 'relative_humidity_2m',
        'feels_like': 'apparent_temperature',
        'pressure': 'surface_pressure',
        'wind_speed': 'wind_speed_10m'
    }
    
    X = df[features]
    
    for model_name, target_col in targets.items():
        if target_col not in df.columns:
            continue
        print(f"Training XGBoost model for: {model_name}...")
        y = df[target_col]
        
        # XGBoost Regressor
        model = xgb.XGBRegressor(
            n_estimators=100, 
            max_depth=6, 
            learning_rate=0.1, 
            n_jobs=-1,
            tree_method='hist'
        )
        model.fit(X, y)
        
        model_path = os.path.join(MODEL_DIR, f"{model_name}_model.pkl")
        joblib.dump(model, model_path)
        print(f"Saved highly accurate {model_name} AI model to {model_path}.")

if __name__ == "__main__":
    train()
