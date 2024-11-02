from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from .models import RequestSchema
from .utils.openai import openai_request
from .utils.db import get_db
from .config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/requests",
    tags=["Requests"]
)

@router.post("/create")
async def create_request(request: RequestSchema, db: Session = Depends(get_db)):
    """
    Handles POST requests to create new OpenAI requests.

    Args:
        request (RequestSchema): The validated request data from the client.
        db (Session): The database session object.

    Returns:
        JSONResponse: A JSON response containing the formatted OpenAI API response.
    """
    try:
        # Make OpenAI API call
        response = await openai_request(request.model, request.prompt, request.parameters)

        # Store request and response in the database
        new_request = OpenAIRequest(
            model=request.model,
            prompt=request.prompt,
            parameters=request.parameters,
            response=response,
            user_id=current_user.id  # Assuming you have user authentication in place
        )
        db.add(new_request)
        db.commit()
        db.refresh(new_request)

        return JSONResponse({"message": "Request created successfully!", "request_id": new_request.id})
    except Exception as e:
        logger.error(f"Error creating OpenAI request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")