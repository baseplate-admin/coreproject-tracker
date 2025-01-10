import json

from autobahn.twisted.websocket import WebSocketServerProtocol

from coreproject_tracker.constants import (
    MAX_ANNOUNCE_PEERS,
    WEBSOCKET_INTERVAL,
)
from coreproject_tracker.functions import (
    bin_to_hex,
    hex_to_bin,
    hget_all_with_ttl,
    hset_with_ttl,
)
from coreproject_tracker.manager import ConnectionManager


class WebSocketServer(WebSocketServerProtocol):
    connection_manager = ConnectionManager()

    def parse_websocket(self, params={}):
        params["type"] = "ws"

        if params["action"] == "announce":
            info_hash_raw = params["info_hash"]
            if not isinstance(info_hash_raw, str):
                raise ValueError("`info_hash` is not a str")
            if (info_hash_length := len(info_hash_raw)) != 20:
                raise ValueError(
                    f"`info_hash` is not a 20 bytes, it is {info_hash_length}"
                )
            info_hash = bin_to_hex(info_hash_raw)
            params["info_hash"] = info_hash

            peer_id = params["peer_id"]
            if not isinstance(peer_id, str):
                raise ValueError("`peer_id` is not a str")
            if (peer_id_length := len(peer_id)) != 20:
                raise ValueError(f"`peer_id` is not a 20 bytes, it is {peer_id_length}")
            params["peer_id"] = bin_to_hex(peer_id)

            if params.get("answer"):
                to_peer_id = params["to_peer_id"]
                if not isinstance(to_peer_id, str):
                    raise ValueError("`to_peer_id` is not a str")
                if (to_peer_id_length := len(peer_id)) != 20:
                    raise ValueError(
                        f"`to_peer_id` is not a 20 bytes, it is {to_peer_id_length}"
                    )
                to_peer_id = bin_to_hex(to_peer_id)

            try:
                params["left"] = (
                    float(params["left"])
                    if params["left"] is not None
                    else float("inf")
                )

            except (ValueError, TypeError, KeyError):
                params["left"] = float("inf")

            if offers := params.get("offers"):
                params["numwant"] = len(offers)
            else:
                params["numwant"] = MAX_ANNOUNCE_PEERS
            params["compact"] = -1

        client_ip = self.transport.getPeer().host
        client_port = self.transport.getPeer().port

        params["ip"] = client_ip
        params["port"] = client_port
        params["addr"] = f"{client_ip}:{client_port}"
        return params

    def onMessage(self, payload, isBinary):
        payload = payload.decode("utf8") if not isBinary else payload
        params = json.loads(payload)
        try:
            data = self.parse_websocket(params)
        except ValueError as e:
            self.sendMessage(
                json.dumps(
                    {
                        "failure reason": e,
                    }
                ),
                isBinary,
            )

        response = {}
        response["action"] = data["action"]
        hset_with_ttl(
            data["info_hash"],
            data["addr"],
            json.dumps(
                {
                    "peer_id": data["peer_id"],
                    "info_hash": data["info_hash"],
                    "peer_ip": data["peer_ip"],
                    "port": data["port"],
                    "left": data["left"],
                }
            ),
        )

        seeders = 0
        leechers = 0

        redis_data = hget_all_with_ttl(data["info_hash"])
        peers_list = [json.loads(peer) for peer in redis_data.values()]

        for peer in peers_list:
            if peer["left"] == 0:
                seeders += 1
            else:
                leechers += 1

        response["completed"] = seeders
        response["incompleted"] = leechers

        if response["action"] == "announce":
            response["info_hash"] = hex_to_bin(params["info_hash"])
            response["interval"] = WEBSOCKET_INTERVAL
            self.sendMessage(json.dumps(response).encode(), isBinary)

        if not params.get("answer"):
            self.sendMessage(json.dumps(response).encode(), isBinary)

        self.connection_manager.add_connection(data["peer_id"], self)

        if (offers := params.get("offers")) and isinstance(offers, list):
            for index, peer in enumerate(peers_list):
                peer_instance = self.connection_manager.get_connection(peer["peer_id"])
                peer_instance.sendMessage(
                    json.dumps(
                        {
                            "action": "announce",
                            "offer": params["offers"][index]["offer"],
                            "offer_id": params["offers"][index]["offer_id"],
                            "peer_id": hex_to_bin(params["peer_id"]),
                            "info_hash": hex_to_bin(params["info_hash"]),
                        }
                    ).encode(),
                    isBinary,
                )

        if params.get("answer"):
            to_peer = self.connection_manager.get_connection(
                bin_to_hex(data["to_peer_id"])
            )

            if to_peer:
                to_peer.sendMessage(
                    json.dumps(
                        {
                            "action": "announce",
                            "answer": params["answer"],
                            "offer_id": params["offer_id"],
                            "peer_id": hex_to_bin(params["peer_id"]),
                            "info_hash": hex_to_bin(params["info_hash"]),
                        }
                    ).encode(),
                    isBinary,
                )
