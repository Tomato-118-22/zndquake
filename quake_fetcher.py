import requests
import websocket
import json
import threading
import time

# HTTP
P2PQUAKE_URL = "https://api.p2pquake.net/v2/history"
WOLFX_EEW_URL = "https://api.wolfx.jp/jma_eew.json"
WOLFX_EQ_URL = "https://api.wolfx.jp/jma_eq.json"

HEADERS = {
    "User-Agent": "ZundaQuake/1.0",
    "Accept": "application/json"
}

# WebSocket
P2P_WS_URL = "wss://api.p2pquake.net/v2/ws"
WOLFX_EEW_WS_URL = "wss://ws-api.wolfx.jp/jma_eew"
WOLFX_EQ_WS_URL = "wss://ws-api.wolfx.jp/jma_eqlist"

def fetch_p2pquake():
    # P2PQuakeから履歴を取得
    params = {"limit": 10}
    try:
        r = requests.get(P2PQUAKE_URL, params=params, headers=HEADERS, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def fetch_p2p_history(limit: int = 30) -> list:
    """P2PQuake APIから地震情報(code=551)の履歴を取得して返す。"""
    try:
        r = requests.get(
            P2PQUAKE_URL,
            params={"codes": 551, "limit": limit},
            headers=HEADERS,
            timeout=10
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return []

# fetch_wolfx()、fetch_wolfx_eq()は必要ないが、main.pyに残しているので消さない
def fetch_wolfx():
    # もう使わない
    try:
        r = requests.get(WOLFX_EEW_URL, headers=HEADERS, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def fetch_wolfx_eq():
    # もう使わない
    try:
        r = requests.get(WOLFX_EQ_URL, headers=HEADERS, timeout=5)
        r.raise_for_status()
        j = r.json()
        
        # リストが返る場合は最初の要素を返す
        if isinstance(j, list):
            if len(j) == 0:
                return None
            return j[0]
        # dictの場合はそのまま返す
        return j
    except Exception:
        return None

def _run_ws_forever(url, on_message_func):
    def on_open(ws):
        print(f"WS Connected: {url}")
    
    def on_error(ws, error):
        print(f"WS Error ({url}): {error}")
    
    def on_close(ws, status, msg):
        print(f"WS Closed ({url}). Reconnecting...")
        time.sleep(3)

    def on_msg_wrapper(ws, message):
        try:
            data = json.loads(message)
            on_message_func(data)
        except Exception:
            pass

    while True:
        try:
            ws = websocket.WebSocketApp(
                url,
                on_open=on_open,
                on_message=on_msg_wrapper,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever()
        except Exception:
            time.sleep(5)

def connect_p2pquake_ws(callback):
    threading.Thread(target=_run_ws_forever, args=(P2P_WS_URL, callback), daemon=True).start()

def connect_wolfx_eew_ws(callback):
    threading.Thread(target=_run_ws_forever, args=(WOLFX_EEW_WS_URL, callback), daemon=True).start()

def connect_wolfx_eq_ws(callback):
    def list_handler(data):
        if isinstance(data, list):
            for item in data:
                callback(item)
        else:
            callback(data)
    threading.Thread(target=_run_ws_forever, args=(WOLFX_EQ_WS_URL, list_handler), daemon=True).start()

def make_eew_event_key(data: dict):
    # EEWが同一かをここで確かめる
    return (
        data.get("OriginTime"),
        round(data.get("Latitude", 0.0), 2),
        round(data.get("Longitude", 0.0), 2),
    )

def is_p2p_eew(item: dict) -> bool:
    return item.get("code") == 556

def is_p2p_eq_info(item: dict) -> bool:
    return item.get("code") == 551

def make_p2p_eew_key(item: dict):
    issue = item.get("issue", {})
    return issue.get("eventId")