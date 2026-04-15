import json
import os
import psycopg2
import time
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_QUEUE = os.getenv("REDIS_QUEUE", "delivery_events")
REDIS_SSL = os.getenv("REDIS_SSL", "False").lower() == "true"

# DB Connection
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
        print("Database setup complete.")
    except Exception as e:
        print(f"Failed to setup database: {e}")

def detect_delay(expected_time, time_elapsed):
    status = "ON_TIME"
    if time_elapsed > expected_time:
        status = "DELAYED"
    return status

def calculate_delay_percentage(expected_time, time_elapsed):
    if expected_time == 0:
        return 0.0
    percentage = ((time_elapsed - expected_time) / expected_time) * 100
    return round(percentage, 2) if percentage > 0 else 0.0

def store_event(event):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        status = detect_delay(event['expected_time'], event['time_elapsed'])
        delay_percentage = calculate_delay_percentage(event['expected_time'], event['time_elapsed'])
        
        cur.execute("""
            INSERT INTO delivery_data (order_id, customer_name, vehicle_type, distance_km, expected_time, time_elapsed, status, delay_percentage)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (order_id) DO NOTHING;
        """, (
            event['order_id'], 
            event.get('customer_name', 'Unknown'),
            event.get('vehicle_type', 'Unknown'),
            event.get('distance_km', 0.0),
            event['expected_time'], 
            event['time_elapsed'], 
            status, 
            delay_percentage
        ))
        conn.commit()
        cur.close()
        conn.close()
        print(f"Stored order {event['order_id']} | Status: {status}")
    except Exception as e:
        print(f"Error storing event: {e}")

def consume_messages():
    try:
        # Wait for DB
        for i in range(10):
            try:
                setup_db()
                break
            except Exception as e:
                print(f"Waiting for DB... (Attempt {i+1}/10) Error: {e}")
                time.sleep(5)
        
        # Connect to Redis
        client = None
        for i in range(10):
            try:
                client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    password=REDIS_PASSWORD,
                    ssl=REDIS_SSL,
                    decode_responses=True
                )
                client.ping()
                break
            except Exception as e:
                print(f"Waiting for Redis... (Attempt {i+1}/10) Error: {e}")
                time.sleep(5)
        
        if not client:
            raise Exception("Failed to connect to Redis")

        print(f"Listening for messages on Redis queue: {REDIS_QUEUE}")
        while True:
            # BLPOP blocks until a message is available
            message = client.blpop(REDIS_QUEUE, timeout=0)
            if message:
                event = json.loads(message[1])
                store_event(event)

    except Exception as e:
        print(f"Failed to consume messages: {e}")

if __name__ == "__main__":
    consume_messages()
