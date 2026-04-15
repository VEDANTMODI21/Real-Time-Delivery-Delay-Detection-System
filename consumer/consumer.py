import json
import os
import psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "delivery_events")

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
        setup_db()
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest' # to read from the beginning if restarting
        )
        print(f"Listening for messages on topic: {KAFKA_TOPIC}")
        for message in consumer:
            event = message.value
            store_event(event)
    except Exception as e:
        print(f"Failed to consume messages: {e}")

if __name__ == "__main__":
    consume_messages()
