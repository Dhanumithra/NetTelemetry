import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import socket
import sys

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


def ip_to_dword(ip_str):
    """Convert IP string to 32-bit integer in network byte order."""
    packed = socket.inet_aton(ip_str)
    return ctypes.c_ulong.from_buffer_copy(packed).value


def ping(ip_address, timeout_ms=1000, payload=b"NetTelemetry"):
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
                    # Backward compatibility fields
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
                    # Backward compatibility fields
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
                # Backward compatibility fields
                "ip": ip_address,
                "status": "Failed"
            }
    finally:
        IcmpCloseHandle(handle)


if __name__ == "__main__":
    result = ping("8.8.8.8")
    print("Ping Result:", result)
