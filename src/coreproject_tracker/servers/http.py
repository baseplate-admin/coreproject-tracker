import json
from http import HTTPStatus

import bencodepy
from twisted.internet import threads
from twisted.logger import Logger
from twisted.web import resource, server
from twisted.web.server import Request

from coreproject_tracker.constants import (
    ANNOUNCE_INTERVAL,
    DEFAULT_ANNOUNCE_PEERS,
    MAX_ANNOUNCE_PEERS,
    PEER_TTL,
)
from coreproject_tracker.functions import (
    bin_to_hex,
    check_ip_type_strict,
    hget_all_with_ttl,
    hset_with_ttl,
    is_valid_ip,
)

log = Logger(namespace="coreproject_tracker")


class HTTPServer(resource.Resource):
    isLeaf = True

    def __init__(self):
        super().__init__()

    def render_GET(self, request: Request):
        deferred = threads.deferToThread(self._render_GET, request)
        deferred.addCallback(self.on_task_done, request)
        deferred.addErrback(self.on_task_error, request)
        return server.NOT_DONE_YET

    def on_task_done(self, result, request):
        request.write(result)
        request.finish()

    def on_task_error(self, failure, request):
        request.write(failure.getErrorMessage().encode())
        request.finish()

    def _render_GET(self, request: Request) -> bytes:
        if request.args == {}:
            request.setHeader("Content-Type", "text/html; charset=utf-8")
            return "🐟🐈 ⸜(｡˃ ᵕ ˂ )⸝♡".encode("utf-8")

        try:
            data = self.validate_data(request)
        except ValueError as e:
            request.setResponseCode(HTTPStatus.BAD_REQUEST)
            return bencodepy.bencode({"failure reason": e})

        hset_with_ttl(
            data["info_hash"],
            f"{data['peer_ip']}:{data['port']}",
            json.dumps(
                {
                    "peer_id": data["peer_id"],
                    "info_hash": data["info_hash"],
                    "peer_ip": data["peer_ip"],
                    "port": data["port"],
                    "left": data["left"],
                }
            ),
            PEER_TTL,
        )

        peer_count = 0
        peers = []
        peers6 = []
        seeders = 0
        leechers = 0

        redis_data = hget_all_with_ttl(data["info_hash"])
        peers_list = redis_data.values()

        for peer in peers_list:
            if peer_count > data["numwant"]:
                break

            peer_data = json.loads(peer)

            if peer_data["left"] == 0:
                seeders += 1
            else:
                leechers += 1

            peer_ip = peer_data["peer_ip"]
            if check_ip_type_strict(peer_ip) == "IPv4":
                peers.append({"ip": peer_data["peer_ip"], "port": peer_data["port"]})
            elif check_ip_type_strict(peer_ip) == "IPv6":
                peers6.append({"ip": peer_data["peer_ip"], "port": peer_data["port"]})
            else:
                raise TypeError("`peer_ip` is not 'ipv4' nor 'ipv6'")

            peer_count += 1

        output = {
            "peers": peers,
            "peers6": peers6,
            "min interval": ANNOUNCE_INTERVAL,
            "complete": seeders,
            "incomplete": leechers,
        }
        return bencodepy.bencode(output)

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
