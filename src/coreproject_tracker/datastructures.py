import time


class Peer:
    def __init__(self, peer_id, peer_ip, port, left, ttl_seconds):
        self.peer_id = peer_id
        self.peer_ip = peer_ip
        self.port = port
        self.left = left
        self.expiry_time = time.time() + ttl_seconds  # Expiry time based on TTL

    def is_expired(self):
        """Check if the peer's TTL has expired."""
        return time.time() > self.expiry_time

    def __eq__(self, other):
        """Check if two peers are the same based on peer_ip and port."""
        return self.peer_ip == other.peer_ip and self.port == other.port

    def __hash__(self):
        """Ensure peers are unique by peer_ip and port."""
        return hash((self.peer_ip, self.port))


class Entity:
    def __init__(self):
        self.peers = set()  # Use a set to ensure uniqueness by peer_ip and port

    def add_peer(self, peer_id, peer_ip, port, left, ttl_seconds):
        """Add a new peer with a TTL to the entity (only if it's unique)."""
        # Create a new peer
        peer = Peer(peer_id, peer_ip, port, left, ttl_seconds)
        # Add the peer to the set (set ensures uniqueness)
        if peer not in self.peers:
            self.peers.add(peer)
        else:
            print(
                f"Peer ({peer_ip}, {port}) already exists in the entity and won't be added."
            )

    def remove_expired_peers(self):
        """Remove expired peers from the set."""
        self.peers = {peer for peer in self.peers if not peer.is_expired()}

    def get_peers(self):
        """Return a list of active peers as tuples (peer_ip, port)."""
        self.remove_expired_peers()
        return self.peers


class DataStructure:
    _instance = None  # Class variable to store the single instance

    def __new__(cls):
        """Ensure that only one instance of DataStructure is created."""
        if cls._instance is None:
            cls._instance = super().__new__(
                cls
            )  # Create a new instance if it doesn't exist
        return cls._instance

    def __init__(self):
        """Initialize the data structure."""
        if not hasattr(self, "initialized"):  # Avoid re-initializing the instance
            self.data = {}
            self.initialized = True

    def add_peer(self, peer_id, entity_id, peer_ip, port, left, ttl_seconds):
        """Add a peer to an entity (ensure uniqueness, and create entity if needed)."""
        # Create an entity if it doesn't exist
        entity = self.data.setdefault(entity_id, Entity())
        entity.add_peer(peer_id, peer_ip, port, left, ttl_seconds)

    def get_peers(self, entity_id):
        """Get the active peers of an entity."""
        if entity_id in self.data:
            return self.data[entity_id].get_peers()
        return []
