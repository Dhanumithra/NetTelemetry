# NetTelemetry

**NetTelemetry** is an advanced, actively measured Computer Networks monitoring system designed to observe, quantify, and analyze network communication quality and performance in real-time. 

Unlike traditional passive data collection systems, NetTelemetry directly probes the network using ICMP and controlled TCP/UDP transport-layer tests to evaluate connectivity, uncover latency variations, and detect statistical network anomalies.

## 🎯 Objective
A network can be technically connected while still providing poor communication quality (slow responses, unstable delay, intermittent packet loss). The primary objective of NetTelemetry is to continuously observe these networking characteristics so performance degradation can be accurately identified directly from measured network behavior. 

## 🚀 Impact & Significance
This project bridges the gap between raw network measurements and high-level performance analytics. The impact of NetTelemetry lies in its ability to:
- **Shift from Passive to Active:** Instead of just recording data, it actively tests both the network layer (ICMP) and transport layer (TCP/UDP) to simulate real-world application experiences.
- **Translate Raw Data into Insights:** It calculates advanced metrics like Jitter, Availability, and Latency Percentiles (P95/P99) to provide a true picture of network health.
- **Enable Autonomous Troubleshooting:** With the built-in anomaly detection engine, it automatically flags network degradation and identifies the likely cause (e.g., latency spikes, unstable delay) without manual intervention.
- **Enterprise-Grade Visualization:** It converts dry telemetry into a professional, actionable Network Operations Dashboard.

## 👥 Team Work Distribution

This project was built with a balanced, highly technical workload split between two members, ensuring deep involvement in Computer Networks, Data Storage, and Analytics.

### Member 1: Network Measurement & Ingestion
*Focus: ICMP/Network-layer monitoring, Measurement Schema, and Data Interface.*
- **Core Network Polling:** Implemented ICMP Echo Request/Reply mechanisms to capture Reachability, Round-Trip Time (RTT), and Time-To-Live (TTL).
- **Robust Error Handling:** Built robust timeout and unreachable host handling for accurate packet loss tracking.
- **Data Ingestion:** Designed the measurement database schema and functions to securely insert raw network observations.
- **Interface Provider:** Supplied a clean data interface for the analytics engine.

### Member 2: Transport Layer & Performance Analytics
*Focus: TCP/UDP Testing, Advanced Metrics, Anomaly Detection, and Dashboard Visualization.*
- **Transport Layer Testing:** Developed controlled TCP connectivity tests, UDP sender/receiver models, and TCP throughput measurement modules.
- **Advanced Metrics Engine:** Built the mathematical and analytical logic to calculate Jitter, Rolling Statistics, and P95/P99 latency percentiles.
- **Anomaly Detection:** Implemented an active statistical anomaly engine that compares current network behavior against healthy baselines to flag severe packet loss or latency spikes.
- **Storage & Visualization:** Built SQLite insertion logic for aggregated metrics and designed the professional, real-time **Streamlit Network Operations Dashboard**.

## 🛠️ Usage & Setup

### Prerequisites
Ensure you have Python 3.8+ installed. 
```bash
# Install required dependencies
pip install streamlit pandas numpy python-docx
```

### Running the System
1. **Configure Targets:** Edit `config.json` to define the IP addresses and hostnames you wish to monitor.
2. **Start the Dashboard:** Run the interactive Streamlit dashboard to monitor the network operations view in real-time.
```bash
streamlit run dashboard/app.py
```
3. **Run Tests:** To execute the unit test suite that validates the transport modules and metrics:
```bash
python -m unittest tests/test_member2.py
```

## 📊 Results & Deliverables
- **Real-Time Network Dashboard:** A professional Streamlit front-end displaying current RTT, Packet Loss, Jitter, and P95/P99 percentiles dynamically.
- **Automated Alerting:** An interactive "Anomaly Timeline" that autonomously logs network degradation events.
- **Detailed Documentation:** Every individual task executed by the members is thoroughly documented in technical, easy-to-understand `.docx` files located in the `docs/` directory.
- **Robust Network Testbed:** A fully functional code suite capable of running ICMP, TCP, UDP, and Throughput tests on controlled endpoints.

---
*NetTelemetry represents a comprehensive approach to modern network observability, proving that active probing combined with statistical analysis yields the most accurate network health assessments.*
