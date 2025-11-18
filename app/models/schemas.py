from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any

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