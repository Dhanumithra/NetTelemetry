import socket
import time
from typing import Dict, Any

def measure_throughput(host: str, port: int, data_size_bytes: int = 1048576, timeout: int = 10) -> Dict[str, Any]:
    """
    Measures TCP throughput by receiving a specific amount of data.
    """
    start_time = time.time()
    received_bytes = 0
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.sendall(b"GET_DATA")
            
            while received_bytes < data_size_bytes:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                received_bytes += len(chunk)
                
        end_time = time.time()
        duration = end_time - start_time
        throughput_mbps = (received_bytes * 8) / (1000000 * duration) if duration > 0 else 0
        return {
            "success": True,
            "throughput_mbps": round(throughput_mbps, 2),
            "duration_sec": round(duration, 2),
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "throughput_mbps": None,
            "duration_sec": None,
            "error": str(e)
        }
