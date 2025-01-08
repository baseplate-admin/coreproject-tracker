from twisted.web.resource import Resource


class CombinedResource(Resource):
    isLeaf = True

    def __init__(self, http_resource, ws_resource):
        self.http_resource = http_resource
        self.ws_resource = ws_resource

        super().__init__()

    def render(self, request):
        # Check if the request is an HTTP request or WebSocket upgrade
        if request.getHeader(b"upgrade") == b"websocket":
            # Upgrade to WebSocket
            return self.ws_resource.render(request)

        else:
            # Handle as regular HTTP request
            return self.http_resource.render(request)
