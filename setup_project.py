import os
import subprocess
import sys

def main():
    print("======================================================")
    print(" Setting up Offline Asia Climate Predictor")
    print("======================================================")
    
    print("\n1. Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("\n2. Fetching Asia Locations Database...")
    print("   (This will download allCountries.zip and build the SQLite database. It may take a few minutes)")
    subprocess.check_call([sys.executable, "src/data_collection/fetch_asia_locations.py"])
    
    print("\n3. Fetching 5 Years Historical Climate Data for Training...")
    subprocess.check_call([sys.executable, "src/data_collection/fetch_climate_data.py"])
    
    print("\n4. Training Machine Learning Models (Offline XGBoost)...")
    subprocess.check_call([sys.executable, "src/training/train_all_models.py"])
    
    print("\n======================================================")
    print(" Setup Complete! You can now run the web interface:")
    print(" python web/app.py")
    print("======================================================")

if __name__ == "__main__":
    main()
