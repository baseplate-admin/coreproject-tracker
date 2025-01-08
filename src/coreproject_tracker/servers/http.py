import urllib.parse
from http import HTTPStatus
from twisted.web.resource import Resource
from twisted.logger import Logger
from twisted.web.server import Request
from coreproject_tracker.functions.ip import is_valid_ip
from coreproject_tracker.datastructures import DataStructure
import bencodepy
from coreproject_tracker.constants.interval import ANNOUNCE_INTERVAL

log = Logger(namespace="coreproject_tracker")


class AnnouncePage(Resource):
    isLeaf = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.datastore = DataStructure()

    def validate_data(self, request: Request) -> dict[str, str | int] | bytes:
        params = {}

        info_hash_raw = request.args.get(b"info_hash")[0]
        info_hash = urllib.parse.unquote_to_bytes(info_hash_raw).hex()
        if (info_hash_length := len(info_hash_raw)) > 20:
            request.setResponseCode(HTTPStatus.BAD_REQUEST)
            return f"`info_hash` length is {info_hash_length} which is greater than 20".encode()
        params["info_hash"] = info_hash

        port = request.args.get(b"port")[0].decode()
        if not port.isdigit():
            request.setResponseCode(HTTPStatus.BAD_REQUEST)
            return "`port` is not an integer".encode()
        port = int(port)
        if port <= 0 and port >= 65535:
            request.setResponseCode(HTTPStatus.BAD_REQUEST)
            return f"`port` is {port} which is not in range(0, 65535)".encode()
        params["port"] = port

        left = request.args.get(b"left")[0].decode()
        if not left.isdigit():
            request.setResponseCode(HTTPStatus.BAD_REQUEST)
            return "`left` is not an integer".encode()
        left = int(left)
        params["left"] = left

        numwant = request.args.get(b"numwant")[0].decode()
        if not numwant.isdigit():
            request.setResponseCode(HTTPStatus.BAD_REQUEST)
            return b"`numwant` is not an integer"
        numwant = int(numwant)
        params["numwant"] = numwant

        peer_ip = request.getClientAddress().host
        if not is_valid_ip(peer_ip):
            request.setResponseCode(HTTPStatus.BAD_REQUEST)
            return "`peer_ip` is not a valid ip".encode()
        params["peer_ip"] = peer_ip

        return params

    def render_GET(self, request: Request) -> bytes:
        if request.args == {}:
            request.setHeader("Content-Type", "text/html; charset=utf-8")
            return "🐟🐈 ⸜(｡˃ ᵕ ˂ )⸝♡".encode("utf-8")

        data = self.validate_data(request)
        # If there is error in data, it should be in bytes
        if isinstance(data, bytes):
            return data

        self.datastore.add_peer(
            data["info_hash"], data["peer_ip"], data["port"], data["left"], 3600
        )

        peer_count = 0
        peers = []
        seeders = 0
        leechers = 0

        for peer in self.datastore.get_peers(data["info_hash"]):
            if peer_count > data["numwant"]:
                break

            if peer.left == 0:
                seeders += 1
            else:
                leechers += 1

            peers.append({"ip": peer.peer_ip, "port": peer.port})
            peer_count += 1

        output = {
            "peers": peers,
            "min interval": ANNOUNCE_INTERVAL,
            "complete": seeders,
            "incomplete": leechers,
        }
        return bencodepy.bencode(output)


class HTTPServer(Resource):
    def __init__(self):
        super().__init__()
        self.putChild(b"announce", AnnouncePage())
