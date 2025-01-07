from twisted.internet.protocol import DatagramProtocol


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
