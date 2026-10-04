import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(page_title="NetTelemetry Dashboard", layout="wide")

st.title("NetTelemetry - Network Operations View")

# Mock data generation for dashboard testing since database integration is not complete
@st.cache_data
def load_mock_data():
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='1min')
    targets = ['192.168.1.1 (Gateway)', '8.8.8.8 (Google DNS)', 'Localhost TCP']
    
    data = []
    for t in targets:
        base_rtt = 5.0 if 'Localhost' in t else (15.0 if 'Google' in t else 2.0)
        for d in dates:
            rtt = max(1.0, np.random.normal(base_rtt, base_rtt * 0.2))
            loss = 0 if np.random.rand() > 0.05 else np.random.randint(5, 20)
            jitter = abs(np.random.normal(rtt * 0.1, 2.0))
            data.append({
                "timestamp": d,
                "target": t,
                "rtt_ms": rtt,
                "loss_pct": loss,
                "jitter_ms": jitter,
                "availability_pct": 100 - loss,
                "p95_ms": rtt * 1.5,
                "p99_ms": rtt * 2.0
            })
    return pd.DataFrame(data)

df = load_mock_data()

# Filters
st.sidebar.header("Filters")
selected_target = st.sidebar.selectbox("Select Target", df['target'].unique())

filtered_df = df[df['target'] == selected_target]
latest_data = filtered_df.iloc[-1]

# Status Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current RTT", f"{latest_data['rtt_ms']:.2f} ms")
col2.metric("Packet Loss", f"{latest_data['loss_pct']}%")
col3.metric("Jitter", f"{latest_data['jitter_ms']:.2f} ms")
col4.metric("Availability", f"{latest_data['availability_pct']}%")

st.markdown("---")

# Charts
st.subheader("Network Performance Metrics")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.line_chart(filtered_df.set_index('timestamp')['rtt_ms'], use_container_width=True)
    st.caption("Round-Trip Time (RTT)")

with col_chart2:
    st.line_chart(filtered_df.set_index('timestamp')['loss_pct'], use_container_width=True)
    st.caption("Packet Loss (%)")

col_chart3, col_chart4 = st.columns(2)

with col_chart3:
    st.line_chart(filtered_df.set_index('timestamp')['jitter_ms'], use_container_width=True)
    st.caption("Jitter (ms)")
    
with col_chart4:
    st.line_chart(filtered_df.set_index('timestamp')[['rtt_ms', 'p95_ms', 'p99_ms']], use_container_width=True)
    st.caption("Latency Percentiles (P95/P99)")

st.markdown("---")

# Anomaly Timeline
st.subheader("Anomaly Timeline")
anomalies = filtered_df[filtered_df['loss_pct'] > 5]
if not anomalies.empty:
    st.error(f"Detected {len(anomalies)} anomalies in the selected timeframe.")
    st.dataframe(anomalies[['timestamp', 'loss_pct', 'rtt_ms', 'jitter_ms']].reset_index(drop=True), use_container_width=True)
else:
    st.success("No anomalies detected.")
