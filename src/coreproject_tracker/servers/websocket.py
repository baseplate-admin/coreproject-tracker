from autobahn.twisted.websocket import WebSocketServerProtocol
import enum
import json
from coreproject_tracker.functions.convertion import binary_to_hex


class Actions(enum.IntEnum):
    CONNECT = 0
    ANNOUNCE = 1
    SCRAPE = 2
    ERROR = 3


class WebSocketServer(WebSocketServerProtocol):
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
            except (ValueError, TypeError):
                params["left"] = float("inf")

            offers = params.get("offers")
            if offers:
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

    def onConnect(self, request):
        print(f"Client connecting: {request.peer}")

    def onOpen(self):
        print("WebSocket connection opened")

    def onMessage(self, payload, isBinary):
        payload = payload.decode("utf8") if not isBinary else payload
        params = json.loads(payload)
        try:
            data = self.parse_websocket(params)
        except ValueError:
            pass
        print(data)

    def onClose(self, wasClean, code, reason):
        print(f"WebSocket closed: {reason} (code: {code}, clean: {wasClean})")
