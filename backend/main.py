from fastapi import FastAPI
import psycopg2
import os
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Delivery Analytics API")

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def setup_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS delivery_data (
                order_id INT PRIMARY KEY,
                customer_name TEXT,
                vehicle_type TEXT,
                distance_km FLOAT,
                expected_time INT,
                time_elapsed INT,
                status TEXT,
                delay_percentage FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Failed to setup database: {e}")

@app.on_event("startup")
def startup_event():
    setup_db()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/orders")
def get_orders(limit: int = 100):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM delivery_data ORDER BY created_at DESC LIMIT %s", (limit,))
        orders = cur.fetchall()
        cur.close()
        conn.close()
        return orders
    except Exception as e:
        return {"error": str(e)}

@app.get("/orders/delayed")
def get_delayed_orders(limit: int = 100):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM delivery_data WHERE status = 'DELAYED' ORDER BY created_at DESC LIMIT %s", (limit,))
        orders = cur.fetchall()
        cur.close()
        conn.close()
        return orders
    except Exception as e:
        return {"error": str(e)}

@app.get("/analytics")
def get_analytics():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM delivery_data;")
        total_orders = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM delivery_data WHERE status = 'DELAYED';")
        delayed_orders = cur.fetchone()[0]
        
        avg_delay = 0
        if delayed_orders > 0:
            cur.execute("SELECT AVG(time_elapsed - expected_time) FROM delivery_data WHERE status = 'DELAYED';")
            avg_delay = round(cur.fetchone()[0], 2)
            
        cur.close()
        conn.close()
        
        return {
            "total_orders": total_orders,
            "delayed_orders": delayed_orders,
            "avg_delay": avg_delay
        }
    except Exception as e:
        return {"error": str(e)}
