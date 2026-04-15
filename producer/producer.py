import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer
import os
from dotenv import load_dotenv

load_dotenv()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "delivery_events")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

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

def send_to_kafka():
    print(f"Starting producer... Sending events to {KAFKA_TOPIC}")
    try:
        while True:
            event = generate_order_event()
            producer.send(KAFKA_TOPIC, event)
            print(f"Sent event: {event}")
            time.sleep(random.uniform(2, 4)) # Send every 2-3 sec roughly
    except KeyboardInterrupt:
        print("Producer stopped.")
    finally:
        producer.close()

if __name__ == "__main__":
    send_to_kafka()
