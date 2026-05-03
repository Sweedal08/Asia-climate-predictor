import os
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.config import MODEL_DIR

class ClimatePredictor:
    def __init__(self):
        self.models = {}
        targets = ['temperature', 'humidity', 'feels_like', 'pressure', 'wind_speed']
        for target in targets:
            model_path = os.path.join(MODEL_DIR, f"{target}_model.pkl")
            if os.path.exists(model_path):
                self.models[target] = joblib.load(model_path)
                
    def predict(self, lat, lon, elev, target_time=None):
        if not self.models:
            return {"error": "Models not trained yet."}
            
        if target_time is None:
            target_time = datetime.now()
            
        day_of_year = target_time.timetuple().tm_yday
        hour = target_time.hour
        
        day_sin = np.sin(2 * np.pi * day_of_year / 365.0)
        day_cos = np.cos(2 * np.pi * day_of_year / 365.0)
        hour_sin = np.sin(2 * np.pi * hour / 24.0)
        hour_cos = np.cos(2 * np.pi * hour / 24.0)
        
        X = pd.DataFrame([{
            'latitude': lat,
            'longitude': lon,
            'elevation': elev,
            'day_sin': day_sin,
            'day_cos': day_cos,
            'hour_sin': hour_sin,
            'hour_cos': hour_cos
        }])
        
        results = {}
        for target, model in self.models.items():
            pred = model.predict(X)[0]
            results[target] = round(float(pred), 2)
            

        
        # UV Index based on temp, time of day and latitude (simplistic curve)
        uv = 0.0
        if 8 <= hour <= 17:
            solar_elev = np.sin(np.pi * (hour - 6) / 12)
            uv = max(0, solar_elev * (results['temperature'] / 3) * (1 - abs(lat)/90))
        results['uv_index'] = round(uv, 1)
        
        # AQI Simulation based on wind (high wind = better AQI)
        base_aqi = 100
        wind_factor = results['wind_speed'] * 2
        
        # Use latitude to add a deterministic modifier
        # so AQI stays exactly the same on refresh for the same location and time
        deterministic_jitter = int((abs(lat) * 10) % 30) - 10
        
        results['aqi'] = max(10, int(base_aqi - wind_factor + deterministic_jitter))
        
        results['weather'] = self._determine_weather(results['temperature'], results['humidity'])
        results['prediction_date'] = target_time.strftime("%Y-%m-%d %H:00")
        
        return results
        
    def _determine_weather(self, temp, humidity):
        if humidity > 85:
            return "Rainy"
        elif humidity > 70:
            return "Cloudy"
        elif temp > 30:
            return "Sunny"
        else:
            return "Clear"
