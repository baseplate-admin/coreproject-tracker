import json

from common import ACTIONS, IPV6_RE, MAX_ANNOUNCE_PEERS, REMOVE_IPV4_MAPPED_IPV6_RE


def handle_ws_request(socket, opts, params):
    if not opts:
        opts = {}

    params = json.loads(params)  # may raise ValueError if the JSON is malformed
    params["type"] = "ws"
    params["socket"] = socket

    if params["action"] == "announce":
        params["action"] = ACTIONS["ANNOUNCE"]

        if isinstance(params["info_hash"], str) and len(params["info_hash"]) == 20:
            params["info_hash"] = params["info_hash"].hex()
        else:
            raise ValueError("invalid info_hash")

        if isinstance(params["peer_id"], str) and len(params["peer_id"]) == 20:
            params["peer_id"] = params["peer_id"].hex()
        else:
            raise ValueError("invalid peer_id")

        if "answer" in params:
            if (
                isinstance(params["to_peer_id"], str)
                and len(params["to_peer_id"]) == 20
            ):
                params["to_peer_id"] = params["to_peer_id"].hex()
            else:
                raise ValueError("invalid `to_peer_id` (required with `answer`)")

        params["left"] = (
            float(params["left"])
            if params["left"].replace(".", "", 1).isdigit()
            else float("inf")
        )

        params["numwant"] = min(len(params.get("offers", [])) or 0, MAX_ANNOUNCE_PEERS)
        params[
            "compact"
        ] = -1  # return full peer objects (used for websocket responses)

    elif params["action"] == "scrape":
        params["action"] = ACTIONS["SCRAPE"]

        if isinstance(params["info_hash"], str):
            params["info_hash"] = [params["info_hash"]]

        if isinstance(params["info_hash"], list):
            params["info_hash"] = [
                binary_info_hash.hex()
                if isinstance(binary_info_hash, str) and len(binary_info_hash) == 20
                else ValueError("invalid info_hash")
                for binary_info_hash in params["info_hash"]
            ]
        else:
            raise ValueError("invalid info_hash")

    else:
        raise ValueError(f"invalid action in WS request: {params['action']}")

    # On first parse, save important data from `socket.upgradeReq` and delete it
    if hasattr(socket, "upgradeReq"):
        if opts.get("trustProxy"):
            if "x-forwarded-for" in socket.upgradeReq.headers:
                real_ip = (
                    socket.upgradeReq.headers["x-forwarded-for"].split(",")[0].strip()
                )
                socket.ip = real_ip
            else:
                socket.ip = socket.upgradeReq.connection.remoteAddress
        else:
            socket.ip = socket.upgradeReq.connection.remoteAddress.replace(
                REMOVE_IPV4_MAPPED_IPV6_RE, ""
            )  # force ipv4

        socket.port = socket.upgradeReq.connection.remotePort
        if socket.port:
            socket.addr = f"{f'[{socket.ip}]' if IPV6_RE.match(socket.ip) else socket.ip}:{socket.port}"

        socket.headers = socket.upgradeReq.headers

        # Delete `socket.upgradeReq` to reduce memory usage
        socket.upgradeReq = None

    params["ip"] = socket.ip
    params["port"] = socket.port
    params["addr"] = socket.addr
    params["headers"] = socket.headers

    return params
