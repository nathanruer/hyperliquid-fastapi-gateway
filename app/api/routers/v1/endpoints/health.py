from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import time

from app.models.schemas import HealthResponse, ServiceStatus
from app.core.config import settings
from app.core.logger import setup_logger
from app.services.hyperliquid_service import HyperliquidService

logger = setup_logger(__name__)

router = APIRouter()

START_TIME = time.time()


def _check_exchange_status() -> ServiceStatus:
    try:
        service = HyperliquidService()
        if service.exchange_instance is None:
            return ServiceStatus(
                status="down",
                message="Exchange not configured (SECRET_KEY missing or TRADING_ENABLED=false)"
            )
        return ServiceStatus(status="up", message="Connected to Hyperliquid")
    except Exception as e:
        logger.error(f"Error checking exchange status: {e}")
        return ServiceStatus(status="down", message=f"Error: {str(e)}")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check Détaillé",
    description="Retourne le statut détaillé de tous les services et composants de l'API"
)
async def health_check(request: Request) -> HealthResponse:
    api_status = ServiceStatus(status="up", message="API operational")
    exchange_status = _check_exchange_status()
    
    if exchange_status.status == "down":
        overall_status = "degraded"
    else:
        overall_status = "healthy"
    
    uptime = time.time() - START_TIME
    
    return HealthResponse(
        status=overall_status,
        api=api_status,
        exchange=exchange_status,
        uptime_seconds=uptime,
        version="1.1.0",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
