import json
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# Upstash REST Config
REDIS_URL = os.getenv("UPSTASH_REST_URL")
REDIS_TOKEN = os.getenv("UPSTASH_REST_TOKEN")
REDIS_QUEUE = os.getenv("REDIS_QUEUE", "delivery_events")

# Supabase REST Config
DB_URL = os.getenv("SUPABASE_REST_URL")
DB_KEY = os.getenv("SUPABASE_REST_KEY")

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
        status = detect_delay(event['expected_time'], event['time_elapsed'])
        delay_percentage = calculate_delay_percentage(event['expected_time'], event['time_elapsed'])
        
        payload = {
            "order_id": event['order_id'],
            "customer_name": event.get('customer_name', 'Unknown'),
            "vehicle_type": event.get('vehicle_type', 'Unknown'),
            "distance_km": event.get('distance_km', 0.0),
            "expected_time": event['expected_time'],
            "time_elapsed": event['time_elapsed'],
            "status": status,
            "delay_percentage": delay_percentage
        }
        
        headers = {
            "apikey": DB_KEY,
            "Authorization": f"Bearer {DB_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates" # ON CONFLICT DO NOTHING equivalent
        }
        
        # POST to Supabase REST endpoint
        response = requests.post(f"{DB_URL}/rest/v1/delivery_data", headers=headers, json=payload)
        
        if response.status_code in [200, 201]:
            print(f"✅ Stored order {event['order_id']} | Status: {status}")
        else:
            print(f"❌ DB Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error storing event: {e}")

def consume_messages():
    try:
        print(f"Starting REST Consumer... Polling Redis and writing to Supabase (Port 443)")
        redis_headers = {"Authorization": f"Bearer {REDIS_TOKEN}"}
        redis_command = ["LPOP", REDIS_QUEUE]

        while True:
            try:
                # Poll Redis
                response = requests.post(f"{REDIS_URL}", headers=redis_headers, json=redis_command)
                if response.status_code == 200:
                    result = response.json().get("result")
                    if result:
                        event = json.loads(result)
                        store_event(event)
                    else:
                        time.sleep(2) # Queue empty
                else:
                    print(f"❌ Redis REST Error: {response.status_code}")
                    time.sleep(5)
            except Exception as e:
                print(f"❌ Network Error: {e}")
                time.sleep(5)

    except Exception as e:
        print(f"Failed to consume messages: {e}")

if __name__ == "__main__":
    consume_messages()
