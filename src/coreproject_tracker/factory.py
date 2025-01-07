from twisted.internet import reactor
from twisted.web.server import Site
from coreproject_tracker.servers import HTTPServer, WebSocketFactory, UDPServer


def make_app(udp_port=9999, http_port=8080, websocket_port=9000):
    # UDP Server
    reactor.listenUDP(udp_port, UDPServer())
    print(f"UDP server listening on port {udp_port}")

    # HTTP Server
    root = HTTPServer(opts={"action": "announce"})
    http_site = Site(root)
    reactor.listenTCP(http_port, http_site)
    print(f"HTTP server listening on port {http_port}")

    # WebSocket Server
    websocket_port = 9000
    reactor.listenTCP(websocket_port, WebSocketFactory())
    print(f"WebSocket server listening on port {websocket_port}")

    return reactor
