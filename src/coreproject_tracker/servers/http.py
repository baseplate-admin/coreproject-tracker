import json
from http import HTTPStatus

import bencodepy
from twisted.internet import defer
from twisted.logger import Logger
from twisted.web import server
from twisted.web.resource import Resource
from twisted.web.server import Request

from coreproject_tracker.common import DEFAULT_ANNOUNCE_PEERS, MAX_ANNOUNCE_PEERS
from coreproject_tracker.constants.interval import ANNOUNCE_INTERVAL
from coreproject_tracker.datastructures import DataStructure
from coreproject_tracker.functions.convertion import bin_to_hex
from coreproject_tracker.functions.ip import is_valid_ip
from coreproject_tracker.singletons.redis import RedisConnectionManager
from coreproject_tracker.functions.redis import hget_with_ttl, hset_with_ttl

log = Logger(namespace="coreproject_tracker")


class AnnouncePage(Resource):
    isLeaf = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Initialize parent class `Resource`
        self.redis_client = RedisConnectionManager.get_client()

        self.datastore = DataStructure()

    def validate_data(self, request: Request) -> dict[str, str | int] | bytes:
        params = {}

        info_hash_raw = request.args[b"info_hash"][0]
        info_hash = info_hash_raw.hex()
        if (info_hash_length := len(info_hash_raw)) > 20:
            raise ValueError(
                f"`info_hash` length is {info_hash_length} which is greater than 20"
            )
        params["info_hash"] = info_hash

        port = request.args[b"port"][0].decode()
        if not port.isdigit():
            raise ValueError("`port` is not an integer")
        port = int(port)
        if port <= 0 and port >= 65535:
            raise ValueError(f"`port` is {port} which is not in range(0, 65535)")
        params["port"] = port

        left = request.args[b"left"][0].decode()
        if not left.isdigit():
            raise ValueError("`left` is not an integer")
        left = int(left)
        params["left"] = left

        numwant = request.args[b"numwant"][0].decode()
        if not numwant.isdigit():
            raise ValueError(b"`numwant` is not an integer")
        numwant = int(numwant)
        params["numwant"] = min(numwant or DEFAULT_ANNOUNCE_PEERS, MAX_ANNOUNCE_PEERS)

        peer_ip = request.getClientAddress().host
        if not is_valid_ip(peer_ip):
            raise ValueError("`peer_ip` is not a valid ip")
        params["peer_ip"] = peer_ip

        peer_id = request.args[b"peer_id"][0].decode()
        if not isinstance(peer_id, str):
            raise ValueError("`peer_id` must be a str")
        params["peer_id"] = bin_to_hex(peer_id)

        return params

    def render_GET(self, request: Request) -> bytes:
        if request.args == {}:
            request.setHeader("Content-Type", "text/html; charset=utf-8")
            return "🐟🐈 ⸜(｡˃ ᵕ ˂ )⸝♡".encode("utf-8")

        try:
            data = self.validate_data(request)
        except ValueError as e:
            request.setResponseCode(HTTPStatus.BAD_REQUEST)
            return bencodepy.bencode({"failure reason": e})

        pass

        peer_count = 0
        peers = []
        seeders = 0
        leechers = 0

        redis_data = json.loads(self.redis_client.get(data["info_hash"]))
        print(type(redis_data))
        for peer in redis_data:
            if peer_count > data["numwant"]:
                break

            if peer["left"] == 0:
                seeders += 1
            else:
                leechers += 1

            peers.append({"ip": peer["peer_ip"], "port": peer["port"]})
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
