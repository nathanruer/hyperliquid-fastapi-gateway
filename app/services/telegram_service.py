import requests
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class TelegramService:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID

        if not self.token or not self.chat_id:
            logger.warning("Configuration Telegram manquante. Les alertes ne seront pas envoyées.")

    def send_trade_alert(self, fill: Dict[str, Any], user_addr: str):
        if not self.token or not self.chat_id:
            return

        message = self._format_fill_message(fill, user_addr)
        self._send_message(message)

    def _format_fill_message(self, fill: Dict[str, Any], user_addr: str) -> str:
        coin = fill.get('coin', 'UNKNOWN')
        price = fill.get('px', '?')
        size = fill.get('sz', '?')
        side = fill.get('side', '') # 'B' = Buy, 'A' = Ask
        closed_pnl = fill.get('closedPnl', '0.0')

        if side == 'B':
            header = "🟢 <b>ACHAT (Long/Buy)</b>"
        elif side == 'A':
            header = "🔴 <b>VENTE (Short/Sell)</b>"
        else:
            header = f"⚪ <b>{side}</b>"

        short_addr = f"{user_addr[:6]}...{user_addr[-4:]}" if user_addr else "N/A"
    

        return (
            f"{header} | {coin}\n"
            f"👤 <code>{short_addr}</code>\n"
            f"💰 Prix : <b>{price} $</b>\n"
            f"📊 Taille : {size}\n"
            f"💵 PnL réalisé : {closed_pnl} $"
        )

    def _send_message(self, message_text: str):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message_text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code != 200:
                logger.error(f"Erreur API Telegram ({response.status_code}): {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Exception réseau Telegram : {e}")
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'envoi Telegram : {e}")
