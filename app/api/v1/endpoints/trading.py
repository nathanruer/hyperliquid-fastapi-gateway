from fastapi import APIRouter, HTTPException
from app.models.schemas import MarketOrderRequest, MarketCloseRequest, OrderResponse, OrderFillDetail
from app.services.hyperliquid_service import hyperliquid_service as hs
from typing import Dict, Any

router = APIRouter()

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

@router.post("/order/market", response_model=OrderResponse)
async def create_market_order(order: MarketOrderRequest):
    try:
        order_result = hs.create_market_order(order)
        return process_order_result(order_result)
    except Exception as e:
        if "Exchange non configuré" in str(e):
            raise HTTPException(status_code=503, detail=str(e))
        raise HTTPException(status_code=500, detail=f"Erreur : {str(e)}")

@router.post("/order/market/close", response_model=OrderResponse)
async def close_market_position(close_request: MarketCloseRequest):
    try:
        order_result = hs.close_market_position(close_request)
        return process_order_result(order_result)
    except Exception as e:
        if "Exchange non configuré" in str(e):
            raise HTTPException(status_code=503, detail=str(e))
        raise HTTPException(status_code=500, detail=f"Erreur : {str(e)}")