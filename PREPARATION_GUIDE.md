# NetTelemetry: Master Project Preparation & Technical Guide
**Course**: 20MSS56 – Networks Programming Laboratory (5th Semester)  
**Domain**: Computer Networks & Active Telemetry  
**Authors**:
- **Member 1**: DHANUMITHRA T (Reg No: 2403717672622011) — *ICMP / Network Layer / Ingestion / Polling Engine*
- **Member 2**: SREE RAG S (Reg No: 2403717672621050) — *TCP/UDP Transport / Performance Analytics / Dashboard*

---

## 1. Project Overview & Philosophy

NetTelemetry is an **active, multi-layer computer network health monitoring and telemetry framework**. It addresses a critical problem in modern networks: **silent performance degradation**. A link or server can be technically "connected" (responding to an isolated ping) while being unusable due to:
1. **Queueing Delay & Bufferbloat**: Router queues overflow, driving latency from 25 ms to 250+ ms.
2. **Micro-Burst Packet Loss**: Dropping 2% to 5% of packets triggers TCP Congestion Control (AIMD) window halving, collapsing throughput.
3. **Delay Variation (Jitter)**: Unstable packet arrival depletes buffers in real-time media (VoIP, video calls, gaming).
4. **Dynamic Route Flapping**: Routing changes alter transit Autonomous Systems (AS) and hop count silently.

NetTelemetry injects synthetic active probes at **Layer 3 (Network - ICMP Echo)** and **Layer 4 (Transport - TCP Handshake & UDP Datagrams)**, computes rolling window statistics, detects anomalies, and displays real-time health on an interactive Streamlit NOC dashboard.

---

## 2. Theoretical Computer Networks Foundation

### 2.1 The TCP/IP & OSI Layer Mapping
| Layer | Protocol | Role in NetTelemetry |
| :--- | :--- | :--- |
| **Layer 3 (Network)** | **ICMP (RFC 792)** & **IPv4 (RFC 791)** | Type 8 Echo Request / Type 0 Echo Reply. Measures pure path propagation and transmission delay without socket buffers. Extracts 8-bit TTL to identify router hops. |
| **Layer 4 (Transport)** | **TCP (RFC 793)** | Connection-oriented stream protocol. Executes 3-way handshake (`SYN` $\rightarrow$ `SYN-ACK` $\rightarrow$ `ACK`) to measure connection establishment latency and inspect service port responsiveness. |
| **Layer 4 (Transport)** | **UDP (RFC 768)** | Connectionless datagram protocol with minimal 8-byte header. Probes observe best-effort delivery and unacknowledged packet loss without retransmissions. |
| **Layer 3 & 7** | **IPv4 & DNS (RFC 1035)** | Dynamically resolves hostnames to 32-bit IPv4 addresses (`socket.gethostbyname`) and routes packets. |

### 2.2 The 4 Components of Network Delay
Total nodal delay is given by:
$$d_{nodal} = d_{proc} + d_{queue} + d_{trans} + d_{prop}$$
- **$d_{proc}$ (Processing Delay)**: Time routers take to examine packet headers, verify checksums, and check routing tables (< 10 µs).
- **$d_{queue}$ (Queueing Delay)**: Time packets wait in router buffer queues. When traffic arrives faster than output link capacity, buffers fill up (Bufferbloat).
- **$d_{trans}$ (Transmission Delay)**: Time to push bits onto the link: $d_{trans} = L / R$ (Length $L$ in bits / Transmission rate $R$ in bps).
- **$d_{prop}$ (Propagation Delay)**: Time for a bit to travel physically: $d_{prop} = d / s$ ($d$ is physical distance, $s \approx 2 \times 10^8$ m/s in fiber).

### 2.3 Time-To-Live (TTL) & Route Hop Analysis
- **Definition**: An 8-bit field in IPv4 headers decremented by 1 at every router hop. Discarded with ICMP Type 11 (Time Exceeded) if TTL = 0 to prevent loops.
- **Hop Count Formula**: $\text{Hops Traversed} = \text{Initial TTL} - \text{Observed TTL}$.
- **Default OS Fingerprints**: Linux/Unix = 64, Windows = 128, Cisco IOS = 255.
- **Route Flap Detection**: If Google DNS (8.8.8.8) normally returns TTL=118 and suddenly drops to 114, NetTelemetry identifies that the packet traversed 4 additional router hops due to an upstream BGP route change.

### 2.4 Quality of Service (QoS) Metrics & Formulas
- **Round-Trip Time (RTT)**: $\text{RTT} = t_{\text{reply}} - t_{\text{send}}$ (ms).
- **Packet Loss %**: $\text{Loss} \% = \frac{\text{Failed Probes}}{\text{Total Probes}} \times 100$.
- **Availability %**: $\text{Availability} \% = \frac{\text{Successful Probes}}{\text{Total Probes}} \times 100$.
- **RFC 3550 Inter-Arrival Jitter**: Mean absolute difference of consecutive RTTs:
  $$\text{Jitter} = \frac{1}{N - 1} \sum_{i=2}^{N} | \text{RTT}_i - \text{RTT}_{i-1} |$$
- **P95 / P99 Tail Latency**: The 95th and 99th percentiles of sorted RTT values. Averages hide 300 ms queue spikes; percentiles expose worst-case user impact.
- **Throughput (Mbps)**: $\text{Throughput} = \frac{\text{Received Bytes} \times 8}{1,000,000 \times \text{Duration (seconds)}}$.

---

## 3. Two-Member Work Distribution & Task Breakdown

### Summary Matrix
| Project Area | Member 1: DHANUMITHRA T | Member 2: SREE RAG S |
| :--- | :--- | :--- |
| **Primary Focus** | Network Layer (Layer 3) & Polling Runner | Transport Layer (Layer 4) & Performance Analytics |
| **Network Implementation** | Native Win32 ICMP Echo (`icmp_monitor.py`), DNS Target Manager (`target_manager.py`) | TCP Connect timing (`tcp_monitor.py`), UDP Ping (`udp_monitor.py`), Throughput (`throughput_monitor.py`) |
| **Metrics Engine** | Raw RTT, TTL extraction, timeout handling, basic loss windows | RFC 3550 Jitter, Availability %, P95/P99 latency, Throughput in Mbps (`metrics.py`) |
| **Anomaly Engine** | Timeout handling & link disconnection errors | Multi-threshold anomaly engine for loss, jitter, and P95 spikes (`anomaly_detector.py`) |
| **Storage & Persistence** | SQLite schema (`schema.sql`), connection context manager & ingestion (`db.py`) | Aggregated metrics schema & anomaly event logging functions |
| **Testing & UI** | ICMP reachability (`test_icmp.py`), collector (`test_collector.py`), runner tests (`test_runner.py`) | Transport tests (`test_member2.py`), metric tests (`test_metrics.py`), Streamlit Dashboard (`app.py`) |

---

### Member 1: DHANUMITHRA T — Deep-Dive Tasks
1. **Target Management (`network/target_manager.py`)**:
   - Reads `config.json` defining targets.
   - Converts hostnames to IPv4 addresses using `socket.gethostbyname()` and caches resolved IPs.
2. **Native Win32 ICMP Echo Engine (`network/icmp_monitor.py`)**:
   - **Why not raw sockets?** Opening `socket.SOCK_RAW` on Windows requires Administrator privileges.
   - **Why not subprocess ping?** Subprocess ping spawns an entire OS process per probe (slow, CPU-heavy) and rounds latency to integers.
   - **Solution**: Member 1 bound directly to `iphlpapi.dll` using Python `ctypes`, calling `IcmpCreateFile`, `IcmpSendEcho`, and `IcmpCloseHandle` to capture microsecond RTT and exact TTL without root permissions.
   - Mapped `IP_OPTION_INFORMATION` and `ICMP_ECHO_REPLY` C-structures.
3. **Database Architecture & Ingestion (`database/schema.sql`, `database/db.py`)**:
   - Designed 4 relational tables: `targets`, `measurements`, `window_metrics`, and `anomalies`.
   - Enabled `PRAGMA journal_mode = WAL;` (Write-Ahead Logging) and `PRAGMA foreign_keys = ON;` to allow simultaneous background writes without locking the Streamlit dashboard reads.
4. **Asynchronous Polling Runner Loop (`telemetry/runner.py`)**:
   - Built continuous loop using `concurrent.futures.ThreadPoolExecutor`.
   - Probes targets concurrently so an unreachable target timing out (2s) does not delay other targets.
   - Handled `KeyboardInterrupt` cleanly.
5. **Testing**:
   - Authored unit tests for ICMP response parsing, DWORD IP conversion, and runner loop dispatch.

---

### Member 2: SREE RAG S — Deep-Dive Tasks
1. **TCP Handshake Connect Timing (`network/tcp_monitor.py`)**:
   - Creates a stream socket (`socket.AF_INET`, `socket.SOCK_STREAM`), initiates `sock.connect((host, port))`, and measures elapsed time.
   - Catches `socket.timeout` (firewalled port) and `ConnectionRefusedError` (closed port).
   - Measures transport handshake latency and OS SYN backlog processing.
2. **UDP Datagram Probe (`network/udp_monitor.py`)**:
   - Uses `socket.SOCK_DGRAM` to observe connectionless datagram delivery and packet drops without retransmissions.
3. **Throughput Monitor (`network/throughput_monitor.py`)**:
   - Transfers 1 MB of test data over TCP, measures duration, and calculates Mbps.
4. **Metrics Engine (`telemetry/metrics.py`)**:
   - Implemented RFC 3550 Jitter algorithm ($\frac{1}{N-1}\sum |RTT_i - RTT_{i-1}|$).
   - Implemented exact P95/P99 latency percentiles via linear interpolation.
5. **Statistical Anomaly Detector (`analytics/anomaly_detector.py`)**:
   - Rule checks: Loss > 5%, P95 > 100 ms, Jitter > 20 ms.
   - Generates structured anomaly dictionaries logged into SQLite.
6. **Streamlit NOC Dashboard (`dashboard/app.py`, `components.py`, `styles.py`)**:
   - Interactive web UI with auto-refresh, metric cards, Plotly time-series charts, and dark/light mode.
7. **Testing**:
   - Authored 19 unit tests in `tests/test_member2.py` and `tests/test_metrics.py`.

---

## 4. Testing & Performance Analysis

### 4.1 Test Matrix (37 Tests Passed in 5.5s)
- **TC-01**: Reachable public DNS (8.8.8.8, 1.1.1.1) $\rightarrow$ Echo Reply, RTT > 0 ms, TTL extracted (`PASS`).
- **TC-02**: Inactive host (10.255.255.1) $\rightarrow$ Socket timeout caught, loss % recorded (`PASS`).
- **TC-03**: TCP Open Port (Port 80/443) $\rightarrow$ 3-way handshake completes, connect RTT recorded (`PASS`).
- **TC-04**: Closed TCP Port (Port 9999) $\rightarrow$ `ConnectionRefused` caught cleanly (`PASS`).
- **TC-05**: UDP Ping $\rightarrow$ Best-effort datagram transmitted and timed (`PASS`).
- **TC-06**: Jitter & Percentile Math $\rightarrow$ RFC 3550 delta and sorted interpolation validated (`PASS`).
- **TC-07**: Anomaly Rules $\rightarrow$ Loss > 5% or Jitter > 20 ms triggers alert (`PASS`).

### 4.2 System Overhead
- **Bandwidth Footprint**: 60 bytes per probe at 5s interval $\approx$ **96 bps** (< 0.0001% of a 100 Mbps link).
- **CPU & RAM**: < 1.2% CPU and < 45 MB RAM over continuous 24-hour execution.
- **Timing Precision**: Microsecond-resolution floating point timers.

---

## 5. Master Viva Examination Handbook (20 Top Questions & Answers)

### Category A: General Project Identity & Networking Relevance
**Q1: Is NetTelemetry just a software database/UI project or a true Computer Networks project?**  
*Answer*: NetTelemetry is fundamentally a Computer Networks project. All data originates directly from live active network probing using ICMP (RFC 792), TCP sockets (RFC 793), and UDP datagrams (RFC 768). We measure packet-level behavior (RTT, TTL, loss, jitter, availability), examine IPv4 headers, and analyze transport socket handshakes. The database and Streamlit dashboard are merely supporting tools to store and visualize the measured network communication.

**Q2: Why is active network probing preferred over passive packet sniffing?**  
*Answer*: Passive sniffing (e.g. Wireshark/libpcap) requires physical access to switch mirror ports (SPAN), captures sensitive payload data raising privacy issues, and produces gigabytes of capture files. Active probing injects lightweight, synthetic test packets at controlled intervals, enabling non-intrusive health assessment of internal gateways and public cloud servers regardless of whether user traffic is currently flowing.

**Q3: What is 'Silent Network Degradation' and why does standard ping miss it?**  
*Answer*: Silent degradation occurs when a host is technically reachable but performs poorly—such as high queueing delay (bufferbloat), micro-burst 2-5% packet drops, and jitter. Standard manual ping only shows isolated point-in-time checks. NetTelemetry uses sliding-window statistics to capture continuous jitter, P95 tail latency, and loss patterns that periodic manual checks completely miss.

---

### Category B: Protocol & Layering Dynamics
**Q4: Why use ICMP Echo when we already have TCP?**  
*Answer*: ICMP operates at Layer 3 (Network Layer) without connection setup, socket allocation, or flow control. It is processed directly by the remote kernel/router, measuring pure physical and routed path delay. TCP operates at Layer 4 (Transport Layer) and requires a 3-way handshake, capturing server application backlog and transport state. Both are required for complete multi-layer visibility.

**Q5: What does the observed IPv4 TTL header field tell us?**  
*Answer*: TTL (Time-To-Live) is an 8-bit IPv4 header field that decrements by 1 at each intermediate router to prevent routing loops. The observed TTL allows us to calculate the exact hop count traversed (Initial_TTL - Observed_TTL) and infer the remote OS (Linux defaults to 64, Windows to 128). Sudden TTL changes alert network administrators to silent dynamic routing flaps.

**Q6: What is the difference between TCP Connect latency and ICMP RTT?**  
*Answer*: ICMP RTT measures the elapsed time for an Echo Request to reach the destination and return an Echo Reply. TCP Connect latency measures the time required to complete the full 3-way handshake (SYN -> SYN-ACK -> ACK). TCP connect time is always slightly higher because it includes TCP stack processing, SYN backlog queueing, and transport socket state transitions.

**Q7: Why did you include UDP if it is an unreliable protocol?**  
*Answer*: UDP is connectionless and does not retransmit lost packets or perform congestion control. This makes it the ideal protocol to observe true best-effort packet loss and transit timing without TCP's retransmission interference, accurately modeling real-time multimedia (VoIP, video calls, DNS).

---

### Category C: Low-Level Coding & System Implementation
**Q8: How did you implement ICMP probing in Python without requiring Administrator root privileges?**  
*Answer*: Opening a raw ICMP socket (`socket.SOCK_RAW`) on Windows requires Administrator privileges. To avoid this, Member 1 utilized Python's `ctypes` library to bind directly to the native Windows IP Helper API (`iphlpapi.dll`), invoking `IcmpCreateFile`, `IcmpSendEcho`, and `IcmpCloseHandle`. Windows allows standard non-admin users to invoke these kernel APIs, enabling native ICMP measurement with microsecond accuracy.

**Q9: Why did you use ThreadPoolExecutor in the polling runner loop?**  
*Answer*: If probes were executed sequentially, a single unreachable target with a 2-second timeout would delay probing all subsequent targets, distorting the configured polling interval. By dispatching probes across worker threads concurrently via `ThreadPoolExecutor`, every target is probed in parallel independently of other targets' response times.

**Q10: Why is SQLite configured with WAL (Write-Ahead Logging) mode?**  
*Answer*: In default journal mode, SQLite locks the entire database file during writes, causing read queries from the Streamlit UI to freeze or fail. In WAL mode (`PRAGMA journal_mode = WAL;`), writers append changes to a WAL log while readers read from the main database file concurrently without locking or database collisions.

**Q11: How does the TCP connect monitor handle closed ports or firewalls?**  
*Answer*: The module wraps `sock.connect()` in a `try...except` block with a timeout. If the port is closed, the target OS immediately responds with a TCP `RST` segment, caught as `ConnectionRefusedError`. If a firewall drops the packet silently, the socket timer expires, caught as `socket.timeout`. Both cases are recorded cleanly without crashing.

---

### Category D: Performance, QoS & Mathematical Calculations
**Q12: What is Jitter, what formula did you use, and why does it matter?**  
*Answer*: Jitter is the statistical variation in packet transit delay. We implemented the RFC 3550 inter-arrival jitter algorithm: $\text{Jitter} = \frac{1}{N - 1} \sum | \text{RTT}_i - \text{RTT}_{i-1} |$. High jitter exhausts playback jitter buffers in real-time multimedia (VoIP, video calls), causing severe audio stutter and frame loss even if average latency is low.

**Q13: Why compute 95th and 99th percentile latency (P95/P99) instead of simple averages?**  
*Answer*: Arithmetic averages lie in computer networks. If 99 packets experience 20 ms latency and 1 packet experiences 500 ms (due to a bufferbloat queue spike), the average is 24.8 ms, which looks healthy. The P99 percentile clearly reports 500 ms, capturing the severe tail latency that degrades user experience.

**Q14: Why does a 3% packet loss rate severely degrade TCP throughput?**  
*Answer*: TCP interprets packet loss as a signal of network congestion. Under TCP's Additive Increase Multiplicative Decrease (AIMD) congestion control algorithm, dropping a packet forces TCP to halve its congestion window (cwnd) and wait for retransmission timeouts, causing throughput to collapse far beyond the 3% loss proportion.

**Q15: How did you calculate network throughput in Mbps?**  
*Answer*: Throughput was measured by connecting to a test socket over TCP, transferring a known payload (e.g. 1 MB = 1,048,576 bytes), measuring the exact duration in seconds, and calculating: $\text{Throughput (Mbps)} = \frac{\text{Received Bytes} \times 8}{1,000,000 \times \text{Duration (seconds)}}$.

---

### Category E: Member-Specific Viva Survival Scripts

#### Custom Script for DHANUMITHRA T (Member 1 Focus):
> *"In this project, I was responsible for the Network Layer (Layer 3) measurement engine, dynamic target management, database ingestion architecture, and the concurrent polling runner loop.*  
> *Specifically, I solved the root privilege limitation on Windows by binding to `iphlpapi.dll` using Python `ctypes` (`IcmpCreateFile`, `IcmpSendEcho`), which maps C-structures to extract microsecond RTT and IPv4 TTL without needing admin privileges. I designed the SQLite schema with WAL mode to prevent database read/write locks, and built `telemetry/runner.py` using `ThreadPoolExecutor` so slow or timing-out hosts do not block concurrent measurements across the network."*

#### Custom Script for SREE RAG S (Member 2 Focus):
> *"In this project, I was responsible for the Transport Layer (Layer 4) monitoring modules, network QoS analytics, statistical anomaly detection, and the Streamlit Network Operations Center dashboard.*  
> *Specifically, I implemented non-blocking TCP 3-way handshake connect timing via `socket.SOCK_STREAM` and UDP ping probes via `socket.SOCK_DGRAM`. I authored the statistical metrics engine in `telemetry/metrics.py` implementing RFC 3550 Jitter and P95/P99 tail latency percentiles, developed the multi-criteria anomaly detection engine in `analytics/anomaly_detector.py`, and designed the real-time Streamlit dashboard."*

---

## 6. Project File Directory Sitemap

```text
NetTelemetry/
├── network/
│   ├── icmp_monitor.py         # Member 1: Native Win32 ICMP Echo engine via ctypes
│   ├── target_manager.py       # Member 1: DNS hostname resolution via socket.gethostbyname
│   ├── tcp_monitor.py          # Member 2: TCP 3-way handshake connect latency measurement
│   ├── udp_monitor.py          # Member 2: UDP connectionless datagram ping
│   └── throughput_monitor.py   # Member 2: TCP stream transfer throughput measurement (Mbps)
├── telemetry/
│   ├── runner.py               # Member 1: Multi-threaded continuous polling runner loop
│   ├── collector.py            # Member 1: Ingestion bridge connecting probes to SQLite
│   └── metrics.py              # Member 2: RFC 3550 Jitter, Availability, Loss %, P95/P99 math
├── database/
│   ├── schema.sql              # Member 1: 4 relational tables (targets, measurements, window, anomalies)
│   ├── db.py                   # Member 1: Connection wrapper with WAL mode & context management
│   └── db_m2.py                # Member 2: Storage functions for window metrics & anomaly logs
├── analytics/
│   └── anomaly_detector.py     # Member 2: Threshold-based network anomaly evaluation
├── dashboard/
│   ├── app.py                  # Member 2: Streamlit real-time NOC web dashboard
│   ├── components.py           # Member 2: Metric cards, charts, and layout components
│   └── styles.py               # Member 2: Dark/light contrast CSS & accessibility styling
├── tests/
│   ├── test_icmp.py            # Member 1: ICMP packet parsing & API tests
│   ├── test_collector.py       # Member 1: Telemetry storage ingestion tests
│   ├── test_runner.py          # Member 1: Runner loop concurrency & shutdown tests
│   ├── test_metrics.py         # Member 2: RFC 3550 Jitter & percentile math tests
│   └── test_member2.py         # Member 2: TCP/UDP sockets & anomaly detection tests
├── docs/
│   ├── diagrams/               # High-resolution 300 DPI architecture and protocol flow diagrams
│   ├── NetTelemetry_Comprehensive_Project_Preparation_Guide.docx # Master prep docx
│   └── NetTelemetry_Short_Abstract.docx                          # Formal project abstract docx
├── config.json                 # Target configuration registry (hosts, intervals, timeouts)
├── PREPARATION_GUIDE.md        # Comprehensive markdown preparation handbook
└── README.md                   # Main project overview and setup instructions
```
