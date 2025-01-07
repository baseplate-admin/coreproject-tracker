import urllib.parse
from twisted.internet.protocol import DatagramProtocol
from twisted.logger import Logger
from coreproject_tracker.functions.ip import is_valid_ip
from coreproject_tracker.datastructures import DataStructure
import bencodepy

log = Logger(namespace="coreproject_tracker")


class AnnounceUDPProtocol(DatagramProtocol):
    def __init__(self):
        self.datastore = DataStructure()

    def validate_data(self, data: bytes, addr) -> dict[str, str | int] | bytes:
        try:
            # Parse the UDP request in a way that is similar to HTTP
            params = urllib.parse.parse_qs(data.decode())
            info_hash_raw = params.get("info_hash", [b""])[0]
            info_hash = urllib.parse.unquote_to_bytes(info_hash_raw).hex()

            if (info_hash_length := len(info_hash_raw)) > 20:
                return f"`info_hash` length is {info_hash_length} which is greater than 20".encode()

            port = params.get("port", [""])[0]
            if not port.isdigit():
                return "`port` is not an integer".encode()

            port = int(port)
            if port <= 0 or port >= 65535:
                return f"`port` is {port} which is not in range(0, 65535)".encode()

            left = params.get("left", [""])[0]
            if not left.isdigit():
                return "`left` is not an integer".encode()
            left = int(left)

            numwant = params.get("numwant", [""])[0]
            if not numwant.isdigit():
                return b"`numwant` is not an integer"
            numwant = int(numwant)

            peer_ip = addr.host
            if not is_valid_ip(peer_ip):
                return "`peer_ip` is not a valid ip".encode()

            return {
                "info_hash": info_hash,
                "port": port,
                "left": left,
                "numwant": numwant,
                "peer_ip": peer_ip,
            }

        except Exception as e:
            return f"Error processing request: {str(e)}".encode()

    def datagramReceived(self, data: bytes, addr):
        # Validate and process the UDP request
        data = self.validate_data(data, addr)
        if isinstance(data, bytes):
            # If there is an error, send back the error message
            self.transport.write(data, addr)
            return

        # Add the peer to the datastore
        self.datastore.add_peer(
            data["info_hash"], data["peer_ip"], data["port"], data["left"], 3600
        )

        # Prepare the peers response
        peer_count = 0
        peers = []
        seeders = 0
        leechers = 0

        for peer in self.datastore.get_peers(data["info_hash"]):
            if peer_count > data["numwant"]:
                break

            if peer.left == 0:
                seeders += 1
            else:
                leechers += 1

            peers.append({"ip": peer.peer_ip, "port": peer.port})
            peer_count += 1

        # Prepare the bencoded response
        output = {
            "peers": peers,
            "min interval": 60,
            "complete": seeders,
            "incomplete": leechers,
        }
        response = bencodepy.bencode(output)

        # Send the response back to the client
        self.transport.write(response, addr)
