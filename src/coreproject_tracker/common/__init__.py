import enum
import re

# Regular expressions
IPV4_RE = re.compile(r"^[\d.]+$")
IPV6_RE = re.compile(r"^[\da-fA-F:]+$")
REMOVE_IPV4_MAPPED_IPV6_RE = re.compile(r"^::ffff:")

# Constants


class ACTIONS(enum.IntEnum):
    CONNECT = 0
    ANNOUNCE = 1
    SCRAPE = 2
    ERROR = 3


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
