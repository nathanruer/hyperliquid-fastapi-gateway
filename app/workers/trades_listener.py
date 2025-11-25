import time
import sys
import os
import threading
import queue
import signal
from typing import Dict, Any, Optional

from app.core.logger import setup_logger
from app.services.telegram_service import TelegramService
from app.core.config import settings

logger = setup_logger(__name__)

try:
    from hyperliquid.info import Info
    from hyperliquid.utils import constants
except ImportError as e:
    logger.critical(f"Erreur d'importation : {e}. Vérifiez votre PYTHONPATH.")
    sys.exit(1)

class TradesListener:
    def __init__(self):
        self.users_list = settings.USERS_LISTENED
        
        self.info_client: Optional[Info] = None
        self.subscriptions: Dict[str, int] = {}
        self.msg_queue = queue.Queue()
        self.running = True
        
        self.telegram_service = TelegramService()
        self.worker_thread = threading.Thread(target=self._notification_worker, daemon=True)

    def start(self):
        logger.info("-----------------------------------------------------")
        logger.info("Démarrage du Listener")
        logger.info("-----------------------------------------------------")

        if not self.users_list:
            logger.error("Aucune adresse trouvée dans USERS_LISTENED.")
            return

        try:
            self.info_client = Info(constants.MAINNET_API_URL, skip_ws=False)
        except Exception as e:
            logger.critical(f"Impossible d'initialiser le client Info : {e}")
            return

        self.worker_thread.start()

        logger.info(f"Abonnement aux trades de {len(self.users_list)} adresse(s).")
        for addr in self.users_list:
            try:
                sub_id = self.info_client.subscribe(
                    {"type": "userFills", "user": addr},
                    self._on_message_received
                )
                self.subscriptions[addr] = sub_id
                logger.info(f"-> Abonné: {addr[:10]}...")
            except Exception as e:
                logger.error(f"Erreur d'abonnement pour {addr}: {e}")

        self._wait_loop()

    def _wait_loop(self):
        def signal_handler(sig, frame):
            logger.info("Signal d'arrêt reçu...")
            self.stop()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        logger.info("Worker actif. Ctrl+C pour arrêter.")
        
        try:
            while self.running:
                time.sleep(1)
        except Exception as e:
            logger.error(f"Erreur inattendue dans la boucle principale : {e}")
            self.stop()

    def stop(self):
        self.running = False
        logger.info("Arrêt en cours...")
        
        if self.info_client:
            for addr, sub_id in self.subscriptions.items():
                try:
                    self.info_client.unsubscribe({"type": "userFills", "user": addr}, sub_id)
                except Exception:
                    pass
            
            try:
                if hasattr(self.info_client, 'ws_manager') and self.info_client.ws_manager:
                     if hasattr(self.info_client.ws_manager, 'ws'):
                        self.info_client.ws_manager.ws.close()
            except Exception as e:
                logger.warning(f"Erreur lors de la fermeture WS: {e}")

        logger.info("Worker terminé.")
        os._exit(0)

    def _on_message_received(self, message: Dict[str, Any]):
        try:
            data = message.get("data") or {}
            
            if data.get("isSnapshot"):
                return

            if message.get("channel") == "userFills":
                user = data.get("user", "Unknown")
                fills = data.get("fills", [])
                
                if fills:
                    for fill in fills:
                        coin = fill.get('coin', 'UNKNOWN')
                        side = fill.get('side', '')
                        price = fill.get('px', '?')
                        size = fill.get('sz', '?')
                        logger.info(f"[!] Trade détecté pour {user[:8]}... | {side} {coin} | Prix: {price} | Taille: {size}")
                        self.msg_queue.put({"fill": fill, "user": user})
                        
        except Exception as e:
            logger.error(f"Erreur processing message WS: {e}", exc_info=True)

    def _notification_worker(self):
        while self.running:
            try:
                item = self.msg_queue.get(timeout=1) 
                
                self.telegram_service.send_trade_alert(item['fill'], item['user'])
                
                self.msg_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Erreur dans le worker de notification: {e}")
