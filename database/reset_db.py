import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.database import engine, Base
from database import models
from database.auth import get_password_hash

def reset_database():
    """
    Reset the database by deleting the existing database file
    and recreating all tables with the current schema.
    """
    db_file = "test.db"
    
    # Remove existing database file
    if os.path.exists(db_file):
        print(f"Removing existing database file: {db_file}")
        os.remove(db_file)
    
    # Recreate all tables
    print("Creating all tables with current schema...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    
    # Initialize with test user (inline implementation to avoid import issues)
    from database.database import SessionLocal
    
    print("Creating test user...")
    db = SessionLocal()
    try:
        # Check if test user already exists
        user = db.query(models.User).filter(models.User.username == "test").first()
        if not user:
            test_user = models.User(
                username="test", 
                hashed_password=get_password_hash("test123")
            )
            db.add(test_user)
            db.commit()
            print("Test user created (username: test, password: test123)")
        else:
            print("Test user already exists")
    finally:
        db.close()
    
    print("Database reset complete!")

if __name__ == "__main__":
    reset_database()