from fastapi import APIRouter
from app.services.hyperliquid_service import hyperliquid_service as hs

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Hyperliquid API running"}

@router.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": "hyperliquid-api",
        "exchange_configured": hs.exchange_instance is not None,
        "account_address": hs.account_address
    }