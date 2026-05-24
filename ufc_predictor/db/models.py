"""SQLAlchemy table definitions for the production database."""

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, MetaData, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Fighter(Base):
    __tablename__ = "fighters"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    normalized_name = Column(Text, index=True)
    nickname = Column(Text)
    wins = Column(Float)
    losses = Column(Float)
    draws = Column(Float)
    height_cm = Column(Float)
    weight_in_kg = Column(Float)
    reach_in_cm = Column(Float)
    stance = Column(Text)
    date_of_birth = Column(Text)
    significant_strikes_landed_per_minute = Column(Float)
    significant_striking_accuracy = Column(Float)
    significant_strikes_absorbed_per_minute = Column(Float)
    significant_strike_defence = Column(Float)
    average_takedowns_landed_per_15_minutes = Column(Float)
    takedown_accuracy = Column(Float)
    takedown_defense = Column(Float)
    average_submissions_attempted_per_15_minutes = Column(Float)
    elo = Column(Float, default=1000)
    peak_elo = Column(Float, default=1000)
    weight_class = Column(Text)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Fight(Base):
    __tablename__ = "fights"

    id = Column(Integer, primary_key=True)
    event = Column(Text)
    fighter_1 = Column(Text)
    fighter_2 = Column(Text)
    result = Column(Text)
    method = Column(Text)
    round = Column(Text)
    time = Column(Text)
    source_hash = Column(Text, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FighterEloHistory(Base):
    __tablename__ = "fighter_elo_history"

    id = Column(Integer, primary_key=True)
    fighter_name = Column(Text, nullable=False)
    normalized_name = Column(Text, index=True)
    elo = Column(Float, nullable=False)
    peak_elo = Column(Float)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())


class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id = Column(String, primary_key=True)
    fighter_a = Column(Text, nullable=False)
    fighter_b = Column(Text, nullable=False)
    winner = Column(Text)
    confidence = Column(Float)
    model = Column(Text)
    payload_json = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    prediction_id = Column(Text)
    fighter_a = Column(Text, nullable=False)
    fighter_b = Column(Text, nullable=False)
    predicted_winner = Column(Text, nullable=False)
    actual_winner = Column(Text)
    confidence = Column(Float)
    was_correct = Column(Boolean, nullable=False)
    user_notes = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class ScrapeCache(Base):
    __tablename__ = "scrape_cache"

    normalized_name = Column(Text, primary_key=True)
    source = Column(Text)
    url = Column(Text)
    raw_json = Column(JSONB, nullable=False)
    confidence = Column(Float, default=0)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
