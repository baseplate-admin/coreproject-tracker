class TorrentStore:
    _instance = None

    def __init__(self):
        self.data = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.data = {}
        return cls._instance

    def add(self, key, value):
        """Add a key-value pair."""
        self.data[key] = value

    def get(self, key):
        """Get a value by key."""
        return self.data.get(key, None)

    def remove(self, key):
        """Remove a key-value pair."""
        if key in self.data:
            del self.data[key]

    def __repr__(self):
        return f"<PeerStore({self.data})>"
