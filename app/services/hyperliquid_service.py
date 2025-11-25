from typing import Optional, Dict, Any
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants
from eth_account.signers.local import LocalAccount
import eth_account
from app.core.config import settings 
from app.core.logger import setup_logger
from app.core.exceptions import ExchangeNotConfiguredError, TradingError
from app.models.schemas import MarketOrderRequest, MarketCloseRequest

logger = setup_logger(__name__)

class HyperliquidService:
    def __init__(self):
        self.exchange_instance: Optional[Exchange] = None
        self.account_address: Optional[str] = None
        self.info_client = Info(constants.MAINNET_API_URL, skip_ws=True)
        self._setup_exchange()

    def _setup_exchange(self):
        if not settings.ACCOUNT_ADDRESS or not settings.SECRET_KEY:
            logger.warning("Variables d'environnement Hyperliquid manquantes (ACCOUNT_ADDRESS ou SECRET_KEY). Trading désactivé - mode read-only.")
            return

        account: LocalAccount = eth_account.Account.from_key(settings.SECRET_KEY)
        address = settings.ACCOUNT_ADDRESS
        if account.address.lower() != address.lower():
            address = account.address
            
        self.account_address = address
        self.exchange_instance = Exchange(
            account,
            constants.MAINNET_API_URL,
            account_address=address
        )
        logger.info(f"Exchange initialisé pour l'adresse: {self.account_address}")

    def get_user_state(self, address: str) -> Optional[Dict[str, Any]]:
        return self.info_client.user_state(address)

    def create_market_order(self, order: MarketOrderRequest) -> Dict[str, Any]:
        if not self.exchange_instance:
            raise ExchangeNotConfiguredError()
        
        try:
            return self.exchange_instance.market_open(
                order.coin,
                order.is_buy,
                order.size,
                None,
                order.slippage
            )
        except Exception as e:
            raise TradingError("ouverture de position", str(e))

    def close_market_position(self, close_request: MarketCloseRequest) -> Dict[str, Any]:
        if not self.exchange_instance:
            raise ExchangeNotConfiguredError()
        
        try:
            return self.exchange_instance.market_close(close_request.coin)
        except Exception as e:
            raise TradingError("fermeture de position", str(e))

hyperliquid_service = HyperliquidService()