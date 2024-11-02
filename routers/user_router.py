from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Optional
from .models import UserSchema
from .utils.auth import create_access_token, get_current_user, oauth2_scheme
from .utils.db import get_db, User  # Assuming you have a User model in utils/db

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserSchema, db: Session = Depends(get_db)):
    """Registers a new user."""
    try:
        existing_user = db.query(User).filter(
            (User.username == user.username) | (User.email == user.email)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists."
            )
        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=user.password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return JSONResponse(
            {"message": "User registered successfully!"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {e}"
        )

@router.post("/login")
async def login(user: UserSchema, db: Session = Depends(get_db)):
    """Logs in an existing user."""
    try:
        db_user = db.query(User).filter(User.username == user.username).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password."
            )
        if not db_user.verify_password(user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password."
            )
        access_token = create_access_token(data={"sub": db_user.id})
        return JSONResponse(
            {"access_token": access_token, "token_type": "bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging in: {e}"
        )

@router.get("/me", dependencies=[Depends(oauth2_scheme)])
async def get_current_user(current_user: User = Depends(get_current_user)):
    """Returns information for the currently logged-in user."""
    return {"username": current_user.username, "email": current_user.email}