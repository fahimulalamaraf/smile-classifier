import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.sql import text

# Database connection URL
DATABASE_URL = "mysql+pymysql://fahimul_alam:12345678Araf#@mysql_container/image_holding_db"

# Create the database engine
engine = create_engine(DATABASE_URL)

# Create a session factory
Session = sessionmaker(bind=engine)

# Test database connection on initialization
with Session() as session:
    result = session.execute(text("SELECT 1"))
    print("Database connection successful:", result.scalar())

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass

class ClassificationHistory(Base):
    """
    Represents the classification history table in the database.

    Attributes:
        id (int): Primary key.
        image_path (str): Path to the classified image.
        predicted_class (str): Predicted class (e.g., 'Smiling', 'Not Smiling').
        created_at (datetime): Timestamp of the classification.
    """
    __tablename__ = "classification_history"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String(255), index=True)  # Set a maximum length for the image path
    predicted_class = Column(String(50))  # Set a maximum length for the predicted class
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def create_tables():
    """
    Creates all tables defined in the Base metadata.
    """
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")

def get_db():
    """
    Provides a database session for FastAPI routes.

    Yields:
        Session: A database session instance.
    """
    db = Session()
    try:
        yield db
    finally:
        db.close()
