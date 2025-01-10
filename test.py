import ipaddress


ipv6_addr = "::ffff:192.168.1.1"
ipv4_address = ipv6_to_ipv4(ipv6_addr)
if ipv4_address:
    print(f"IPv4 address: {ipv4_address}")
else:
    print("Not an IPv4-mapped IPv6 address.")
