import openai
from .config import settings
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class OpenAIUtils:
    __instance = None

    def __init__(self):
        if OpenAIUtils.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            openai.api_key = settings.OPENAI_API_KEY
            OpenAIUtils.__instance = self

    @staticmethod
    def get_instance():
        if OpenAIUtils.__instance is None:
            OpenAIUtils()
        return OpenAIUtils.__instance

    async def make_request(self, model: str, prompt: str, parameters: dict = {}):
        """
        Makes a request to the OpenAI API.

        Args:
            model (str): The OpenAI model to use.
            prompt (str): The input prompt for the model.
            parameters (dict, optional): Optional parameters for the API call. Defaults to {}.

        Returns:
            dict: The response from the OpenAI API.
        """
        try:
            response = await openai.Completion.create(
                model=model,
                prompt=prompt,
                **parameters
            )
            return response.choices[0].text
        except openai.error.APIError as e:
            logger.error(f"Error while making OpenAI request: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"OpenAI API Error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during OpenAI request: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    async def get_response(self, model: str, prompt: str, parameters: dict = {}):
        """
        Retrieves a response from the OpenAI API, handling caching if configured.

        Args:
            model (str): The OpenAI model to use.
            prompt (str): The input prompt for the model.
            parameters (dict, optional): Optional parameters for the API call. Defaults to {}.

        Returns:
            str: The response from the OpenAI API.
        """
        # Implement caching logic if needed (see section 7 for caching strategies)
        return await self.make_request(model, prompt, parameters)

async def openai_request(model: str, prompt: str, parameters: dict = {}):
    """
    A wrapper function for making OpenAI requests using the OpenAIUtils class.

    Args:
        model (str): The OpenAI model to use.
        prompt (str): The input prompt for the model.
        parameters (dict, optional): Optional parameters for the API call. Defaults to {}.

    Returns:
        str: The response from the OpenAI API.
    """
    openai_utils = OpenAIUtils.get_instance()
    return await openai_utils.get_response(model, prompt, parameters)