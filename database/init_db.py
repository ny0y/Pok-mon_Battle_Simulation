from . import models
from .database import SessionLocal, engine, Base
from .auth import get_password_hash

def init():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    
    db = SessionLocal()
    print("Checking for existing test user...")
    user = db.query(models.User).filter(models.User.username == "test").first()
    if not user:
        print("Creating test user...")
        test_user = models.User(username="test", hashed_password=get_password_hash("test123"))
        db.add(test_user)
        db.commit()
        print("Test user created.")
    else:
        print("Test user already exists.")
    db.close()


if __name__ == "__main__":
    print("Starting database initialization...")
    init()
    print("Database initialization complete.")
