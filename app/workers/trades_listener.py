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

MAX_RECONNECT_ATTEMPTS = 10
INITIAL_RECONNECT_DELAY = 1 
MAX_RECONNECT_DELAY = 60
HEARTBEAT_INTERVAL = 30
HEARTBEAT_TIMEOUT = 90

class TradesListener:
    def __init__(self):
        self.users_list = settings.USERS_LISTENED
        
        self.info_client: Optional[Info] = None
        self.subscriptions: Dict[str, int] = {}
        self.msg_queue = queue.Queue()
        self.running = True
        self.connected = False
        
        self.reconnect_count = 0
        self.last_message_time = time.time()
        
        self.telegram_service = TelegramService()
        self.notification_thread = threading.Thread(target=self._notification_worker, daemon=True)
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_monitor, daemon=True)

    def start(self):
        logger.info("-----------------------------------------------------")
        logger.info("Démarrage du Listener")
        logger.info("-----------------------------------------------------")

        if not self.users_list:
            logger.error("Aucune adresse trouvée dans USERS_LISTENED.")
            return

        self.notification_thread.start()
        self.heartbeat_thread.start()

        if not self._connect():
            logger.error("Impossible de se connecter initialement. Abandon.")
            return

        self._wait_loop()

    def _connect(self) -> bool:
        try:
            logger.info("Connexion au WebSocket Hyperliquid...")
            self.info_client = Info(constants.MAINNET_API_URL, skip_ws=False)
            
            logger.info(f"Abonnement aux trades de {len(self.users_list)} adresse(s)...")
            self.subscriptions.clear()
            
            for addr in self.users_list:
                try:
                    sub_id = self.info_client.subscribe(
                        {"type": "userFills", "user": addr},
                        self._on_message_received
                    )
                    self.subscriptions[addr] = sub_id
                    logger.info(f"  ✓ Abonné: {addr[:10]}...")
                except Exception as e:
                    logger.error(f"  ✗ Erreur d'abonnement pour {addr}: {e}")
                    return False
            
            self.connected = True
            self.reconnect_count = 0
            self.last_message_time = time.time()
            logger.info(f"✓ Connexion établie, {len(self.subscriptions)} abonnements actifs")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {e}", exc_info=True)
            self.connected = False
            return False

    def _reconnect(self):
        while self.running and self.reconnect_count < MAX_RECONNECT_ATTEMPTS:
            self.reconnect_count += 1
            delay = min(
                INITIAL_RECONNECT_DELAY * (2 ** (self.reconnect_count - 1)),
                MAX_RECONNECT_DELAY
            )
            
            logger.warning(
                f"Tentative de reconnexion {self.reconnect_count}/{MAX_RECONNECT_ATTEMPTS} "
                f"dans {delay}s..."
            )
            time.sleep(delay)
            
            self._close_connection()
            
            if self._connect():
                logger.info("✓ Reconnexion réussie !")
                return
            
            logger.error(f"✗ Échec de la tentative {self.reconnect_count}")
        
        if self.reconnect_count >= MAX_RECONNECT_ATTEMPTS:
            logger.critical(
                f"Échec après {MAX_RECONNECT_ATTEMPTS} tentatives de reconnexion. Arrêt du worker."
            )
            self.stop()

    def _heartbeat_monitor(self):
        while self.running:
            time.sleep(HEARTBEAT_INTERVAL)
            
            if not self.connected:
                continue
            
            time_since_last_message = time.time() - self.last_message_time
            
            if time_since_last_message > HEARTBEAT_TIMEOUT:
                logger.warning(
                    f"Aucun message reçu depuis {time_since_last_message:.0f}s "
                    f"(timeout: {HEARTBEAT_TIMEOUT}s). Vérification de la connexion..."
                )
                
                self.connected = False
                self._reconnect()

    def _close_connection(self):
        if not self.info_client:
            return
        
        try:
            for addr, sub_id in self.subscriptions.items():
                try:
                    self.info_client.unsubscribe({"type": "userFills", "user": addr}, sub_id)
                except Exception:
                    pass
            
            if hasattr(self.info_client, 'ws_manager') and self.info_client.ws_manager:
                if hasattr(self.info_client.ws_manager, 'ws'):
                    self.info_client.ws_manager.ws.close()
        except Exception as e:
            logger.debug(f"Erreur lors de la fermeture de connexion: {e}")

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
                
                if not self.connected and self.reconnect_count == 0:
                    logger.warning("Déconnexion détectée, tentative de reconnexion...")
                    self._reconnect()
                    
        except Exception as e:
            logger.error(f"Erreur inattendue dans la boucle principale : {e}")
            self.stop()

    def stop(self):
        self.running = False
        self.connected = False
        logger.info("Arrêt en cours...")
        
        self._close_connection()
        
        logger.info("Worker terminé.")
        os._exit(0)

    def _on_message_received(self, message: Dict[str, Any]):
        try:
            self.last_message_time = time.time()
            
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
