from twisted.web.resource import Resource
from coreproject_tracker.servers import WebSocketServer, HTTPServer
from autobahn.twisted.websocket import WebSocketServerFactory
from twisted.web.server import Request
from autobahn.twisted.resource import WebSocketResource


# Main handler that distinguishes between WebSocket and HTTP
class MainResource(Resource):
    def __init__(self):
        self.httpServer = HTTPServer()

    def render(self, request: Request):
        # Check if this is a WebSocket handshake (based on headers)
        if (
            request.getHeader("Upgrade") == "websocket"
            and request.getHeader("Connection") == "Upgrade"
        ):
            # WebSocket handshake and upgrade
            factory = WebSocketServerFactory()
            factory.protocol = WebSocketServer
            websocket_resource = WebSocketResource(factory)
            return websocket_resource.render(request)

        # Handle as an HTTP request if it's not a WebSocket upgrade
        return self.httpServer.render(request)
