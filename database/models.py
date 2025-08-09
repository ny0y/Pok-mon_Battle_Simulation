from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    # email = Column(String, unique=True, index=True, nullable=True)  # Commented out temporarily
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    battles = relationship("Battle", back_populates="user")
    training_sessions = relationship("TrainingSession", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', active={self.is_active})>"
    
class Battle(Base):
    __tablename__ = "battles"

    id = Column(String, primary_key=True, index=True)  # UUID string
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    player_pokemon = Column(Text, nullable=False)  # JSON string
    ai_pokemon = Column(Text, nullable=False)  # JSON string
    battle_log = Column(Text, nullable=True)  # JSON string of battle events
    winner = Column(String, nullable=True)  # "player", "ai", "draw", or null if ongoing
    status = Column(String, default="active")  # "active", "completed", "abandoned"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="battles")

    def __repr__(self):
        return f"<Battle(id='{self.id}', user_id={self.user_id}, status='{self.status}')>"

class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    episodes = Column(Integer, nullable=False)
    win_rate = Column(Float, nullable=False)
    final_epsilon = Column(Float, nullable=False)
    training_time_seconds = Column(Float, nullable=False)
    model_version = Column(String, nullable=True)  # Track different model versions
    hyperparameters = Column(Text, nullable=True)  # JSON string of hyperparameters used
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="training_sessions")

    def __repr__(self):
        return f"<TrainingSession(id={self.id}, episodes={self.episodes}, win_rate={self.win_rate:.2f})>"

class Pokemon(Base):
    """Cache frequently accessed Pokémon data to reduce API calls."""
    __tablename__ = "pokemon_cache"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    types = Column(Text, nullable=False)  # JSON array of types
    stats = Column(Text, nullable=False)  # JSON object of stats
    abilities = Column(Text, nullable=False)  # JSON array of abilities
    moves = Column(Text, nullable=False)  # JSON array of moves
    cached_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Pokemon(id={self.id}, name='{self.name}')>"

class GameStats(Base):
    """Track overall game statistics."""
    __tablename__ = "game_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_battles = Column(Integer, default=0)
    battles_won = Column(Integer, default=0)
    battles_lost = Column(Integer, default=0)
    battles_drawn = Column(Integer, default=0)
    favorite_pokemon = Column(String, nullable=True)
    total_training_episodes = Column(Integer, default=0)
    best_win_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User")

    @property
    def win_rate(self) -> float:
        """Calculate current win rate."""
        if self.total_battles == 0:
            return 0.0
        return self.battles_won / self.total_battles

    def __repr__(self):
        return f"<GameStats(user_id={self.user_id}, total_battles={self.total_battles}, win_rate={self.win_rate:.2f})>"