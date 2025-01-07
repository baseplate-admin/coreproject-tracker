from twisted.web.resource import Resource


# HTTP Protocol
class HTTPServer(Resource):
    isLeaf = True

    def render_GET(self, request):
        print(f"HTTP GET request received: {request.path}")
        return b"Hello, HTTP!"

    def render_POST(self, request):
        data = request.content.read()
        print(f"HTTP POST request received with data: {data.decode()}")
        return b"Data received!"
