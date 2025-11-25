from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.routers.v1.endpoints import trading, user_state
from app.api.routers import root
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)

limiter = Limiter(key_func=get_remote_address)

def create_app() -> FastAPI:
    app = FastAPI(
        title="Hyperliquid Trading & State API",
        description="API pour récupérer l'état et interagir avec Hyperliquid",
        version="1.0.0"
    )

    app.state.limiter = limiter
    
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-API-Key"],
    )
    
    app.include_router(root.router)
    app.include_router(trading.router, prefix="/v1", tags=["Trading"])
    app.include_router(user_state.router, prefix="/v1", tags=["User State"])

    return app
