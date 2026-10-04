import socket
import time
from typing import Dict, Any

def measure_udp_ping(host: str, port: int, timeout: int = 5) -> Dict[str, Any]:
    """
    Measures the UDP response time by sending a simple ping message.
    """
    start_time = time.time()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(timeout)
            sock.sendto(b"ping", (host, port))
            # Wait for response
            data, _ = sock.recvfrom(1024)
        end_time = time.time()
        rtt_ms = (end_time - start_time) * 1000
        return {
            "success": True,
            "rtt_ms": round(rtt_ms, 2),
            "error": None
        }
    except socket.timeout:
        return {
            "success": False,
            "rtt_ms": None,
            "error": "timeout"
        }
    except Exception as e:
        return {
            "success": False,
            "rtt_ms": None,
            "error": str(e)
        }
