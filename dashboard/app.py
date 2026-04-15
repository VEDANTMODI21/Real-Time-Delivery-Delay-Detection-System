import streamlit as st
import pandas as pd
import requests
import os
import time

# Use environment variable for API URL or default to localhost
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="UltraDelivery Analytics", page_icon="⚡", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: #00d4ff;
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 212, 255, 0.1);
    }
    .stMetric {
        background: transparent !important;
    }
    h1 {
        background: linear-gradient(90deg, #00d4ff, #0055ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    .stDataFrame {
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Real-Time Delivery Performance Engine")

def fetch_analytics():
    try:
        response = requests.get(f"{API_URL}/analytics")
        response.raise_for_status()
        return response.json()
    except:
        return None

def fetch_delayed_orders():
    try:
        response = requests.get(f"{API_URL}/orders/delayed")
        response.raise_for_status()
        return response.json()
    except:
        return []

# Metrics Section
analytics = fetch_analytics()
if analytics and "error" not in analytics:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Deliveries", analytics.get("total_orders", 0))
    with col2:
        delayed = analytics.get("delayed_orders", 0)
        total = max(analytics.get("total_orders", 1), 1)
        rate = round((delayed / total) * 100, 1)
        st.metric("Detection Alert", f"{delayed} Delays", f"{rate}% Rate", delta_color="inverse")
    with col3:
        st.metric("Avg Latency (min)", analytics.get("avg_delay", 0))

st.markdown("### 🛰️ Live Logistics Tracker")
delayed_orders = fetch_delayed_orders()

if delayed_orders and not isinstance(delayed_orders, dict):
    df = pd.DataFrame(delayed_orders)
    if not df.empty:
        df = df[['order_id', 'customer_name', 'vehicle_type', 'distance_km', 'expected_time', 'time_elapsed', 'delay_percentage', 'created_at']]
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%H:%M:%S')
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.success("All systems green - 0 delays detected.")
else:
    st.info("System initializing... Awaiting Kafka stream synchronization.")

if st.button("🔄 Sync Stream"):
    st.rerun()

time.sleep(3)
st.rerun()
