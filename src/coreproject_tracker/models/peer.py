from coreproject_tracker.models._base import Base
from sqlalchemy import Column, Integer, String, Sequence


class Peer(Base):
    __tablename__ = "peers"
    id = Column(Integer, Sequence("peer_id_seq"), primary_key=True)
    info_hash = Column(String(64), nullable=False)
    peer_ip = Column(String(50), nullable=False)
    port = Column(Integer, nullable=False)
    left = Column(Integer, nullable=False)
    last_seen = Column(Integer, nullable=False)
