import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "database", "asia_locations.db")
MODEL_DIR = os.path.join(BASE_DIR, "models")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")

# Asian Country Codes
ASIA_COUNTRY_CODES = {
    'AF', 'AM', 'AZ', 'BH', 'BD', 'BT', 'BN', 'KH', 'CN', 'CY', 'GE', 'IN', 'ID', 'IR', 'IQ', 
    'IL', 'JP', 'JO', 'KZ', 'KP', 'KR', 'KW', 'KG', 'LA', 'LB', 'MY', 'MV', 'MN', 'MM', 'NP', 
    'OM', 'PK', 'PH', 'QA', 'SA', 'SG', 'LK', 'SY', 'TW', 'TJ', 'TH', 'TR', 'TM', 'AE', 'UZ', 
    'VN', 'YE', 'MO', 'HK', 'PS'
}

for d in [DATA_DIR, os.path.dirname(DB_PATH), MODEL_DIR, RAW_DATA_DIR]:
    os.makedirs(d, exist_ok=True)
