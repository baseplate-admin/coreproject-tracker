import urllib.parse
from http import HTTPStatus
from twisted.web.resource import Resource
from twisted.logger import Logger
from twisted.web.server import Request
from coreproject_tracker.functions.ip import is_valid_ip

log = Logger(namespace="coreproject_tracker")


class AnnouncePage(Resource):
    isLeaf = True

    def render_GET(self, request: Request) -> bytes:
        info_hash_raw = request.args.get(b"info_hash")[0]
        info_hash = urllib.parse.unquote_to_bytes(info_hash_raw).hex()
        if (info_hash_length := len(info_hash_raw)) > 20:
            request.setResponseCode(HTTPStatus.BAD_REQUEST)
            return f"`info_hash` length is {info_hash_length} which is greater than 20".encode()

        port = request.args.get(b"port")[0].decode()
        if not port.isdigit():
            request.setResponseCode(HTTPStatus.BAD_REQUEST)
            return "`port` is not an integer".encode()

        port = int(port)
        if port <= 0 and port >= 65535:
            request.setResponseCode(HTTPStatus.BAD_REQUEST)
            return f"`port` is {port} which is not in range(0, 65535)".encode()

        left = request.args.get(b"left")[0].decode()
        if not left.isdigit():
            request.setResponseCode(HTTPStatus.BAD_REQUEST)
            return "`left` is not an integer".encode()
        left = int(left)

        numwant = request.args.get(b"numwant")[0].decode()
        if not numwant.isdigit():
            request.setResponseCode(HTTPStatus.BAD_REQUEST)
            return b"`numwant` is not an integer"
        numwant = int(numwant)

        peer_ip = request.getClientAddress().host
        if not is_valid_ip(peer_ip):
            request.setResponseCode(HTTPStatus.BAD_REQUEST)
            return "`peer_ip` is not a valid ip".encode()


class HTTPServer(Resource):
    def __init__(self, opts=None):
        super().__init__()
        self.putChild(b"announce", AnnouncePage())

    def render_params(self, params):
        pass

    def parse_request(self, request):
        pass
