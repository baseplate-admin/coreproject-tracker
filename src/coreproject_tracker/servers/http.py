from twisted.web.resource import Resource
import json


class HTTPServer(Resource):
    isLeaf = True  # To handle only one resource (like a single endpoint)

    def __init__(self, opts=None):
        self.opts = opts or {}

    def render_GET(self, request):
        # This method is called when a GET request is received
        try:
            params = self.parse_request(request)
            return self.render_params(params)
        except ValueError as e:
            request.setResponseCode(400)  # Bad request
            return f"Error: {str(e)}"

    def render_params(self, params):
        # This can return a JSON response or any format depending on the application
        return json.dumps(params)

    def parse_request(self, request):
        pass
