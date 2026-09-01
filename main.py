from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text

app = FastAPI(
    title="Live Urban Environment API",
    description="Real-time and historical Air Quality Index (AQI) data pipeline."
)

import os

DB_URL = os.environ.get("DATABASE_URL")

if not DB_URL:
    raise ValueError("DATABASE_URL environment variable is missing.")

engine = create_engine(DB_URL)

@app.get("/")
def home():
    return {"status": "API is live", "message": "Welcome to the Urban Environment API"}

@app.get("/api/v1/aqi/latest")
def get_latest_aqi():
    query = text("""
        SELECT DISTINCT ON (city) city, aqi, pm2_5, pm10, recorded_at 
        FROM aqi_readings 
        ORDER BY city, recorded_at DESC;
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query)
        data = [
            {
                "city": row[0], 
                "aqi": row[1], 
                "pm2_5": row[2], 
                "pm10": row[3], 
                "recorded_at": row[4].isoformat() if row[4] else None
            } 
            for row in result
        ]
        
    return {"count": len(data), "data": data}

@app.get("/api/v1/aqi/{city}")
def get_city_aqi(city: str, limit: int = 10):
    query = text("""
        SELECT city, aqi, pm2_5, pm10, recorded_at 
        FROM aqi_readings 
        WHERE LOWER(city) = LOWER(:city)
        ORDER BY recorded_at DESC 
        LIMIT :limit;
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {"city": city, "limit": limit})
        rows = result.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail=f"No data found for city: {city}")
            
        data = [
            {
                "city": row[0], 
                "aqi": row[1], 
                "pm2_5": row[2], 
                "pm10": row[3], 
                "recorded_at": row[4].isoformat() if row[4] else None
            } 
            for row in rows
        ]
        
    return {"city": city.capitalize(), "count": len(data), "records": data}
