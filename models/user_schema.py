from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any

class UserSchema(BaseModel):
    username: str = Field(..., description="The username of the user")
    email: str = Field(..., description="The email address of the user")
    password: str = Field(..., description="The password of the user")

    @validator("username")
    def validate_username(cls, value):
        if not value:
            raise ValueError("Username cannot be empty.")
        if len(value) < 3 or len(value) > 20:
            raise ValueError("Username must be between 3 and 20 characters long.")
        # Additional validation logic if required 
        return value

    @validator("email")
    def validate_email(cls, value):
        if not value:
            raise ValueError("Email address cannot be empty.")
        # Use a more robust email validation library like 'email_validator' for a more comprehensive check
        if "@" not in value or "." not in value:
            raise ValueError("Invalid email address format.")
        # Additional validation logic if required 
        return value

    @validator("password")
    def validate_password(cls, value):
        if not value:
            raise ValueError("Password cannot be empty.")
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        # Implement more complex password strength validation if required 
        # Use a library like 'password_strength' for comprehensive password validation
        return value