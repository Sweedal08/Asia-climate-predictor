import os
import requests
import pandas as pd
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.config import RAW_DATA_DIR

# 5-10 Years of data for a comprehensive set of reference Asian locations to train the generalized model
# We cover varying latitudes, longitudes, and elevations across the continent
REFERENCE_CITIES = [
    (28.6139, 77.2090, 216),  # New Delhi, India
    (39.9042, 116.4074, 44),  # Beijing, China
    (35.6895, 139.6917, 40),  # Tokyo, Japan
    (13.7563, 100.5018, 1),   # Bangkok, Thailand
    (25.2048, 55.2708, 14),   # Dubai, UAE
    (14.5995, 120.9842, 16),  # Manila, Philippines
    (1.3521, 103.8198, 15),   # Singapore
    (-6.2088, 106.8456, 8),   # Jakarta, Indonesia
    (41.3110, 69.2401, 455),  # Tashkent, Uzbekistan
    (35.6892, 51.3890, 1189), # Tehran, Iran
    (47.9200, 106.9200, 1350),# Ulaanbaatar, Mongolia (Cold/High)
    (6.9271, 79.8612, 7),     # Colombo, Sri Lanka (Tropical)
    (31.2304, 121.4737, 4),   # Shanghai, China
    (33.5138, 36.2765, 680),  # Damascus, Syria
    (23.7957, 90.4113, 4)     # Dhaka, Bangladesh
]

def fetch_historical_climate():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365) # 5 years
    
    end_str = end_date.strftime('%Y-%m-%d')
    start_str = start_date.strftime('%Y-%m-%d')
    
    out_file = os.path.join(RAW_DATA_DIR, "climate_training_data.csv")
    if os.path.exists(out_file):
        print("Training data already fetched.")
        return

    print(f"Fetching 5 years of historical climate data from {start_str} to {end_str} for training...")
    
    all_data = []
    
    for lat, lon, elev in REFERENCE_CITIES:
        # Open-Meteo Archive API
        url = (f"https://archive-api.open-meteo.com/v1/archive?"
               f"latitude={lat}&longitude={lon}&start_date={start_str}&end_date={end_str}"
               f"&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,"
               f"surface_pressure,wind_speed_10m"
               f"&timezone=auto")
        print(f"Fetching for Lat: {lat}, Lon: {lon}")
        try:
            r = requests.get(url)
            data = r.json()
            if 'hourly' in data:
                df = pd.DataFrame(data['hourly'])
                df['latitude'] = lat
                df['longitude'] = lon
                df['elevation'] = elev
                all_data.append(df)
            else:
                print(f"No hourly data found for {lat}, {lon}")
        except Exception as e:
            print(f"Failed to fetch for {lat}, {lon}: {e}")
            
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        # Drop rows with NaN
        final_df = final_df.dropna()
        final_df.to_csv(out_file, index=False)
        print(f"Saved training data to {out_file} with {len(final_df)} records.")
    else:
        print("No data fetched.")

if __name__ == "__main__":
    fetch_historical_climate()
