"""Database connection and models using SQLAlchemy."""
import datetime
from typing import Generator
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import sessionmaker, declarative_base, Session

import config

# Define Base
Base = declarative_base()

# Define Models
class ChatLog(Base):
    """Log of all chat interactions."""
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Interaction
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    
    # Metadata
    model = Column(String)
    processing_time = Column(Float) # in seconds
    sources_count = Column(Integer)
    
    def __repr__(self):
        return f"<ChatLog(id={self.id}, date={self.timestamp})>"


# Create global engine and SessionLocal
_engine = None
SessionLocal = None

def init_db():
    """Initialize database connection."""
    global _engine, SessionLocal
    
    if not config.DATABASE_URL:
        print("Warning: DATABASE_URL not set. Database features disabled.")
        return

    try:
        # Create engine
        _engine = create_engine(config.DATABASE_URL, pool_pre_ping=True)
        
        # Create tables
        Base.metadata.create_all(bind=_engine)
        
        # Create Session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        print("Database initialized successfully.")
        
    except Exception as e:
        print(f"Error initializing database: {e}")

def get_db() -> Generator[Session, None, None]:
    """Dependency to get DB session."""
    if SessionLocal is None:
        yield None
        return
        
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_chat_log(db: Session, query: str, answer: str, model: str, time_taken: float, sources_count: int):
    """Save a chat interaction to the database."""
    if db is None:
        return
        
    try:
        log = ChatLog(
            query=query,
            answer=answer,
            model=model,
            processing_time=time_taken,
            sources_count=sources_count
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    except Exception as e:
        print(f"Error saving chat log: {e}")
        db.rollback()
