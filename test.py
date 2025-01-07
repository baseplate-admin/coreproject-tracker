import ipaddress
import struct


# Example usage
if __name__ == "__main__":
    addrs = ["10.10.10.5:128", "100.56.58.99:28525"]
    compact = addrs_to_compact(addrs)
    print(compact)
