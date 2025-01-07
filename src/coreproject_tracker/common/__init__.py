import re
from urllib.parse import urlencode, parse_qs, urlparse, urlunparse

# Regular expressions
IPV4_RE = re.compile(r"^[\d.]+$")
IPV6_RE = re.compile(r"^[\da-fA-F:]+$")
REMOVE_IPV4_MAPPED_IPV6_RE = re.compile(r"^::ffff:")

# Constants
CONNECTION_ID = (0x417 << 32) | 0x27101980
ACTIONS = {"CONNECT": 0, "ANNOUNCE": 1, "SCRAPE": 2, "ERROR": 3}
EVENTS = {
    "update": 0,
    "completed": 1,
    "started": 2,
    "stopped": 3,
    "paused": 4,
}
EVENT_IDS = {v: k for k, v in EVENTS.items()}
EVENT_NAMES = {
    "update": "update",
    "completed": "complete",
    "started": "start",
    "stopped": "stop",
    "paused": "pause",
}

# Timeouts
REQUEST_TIMEOUT = 15000
DESTROY_TIMEOUT = 1000

DEFAULT_ANNOUNCE_PEERS = 50
MAX_ANNOUNCE_PEERS = 82


def to_uint32(n):
    """Convert an integer to a 4-byte big-endian representation."""
    return n.to_bytes(4, byteorder="big", signed=False)


def querystring_parse(q):
    """
    Parse a query string using `unescape` instead of decodeURIComponent.
    Bittorrent clients often send non-UTF8 query strings.
    """

    def unescape(s):
        return re.sub(r"%([0-9A-Fa-f]{2})", lambda m: chr(int(m.group(1), 16)), s)

    return {k: [unescape(v) for v in vs] for k, vs in parse_qs(q).items()}


def querystring_stringify(obj):
    """
    Stringify a query string using `escape` instead of encodeURIComponent.
    """

    def escape(s):
        return re.sub(r"[^A-Za-z0-9_~]", lambda m: f"%{ord(m.group(0)):02X}", s)

    encoded = urlencode(obj, doseq=True, safe="").replace("+", "%20")
    return re.sub(r"[@*/+]", lambda m: f"%{ord(m.group(0)):02X}", encoded)


def parse_url(url_str):
    """
    Parse URLs and handle non-standard URL schemes like `udp`.
    """
    parsed = urlparse(url_str.replace("udp:", "http:"))
    if url_str.startswith("udp:"):
        updated_parts = parsed._replace(
            scheme="udp",
            netloc=parsed.netloc,
            path=parsed.path,
        )
        return urlunparse(updated_parts)
    return url_str
