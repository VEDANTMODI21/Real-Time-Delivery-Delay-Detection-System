import json
import time
import random
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("UPSTASH_REST_URL")
TOKEN = os.getenv("UPSTASH_REST_TOKEN")
QUEUE = os.getenv("REDIS_QUEUE", "delivery_events")

def send_to_upstash(event):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    # Command for Redis RPUSH via REST
    command = ["RPUSH", QUEUE, json.dumps(event)]
    
    try:
        response = requests.post(f"{URL}", headers=headers, json=command)
        if response.status_code == 200:
            print(f"✅ Sent event (via REST): {event['order_id']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Network Error: {e}")

def generate_order_event():
    order_id = random.randint(1000, 9999)
    customer_names = ["Arjun", "Deepika", "Rahul", "Sarah", "Michael", "Elena", "Rohan", "Sanya"]
    vehicles = ["Bike", "Scooter", "Electric Cycle", "Car"]
    
    expected_time = random.randint(15, 45)
    time_elapsed = random.randint(5, 60)
    
    event = {
        "order_id": order_id,
        "customer_name": random.choice(customer_names),
        "vehicle_type": random.choice(vehicles),
        "distance_km": round(random.uniform(1.0, 12.0), 1),
        "expected_time": expected_time,
        "time_elapsed": time_elapsed,
        "timestamp": datetime.utcnow().isoformat()
    }
    return event

if __name__ == "__main__":
    print(f"Starting REST Producer... Sending events to {URL}")
    while True:
        event = generate_order_event()
        send_to_upstash(event)
        time.sleep(random.uniform(2, 4))
