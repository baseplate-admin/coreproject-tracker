import sys

from twisted.internet import reactor
from twisted.web.server import Site
from coreproject_tracker.servers import HTTPServer, UDPServer
from twisted.logger import textFileLogObserver, globalLogPublisher
from twisted.web import resource


def make_app(PORT=3000):
    console_observer = textFileLogObserver(sys.stdout)
    globalLogPublisher.addObserver(console_observer)

    # UDP Server
    udp = UDPServer()

    # HTTP Server
    root = resource.Resource()
    http_resource = HTTPServer()
    root.putChild(b"", http_resource)

    site = Site(root)

    reactor.listenTCP(PORT, site)
    reactor.listenUDP(PORT, udp)

    return reactor
