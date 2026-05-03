import os
import zipfile
import requests
import sqlite3
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.config import DB_PATH, RAW_DATA_DIR, ASIA_COUNTRY_CODES

# Download allCountries to get absolutely every single location in Asia.
GEONAMES_URL = "https://download.geonames.org/export/dump/allCountries.zip"

def download_locations():
    zip_path = os.path.join(RAW_DATA_DIR, "allCountries.zip")
    if not os.path.exists(zip_path):
        print(f"Downloading {GEONAMES_URL} (This may take a while as it is ~400MB)...")
        r = requests.get(GEONAMES_URL, stream=True)
        with open(zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    
    print("Extracting and filtering for Asia...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            geonameid INTEGER PRIMARY KEY,
            name TEXT,
            asciiname TEXT,
            latitude REAL,
            longitude REAL,
            country_code TEXT,
            admin1_code TEXT,
            elevation INTEGER
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_country ON locations(country_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON locations(asciiname)')
    
    # Check if data already exists
    cursor.execute('SELECT COUNT(*) FROM locations')
    if cursor.fetchone()[0] > 0:
        print("Locations already populated in DB.")
        return

    print("Processing massive dataset line-by-line (to save RAM)...")
    with zipfile.ZipFile(zip_path) as z:
        with z.open('allCountries.txt') as f:
            batch = []
            count = 0
            for line in f:
                parts = line.decode('utf-8').split('\t')
                if len(parts) > 15:
                    country_code = parts[8]
                    # Filter for Asia and valid populated places ('P') or Administrative divisions ('A')
                    feat_class = parts[6]
                    if country_code in ASIA_COUNTRY_CODES and feat_class in ('P', 'A'):
                        try:
                            lat = float(parts[4])
                            lon = float(parts[5])
                            elev = int(parts[15]) if parts[15] else 0
                            batch.append((
                                int(parts[0]), parts[1], parts[2], lat, lon, 
                                country_code, parts[10], elev
                            ))
                            count += 1
                        except ValueError:
                            continue
                
                if len(batch) >= 20000:
                    cursor.executemany('''
                        INSERT OR IGNORE INTO locations 
                        (geonameid, name, asciiname, latitude, longitude, country_code, admin1_code, elevation)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', batch)
                    conn.commit()
                    batch = []
            
            if batch:
                cursor.executemany('''
                        INSERT OR IGNORE INTO locations 
                        (geonameid, name, asciiname, latitude, longitude, country_code, admin1_code, elevation)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', batch)
                conn.commit()
                
    print(f"Database populated successfully with {count} Asian locations (every single recorded place).")

if __name__ == "__main__":
    download_locations()
