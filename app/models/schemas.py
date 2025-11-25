from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class MarginSummary(BaseModel):
    accountValue: str
    totalRawUsd: str
    totalMarginUsed: Optional[str] = None
    withdrawable: Optional[str] = None

class UserStateResponse(BaseModel):
    address: str
    accountValue: str
    totalRawUsd: str
    numPositions: int
    marginSummary: Dict[str, Any]
    assetPositions: List[Dict[str, Any]]
    crossMarginSummary: Optional[Dict[str, Any]] = None
    withdrawable: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

class MarketOrderRequest(BaseModel):
    coin: str = Field(..., description="Symbole de la crypto (ex: ASTER, BTC)")
    is_buy: bool = Field(..., description="True pour acheter, False pour vendre")
    size: float = Field(..., gt=0, description="Quantité à trader")
    slippage: Optional[float] = Field(0.01, description="Slippage autorisé (défaut: 0.01 = 1%)")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "coin": "ASTER",
                "is_buy": True,
                "size": 10,
                "slippage": 0.01
            }
        }
    )

class MarketCloseRequest(BaseModel):
    coin: str = Field(..., description="Symbole de la crypto à fermer")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"coin": "ASTER"}
        }
    )

class OrderFillDetail(BaseModel):
    oid: int
    totalSz: str
    avgPx: str

class OrderResponse(BaseModel):
    status: str
    filled_orders: List[OrderFillDetail]
    errors: List[str]


# ==================== Health Check Models ====================

class ServiceStatus(BaseModel):
    """Status of an individual service."""
    status: str = Field(..., description="Service status: 'up', 'down', or 'degraded'")
    message: Optional[str] = Field(None, description="Additional status information")


class HealthResponse(BaseModel):
    """Detailed health check response."""
    status: str = Field(..., description="Overall system status: 'healthy', 'degraded', or 'unhealthy'")
    api: ServiceStatus = Field(..., description="API service status")
    exchange: ServiceStatus = Field(..., description="Hyperliquid exchange connection status")
    uptime_seconds: float = Field(..., description="Application uptime in seconds")
    version: str = Field(..., description="Application version")
    timestamp: str = Field(..., description="Current timestamp (ISO 8601)")