import json
import socket


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