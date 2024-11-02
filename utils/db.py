from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.sql import func
from fastapi import Depends
from .config import settings
import bcrypt

# Configure SQLAlchemy engine and session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define base model
Base = declarative_base()

# Create a scoped session factory
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    requests = relationship("Request", backref="user", cascade="all, delete-orphan")

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode(), self.hashed_password.encode())

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    model = Column(String(50), nullable=False)
    prompt = Column(String, nullable=False)
    parameters = Column(JSON, nullable=False)
    response = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

def create_user(db: Session, user: UserSchema):
    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_request(db: Session, request: RequestSchema, user_id: int):
    db_request = Request(
        model=request.model,
        prompt=request.prompt,
        parameters=request.parameters,
        response=request.response,
        user_id=user_id
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

def get_requests_by_user(db: Session, user_id: int):
    return db.query(Request).filter(Request.user_id == user_id).all()

def get_request_by_id(db: Session, request_id: int):
    return db.query(Request).filter(Request.id == request_id).first()

def initialize_db():
    Base.metadata.create_all(bind=engine)