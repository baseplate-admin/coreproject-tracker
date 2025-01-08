from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
from autobahn.twisted.resource import WebSocketResource


# HTTP Resource to handle standard HTTP requests
class MyHTTPResource(Resource):
    isLeaf = True

    def render_GET(self, request):
        return b"Hello, this is an HTTP response!"


# WebSocket Protocol for handling WebSocket connections
class MyWebSocketProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print(f"Client connecting: {request.peer}")

    def onOpen(self):
        print("WebSocket connection open")

    def onMessage(self, msg, binary):
        print(f"Message received: {msg}")
        self.sendMessage(f"Echo: {msg}".encode("utf8"))

    def onClose(self, reason):
        print(f"WebSocket connection closed: {reason}")


# WebSocket Factory
ws_factory = WebSocketServerFactory("ws://localhost:8080")
ws_factory.protocol = MyWebSocketProtocol

# WebSocket Resource
ws_resource = WebSocketResource(ws_factory)


# Main Resource that handles both HTTP and WebSocket
class CombinedResource(Resource):
    isLeaf = True

    def __init__(self, http_resource, ws_resource):
        self.http_resource = http_resource
        self.ws_resource = ws_resource

    def render(self, request):
        # Check if the request is an HTTP request or WebSocket upgrade
        if request.getHeader(b"upgrade") == b"websocket":
            # Upgrade to WebSocket
            return self.ws_resource.render(request)

        else:
            # Handle as regular HTTP request
            return self.http_resource.render(request)


# Create the HTTP and WebSocket resources
http_resource = MyHTTPResource()
combined_resource = CombinedResource(http_resource, ws_resource)

# Create the Site and listen on port 8080
site = Site(combined_resource)
reactor.listenTCP(8080, site)
reactor.run()
