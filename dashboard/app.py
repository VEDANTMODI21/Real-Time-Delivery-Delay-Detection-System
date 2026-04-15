import streamlit as st
import pandas as pd
import requests
import os
import time

# Use environment variable for API URL or default to localhost
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Delivery Delay Dashboard", page_icon="🚚", layout="wide")
st.title("🚚 Real-Time Delivery Delay Dashboard")

def fetch_analytics():
    try:
        response = requests.get(f"{API_URL}/analytics")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to connect to backend analytics: {e}")
        return None

def fetch_delayed_orders():
    try:
        response = requests.get(f"{API_URL}/orders/delayed")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return []

# Layout: Metrics
analytics = fetch_analytics()
if analytics and "error" not in analytics:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", analytics.get("total_orders", 0))
    col2.metric("Delayed Orders", analytics.get("delayed_orders", 0), f"{int((analytics.get('delayed_orders', 0) / max(analytics.get('total_orders', 1), 1)) * 100)}%")
    col3.metric("Average Delay (mins)", analytics.get("avg_delay", 0))
elif analytics and "error" in analytics:
    st.error(f"Backend Error: {analytics['error']}")

st.markdown("---")

# Layout: Delayed Orders Table
st.subheader("⚠️ Currently Delayed Orders")
delayed_orders = fetch_delayed_orders()

if delayed_orders and not isinstance(delayed_orders, dict):
    df = pd.DataFrame(delayed_orders)
    if not df.empty:
        # Format and select columns
        df = df[['order_id', 'expected_time', 'time_elapsed', 'delay_percentage', 'created_at']]
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No delayed orders currently.")
else:
    st.info("No delayed orders found or awaiting data.")

st.markdown("---")
st.caption("Data refreshes automatically.")

if st.button("Manual Refresh"):
    st.rerun()

time.sleep(5) # basic auto refresh interval simulation
st.rerun()
