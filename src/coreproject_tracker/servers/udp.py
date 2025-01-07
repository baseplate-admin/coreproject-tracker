from twisted.internet.protocol import DatagramProtocol
from twisted.logger import Logger
import struct
from coreproject_tracker.common import CONNECTION_ID

log = Logger(namespace="coreproject_tracker")


class Actions:
    CONNECT = 0
    ANNOUNCE = 1
    SCRAPE = 2
    ERROR = 3


def to_uint32(value: int) -> bytes:
    """Convert an integer to a 4-byte unsigned integer in network byte order."""
    return struct.pack(">I", value)


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
    print(params)
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


def parse_udp_packet(msg):
    connection_id = msg[:8]
    connection_id_unpacked = struct.unpack(">Q", msg[:8])[0]
    if connection_id_unpacked != CONNECTION_ID:
        raise ValueError("Error")

    action = struct.unpack(">I", msg[8:12])[0]
    transaction_id = struct.unpack(">I", msg[12:16])[0]

    # Construct the result (similar to the JavaScript object)
    params = {
        "connection_id": connection_id,
        "action": action,
        "transaction_id": transaction_id,
        "type": "udp",
    }

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

        param = parse_udp_packet(data)
        res = make_udp_packet(param)
        self.transport.write(res, addr)
