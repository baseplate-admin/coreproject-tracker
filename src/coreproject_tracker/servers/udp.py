from twisted.internet.protocol import DatagramProtocol
from twisted.logger import Logger
import struct
from coreproject_tracker.common import CONNECTION_ID

log = Logger(namespace="coreproject_tracker")


def parse_udp_packet(msg):
    connection_id = struct.unpack(">Q", msg[:8])[0]
    if connection_id != CONNECTION_ID:
        raise ValueError("Error")

    action = struct.unpack(">I", msg[8:12])[0]
    transaction_id = struct.unpack(">I", msg[12:16])[0]

    # Construct the result (similar to the JavaScript object)
    params = {
        "connection_id": connection_id,
        "action": action,
        "transactionId": transaction_id,
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

        print(parse_udp_packet(data))

        # Send a response back to the sender
        response = b"Message received"
        self.transport.write(response, addr)
