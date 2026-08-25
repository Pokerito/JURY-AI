import structlog
from google import genai
from google.genai import types

from app.config import get_settings
from app.core.exceptions import ExternalServiceException

logger = structlog.get_logger(__name__)

class GeminiClient:
    """Singleton client for interacting with Google GenAI API."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeminiClient, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self._client = None

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            settings = get_settings()
            if not settings.GOOGLE_API_KEY:
                raise ExternalServiceException(
                    detail="GOOGLE_API_KEY is not configured in .env. Please set a valid Gemini API key."
                )
            self._client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        return self._client

    def embed_text(self, text: str) -> list[float]:
        """Embed text using the gemini-embedding-2 model."""
        try:
            response = self.client.models.embed_content(
                model="gemini-embedding-2",
                contents=text,
            )
            # embeddings is a list of Embedding objects, each has a values attribute
            return response.embeddings[0].values
        except ExternalServiceException:
            raise
        except Exception as e:
            logger.error("gemini_embed_error", error=str(e))
            raise ExternalServiceException(detail=f"Failed to embed text: {str(e)}")

    def generate_content(self, prompt: str) -> str:
        """Generate content from a text prompt using gemini-3.6-flash with fallback to gemini-3.7-flash."""
        try:
            response = self.client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )
            return response.text
        except ExternalServiceException:
            raise
        except Exception as e:
            logger.warning("gemini_3_6_flash_error", error=str(e), fallback="gemini-3.7-flash")
            try:
                response = self.client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents=prompt,
                )
                return response.text
            except Exception as fallback_e:
                logger.error("gemini_generate_error", error=str(fallback_e))
                raise ExternalServiceException(detail=f"Failed to generate content: {str(fallback_e)}")

gemini_client = GeminiClient()
