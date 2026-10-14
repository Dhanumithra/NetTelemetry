import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

COLOR_BLACK = RGBColor(0, 0, 0)
COLOR_MUTED = RGBColor(70, 70, 70)
HEX_WHITE = "FFFFFF"

def set_cell_background(cell, fill_hex="FFFFFF"):
    shd_xml = f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shd_xml))

def set_cell_margins(cell, top=70, bottom=70, left=110, right=110):
    tcMar = parse_xml(f'''<w:tcMar {nsdecls("w")}>
        <w:top w:w="{top}" w:type="dxa"/>
        <w:bottom w:w="{bottom}" w:type="dxa"/>
        <w:left w:w="{left}" w:type="dxa"/>
        <w:right w:w="{right}" w:type="dxa"/>
    </w:tcMar>''')
    cell._tc.get_or_add_tcPr().append(tcMar)

def set_table_borders(table, color="888888", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''<w:tblBorders {nsdecls("w")}>
        <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
        <w:left w:val="none"/>
        <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
        <w:right w:val="none"/>
        <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
        <w:insideV w:val="none"/>
    </w:tblBorders>''')
    tblPr.append(borders)

def format_clean_table(table, col_widths, headers, data_rows, center_cols=[]):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color="888888", sz="5")
    
    # Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], HEX_WHITE)
        set_cell_margins(hdr_cells[i], top=90, bottom=90, left=110, right=110)
        p = hdr_cells[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (i in center_cols or i > 1) else WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
            run.font.name = "Calibri"
            run.font.size = Pt(9)
            run.font.bold = True
            run.font.color.rgb = COLOR_BLACK
            
    # Data Rows
    for row_idx, row_data in enumerate(data_rows):
        row_cells = table.rows[row_idx + 1].cells
        for col_idx, cell_value in enumerate(row_data):
            row_cells[col_idx].text = str(cell_value)
            set_cell_background(row_cells[col_idx], HEX_WHITE)
            set_cell_margins(row_cells[col_idx], top=70, bottom=70, left=100, right=100)
            p = row_cells[col_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (col_idx in center_cols or col_idx > 1) else WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = "Calibri"
                run.font.size = Pt(8.5)
                run.font.color.rgb = COLOR_BLACK
                if col_idx == 0:
                    run.font.bold = True

    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = Inches(width)

def add_header_footer(doc):
    for s in doc.sections:
        s.top_margin = Inches(0.7)
        s.bottom_margin = Inches(0.7)
        s.left_margin = Inches(0.75)
        s.right_margin = Inches(0.75)
        
        header = s.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("NetTelemetry — Viva Voce & Presentation Cheat-Sheet")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8)
        hrun.font.color.rgb = COLOR_MUTED
        
        footer = s.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("20MSS56 Networks Programming Laboratory • Fast Prep Handbook")
        frun.font.name = "Calibri"
        frun.font.size = Pt(8)
        frun.font.color.rgb = COLOR_MUTED

def add_title_block(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    
    r0 = p.add_run("20MSS56 – NETWORKS PROGRAMMING LABORATORY\n")
    r0.font.name = "Calibri"
    r0.font.size = Pt(10.5)
    r0.font.bold = True
    r0.font.color.rgb = COLOR_BLACK
    
    r1 = p.add_run("VIVA VOCE & PRESENTATION MASTER CHEAT-SHEET\n")
    r1.font.name = "Calibri"
    r1.font.size = Pt(13)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_BLACK
    
    r2 = p.add_run("NetTelemetry: Real-Time Network Health Monitoring and Performance Telemetry\n")
    r2.font.name = "Calibri"
    r2.font.size = Pt(15)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_BLACK
    
    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_before = Pt(3)
    p_auth.paragraph_format.space_after = Pt(3)
    
    ra1 = p_auth.add_run("PRESENTED BY:\n")
    ra1.font.name = "Calibri"
    ra1.font.size = Pt(9.5)
    ra1.font.bold = True
    ra1.font.color.rgb = COLOR_BLACK
    
    ra2 = p_auth.add_run("DHANUMITHRA T (2403717672622011)   &   SREE RAG S (2403717672621050)\n")
    ra2.font.name = "Calibri"
    ra2.font.size = Pt(9.5)
    ra2.font.bold = True
    ra2.font.color.rgb = COLOR_BLACK
    
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_background(cell, HEX_WHITE)
    set_cell_margins(cell, top=60, bottom=60, left=120, right=120)
    
    border_xml = f'''<w:tcBorders {nsdecls("w")}>
        <w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>
        <w:left w:val="single" w:sz="6" w:space="0" w:color="000000"/>
        <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>
        <w:right w:val="single" w:sz="6" w:space="0" w:color="000000"/>
    </w:tcBorders>'''
    cell._tc.get_or_add_tcPr().append(parse_xml(border_xml))
    
    mp = cell.paragraphs[0]
    mp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    mp.paragraph_format.space_before = Pt(0)
    mp.paragraph_format.space_after = Pt(0)
    
    mrun = mp.add_run("Quick-Study Viva Handbook • Concise Q&A • Work Split • Live Demo Script")
    mrun.font.name = "Calibri"
    mrun.font.size = Pt(8.5)
    mrun.font.bold = True
    mrun.font.color.rgb = COLOR_BLACK
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_h1(doc, title_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    
    run = p.add_run(title_text)
    run.font.name = "Calibri"
    run.font.size = Pt(11.5)
    run.font.bold = True
    run.font.color.rgb = COLOR_BLACK
    return p

def add_h2(doc, title_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.keep_with_next = True
    
    run = p.add_run(title_text)
    run.font.name = "Calibri"
    run.font.size = Pt(10)
    run.font.bold = True
    run.font.color.rgb = COLOR_BLACK
    return p

def add_p(doc, text, bold_prefix=None, space_after=3):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.1
    
    if bold_prefix:
        brun = p.add_run(bold_prefix)
        brun.font.name = "Calibri"
        brun.font.size = Pt(9)
        brun.font.bold = True
        brun.font.color.rgb = COLOR_BLACK
        
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(9)
    run.font.color.rgb = COLOR_BLACK
    return p

def add_bullet(doc, title, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(1.5)
    p.paragraph_format.line_spacing = 1.08
    
    trun = p.add_run(title + ": ")
    trun.font.name = "Calibri"
    trun.font.size = Pt(8.5)
    trun.font.bold = True
    trun.font.color.rgb = COLOR_BLACK
    
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(8.5)
    run.font.color.rgb = COLOR_BLACK
    return p

def add_viva_item(doc, q_num, question, answer, concept_tag=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.keep_with_next = True
    
    qrun = p.add_run(f"Q{q_num}: {question}")
    qrun.font.name = "Calibri"
    qrun.font.size = Pt(9)
    qrun.font.bold = True
    qrun.font.color.rgb = COLOR_BLACK
    
    if concept_tag:
        trun = p.add_run(f" [{concept_tag}]")
        trun.font.name = "Calibri"
        trun.font.size = Pt(8)
        trun.font.italic = True
        trun.font.color.rgb = COLOR_MUTED
        
    p_ans = doc.add_paragraph()
    p_ans.paragraph_format.space_before = Pt(0)
    p_ans.paragraph_format.space_after = Pt(4)
    p_ans.paragraph_format.line_spacing = 1.08
    
    arun = p_ans.add_run("Answer: ")
    arun.font.name = "Calibri"
    arun.font.size = Pt(8.5)
    arun.font.bold = True
    arun.font.color.rgb = COLOR_BLACK
    
    ans_run = p_ans.add_run(answer)
    ans_run.font.name = "Calibri"
    ans_run.font.size = Pt(8.5)
    ans_run.font.color.rgb = COLOR_BLACK

def build_cheat_sheet():
    doc = docx.Document()
    add_header_footer(doc)
    add_title_block(doc)
    
    # =========================================================================
    # SECTION 1: 90-SECOND PRESENTATION OPENING PITCH
    # =========================================================================
    add_h1(doc, "1. 90-Second Presentation Pitch (Say This to Start Confidently)")
    add_p(doc, "Good morning, respected examiners. We are presenting NetTelemetry, an active, multi-layer computer network performance monitoring and telemetry system.", bold_prefix="Opening: ")
    add_bullet(doc, "The Core Problem", "Traditional diagnostic tools (like manual ping) only answer a binary question: 'is the server reachable?' In real networks, silent degradation occurs—such as bufferbloat (queueing latency), micro-burst 2-5% packet drops, and jitter—which devastates VoIP, video calls, and web services while the link still appears 'online'.")
    add_bullet(doc, "Our Solution", "NetTelemetry actively probes network endpoints across Layer 3 (ICMP Echo) and Layer 4 (TCP 3-Way Handshake & UDP datagrams). It computes rolling statistics: RTT, TTL, Packet Loss %, Availability %, RFC 3550 Jitter, and P95 latency.")
    add_bullet(doc, "The Output", "An automated anomaly engine flags link degradation when loss > 5% or jitter > 20ms, and a real-time Streamlit NOC dashboard presents live graphs, metric tiles, and incident logs.")

    # =========================================================================
    # SECTION 2: TWO-MEMBER WORK SPLIT QUICK-CARD (WHO DID WHAT)
    # =========================================================================
    add_h1(doc, "2. Work Split Quick-Card (Know Your Exact Parts)")
    
    work_table = doc.add_table(rows=6, cols=3)
    w_headers = ["Project Module", "DHANUMITHRA T (Member 1)", "SREE RAG S (Member 2)"]
    w_widths = [1.6, 2.7, 2.7]
    w_data = [
        ["Network Layer Focus", "Layer 3 (Network Layer) & Core Engine", "Layer 4 (Transport Layer) & Performance Analytics"],
        ["Network Modules Built", "Native Win32 ICMP Echo engine (icmp_monitor.py) via ctypes & DNS Target Manager (target_manager.py)", "TCP 3-way handshake connect timer (tcp_monitor.py), UDP ping (udp_monitor.py), Throughput (throughput_monitor.py)"],
        ["Metrics & Analytics", "Raw RTT timing, TTL extraction, timeout handling, basic loss windows", "RFC 3550 Jitter math, Availability %, P95/P99 latency math (metrics.py), Anomaly Engine (anomaly_detector.py)"],
        ["Database & Polling", "SQLite schema (schema.sql), WAL mode, and ThreadPool continuous runner loop (runner.py)", "Aggregated metrics database functions (db_m2.py) & Streamlit NOC dashboard (app.py)"],
        ["Unit Testing Done", "ICMP reachability, IP byte conversion, and runner loop tests (test_icmp.py, test_runner.py)", "TCP socket connect, UDP ping, jitter math, and anomaly engine tests (test_member2.py, test_metrics.py)"]
    ]
    format_clean_table(work_table, w_widths, w_headers, w_data, center_cols=[0])
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # =========================================================================
    # SECTION 3: KEY NETWORKING CONCEPTS IN 2 LINES (THE WHY & WHERE)
    # =========================================================================
    add_h1(doc, "3. Core Networking Concepts in 2 Lines (Why, Where & How)")
    add_bullet(doc, "Why ICMP Echo? (Layer 3)", "ICMP has no ports or socket buffers; it is answered directly by the remote kernel/router. It measures pure physical and routed path delay.")
    add_bullet(doc, "Why TCP Connect Latency? (Layer 4)", "Measures the time to complete the 3-way handshake (SYN -> SYN-ACK -> ACK). Catches server application backlog queueing and closed/firewalled ports.")
    add_bullet(doc, "Why UDP Ping? (Layer 4)", "Connectionless protocol with no retransmissions or flow control. Shows true unacknowledged packet drop behavior (models VoIP and DNS).")
    add_bullet(doc, "Why Observe TTL?", "8-bit IPv4 header field decremented by 1 at every router hop. Hop Count = Initial TTL - Observed TTL. Detects sudden dynamic BGP routing flaps.")
    add_bullet(doc, "Why Jitter? (RFC 3550)", "Mean absolute difference between consecutive RTTs: 1/(N-1) * sum(|RTT_i - RTT_{i-1}|). High jitter exhausts buffers in VoIP and video calls, causing robotic audio stutter.")
    add_bullet(doc, "Why P95/P99 Latency?", "Averages lie in networking. 99 packets at 20ms and 1 packet at 500ms has an average of 24.8ms (looks fine). P99 reveals the 500ms bufferbloat spike.")
    add_bullet(doc, "Why Native Win32 API via ctypes?", "Opening raw sockets (SOCK_RAW) on Windows requires Administrator privileges. Subprocess ping is slow. We called iphlpapi.dll (IcmpSendEcho) directly—microsecond accuracy without admin rights!")
    add_bullet(doc, "Why ThreadPoolExecutor?", "Concurrent parallel probing. If one target times out (takes 2s), it does not delay or stall the measurement of other responsive targets.")
    add_bullet(doc, "Why SQLite WAL Mode?", "Write-Ahead Logging allows simultaneous background writes from worker threads while the Streamlit web dashboard reads data without database lock collisions.")

    # =========================================================================
    # SECTION 4: TOP 16 VIVA QUESTIONS & BULLETPROOF ANSWERS
    # =========================================================================
    add_h1(doc, "4. Top 16 Viva Questions & Bulletproof Answers (Memorize These)")

    add_viva_item(doc, 1, "Is NetTelemetry just a software dashboard or a true Computer Networks project?",
                  "It is fundamentally a Computer Networks project. All telemetry is generated by active synthetic network probing using ICMP (RFC 792), TCP sockets (RFC 793), and UDP datagrams (RFC 768). We measure packet-level behavior, examine IPv4 headers, and analyze socket handshakes. The database and Streamlit dashboard are merely supporting tools to store and visualize network behavior.",
                  "Identity")

    add_viva_item(doc, 2, "What is the exact difference between ICMP RTT and TCP Connect RTT?",
                  "ICMP RTT measures pure network-layer transmission and propagation delay without socket buffers. TCP Connect RTT measures the 3-way handshake (SYN -> SYN-ACK -> ACK), which includes network delay PLUS remote server socket backlog queueing and transport stack state processing.",
                  "Protocols")

    add_viva_item(doc, 3, "What does the observed TTL value tell us about the remote host and path?",
                  "TTL decrements by 1 at every router. Hop Count = Initial_TTL - Observed_TTL. Standard initial TTL defaults are Linux = 64, Windows = 128. If Google DNS (8.8.8.8) returns TTL=118, it traversed 10 hops (128 - 118). If it drops to 114, it indicates a dynamic routing flap added 4 hops.",
                  "IPv4 Header")

    add_viva_item(doc, 4, "What happens when an IP packet's TTL reaches 0?",
                  "The router discards the packet and sends an ICMP Type 11 (Time Exceeded) message back to the sender. This mechanism prevents packets from circulating infinitely during routing loops.",
                  "Routing")

    add_viva_item(doc, 5, "Why didn't you use raw sockets (socket.SOCK_RAW) for ICMP?",
                  "On Windows, opening SOCK_RAW requires Administrator privileges. To make NetTelemetry run safely as standard non-admin user code, Member 1 used Python ctypes to bind directly to the native Windows IP Helper API (iphlpapi.dll, IcmpSendEcho).",
                  "Implementation")

    add_viva_item(doc, 6, "Why is subprocess ping (os.system or subprocess.run) bad for continuous monitoring?",
                  "Spawning a ping process creates an entire operating system process per probe, consuming heavy CPU. Furthermore, standard ping rounds latency to whole integers, losing microsecond-level delay jitter.",
                  "Performance")

    add_viva_item(doc, 7, "What is Bufferbloat and which delay component does it affect?",
                  "Bufferbloat occurs when intermediate router buffers become overly large and fill with packets during congestion, causing massive queueing delay (d_queue in the nodal delay formula: d_nodal = d_proc + d_queue + d_trans + d_prop) without dropping packets.",
                  "Network Delay")

    add_viva_item(doc, 8, "Why does a 3% packet loss rate severely degrade TCP throughput?",
                  "TCP interprets packet loss as congestion. Under TCP's Additive Increase Multiplicative Decrease (AIMD) algorithm, a lost packet forces TCP to halve its congestion window (cwnd) and wait for retransmissions, collapsing throughput far beyond the 3% loss proportion.",
                  "TCP Congestion")

    add_viva_item(doc, 9, "What is Jitter, what formula did you use, and which applications suffer most?",
                  "Jitter is the delay variation between consecutive packets. We implemented RFC 3550: Jitter = (1/(N-1)) * sum(|RTT_i - RTT_{i-1}|). Jitter exhausts playback buffers in real-time interactive media (VoIP, video calls, online gaming), causing audio stutter and frame freezes.",
                  "QoS")

    add_viva_item(doc, 10, "Why compute P95/P99 latency instead of simple arithmetic mean?",
                  "Averages hide extreme spikes. If 99 packets take 20 ms and 1 packet takes 500 ms, the average is 24.8 ms (looks healthy). The P99 percentile accurately reports 500 ms, exposing severe tail latency experienced by users.",
                  "Statistics")

    add_viva_item(doc, 11, "What happens when you probe a closed TCP port vs a firewalled port?",
                  "A closed port immediately returns a TCP RST segment, caught by Python as ConnectionRefusedError. A firewalled port silently drops the SYN packet, causing the socket timer to expire, caught as socket.timeout.",
                  "Transport Sockets")

    add_viva_item(doc, 12, "Why did you choose a Distributed Star Topology?",
                  "In a Star topology, the monitor sits at the center probing multiple endpoints independently. If a remote cloud host goes down, it does not affect probing of the local gateway. Comparing local gateway RTT (2ms) against public DNS (25ms) instantly pinpoints whether bottlenecks are on the LAN or the ISP link.",
                  "Topology")

    add_viva_item(doc, 13, "How does your anomaly detection engine work?",
                  "analytics/anomaly_detector.py evaluates rolling window metrics against configurable thresholds: Loss > 5%, P95 Latency > 100 ms, or Jitter > 20 ms. If breached, it logs a structured anomaly event with observed value, threshold, and reason into SQLite.",
                  "Anomaly Engine")

    add_viva_item(doc, 14, "What is the network bandwidth overhead of your tool?",
                  "Each ICMP probe is 60 bytes (20B IP + 8B ICMP + 32B payload). At a 5-second interval, bandwidth overhead is ~12 bytes/sec = 96 bps. This is less than 0.0001% of a 100 Mbps broadband link, introducing negligible overhead.",
                  "Overhead")

    add_viva_item(doc, 15, "How did you test your implementation?",
                  "We built an automated test suite using Python's unittest framework across 5 test files (test_icmp.py, test_collector.py, test_runner.py, test_metrics.py, test_member2.py). All 37 unit and integration tests passed in 5.53 seconds with 100% success rate.",
                  "Testing")

    add_viva_item(doc, 16, "What are the limitations of ICMP-based monitoring?",
                  "1. Firewalls often rate-limit or drop ICMP Echo requests; a timeout doesn't always prove the whole server is down. 2. ICMP ping does not measure bandwidth capacity (throughput). 3. ICMP RTT is not application response time.",
                  "Limitations")

    # =========================================================================
    # SECTION 5: STEP-BY-STEP LIVE DEMO WALKTHROUGH
    # =========================================================================
    add_h1(doc, "5. Step-by-Step Live Demo Script (Follow This During Viva)")
    add_bullet(doc, "Step 1: Show Target Configuration", "Open config.json. Point out enabled targets: Google (8.8.8.8), Cloudflare (1.1.1.1), GitHub, and Microsoft.")
    add_bullet(doc, "Step 2: Show Native ICMP Code", "Open network/icmp_monitor.py. Explain the ctypes call to iphlpapi.IcmpSendEcho, showing RTT and TTL extraction.")
    add_bullet(doc, "Step 3: Run Automated Test Suite", "Run `python -m unittest discover tests` in terminal. Show examiners: 'Ran 37 tests in 5.5s ... OK'.")
    add_bullet(doc, "Step 4: Open Live Streamlit Dashboard", "Run `streamlit run dashboard/app.py`. Show: (1) Target Latency Tiles, (2) Interactive RTT vs Time Plotly graph, (3) Loss & Jitter charts, (4) Dark/Light mode toggle.")
    add_bullet(doc, "Step 5: Demonstrate Anomaly Trigger", "Point to an inactive or high-delay target (e.g., Amazon or simulated drop). Show the red anomaly warning tile: 'High packet loss / Latency spike detected'.")

    # Save to both target locations
    root_filename = "NetTelemetry_Viva_Presentation_CheatSheet.docx"
    docs_filename = os.path.join("docs", "NetTelemetry_Viva_Presentation_CheatSheet.docx")
    
    doc.save(root_filename)
    doc.save(docs_filename)
    print(f"Cheat-Sheet Docx successfully created:\n1. {root_filename}\n2. {docs_filename}")

if __name__ == "__main__":
    build_cheat_sheet()
