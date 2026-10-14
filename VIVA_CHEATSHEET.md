# NetTelemetry: Viva Voce & Presentation Master Cheat-Sheet
**Course**: 20MSS56 – Networks Programming Laboratory (5th Semester)  
**Authors**:
- **Member 1**: DHANUMITHRA T (Reg No: 2403717672622011) — *Network Layer (ICMP) / Ingestion / Polling Engine*
- **Member 2**: SREE RAG S (Reg No: 2403717672621050) — *Transport Layer (TCP/UDP) / Performance Analytics / Dashboard*

---

## 1. 90-Second Presentation Opening Pitch (Say This to Start Confidently)
> *"Good morning, respected examiners. We are presenting **NetTelemetry**, an active, multi-layer computer network performance monitoring and telemetry system.*  
> 
> *1. **The Core Problem**: Traditional diagnostic tools like standard ping only answer a binary question: 'is the server reachable?' In real networks, **silent performance degradation** occurs—such as queueing delay (bufferbloat), micro-burst 2–5% packet drops, and delay jitter—which cripples applications like VoIP, video streaming, and web services while the link still appears 'online'.*  
> *2. **Our Solution**: NetTelemetry actively probes network endpoints across **Layer 3 (ICMP Echo)** and **Layer 4 (TCP 3-Way Handshake & UDP datagrams)**. It computes rolling window statistics: Round-Trip Time (RTT), IPv4 Time-To-Live (TTL), Packet Loss %, Availability %, RFC 3550 Jitter, and P95 tail latency.*  
> *3. **The Output**: An automated anomaly engine flags link degradation when loss > 5% or jitter > 20ms, and a real-time Streamlit NOC dashboard visualizes live graphs, metric indicator tiles, and incident logs."*

---

## 2. Work Split Quick-Card (Know Your Exact Deliverables)

| Project Module | **DHANUMITHRA T (Member 1)** | **SREE RAG S (Member 2)** |
| :--- | :--- | :--- |
| **Layer Focus** | **Layer 3 (Network Layer) & Core Engine** | **Layer 4 (Transport Layer) & Analytics** |
| **Network Coding** | • Native Win32 ICMP Echo (`network/icmp_monitor.py`) via `ctypes` calling `iphlpapi.dll` (no root/admin needed).<br>• Dynamic DNS Target Manager (`network/target_manager.py`). | • TCP 3-way handshake connect timer (`network/tcp_monitor.py`).<br>• UDP datagram ping (`network/udp_monitor.py`).<br>• Controlled throughput monitor (`network/throughput_monitor.py`). |
| **Metrics & Rules** | • Raw RTT measurement, TTL extraction, timeout handling, basic loss windows. | • RFC 3550 Jitter algorithm, Availability %, P95/P99 latency math (`telemetry/metrics.py`).<br>• Statistical Anomaly Detector (`analytics/anomaly_detector.py`). |
| **Database & Runner** | • SQLite 4-table schema (`database/schema.sql`), WAL mode, and ThreadPool polling runner loop (`telemetry/runner.py`). | • Aggregated metrics database functions (`database/db_m2.py`) and Streamlit NOC Dashboard (`dashboard/app.py`). |
| **Testing** | • ICMP packet parsing, IP DWORD conversion, and runner loop tests (`test_icmp.py`, `test_runner.py`). | • TCP socket connect, UDP ping, jitter math, and anomaly engine tests (`test_member2.py`, `test_metrics.py`). |
| **Shared Tasks** | • Distributed Star Topology design, unified JSON data contract, end-to-end integration, and 37/37 automated tests passing in 5.5s. |

---

## 3. Core Networking Concepts in 2 Lines (The "Why, Where & How")

1. **Why ICMP Echo? (Layer 3)**: Has no ports or socket buffers; answered directly by remote kernel/router. Measures pure physical and routed path delay.
2. **Why TCP Connect Latency? (Layer 4)**: Measures the time to complete the 3-way handshake (`SYN` $\rightarrow$ `SYN-ACK` $\rightarrow$ `ACK`). Catches server application backlog queueing and closed/firewalled ports.
3. **Why UDP Ping? (Layer 4)**: Connectionless protocol with no retransmissions or flow control. Shows true unacknowledged packet drop behavior (models VoIP and DNS).
4. **Why Observe TTL?**: 8-bit IPv4 header field decremented by 1 at every router hop. $\text{Hop Count} = \text{Initial TTL} - \text{Observed TTL}$. Detects sudden dynamic BGP routing flaps.
5. **Why Jitter? (RFC 3550)**: Mean absolute difference between consecutive RTTs: $\frac{1}{N-1} \sum | \text{RTT}_i - \text{RTT}_{i-1} |$. High jitter exhausts buffers in VoIP and video calls, causing robotic audio stutter.
6. **Why P95/P99 Latency?**: Averages lie in networking. 99 packets at 20ms and 1 packet at 500ms has an average of 24.8ms (looks fine). P99 reveals the 500ms bufferbloat spike.
7. **Why Native Win32 API via ctypes?**: Opening raw sockets (`SOCK_RAW`) on Windows requires Administrator privileges. Subprocess ping is slow. We called `iphlpapi.dll` (`IcmpSendEcho`) directly—microsecond accuracy without admin rights!
8. **Why ThreadPoolExecutor?**: Concurrent parallel probing. If one target times out (takes 2s), it does not delay or stall the measurement of other responsive targets.
9. **Why SQLite WAL Mode?**: Write-Ahead Logging allows simultaneous background writes from worker threads while the Streamlit web dashboard reads data without database lock collisions.

---

## 4. Top 16 Viva Questions & Bulletproof Answers

#### Q1: Is NetTelemetry just a software dashboard or a true Computer Networks project?
> **Answer**: It is fundamentally a Computer Networks project. All telemetry is generated by active synthetic network probing using ICMP (RFC 792), TCP sockets (RFC 793), and UDP datagrams (RFC 768). We measure packet-level behavior, examine IPv4 headers, and analyze socket handshakes. The database and Streamlit dashboard are merely supporting tools to store and visualize network behavior.

#### Q2: What is the exact difference between ICMP RTT and TCP Connect RTT?
> **Answer**: ICMP RTT measures pure network-layer transmission and propagation delay without socket buffers. TCP Connect RTT measures the 3-way handshake (`SYN` $\rightarrow$ `SYN-ACK` $\rightarrow$ `ACK`), which includes network delay PLUS remote server socket backlog queueing and transport stack state processing.

#### Q3: What does the observed TTL value tell us about the remote host and path?
> **Answer**: TTL decrements by 1 at every router. $\text{Hop Count} = \text{Initial TTL} - \text{Observed TTL}$. Standard initial TTL defaults are Linux = 64, Windows = 128. If Google DNS (8.8.8.8) returns TTL=118, it traversed 10 hops (128 - 118). If it drops to 114, it indicates a dynamic routing flap added 4 hops.

#### Q4: What happens when an IP packet's TTL reaches 0?
> **Answer**: The router discards the packet and sends an ICMP Type 11 (Time Exceeded) message back to the sender. This mechanism prevents packets from circulating infinitely during routing loops.

#### Q5: Why didn't you use raw sockets (`socket.SOCK_RAW`) for ICMP?
> **Answer**: On Windows, opening `SOCK_RAW` requires Administrator privileges. To make NetTelemetry run safely as standard non-admin user code, Member 1 used Python `ctypes` to bind directly to the native Windows IP Helper API (`iphlpapi.dll`, `IcmpSendEcho`).

#### Q6: Why is subprocess ping (`os.system` or `subprocess.run`) bad for continuous monitoring?
> **Answer**: Spawning a ping process creates an entire operating system process per probe, consuming heavy CPU. Furthermore, standard ping rounds latency to whole integers, losing microsecond-level delay jitter.

#### Q7: What is Bufferbloat and which delay component does it affect?
> **Answer**: Bufferbloat occurs when intermediate router buffers become overly large and fill with packets during congestion, causing massive queueing delay ($d_{queue}$ in the nodal delay formula: $d_{nodal} = d_{proc} + d_{queue} + d_{trans} + d_{prop}$) without dropping packets.

#### Q8: Why does a 3% packet loss rate severely degrade TCP throughput?
> **Answer**: TCP interprets packet loss as congestion. Under TCP's Additive Increase Multiplicative Decrease (AIMD) algorithm, a lost packet forces TCP to halve its congestion window (`cwnd`) and wait for retransmissions, collapsing throughput far beyond the 3% loss proportion.

#### Q9: What is Jitter, what formula did you use, and which applications suffer most?
> **Answer**: Jitter is the delay variation between consecutive packets. We implemented RFC 3550: $\text{Jitter} = \frac{1}{N-1} \sum | \text{RTT}_i - \text{RTT}_{i-1} |$. Jitter exhausts playback buffers in real-time interactive media (VoIP, video calls, online gaming), causing audio stutter and frame freezes.

#### Q10: Why compute P95/P99 latency instead of simple arithmetic mean?
> **Answer**: Averages hide extreme spikes. If 99 packets take 20 ms and 1 packet takes 500 ms, the average is 24.8 ms (looks healthy). The P99 percentile accurately reports 500 ms, exposing severe tail latency experienced by users.

#### Q11: What happens when you probe a closed TCP port vs a firewalled port?
> **Answer**: A closed port immediately returns a TCP `RST` segment, caught by Python as `ConnectionRefusedError`. A firewalled port silently drops the SYN packet, causing the socket timer to expire, caught as `socket.timeout`.

#### Q12: Why did you choose a Distributed Star Topology?
> **Answer**: In a Star topology, the monitor sits at the center probing multiple endpoints independently. If a remote cloud host goes down, it does not affect probing of the local gateway. Comparing local gateway RTT (2ms) against public DNS (25ms) instantly pinpoints whether bottlenecks are on the LAN or the ISP link.

#### Q13: How does your anomaly detection engine work?
> **Answer**: `analytics/anomaly_detector.py` evaluates rolling window metrics against configurable thresholds: Loss > 5%, P95 Latency > 100 ms, or Jitter > 20 ms. If breached, it logs a structured anomaly event with observed value, threshold, and reason into SQLite.

#### Q14: What is the network bandwidth overhead of your tool?
> **Answer**: Each ICMP probe is 60 bytes (20B IP + 8B ICMP + 32B payload). At a 5-second interval, bandwidth overhead is ~12 bytes/sec = 96 bps. This is less than 0.0001% of a 100 Mbps broadband link, introducing negligible overhead.

#### Q15: How did you test your implementation?
> **Answer**: We built an automated test suite using Python's `unittest` framework across 5 test files (`test_icmp.py`, `test_collector.py`, `test_runner.py`, `test_metrics.py`, `test_member2.py`). All 37 unit and integration tests passed in 5.53 seconds with 100% success rate.

#### Q16: What are the limitations of ICMP-based monitoring?
> **Answer**: 1. Firewalls often rate-limit or drop ICMP Echo requests; a timeout doesn't always prove the whole server is down. 2. ICMP ping does not measure bandwidth capacity (throughput). 3. ICMP RTT is not application response time.

---

## 5. Step-by-Step Live Demo Script (Follow This During Viva)

1. **Step 1: Show Target Configuration**
   - Open [`config.json`](file:///d:/SEM_5/CN/PROJECT/NetTelemetry/config.json).
   - Point out enabled targets: Google (8.8.8.8), Cloudflare (1.1.1.1), GitHub, and Microsoft.
2. **Step 2: Show Native ICMP Code**
   - Open [`network/icmp_monitor.py`](file:///d:/SEM_5/CN/PROJECT/NetTelemetry/network/icmp_monitor.py).
   - Explain the `ctypes` call to `iphlpapi.IcmpSendEcho`, showing RTT and TTL extraction.
3. **Step 3: Run Automated Test Suite**
   - In terminal, run: `python -m unittest discover tests`
   - Point to output: *"Ran 37 tests in 5.5s ... OK"*.
4. **Step 4: Open Live Streamlit Dashboard**
   - In terminal, run: `streamlit run dashboard/app.py`
   - Show: (1) Target Latency Tiles, (2) Interactive RTT vs Time Plotly graph, (3) Loss & Jitter charts, (4) Dark/Light mode toggle.
5. **Step 5: Demonstrate Anomaly Trigger**
   - Point to an inactive or high-delay target (e.g. Amazon or simulated drop).
   - Show the red anomaly warning tile: *"High packet loss / Latency spike detected"*.
