from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any

class RequestSchema(BaseModel):
    model: str = Field(..., description="The OpenAI model to use (e.g., gpt-3.5-turbo, text-davinci-003)")
    prompt: str = Field(..., description="The input prompt for the OpenAI model")
    parameters: Dict[str, Any] = Field(default={}, description="Optional parameters for the OpenAI API call")

    @validator("model", pre=True)
    def validate_model(cls, value):
        allowed_models = ["gpt-3.5-turbo", "text-davinci-003", "text-curie-001", "text-babbage-001", "text-ada-001"]
        if value.lower() not in allowed_models:
            raise ValueError(f"Invalid OpenAI model. Allowed models are: {', '.join(allowed_models)}")
        return value.lower()

    @validator("prompt", pre=True)
    def validate_prompt(cls, value):
        if not isinstance(value, str) or len(value) > 1000:
            raise ValueError("Prompt must be a string and not exceed 1000 characters.")
        return value

    @validator("parameters", pre=True)
    def validate_parameters(cls, value):
        if not isinstance(value, dict):
            raise ValueError("Parameters must be a dictionary.")
        return value