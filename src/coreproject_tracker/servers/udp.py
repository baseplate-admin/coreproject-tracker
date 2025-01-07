import ipaddress
from twisted.internet.protocol import DatagramProtocol
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


class UDPServer(DatagramProtocol):
    def __init__(self, opts=None):
        self.opts = opts or {}

    def datagramReceived(self, msg, addr):
        # This method is called when a UDP datagram is received
        try:
            params = self.parse_udp_packet(msg, addr)
            print("Received params:", params)  # Log or process params here
        except ValueError as e:
            print(f"Error processing packet from {addr}: {str(e)}")

    def parse_udp_packet(self, msg, rinfo):
        pass
