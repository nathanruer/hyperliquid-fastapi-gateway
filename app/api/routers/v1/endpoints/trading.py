from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.exceptions import ExchangeNotConfiguredError, TradingError
from app.models.schemas import MarketOrderRequest, MarketCloseRequest, OrderResponse, OrderFillDetail
from app.services.hyperliquid_service import hyperliquid_service as hs
from app.api.dependencies import APIKeyDep
from typing import Dict, Any

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

def process_order_result(order_result: Dict[str, Any]) -> OrderResponse:
    filled_orders = []
    errors = []
    if order_result["status"] == "ok":
        for status in order_result.get("response", {}).get("data", {}).get("statuses", []):
            if "filled" in status:
                filled = status["filled"]
                filled_orders.append(OrderFillDetail(
                    oid=filled["oid"],
                    totalSz=filled["totalSz"],
                    avgPx=filled["avgPx"]
                ))
            elif "error" in status:
                errors.append(status["error"])
    else:
        errors.append(f"Order failed: {order_result['status']}")
    
    return OrderResponse(
        status=order_result["status"],
        filled_orders=filled_orders,
        errors=errors
    )

@router.post(
    "/order/market",
    response_model=OrderResponse,
    summary="Ouvrir une position market",
    description="Place un ordre market avec slippage configurable. **Authentification requise via header X-API-Key.**"
)
@limiter.limit("30/minute")
async def create_market_order(request: Request, order: MarketOrderRequest, api_key: APIKeyDep):
    try:
        order_result = hs.create_market_order(order)
        return process_order_result(order_result)
    except ExchangeNotConfiguredError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except TradingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur inattendue : {str(e)}")

@router.post(
    "/order/market/close",
    response_model=OrderResponse,
    summary="Fermer une position market",
    description="Ferme une position existante. **Authentification requise via header X-API-Key.**"
)
@limiter.limit("30/minute")
async def close_market_position(request: Request, close_request: MarketCloseRequest, api_key: APIKeyDep):
    try:
        order_result = hs.close_market_position(close_request)
        return process_order_result(order_result)
    except ExchangeNotConfiguredError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except TradingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur inattendue : {str(e)}")
