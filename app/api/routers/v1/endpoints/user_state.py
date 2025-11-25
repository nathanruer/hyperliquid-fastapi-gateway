from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.schemas import UserStateResponse
from app.services.hyperliquid_service import hyperliquid_service as hs

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.get(
    "/user/{address}",
    response_model=UserStateResponse,
    summary="Récupérer l'état d'un utilisateur",
    description="Consulte l'état d'un compte (positions, margin, valeur du portefeuille). Endpoint public avec rate limiting."
)
@limiter.limit("60/minute")
async def get_user_state_by_address(request: Request, address: str):
    try:
        user_state = hs.get_user_state(address)
        if not user_state:
            raise HTTPException(status_code=404, detail=f"Impossible de récupérer l'état pour {address}")
            
        margin_summary = user_state.get('marginSummary', {})
        account_value = margin_summary.get('accountValue', '0.0')
        total_raw_usd = margin_summary.get('totalRawUsd', '0.0')
        asset_positions = user_state.get('assetPositions', [])

        return UserStateResponse(
            address=address,
            accountValue=account_value,
            totalRawUsd=total_raw_usd,
            numPositions=len(asset_positions),
            marginSummary=margin_summary,
            assetPositions=asset_positions,
            crossMarginSummary=user_state.get('crossMarginSummary'),
            withdrawable=user_state.get('withdrawable')
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur : {str(e)}")
