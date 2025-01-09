import ipaddress
import struct
from typing import Literal


def is_valid_ip(ip: str):
    try:
        # Try to create an IP address object (this works for both IPv4 and IPv6)
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def addr_to_ip_port(addr):
    """Convert address in the format [IP]:[PORT] to a tuple (IP, PORT)."""
    if not isinstance(addr, str):
        raise ValueError("Address must be a string in the format [IP]:[PORT]")
    parts = addr.rsplit(":", 1)
    if len(parts) != 2:
        raise ValueError("Invalid address format, expecting: [IP]:[PORT]")
    ip = parts[0]
    port = int(parts[1])
    return ip, port


def addrs_to_compact(addrs):
    """Convert a list of addresses to compact format."""
    if isinstance(addrs, str):
        addrs = [addrs]

    compact = bytearray()
    for addr in addrs:
        ip, port = addr_to_ip_port(addr)
        ip_obj = ipaddress.ip_address(ip)  # Parse the IP address
        ip_bytes = ip_obj.packed  # Convert to byte representation
        port_bytes = struct.pack("!H", port)  # Convert port to 2-byte big-endian
        compact.extend(ip_bytes + port_bytes)

    return bytes(compact)


def check_ip_type(address) -> Literal["IPv4"] | Literal["IPv6"]:
    try:
        ip = ipaddress.ip_address(address)
        if isinstance(ip, ipaddress.IPv4Address):
            return "IPv4"
        elif isinstance(ip, ipaddress.IPv6Address):
            return "IPv6"
    except ValueError:
        return "Invalid IP address"
