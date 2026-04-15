# Real-Time Delivery Delay Detection System

This project is an end-to-end data engineering system that detects delivery delays in real time. It uses Apache Kafka for streaming order events, PostgreSQL (Supabase) for persistent storage, FastAPI for exposing API endpoints, and Streamlit for data visualization.

## Architecture Architecture Overview

- **Kafka**: Message broker for streaming order events in real time.
- **Producer**: Python script generating live mock order events and streaming them to Kafka continuously.
- **Consumer**: Python script reading from Kafka, processing the delay logic, and writing to the cloud-hosted database.
- **Database**: PostgreSQL (e.g. Supabase) stores data securely and is ready for production scaling.
- **Backend**: FastAPI serving processed metrics and delivery data via clean REST endpoints.
- **Dashboard**: Streamlit lightweight, real-time dashboard visualizing system analytics.

## Setup & Execution

### 1. Requirements
Ensure you have Kafka running locally or via Docker. Install the required dependencies using:
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
You must define your database coordinates and Kafka broker endpoints in `.env` file at root level:
```ini
KAFKA_BROKER=localhost:9092
KAFKA_TOPIC=delivery_events
DB_HOST=your-supabase-db-host.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-supabase-password
API_URL=http://localhost:8000
```

### 3. Kafka Setup
Start Kafka and Zookeeper. Create the `delivery_events` topic:
```bash
kafka-topics.sh --create --topic delivery_events --bootstrap-server localhost:9092
```

### 4. Running the Components

Run each in a separate terminal:

**Start Backend API**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Start Consumer Engine**
```bash
python consumer/consumer.py
```

**Start Producer Engine**
```bash
python producer/producer.py
```

**Start Dashboard**
```bash
streamlit run dashboard/app.py
```
