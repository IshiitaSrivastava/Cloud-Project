# backend/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import hashlib

Base = declarative_base()

class Voter(Base):
    __tablename__ = 'voters'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

class Election(Base):
    __tablename__ = 'elections'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    options = relationship('Option', back_populates='election')

class Option(Base):
    __tablename__ = 'options'
    id = Column(Integer, primary_key=True)
    election_id = Column(Integer, ForeignKey('elections.id'))
    text = Column(String, nullable=False)
    votes = Column(Integer, default=0)
    election = relationship('Election', back_populates='options')

class VoteRecord(Base):
    __tablename__ = 'vote_records'
    id = Column(Integer, primary_key=True)
    voter_id = Column(Integer, ForeignKey('voters.id'))
    election_id = Column(Integer, ForeignKey('elections.id'))
    option_id = Column(Integer, ForeignKey('options.id'))
    timestamp = Column(DateTime, server_default=func.now())

class AuditBlock(Base):
    __tablename__ = 'audit_blocks'
    id = Column(Integer, primary_key=True)
    prev_hash = Column(String)
    data = Column(Text)
    block_hash = Column(String)
    timestamp = Column(DateTime, server_default=func.now())

    @staticmethod
    def compute_hash(prev_hash, data):
        payload = f"{prev_hash}|{data}".encode('utf-8')
        return hashlib.sha256(payload).hexdigest()
