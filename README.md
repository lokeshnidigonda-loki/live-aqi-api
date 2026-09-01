# 🌍 Live Urban Environment API (AQI ETL Pipeline)

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Neon Postgres](https://img.shields.io/badge/Database-Neon_Postgres-blueviolet.svg)](https://neon.tech/)
[![Render](https://img.shields.io/badge/Hosted-Render-black.svg)](https://render.com/)

An automated Data Engineering pipeline and REST API that extracts real-time Air Quality Index (AQI) data for major metropolitan areas, stores it in a cloud PostgreSQL database, and serves it to the public via a documented FastAPI backend.

**🔴 Live API Documentation (Swagger UI):** [https://live-urban-aqi.onrender.com/docs](https://live-urban-aqi.onrender.com/docs)

---

## 🏗️ Architecture & Data Flow

1. **Extract:** A scheduled GitHub Actions Cron job runs `extract.py` daily to pull live JSON data from the OpenWeatherMap Air Pollution API.
2. **Transform:** Data is parsed and cleaned using `pandas`, converting raw UNIX timestamps to structured UTC formats.
3. **Load:** The cleaned data is pushed to a Serverless Neon PostgreSQL database using `SQLAlchemy`, utilizing idempotent SQL `ON CONFLICT` constraints to ensure data integrity.
4. **Serve:** A `FastAPI` application queries the database and serves the historical and real-time data through structured JSON endpoints.

---

## 🛠️ Tech Stack
* **Language:** Python
* **Backend Framework:** FastAPI, Uvicorn
* **Data Processing:** Pandas, Requests
* **Database:** PostgreSQL (Neon Serverless), SQLAlchemy, psycopg2
* **CI/CD & Automation:** GitHub Actions
* **Deployment:** Render (Cloud PaaS)

---

## 🔌 API Endpoints

The API is fully documented using OpenAPI/Swagger.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check and welcome message |
| `GET` | `/api/v1/aqi/latest` | Returns the most recent AQI readings for all tracked cities |
| `GET` | `/api/v1/aqi/{city}` | Returns historical AQI data for a specific city (e.g., `Hyderabad`) |

## Example Response:
``JSON
  {
  "city": "Hyderabad",
  "count": 1,
  "records": [
    {
      "city": "Hyderabad",
      "aqi": 2,
      "pm2_5": 14.5,
      "pm10": 22.3,
      "recorded_at": "2026-09-01T06:00:00"
    }
  ]
}

**Example Request:**
```http
GET [https://live-urban-aqi.onrender.com/api/v1/aqi/Hyderabad](https://live-urban-aqi.onrender.com/api/v1/aqi/Hyderabad)
