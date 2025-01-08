import asyncio
import sys

from autobahn.twisted.websocket import WebSocketServerFactory
from twisted.internet import asyncioreactor
from twisted.logger import globalLogPublisher, textFileLogObserver
from twisted.web.server import Site

from coreproject_tracker.servers import (
    HTTPServer,
    UDPServer,
    WebSocketServer,
)
from coreproject_tracker.singletons.redis import RedisConnectionManager

# Fix for Windows: Use SelectorEventLoop
if (
    asyncio.get_event_loop_policy().__class__.__name__
    == "WindowsProactorEventLoopPolicy"
):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Install the asyncio reactor (only once)
try:
    asyncioreactor.install()
except RuntimeError:
    pass  # Reactor already installed, no need to do it again


def make_app(udp_port=9000, http_port=8000, websocket_port=8080):
    # Setup logging
    console_observer = textFileLogObserver(sys.stdout)
    globalLogPublisher.addObserver(console_observer)

    # Initialize Redis connection
    RedisConnectionManager.initialize()

    from twisted.internet import reactor  # Import reactor after it's installed

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
