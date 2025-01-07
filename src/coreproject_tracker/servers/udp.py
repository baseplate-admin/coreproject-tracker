from twisted.internet.protocol import DatagramProtocol
from twisted.protocols import basic


class UDPServer(DatagramProtocol):
    def datagramReceived(self, data, addr):
        """
        Called when a datagram (UDP packet) is received.

        - `data`: The received message.
        - `addr`: The address of the sender (tuple of IP and port).
        """
        print(f"Received message: {data.decode()} from {addr}")

        # Send a response back to the sender
        response = b"Message received"
        self.transport.write(response, addr)
        print(f"Sent response to {addr}")
