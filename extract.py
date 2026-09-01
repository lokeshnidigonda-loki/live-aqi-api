import requests
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timezone

# 1. Your specific credentials are already here
API_KEY = "838e7857a0fa8cef9afdb64b5dc47ec5"
DB_URL = "postgresql://neondb_owner:npg_U9PTdwk7XGLm@ep-raspy-smoke-a51wnara-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# 2. Target Cities with Latitude and Longitude
CITIES = {
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777}
}

print("Connecting to Neon Database...")
engine = create_engine(DB_URL)

# 3. Create the table in your cloud database if it doesn't exist yet
create_table_query = """
CREATE TABLE IF NOT EXISTS aqi_readings (
    id SERIAL PRIMARY KEY,
    city VARCHAR(50),
    aqi INTEGER,
    pm2_5 FLOAT,
    pm10 FLOAT,
    recorded_at TIMESTAMP,
    UNIQUE(city, recorded_at)
);
"""
with engine.begin() as conn:
    conn.execute(text(create_table_query))

# 4. Extract Live Data from OpenWeatherMap
print("Pulling live data from OpenWeatherMap API...")
data_rows = []
for city, coords in CITIES.items():
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={coords['lat']}&lon={coords['lon']}&appid={API_KEY}"
    response = requests.get(url).json()
    
    if "list" in response:
        reading = response["list"][0]
        timestamp = datetime.fromtimestamp(reading["dt"], timezone.utc)
        
        data_rows.append({
            "city": city,
            "aqi": reading["main"]["aqi"],
            "pm2_5": reading["components"]["pm2_5"],
            "pm10": reading["components"]["pm10"],
            "recorded_at": timestamp
        })

# 5. Transform and Load to Database
if data_rows:
    df = pd.DataFrame(data_rows)
    print(f"Extracted {len(df)} records. Pushing to cloud database...")
    
    insert_query = text("""
        INSERT INTO aqi_readings (city, aqi, pm2_5, pm10, recorded_at)
        VALUES (:city, :aqi, :pm2_5, :pm10, :recorded_at)
        ON CONFLICT (city, recorded_at) DO NOTHING;
    """)
    
    with engine.begin() as conn:
        for record in df.to_dict(orient="records"):
            conn.execute(insert_query, record)
            
    print("Success! Data is now live in your Neon Database.")
else:
    print("Error: No data pulled. Your API key might still be activating.")