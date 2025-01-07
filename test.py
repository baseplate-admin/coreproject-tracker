import ipaddress
import struct


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


# Support for multi and multi6 usage
multi = addrs_to_compact
multi6 = addrs_to_compact

# Example usage
if __name__ == "__main__":
    addrs = ["10.10.10.5:128", "100.56.58.99:28525"]
    compact = addrs_to_compact(addrs)
    print(compact)
