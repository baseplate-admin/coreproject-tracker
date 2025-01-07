from ._base import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import INTEGER
from datetime import datetime


class Torrent(Base):
    __tablename__ = "torrents"

    # Unique ID, UUID
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    info_hash = Column(String, unique=True, nullable=False)

    # Created at field
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Torrent(name={self.name}, info_hash={self.info_hash})>"


class Peer(Base):
    __tablename__ = "peers"

    # ID of Peer
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    ip = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    is_seeding = Column(Boolean, nullable=False)
    peer_id = Column(String, nullable=False)

    # Foreign Key relationship with Torrent
    torrent_id = Column(Integer, ForeignKey("torrents.id"), nullable=False)
    torrent = relationship("Torrent", backref="peers")

    # Updated at field
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint on combination of torrent, ip, port, and peer_id
    __table_args__ = (
        UniqueConstraint("torrent_id", "ip", "port", "peer_id", name="_peer_unique"),
    )

    def __repr__(self):
        return f"<Peer(ip={self.ip}, port={self.port}, peer_id={self.peer_id}, is_seeding={self.is_seeding})>"
