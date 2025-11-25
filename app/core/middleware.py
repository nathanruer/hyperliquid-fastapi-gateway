from fastapi import HTTPException, status, Request
from fastapi.security import APIKeyHeader
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(request: Request, api_key: str = None) -> str:
    if not settings.API_KEY:
        logger.warning("API key authentication skipped - API_KEY not configured")
        return ""

    if api_key is None:
        api_key = request.headers.get("X-API-Key")

    if not api_key:
        logger.warning(f"Unauthorized access attempt from {request.client.host} - missing API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key manquante. Incluez le header 'X-API-Key' dans votre requête.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key != settings.API_KEY:
        logger.warning(f"Unauthorized access attempt from {request.client.host} - invalid API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key invalide.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return api_key
