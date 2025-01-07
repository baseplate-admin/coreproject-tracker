import re
from coreproject_tracker.common import (
    querystring_parse,
    ACTIONS,
    REMOVE_IPV4_MAPPED_IPV6_RE,
    IPV6_RE,
    DEFAULT_ANNOUNCE_PEERS,
    MAX_ANNOUNCE_PEERS,
)


def parse_request(req, opts=None):
    if opts is None:
        opts = {}

    url_parts = req["url"].split("?")
    params = querystring_parse(url_parts[1]) if len(url_parts) > 1 else {}
    params["type"] = "http"

    if opts.get("action") == "announce" or url_parts[0] == "/announce":
        params["action"] = ACTIONS["ANNOUNCE"]

        if (
            not isinstance(params.get("info_hash"), str)
            or len(params["info_hash"]) != 20
        ):
            raise ValueError("invalid info_hash")
        params["info_hash"] = params["info_hash"].hex()

        if not isinstance(params.get("peer_id"), str) or len(params["peer_id"]) != 20:
            raise ValueError("invalid peer_id")
        params["peer_id"] = params["peer_id"].hex()

        params["port"] = int(params.get("port", 0))
        if params["port"] <= 0 or params["port"] > 65535:
            raise ValueError("invalid port")

        params["left"] = float(params.get("left", "inf"))
        if params["left"] == float("nan"):
            params["left"] = float("inf")

        params["compact"] = int(params.get("compact", 0))
        params["numwant"] = min(
            int(params.get("numwant", DEFAULT_ANNOUNCE_PEERS)),
            MAX_ANNOUNCE_PEERS,
        )

        if opts.get("trustProxy"):
            if "x-forwarded-for" in req["headers"]:
                real_ip = req["headers"]["x-forwarded-for"].split(",")[0].strip()
                params["ip"] = real_ip
            else:
                params["ip"] = req["connection"]["remoteAddress"]
        else:
            params["ip"] = re.sub(
                REMOVE_IPV4_MAPPED_IPV6_RE, "", req["connection"]["remoteAddress"]
            )

        params["addr"] = (
            f"{f'[{params['ip']}]' if IPV6_RE.match(params['ip']) else params['ip']}:{params['port']}"
        )
        params["headers"] = req["headers"]

    elif opts.get("action") == "scrape" or url_parts[0] == "/scrape":
        params["action"] = ACTIONS["SCRAPE"]

        if isinstance(params.get("info_hash"), str):
            params["info_hash"] = [params["info_hash"]]
        if isinstance(params.get("info_hash"), list):
            params["info_hash"] = [
                binary_info_hash.hex()
                if isinstance(binary_info_hash, str) and len(binary_info_hash) == 20
                else ValueError("invalid info_hash")
                for binary_info_hash in params["info_hash"]
            ]
    else:
        raise ValueError(f"invalid action in HTTP request: {req['url']}")

    return params
