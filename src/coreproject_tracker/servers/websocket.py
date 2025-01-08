import json

from autobahn.twisted.websocket import WebSocketServerProtocol

from coreproject_tracker.datastructures import DataStructure
from coreproject_tracker.functions.convertion import binary_to_hex, hex_to_bin


class WebSocketServer(WebSocketServerProtocol):
    def __init__(self):
        self.datastore = DataStructure()

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
            info_hash = binary_to_hex(info_hash_raw)
            params["info_hash"] = info_hash

            peer_id = params["peer_id"]
            if not isinstance(peer_id, str):
                raise ValueError("`peer_id` is not a str")
            if (peer_id_length := len(peer_id)) != 20:
                raise ValueError(f"`peer_id` is not a 20 bytes, it is {peer_id_length}")
            params["peer_id"] = binary_to_hex(peer_id)

            if params.get("answer", None):
                to_peer_id = params["to_peer_id"]
                if not isinstance(to_peer_id, str):
                    raise ValueError("`to_peer_id` is not a str")
                if (to_peer_id_length := len(peer_id)) != 20:
                    raise ValueError(
                        f"`to_peer_id` is not a 20 bytes, it is {to_peer_id_length}"
                    )
                to_peer_id = binary_to_hex(to_peer_id)

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
                params["numwant"] = 50  # MAX_ANNOUNCE_PEERS
            params["compact"] = -1

        client_ip = self.transport.getPeer().host
        client_port = self.transport.getPeer().port

        params["ip"] = client_ip
        params["port"] = client_port
        params["addr"] = f"{client_ip}:{client_port}"
        return params
        # self.transport.getHost()

    def onMessage(self, payload, isBinary):
        payload = payload.decode("utf8") if not isBinary else payload
        params = json.loads(payload)

        try:
            data = self.parse_websocket(params)
        except ValueError as e:
            self.sendMessage(
                json.load(
                    {
                        "failure reason": e,
                    }
                ),
                isBinary,
            )

        response = {}
        response["action"] = data["action"]
        peers = []

        if response["action"] == "announce":
            response.setdefault("peers", [])
            peers = response.get("peers")
            response["info_hash"] = hex_to_bin(params["info_hash"])
            response["interval"] = 60 * 2

        if not params.get("answer"):
            self.sendMessage(json.loads(response), isBinary)

        if (offers := params.get("offers")) and isinstance(offers, list):
            for peer in peers:
                ...
                #  peers.forEach((peer, i) => {
                #     peer.socket.send(
                #         JSON.stringify({
                #             action: 'announce',
                #             offer: params.offers[i].offer,
                #             offer_id: params.offers[i].offer_id,
                #             peer_id: hex2bin(params.peer_id),
                #             info_hash: hex2bin(params.info_hash),
                #         }),
                #         peer.socket.onSend
                #     );
                #     debug(
                #         'sent offer to %s from %s',
                #         peer.peerId,
                #         params.peer_id
                #     );
                # });
        if params.get("answer"):
            to_peer = self.datastore.get_peers()
