import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import socket
import sys
import subprocess
import platform
import re
import time
from typing import Dict, Any

class IP_OPTION_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("Ttl", ctypes.c_ubyte),
        ("Tos", ctypes.c_ubyte),
        ("Flags", ctypes.c_ubyte),
        ("OptionsSize", ctypes.c_ubyte),
        ("OptionsData", ctypes.c_void_p),
    ]

class ICMP_ECHO_REPLY(ctypes.Structure):
    _fields_ = [
        ("Address", ctypes.c_ulong),
        ("Status", ctypes.c_ulong),
        ("RoundTripTime", ctypes.c_ulong),
        ("DataSize", ctypes.c_ushort),
        ("Reserved", ctypes.c_ushort),
        ("Data", ctypes.c_void_p),
        ("Options", IP_OPTION_INFORMATION),
    ]

if sys.platform == "win32":
    iphlpapi = ctypes.windll.iphlpapi
    
    IcmpCreateFile = iphlpapi.IcmpCreateFile
    IcmpCreateFile.restype = wintypes.HANDLE
    IcmpCreateFile.argtypes = []

    IcmpCloseHandle = iphlpapi.IcmpCloseHandle
    IcmpCloseHandle.restype = wintypes.BOOL
    IcmpCloseHandle.argtypes = [wintypes.HANDLE]

    IcmpSendEcho = iphlpapi.IcmpSendEcho
    IcmpSendEcho.restype = wintypes.DWORD
    IcmpSendEcho.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPCSTR,
        wintypes.WORD,
        ctypes.POINTER(IP_OPTION_INFORMATION),
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD
    ]
else:
    iphlpapi = None


def ip_to_dword(ip_str: str) -> int:
    """Convert IP string to 32-bit integer in network byte order."""
    packed = socket.inet_aton(ip_str)
    return ctypes.c_ulong.from_buffer_copy(packed).value


def ping(ip_address: str, timeout_ms: int = 1000, payload: bytes = b"NetTelemetry") -> Dict[str, Any]:
    """
    Send ICMP Echo request using Windows IcmpSendEcho via ctypes.
    Returns structured measurement dict matching project data contract.
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    if sys.platform != "win32" or not iphlpapi:
        return {
            "timestamp": timestamp,
            "target": ip_address,
            "protocol": "ICMP",
            "test_type": "echo",
            "success": False,
            "rtt_ms": None,
            "ttl": None,
            "error": "Platform not supported",
            "ip": ip_address,
            "status": "Failed"
        }

    handle = IcmpCreateFile()
    if handle == wintypes.HANDLE(-1).value or handle == 0:
        return {
            "timestamp": timestamp,
            "target": ip_address,
            "protocol": "ICMP",
            "test_type": "echo",
            "success": False,
            "rtt_ms": None,
            "ttl": None,
            "error": "Could not create ICMP handle",
            "ip": ip_address,
            "status": "Failed"
        }

    try:
        dest_addr = ip_to_dword(ip_address)
        request_data = payload
        request_size = len(payload)
        
        reply_size = ctypes.sizeof(ICMP_ECHO_REPLY) + request_size + 8
        reply_buffer = ctypes.create_string_buffer(reply_size)

        replies = IcmpSendEcho(
            handle,
            dest_addr,
            request_data,
            request_size,
            None,
            reply_buffer,
            reply_size,
            timeout_ms
        )

        if replies > 0:
            reply = ICMP_ECHO_REPLY.from_buffer(reply_buffer)
            if reply.Status == 0:  # IP_SUCCESS
                return {
                    "timestamp": timestamp,
                    "target": ip_address,
                    "protocol": "ICMP",
                    "test_type": "echo",
                    "success": True,
                    "rtt_ms": float(reply.RoundTripTime),
                    "ttl": int(reply.Options.Ttl),
                    "error": None,
                    "ip": ip_address,
                    "status": "Success",
                    "bytes": reply.DataSize
                }
            else:
                return {
                    "timestamp": timestamp,
                    "target": ip_address,
                    "protocol": "ICMP",
                    "test_type": "echo",
                    "success": False,
                    "rtt_ms": None,
                    "ttl": None,
                    "error": "timeout" if reply.Status == 11010 else f"status_code_{reply.Status}",
                    "ip": ip_address,
                    "status": "Timeout",
                    "status_code": reply.Status
                }
        else:
            return {
                "timestamp": timestamp,
                "target": ip_address,
                "protocol": "ICMP",
                "test_type": "echo",
                "success": False,
                "rtt_ms": None,
                "ttl": None,
                "error": f"IcmpSendEcho returned 0, error code: {ctypes.GetLastError()}",
                "ip": ip_address,
                "status": "Failed"
            }
    finally:
        IcmpCloseHandle(handle)


def ping_target(host: str, timeout_sec: int = 2) -> Dict[str, Any]:
    """
    Performs an ICMP ping observation to the destination host.
    Uses Win32 ICMP API and falls back to system ping utility if necessary.
    """
    # Try ctypes ping first using resolved IP
    try:
        resolved_ip = socket.gethostbyname(host)
        res = ping(resolved_ip, timeout_ms=int(timeout_sec * 1000))
        if res.get("success"):
            return {
                "success": True,
                "rtt_ms": res.get("rtt_ms"),
                "ttl": res.get("ttl"),
                "error": None
            }
    except socket.gaierror:
        return {"success": False, "rtt_ms": None, "ttl": None, "error": f"DNS resolution failed for '{host}'"}
    except Exception:
        pass

    # Subprocess ping fallback
    system = platform.system().lower()
    start_time = time.time()
    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", str(int(timeout_sec * 1000)), host]
    else:
        cmd = ["ping", "-c", "1", "-W", str(timeout_sec), host]

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_sec + 2
        )
        elapsed_total = (time.time() - start_time) * 1000
        output = proc.stdout

        if proc.returncode == 0:
            time_match = re.search(r"time[=<](\d+(?:\.\d+)?)\s*ms", output, re.IGNORECASE)
            ttl_match = re.search(r"TTL=(\d+)", output, re.IGNORECASE)
            rtt_ms = float(time_match.group(1)) if time_match else round(elapsed_total, 2)
            ttl = int(ttl_match.group(1)) if ttl_match else 64
            return {"success": True, "rtt_ms": rtt_ms, "ttl": ttl, "error": None}
        else:
            err = "Request timed out" if ("timeout" in output.lower() or "timed out" in output.lower()) else "Ping probe failed"
            return {"success": False, "rtt_ms": None, "ttl": None, "error": err}
    except Exception as e:
        return {"success": False, "rtt_ms": None, "ttl": None, "error": str(e)}


if __name__ == "__main__":
    result = ping("8.8.8.8")
    print("Ping Result:", result)
