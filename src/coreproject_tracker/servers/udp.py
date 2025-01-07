from twisted.internet.protocol import DatagramProtocol


# UDP Protocol
class UDPServer(DatagramProtocol):
    def datagramReceived(self, data, addr):
        print(f"Received {data} from {addr}")
        self.transport.write(data, addr)
