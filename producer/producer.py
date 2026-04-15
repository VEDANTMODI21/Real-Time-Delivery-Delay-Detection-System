import json
import time
import random
from datetime import datetime
import redis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_QUEUE = os.getenv("REDIS_QUEUE", "delivery_events")
REDIS_SSL = os.getenv("REDIS_SSL", "False").lower() == "true"

def get_redis_client():
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
            return client
        except Exception as e:
            print(f"Waiting for Redis... (Attempt {i+1}/10) Error: {e}")
            time.sleep(5)
    raise Exception("Could not connect to Redis after 10 attempts")

r = get_redis_client()

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

def send_to_redis():
    print(f"Starting producer... Sending events to Redis queue: {REDIS_QUEUE}")
    try:
        while True:
            event = generate_order_event()
            r.rpush(REDIS_QUEUE, json.dumps(event))
            print(f"Sent event: {event}")
            time.sleep(random.uniform(2, 4))
    except KeyboardInterrupt:
        print("Producer stopped.")

if __name__ == "__main__":
    send_to_redis()
