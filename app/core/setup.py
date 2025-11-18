from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import trading, user_state
from app.api import root

def create_app() -> FastAPI:
    app = FastAPI(
        title="Hyperliquid Trading & State API",
        description="API pour récupérer l'état et interagir avec Hyperliquid",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(root.router)
    app.include_router(trading.router, prefix="/v1", tags=["Trading"])
    app.include_router(user_state.router, prefix="/v1", tags=["User State"])

    return app