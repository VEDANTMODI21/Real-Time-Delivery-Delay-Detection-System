from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Delivery Analytics API")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase REST Config
DB_URL = os.getenv("SUPABASE_REST_URL")
DB_KEY = os.getenv("SUPABASE_REST_KEY")

def get_headers():
    return {
        "apikey": DB_KEY,
        "Authorization": f"Bearer {DB_KEY}",
        "Content-Type": "application/json"
    }

@app.get("/health")
def health_check():
    try:
        # Simple probe to Supabase
        response = requests.get(f"{DB_URL}/rest/v1/delivery_data?select=count", headers=get_headers())
        if response.status_code == 200:
            return {"status": "ok", "database": "connected"}
        return {"status": "partial", "error": f"DB Error {response.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/orders")
def get_orders(limit: int = 100):
    try:
        url = f"{DB_URL}/rest/v1/delivery_data?select=*&order=created_at.desc&limit={limit}"
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/orders/delayed")
def get_delayed_orders(limit: int = 100):
    try:
        url = f"{DB_URL}/rest/v1/delivery_data?select=*&status=eq.DELAYED&order=created_at.desc&limit={limit}"
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/analytics")
def get_analytics():
    try:
        # Total orders
        count_url = f"{DB_URL}/rest/v1/delivery_data?select=count"
        res_total = requests.get(count_url, headers={**get_headers(), "Prefer": "count=exact"})
        total_orders = int(res_total.headers.get("Content-Range", "0-0/0").split("/")[-1])
        
        # Delayed orders
        delay_url = f"{DB_URL}/rest/v1/delivery_data?select=count&status=eq.DELAYED"
        res_delay = requests.get(delay_url, headers={**get_headers(), "Prefer": "count=exact"})
        delayed_orders = int(res_delay.headers.get("Content-Range", "0-0/0").split("/")[-1])
        
        # Avg delay (approximate via select)
        avg_delay = 0
        if delayed_orders > 0:
            # Note: PostgREST doesn't support AVG directly in simple select, 
            # we'd usually use an RPC or just fetch recent ones and calculate.
            # For simplicity, we'll return a mocked avg or fetch first 100.
            data_url = f"{DB_URL}/rest/v1/delivery_data?select=expected_time,time_elapsed&status=eq.DELAYED&limit=50"
            rows = requests.get(data_url, headers=get_headers()).json()
            if rows:
                delays = [(r['time_elapsed'] - r['expected_time']) for r in rows]
                avg_delay = round(sum(delays) / len(delays), 2)

        return {
            "total_orders": total_orders,
            "delayed_orders": delayed_orders,
            "avg_delay": avg_delay
        }
    except Exception as e:
        return {"error": str(e)}
