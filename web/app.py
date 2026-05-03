from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
from datetime import datetime, timedelta
from config.config import DB_PATH, DATA_DIR
from src.prediction.predict import ClimatePredictor

app = Flask(__name__)

ADMIN1_MAP = {}
def load_admin1_map():
    map_path = os.path.join(DATA_DIR, "admin1CodesASCII.txt")
    if not os.path.exists(map_path):
        try:
            print("Downloading admin1CodesASCII.txt for state names...")
            r = requests.get("https://download.geonames.org/export/dump/admin1CodesASCII.txt", timeout=10)
            with open(map_path, "wb") as f:
                f.write(r.content)
        except Exception as e:
            print(f"Failed to download state map: {e}")
            
    if os.path.exists(map_path):
        with open(map_path, "r", encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) >= 3:
                    ADMIN1_MAP[parts[0]] = parts[2]

load_admin1_map()

COUNTRY_NAMES = {
    'AF': 'Afghanistan', 'AM': 'Armenia', 'AZ': 'Azerbaijan', 'BH': 'Bahrain', 'BD': 'Bangladesh',
    'BT': 'Bhutan', 'BN': 'Brunei', 'KH': 'Cambodia', 'CN': 'China', 'CY': 'Cyprus',
    'GE': 'Georgia', 'IN': 'India', 'ID': 'Indonesia', 'IR': 'Iran', 'IQ': 'Iraq',
    'IL': 'Israel', 'JP': 'Japan', 'JO': 'Jordan', 'KZ': 'Kazakhstan', 'KP': 'North Korea',
    'KR': 'South Korea', 'KW': 'Kuwait', 'KG': 'Kyrgyzstan', 'LA': 'Laos', 'LB': 'Lebanon',
    'MY': 'Malaysia', 'MV': 'Maldives', 'MN': 'Mongolia', 'MM': 'Myanmar', 'NP': 'Nepal',
    'OM': 'Oman', 'PK': 'Pakistan', 'PH': 'Philippines', 'QA': 'Qatar', 'SA': 'Saudi Arabia',
    'SG': 'Singapore', 'LK': 'Sri Lanka', 'SY': 'Syria', 'TW': 'Taiwan', 'TJ': 'Tajikistan',
    'TH': 'Thailand', 'TR': 'Turkey', 'TM': 'Turkmenistan', 'AE': 'United Arab Emirates',
    'UZ': 'Uzbekistan', 'VN': 'Vietnam', 'YE': 'Yemen', 'MO': 'Macau', 'HK': 'Hong Kong',
    'PS': 'Palestine'
}
predictor = ClimatePredictor()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/countries')
def get_countries():
    try:
        conn = get_db_connection()
        countries = conn.execute("SELECT DISTINCT country_code FROM locations ORDER BY country_code").fetchall()
        conn.close()
        result = []
        for c in countries:
            code = c['country_code']
            result.append({'country_code': code, 'country_name': COUNTRY_NAMES.get(code, code)})
        result.sort(key=lambda x: x['country_name'])
        return jsonify(result)
    except Exception as e:
        return jsonify([])

@app.route('/api/states/<country_code>')
def get_states(country_code):
    conn = get_db_connection()
    states = conn.execute("SELECT DISTINCT admin1_code FROM locations WHERE country_code = ? AND admin1_code != '' ORDER BY admin1_code", (country_code,)).fetchall()
    conn.close()
    
    result = []
    for s in states:
        admin_code = s['admin1_code']
        key = f"{country_code}.{admin_code}"
        state_name = ADMIN1_MAP.get(key, admin_code)
        
        # If it falls back to a raw number, give it a proper label
        if state_name == admin_code and str(state_name).isdigit():
            state_name = f"Region {admin_code}"
            
        result.append({
            'admin1_code': admin_code,
            'state_name': state_name
        })
    result.sort(key=lambda x: x['state_name'])
    return jsonify(result)

@app.route('/api/cities/<country_code>/<state_code>')
def get_cities(country_code, state_code):
    conn = get_db_connection()
    # Limit to 2000 to prevent overwhelming the browser
    cities = conn.execute("SELECT asciiname, geonameid FROM locations WHERE country_code = ? AND admin1_code = ? AND asciiname != '' LIMIT 2000", (country_code, state_code)).fetchall()
    conn.close()
    return jsonify([dict(c) for c in cities])

@app.route('/api/predict', methods=['POST'])
def predict_climate():
    data = request.json
    geonameid = data.get('geonameid')
    
    conn = get_db_connection()
    location = conn.execute("SELECT * FROM locations WHERE geonameid = ?", (geonameid,)).fetchone()
    conn.close()
    
    if not location:
        return jsonify({"error": "Location not found"}), 404
        
    prediction = predictor.predict(location['latitude'], location['longitude'], location['elevation'])
    prediction['city'] = location['asciiname']
    code = location['country_code']
    prediction['country'] = COUNTRY_NAMES.get(code, code)

    
    # Hourly forecast for next 24 hours
    hourly_forecast = []
    now = datetime.now()
    for i in range(1, 25):
        future_time = now + timedelta(hours=i)
        pred = predictor.predict(location['latitude'], location['longitude'], location['elevation'], target_time=future_time)
        hourly_forecast.append(pred)
    prediction['hourly_forecast'] = hourly_forecast

    forecast = []
    for i in range(1, 8):
        future_date = now + timedelta(days=i)
        pred = predictor.predict(location['latitude'], location['longitude'], location['elevation'], target_time=future_date)
        forecast.append(pred)
        
    prediction['forecast'] = forecast
    
    return jsonify(prediction)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
