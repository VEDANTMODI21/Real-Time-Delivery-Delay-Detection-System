backend: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
consumer: python consumer/consumer.py
producer: python producer/producer.py
dashboard: streamlit run dashboard/app.py --server.port $PORT --server.address 0.0.0.0
