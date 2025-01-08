import sys

from autobahn.twisted.websocket import WebSocketServerFactory
from redis.asyncio import Redis
from twisted.internet import reactor
from twisted.logger import globalLogPublisher, textFileLogObserver
from twisted.web.server import Site

from coreproject_tracker.servers import (
    HTTPServer,
    UDPServer,
    WebSocketServer,
)
from coreproject_tracker.singletons.redis import RedisConnectionManager


def make_app(udp_port=9000, http_port=8000, websocket_port=8080):
    console_observer = textFileLogObserver(sys.stdout)
    globalLogPublisher.addObserver(console_observer)

    RedisConnectionManager.initialize()
    # UDP Server
    reactor.listenUDP(udp_port, UDPServer())

    # HTTP Server
    root = HTTPServer()
    http_site = Site(root)
    reactor.listenTCP(http_port, http_site)

    # WebSocket Server
    factory = WebSocketServerFactory()
    factory.protocol = WebSocketServer
    reactor.listenTCP(websocket_port, factory)

    return reactor
