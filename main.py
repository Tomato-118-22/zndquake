'''
ZUNDAQUAKE
EARTHQUAKE & TSUNAMI PROGRAM
VERSION: BETA 1.0.0
COPYRIGHT TOMATO ALL RIGHTS RESERVED.
'''

'''
Why are you reading this sentence?
Article 3-3 of the EURA prohibits reverse engineering and decompiling.
'''

import os
import threading
import time
import traceback
from datetime import datetime
import sys
import logging
from pathlib import Path
import urllib.request
from notifypy import Notify
import json as _json

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QDialog, QScrollArea, QFrame, QTabWidget, QCheckBox, QMessageBox,
    QComboBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPoint, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QColor, QWheelEvent, QMouseEvent, QIcon
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

from quake_fetcher import (
    connect_wolfx_eew_ws,
    connect_p2pquake_ws,
    fetch_p2pquake, 
    fetch_wolfx,
    fetch_p2p_history,
    make_eew_event_key
)

from notifier import (
    play_eew_sequence, 
    play_wav_sync, 
    play_quake_info_sequence, 
    play_shindo_sokuho_sequence, 
    play_destination_sequence,
    play_eew_forecast_sequence,
    # play_eew_update_sequence,
    play_eew_cancel_sequence,
    play_tsunami_sequence,
    convert_city_list_to_regions
)

# ユーザー位置取得
def get_user_location():
    # 仮の実装として None を返す
    return None, None

print("DEBUG: All imports finished")

# ID管理変数
latest_p2p_ids = {
    551: None,
    552: None,
    556: None
}
latest_id_wolfx = None
latest_serial_wolfx = None
latest_eew_event_key = None

APP_START_TIME = time.time()

EEW_AREA_TO_PREF = {
    # 北海道
    "石狩地方北部": "北海道道央", "石狩地方中部": "北海道道央", "石狩地方南部": "北海道道央",
    "後志地方北部": "北海道道央", "後志地方東部": "北海道道央", "後志地方西部": "北海道道央",
    "空知地方北部": "北海道道央", "空知地方中部": "北海道道央", "空知地方南部": "北海道道央",
    "胆振地方西部": "北海道道央", "胆振地方中東部": "北海道道央",
    "日高地方西部": "北海道道央", "日高地方中部": "北海道道央", "日高地方東部": "北海道道央",
    "渡島地方北部": "北海道道南", "渡島地方東部": "北海道道南", "渡島地方西部": "北海道道南",
    "檜山地方": "北海道道南", "奥尻島": "北海道道南",
    "上川地方北部": "北海道道北", "上川地方中部": "北海道道北", "上川地方南部": "北海道道北",
    "留萌地方中北部": "北海道道北", "留萌地方南部": "北海道道北",
    "宗谷地方北部": "北海道道北", "宗谷地方南部": "北海道道北", "北海道利尻礼文": "北海道道北",
    "網走地方": "北海道道東", "北見地方": "北海道道東", "紋別地方": "北海道道東",
    "十勝地方北部": "北海道道東", "十勝地方中部": "北海道道東", "十勝地方南部": "北海道道東",
    "釧路地方北部": "北海道道東", "釧路地方中南部": "北海道道東",
    "根室地方北部": "北海道道東", "根室地方中部": "北海道道東", "根室地方南部": "北海道道東",
    # 東北
    "青森県津軽北部": "青森", "青森県津軽南部": "青森",
    "青森県三八上北": "青森", "青森県下北": "青森",
    "岩手県沿岸北部": "岩手", "岩手県沿岸南部": "岩手",
    "岩手県内陸北部": "岩手", "岩手県内陸南部": "岩手",
    "宮城県北部": "宮城", "宮城県中部": "宮城", "宮城県南部": "宮城",
    "秋田県沿岸北部": "秋田", "秋田県沿岸南部": "秋田",
    "秋田県内陸北部": "秋田", "秋田県内陸南部": "秋田",
    "山形県庄内": "山形", "山形県最上": "山形",
    "山形県村山": "山形", "山形県置賜": "山形",
    "福島県中通り": "福島", "福島県浜通り": "福島", "福島県会津": "福島",
    # 関東
    "茨城県北部": "茨城", "茨城県南部": "茨城",
    "栃木県北部": "栃木", "栃木県南部": "栃木",
    "群馬県北部": "群馬", "群馬県南部": "群馬",
    "埼玉県北部": "埼玉", "埼玉県南部": "埼玉", "埼玉県秩父": "埼玉",
    "千葉県北東部": "千葉", "千葉県北西部": "千葉", "千葉県南部": "千葉",
    "東京都23区": "東京都", "東京都多摩東部": "東京都", "東京都多摩西部": "東京都",
    "東京都伊豆大島": "伊豆諸島", "東京都新島": "伊豆諸島",
    "東京都神津島": "伊豆諸島", "東京都三宅島": "伊豆諸島", "東京都八丈島": "伊豆諸島",
    "東京都小笠原": "小笠原",
    "神奈川県東部": "神奈川", "神奈川県西部": "神奈川",
    # 北陸
    "新潟県上越": "新潟", "新潟県中越": "新潟",
    "新潟県下越": "新潟", "新潟県佐渡": "新潟",
    "富山県東部": "富山", "富山県西部": "富山",
    "石川県能登": "石川", "石川県加賀": "石川",
    "福井県嶺北": "福井", "福井県嶺南": "福井",
    # 甲信
    "山梨県東部・富士五湖": "山梨", "山梨県中西部": "山梨",
    "長野県北部": "長野", "長野県中部": "長野", "長野県南部": "長野",
    # 東海
    "岐阜県飛騨": "岐阜", "岐阜県美濃東部": "岐阜", "岐阜県美濃中西部": "岐阜",
    "静岡県伊豆": "静岡", "静岡県東部": "静岡",
    "静岡県中部": "静岡", "静岡県南部": "静岡",
    "愛知県東部": "愛知", "愛知県西部": "愛知",
    "三重県北部": "三重", "三重県中部": "三重", "三重県南部": "三重",
    # 近畿
    "滋賀県北部": "滋賀", "滋賀県南部": "滋賀",
    "京都府北部": "京都府", "京都府南部": "京都府",
    "大阪府北部": "大阪府", "大阪府南部": "大阪府",
    "兵庫県北部": "兵庫", "兵庫県南部": "兵庫", "兵庫県淡路島": "兵庫",
    "奈良県": "奈良",
    "和歌山県北部": "和歌山", "和歌山県南部": "和歌山",
    # 中国
    "鳥取県北部": "鳥取", "鳥取県中部": "鳥取", "鳥取県南部": "鳥取",
    "島根県東部": "島根", "島根県西部": "島根", "島根県隠岐": "島根",
    "岡山県北部": "岡山", "岡山県南部": "岡山",
    "広島県北部": "広島", "広島県南東部": "広島", "広島県南西部": "広島",
    "山口県北部": "山口", "山口県東部": "山口",
    "山口県中部": "山口", "山口県西部": "山口",
    # 四国
    "徳島県北部": "徳島", "徳島県南部": "徳島",
    "香川県東部": "香川", "香川県西部": "香川",
    "愛媛県東予": "愛媛", "愛媛県中予": "愛媛", "愛媛県南予": "愛媛",
    "高知県東部": "高知", "高知県中部": "高知", "高知県西部": "高知",
    # 九州
    "福岡県福岡": "福岡", "福岡県北九州": "福岡",
    "福岡県筑豊": "福岡", "福岡県筑後": "福岡",
    "佐賀県北部": "佐賀", "佐賀県南部": "佐賀",
    "長崎県北部": "長崎", "長崎県南部": "長崎", "長崎県島原半島": "長崎",
    "長崎県対馬": "長崎", "長崎県壱岐": "長崎", "長崎県五島": "長崎",
    "熊本県阿蘇": "熊本", "熊本県熊本": "熊本",
    "熊本県球磨": "熊本", "熊本県天草・芦北": "熊本",
    "大分県北部": "大分", "大分県中部": "大分",
    "大分県南部": "大分", "大分県西部": "大分",
    "宮崎県北部平野部": "宮崎", "宮崎県北部山沿い": "宮崎",
    "宮崎県南部平野部": "宮崎", "宮崎県南部山沿い": "宮崎",
    "鹿児島県薩摩": "鹿児島", "鹿児島県大隅": "鹿児島",
    "鹿児島県十島村": "鹿児島", "鹿児島県甑島": "鹿児島",
    "鹿児島県種子島": "鹿児島", "鹿児島県屋久島": "鹿児島",
    "鹿児島県奄美北部": "奄美群島", "鹿児島県奄美南部": "奄美群島",
    # 沖縄
    "沖縄県本島北部": "沖縄本土", "沖縄県本島中南部": "沖縄本土",
    "沖縄県久米島": "沖縄本土", "沖縄県大東島": "大東島",
    "沖縄県宮古島": "宮古島", "沖縄県石垣島": "八重山",
    "沖縄県与那国島": "八重山", "沖縄県西表島": "八重山",
}

def eew_area_to_pref(area_name: str) -> str:
    # 区域名を県名に変更
    return EEW_AREA_TO_PREF.get(area_name, area_name)

def eew_areas_to_prefs(area_names: list) -> list:
    seen = set()
    result = []
    for a in area_names:
        pref = eew_area_to_pref(a)
        if pref not in seen:
            seen.add(pref)
            result.append(pref)
    return result

# 画像マップ連番
EEW_IMG_MAP = {
    "北海道道北": "002", "北海道道央": "003", "北海道道南": "004", "北海道道東": "005",
    "青森": "007", "秋田": "008", "岩手": "009", "宮城": "010",
    "山形": "011", "福島": "012", "茨城": "014", "栃木": "015",
    "群馬": "016", "埼玉": "017", "東京都": "018", "千葉": "019", "神奈川": "020",
    "伊豆諸島": "022", "小笠原": "023", "新潟": "024", "富山": "025",
    "石川": "026", "福井": "027", "長野": "029", "山梨": "030",
    "岐阜": "032", "静岡": "033", "愛知": "034", "三重": "035",
    "兵庫": "037", "京都府": "038", "滋賀": "039", "大阪府": "040",
    "奈良": "041", "和歌山": "042", "鳥取": "044", "島根": "045",
    "岡山": "046", "広島": "047", "山口": "048", "香川": "050",
    "愛媛": "051", "徳島": "052", "高知": "053", "福岡": "055",
    "大分": "056", "佐賀": "057", "長崎": "058", "熊本": "059", "宮崎": "060",
    "鹿児島": "061", "奄美群島": "062", "沖縄本土": "064",
    "大東島": "065", "宮古島": "066", "八重山": "067"
}

TSUNAMI_REGION_TO_ID = {
    "オホーツク海沿岸": "001", "北海道太平洋沿岸東部": "002", "北海道太平洋沿岸中部": "003",
    "北海道太平洋沿岸西部": "004", "北海道日本海沿岸北部": "005", "北海道日本海沿岸南部": "006",
    "陸奥湾": "007", "青森県太平洋沿岸": "008", "青森県日本海沿岸": "009",
    "岩手県": "010", "宮城県": "011", "福島県": "012", "秋田県": "013", "山形県": "014",
    "茨城県": "015", "千葉県九十九里・外房": "016", "千葉県内房": "017", "東京湾内湾": "018",
    "伊豆諸島": "019", "小笠原諸島": "020", "相模湾・三浦半島": "021", "静岡県": "022",
    "愛知県外海": "023", "伊勢・三河湾": "024", "三重県南部": "025",
    "新潟県上中下越": "026", "佐渡": "027", "富山県": "028",
    "石川県能登": "029", "石川県加賀": "030", "福井県": "031",
    "京都府": "032", "兵庫県北部": "033", "兵庫県南部": "034", "兵庫県瀬戸内海沿岸": "035",
    "淡路島南部": "036", "大阪府": "037", "和歌山県": "038",
    "鳥取県": "039", "島根県出雲・石見": "040", "島根県隠岐": "041",
    "岡山県": "042", "広島県": "043", "香川県": "044",
    "愛媛県瀬戸内海沿岸": "045", "愛媛県宇和海沿岸": "046",
    "徳島県": "047", "高知県": "048",
    "山口県瀬戸内海沿岸": "049", "山口県日本海沿岸": "050",
    "福岡県瀬戸内海沿岸": "051", "福岡県日本海沿岸": "052",
    "佐賀県北部": "053", "長崎県西方": "054", "壱岐・対馬": "055",
    "有明・八代海": "056", "熊本県天草灘沿岸": "057",
    "大分県瀬戸内海沿岸": "058", "大分県豊後水道沿岸": "059",
    "宮崎県": "060",
    "鹿児島県東部": "061", "鹿児島県西部": "062",
    "種子島・屋久島地方": "063", "奄美群島・トカラ列島": "064",
    "沖縄本島地方": "065", "宮古島・八重山地方": "066", "大東島地方": "067"
}

SETTINGS_PATH = Path(__file__).parent / "datas" / "settings.json"

_DEFAULT_SETTINGS = {
    "version": VERSION if "VERSION" in dir() else "-1.0.0",
    "lang": "ja-JP",
    "country": "ja",
    "home-ja": {
        "main-municipality": "",
        "sub-municipality": []
    },
    "autorun": False,
    "log-save": True,
    "show-debug": False,
    "notify-shindo": 10,
    "notify-forecast": False,
    "pref-discrict": 10
}

def load_settings() -> dict:
    try:
        if SETTINGS_PATH.exists():
            import re
            text = SETTINGS_PATH.read_text(encoding="utf-8")
            text = re.sub(r"//[^\n]*", "", text)
            data = _json.loads(text)
            # トップレベルをマージしつつ、home-jaは個別にマージ
            merged = _json.loads(_json.dumps(_DEFAULT_SETTINGS)) # ディープコピー
            for k, v in data.items():
                if k == "home-ja" and isinstance(v, dict):
                    merged["home-ja"].update(v)
                else:
                    merged[k] = v
            return merged
    except Exception as e:
        print(f"[Settings] load error: {e}")
    return _json.loads(_json.dumps(_DEFAULT_SETTINGS)) # ディープコピー

def save_settings(settings: dict) -> None:
    try:
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_PATH.write_text(
            _json.dumps(settings, ensure_ascii=False, indent=4),
            encoding="utf-8"
        )
    except Exception as e:
        print(f"[Settings] save error: {e}")

# バージョン
VERSION = "Beta 1.0.0"

# 起動時に読み込み
APP_SETTINGS = load_settings()

# ログ設定
timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
log_filename = f"log-{timestamp}.txt"
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_path = log_dir / log_filename

logger = logging.getLogger("gui_print")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

def _apply_log_save(enabled: bool) -> None:
    # ログファイル書き出しのon/offを動的に切り替える
    logger.handlers.clear()
    if enabled:
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

# 初回はsettingsに従って設定
_initial_log_save = load_settings().get("log-save", True)
_apply_log_save(_initial_log_save)

class PrintToLogger:
    def write(self, message):
        if message and not message.isspace():
            logger.info(message.rstrip())
    def flush(self):
        for h in logger.handlers:
            h.flush()

sys.stdout = PrintToLogger()
sys.stderr = PrintToLogger()

def convert_intensity(scale_int: int) -> str:
    mapping = {
        10: "1", 20: "2", 30: "3", 40: "4",
        45: "5弱", 50: "5強", 55: "6弱", 60: "6強", 70: "7"
    }
    return mapping.get(scale_int, "不明")

def convert_wolfx_intensity(scale_str: str) -> int:
    mapping = {
        "1": 10, "2": 20, "3": 30, "4": 40,
        "5弱": 45, "5強": 50, "6弱": 55, "6強": 60, "7": 70
    }
    return mapping.get(scale_str, 0)


# Qt用シグナルエミッター
class SignalEmitter(QObject):
    log_signal = pyqtSignal(str)
    update_eew_map_signal = pyqtSignal(list)
    update_tsunami_map_signal = pyqtSignal(list)
    update_quake_info_signal = pyqtSignal(dict)
    update_tsunami_info_signal = pyqtSignal(list)
    update_eew_info_signal = pyqtSignal(dict)
    show_window_signal = pyqtSignal()

# Wolfxデータ処理(EEW予報&津波)
def process_wolfx_data(item: dict, log_func, update_map_func, update_eew_ui_func=None, is_silent=False):
    global latest_eew_event_key
    n = Notify()
    n.urgency="normal"
    try:
        title = item.get("Title") or item.get("title", "")
        # キャンセル報
        if item.get("isCancel") is True:
            if not is_silent:
                n.title = "緊急地震速報(キャンセル報)"
                n.message = "先程の緊急地震速報は取り消されました。"
                n.icon = "icons/icon_2048x.png"
                n.application_name = "ZundaQuake"
                n.send()
            log_func("緊急地震速報(キャンセル報) 先程の緊急地震速報は取り消されました。")
            update_map_func([])
            if not is_silent:
                threading.Thread(target=play_eew_cancel_sequence, daemon=True).start()
            latest_eew_event_key = None
            return

        if not item.get("OriginTime") or not item.get("EventID"):
            return

        # イベントキーの生成
        eew_event_key = (
            item.get("OriginTime"),
            round(item.get("Latitude", 0.0), 2),
            round(item.get("Longitude", 0.0), 2),
        )

        # 続報判定
        is_zokuho = False
        if latest_eew_event_key == eew_event_key:
            is_zokuho = True
        else:
            latest_eew_event_key = eew_event_key

        # 基本情報
        hypo_name = item.get("Hypocenter", "不明")
        mag_raw = item.get("Magunitude", -1.0)
        try:
            if isinstance(mag_raw, str):
                magnitude = float(mag_raw.replace("M", ""))
            else:
                magnitude = float(mag_raw)
        except (ValueError, TypeError):
            magnitude = -1.0

        max_int_str = item.get("MaxIntensity", "不明")
        max_scale_int = convert_wolfx_intensity(max_int_str)

        # S波到達時間計算
        s_wave_sec = None
        #user_lat, user_lon = get_user_location()
        #if user_lat is not None and user_lon is not None:
        #    try:
        #        ot_str = item.get("OriginTime")
        #        ot_dt = datetime.strptime(ot_str, "%Y/%m/%d %H:%M:%S")
        #        depth_str = item.get("Depth", "10km").replace("km", "")
        #        depth = float(depth_str) if depth_str.replace(".", "").isdigit() else 10.0
        #        s_wave_sec = get_remaining_seconds(ot_dt, eew_event_key[1], eew_event_key[2], depth, user_lat, user_lon, "s_wave")
        #    except Exception as calc_err:
        #        print(f"Calc error: {calc_err}")

        serial = int(item.get("Serial", 1))
        is_warning = item.get("isWarn", False)
        is_forecast = not is_warning
        is_final = item.get("isFinal", False)

        # 予報の処理
        if is_forecast:
            event_id = item.get("EventID")
            _notify_forecast = APP_SETTINGS.get("notify-forecast", False)
            _notify_shindo   = APP_SETTINGS.get("notify-shindo", 30)
            # 予報onかつ予想最大震度が設定値以上の時のみ通知・再生
            _should_notify = not is_silent and _notify_forecast and max_scale_int >= _notify_shindo

            if is_zokuho:
                final_str = " [最終報]" if is_final else ""
                if _should_notify:
                    n.title = f"緊急地震速報(予報 第{serial}報{final_str})"
                    n.message = f"{hypo_name}で地震\nM{magnitude}\n推定最大震度{max_int_str}"
                    n.icon = "icons/icon_2048x.png"
                    n.application_name = "ZundaQuake"
                    n.send()
                msg = f"緊急地震速報(予報、続報第{serial}報{final_str})\n{hypo_name}で地震\nM{magnitude}\n最大震度{max_int_str}"
                log_func(msg)
                #続報は音声再生しない
                #if not is_silent:
                #    threading.Thread(target=lambda: play_eew_update_sequence(hypo_name, magnitude, max_scale_int), daemon=True).start()
            else:
                final_str = " [最終報]" if is_final else ""
                if _should_notify:
                    n.title = f"緊急地震速報(予報 第{serial}報{final_str})"
                    n.message = f"{hypo_name}で地震\nM{magnitude}\n推定最大震度{max_int_str}"
                    n.icon = "icons/icon_2048x.png"
                    n.application_name = "ZundaQuake"
                    n.send()
                msg = f"緊急地震速報(予報)\n{hypo_name}で地震\nM{magnitude}\n最大震度{max_int_str}"
                log_func(msg)
                if _should_notify:
                    threading.Thread(target=lambda eid=event_id: play_eew_forecast_sequence(hypo_name, magnitude, max_scale_int, event_id=eid), daemon=True).start()

        # 警報の処理
        if is_warning:
            print("Wolfx EEW警報受信")
        
        # 地図更新処理
        # 強い揺れが予想される地域を地図に表示
        target_areas = []
        areas_data = item.get("Areas", [])
        
        if areas_data:
            for area in areas_data:
                area_name = area.get("Name", "")
                area_scale_str = area.get("ScaleFrom", "")
                
                # 震度4以上の地域を地図に表示
                area_scale_int = convert_wolfx_intensity(area_scale_str)
                if area_scale_int >= 40 and area_name in EEW_IMG_MAP:
                    target_areas.append(area_name)
        
        # 地図更新を即座に実行
        update_map_func(target_areas)

    except Exception as e:
        log_func(f"Wolfx(EEW)処理エラー: {e}")
        traceback.print_exc()


# P2PQuakeデータ処理
def process_p2p_data(item: dict, log_func, announce_func, update_eew_map_func, update_tsunami_map_func, update_eew_ui_func=None, update_tsunami_info_func=None, is_silent=False):
    n = Notify()
    n.urgency="normal"
    try:
        code = item.get("code")

        if code == 554: # 緊急地震速報発表検知
            if not is_silent:
                n.title = "緊急地震速報"
                n.message = "緊急地震速報が発表されました。強い揺れに警戒してください。"
                n.icon = "icons/eew.png"
                n.application_name = "ZundaQuake"
                n.send()
            log_func("[緊急地震速報]")
            return

        elif code == 556: # 緊急地震速報(警報)
            process_p2p_eew(item, log_func, update_eew_ui_func, is_silent)
            return

        elif code == 551: # 地震情報
            process_p2p_eq(item, log_func, update_tsunami_info_func=update_tsunami_info_func, is_silent=is_silent)
            return

        elif code == 552: # 津波情報
            cancelled = item.get("cancelled", False)
            if cancelled:
                if not is_silent:
                    n.title = "津波に関する情報"
                    n.message = "全ての大津波警報、津波警報、津波注意報、津波予報(若干の海面変動)が解除されました。"
                    n.icon = "icons/tsunami.png"
                    n.application_name = "ZundaQuake"
                    n.send()
                log_func("津波予報は解除されました。")
                update_tsunami_map_func([]) 
                return

            areas = item.get("areas", [])
            if not areas:
                return  # areasが空なら何もしない
                
            major_regions = []
            warning_regions = []
            advisory_regions = []
            forecast_regions = []
            details_log = []
            map_data = []

            ui_areas = []
            for a in areas:
                name = a.get("name")
                grade = a.get("grade")
                first_height = a.get("firstHeight", {})
                max_height = a.get("maxHeight", {})
                
                if not name or not grade:
                    continue
                    
                map_data.append({"name": name, "grade": grade})
                
                arrival_time = first_height.get("arrivalTime")
                condition = first_height.get("condition")
                time_display = arrival_time if arrival_time else (condition if condition else "不明")
                height_desc = max_height.get("description")
                height_val = max_height.get("value")
                height_display = height_desc if height_desc else (f"{height_val}m" if height_val else "不明")
                
                details_log.append(f"・{name}: 到達 {time_display} / 高さ {height_display}")
                ui_areas.append({"name": name, "grade": grade, "arrival": time_display, "height": height_display})

                if grade == "MajorWarning": major_regions.append(name)
                elif grade == "Warning": warning_regions.append(name)
                elif grade == "Watch": advisory_regions.append(name)
                elif grade in ["Forecast", "Unknown"]: forecast_regions.append(name)
            
            if major_regions: 
                log_func(f"【大津波警報】: {'、'.join(major_regions)}")
                if not is_silent:
                    n.title = "大津波警報"
                    n.message = "大津波警報が発表されました。今すぐに高台や河川から遠く離れた場所に逃げてください。"
                    n.icon = "icons/tsunami.png"
                    n.application_name = "ZundaQuake"
                    n.send()
            if warning_regions: 
                log_func(f"【津波警報】: {'、'.join(warning_regions)}")
                if not is_silent:
                    n.title = "津波警報"
                    n.message = "津波警報が発表されました。急いで安全な場所に逃げてください。"
                    n.icon = "icons/tsunami.png"
                    n.application_name = "ZundaQuake"
                    n.send()
            if advisory_regions: 
                log_func(f"【津波注意報】: {'、'.join(advisory_regions)}")
                if not is_silent:
                    n.title = "津波注意報"
                    n.message = "津波注意報が発表されました。海岸には近寄らないでください。"
                    n.icon = "icons/icon_2048x.png"
                    n.application_name = "ZundaQuake"
                    n.send()
            if forecast_regions: 
                log_func(f"【津波予報(若干の海面変動)】: {'、'.join(forecast_regions)}")
                if not is_silent:
                    n.title = "津波予報(若干の海面変動)"
                    n.message = "津波予報(若干の海面変動)が発表されました。沿岸部にいる場合は十分に注意してください。"
                    n.icon = "icons/icon_2048x.png"
                    n.application_name = "ZundaQuake"
                    n.send()
                n.icon = "icons/icon_2048x.png"
                n.application_name = "ZundaQuake"
                n.send()
            if details_log: 
                log_func("\n".join(details_log))

            log_func(f"[DEBUG] 津波マップ更新 - {len(map_data)}件")
            update_tsunami_map_func(map_data)
            if update_tsunami_info_func and ui_areas:
                update_tsunami_info_func(ui_areas)

            if not is_silent:
                def _play_tsunami_all():
                    if major_regions:
                        play_tsunami_sequence("Major", major_regions)
                        time.sleep(0.25)
                    if warning_regions:
                        play_tsunami_sequence("Warning", warning_regions)
                        time.sleep(0.25)
                    if advisory_regions:
                        play_tsunami_sequence("Advisory", advisory_regions)
                        time.sleep(0.25)
                    if forecast_regions:
                        play_tsunami_sequence("Forecast", forecast_regions)
                threading.Thread(target=_play_tsunami_all, daemon=True).start()
            return
            
        elif code == 555: 
            return
        elif code == 561: 
            return
        else:
            log_func(f"その他情報受信 (code={code})")

    except Exception as e:
        log_func(f"データ処理エラー: {e}")
        print(traceback.format_exc())

active_p2p_eew = {}

# P2PQuake緊急地震速報(警報)
def process_p2p_eew(item: dict, log_func, update_eew_ui_func=None, is_silent=False):
    n = Notify()
    n.urgency="normal"
    try:
        issue = item.get("issue", {})
        earthquake = item.get("earthquake", {})
        areas = item.get("areas", [])

        event_id = issue.get("eventId")
        serial = int(issue.get("serial", 1))

        hypo = earthquake.get("hypocenter", {})
        name = hypo.get("name", "不明")
        mag = hypo.get("magnitude", -1)

        is_warning = any(a.get("kindCode") == "19" for a in areas)
        state = active_p2p_eew.get(event_id)

        log_func(f"[DEBUG] EEW処理: eventId={event_id}, serial={serial}, is_warning={is_warning}, 対象地域数={len(areas)}")

        # 新規EEW
        if state is None:
            active_p2p_eew[event_id] = {"serial": serial}
            if is_warning:
                # 区域名を県名に変換
                raw_names = [a.get("name", "") for a in areas if a.get("name")]
                prefs = sorted(set(eew_areas_to_prefs(raw_names)))
                prefs_str = "、".join(prefs)
                log_func(f"緊急地震速報(警報)\n{name}で地震 強い揺れに警戒\n対象地域: {prefs_str}")
                if not is_silent:
                    n.title = "緊急地震速報(警報)"
                    n.message = f"対象地域: {'、'.join(prefs_str)}"
                    n.icon = "icons/earthquake.png"
                    n.application_name = "ZundaQuake"
                    n.send()
                if not is_silent:
                    threading.Thread(target=lambda eid=event_id, pl=prefs: play_eew_sequence(pl, is_zokuho=False, event_id=eid), daemon=True).start()
            else:
                log_func(f"[DEBUG] 警報ではないため音声なし (kindCode != 19)")

        # 続報
        elif serial > state["serial"]:
            raw_names = [a.get("name", "") for a in areas if a.get("name")]
            prefs = sorted(set(eew_areas_to_prefs(raw_names)))
            prefs_str = "、".join(prefs)
            state["serial"] = serial
            log_func(f"緊急地震速報(警報、続報)\n{name}で地震 強い揺れに警戒\n対象地域: {prefs_str}")
            if not is_silent:
                n.title = "緊急地震速報(警報)"
                n.message = f"対象地域: {prefs_str}"
                n.icon = "icons/earthquake.png"
                n.application_name = "ZundaQuake"
                n.send()
            if not is_silent:
                threading.Thread(target=lambda eid=event_id, pl=prefs: play_eew_sequence(pl, is_zokuho=True, event_id=eid), daemon=True).start()
        else:
            log_func(f"[DEBUG] 既に受信済みのシリアル番号: {serial} <= {state['serial']}")
            
    except Exception as e:
        log_func(f"P2P EEW処理エラー: {e}")
        traceback.print_exc()

def process_p2p_eq(item: dict, log_func, update_tsunami_info_func=None, is_silent=False):
    n = Notify()
    n.urgency="normal"
    try:
        print(f"[process_p2p_eq] Called with item keys: {item.keys()}")
        
        issue = item.get("issue", {})
        eq = item.get("earthquake", {})
        hypo = eq.get("hypocenter", {})
        points = item.get("points", [])
        info_type = issue.get("type")

        print(f"[process_p2p_eq] info_type={info_type}")
        log_func(f"[DEBUG] 地震情報処理: type={info_type}")

        # 震度速報
        if info_type == "ScalePrompt":
            time_str = eq.get("time", "不明")
            max_scale = eq.get("maxScale", -1)
            max_scale_int = convert_intensity(max_scale)
            max_scale_areas = []
            
            if points:
                for point in points:
                    if point.get("scale") == max_scale and point.get("addr"):
                        max_scale_areas.append(point.get("addr"))

            max_scale_areas = list(dict.fromkeys(max_scale_areas))[:5]
            
            _notify_shindo = APP_SETTINGS.get("notify-shindo", 30)
            _should_notify = not is_silent and max_scale >= _notify_shindo
            if max_scale_areas:
                regions_str = "、".join(max_scale_areas)
                if _should_notify:
                    n.title = "震度速報"
                    n.message = f"{regions_str}: 震度{max_scale_int}"
                    n.icon = "icons/icon_2048x.png"
                    n.application_name = "ZundaQuake"
                    n.send()
                log_func(f"震度速報 発生時刻 {time_str}\n最大震度{max_scale_int}を'{regions_str}'で観測")
            else:
                if _should_notify:
                    n.title = "震度速報"
                    n.message = f"震度{max_scale_int}を観測"
                    n.icon = "icons/icon_2048x.png"
                    n.application_name = "ZundaQuake"
                    n.send()
                log_func(f"震度速報 発生時刻 {time_str}\n最大震度{max_scale_int}")

            if _should_notify:
                threading.Thread(target=lambda: play_shindo_sokuho_sequence(max_scale, max_scale_areas), daemon=True).start()
            return

        # 震源に関する情報
        elif info_type == "Destination":
            time_str = eq.get("time", "不明")
            name = hypo.get("name", "不明")
            mag = hypo.get("magnitude", -1)
            depth = hypo.get("depth", "不明")
            tsunami = eq.get("domesticTsunami", "None")
            
            if tsunami == "None":
                worry_tsunami = "この地震による津波の心配はありません。"
                tsunamino = "001"
            elif tsunami == "Checking":
                worry_tsunami = "津波の有無は現在調査中です。今後の情報に警戒してください。"
                tsunamino = "000"
            elif tsunami == "NonEffective":
                worry_tsunami = "この地震による多少の潮位の変化はあるかもしれませんが、被害の心配はありません。"
                tsunamino = "002"
            elif tsunami in ["Watch", "Advisory"]:
                worry_tsunami = "この地震により現在、津波注意報を発表しています。"
                tsunamino = "003"
            elif tsunami == "Warning":
                worry_tsunami = "この地震により現在、津波警報を発表しています。"
                tsunamino = "003"
            elif tsunami in ["Major", "MajorWarning"]:
                worry_tsunami = "この地震により現在、大津波警報を発表しています。"
                tsunamino = "003"
            else:
                worry_tsunami = "津波情報の受信に失敗しました。"
                tsunamino = "004"
                
            log_func(f"震源情報\n{name}で地震\n発生時刻 {time_str}\nM{mag}\n深さ{depth}km\n{worry_tsunami}")
            if not is_silent:
                n.title = "震源情報"
                n.message = f"{time_str}頃、{name}で地震がありました。\n{worry_tsunami}"
                n.icon = "icons/icon_2048x.png"
                n.application_name = "ZundaQuake"
                n.send()
            if not is_silent:
                threading.Thread(target=lambda: play_destination_sequence(name, tsunamino), daemon=True).start()
            return

        # 地震情報
        elif info_type == "DetailScale":
            time_str = eq.get("time", "不明")
            name = hypo.get("name", "不明")
            mag = hypo.get("magnitude", -1)
            depth = hypo.get("depth", "不明")
            max_scale = eq.get("maxScale", -1)
            max_scale_areas = []
            
            if points:
                for point in points:
                    if point.get("scale") == max_scale and point.get("addr"):
                        max_scale_areas.append(point.get("addr"))

            max_scale_areas = list(dict.fromkeys(max_scale_areas))[:5]
            
            _notify_shindo = APP_SETTINGS.get("notify-shindo", 30)
            _should_notify = not is_silent and max_scale >= _notify_shindo

            if max_scale_areas:
                regions_str = "、".join(max_scale_areas)
                if _should_notify:
                    n.title = "地震情報"
                    n.message = f"{time_str} {name}で地震\nM{mag} 深さ{depth}km\n最大震度{convert_intensity(max_scale)}を観測"
                    n.icon = "icons/icon_2048x.png"
                    n.application_name = "ZundaQuake"
                    n.send()
                log_func(f"地震情報\n{name}で地震\n発生時刻 {time_str}\nM{mag}\n深さ{depth}km\n最大震度{convert_intensity(max_scale)}を'{regions_str}'で観測")
            else:
                if _should_notify:
                    n.title = "地震情報"
                    n.message = f"{time_str} {name}で地震\nM{mag} 深さ{depth}km\n最大震度{convert_intensity(max_scale)}を観測"
                    n.icon = "icons/icon_2048x.png"
                    n.application_name = "ZundaQuake"
                    n.send()
                log_func(f"地震情報\n{name}で地震\n発生時刻 {time_str}\nM{mag}\n深さ{depth}km\n最大震度{convert_intensity(max_scale)}")

            if _should_notify:
                threading.Thread(target=lambda: play_quake_info_sequence(name, mag, depth, max_scale, max_scale_areas), daemon=True).start()
            return
        
        else:
            log_func(f"[DEBUG] 未対応の地震情報タイプ: {info_type}")
        
    except Exception as e:
        log_func(f"P2P地震情報処理エラー: {e}")
        traceback.print_exc()

# EEW表示ウィジェット
class EEWDisplayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_color = "#E53935"  # デフォルト色
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # タイトル部分
        self.title_label = QLabel("緊急地震速報")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setVisible(False)
        layout.addWidget(self.title_label)
        
        # S波到達まで
        self.arrival_label = QLabel("S波到達まで")
        self.arrival_label.setStyleSheet("font-size: 18px; color: #666;")
        self.arrival_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.arrival_label.setVisible(False)
        layout.addWidget(self.arrival_label)
        
        # カウントダウン表示
        self.countdown_label = QLabel("現在未実装")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setVisible(False)
        layout.addWidget(self.countdown_label)
        
        # 秒表示
        self.sec_label = QLabel("秒")
        self.sec_label.setStyleSheet("font-size: 24px; color: #666;")
        self.sec_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sec_label.setVisible(False)
        layout.addWidget(self.sec_label)
        
        # 震源地表示
        self.detail_container = QWidget()
        self.detail_container.setVisible(False)
        detail_row = QHBoxLayout(self.detail_container)
        detail_row.setContentsMargins(0, 0, 0, 0)
        detail_row.setSpacing(8)

        # 左カラム: 震源地 + 詳細テキスト
        left_col = QWidget()
        left_col.setStyleSheet("background-color: #F5F5F5; border-radius: 5px;")
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(4)

        # 震源地表示
        self.epicenter_label = QLabel("")
        self.epicenter_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        self.epicenter_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.epicenter_label.setWordWrap(True)
        left_layout.addWidget(self.epicenter_label)

        # 詳細情報表示
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                background-color: transparent;
                line-height: 1.8;
            }
        """)
        self.detail_label.setWordWrap(True)
        left_layout.addWidget(self.detail_label)
        left_layout.addStretch()

        detail_row.addWidget(left_col, stretch=1)

        # 震度アイコン表示
        self.shindo_icon_lbl = QLabel()
        self.shindo_icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.shindo_icon_lbl.setStyleSheet("background-color: transparent;")
        self.shindo_icon_lbl.setFixedWidth(110)
        detail_row.addWidget(self.shindo_icon_lbl)

        layout.addWidget(self.detail_container)
        
        # 対象地域表示
        self.areas_label = QLabel("")
        self.areas_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                padding: 15px;
                background-color: #FFF3E0;
                border-radius: 5px;
                line-height: 1.6;
            }
        """)
        self.areas_label.setWordWrap(True)
        self.areas_label.setVisible(False)
        layout.addWidget(self.areas_label)
        
        # メッセージ表示
        self.message_label = QLabel("")
        self.message_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 10px;
                color: #666;
            }
        """)
        self.message_label.setWordWrap(True)
        self.message_label.setVisible(False)
        layout.addWidget(self.message_label)
        
        # デフォルトメッセージ
        self.default_label = QLabel("現在、緊急地震速報は発表されていません")
        self.default_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #999;
                padding: 50px;
            }
        """)
        self.default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.default_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def get_color_by_intensity(self, max_intensity_value):
        if max_intensity_value <= 20:  # 震度1-2
            return "#4CAF50", "予報"  # 緑
        elif max_intensity_value <= 40:  # 震度3-4
            return "#FBC02D", "予報"  # 黄色
        elif max_intensity_value <= 55:  # 震度5弱-5強
            return "#E53935", "警報"  # 赤
        else:  # 震度6弱以上
            return "#7B1FA2", "特別警報"  # 紫
    
    def show_eew(self, is_forecast, epicenter, magnitude, depth, max_intensity_str, max_intensity_value, countdown=None, areas=None, serial=1, is_final=False):
        print(f"[EEWDisplayWidget.show_eew] Called!")
        print(f"  is_forecast={is_forecast}, epicenter={epicenter}, magnitude={magnitude}")
        print(f"  max_intensity_str={max_intensity_str}, max_intensity_value={max_intensity_value}")
        
        self.default_label.setVisible(False)
        
        # 震度から色を決定
        color, level_text = self.get_color_by_intensity(max_intensity_value)
        self.current_color = color
        
        # タイトル作成
        if is_forecast:
            title_text = f"緊急地震速報(予報"
        else:
            title_text = f"緊急地震速報({level_text}"
        
        if is_final:
            title_text += f" 第{serial}報 最終報)"
        else:
            title_text += f" 第{serial}報)"
        
        # タイトル更新
        self.title_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }}
        """)
        self.title_label.setText(title_text)
        self.title_label.setVisible(True)
        
        # カウントダウン表示
        if countdown is not None and countdown >= 0:
            self.arrival_label.setVisible(True)
            self.countdown_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 80px;
                    font-weight: bold;
                    color: {color};
                }}
            """)
            self.countdown_label.setText(f"{countdown:02d}" if countdown <= 99 else "99+")
            self.countdown_label.setVisible(True)
            self.sec_label.setVisible(True)
        else:
            self.arrival_label.setVisible(False)
            self.countdown_label.setVisible(False)
            self.sec_label.setVisible(False)
        
        # 震源地表示
        self.epicenter_label.setText(f"{epicenter}で地震")

        # 詳細情報
        details = []
        details.append(f"マグニチュード: M{magnitude}")
        if depth:
            details.append(f"深さ: {depth}km")
        if max_intensity_str:
            details.append(f"予想最大震度: {max_intensity_str}")
        self.detail_label.setText("\n".join(details))

        # 震度アイコン更新
        scale_to_file = {
            "1": "10", "2": "20", "3": "30", "4": "40",
            "5弱": "45", "5強": "50", "6弱": "55", "6強": "60", "7": "70"
        }
        icon_file_num = scale_to_file.get(str(max_intensity_str), "")
        if icon_file_num:
            icon_pix = QPixmap(f"images/Shindo_{icon_file_num}.png")
            if not icon_pix.isNull():
                icon_pix = icon_pix.scaledToHeight(100, Qt.TransformationMode.SmoothTransformation)
                self.shindo_icon_lbl.setPixmap(icon_pix)
            else:
                self.shindo_icon_lbl.clear()
        else:
            self.shindo_icon_lbl.clear()

        self.detail_container.setVisible(True)
        
        # 対象地域表示
        if not is_forecast and areas:
            areas_text = "対象地域:\n" + "、".join(areas)
            self.areas_label.setText(areas_text)
            self.areas_label.setVisible(True)
        else:
            self.areas_label.setVisible(False)
        
        # メッセージ
        if is_forecast:
            message = "揺れに注意してください。\nWolfx APIより受信\n音声読み上げ: VOICEVOX 東北きりたん"
        else:
            if max_intensity_value >= 60:
                message = "慌てずに、まず身の安全を確保してください。\nWolfx API、P2P地震情報 APIより受信\n音声読み上げ: VOICEVOX 東北イタコ"
            elif max_intensity_value >= 50:
                message = "強い揺れに警戒してください。\nWolfx API、P2P地震情報 APIより受信\n音声読み上げ: VOICEVOX 東北イタコ"
            else:
                message = "対象地域では、強い揺れに警戒してください。\nWolfx API、P2P地震情報 APIより受信\n音声読み上げ: VOICEVOX 東北イタコ"
        
        self.message_label.setText(message)
        self.message_label.setVisible(True)
        
        print(f"[EEWDisplayWidget.show_eew] Completed!")
    
    def clear(self):
        self.title_label.setVisible(False)
        self.arrival_label.setVisible(False)
        self.countdown_label.setVisible(False)
        self.sec_label.setVisible(False)
        self.detail_container.setVisible(False)
        self.areas_label.setVisible(False)
        self.message_label.setVisible(False)
        self.default_label.setVisible(True)


# 震度別観測地域の折り畳みセクション
class CollapsibleSection(QWidget):
    # タイトルボタンを押すと展開/折り畳みができるセクション
    def __init__(self, title: str, color: str, indent: int = 0, parent=None):
        super().__init__(parent)
        self._expanded = False
        layout = QVBoxLayout(self)
        layout.setContentsMargins(indent, 2, 0, 2)
        layout.setSpacing(0)

        # トグルボタン
        font_size = 12 if indent > 0 else 13
        self.toggle_btn = QPushButton(f"▶ {title}")
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-size: {font_size}px;
                font-weight: bold;
                padding: 4px 10px;
                border: none;
                border-radius: 3px;
                text-align: left;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
        """)
        self.toggle_btn.clicked.connect(self._toggle)
        layout.addWidget(self.toggle_btn)

        # 中身
        self.content_widget = QWidget()
        self.content_widget.setVisible(False)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(indent + 10, 2, 4, 2)
        self.content_layout.setSpacing(1)
        layout.addWidget(self.content_widget)

    def _toggle(self):
        self._expanded = not self._expanded
        self.content_widget.setVisible(self._expanded)
        title = self.toggle_btn.text()[2:]
        self.toggle_btn.setText(("▼ " if self._expanded else "▶ ") + title)

    def add_row(self, text: str):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 13px; padding: 1px 4px; background-color: #F5F5F5; color: black;")
        lbl.setWordWrap(True)
        self.content_layout.addWidget(lbl)

    def add_child_section(self, section: "CollapsibleSection"):
        # 子CollapsibleSection(都道府県折り畳み)を追加する
        self.content_layout.addWidget(section)

    def clear_rows(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

# 地震情報表示ウィジェット
class QuakeInfoWidget(QWidget):
    _history_fetched = pyqtSignal(list)
    SCALE_INFO = {
        70: ("7",   "#9C27B0"),
        60: ("6強", "#E53935"),
        55: ("6弱", "#FF5722"),
        50: ("5強", "#FF9800"),
        45: ("5弱", "#FFC107"),
        40: ("4",   "#8BC34A"),
        30: ("3",   "#4CAF50"),
        20: ("2",   "#29B6F6"),
        10: ("1",   "#90A4AE"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._history_cache: list = []   # 取得済み履歴データ
        self._history_loaded = False
        self._history_fetched.connect(self._apply_history)
        self.init_ui()

    # UI構築 
    def init_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(6)

        # 履歴セレクタ行 
        selector_row = QHBoxLayout()
        selector_row.setSpacing(6)

        self.history_combo = QComboBox()
        self.history_combo.addItem("最新の地震情報")
        self.history_combo.setToolTip("過去の地震を選択して表示できます")
        self.history_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.history_combo.currentIndexChanged.connect(self._on_history_selected)
        selector_row.addWidget(self.history_combo)

        self.reload_btn = QPushButton("履歴を読み込む")
        self.reload_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #1565C0; }
        """)
        self.reload_btn.clicked.connect(self._load_history_async)
        selector_row.addWidget(self.reload_btn)

        outer.addLayout(selector_row)

        # スクロールエリア
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        self.info_widget = QWidget()
        self.info_layout = QVBoxLayout(self.info_widget)
        self.info_layout.setContentsMargins(0, 0, 0, 0)
        self.info_layout.setSpacing(6)
        scroll.setWidget(self.info_widget)
        outer.addWidget(scroll)

        # デフォルトメッセージ
        self.default_label = QLabel("現在、地震情報はありません")
        self.default_label.setStyleSheet("font-size: 18px; color: #999; padding: 50px;")
        self.default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_layout.addWidget(self.default_label)
        self.info_layout.addStretch()

    # 履歴の非同期ロード 
    def _load_history_async(self):
        self.reload_btn.setEnabled(False)
        self.reload_btn.setText("読み込み中...")
        threading.Thread(target=self._fetch_history_thread, daemon=True).start()

    def _fetch_history_thread(self):
        data = fetch_p2p_history(limit=50)
        self._history_fetched.emit(data)

    def _apply_history(self, data: list):
        self._history_cache = data
        self._history_loaded = True
        self.reload_btn.setEnabled(True)
        self.reload_btn.setText("履歴を更新")

        # コンボボックスを更新
        self.history_combo.blockSignals(True)
        current = self.history_combo.currentIndex()
        self.history_combo.clear()
        self.history_combo.addItem("最新の地震情報")

        for item in data:
            eq = item.get("earthquake", {})
            hypo = eq.get("hypocenter", {})
            issue = item.get("issue", {})
            info_type = issue.get("type", "")
            name = hypo.get("name", "不明")
            time_str = eq.get("time", "")[:16]   # "YYYY/MM/DD HH:MM"
            max_scale = eq.get("maxScale", -1)
            scale_str = convert_intensity(max_scale) if max_scale > 0 else "不明"
            mag = hypo.get("magnitude", "?")
            if info_type == "ScalePrompt":
                prefix = "【震度速報】 "
            elif info_type == "Destination":
                prefix = "【震源に関する情報】 "
            else:
                prefix = ""
            self.history_combo.addItem(f"{prefix}{time_str}  {name}  M{mag}  最大震度{scale_str}")

        self.history_combo.blockSignals(False)
        self.history_combo.setCurrentIndex(0)

    def _on_history_selected(self, index: int):
        if index == 0:
            # 最新の場合、現在表示をそのまま保持
            return
        history_index = index - 1
        if 0 <= history_index < len(self._history_cache):
            item = self._history_cache[history_index]
            self._display_from_p2p_item(item)

    def _display_from_p2p_item(self, item: dict):
        # P2P地震情報(code=551)のdictからUIを構築する。
        issue = item.get("issue", {})
        eq = item.get("earthquake", {})
        hypo = eq.get("hypocenter", {})
        points = item.get("points", [])

        info_type = issue.get("type", "DetailScale")
        time_str = eq.get("time", "不明")
        name = hypo.get("name", "不明")
        mag = hypo.get("magnitude", -1)
        depth = hypo.get("depth", "不明")
        max_scale = eq.get("maxScale", -1)
        tsunami = eq.get("domesticTsunami", "None")

        tsunami_map = {
            "None": "この地震による津波の心配はありません。",
            "Checking": "津波の有無は現在調査中です。",
            "NonEffective": "若干の海面変動があるかもしれませんが、被害の心配はありません。",
            "Watch": "津波注意報が発表されています。",
            "Advisory": "津波注意報が発表されています。",
            "Warning": "津波警報が発表されています。",
            "Major": "大津波警報が発表されています。",
            "MajorWarning": "大津波警報が発表されています。",
        }
        tsunami_text = tsunami_map.get(tsunami, "")

        quake_type_map = {
            "ScalePrompt": "震度速報",
            "Destination": "震源情報",
            "DetailScale": "地震情報",
        }
        quake_type = quake_type_map.get(info_type, "地震情報")
        max_intensity_str = convert_intensity(max_scale) if max_scale > 0 else ""

        # 最大震度の観測地域
        max_scale_areas = []
        if points and max_scale > 0:
            for p in points:
                if p.get("scale") == max_scale and p.get("addr"):
                    max_scale_areas.append(p["addr"])
            max_scale_areas = list(dict.fromkeys(max_scale_areas))[:5]

        self.show_quake_info(
            quake_type, time_str, name, mag, depth,
            max_intensity_str, tsunami_text, max_scale_areas, points
        )

    # メイン表示メソッド 
    def show_quake_info(self, quake_type, time_str, location, magnitude, depth,
                        max_intensity, tsunami_info, areas=None, points=None):
        '''
        areas: 最大震度の観測地域リスト(str)
        points: P2P APIのpoints配列(dictのリスト)
            各要素: {"addr", "pref", "scale", "isArea"}
        '''
        if areas is None:
            areas = []
        if points is None:
            points = []

        # レイアウトをクリア
        self._clear_info_layout()

        self.default_label.setVisible(False)

        # タイトルバー 
        color = self._title_color(max_intensity)
        title_lbl = QLabel(quake_type)
        title_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 7px 10px;
                border-radius: 5px;
            }}
        """)
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_layout.addWidget(title_lbl)

        # 基本情報グリッド風 
        info_row_widget = QWidget()
        info_row_widget.setStyleSheet("background-color: #FFF8E1; border-radius: 5px;")
        info_row_layout = QHBoxLayout(info_row_widget)
        info_row_layout.setContentsMargins(0, 0, 0, 0)
        info_row_layout.setSpacing(0)

        # 左: 基本情報テキスト
        basic_widget = QWidget()
        basic_widget.setStyleSheet("background-color: transparent;")
        basic_layout = QVBoxLayout(basic_widget)
        basic_layout.setContentsMargins(10, 8, 10, 8)
        basic_layout.setSpacing(3)

        def row(key, val):
            lbl = QLabel(f"<b>{key}</b>　{val}")
            lbl.setStyleSheet("font-size: 14px; color: black; background-color: transparent;")
            lbl.setWordWrap(True)
            basic_layout.addWidget(lbl)

        row("発生時刻", time_str)
        row("震源地", location)
        row("マグニチュード", f"M{magnitude}")
        row("深さ", f"{depth}km")
        if max_intensity:
            row("最大震度", max_intensity)
        if tsunami_info:
            tsunami_lbl = QLabel(tsunami_info)
            tsunami_color = "#E53935" if "警報" in tsunami_info else "#1976D2"
            tsunami_lbl.setStyleSheet(
                f"font-size: 13px; color: {tsunami_color}; font-weight: bold; "
                f"padding-top: 4px; background-color: transparent;"
            )
            tsunami_lbl.setWordWrap(True)
            basic_layout.addWidget(tsunami_lbl)

        basic_layout.addStretch()
        info_row_layout.addWidget(basic_widget, stretch=1)

        # 右: 震度アイコン
        scale_to_file = {
            "1": "10", "2": "20", "3": "30", "4": "40",
            "5弱": "45", "5強": "50", "6弱": "55", "6強": "60", "7": "70"
        }
        icon_file_num = scale_to_file.get(str(max_intensity), "")
        if icon_file_num:
            icon_path = f"images/Shindo_{icon_file_num}.png"
            icon_pix = QPixmap(icon_path)
            if not icon_pix.isNull():
                icon_pix = icon_pix.scaledToHeight(110, Qt.TransformationMode.SmoothTransformation)
                icon_lbl = QLabel()
                icon_lbl.setPixmap(icon_pix)
                icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                icon_lbl.setStyleSheet("background-color: transparent; padding: 6px;")
                info_row_layout.addWidget(icon_lbl)

        self.info_layout.addWidget(info_row_widget)

        # 最大震度観測地域
        if areas:
            # 市町村名を区域名に変換
            region_names = convert_city_list_to_regions(areas)
            max_area_lbl = QLabel("【最大震度観測地域】\n" + "　".join(region_names))
            max_area_lbl.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    color: white;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 6px 10px;
                    border-radius: 4px;
                }}
            """)
            max_area_lbl.setWordWrap(True)
            self.info_layout.addWidget(max_area_lbl)

        # 震度別観測地域
        if points:
            self._add_scale_sections(points)

        self.info_layout.addStretch()

    # 震度別セクション 
    def _add_scale_sections(self, points: list):
        # 震度の高い順にCollapsibleSectionを追加する
        from collections import defaultdict

        # scale→pref→addrの三段構造
        scale_pref_map: dict[int, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
        for p in points:
            s = p.get("scale", -1)
            addr = p.get("addr", "")
            pref = p.get("pref", "不明")
            if s > 0 and addr:
                scale_pref_map[s][pref].append(addr)

        if not scale_pref_map:
            return

        detail_header = QLabel("震度別の観測地域を表示")
        detail_header.setStyleSheet("font-size: 12px; color: #666; padding-top: 4px;")
        self.info_layout.addWidget(detail_header)

        for scale_val in sorted(scale_pref_map.keys(), reverse=True):
            scale_str, bg_color = self.SCALE_INFO.get(scale_val, ("?", "#9E9E9E"))
            pref_map = scale_pref_map[scale_val]
            total = sum(len(v) for v in pref_map.values())

            # 震度別セクション
            scale_section = CollapsibleSection(
                f"震度{scale_str}　({total}地点)",
                bg_color,
                indent=0
            )

            # 都道府県別サブセクション
            for pref in sorted(pref_map.keys()):
                addrs = pref_map[pref]
                # 都道府県ボタンは少し暗い色で
                r, g, b = self._darken_hex(bg_color, factor=0.75)
                pref_color = f"rgb({r},{g},{b})"
                pref_section = CollapsibleSection(
                    f"{pref}　({len(addrs)}地点)",
                    pref_color,
                    indent=12
                )
                for addr in addrs:
                    pref_section.add_row(f"　{addr}")
                scale_section.add_child_section(pref_section)

            self.info_layout.addWidget(scale_section)

    @staticmethod
    def _darken_hex(hex_color: str, factor: float) -> tuple[int, int, int]:
        # #RRGGBB をfactor倍暗くした(r,g,b)を返す
        hex_color = hex_color.lstrip("#")
        r = int(int(hex_color[0:2], 16) * factor)
        g = int(int(hex_color[2:4], 16) * factor)
        b = int(int(hex_color[4:6], 16) * factor)
        return max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))

    # ヘルパー 
    def _clear_info_layout(self):
        while self.info_layout.count():
            item = self.info_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # default_labelを再追加
        self.default_label = QLabel("現在、地震情報はありません")
        self.default_label.setStyleSheet("font-size: 18px; color: #999; padding: 50px;")
        self.default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.default_label.setVisible(False)
        self.info_layout.addWidget(self.default_label)

    def _title_color(self, max_intensity_str: str) -> str:
        mapping = {
            "7": "#9C27B0", "6強": "#E53935", "6弱": "#FF5722",
            "5強": "#FF9800", "5弱": "#FFC107",
            "4": "#8BC34A", "3": "#4CAF50", "2": "#29B6F6", "1": "#90A4AE",
        }
        return mapping.get(str(max_intensity_str), "#FF9800")

    def clear(self):
        self._clear_info_layout()
        self.default_label.setVisible(True)


# 津波情報表示ウィジェット
class TsunamiInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # タイトル
        self.title_label = QLabel("津波情報")
        self.title_label.setStyleSheet("""
            QLabel {
                background-color: #9C27B0;
                color: white;
                font-size: 20px;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
            }
        """)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setVisible(False)
        layout.addWidget(self.title_label)
        
        # スクロールエリア
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.info_widget = QWidget()
        self.info_layout = QVBoxLayout()
        self.info_widget.setLayout(self.info_layout)
        scroll.setWidget(self.info_widget)
        
        layout.addWidget(scroll)
        
        # デフォルトメッセージ
        self.default_label = QLabel("現在、津波情報はありません")
        self.default_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #999;
                padding: 50px;
            }
        """)
        self.default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_layout.addWidget(self.default_label)
        
        self.setLayout(layout)
    
    def show_tsunami_info(self, areas_data):
        # 既存の表示をクリア
        for i in reversed(range(self.info_layout.count())):
            self.info_layout.itemAt(i).widget().setParent(None)
        
        self.title_label.setVisible(True)
        
        if not areas_data:
            self.default_label = QLabel("現在、津波情報はありません")
            self.default_label.setStyleSheet("font-size: 18px; color: #999; padding: 50px;")
            self.default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.info_layout.addWidget(self.default_label)
            return
        
        # 階級別に表示
        major_areas = []
        warning_areas = []
        advisory_areas = []
        forecast_areas = []
        
        for area in areas_data:
            name = area.get('name', '')
            grade = area.get('grade', '')
            
            if grade == 'MajorWarning':
                major_areas.append(area)
            elif grade == 'Warning':
                warning_areas.append(area)
            elif grade == 'Watch':
                advisory_areas.append(area)
            else:
                forecast_areas.append(area)
        
        # 大津波警報
        if major_areas:
            self._add_tsunami_section("大津波警報", major_areas, "#FF00FF")
        
        # 津波警報
        if warning_areas:
            self._add_tsunami_section("津波警報", warning_areas, "#FF0000")
        
        # 津波注意報
        if advisory_areas:
            self._add_tsunami_section("津波注意報", advisory_areas, "#FFFF00")
        
        # 津波予報
        if forecast_areas:
            self._add_tsunami_section("津波予報", forecast_areas, "#00AAFF")
    
    def _add_tsunami_section(self, title, areas, color):
        section_label = QLabel(f"【{title}】")
        section_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
                border-radius: 3px;
            }}
        """)
        self.info_layout.addWidget(section_label)
        
        for area in areas:
            name = area.get('name', '不明')
            arrival = area.get('arrival', '不明')
            height = area.get('height', '不明')
            
            area_text = f"・{name}\n  到達: {arrival} / 高さ: {height}"
            area_label = QLabel(area_text)
            area_label.setStyleSheet("font-size: 14px; padding: 5px 10px; background-color: #F5F5F5; border-radius: 3px; margin: 2px;")
            self.info_layout.addWidget(area_label)
    
    def clear(self):
        for i in reversed(range(self.info_layout.count())):
            self.info_layout.itemAt(i).widget().setParent(None)
        
        self.title_label.setVisible(False)
        self.default_label = QLabel("現在、津波情報はありません")
        self.default_label.setStyleSheet("font-size: 18px; color: #999; padding: 50px;")
        self.default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_layout.addWidget(self.default_label)


# 地図ウィジェット
class MapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ウィンドウサイズに合わせて可変にする
        self.setMinimumSize(400, 300)
        
        # 地図の初期サイズ
        self.original_width = 6000
        self.original_height = 3554
        self.aspect_ratio = self.original_width / self.original_height  # 約1.688
        
        # 基本地図
        try:
            self.base_map = QPixmap("images/EEW_001.png")
            if self.base_map.isNull():
                print("WARNING: Base map image not found, creating blank pixmap")
                self.base_map = QPixmap(self.original_width, self.original_height)
                self.base_map.fill(QColor(50, 50, 50))
        except Exception as e:
            print(f"Error loading base map: {e}")
            self.base_map = QPixmap(self.original_width, self.original_height)
            self.base_map.fill(QColor(50, 50, 50))
        
        # EEWオーバーレイ
        self.eew_overlays = {}
        for region_name, file_id in EEW_IMG_MAP.items():
            img_path = f"images/EEW_{file_id}.png"
            self.eew_overlays[region_name] = {"path": img_path, "visible": False}
        
        # 津波オーバーレイ
        self.tsunami_overlays = {}
        grade_keys = {
            "MajorWarning": "Major",
            "Warning": "Warning",
            "Watch": "Advisory",
            "Forecast": "Forecast",
            "Unknown": "Forecast"
        }
        
        # 画像パスのみを保存
        for region_name, r_id in TSUNAMI_REGION_TO_ID.items():
            self.tsunami_overlays[region_name] = {}
            for g_api, g_file in grade_keys.items():
                if g_file not in self.tsunami_overlays[region_name]:
                    img_path = f"images/Tsunami_{g_file}_{r_id}.png"
                    self.tsunami_overlays[region_name][g_file] = {
                        "path": img_path,
                        "visible": False
                    }
        
        # 拡大縮小
        self.scale = 1.4
        self.offset_x = 0
        self.offset_y = 0
        self.last_pos = None
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # 描画品質を向上させる設定
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        
        # ウィジェットサイズに合わせたスケーリング計算
        widget_width = self.width()
        widget_height = self.height()
        widget_aspect = widget_width / widget_height
        
        # アスペクト比を保持して表示領域を計算
        if widget_aspect > self.aspect_ratio:
            # ウィジェットが横長→高さに合わせる
            base_scale = widget_height / self.original_height
        else:
            # ウィジェットが縦長→幅に合わせる
            base_scale = widget_width / self.original_width
        
        # 画像の中心を基準にズーム
        center_x = widget_width / 2
        center_y = widget_height / 2
        
        # 変換行列の適用
        painter.translate(center_x + self.offset_x, center_y + self.offset_y)
        painter.scale(self.scale * base_scale, self.scale * base_scale)
        painter.translate(-self.original_width / 2, -self.original_height / 2)
        
        # 基本地図
        painter.drawPixmap(0, 0, self.base_map)
        
        # EEWオーバーレイ
        for data in self.eew_overlays.values():
            if data["visible"]:
                img_path = data["path"]
                try:
                    pixmap = QPixmap(img_path)
                    if not pixmap.isNull():
                        # 967x573を6000x3554にスケール
                        painter.drawPixmap(
                            QRectF(0, 0, self.original_width, self.original_height),  # 描画先: 6000x3554
                            pixmap,
                            QRectF(0, 0, pixmap.width(), pixmap.height())  # 元画像サイズ
                        )
                except Exception as e:
                    print(f"Error drawing EEW image {img_path}: {e}")
        
        # 津波オーバーレイ
        for region_data in self.tsunami_overlays.values():
            for grade_data in region_data.values():
                if grade_data["visible"]:
                    img_path = grade_data["path"]
                    try:
                        pixmap = QPixmap(img_path)
                        if not pixmap.isNull():
                            # 967x573→6000x3554
                            painter.drawPixmap(
                                QRectF(0, 0, self.original_width, self.original_height),  # 描画先: 6000x3554
                                pixmap,
                                QRectF(0, 0, pixmap.width(), pixmap.height())  # 元画像サイズ
                            )
                    except Exception as e:
                        print(f"Error drawing tsunami image {img_path}: {e}")
    
    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        if delta > 0:
            self.scale = min(self.scale + 0.1, 5.0)
        else:
            self.scale = max(self.scale - 0.1, 0.5)
        self.update()
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_pos = event.pos()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.last_pos:
            delta = event.pos() - self.last_pos
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.last_pos = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        self.last_pos = None
    
    def clear_all_overlays(self):
        for data in self.eew_overlays.values():
            data["visible"] = False
        for region_data in self.tsunami_overlays.values():
            for grade_data in region_data.values():
                grade_data["visible"] = False
        self.update()
    
    def update_eew_map(self, target_areas):
        self.clear_all_overlays()
        for area in target_areas:
            if area in self.eew_overlays:
                self.eew_overlays[area]["visible"] = True
        self.update()
    
    def update_tsunami_map(self, areas_data):
        # 津波マップ更新
        print(f"DEBUG: MapWidget.update_tsunami_map called with {len(areas_data)} areas")
        self.clear_all_overlays()
        for item in areas_data:
            name = item.get('name')
            grade = item.get('grade')
            
            print(f"DEBUG: MapWidget processing - name={name}, grade={grade}")
            
            file_key = "Forecast"
            if grade == "MajorWarning": file_key = "Major"
            elif grade == "Warning": file_key = "Warning"
            elif grade == "Watch": file_key = "Advisory"
            
            if name in self.tsunami_overlays and file_key in self.tsunami_overlays[name]:
                self.tsunami_overlays[name][file_key]["visible"] = True
                print(f"DEBUG: MapWidget set visible - {name} / {file_key}")
            else:
                print(f"DEBUG: MapWidget - region or grade not found: {name} / {file_key}")
        
        self.update()
        print("DEBUG: MapWidget update() called")
    
    def zoom_in(self):
        self.scale = min(self.scale + 0.2, 5.0)
        self.update()
    
    def zoom_out(self):
        self.scale = max(self.scale - 0.2, 0.5)
        self.update()
    
    def reset_map(self):
        self.scale = 1.4
        self.offset_x = 0
        self.offset_y = 0
        self.update()


# テストダイアログ
class TestDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("テストメニュー選択")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        btn_eew_warning = QPushButton("緊急地震速報(警報)")
        btn_eew_warning.setStyleSheet("background-color: red; color: white; padding: 10px;")
        btn_eew_warning.clicked.connect(self.accept_eew_warning)
        
        btn_eew_forecast = QPushButton("緊急地震速報(予報)")
        btn_eew_forecast.setStyleSheet("padding: 10px;")
        btn_eew_forecast.clicked.connect(self.accept_eew_forecast)
        
        btn_shindo = QPushButton("震度速報")
        btn_shindo.setStyleSheet("padding: 10px;")
        btn_shindo.clicked.connect(self.accept_shindo)
        
        btn_destination = QPushButton("震源情報")
        btn_destination.setStyleSheet("padding: 10px;")
        btn_destination.clicked.connect(self.accept_destination)
        
        btn_quake_info = QPushButton("地震情報")
        btn_quake_info.setStyleSheet("padding: 10px;")
        btn_quake_info.clicked.connect(self.accept_quake_info)
        
        btn_tsunami = QPushButton("津波情報")
        btn_tsunami.setStyleSheet("padding: 10px;")
        btn_tsunami.clicked.connect(self.accept_tsunami)
        
        btn_cancel = QPushButton("キャンセル")
        btn_cancel.clicked.connect(self.reject)
        
        layout.addWidget(btn_eew_warning)
        layout.addWidget(btn_eew_forecast)
        layout.addWidget(btn_shindo)
        layout.addWidget(btn_destination)
        layout.addWidget(btn_quake_info)
        layout.addWidget(btn_tsunami)
        layout.addWidget(btn_cancel)
        
        self.setLayout(layout)
        self.test_type = None
    
    def accept_eew_warning(self):
        self.test_type = "eew_warning"
        self.accept()
    
    def accept_eew_forecast(self):
        self.test_type = "eew_forecast"
        self.accept()
    
    def accept_shindo(self):
        self.test_type = "shindo"
        self.accept()
    
    def accept_destination(self):
        self.test_type = "destination"
        self.accept()
    
    def accept_quake_info(self):
        self.test_type = "quake_info"
        self.accept()
    
    def accept_tsunami(self):
        self.test_type = "tsunami"
        self.accept()

# 説明ダイアログ
class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("このソフトについて")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # タイトル
        title_label = QLabel(f"ZundaQuake ver{VERSION}")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: black;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # サブタイトル
        text_label = QLabel("地震･津波情報受信ソフトウェア\n公式サイト: https://www.tomato-tts.com/officez/products/zndquake\n")
        text_label.setStyleSheet("font-size: 12px; color: black;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setWordWrap(True)
        layout.addWidget(text_label)

        # タブウィジェット
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #CCCCCC;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #E0E0E0;
                color: black;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                font-weight: bold;
            }
        """)

        # ZundaQuakeについて
        about_tab = QWidget()
        about_layout = QVBoxLayout()
        about_label = QLabel("[!]現在公開しているバージョンは開発中の物となります。このページに記載されているすべての機能がご利用できるわけではありません。また、誤情報の受信や、予期せぬ不具合が発生する可能性があります。必ず他の情報源と併用してください。\n\nZundaQuakeは、日本の地震情報を受信･表示し、音声で伝えるソフトウェアです。本バージョン(β1.0.0)の公開日である2026年3月11日は、東日本大震災から丁度15年という節目の日。あのような悲劇をもう繰り返さないために、ZundaQuakeは、高性能ながらも軽量で、誰でも簡単に使える事を目指して開発されました。\n名前の「ZundaQuake」は、2011年3月11日発生の東北地方太平洋沖地震(東日本大震災)から、被災地の東北地方の郷土料理のずんだ餅から「ずんだ(Zunda)」、地震を意味する「Quake」から取られました。東日本大震災の教訓を忘れず、防災意識を高めたいという思いから名付けられました。")
        about_label.setWordWrap(True)
        about_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        about_layout.addWidget(about_label)
        about_layout.addStretch()
        about_tab.setLayout(about_layout)
        self.tab_widget.addTab(about_tab, "ZundaQuakeについて")

        # 緊急地震速報について
        eew_tab = QWidget()
        eew_layout = QVBoxLayout()
        eew_label = QLabel("緊急地震速報は、地震発生後大きな揺れが到達する数秒から数十秒前に発表される、日本の気象庁が提供している地震早期警報システムである。予測震度5弱以上、長周期地震動階級3以上の時に発表され、テレビ放送や携帯端末等で「強い揺れとなる地域」を伝える一般向け(警報、特別警報)と、発表基準が低く第1報の精度が高くないが、情報の迅速性が高く各地の震度や震源情報が詳しくが分かる高度利用者向け(予報)の2種類がある。")
        eew_label.setWordWrap(True)
        eew_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        eew_layout.addWidget(eew_label)
        eew_layout.addStretch()
        eew_tab.setLayout(eew_layout)
        self.tab_widget.addTab(eew_tab, "緊急地震速報について")

        # 更新履歴
        history_tab = QWidget()
        history_layout = QVBoxLayout()
        history_label = QLabel("読み込み中...")
        history_label.setWordWrap(True)
        history_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        history_layout.addWidget(history_label)
        history_layout.addStretch()
        history_tab.setLayout(history_layout)
        self.tab_widget.addTab(history_tab, "更新履歴")
        self._load_update_history(history_label)

        # 利用規約
        term_tab = QWidget()
        term_layout = QVBoxLayout()
        term_scroll = QScrollArea()
        term_scroll.setWidgetResizable(True)
        term_inner = QWidget()
        term_inner_layout = QVBoxLayout()
        term_label = QLabel(self._load_licence_txt())
        term_label.setWordWrap(True)
        term_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        term_inner_layout.addWidget(term_label)
        term_inner_layout.addStretch()
        term_inner.setLayout(term_inner_layout)
        term_scroll.setWidget(term_inner)
        term_layout.addWidget(term_scroll)
        term_tab.setLayout(term_layout)
        self.tab_widget.addTab(term_tab, "利用規約")

        # ライセンス
        licence_tab = QWidget()
        licence_main_layout = QHBoxLayout()

        # ライブラリ一覧ボタン
        licence_btn_widget = QWidget()
        licence_btn_layout = QVBoxLayout()
        licence_btn_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.licence_display = QLabel("")
        self.licence_display.setWordWrap(True)
        self.licence_display.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.licence_display.setStyleSheet("padding: 8px;")

        # ライセンス情報
        licences = {
            "Python 3.13": "Python Software Foundation License\nhttps://docs.python.org/3/license.html",
            "PyQt6": "GNU General Public License v3\nhttps://www.riverbankcomputing.com/software/pyqt/",
            "requests": "Apache License 2.0\nhttps://github.com/psf/requests/blob/main/LICENSE",
            "P2P地震情報 API": "P2P地震情報 JSON API\nhttps://www.p2pquake.net/develop/json_api_v2/",
            "Wolfx API": "Wolfx Project 利用規約\nhttps://wolfx.jp/tos",
            "MapChart": "MapChart Terms and conditions\nhttps://www.mapchart.net/terms.html",
            "MuseScore4": "Musescore User Agreement – Terms of Service\nhttps://musescore.com/legal/terms",
            "VOICEVOX": "VOICEVOX ソフトウェア利用規約\nhttps://voicevox.hiroshiba.jp/term/"#,
            # 下の内容は今後の更新で実装される予定の機能で使用されるAPI等の利用規約なのでいまはコメントアウト
            #"Typecast": "Typecast Terms of Use\nhttps://help.typecast.ai/en/articles/13448178-terms-of-use", # 英語と韓国語の読み上げ
            #"A.I.VOICE": "株式会社エーアイ ご利用規約・免責事項\nhttps://www.ai-j.jp/agreement/\n\nユースケース / EULA\nhttps://aivoice.jp/product/kotonohatalk_ja/", # 中国語の読み上げ(台湾華語)
            #"音読さん": "「音読さん」利用規約\nhttps://ondoku3.com/ja/terms/", # スペイン語
            #"日本気象庁": "気象庁ホームページを通じて公開するＸＭＬ形式電文のご利用にあたっての留意事項\nhttps://xml.kishou.go.jp/considerationforxml.pdf", # JMAのXML API
            #"台湾中央気象署": "中華民國交通部中央氣象署 氣象開放資料平台 使用說明\nhttps://opendata.cwa.gov.tw/devManual/instruction", # CWA中華民国交通部中央気象署 解放資料
            #"ExpTech": "" # 台湾の地震の民間団体
            #"韓国気象庁": "기상청 API허브 이용안내\nhttps://apihub.kma.go.kr/apiInfo.do", # KMA韓国国土交通部気象庁 気象庁APIハブ
            #"Chile Alerta": "Chile Alerta - Api\nhttps://github.com/TBMSP/Chile-Alerta-API", # チリの地震の民間団体
            # メキシコ、ペルー等はまだAPIを見つけていない
        }

        for lib_name, licence_text in licences.items():
            btn = QPushButton(lib_name)
            btn.setStyleSheet("text-align: left; padding: 6px;")
            # デフォルト引数でクロージャのキャプチャ問題を回避
            btn.clicked.connect(lambda _, t=licence_text: self.licence_display.setText(t))
            licence_btn_layout.addWidget(btn)

        licence_btn_layout.addStretch()
        licence_btn_widget.setLayout(licence_btn_layout)

        # 右側: ライセンス表示エリア
        licence_right_widget = QWidget()
        licence_right_layout = QVBoxLayout()
        licence_scroll = QScrollArea()
        licence_scroll.setWidgetResizable(True)
        licence_scroll.setWidget(self.licence_display)
        licence_right_layout.addWidget(licence_scroll)
        licence_right_widget.setLayout(licence_right_layout)

        licence_main_layout.addWidget(licence_btn_widget, 1)
        licence_main_layout.addWidget(licence_right_widget, 2)
        licence_tab.setLayout(licence_main_layout)
        self.tab_widget.addTab(licence_tab, "ライセンス")

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

        # setLayoutの後にresizeを呼ぶ
        screen = QApplication.primaryScreen().availableGeometry()
        w = int(screen.width() * 0.3)
        h = int(screen.height() * 0.4)
        self.resize(w, h)

    def _load_update_history(self, label: QLabel):
        '''
        大体の形式:
        {
            [
                {"version": "Beta 1.0.1", "date": "2026-03-11", "changes": ["バグ修正", "機能追加"]},
                ...
            ]
        }
        '''
        try:
            url = "https://www.tomato-tts.com/officez/products/zndquake/update.json"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as res:
                data = _json.loads(res.read().decode("utf-8"))

            entries = data.get("versions", []) if isinstance(data, dict) else data
            lines = []
            for entry in entries:
                ver  = entry.get("version", "?")
                date = entry.get("date", "")
                changes = entry.get("changes", [])
                lines.append(f"- ver{ver}  ({date})")
                for c in changes:
                    lines.append(f"  ・{c}")
                lines.append("")
            label.setText("\n".join(lines) if lines else "更新履歴はありません。")

        except Exception as e:
            label.setText(f"更新履歴の取得に失敗しました。\n({e})")

    def _load_licence_txt(self) -> str:
        # licence.txt を読み込む
        path = Path(__file__).parent / "licence.txt"
        try:
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return "licence.txt が見つかりませんでした。"
        except Exception as e:
            return f"ファイルの読み込みに失敗しました。\n({e})"

# 設定ダイアログ
class SettingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("設定")
        self.setModal(True)
        self._settings = load_settings()
        self._parent = parent

        # municipality.json読み込み
        self._municipalities: dict[str, str] = {}  # {"01101": "札幌市中央区", ...}
        self._load_municipalities()

        outer = QVBoxLayout(self)

        # スクロールエリア
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(12)
        scroll.setWidget(content)
        outer.addWidget(scroll)

        def section_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(
                "font-size: 13px; font-weight: bold; color: white;"
                "background-color: #1976D2; padding: 4px 8px; border-radius: 3px;"
            )
            layout.addWidget(lbl)

        def note(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 11px; color: #666;")
            lbl.setWordWrap(True)
            layout.addWidget(lbl)

        # デバッグログ表示
        section_label("ログ")
        main_win = parent
        log_visible = self._settings.get("show-debug", False)
        self.chk_log_display = QCheckBox("デバッグログを表示する")
        self.chk_log_display.setChecked(log_visible)
        if main_win and hasattr(main_win, "toggle_log_display"):
            self.chk_log_display.stateChanged.connect(main_win.toggle_log_display)
        layout.addWidget(self.chk_log_display)

        self.chk_log_save = QCheckBox("ログを保存する")
        self.chk_log_save.setChecked(self._settings.get("log-save", True))
        layout.addWidget(self.chk_log_save)

        # 自宅設定
        section_label("自宅･勤務先設定")
        note("自宅(主な生活場所)と勤務先･学校(主な生活場所ではないが、通知する場所)を設定できます。\n現在のバージョンでは機能しません。")

        home_row = QHBoxLayout()
        home_row.addWidget(QLabel("自宅:"))
        self.combo_main = QComboBox()
        self.combo_main.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        home_row.addWidget(self.combo_main)
        layout.addLayout(home_row)

        # 通知設定
        section_label("通知設定")

        shindo_row = QHBoxLayout()
        shindo_row.addWidget(QLabel("通知する最大震度:"))
        self.combo_shindo = QComboBox()
        shindo_items = [
            ("震度1以上", 10), ("震度2以上", 20), ("震度3以上", 30), ("震度4以上", 40),
            ("震度5弱以上", 45), ("震度5強以上", 50), ("震度6弱以上", 55), ("震度6強以上", 60), ("震度7のみ", 70),
        ]
        current_shindo = self._settings.get("notify-shindo", 30)
        for label, val in shindo_items:
            self.combo_shindo.addItem(label, val)
            if val == current_shindo:
                self.combo_shindo.setCurrentIndex(self.combo_shindo.count() - 1)
        shindo_row.addWidget(self.combo_shindo)
        layout.addLayout(shindo_row)
        note("設定値以上の最大震度の地震情報のみ通知します。")

        self.chk_forecast = QCheckBox("緊急地震速報(高度利用者向け)も通知する")
        self.chk_forecast.setChecked(self._settings.get("notify-forecast", False))
        layout.addWidget(self.chk_forecast)

        # 府県予報区から地方予報区への切り替え
        section_label("緊急地震速報(一般向け)の表示範囲設定")
        note(
            "警報対象の府県予報区数が設定値以上になった場合、\n府県名の代わりに地方予報区で表示･読み上げます。\n現在のバージョンでは機能しません。"
        )
        dist_row = QHBoxLayout()
        dist_row.addWidget(QLabel("府県数:"))
        self.spin_pref_dist = QComboBox()
        for v in [0, 3, 5, 7, 10, 15, 20]:
            label = "常に府県名で通知" if v == 0 else f"{v}以上で地方名"
            self.spin_pref_dist.addItem(label, v)
            if v == self._settings.get("pref-discrict", 10):
                self.spin_pref_dist.setCurrentIndex(self.spin_pref_dist.count() - 1)
        dist_row.addWidget(self.spin_pref_dist)
        layout.addLayout(dist_row)

        layout.addStretch()

        # 保存/閉じるボタン
        btn_row = QHBoxLayout()
        save_btn = QPushButton("保存して閉じる")
        save_btn.setStyleSheet(
            "background-color: #1976D2; color: white; padding: 8px 20px;"
            "border-radius: 4px; font-size: 13px;"
        )
        save_btn.clicked.connect(self._save_and_close)
        cancel_btn = QPushButton("キャンセル")
        cancel_btn.setStyleSheet("padding: 8px 20px; border-radius: 4px; font-size: 13px;")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        outer.addLayout(btn_row)

        # 市町村コンボを非同期で読み込む
        self._fill_municipality_combo()

        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(int(screen.width() * 0.28), int(screen.height() * 0.55))

    def _load_municipalities(self):
        path = Path(__file__).parent / "datas" / "municipality.json"
        try:
            if path.exists():
                import re
                text = re.sub(r"//[^\n]*", "", path.read_text(encoding="utf-8"))
                data = _json.loads(text)
                muni_ja = data.get("municpality-ja", {})
                # "area"キーが重複しているためリスト形式を想定してフォールバック
                areas = muni_ja if isinstance(muni_ja, list) else [muni_ja]
                for area in areas:
                    for code, name in area.get("municipalities", {}).items():
                        self._municipalities[code] = name
        except Exception as e:
            print(f"[SettingDialog] municipality load error: {e}")


    def _fill_municipality_combo(self):
        current_main = self._settings.get("home-ja", {}).get("main-municipality", "")
        self.combo_main.blockSignals(True)
        self.combo_main.addItem("(未設定)", "")
        for code, name in sorted(self._municipalities.items()):
            self.combo_main.addItem(f"{code}  {name}", code)
            if code == current_main:
                self.combo_main.setCurrentIndex(self.combo_main.count() - 1)
        self.combo_main.blockSignals(False)

    def _save_and_close(self):
        self._settings["log-save"] = self.chk_log_save.isChecked()
        self._settings["show-debug"] = self.chk_log_display.isChecked()
        self._settings["notify-shindo"] = self.combo_shindo.currentData()
        self._settings["notify-forecast"] = self.chk_forecast.isChecked()
        self._settings["pref-discrict"] = self.spin_pref_dist.currentData()

        main_code = self.combo_main.currentData() or ""
        if "home-ja" not in self._settings:
            self._settings["home-ja"] = {}
        self._settings["home-ja"]["main-municipality"] = main_code

        save_settings(self._settings)

        # ログ書き出しを即時反映
        _apply_log_save(self._settings["log-save"])

        # グローバル設定を更新
        global APP_SETTINGS
        APP_SETTINGS = self._settings

        self.accept()

# メインウィンドウ
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        print("MainWindow.__init__ started")

        try:
            # 二重起動チェック
            test_socket = QLocalSocket()
            test_socket.connectToServer("ZundaQuake")
            
            if test_socket.waitForConnected(500):
                # 既存インスタンスが存在する
                print("Existing instance detected. Activating existing window...")
                test_socket.write(b"SHOW")
                test_socket.flush()
                test_socket.waitForBytesWritten(1000)
                test_socket.disconnectFromServer()
                
                # メッセージボックスを表示
                #QMessageBox.information(None, "ZundaQuake", 
                #    "ZundaQuakeは既に起動しています。\n既存のウィンドウを表示します。")
                
                # このインスタンスは終了
                QTimer.singleShot(0, lambda: QApplication.instance().quit())
                return
            
            test_socket.close()
            
            # サーバー起動
            QLocalServer.removeServer("ZundaQuake")
            self.server = QLocalServer(self)
            if not self.server.listen("ZundaQuake"):
                print(f"Failed to start server: {self.server.errorString()}")
            self.server.newConnection.connect(self.handle_connection)
            
            self.setWindowTitle("ZundaQuake Beta 1.0.0")
            self.setGeometry(100, 100, 1100, 700)
            
            # シグナルエミッター
            print("Creating signal emitter...")
            self.signal_emitter = SignalEmitter()
            self.signal_emitter.log_signal.connect(self.add_log_slot)
            self.signal_emitter.update_eew_map_signal.connect(self.update_eew_map_slot)
            self.signal_emitter.update_tsunami_map_signal.connect(self.update_tsunami_map_slot)
            # UI更新シグナルを接続
            self.signal_emitter.update_quake_info_signal.connect(self.update_quake_info_slot)
            self.signal_emitter.update_tsunami_info_signal.connect(self.update_tsunami_info_slot)
            self.signal_emitter.update_eew_info_signal.connect(self.update_eew_info_slot)
            # ウィンドウ表示シグナルを接続
            self.signal_emitter.show_window_signal.connect(self.ShowWindow)
            
            # 中央ウィジェット
            print("Creating central widget...")
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # メインレイアウト
            main_layout = QHBoxLayout()
            
            # 左側...地図エリア
            print("Creating map widget...")
            left_layout = QVBoxLayout()
            
            self.map_widget = MapWidget()
            left_layout.addWidget(self.map_widget)
            
            # 地図操作ボタン
            map_controls = QHBoxLayout()
            btn_zoom_in = QPushButton("拡大")
            btn_zoom_in.setStyleSheet("background-color: #F9F9F9; color: black; font-size: 14px;")
            btn_zoom_in.clicked.connect(self.map_widget.zoom_in)
            btn_zoom_out = QPushButton("縮小")
            btn_zoom_out.setStyleSheet("background-color: #F9F9F9; color: black; font-size: 14px;")
            btn_zoom_out.clicked.connect(self.map_widget.zoom_out)
            btn_reset = QPushButton("元に戻す")
            btn_reset.setStyleSheet("background-color: #F9F9F9; color: black; font-size: 14px;")
            btn_reset.clicked.connect(self.map_widget.reset_map)
            
            map_controls.addWidget(btn_zoom_in)
            map_controls.addWidget(btn_zoom_out)
            map_controls.addWidget(btn_reset)
            left_layout.addLayout(map_controls)
            
            # 右側レイアウト
            print("Creating right panel...")
            right_layout = QVBoxLayout()

            # ロゴ表示
            logo_label = QLabel()
            logo_pixmap = QPixmap(os.path.join("run", "logo.png"))
            if not logo_pixmap.isNull():
                scaled_logo = logo_pixmap.scaledToWidth(180, Qt.TransformationMode.SmoothTransformation)
                logo_label.setPixmap(scaled_logo)
            else:
                logo_label.setText("ZundaQuake")
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            right_layout.addWidget(logo_label)

            # タイトル
            title_label = QLabel("地震津波情報")
            title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: black;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            right_layout.addWidget(title_label)
            
            # タブウィジェット
            self.tab_widget = QTabWidget()
            self.tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #CCCCCC;
                    background-color: white;
                }
                QTabBar::tab {
                    background-color: #E0E0E0;
                    color: black;
                    padding: 8px 15px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: white;
                    font-weight: bold;
                }
            """)
            
            # EEWタブ
            self.eew_display = EEWDisplayWidget()
            self.tab_widget.addTab(self.eew_display, "緊急地震速報")
            
            # 地震情報タブ
            self.quake_info_display = QuakeInfoWidget()
            self.tab_widget.addTab(self.quake_info_display, "地震情報")
            
            # 津波タブ
            self.tsunami_display = TsunamiInfoWidget()
            self.tab_widget.addTab(self.tsunami_display, "津波情報")
            
            # 気象タブ
            weather_tab = QWidget()
            weather_layout = QVBoxLayout()
            weather_label = QLabel("お使いのバージョンでは、気象情報はご利用いただけません。")
            weather_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            weather_label.setStyleSheet("font-size: 16px; color: #999; padding: 50px;")
            weather_layout.addWidget(weather_label)
            weather_tab.setLayout(weather_layout)
            self.tab_widget.addTab(weather_tab, "気象")
            
            # 設定タブ
            settings_tab = QWidget()
            settings_layout = QVBoxLayout()
            settings_layout.setContentsMargins(15, 15, 15, 15)
            
            # テストメニューボタン
            test_btn = QPushButton("テストメニューを開く")
            test_btn.setStyleSheet("""
                QPushButton {
                    background-color: #81C784;
                    color: white;
                    padding: 10px;
                    font-size: 14px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #66BB6A;
                }
            """)
            test_btn.clicked.connect(self.open_test_menu)
            settings_layout.addWidget(test_btn)

            # 説明メニューボタン
            about_btn = QPushButton("このソフトについて")
            about_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E0E0E0;
                    color: white;
                    padding: 10px;
                    font-size: 14px;
                    border-radius: 5px;
                    color: black;
                }
                QPushButton:hover {
                    background-color: #CCCCCC;
                }
            """)
            about_btn.clicked.connect(self.open_about_menu)
            settings_layout.addWidget(about_btn)

            # 説明メニューボタン
            setting_btn = QPushButton("設定")
            setting_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E0E0E0;
                    color: white;
                    padding: 10px;
                    font-size: 14px;
                    border-radius: 5px;
                    color: black;
                }
                QPushButton:hover {
                    background-color: #CCCCCC;
                }
            """)
            setting_btn.clicked.connect(self.open_setting_menu)
            settings_layout.addWidget(setting_btn)
            
            settings_layout.addStretch()
            settings_tab.setLayout(settings_layout)
            self.tab_widget.addTab(settings_tab, "設定")
            
            right_layout.addWidget(self.tab_widget)
            
            # ログ表示エリア
            self.log_text = QTextEdit()
            self.log_text.setReadOnly(True)
            self.log_text.setStyleSheet("background-color: #F9F9F9; color: black; font-size: 12px;")
            self.log_text.setMaximumHeight(150)
            right_layout.addWidget(self.log_text)
            # 起動時にshow-debug設定を反映
            self.log_text.setVisible(APP_SETTINGS.get("show-debug", False))

            # レイアウトの組み立て
            print("Assembling layouts...")
            main_layout.addLayout(left_layout, 3)
            main_layout.addLayout(right_layout, 2)
            
            central_widget.setLayout(main_layout)
            
            # スタイル設定
            self.setStyleSheet("QMainWindow { background-color: #E0E0E0; }")
            
            print("MainWindow.__init__ completed")
            
            QTimer.singleShot(100, self.delayed_init)
            
        except Exception as e:
            print(f"Error in MainWindow.__init__: {e}")
            traceback.print_exc()
            raise

    def handle_connection(self):
        socket = self.server.nextPendingConnection()
        socket.readyRead.connect(lambda: self.process_command(socket))

    def process_command(self, socket):
        data = socket.readAll().data().decode()
        print(f"[LocalSocket] Received: {data}")
        if data == "SHOW":
            # シグナル経由でメインスレッドで実行
            print("[LocalSocket] Emitting show_window_signal")
            self.signal_emitter.show_window_signal.emit()
    
    def ShowWindow(self):
        print("[ShowWindow] Called")
        
        # 既に表示されている場合は最前面にするだけ
        if self.isVisible() and not self.isMinimized():
            print("[ShowWindow] Already visible, just raising to front")
            self.activateWindow()
            self.raise_()
            print("[ShowWindow] Completed (already visible)")
            return
        
        # 非表示または最小化されている場合
        if self.isMinimized():
            print("[ShowWindow] Restoring from minimized")
            self.showNormal()
        else:
            print("[ShowWindow] Showing window")
            self.show()

        # 最前面に持ってくる
        self.activateWindow()
        self.raise_()
        print("[ShowWindow] Completed")


    def closeEvent(self, event):
        event.ignore()
        self.hide()
    
    def delayed_init(self):
        try:
            print("delayed_init started")
            self.add_log("アプリケーション起動中...")
            
            # バックグラウンドスレッドで初期化を実行
            def background_init():
                try:
                    print("background_init: calling init_data_fetch")
                    self.init_data_fetch()
                    print("background_init: calling start_websockets")
                    self.start_websockets()
                    print("background_init: completed")
                except Exception as e:
                    print(f"Error in background_init: {e}")
                    traceback.print_exc()
                    self.add_log(f"初期化エラー: {e}")
            
            # スレッドで実行
            threading.Thread(target=background_init, daemon=True).start()

            # 起動時に履歴を自動読み込み
            self.quake_info_display._load_history_async()
            
        except Exception as e:
            print(f"Error in delayed_init: {e}")
            traceback.print_exc()
            self.add_log(f"初期化エラー: {e}")
    
    def add_log_slot(self, text):
        try:
            timestamp = time.strftime("%H:%M:%S")
            # テキストを先頭に追加
            current_text = self.log_text.toPlainText()
            new_text = f"[{timestamp}] {text}\n{current_text}"
            self.log_text.setPlainText(new_text)
        except Exception as e:
            print(f"Error in add_log_slot: {e}")
    
    def toggle_log_display(self, state):
        if state:
            self.log_text.setVisible(True)
        else:
            self.log_text.setVisible(False)
    
    def update_quake_info_slot(self, data):
        try:
            print(f"[update_quake_info_slot] Called with data keys: {data.keys()}")
            self.quake_info_display.show_quake_info(
                data.get("quake_type"),
                data.get("time_str"),
                data.get("name"),
                data.get("mag"),
                data.get("depth"),
                data.get("max_intensity"),
                data.get("tsunami_text"),
                data.get("areas", []),
                data.get("points", [])
            )
            self.tab_widget.setCurrentWidget(self.quake_info_display)
            print("[update_quake_info_slot] UI updated successfully")

            # 新しい地震情報受信時に履歴を自動再読み込み
            self.quake_info_display._load_history_async()
        except Exception as e:
            print(f"Error in update_quake_info_slot: {e}")
            traceback.print_exc()
    
    def update_tsunami_info_slot(self, ui_areas):
        try:
            print(f"[update_tsunami_info_slot] Called with {len(ui_areas)} areas")
            self.tsunami_display.show_tsunami_info(ui_areas)
            self.tab_widget.setCurrentWidget(self.tsunami_display)
            print("[update_tsunami_info_slot] UI updated successfully")
        except Exception as e:
            print(f"Error in update_tsunami_info_slot: {e}")
            traceback.print_exc()
    
    def update_eew_info_slot(self, data):
        try:
            print(f"[update_eew_info_slot] Called")
            print(f"  is_forecast={data.get('is_forecast')}")
            print(f"  max_intensity={data.get('max_intensity_str')}")
            print(f"  countdown={data.get('countdown')}")
            
            self.eew_display.show_eew(
                is_forecast=data.get("is_forecast", True),
                epicenter=data.get("epicenter", "不明"),
                magnitude=data.get("magnitude", 0),
                depth=data.get("depth", "不明"),
                max_intensity_str=data.get("max_intensity_str", "不明"),
                max_intensity_value=data.get("max_intensity_value", 0),
                countdown=data.get("countdown"),
                areas=data.get("areas"),
                serial=data.get("serial", 1),
                is_final=data.get("is_final", False)
            )
            self.tab_widget.setCurrentWidget(self.eew_display)
            print("[update_eew_info_slot] UI updated successfully")
        except Exception as e:
            print(f"Error in update_eew_info_slot: {e}")
            traceback.print_exc()
    
    def add_log(self, text):
        self.signal_emitter.log_signal.emit(text)
    
    def update_eew_map_slot(self, areas):
        self.map_widget.update_eew_map(areas)
    
    def update_eew_map(self, areas):
        self.signal_emitter.update_eew_map_signal.emit(areas)
    
    def update_tsunami_map_slot(self, areas_data):
        try:
            print(f"DEBUG: update_tsunami_map_slot called with {len(areas_data)} areas")
            
            # すべてのオーバーレイを非表示
            for region_data in self.map_widget.tsunami_overlays.values():
                for grade_data in region_data.values():
                    grade_data["visible"] = False
            
            # 指定された地域を表示
            for item in areas_data:
                name = item.get('name')
                grade = item.get('grade')
                
                print(f"DEBUG: Processing tsunami area - name={name}, grade={grade}")
                
                file_key = "Forecast"
                if grade == "MajorWarning": 
                    file_key = "Major"
                elif grade == "Warning": 
                    file_key = "Warning"
                elif grade == "Watch": 
                    file_key = "Advisory"
                
                if name in self.map_widget.tsunami_overlays:
                    if file_key in self.map_widget.tsunami_overlays[name]:
                        self.map_widget.tsunami_overlays[name][file_key]["visible"] = True
                        print(f"DEBUG: Set visible - {name} / {file_key}")
                    else:
                        print(f"DEBUG: file_key not found - {name} / {file_key}")
                else:
                    print(f"DEBUG: Region not found in tsunami_overlays - {name}")
            
            # マップを再描画
            self.map_widget.update()
            print("DEBUG: Map widget updated")
            
        except Exception as e:
            print(f"Error in update_tsunami_map_slot: {e}")
            traceback.print_exc()
    
    def update_tsunami_map(self, areas_data):
        self.signal_emitter.update_tsunami_map_signal.emit(areas_data)
    
    def announce(self, sound_file, text, log_text=None):
        if log_text:
            self.add_log(log_text)
        threading.Thread(target=lambda: play_wav_sync(sound_file), daemon=True).start()
    
    def open_test_menu(self):
        dialog = TestDialog(self)
        if dialog.exec():
            test_type = dialog.test_type
            if test_type == "eew_warning":
                self.run_test_eew_warning()
            elif test_type == "eew_forecast":
                self.run_test_eew_forecast()
            elif test_type == "shindo":
                self.run_test_shindo_sokuho()
            elif test_type == "destination":
                self.run_test_destination_info()
            elif test_type == "quake_info":
                self.run_test_quake_info()
            elif test_type == "tsunami":
                self.run_test_tsunami_info()

    def open_about_menu(self):
        dialog = AboutDialog(self)
        dialog.exec()
    
    def open_setting_menu(self):
        dialog = SettingDialog(self)
        dialog.exec()

    def run_test_eew_warning(self):
        def _run():
            n = Notify()
            n.urgency="critical"
            time.sleep(5)
            # ウィンドウを表示
            self.signal_emitter.show_window_signal.emit()
            time.sleep(0.1)  # UIの更新を待つ
            
            name = "宮城県沖"
            test_areas = ["宮城", "岩手", "福島", "秋田", "山形"]
            mag = 7.2
            max_int_value = 45 # 震度5-
            max_int_str = "5強"
            self.add_log(f"緊急地震速報(警報)\n{name}で地震 強い揺れに警戒\n対象地域: {test_areas}")
            self.update_eew_map(test_areas)
            n.title = "緊急地震速報"
            n.message = "緊急地震速報が発表されました。強い揺れに警戒してください。"
            n.icon = "icons/eew.png"
            n.application_name = "ZundaQuake"
            n.send()
            n.title = "緊急地震速報(警報)"
            n.message = f"対象地域: {'、'.join(test_areas)}"
            n.icon = "icons/earthquake.png"
            n.application_name = "ZundaQuake"
            n.send()
            # UIに表示
            self.eew_display.show_eew(
                is_forecast=False,
                epicenter=name,
                magnitude=mag,
                depth="10",
                max_intensity_str=max_int_str,
                max_intensity_value=max_int_value,
                countdown=5,
                areas=test_areas,
                serial=4,
                is_final=False
            )
            self.tab_widget.setCurrentWidget(self.eew_display)
            play_eew_sequence(test_areas)
        
        self.add_log("【テスト】5秒後にEEW警報を再生します...")
        threading.Thread(target=_run, daemon=True).start()
    
    def run_test_eew_forecast(self):
        def _run():
            n = Notify()
            n.urgency="normal"
            time.sleep(5)
            # ウィンドウを表示
            self.signal_emitter.show_window_signal.emit()
            time.sleep(0.1)  # UIの更新を待つ
            
            self.update_eew_map([])
            name = "宮城県沖"
            mag = 4.3
            max_int_value = 10  # 震度1
            max_int_str = "1"
            self.add_log(f"【テスト】緊急地震速報(予報)\n{name}で地震\nM{mag}\n最大震度{max_int_str}")
            n.title = f"緊急地震速報(予報 第1報)"
            n.message = f"{name}で地震\nM{mag}\n推定最大震度{max_int_str}"
            n.icon = "icons/icon_2048x.png"
            n.application_name = "ZundaQuake"
            n.send()
            # UIに表示
            self.eew_display.show_eew(
                is_forecast=True,
                epicenter=name,
                magnitude=mag,
                depth="10",
                max_intensity_str=max_int_str,
                max_intensity_value=max_int_value,
                countdown=10, # カウントダウンを追加
                areas=None, # 予報には対象地域なし
                serial=1,
                is_final=False
            )
            self.tab_widget.setCurrentWidget(self.eew_display)
            play_eew_forecast_sequence(name, mag, max_int_value)
        
        self.add_log("【テスト】5秒後にEEW予報を再生します...")
        threading.Thread(target=_run, daemon=True).start()
    
    def run_test_shindo_sokuho(self):
        def _run():
            time.sleep(5)
            # ウィンドウを表示
            self.signal_emitter.show_window_signal.emit()
            time.sleep(0.1)  # UIの更新を待つ
            
            self.update_eew_map([])
            time_str = "2011/03/11 14:46:17"
            max_int = 70
            max_scale_int = convert_intensity(max_int)
            max_scale_area = ["宮城県北部"]
            regions_str = "、".join(max_scale_area)
            self.add_log(f"【テスト】震度速報 発生時刻 {time_str}\n最大震度{max_scale_int}を'{regions_str}'で観測")
            
            # 通知を送信
            n = Notify()
            n.urgency = "normal"
            n.title = "震度速報"
            n.message = f"{regions_str}: 震度{max_scale_int}"
            n.icon = "icons/icon_2048x.png"
            n.application_name = "ZundaQuake"
            n.send()
            
            # シグナル経由でUIに表示
            self.signal_emitter.update_quake_info_signal.emit({
                "quake_type": "震度速報",
                "time_str": time_str,
                "name": "(詳細不明)",
                "mag": "-",
                "depth": "-",
                "max_intensity": max_scale_int,
                "tsunami_text": "",
                "areas": max_scale_area,
                "points": []
            })
            play_shindo_sokuho_sequence(max_int, max_scale_area)
        
        self.add_log("【テスト】5秒後に震度速報を再生します...")
        threading.Thread(target=_run, daemon=True).start()
    
    def run_test_destination_info(self):
        def _run():
            time.sleep(5)
            # ウィンドウを表示
            self.signal_emitter.show_window_signal.emit()
            time.sleep(0.1)  # UIの更新を待つ
            
            self.update_eew_map([])
            time_str = "2011/03/11 14:46:17"
            name = "三陸沖"
            mag = "7.9"
            depth = "10"
            worry_tsunami = "津波の有無は現在調査中です。今後の情報に警戒してください。"
            self.add_log(f"【テスト】震源情報\n{name}で地震\n発生時刻 {time_str}\nM{mag}\n深さ{depth}km\n{worry_tsunami}")
            
            # 通知を送信
            n = Notify()
            n.urgency = "normal"
            n.title = "震源情報"
            n.message = f"{time_str}頃、{name}で地震がありました。\n{worry_tsunami}"
            n.icon = "icons/icon_2048x.png"
            n.application_name = "ZundaQuake"
            n.send()
            
            # UIに表示
            self.signal_emitter.update_quake_info_signal.emit({
                "quake_type": "震源情報",
                "time_str": time_str,
                "name": name,
                "mag": mag,
                "depth": depth,
                "max_intensity": "",
                "tsunami_text": worry_tsunami,
                "areas": [],
                "points": []
            })
            play_destination_sequence("三陸沖", "000")
        
        self.add_log("【テスト】5秒後に震源情報を再生します...")
        threading.Thread(target=_run, daemon=True).start()
    
    def run_test_quake_info(self):
        def _run():
            time.sleep(5)
            # ウィンドウを表示
            self.signal_emitter.show_window_signal.emit()
            time.sleep(0.1)  # UIの更新を待つ
            
            self.update_eew_map([])
            time_str = "2011/03/11 14:46:17"
            name = "三陸沖"
            mag = 7.9
            depth = "20"
            max_scale = 70
            self.add_log(f"【テスト】地震情報\n{name}で地震\n発生時刻 {time_str}\nM{mag}\n深さ{depth}km\n最大震度{convert_intensity(max_scale)}")
            
            # 通知を送信
            n = Notify()
            n.urgency = "normal"
            n.title = "地震情報"
            n.message = f"{time_str} {name}で地震\nM{mag} 深さ{depth}km\n最大震度{convert_intensity(max_scale)}を観測"
            n.icon = "icons/icon_2048x.png"
            n.application_name = "ZundaQuake"
            n.send()
            
            # UIに表示
            self.signal_emitter.update_quake_info_signal.emit({
                "quake_type": "地震情報",
                "time_str": time_str,
                "name": name,
                "mag": mag,
                "depth": depth,
                "max_intensity": convert_intensity(max_scale),
                "tsunami_text": "この地震による津波の心配はありません。",
                "areas": ["栗原市築館"],
                "points": [
                    # 震度7
                    {"addr": "栗原市築館", "pref": "宮城県", "scale": 70},
                    # 震度6強: 宮城県
                    {"addr": "涌谷町新町", "pref": "宮城県", "scale": 60},
                    {"addr": "栗原市若柳", "pref": "宮城県", "scale": 60},
                    {"addr": "栗原市高清水", "pref": "宮城県", "scale": 60},
                    {"addr": "栗原市一迫", "pref": "宮城県", "scale": 60},
                    {"addr": "登米市米山町", "pref": "宮城県", "scale": 60},
                    {"addr": "登米市南方町", "pref": "宮城県", "scale": 60},
                    {"addr": "宮城美里町木間塚", "pref": "宮城県", "scale": 60},
                    {"addr": "大崎市古川三日町", "pref": "宮城県", "scale": 60},
                    {"addr": "大崎市古川北町", "pref": "宮城県", "scale": 60},
                    {"addr": "大崎市鹿島台", "pref": "宮城県", "scale": 60},
                    {"addr": "大崎市田尻", "pref": "宮城県", "scale": 60},
                    {"addr": "名取市増田", "pref": "宮城県", "scale": 60},
                    {"addr": "蔵王町円田", "pref": "宮城県", "scale": 60},
                    {"addr": "宮城川崎町前川", "pref": "宮城県", "scale": 60},
                    {"addr": "山元町浅生原", "pref": "宮城県", "scale": 60},
                    {"addr": "仙台宮城野区苦竹", "pref": "宮城県", "scale": 60},
                    {"addr": "石巻市桃生町", "pref": "宮城県", "scale": 60},
                    {"addr": "塩竈市旭町", "pref": "宮城県", "scale": 60},
                    {"addr": "東松島市矢本", "pref": "宮城県", "scale": 60},
                    {"addr": "大衡村大衡", "pref": "宮城県", "scale": 60},
                    # 福島県
                    {"addr": "白河市新白河", "pref": "福島県", "scale": 60},
                    {"addr": "須賀川市八幡町", "pref": "福島県", "scale": 60},
                    {"addr": "国見町藤田", "pref": "福島県", "scale": 60},
                    {"addr": "鏡石町不時沼", "pref": "福島県", "scale": 60},
                    {"addr": "天栄村下松本", "pref": "福島県", "scale": 60},
                    {"addr": "楢葉町北田", "pref": "福島県", "scale": 60},
                    {"addr": "富岡町本岡", "pref": "福島県", "scale": 60},
                    {"addr": "大熊町下野上", "pref": "福島県", "scale": 60},
                    {"addr": "双葉町新山", "pref": "福島県", "scale": 60},
                    {"addr": "浪江町幾世橋", "pref": "福島県", "scale": 60},
                    {"addr": "新地町谷地小屋", "pref": "福島県", "scale": 60},
                    # 茨城県
                    {"addr": "日立市助川小学校", "pref": "茨城県", "scale": 60},
                    {"addr": "日立市十王町友部", "pref": "茨城県", "scale": 60},
                    {"addr": "高萩市本町", "pref": "茨城県", "scale": 60},
                    {"addr": "笠間市中央", "pref": "茨城県", "scale": 60},
                    {"addr": "常陸大宮市北町", "pref": "茨城県", "scale": 60},
                    {"addr": "那珂市瓜連", "pref": "茨城県", "scale": 60},
                    {"addr": "小美玉市上玉里", "pref": "茨城県", "scale": 60},
                    {"addr": "筑西市舟生", "pref": "茨城県", "scale": 60},
                    {"addr": "鉾田市当間", "pref": "茨城県", "scale": 60},
                    # 栃木県
                    {"addr": "大田原市湯津上", "pref": "栃木県", "scale": 60},
                    {"addr": "宇都宮市白沢町", "pref": "栃木県", "scale": 60},
                    {"addr": "真岡市石島", "pref": "栃木県", "scale": 60},
                    {"addr": "市貝町市塙", "pref": "栃木県", "scale": 60},
                    {"addr": "高根沢町石末", "pref": "栃木県", "scale": 60},
                    # 震度5弱: 岩手県
                    {"addr": "大船渡市大船渡町", "pref": "岩手県", "scale": 55},
                    {"addr": "大船渡市猪川町", "pref": "岩手県", "scale": 55},
                    {"addr": "釜石市中妻町", "pref": "岩手県", "scale": 55},
                    {"addr": "滝沢村鵜飼", "pref": "岩手県", "scale": 55},
                    {"addr": "矢巾町南矢幅", "pref": "岩手県", "scale": 55},
                    {"addr": "花巻市大迫町", "pref": "岩手県", "scale": 55},
                    {"addr": "一関市山目", "pref": "岩手県", "scale": 55},
                    {"addr": "一関市花泉町", "pref": "岩手県", "scale": 55},
                    {"addr": "一関市千厩町", "pref": "岩手県", "scale": 55},
                    {"addr": "一関市室根町", "pref": "岩手県", "scale": 55},
                    {"addr": "一関市藤沢町", "pref": "岩手県", "scale": 55},
                    {"addr": "奥州市前沢区", "pref": "岩手県", "scale": 55},
                    {"addr": "奥州市衣川区", "pref": "岩手県", "scale": 55},
                    # 宮城県
                    {"addr": "気仙沼市赤岩", "pref": "宮城県", "scale": 55},
                    {"addr": "気仙沼市唐桑町", "pref": "宮城県", "scale": 55},
                    {"addr": "栗原市栗駒", "pref": "宮城県", "scale": 55},
                    {"addr": "栗原市瀬峰", "pref": "宮城県", "scale": 55},
                    {"addr": "栗原市金成", "pref": "宮城県", "scale": 55},
                    {"addr": "登米市中田町", "pref": "宮城県", "scale": 55},
                    {"addr": "登米市東和町", "pref": "宮城県", "scale": 55},
                    {"addr": "登米市豊里町", "pref": "宮城県", "scale": 55},
                    {"addr": "登米市登米町", "pref": "宮城県", "scale": 55},
                    {"addr": "登米市迫町", "pref": "宮城県", "scale": 55},
                    {"addr": "南三陸町志津川", "pref": "宮城県", "scale": 55},
                    {"addr": "南三陸町歌津", "pref": "宮城県", "scale": 55},
                    {"addr": "宮城美里町北浦", "pref": "宮城県", "scale": 55},
                    {"addr": "大崎市松山", "pref": "宮城県", "scale": 55},
                    {"addr": "白石市亘理町", "pref": "宮城県", "scale": 55},
                    {"addr": "仙台空港", "pref": "宮城県", "scale": 55},
                    {"addr": "角田市角田", "pref": "宮城県", "scale": 55},
                    {"addr": "岩沼市桜", "pref": "宮城県", "scale": 55},
                    {"addr": "大河原町新南", "pref": "宮城県", "scale": 55},
                    {"addr": "亘理町下小路", "pref": "宮城県", "scale": 55},
                    {"addr": "仙台青葉区大倉", "pref": "宮城県", "scale": 55},
                    {"addr": "仙台青葉区作並", "pref": "宮城県", "scale": 55},
                    {"addr": "仙台青葉区雨宮", "pref": "宮城県", "scale": 55},
                    {"addr": "仙台青葉区落合", "pref": "宮城県", "scale": 55},
                    {"addr": "仙台宮城野区五輪", "pref": "宮城県", "scale": 55},
                    {"addr": "仙台若林区遠見塚", "pref": "宮城県", "scale": 55},
                    {"addr": "仙台泉区将監", "pref": "宮城県", "scale": 55},
                    {"addr": "石巻市泉町", "pref": "宮城県", "scale": 55},
                    {"addr": "石巻市門脇", "pref": "宮城県", "scale": 55},
                    {"addr": "石巻市北上町", "pref": "宮城県", "scale": 55},
                    {"addr": "石巻市鮎川浜", "pref": "宮城県", "scale": 55},
                    {"addr": "石巻市相野谷", "pref": "宮城県", "scale": 55},
                    {"addr": "石巻市前谷地", "pref": "宮城県", "scale": 55},
                    {"addr": "東松島市小野", "pref": "宮城県", "scale": 55},
                    {"addr": "松島町高城", "pref": "宮城県", "scale": 55},
                    {"addr": "利府町利府", "pref": "宮城県", "scale": 55},
                    {"addr": "大和町吉岡", "pref": "宮城県", "scale": 55},
                    {"addr": "大郷町粕川", "pref": "宮城県", "scale": 55},
                    {"addr": "富谷町富谷", "pref": "宮城県", "scale": 55},
                    # 以下コメント略
                    {"addr": "福島市五老内町", "pref": "福島県", "scale": 55},
                    {"addr": "郡山市朝日", "pref": "福島県", "scale": 55},
                    {"addr": "郡山市開成", "pref": "福島県", "scale": 55},
                    {"addr": "郡山市湖南町", "pref": "福島県", "scale": 55},
                    {"addr": "白河市表郷", "pref": "福島県", "scale": 55},
                    {"addr": "須賀川市八幡山", "pref": "福島県", "scale": 55},
                    {"addr": "須賀川市長沼支所", "pref": "福島県", "scale": 55},
                    {"addr": "二本松市金色", "pref": "福島県", "scale": 55},
                    {"addr": "二本松市油井", "pref": "福島県", "scale": 55},
                    {"addr": "桑折町東大隅", "pref": "福島県", "scale": 55},
                    {"addr": "川俣町五百田", "pref": "福島県", "scale": 55},
                    {"addr": "西郷村熊倉", "pref": "福島県", "scale": 55},
                    {"addr": "中島村滑津", "pref": "福島県", "scale": 55},
                    {"addr": "矢吹町一本木", "pref": "福島県", "scale": 55},
                    {"addr": "棚倉町棚倉中居野", "pref": "福島県", "scale": 55},
                    {"addr": "玉川村小高", "pref": "福島県", "scale": 55},
                    {"addr": "浅川町浅川", "pref": "福島県", "scale": 55},
                    {"addr": "小野町中通", "pref": "福島県", "scale": 55},
                    {"addr": "小野町小野新町", "pref": "福島県", "scale": 55},
                    {"addr": "田村市大越町", "pref": "福島県", "scale": 55},
                    {"addr": "田村市常葉町", "pref": "福島県", "scale": 55},
                    {"addr": "田村市都路町", "pref": "福島県", "scale": 55},
                    {"addr": "田村市滝根町", "pref": "福島県", "scale": 55},
                    {"addr": "福島伊達市前川原", "pref": "福島県", "scale": 55},
                    {"addr": "福島伊達市梁川町", "pref": "福島県", "scale": 55},
                    {"addr": "本宮市白岩", "pref": "福島県", "scale": 55},
                    {"addr": "いわき市小名浜", "pref": "福島県", "scale": 55},
                    {"addr": "いわき市三和町", "pref": "福島県", "scale": 55},
                    {"addr": "いわき市錦町", "pref": "福島県", "scale": 55},
                    {"addr": "相馬市中村", "pref": "福島県", "scale": 55},
                    {"addr": "福島広野町下北迫大谷地原", "pref": "福島県", "scale": 55},
                    {"addr": "川内村上川内小山平", "pref": "福島県", "scale": 55},
                    {"addr": "川内村上川内早渡", "pref": "福島県", "scale": 55},
                    {"addr": "大熊町野上", "pref": "福島県", "scale": 55},
                    {"addr": "飯舘村伊丹沢", "pref": "福島県", "scale": 55},
                    {"addr": "南相馬市原町区高見町", "pref": "福島県", "scale": 55},
                    {"addr": "南相馬市鹿島区西町", "pref": "福島県", "scale": 55},
                    {"addr": "猪苗代町千代田", "pref": "福島県", "scale": 55},

                    {"addr": "水戸市金町", "pref": "茨城県", "scale": 55},
                    {"addr": "水戸市千波町", "pref": "茨城県", "scale": 55},
                    {"addr": "水戸市中央", "pref": "茨城県", "scale": 55},
                    {"addr": "水戸市内原町", "pref": "茨城県", "scale": 55},
                    {"addr": "日立市役所", "pref": "茨城県", "scale": 55},
                    {"addr": "常陸太田市高柿町", "pref": "茨城県", "scale": 55},
                    {"addr": "高萩市安良川", "pref": "茨城県", "scale": 55},
                    {"addr": "北茨城市磯原町", "pref": "茨城県", "scale": 55},
                    {"addr": "笠間市石井", "pref": "茨城県", "scale": 55},
                    {"addr": "笠間市下郷", "pref": "茨城県", "scale": 55},
                    {"addr": "ひたちなか市南神敷台", "pref": "茨城県", "scale": 55},
                    {"addr": "ひたちなか市東石川", "pref": "茨城県", "scale": 55},
                    {"addr": "茨城町小堤", "pref": "茨城県", "scale": 55},
                    {"addr": "東海村東海", "pref": "茨城県", "scale": 55},
                    {"addr": "常陸大宮市中富町", "pref": "茨城県", "scale": 55},
                    {"addr": "常陸大宮市野口", "pref": "茨城県", "scale": 55},
                    {"addr": "常陸大宮市山方", "pref": "茨城県", "scale": 55},
                    {"addr": "那珂市福田", "pref": "茨城県", "scale": 55},
                    {"addr": "城里町石塚", "pref": "茨城県", "scale": 55},
                    {"addr": "城里町阿波山", "pref": "茨城県", "scale": 55},
                    {"addr": "小美玉市小川", "pref": "茨城県", "scale": 55},
                    {"addr": "小美玉市堅倉", "pref": "茨城県", "scale": 55},
                    {"addr": "土浦市常名", "pref": "茨城県", "scale": 55},
                    {"addr": "土浦市下高津", "pref": "茨城県", "scale": 55},
                    {"addr": "石岡市柿岡", "pref": "茨城県", "scale": 55},
                    {"addr": "石岡市石岡", "pref": "茨城県", "scale": 55},
                    {"addr": "取手市井野", "pref": "茨城県", "scale": 55},
                    {"addr": "つくば市天王台", "pref": "茨城県", "scale": 55},
                    {"addr": "つくば市苅間", "pref": "茨城県", "scale": 55},
                    {"addr": "茨城鹿嶋市鉢形", "pref": "茨城県", "scale": 55},
                    {"addr": "茨城鹿嶋市宮中", "pref": "茨城県", "scale": 55},
                    {"addr": "潮来市辻", "pref": "茨城県", "scale": 55},
                    {"addr": "美浦村受領", "pref": "茨城県", "scale": 55},
                    {"addr": "坂東市山", "pref": "茨城県", "scale": 55},
                    {"addr": "稲敷市役所", "pref": "茨城県", "scale": 55},
                    {"addr": "稲敷市結佐", "pref": "茨城県", "scale": 55},
                    {"addr": "筑西市門井", "pref": "茨城県", "scale": 55},
                    {"addr": "かすみがうら市上土田", "pref": "茨城県", "scale": 55},
                    {"addr": "行方市麻生", "pref": "茨城県", "scale": 55},
                    {"addr": "行方市山田", "pref": "茨城県", "scale": 55},
                    {"addr": "行方市玉造", "pref": "茨城県", "scale": 55},
                    {"addr": "桜川市岩瀬", "pref": "茨城県", "scale": 55},
                    {"addr": "桜川市真壁", "pref": "茨城県", "scale": 55},
                    {"addr": "鉾田市鉾田", "pref": "茨城県", "scale": 55},
                    {"addr": "鉾田市造谷", "pref": "茨城県", "scale": 55},
                    {"addr": "鉾田市汲上", "pref": "茨城県", "scale": 55},
                    {"addr": "常総市石下", "pref": "茨城県", "scale": 55},
                    {"addr": "つくばみらい市加藤", "pref": "茨城県", "scale": 55},

                    {"addr": "大田原市本町", "pref": "栃木県", "scale": 55},
                    {"addr": "那須町寺子", "pref": "栃木県", "scale": 55},
                    {"addr": "那須塩原市鍋掛", "pref": "栃木県", "scale": 55},
                    {"addr": "那須塩原市あたご町", "pref": "栃木県", "scale": 55},
                    {"addr": "真岡市田町", "pref": "栃木県", "scale": 55},
                    {"addr": "真岡市荒町", "pref": "栃木県", "scale": 55},
                    {"addr": "芳賀町祖母井", "pref": "栃木県", "scale": 55},
                    {"addr": "那須烏山市中央", "pref": "栃木県", "scale": 55},
                    {"addr": "那須烏山市大金", "pref": "栃木県", "scale": 55},
                    {"addr": "栃木那珂川町馬頭", "pref": "栃木県", "scale": 55},
                    {"addr": "栃木那珂川町小川", "pref": "栃木県", "scale": 55},

                    {"addr": "桐生市元宿町", "pref": "群馬県", "scale": 55},

                    {"addr": "宮代町笠原", "pref": "埼玉県", "scale": 55},

                    {"addr": "成田市花崎", "pref": "千葉県", "scale": 55},
                    {"addr": "印西市大森", "pref": "千葉県", "scale": 55},
                    {"addr": "印西市笠神", "pref": "千葉県", "scale": 55}
                ]
            })
            play_quake_info_sequence("三陸沖", 7.9, 10, 70, ["栗原市築館"])
        
        self.add_log("【テスト】5秒後に地震情報を再生します...")
        threading.Thread(target=_run, daemon=True).start()
    
    def run_test_tsunami_info(self):
        def _run():
            time.sleep(5)
            # ウィンドウを表示
            self.signal_emitter.show_window_signal.emit()
            time.sleep(0.1)  # UIの更新を待つ
            
            self.add_log("【テスト】津波情報")
            
            # 通知を送信
            n = Notify()
            n.urgency = "critical"
            n.title = "大津波警報"
            n.message = "大津波警報が発表されました。今すぐに高台や河川から遠く離れた場所に逃げてください。"
            n.icon = "icons/tsunami.png"
            n.application_name = "ZundaQuake"
            n.send()
            
            mock_areas = [
                {"name": "岩手県", "grade": "MajorWarning", "firstHeight": {"arrivalTime": "津波到達中"}, "maxHeight": {"description": "巨大"}},
                {"name": "宮城県", "grade": "MajorWarning", "firstHeight": {"arrivalTime": "15:00"}, "maxHeight": {"description": "巨大"}},
                {"name": "福島県", "grade": "MajorWarning", "firstHeight": {"arrivalTime": "15:10"}, "maxHeight": {"description": "巨大"}},
                {"name": "千葉県九十九里・外房", "grade": "Warning", "firstHeight": {"arrivalTime": "15:20"}, "maxHeight": {"description": "高い"}},
                {"name": "伊豆諸島", "grade": "Warning", "firstHeight": {"arrivalTime": "15:20"}, "maxHeight": {"description": "高い"}},
                {"name": "北海道太平洋沿岸中部", "grade": "Warning", "firstHeight": {"arrivalTime": "15:30"}, "maxHeight": {"description": "高い"}},
                {"name": "青森県太平洋沿岸", "grade": "Warning", "firstHeight": {"arrivalTime": "15:30"}, "maxHeight": {"description": "高い"}},
                {"name": "茨城県", "grade": "Warning", "firstHeight": {"arrivalTime": "15:30"}, "maxHeight": {"description": "高い"}},
                {"name": "千葉県内房", "grade": "Watch", "firstHeight": {"arrivalTime": "15:20"}, "maxHeight": {"description": "-"}},
                {"name": "北海道太平洋沿岸東部", "grade": "Watch", "firstHeight": {"arrivalTime": "15:30"}, "maxHeight": {"description": "-"}},
                {"name": "相模湾・三浦半島", "grade": "Watch", "firstHeight": {"arrivalTime": "15:30"}, "maxHeight": {"description": "-"}},
                {"name": "静岡県", "grade": "Watch", "firstHeight": {"arrivalTime": "15:30"}, "maxHeight": {"description": "-"}},
                {"name": "北海道太平洋沿岸西部", "grade": "Watch", "firstHeight": {"arrivalTime": "15:40"}, "maxHeight": {"description": "-"}},
                {"name": "小笠原諸島", "grade": "Watch", "firstHeight": {"arrivalTime": "16:00"}, "maxHeight": {"description": "-"}},
                {"name": "三重県南部", "grade": "Watch", "firstHeight": {"arrivalTime": "16:00"}, "maxHeight": {"description": "-"}},
                {"name": "青森県日本海沿岸", "grade": "Watch", "firstHeight": {"arrivalTime": "16:10"}, "maxHeight": {"description": "-"}},
                {"name": "愛知県外海", "grade": "Watch", "firstHeight": {"arrivalTime": "16:10"}, "maxHeight": {"description": "-"}},
                {"name": "和歌山県", "grade": "Watch", "firstHeight": {"arrivalTime": "16:10"}, "maxHeight": {"description": "-"}},
                {"name": "高知県", "grade": "Watch", "firstHeight": {"arrivalTime": "16:30"}, "maxHeight": {"description": "-"}},
                {"name": "徳島県", "grade": "Watch", "firstHeight": {"arrivalTime": "16:40"}, "maxHeight": {"description": "-"}},
                {"name": "宮崎県", "grade": "Watch", "firstHeight": {"arrivalTime": "17:00"}, "maxHeight": {"description": "-"}},
                {"name": "種子島・屋久島地方", "grade": "Watch", "firstHeight": {"arrivalTime": "17:10"}, "maxHeight": {"description": "-"}},
                {"name": "奄美群島・トカラ列島", "grade": "Watch", "firstHeight": {"arrivalTime": "17:10"}, "maxHeight": {"description": "-"}},
                {"name": "北海道日本海沿岸南部", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "陸奥湾", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "東京湾内湾", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "伊勢・三河湾", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "大阪府", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "兵庫県瀬戸内海沿岸", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "淡路島南部", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "岡山県", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "香川県", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "愛媛県宇和海沿岸", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "大分県瀬戸内海沿岸", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "大分県豊後水道沿岸", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "長崎県西方", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "鹿児島県東部", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "鹿児島県西部", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "沖縄本島地方", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "宮古島・八重山地方", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "大東島地方", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}}
            ]
            
            # シグナル経由でUI更新
            self.signal_emitter.update_tsunami_info_signal.emit(mock_areas)
            parsed_mock_areas = []
            for a in mock_areas:
                fh = a.get("firstHeight", {})
                mh = a.get("maxHeight", {})
                arrival = fh.get("arrivalTime") or fh.get("condition") or "不明"
                height = mh.get("description") or (f"{mh.get('value')}m" if mh.get("value") else "不明")
                parsed_mock_areas.append({"name": a["name"], "grade": a["grade"], "arrival": arrival, "height": height})
            self.signal_emitter.update_tsunami_info_signal.emit(parsed_mock_areas)
            
            # 元の処理も実行
            mock_data = {
                "code": 552, "cancelled": False,
                "areas": [
                    {"name": "岩手県", "grade": "MajorWarning", "firstHeight": {"arrivalTime": "津波到達中"}, "maxHeight": {"description": "巨大"}},
                    {"name": "宮城県", "grade": "MajorWarning", "firstHeight": {"arrivalTime": "15:00"}, "maxHeight": {"description": "巨大"}},
                {"name": "福島県", "grade": "MajorWarning", "firstHeight": {"arrivalTime": "15:10"}, "maxHeight": {"description": "巨大"}},
                {"name": "千葉県九十九里・外房", "grade": "Warning", "firstHeight": {"arrivalTime": "15:20"}, "maxHeight": {"description": "高い"}},
                {"name": "伊豆諸島", "grade": "Warning", "firstHeight": {"arrivalTime": "15:20"}, "maxHeight": {"description": "高い"}},
                {"name": "北海道太平洋沿岸中部", "grade": "Warning", "firstHeight": {"arrivalTime": "15:30"}, "maxHeight": {"description": "高い"}},
                {"name": "青森県太平洋沿岸", "grade": "Warning", "firstHeight": {"arrivalTime": "15:30"}, "maxHeight": {"description": "高い"}},
                {"name": "茨城県", "grade": "Warning", "firstHeight": {"arrivalTime": "15:30"}, "maxHeight": {"description": "高い"}},
                {"name": "千葉県内房", "grade": "Watch", "firstHeight": {"arrivalTime": "15:20"}, "maxHeight": {"description": "-"}},
                {"name": "北海道太平洋沿岸東部", "grade": "Watch", "firstHeight": {"arrivalTime": "15:30"}, "maxHeight": {"description": "-"}},
                {"name": "相模湾・三浦半島", "grade": "Watch", "firstHeight": {"arrivalTime": "15:30"}, "maxHeight": {"description": "-"}},
                {"name": "静岡県", "grade": "Watch", "firstHeight": {"arrivalTime": "15:30"}, "maxHeight": {"description": "-"}},
                {"name": "北海道太平洋沿岸西部", "grade": "Watch", "firstHeight": {"arrivalTime": "15:40"}, "maxHeight": {"description": "-"}},
                {"name": "小笠原諸島", "grade": "Watch", "firstHeight": {"arrivalTime": "16:00"}, "maxHeight": {"description": "-"}},
                {"name": "三重県南部", "grade": "Watch", "firstHeight": {"arrivalTime": "16:00"}, "maxHeight": {"description": "-"}},
                {"name": "青森県日本海沿岸", "grade": "Watch", "firstHeight": {"arrivalTime": "16:10"}, "maxHeight": {"description": "-"}},
                {"name": "愛知県外海", "grade": "Watch", "firstHeight": {"arrivalTime": "16:10"}, "maxHeight": {"description": "-"}},
                {"name": "和歌山県", "grade": "Watch", "firstHeight": {"arrivalTime": "16:10"}, "maxHeight": {"description": "-"}},
                {"name": "高知県", "grade": "Watch", "firstHeight": {"arrivalTime": "16:30"}, "maxHeight": {"description": "-"}},
                {"name": "徳島県", "grade": "Watch", "firstHeight": {"arrivalTime": "16:40"}, "maxHeight": {"description": "-"}},
                {"name": "宮崎県", "grade": "Watch", "firstHeight": {"arrivalTime": "17:00"}, "maxHeight": {"description": "-"}},
                {"name": "種子島・屋久島地方", "grade": "Watch", "firstHeight": {"arrivalTime": "17:10"}, "maxHeight": {"description": "-"}},
                {"name": "奄美群島・トカラ列島", "grade": "Watch", "firstHeight": {"arrivalTime": "17:10"}, "maxHeight": {"description": "-"}},
                {"name": "北海道日本海沿岸南部", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "陸奥湾", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "東京湾内湾", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "伊勢・三河湾", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "大阪府", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "兵庫県瀬戸内海沿岸", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "淡路島南部", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "岡山県", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "香川県", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "愛媛県宇和海沿岸", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "大分県瀬戸内海沿岸", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "大分県豊後水道沿岸", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "長崎県西方", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "鹿児島県東部", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "鹿児島県西部", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "沖縄本島地方", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "宮古島・八重山地方", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}},
                {"name": "大東島地方", "grade": "Forecast", "firstHeight": {"condition": "--:--"}, "maxHeight": {"description": "0.2m未満"}}
            ]
            }
            process_p2p_data(
                mock_data, self.add_log, self.announce, 
                self.update_eew_map, self.update_tsunami_map
            )
        
        self.add_log("【テスト】5秒後に津波情報を再生します...")
        threading.Thread(target=_run, daemon=True).start()
    
    def init_data_fetch(self):
        global latest_p2p_ids, latest_id_wolfx, latest_serial_wolfx
        
        try:
            # P2P初期取得
            p2p_data = fetch_p2pquake()
            if p2p_data:
                for item in p2p_data:
                    code = item.get("code")
                    
                    # 555、561、9611はスキップ
                    if code in [555, 561, 9611]:
                        continue
                    
                    # 551、552、556の初期データを取得
                    if code in [551, 552, 556] and latest_p2p_ids.get(code) is None:
                        latest_p2p_ids[code] = item.get("id")
                        if code == 551:
                            process_p2p_eq(item, self.add_log, update_tsunami_info_func=None, is_silent=True)
                        else:
                            process_p2p_data(item, self.add_log, self.announce, 
                                           self.update_eew_map, self.update_tsunami_map, is_silent=True)
            
            # Wolfx初期取得
            wolfx_data = fetch_wolfx()
            if wolfx_data:
                latest_id_wolfx = wolfx_data.get("EventID")
                latest_serial_wolfx = wolfx_data.get("Serial")
                process_wolfx_data(wolfx_data, self.add_log, self.update_eew_map, is_silent=True)
            
            self.add_log("初期データ取得完了。監視を開始します。")
        except Exception as e:
            print(f"Error in init_data_fetch: {e}")
            traceback.print_exc()
            self.add_log(f"初期データ取得エラー: {e}")
    
    def start_websockets(self):
        try:
            def safe_add_log(text):
                self.signal_emitter.log_signal.emit(text)
            
            def safe_update_eew_map(areas):
                self.signal_emitter.update_eew_map_signal.emit(areas)
            
            def safe_update_tsunami_map(areas_data):
                self.signal_emitter.update_tsunami_map_signal.emit(areas_data)
            
            def safe_announce(sound_file, text, log_text=None):
                if log_text:
                    safe_add_log(log_text)
                threading.Thread(target=lambda: play_wav_sync(sound_file), daemon=True).start()
            
            def safe_update_tsunami_info(ui_areas):
                self.signal_emitter.update_tsunami_info_signal.emit(ui_areas)

            def on_p2p_ws_message(data):
                global latest_p2p_ids
                code = data.get("code")
                event_id = data.get("id")
                
                # 受信データ確認
                print(f"[P2P WS] Received: code={code}, id={event_id}")
                
                # 555、561、9611はスキップ
                if code in [555, 561, 9611]:
                    print(f"[P2P WS] Skipped: code={code} is in skip list")
                    return
                
                # 受信した事をログに記録
                safe_add_log(f"[P2P WS] 受信: code={code}, id={event_id}")
                
                # コードに応じて処理
                if code == 551:
                    print(f"[P2P WS] Processing 551 (地震情報)")
                    safe_add_log(f"[P2P WS] 地震情報を処理開始")
                    latest_p2p_ids[code] = event_id
                    
                    # データ処理
                    process_p2p_eq(data, safe_add_log, update_tsunami_info_func=safe_update_tsunami_info, is_silent=False)
                    
                    # UIにも表示
                    try:
                        issue = data.get("issue", {})
                        eq = data.get("earthquake", {})
                        hypo = eq.get("hypocenter", {})
                        points = data.get("points", [])
                        info_type = issue.get("type")
                        
                        time_str = eq.get("time", "不明")
                        name = hypo.get("name", "不明")
                        mag = hypo.get("magnitude", -1)
                        depth = hypo.get("depth", "不明")
                        max_scale = eq.get("maxScale", -1)
                        tsunami = eq.get("domesticTsunami", "None")
                        
                        # 津波情報
                        tsunami_text = ""
                        if tsunami == "None":
                            tsunami_text = "この地震による津波の心配はありません。"
                        elif tsunami == "Checking":
                            tsunami_text = "津波の有無は現在調査中です。"
                        elif tsunami == "NonEffective":
                            tsunami_text = "若干の海面変動があるかもしれませんが、被害の心配はありません。"
                        elif tsunami in ["Watch", "Advisory"]:
                            tsunami_text = "津波注意報が発表されています。"
                        elif tsunami == "Warning":
                            tsunami_text = "津波警報が発表されています。"
                        elif tsunami in ["Major", "MajorWarning"]:
                            tsunami_text = "大津波警報が発表されています。"
                        
                        # 観測地域
                        max_scale_areas = []
                        if points and max_scale > 0:
                            for point in points:
                                if point.get("scale") == max_scale and point.get("addr"):
                                    max_scale_areas.append(point.get("addr"))
                            max_scale_areas = list(dict.fromkeys(max_scale_areas))[:5]
                        
                        # 情報タイプに応じて表示
                        quake_type = "地震情報"
                        if info_type == "ScalePrompt":
                            quake_type = "震度速報"
                        elif info_type == "Destination":
                            quake_type = "震源情報"
                        elif info_type == "DetailScale":
                            quake_type = "地震情報"
                        
                        max_intensity_str = convert_intensity(max_scale) if max_scale > 0 else ""
                        
                        # UIを更新
                        self.signal_emitter.log_signal.emit(f"[UI更新] {quake_type}を表示")
                        
                        # シグナルでUI更新データを送信
                        ui_data = {
                            "quake_type": quake_type,
                            "time_str": time_str,
                            "name": name,
                            "mag": mag,
                            "depth": str(depth),
                            "max_intensity": max_intensity_str,
                            "tsunami_text": tsunami_text,
                            "areas": max_scale_areas,
                            "points": points
                        }
                        self.signal_emitter.update_quake_info_signal.emit(ui_data)
                        print(f"[551] Emitted update_quake_info_signal with data: {ui_data}")
                        
                    except Exception as e:
                        print(f"Error updating quake UI: {e}")
                        traceback.print_exc()
                    
                elif code == 552:
                    print(f"[P2P WS] Processing 552 (津波情報)")
                    safe_add_log(f"[P2P WS] 津波情報を処理開始")
                    latest_p2p_ids[code] = event_id
                    
                    # データ処理
                    process_p2p_data(data, safe_add_log, safe_announce, safe_update_eew_map, safe_update_tsunami_map, is_silent=False)
                    
                elif code == 554:
                    print(f"[P2P WS] Processing 554 (EEW発表検知)")
                    safe_add_log("緊急地震速報が発表されました")
                    
                elif code == 556:
                    print(f"[P2P WS] Processing 556 (EEW警報)")
                    safe_add_log(f"[P2P WS] EEW警報を処理開始")
                    latest_p2p_ids[code] = event_id
                    
                    # データ処理
                    process_p2p_data(data, safe_add_log, safe_announce, safe_update_eew_map, safe_update_tsunami_map, is_silent=False)
                    
                    # UIにも表示
                    try:
                        issue = data.get("issue", {})
                        earthquake = data.get("earthquake", {})
                        areas = data.get("areas", [])
                        
                        serial = int(issue.get("serial", 1))
                        hypo = earthquake.get("hypocenter", {})
                        name = hypo.get("name", "不明")
                        mag = hypo.get("magnitude", -1)
                        depth = hypo.get("depth", "不明")
                        
                        # 対象地域を抽出
                        raw_names = [a.get("name", "") for a in areas if a.get("name")]
                        target_areas = sorted(set(eew_areas_to_prefs(raw_names)))
                        
                        # タイトル
                        title = f"緊急地震速報(警報 第{serial}報)"
                        
                        # シグナルでUI更新
                        ui_data = {
                            "title": title,
                            "countdown": None,
                            "areas": target_areas,
                            "magnitude": mag,
                            "depth": str(depth) + "km" if depth != "不明" else depth,
                            "message": "対象地域では、周囲の状況に応じて、慌てずに、まず身の安全を確保してください。"
                        }
                        self.signal_emitter.update_eew_info_signal.emit(ui_data)
                        print(f"[556] Emitted update_eew_info_signal with title: {title}")
                    except Exception as e:
                        print(f"Error updating EEW UI: {e}")
                        traceback.print_exc()
                    
                else:
                    # その他のコードも受信して記録
                    print(f"[P2P WS] Received other code: {code}")
                    safe_add_log(f"[P2P WS] 未処理のコード受信: code={code}, id={event_id}")
            
            def on_wolfx_eew_ws_message(data):
                global latest_id_wolfx, latest_serial_wolfx
                event_id = data.get("EventID")
                serial = data.get("Serial")
                title = data.get("Title", "")
                
                print(f"[Wolfx WS] Received: EventID={event_id}, Serial={serial}, Title={title}")
                
                # Titleが空欄またはEventIDがNoneの場合は無視
                if not title or event_id is None:
                    print(f"[Wolfx WS] Skipped: empty title or None event_id")
                    return
                
                # 重複チェック
                if event_id == latest_id_wolfx and serial == latest_serial_wolfx:
                    print(f"[Wolfx WS] Skipped: duplicate event")
                    return  # 同じイベントの同じ報番は処理しない
                
                # グローバル変数の更新
                latest_id_wolfx = event_id
                latest_serial_wolfx = serial
                
                print(f"[Wolfx WS] Processing EEW...")
                
                # データ処理
                process_wolfx_data(data, safe_add_log, safe_update_eew_map, is_silent=False)
                
                # UIも更新
                try:
                    hypo_name = data.get("Hypocenter", "不明")
                    mag_raw = data.get("Magunitude", -1.0)
                    try:
                        if isinstance(mag_raw, str):
                            magnitude = float(mag_raw.replace("M", ""))
                        else:
                            magnitude = float(mag_raw)
                    except:
                        magnitude = -1.0
                    
                    depth_raw = data.get("Depth", "10")
                    depth_str = str(depth_raw).replace("km", "")
                    max_int_str = data.get("MaxIntensity", "不明")
                    max_scale_int = convert_wolfx_intensity(max_int_str)
                    is_warning = data.get("isWarn", False)
                    is_forecast = not is_warning
                    is_final = data.get("isFinal", False)
                    
                    # S波到達時間計算
                    s_wave_sec = None
                    # user_lat, user_lon = get_user_location()
                    # if user_lat is not None and user_lon is not None:
                    #     try:
                    #         ot_str = data.get("OriginTime")
                    #         ot_dt = datetime.strptime(ot_str, "%Y/%m/%d %H:%M:%S")
                    #         depth = float(depth_str) if depth_str.replace(".", "").isdigit() else 10.0
                    #         lat = data.get("Latitude", 0.0)
                    #         lon = data.get("Longitude", 0.0)
                    #         s_wave_sec = get_remaining_seconds(ot_dt, lat, lon, depth, user_lat, user_lon, "s_wave")
                    #     except:
                    #         pass
                    
                    # 警報の場合は対象地域を取得
                    target_areas_list = []
                    if not is_forecast:
                        areas_data = data.get("Areas", [])
                        for area in areas_data:
                            area_name = area.get("Name", "")
                            if area_name:
                                target_areas_list.append(area_name)
                    
                    # シグナルでUI更新
                    ui_data = {
                        "is_forecast": is_forecast,
                        "epicenter": hypo_name,
                        "magnitude": magnitude,
                        "depth": depth_str,
                        "max_intensity_str": max_int_str,
                        "max_intensity_value": max_scale_int,
                        "countdown": int(s_wave_sec) if s_wave_sec and s_wave_sec > 0 else None,
                        "areas": target_areas_list if target_areas_list else None,
                        "serial": serial,
                        "is_final": is_final
                    }
                    self.signal_emitter.update_eew_info_signal.emit(ui_data)
                    print(f"[Wolfx] Emitted update_eew_info_signal: forecast={is_forecast}, intensity={max_int_str}")
                except Exception as e:
                    print(f"Error updating Wolfx EEW UI: {e}")
                    traceback.print_exc()
            
            # WebSocket接続
            self.add_log("WebSocket接続を開始しています...")
            connect_p2pquake_ws(on_p2p_ws_message)
            self.add_log("P2PQuake WebSocket接続完了")
            connect_wolfx_eew_ws(on_wolfx_eew_ws_message)
            self.add_log("Wolfx WebSocket接続完了")
            
        except Exception as e:
            print(f"Error in start_websockets: {e}")
            traceback.print_exc()
            self.add_log(f"WebSocket接続エラー: {e}")

if __name__ == "__main__":
    try:
        print("Starting application...")
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon(os.path.join('icons', 'icon_2048x.png')))
        print("QApplication created")

        # 多重起動チェック
        socket = QLocalSocket()
        socket.connectToServer("ZundaQuake")

        # 既に起動している場合
        if socket.waitForConnected(500):
            print("Already running, showing existing window")
            socket.write(b"SHOW")
            socket.waitForBytesWritten(500)
            socket.disconnectFromServer()
            sys.exit(0)

        # 起動していない場合、自分がメインになる
        print("Creating main window...")
        window = MainWindow()
        print("MainWindow created")
        
        window.show()
        print("Window shown - startup complete")
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)