from twisted.internet.protocol import DatagramProtocol
from twisted.logger import Logger
import struct
from coreproject_tracker.common import CONNECTION_ID
import enum

log = Logger(namespace="coreproject_tracker")


class Actions(enum.IntEnum):
    CONNECT = 0
    ANNOUNCE = 1
    SCRAPE = 2
    ERROR = 3


EVENTS = {
    0: "update",
    1: "completed",
    2: "started",
    3: "stopped",
    4: "paused",
}


def to_uint32(value: int) -> bytes:
    """Convert an integer to a 4-byte unsigned integer in network byte order."""
    return struct.pack(">I", value)


def from_uint64(buf):
    """
    Convert an 8-byte buffer into an unsigned 64-bit integer.
    """
    # Ensure the buffer is 8 bytes long
    if len(buf) != 8:
        raise ValueError("Buffer must be exactly 8 bytes")

    # Unpack the high and low 32-bit parts (big-endian)
    high, low = struct.unpack(">II", buf)

    # Calculate the 64-bit integer
    TWO_PWR_32 = 2**32
    low_unsigned = low if low >= 0 else TWO_PWR_32 + low
    return high * TWO_PWR_32 + low_unsigned


def from_uint32(data):
    return struct.unpack(">I", data)[0]


def from_uint16(data):
    return struct.unpack(">H", data)[0]


def make_udp_packet(params: dict[str, int | bytes | dict]) -> bytes:
    """
    Create UDP packets for BitTorrent tracker protocol.

    Args:
        params: Dictionary containing packet parameters including 'action' and other
               action-specific parameters.

    Returns:
        bytes: The constructed UDP packet

    Raises:
        ValueError: If the action is not implemented
    """
    action = params["action"]

    if action == Actions.CONNECT:
        packet = b"".join(
            [
                to_uint32(Actions.CONNECT),
                to_uint32(params["transaction_id"]),
                params["connection_id"],
            ]
        )

    elif action == Actions.ANNOUNCE:
        packet = b"".join(
            [
                to_uint32(Actions.ANNOUNCE),
                to_uint32(params["transaction_id"]),
                to_uint32(params["interval"]),
                to_uint32(params["incomplete"]),
                to_uint32(params["complete"]),
                params["peers"],
            ]
        )

    elif action == Actions.SCRAPE:
        scrape_response = [
            to_uint32(Actions.SCRAPE),
            to_uint32(params["transaction_id"]),
        ]

        for info_hash, file in params["files"].items():
            scrape_response.extend(
                [
                    to_uint32(file["complete"]),
                    to_uint32(
                        file["downloaded"]
                    ),  # Note: this only provides a lower-bound
                    to_uint32(file["incomplete"]),
                ]
            )

        packet = b"".join(scrape_response)

    elif action == Actions.ERROR:
        packet = b"".join(
            [
                to_uint32(Actions.ERROR),
                to_uint32(params.get("transaction_id", 0)),
                str(params.get("failure_reason", "")).encode(),
            ]
        )

    else:
        raise ValueError(f"Action not implemented: {action}")

    return packet


def parse_udp_packet(msg, addr):
    connection_id = msg[:8]
    connection_id_unpacked = struct.unpack(">Q", msg[:8])[0]
    if connection_id_unpacked != CONNECTION_ID:
        raise ValueError("Error")

    action = from_uint32(msg[8:12])
    transaction_id = from_uint32(msg[12:16])

    # Construct the result (similar to the JavaScript object)
    params = {
        "connection_id": connection_id,
        "action": action,
        "transaction_id": transaction_id,
        "type": "udp",
    }

    if params["action"] == Actions.ANNOUNCE:
        params["info_hash"] = msg[16:36].hex()  # 20 bytes
        params["peer_id"] = msg[36:56].hex()  # 20 bytes
        params["downloaded"] = from_uint64(
            msg[56:64]
        )  # Convert 64-bit unsigned integer
        params["left"] = from_uint64(msg[64:72])  # Convert 64-bit unsigned integer
        params["uploaded"] = from_uint64(msg[72:80])  # Convert 64-bit unsigned integer

        # Read 4-byte unsigned int (big-endian)
        event_id = struct.unpack(">I", msg[80:84])[0]
        params["event"] = EVENTS.get(event_id)
        if not params["event"]:
            raise ValueError("Invalid event")

        params["ip"] = from_uint32(msg[84:88]) or addr[0]
        params["key"] = from_uint32(msg[88:92])

        params["numwant"] = from_uint32(msg[92:96]) or 50  # Default announce peer
        params["port"] = from_uint16(msg[96:98]) or addr[1]
        params["addr"] = f"{params['ip']}:{params['port']}"
        params["compact"] = 1
    return params


class UDPServer(DatagramProtocol):
    def datagramReceived(self, data, addr):
        """
        Called when a datagram (UDP packet) is received.

        - `data`: The received message.
        - `addr`: The address of the sender (tuple of IP and port).
        """
        if (packet_length := len(data)) < 16:
            log.error(
                f"received packet length is {packet_length} is shorter than 16 bytes"
            )

        param = parse_udp_packet(data, addr)
        res = make_udp_packet(param)
        self.transport.write(res, addr)
