import time
import json
import sys
import os
import traceback
from typing import Dict, Any, List

from hyperliquid.info import Info
from hyperliquid.utils import constants

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app.core.config import settings

subscription_ids: Dict[str, int] = {}
should_stop = False


def print_message(message: Dict[str, Any]):
    global should_stop
    if should_stop:
        return

    try:
        data = message.get("data") or {}
        if data.get("isSnapshot"):
            return
        print(json.dumps(message, indent=2))
    except Exception:
        if not should_stop:
            print("Erreur lors du traitement du message :")
            traceback.print_exc()
            print("Message brut :", message)


def main():
    global subscription_ids, should_stop

    print("-----------------------------------------------------")
    print("Démarrage du Hyperliquid User Fills Listener...")
    print("-----------------------------------------------------")

    try:
        info_client = Info(constants.MAINNET_API_URL, skip_ws=False)
    except Exception as e:
        print(f"Erreur d'initialisation du client Info : {e}")
        return

    address_string = settings.ACCOUNT_ADDRESS or ""
    addresses: List[str] = [
        addr.strip() for addr in address_string.split(",") if addr.strip()
    ]

    if not addresses:
        print("Aucune adresse valide trouvée dans ACCOUNT_ADDRESS.")
        print("Arrêt du listener.")
        return

    print(f"Connexion OK -> {constants.MAINNET_API_URL}")
    print(f"Abonnement aux fills de {len(addresses)} adresse(s).")
    print("-----------------------------------------------------")

    print("\n--- ABONNEMENTS EN COURS ---")
    for addr in addresses:
        print(f"-> Abonnement: {addr[:10]}...")
        try:
            sub_id = info_client.subscribe(
                {"type": "userFills", "user": addr},
                print_message
            )
            subscription_ids[addr] = sub_id
        except Exception as e:
            print(f"Erreur d'abonnement ({addr}) : {e}")

    print("\nListener actif. Ctrl+C pour arrêter.")
    print("-----------------------------------------------------")

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n\nArrêt demandé par l'utilisateur...")
    finally:
        should_stop = True
        
        print("Désabonnement en cours...")
        for addr, sub_id in subscription_ids.items():
            try:
                info_client.unsubscribe(
                    {"type": "userFills", "user": addr},
                    sub_id
                )
                print(f"  -> Désabonné: {addr[:10]}...")
            except Exception as e:
                print(f"  -> Erreur désabonnement ({addr[:10]}): {e}")

        time.sleep(0.5)

        try:
            if hasattr(info_client, 'ws_manager') and info_client.ws_manager:
                if hasattr(info_client.ws_manager, 'ws') and info_client.ws_manager.ws:
                    info_client.ws_manager.ws.close()
            elif hasattr(info_client, 'ws') and info_client.ws:
                info_client.ws.close()
            print("WebSocket fermé.")
        except Exception as e:
            print(f"Erreur fermeture WS: {e}")

        print("Listener terminé.")
        os._exit(0)


if __name__ == "__main__":
    main()