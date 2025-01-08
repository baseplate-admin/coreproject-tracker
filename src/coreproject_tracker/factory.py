import sys

from twisted.internet import reactor
from twisted.web.server import Site
from coreproject_tracker.servers import HTTPServer, UDPServer, WebSocketServer
from twisted.logger import textFileLogObserver, globalLogPublisher
from coreproject_tracker.resources.main import CombinedResource
from autobahn.twisted.resource import WebSocketResource
from autobahn.twisted.websocket import WebSocketServerFactory


def make_app(PORT=3000):
    console_observer = textFileLogObserver(sys.stdout)
    globalLogPublisher.addObserver(console_observer)

    # UDP Server
    udp = UDPServer()

    # HTTP and Websocket Server
    http_resource = HTTPServer()

    websocket_factory = WebSocketServerFactory()
    websocket_factory.protocol = WebSocketServer
    websocket_resource = WebSocketResource(websocket_factory)

    root = CombinedResource(http_resource, websocket_resource)
    site = Site(root)

    reactor.listenTCP(PORT, site)
    reactor.listenUDP(PORT, udp)

    return reactor
