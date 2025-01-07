import ipaddress
from coreproject_tracker.common import (
    ACTIONS,
    EVENT_IDS,
    CONNECTION_ID,
    DEFAULT_ANNOUNCE_PEERS,
    MAX_ANNOUNCE_PEERS,
)

TWO_PWR_32 = (1 << 16) * 2


def from_uint64(buf):
    high = int.from_bytes(buf[:4], byteorder="big")
    low = int.from_bytes(buf[4:], byteorder="big")
    low_unsigned = low if low >= 0 else TWO_PWR_32 + low
    return (high * TWO_PWR_32) + low_unsigned


def parse_udp_packet(msg, rinfo):
    if len(msg) < 16:
        raise ValueError("received packet is too short")

    params = {
        "connectionId": msg[:8],  # 64-bit
        "action": int.from_bytes(msg[8:12], byteorder="big"),
        "transactionId": int.from_bytes(msg[12:16], byteorder="big"),
        "type": "udp",
    }

    if not CONNECTION_ID == params["connectionId"]:
        raise ValueError("received packet with invalid connection id")

    if params["action"] == ACTIONS["CONNECT"]:
        # No further params
        pass
    elif params["action"] == ACTIONS["ANNOUNCE"]:
        params["info_hash"] = msg[16:36].hex()  # 20 bytes
        params["peer_id"] = msg[36:56].hex()  # 20 bytes
        params["downloaded"] = from_uint64(msg[56:64])  # TODO: track this?
        params["left"] = from_uint64(msg[64:72])
        params["uploaded"] = from_uint64(msg[72:80])  # TODO: track this?

        event = int.from_bytes(msg[80:84], byteorder="big")
        params["event"] = EVENT_IDS.get(event)
        if not params["event"]:
            raise ValueError("invalid event")

        ip = int.from_bytes(msg[84:88], byteorder="big")  # optional
        params["ip"] = ipaddress.IPv4Address(ip) if ip else rinfo["address"]

        params["key"] = int.from_bytes(
            msg[88:92], byteorder="big"
        )  # Optional: unique random key from client

        params["numwant"] = min(
            int.from_bytes(msg[92:96], byteorder="big")
            if len(msg) > 92
            else DEFAULT_ANNOUNCE_PEERS,
            MAX_ANNOUNCE_PEERS,
        )

        params["port"] = (
            int.from_bytes(msg[96:98], byteorder="big")
            if len(msg) > 96
            else rinfo["port"]
        )  # optional
        params["addr"] = f"{params['ip']}:{params['port']}"  # TODO: ipv6 brackets
        params["compact"] = 1  # UDP is always compact
    elif params["action"] == ACTIONS["SCRAPE"]:  # scrape message
        if (len(msg) - 16) % 20 != 0:
            raise ValueError("invalid scrape message")
        params["info_hash"] = []
        for i in range(0, (len(msg) - 16) // 20):
            info_hash = msg[16 + (i * 20) : 36 + (i * 20)].hex()  # 20 bytes
            params["info_hash"].append(info_hash)
    else:
        raise ValueError(f"Invalid action in UDP packet: {params['action']}")

    return params
