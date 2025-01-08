import struct

from twisted.internet.protocol import DatagramProtocol
from twisted.logger import Logger

from coreproject_tracker.common import ACTIONS, EVENTS
from coreproject_tracker.constants.interval import ANNOUNCE_INTERVAL
from coreproject_tracker.datastructures import DataStructure
from coreproject_tracker.functions.bytes import (
    from_uint16,
    from_uint32,
    from_uint64,
    to_uint32,
)
from coreproject_tracker.functions.ip import addrs_to_compact

log = Logger(namespace="coreproject_tracker")
CONNECTION_ID = (0x417 << 32) | 0x27101980


class UDPServer(DatagramProtocol):
    def __init__(self, *args, **kwargs):
        self.data = self.datastore = DataStructure()

    def make_udp_packet(self, params: dict[str, int | bytes | dict]) -> bytes:
        """
        Create UDP packets for BitTorrent tracker protocol.

        Args:
            params: Dictionary containing packet parameters including 'action' and other
                action-specific parameters.

        Returns:
            bytes: The constructed UDP packet

        Raises:
            ValueError: If the action is not implemented
        """
        action = params["action"]

        if action == ACTIONS.CONNECT:
            packet = b"".join(
                [
                    to_uint32(ACTIONS.CONNECT),
                    to_uint32(params["transaction_id"]),
                    params["connection_id"],
                ]
            )

        elif action == ACTIONS.ANNOUNCE:
            packet = b"".join(
                [
                    to_uint32(ACTIONS.ANNOUNCE),
                    to_uint32(params["transaction_id"]),
                    to_uint32(params["interval"]),
                    to_uint32(params["incomplete"]),
                    to_uint32(params["complete"]),
                    params["peers"],
                ]
            )

        elif action == ACTIONS.SCRAPE:
            scrape_response = [
                to_uint32(ACTIONS.SCRAPE),
                to_uint32(params["transaction_id"]),
            ]

            for info_hash, file in params["files"].items():
                scrape_response.extend(
                    [
                        to_uint32(file["complete"]),
                        to_uint32(
                            file["downloaded"]
                        ),  # Note: this only provides a lower-bound
                        to_uint32(file["incomplete"]),
                    ]
                )

            packet = b"".join(scrape_response)

        elif action == ACTIONS.ERROR:
            packet = b"".join(
                [
                    to_uint32(ACTIONS.ERROR),
                    to_uint32(params.get("transaction_id", 0)),
                    str(params.get("failure_reason", "")).encode(),
                ]
            )

        else:
            raise ValueError(f"Action not implemented: {action}")

        return packet

    def parse_udp_packet(self, msg, addr):
        connection_id = msg[:8]
        connection_id_unpacked = struct.unpack(">Q", msg[:8])[0]
        if connection_id_unpacked != CONNECTION_ID:
            raise ValueError("Error")

        action = from_uint32(msg[8:12])
        transaction_id = from_uint32(msg[12:16])

        # Construct the result (similar to the JavaScript object)
        params = {
            "connection_id": connection_id,
            "action": action,
            "transaction_id": transaction_id,
            "type": "udp",
        }

        if params["action"] == ACTIONS.ANNOUNCE:
            params["info_hash"] = msg[16:36].hex()  # 20 bytes
            params["peer_id"] = msg[36:56].hex()  # 20 bytes
            params["downloaded"] = from_uint64(
                msg[56:64]
            )  # Convert 64-bit unsigned integer
            params["left"] = from_uint64(msg[64:72])  # Convert 64-bit unsigned integer
            params["uploaded"] = from_uint64(
                msg[72:80]
            )  # Convert 64-bit unsigned integer

            # Read 4-byte unsigned int (big-endian)
            event_id = struct.unpack(">I", msg[80:84])[0]
            params["event"] = EVENTS.get(event_id)
            if not params["event"]:
                raise ValueError("Invalid event")

            params["ip"] = from_uint32(msg[84:88]) or addr[0]
            params["key"] = from_uint32(msg[88:92])

            params["numwant"] = from_uint32(msg[92:96]) or 50  # Default announce peer
            params["port"] = from_uint16(msg[96:98]) or addr[1]
            params["addr"] = f"{params['ip']}:{params['port']}"
            params["compact"] = 1
        return params

    def datagramReceived(self, data, addr):
        """
        Called when a datagram (UDP packet) is received.

        - `data`: The received message.
        - `addr`: The address of the sender (tuple of IP and port).
        """
        if (packet_length := len(data)) < 16:
            log.error(
                f"received packet length is {packet_length} is shorter than 16 bytes"
            )

        param = self.parse_udp_packet(data, addr)

        if param["action"] == ACTIONS.ANNOUNCE:
            self.datastore.add_peer(
                param["info_hash"], param["ip"], param["port"], param["left"], 3600
            )

            peer_count = 0
            peers = []
            seeders = 0
            leechers = 0
            for peer in self.datastore.get_peers(param["info_hash"]):
                if peer_count > param["numwant"]:
                    break

                if peer.left == 0:
                    seeders += 1
                else:
                    leechers += 1

                peers.append(f"{peer.peer_ip}:{peer.port}")
                peer_count += 1

            param["peers"] = addrs_to_compact(peers)
            param["complete"] = seeders
            param["incomplete"] = leechers
            param["interval"] = ANNOUNCE_INTERVAL

        res = self.make_udp_packet(param)
        self.transport.write(res, addr)
