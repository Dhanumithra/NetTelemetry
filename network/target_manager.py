import json
import socket
import re
import ipaddress
from typing import Tuple

from network.settings_manager import (
    DEFAULT_THRESHOLDS,
    validate_thresholds,
    load_thresholds,
    save_thresholds,
    reset_thresholds
)


LABEL_REGEX = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$")
ILLEGAL_CHARS_REGEX = re.compile(r'[;&|`$<>"\n\r\t\\ ]')


def normalize_target_host(host_input: str) -> str:
    """
    Normalizes a target host string:
    - Strips whitespace.
    - Canonicalizes valid IP addresses (e.g. lowercase IPv6).
    - Lowercases DNS hostnames and removes optional trailing dot.
    """
    if not host_input or not isinstance(host_input, str):
        return ""
    cleaned = host_input.strip()
    try:
        ip = ipaddress.ip_address(cleaned)
        return str(ip).lower()
    except ValueError:
        pass
    return cleaned.rstrip(".").lower()


def validate_hostname_or_ip(host_input: str) -> Tuple[bool, str]:
    """
    Strictly validates that the provided input is a valid IPv4 address,
    valid IPv6 address, or standards-compliant DNS hostname.

    Rules:
    - Accepts valid IPv4 addresses (e.g. '1.1.1.1', '8.8.8.8').
    - Accepts valid IPv6 addresses (e.g. '2001:4860:4860::8888', '::1').
    - Accepts valid DNS hostnames (e.g. 'www.google.com', 'google.com').
    - Rejects numeric-only input (e.g. '1234').
    - Rejects malformed IPv4 addresses (e.g. '999.999.999.999', '1.2.3.4.5').
    - Rejects whitespace, empty input, shell metacharacters, and malformed hostnames.
    - Format validation does not require live DNS reachability.
    """
    if not host_input or not isinstance(host_input, str):
        return False, "Target address cannot be empty or blank."

    cleaned = host_input.strip()
    if not cleaned:
        return False, "Target address cannot be empty or blank."

    # Prevent whitespace inside input
    if any(c.isspace() for c in cleaned):
        return False, "Target address cannot contain spaces or whitespace."

    if len(cleaned) > 253:
        return False, "Target address exceeds maximum allowable length of 253 characters."

    # Prevent shell injection metacharacters
    if ILLEGAL_CHARS_REGEX.search(cleaned):
        return False, "Target contains illegal characters, spaces, or command separators."

    # 1. IP address validation (IPv4 and IPv6) via Python's standard ipaddress module
    try:
        ip = ipaddress.ip_address(cleaned)
        return True, f"Valid IPv{ip.version} address."
    except ValueError:
        pass

    # 2. Reject numeric-only input (e.g. '1234')
    if cleaned.isdigit():
        return False, "Invalid target: numeric-only input is not a valid hostname or IP address."

    # 3. Reject malformed IPv4 (strings consisting purely of digits and dots that failed ipaddress validation)
    if all(c.isdigit() or c == "." for c in cleaned):
        return False, "Invalid target: malformed IPv4 address (octets must be between 0 and 255)."

    # 4. Standards-compliant DNS Hostname validation (RFC 952, RFC 1123, RFC 1035, RFC 3696)
    # Strip optional single trailing dot (FQDN root)
    to_check = cleaned[:-1] if cleaned.endswith(".") else cleaned
    labels = to_check.split(".")

    if not labels or any(len(l) == 0 for l in labels):
        return False, "Invalid hostname format: empty label or consecutive dots."

    for l in labels:
        if len(l) > 63:
            return False, f"Invalid hostname: label '{l[:10]}...' exceeds maximum 63 characters."
        if not LABEL_REGEX.match(l):
            return False, f"Invalid hostname label: '{l}' (must be 1-63 alphanumeric chars and cannot start/end with hyphen)."

    # Top-level domain (last label) cannot be all-numeric (RFC 1123 §2.1, RFC 3696 §2)
    if labels[-1].isdigit():
        return False, "Invalid hostname: top-level domain cannot be numeric."

    # Hostname must contain at least one alphabetic character
    if not any(c.isalpha() for c in to_check):
        return False, "Invalid hostname: must contain at least one alphabetic character."

    # For multi-label domains, TLD must be at least 2 characters (e.g. .com, .org, .internal)
    if len(labels) > 1 and len(labels[-1]) < 2:
        return False, "Invalid hostname: top-level domain must be at least 2 characters."

    return True, "Valid hostname."


def load_targets(config_path="config.json"):
    """Load network targets from the project configuration file."""

    with open(config_path, "r") as file:
        config = json.load(file)

    return config.get("targets", [])


def resolve_target(host):
    """Resolve a hostname or IP address to an IP address."""

    try:
        resolved_ip = socket.gethostbyname(host)
        return resolved_ip

    except socket.gaierror:
        return None


def validate_target(target):
    """Validate the basic target configuration."""

    required_fields = ["name", "host", "enabled", "interval", "timeout"]

    for field in required_fields:
        if field not in target:
            return False

    if not isinstance(target["enabled"], bool):
        return False

    if target["interval"] <= 0:
        return False

    if target["timeout"] <= 0:
        return False

    is_valid, _ = validate_hostname_or_ip(target.get("host", ""))
    if not is_valid:
        return False

    return True


def prepare_targets(config_path="config.json"):
    """Load, validate and resolve configured targets."""

    targets = load_targets(config_path)
    prepared_targets = []

    for target in targets:

        if not validate_target(target):
            print(f"Invalid target configuration: {target}")
            continue

        resolved_ip = resolve_target(target["host"])

        if resolved_ip is None:
            print(f"Could not resolve target: {target['host']}")
            continue

        target["resolved_ip"] = resolved_ip
        prepared_targets.append(target)

    return prepared_targets
if __name__ == "__main__":
    targets = prepare_targets()

    for target in targets:
        print(target)