import sys

from twisted.internet import reactor
from twisted.web.server import Site
from coreproject_tracker.servers import HTTPServer, WebSocketFactory, UDPServer
from twisted.logger import textFileLogObserver, globalLogPublisher


def make_app(udp_port=9999, http_port=8080, websocket_port=9000):
    console_observer = textFileLogObserver(sys.stdout)
    globalLogPublisher.addObserver(console_observer)

    # UDP Server
    reactor.listenUDP(udp_port, UDPServer())

    # HTTP Server
    root = HTTPServer(opts={"action": "announce"})
    http_site = Site(root)
    reactor.listenTCP(http_port, http_site)

    # WebSocket Server
    websocket_port = 9000
    reactor.listenTCP(websocket_port, WebSocketFactory())

    return reactor
