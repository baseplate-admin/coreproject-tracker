from twisted.web.resource import Resource


from autobahn.twisted.websocket import WebSocketServerFactory
from coreproject_tracker.servers import WebSocketServer


class CombinedResource(Resource):
    isLeaf = True

    def __init__(self, http_resource, ws_resource):
        self.http_resource = http_resource
        self.ws_resource = ws_resource
        super().__init__()

    def render(self, request):
        # Check if the request is an HTTP request or WebSocket upgrade
        if request.getHeader(b"upgrade") == b"websocket":
            # Handle WebSocket request
            ws_factory = WebSocketServerFactory("ws://localhost:8080")
            ws_factory.protocol = WebSocketServer
            ws_factory.buildProtocol(request)
            return self.ws_resource.render(request)
        else:
            # Handle HTTP request
            self.http_resource.server = self.server
            return self.http_resource.render(request)
