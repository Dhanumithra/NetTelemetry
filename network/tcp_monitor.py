import socket
import time
from typing import Dict, Any, Optional

def measure_tcp_connect(host: str, port: int, timeout: int = 5) -> Dict[str, Any]:
    """
    Measures the TCP connection response time to a given host and port.
    """
    start_time = time.time()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))
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
