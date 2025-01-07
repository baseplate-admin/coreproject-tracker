import ipaddress

__all__ = ["is_valid_ip"]


def is_valid_ip(ip: str):
    try:
        # Try to create an IP address object (this works for both IPv4 and IPv6)
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
