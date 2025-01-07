from twisted.internet.protocol import DatagramProtocol


class UDPServer(DatagramProtocol):
    def __init__(self, opts=None):
        self.opts = opts or {}

    def datagramReceived(self, msg, addr):
        pass

    def parse_udp_packet(self, msg, rinfo):
        pass
