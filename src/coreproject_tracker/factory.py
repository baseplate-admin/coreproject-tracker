from twisted.internet import reactor
from twisted.web.server import Site
from twisted.internet.endpoints import TCP4ServerEndpoint
from autobahn.twisted.websocket import WebSocketServerFactory
from coreproject_tracker.servers import HTTPServer, WebSocketServer, UDPServer


def make_app(udp_port=9999, http_port=8080, websocket_port=9000):
    # UDP Server
    reactor.listenUDP(udp_port, UDPServer())
    print(f"UDP server listening on port {udp_port}")

    # HTTP Server
    root = HTTPServer()
    http_site = Site(root)
    reactor.listenTCP(http_port, http_site)
    print(f"HTTP server listening on port {http_port}")

    # WebSocket Server
    ws_factory = WebSocketServerFactory(f"ws://127.0.0.1:{websocket_port}")
    ws_factory.protocol = WebSocketServer
    ws_endpoint = TCP4ServerEndpoint(reactor, websocket_port)
    ws_endpoint.listen(ws_factory)
    print(f"WebSocket server listening on port {websocket_port}")

    return reactor
