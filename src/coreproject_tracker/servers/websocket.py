import json
import time
import weakref
from threading import Lock

from autobahn.twisted.websocket import WebSocketServerProtocol

from coreproject_tracker.constants import (
    CONNECTION_TTL,
    MAX_ANNOUNCE_PEERS,
    PEER_TTL,
    WEBSOCKET_INTERVAL,
)
from coreproject_tracker.functions import (
    bin_to_hex,
    hex_to_bin,
    hget_all_with_ttl,
    hset_with_ttl,
)


class ConnectionManager:
    def __init__(self):
        # Store connections and their last activity time
        self._connections: dict[str, (weakref.ref, float)] = {}
        self._inactive_timeout = CONNECTION_TTL
        self._lock = Lock()

    def add_connection(
        self, identifier: str, connection: WebSocketServerProtocol
    ) -> None:
        """
        Store a websocket connection with an identifier and current timestamp
        Uses weakref to avoid memory leaks
        """
        with self._lock:
            self._connections[identifier] = (weakref.ref(connection), time.time())
            self._cleanup_stale_connections()

    def remove_connection(self, identifier: str) -> None:
        """Remove a connection from storage"""
        with self._lock:
            if identifier in self._connections:
                del self._connections[identifier]

    def get_connection(self, identifier: str) -> WebSocketServerProtocol | None:
        """
        Retrieve a connection by its identifier
        Updates the last activity timestamp when connection is accessed
        """
        with self._lock:
            if identifier in self._connections:
                connection_ref, _ = self._connections[identifier]
                connection = connection_ref()

                if connection is not None and connection.connected:
                    # Update last activity time
                    self._connections[identifier] = (connection_ref, time.time())
                    return connection
                else:
                    # Clean up dead reference
                    self.remove_connection(identifier)

            self._cleanup_stale_connections()
            return None

    def _cleanup_stale_connections(self) -> None:
        """Remove connections that haven't been active for longer than the timeout"""
        current_time = time.time()
        dead_connections = []

        for identifier, (connection_ref, last_active) in self._connections.items():
            connection = connection_ref()

            # Remove if connection is dead or inactive
            if (
                connection is None
                or not connection.connected
                or (current_time - last_active) > self._inactive_timeout
            ):
                dead_connections.append(identifier)

        # Clean up identified dead/stale connections
        for identifier in dead_connections:
            self.remove_connection(identifier)


class WebSocketServer(WebSocketServerProtocol):
    connection_manager = ConnectionManager(inactive_timeout=600)

    def __init__(self):
        super().__init__()

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
            data["peer_id"],
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
