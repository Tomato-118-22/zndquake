import os
import time
import pygame
import threading
import queue
import json

_mixer_initialized = False
_city_map_loaded = False

# 初回読み込み時にミキサーを初期化
def _ensure_mixer_initialized():
    global _mixer_initialized
    if not _mixer_initialized:
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
            pygame.mixer.set_num_channels(32)
            _mixer_initialized = True
            print("[Audio] Mixer initialized")
        except pygame.error as e:
            print(f"Audio init failed: {e}")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")

# 音声再生管理
class AudioPlaybackManager:
    def __init__(self):
        self.current_channel = None
        self.is_playing = False
        self.lock = threading.Lock()
        self.sequence_active = False
        self.is_tsunami = False  # 津波再生中フラグ

    def can_play(self):
        return True

    def start_sequence(self, is_tsunami: bool = False):
        with self.lock:
            if self.is_playing:
                # 津波再生中は中断しない
                if self.is_tsunami:
                    print(f"[Audio] Blocked interruption: tsunami is playing")
                    return False
                # 津波以外の再生中は中断して新しい音声へ
                print(f"[Audio] Interrupting current playback")
                self.sequence_active = False
                pygame.mixer.stop()

            self.is_playing = True
            self.sequence_active = True
            self.is_tsunami = is_tsunami
            print(f"[Audio] Starting new sequence (tsunami={is_tsunami})")
            return True

    def end_sequence(self):
        with self.lock:
            self.is_playing = False
            self.sequence_active = False
            self.is_tsunami = False
            self.current_channel = None
            print(f"[Audio] Sequence ended")
    
    def set_channel(self, channel):
        with self.lock:
            self.current_channel = channel
    
    def is_sequence_active(self):
        with self.lock:
            return self.sequence_active
    
    def should_play_eew_forecast(self, event_id):
        # EEW予報は第一報のみを再生
        with self.lock:
            if event_id in self.eew_forecast_events:
                print(f"[Audio] Skipping EEW forecast (already played): {event_id}")
                return False
            self.eew_forecast_events.add(event_id)
            return True
    
    def should_play_eew_warning(self, event_id, new_areas):
        # EEW警報は対象地域の拡大時のみ再生
        with self.lock:
            if event_id not in self.eew_warning_areas:
                # 第一報
                self.eew_warning_areas[event_id] = set(new_areas)
                return True
            
            # 既存の対象地域を取得
            existing_areas = self.eew_warning_areas[event_id]
            new_areas_set = set(new_areas)
            
            # 新しい地域が追加されたか確認
            added_areas = new_areas_set - existing_areas
            if added_areas:
                print(f"[Audio] EEW warning areas expanded: +{added_areas}")
                self.eew_warning_areas[event_id] = new_areas_set
                return True
            
            print(f"[Audio] Skipping EEW warning (no new areas): {event_id}")
            return False
    
    def clear_eew_event(self, event_id):
        with self.lock:
            self.eew_forecast_events.discard(event_id)
            self.eew_warning_areas.pop(event_id, None)

# グローバルインスタンス
audio_manager = AudioPlaybackManager()

# 市町村名→地域名JSON初期化
CITY_TO_REGION_MAP = {}

def load_city_to_region_map():
    # 市町村名→地域名JSON読み込み
    global CITY_TO_REGION_MAP
    json_path = os.path.join(BASE_DIR, "datas", "city_to_region.json")
    
    try:
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                CITY_TO_REGION_MAP = json.load(f)
            print(f"Loaded city_to_region.json: {len(CITY_TO_REGION_MAP)} entries")
        else:
            error_message = (f"city_to_region.json not found at {json_path}")
            print(f"ERROR: {error_message}")
            QMessageBox.information(None, "ZundaQuake", 
                f"起動に必要なファイルが見つかりませんでした。\n{error_message}")
            exit()
    except Exception as e:
        print(f"Error loading city_to_region.json: {e}")
        CITY_TO_REGION_MAP = {}

# 初回ロード
load_city_to_region_map()

def convert_city_to_region(city_name: str) -> str:
    # 部分一致
    for city_key, region_name in CITY_TO_REGION_MAP.items():
        if city_name.startswith(city_key):
            return region_name
    
    # 見つからない場合
    return city_name

def convert_city_list_to_regions(city_names: list[str]) -> list[str]:
    # 重複チェック
    regions = []
    seen = set()
    
    for city in city_names:
        region = convert_city_to_region(city)
        if region not in seen:
            regions.append(region)
            seen.add(region)
    
    return regions

# Quake_XXX.wav
BROAD_REGION_MAP = {
    # 北海道地方
    "北海道": "001", "十勝": "001", "根室": "001", "釧路": "001", 
    "石狩": "001", "日高": "001", "渡島": "001", "胆振": "001", 
    "宗谷": "001", "網走": "001", "紋別": "001", "留萌": "001",
    "後志": "001", "空知": "001", "上川": "001", "檜山": "001",
    "千島列島": "001", "択捉": "001", "国後": "001", "色丹": "001",

    # 東北地方
    "青森": "002", "岩手": "002", "宮城": "002", "秋田": "002", 
    "山形": "002", "福島": "002", "三陸": "002", "陸奥湾": "002",

    # 関東地方
    "茨城": "003", "栃木": "003", "群馬": "003", "埼玉": "003", 
    "千葉": "003", "東京": "003", "神奈川": "003", 
    "房総": "003", "相模湾": "003", "東京湾": "003", 
    "伊豆大島": "003", "新島": "003", "神津島": "003", "三宅島": "003", "八丈島": "003",

    # 北陸･甲信越地方
    "新潟": "004", "富山": "004", "石川": "004", "福井": "004", 
    "佐渡": "004", "能登": "004", "若狭湾": "004",
    "山梨": "005", "長野": "005", 

    # 東海地方
    "岐阜": "006", "静岡": "006", "愛知": "006", "三重": "006", 
    "伊豆半島": "006", "駿河湾": "006", "遠州灘": "006", "三河湾": "006", "伊勢湾": "006",

    # 近畿地方
    "滋賀": "007", "京都": "007", "大阪": "007", "兵庫": "007",
    "奈良": "007", "和歌山": "007", "淡路島": "007", "紀伊水道": "007",

    # 中国地方
    "鳥取": "008", "島根": "008", "岡山": "008", "広島": "008", "山口": "008",

    # 四国地方
    "徳島": "009", "香川": "009", "愛媛": "009", "高知": "009", 
    "瀬戸内海": "008",
    "伊予灘": "009", "土佐湾": "009", "豊後水道": "009",

    # 九州地方
    "福岡": "010", "佐賀": "010", "長崎": "010", "熊本": "010", 
    "大分": "010", "宮崎": "010", "鹿児島": "010", 
    "日向灘": "010", "有明海": "010", "天草": "010", 
    "種子島": "010", "屋久島": "010", "奄美": "010",

    # 沖縄地方
    "沖縄": "011", "宮古": "011", "石垣": "011", "西表": "011", 
    "与那国": "011", "八重山": "011", "台湾": "011", "フィリピン": "011" # 台湾は沖縄扱い
}

# QuakeInfo_XXX.wav
FORECAST_REGION_MAP = {
    # 北海道
    "北海道": "002", "十勝": "002", "根室": "002", "釧路": "002", "石狩": "002", "日高": "002",
    "渡島": "002", "胆振": "002", "宗谷": "002", "網走": "002", "紋別": "002", "留萌": "002",
    "後志": "002", "空知": "002", "上川": "002", "檜山": "002", "千島": "002", "択捉": "002", "国後": "002",
    "苫小牧": "002", "内浦": "002", "浦河": "002", "桧山": "002", "オホーツク": "002", "日本海北部": "002", "津軽海峡": "002",
    # 北海道? 
    "サハリン西方沖": "002", "サハリン南部付近": "002", "シベリア": "002", "ウラジオストク": "002", 
    # 東北
    "青森": "003", "岩手": "003", "宮城": "003", "秋田": "003", "山形": "003", "福島": "003", "三陸": "003", "陸奥": "003",
    # 関東
    "茨城": "004", "栃木": "004", "群馬": "004", "埼玉": "004", "千葉": "004", "東京": "004", "神奈川": "004",
    "房総": "004", "相模": "004", "伊豆大島": "004", "新島": "004", "三宅": "004", "八丈": "004", "関東": "004", 
    "父島": "004", "鳥島": "004", "小笠原": "004", "硫黄島": "004", "父島": "004", "北西太平洋": "004", "マリアナ": "004", 
    # 北陸
    "新潟": "005", "富山": "005", "石川": "005", "福井": "005", "佐渡": "005", "能登": "005", "日本海中部": "005",
    # 甲信･東海
    "山梨": "006", "長野": "006", "岐阜": "007", "静岡": "007", "愛知": "007", "三重": "007", 
    "伊豆半島": "007", "駿河": "007", "遠州": "007", "伊豆半島東方沖": "007", "伊勢": "007", "三河": "007", "東海道": "007",
    # 近畿
    "滋賀": "008", "京都": "008", "大阪": "008", "兵庫": "008", "奈良": "008", "和歌山": "008", "淡路": "008", "紀伊": "008", "播磨": "008",
    # 中国
    "鳥取": "009", "島根": "009", "岡山": "009", "広島": "009", "山口": "009", "安芸": "009", "周防": "009", "隠岐": "009", "日本海西部": "009", 
    # 四国
    "徳島": "010", "香川": "010", "愛媛": "010", "高知": "010", "伊予": "010", "土佐": "010", "西海道": "010", "瀬戸内海": "010",
    # 九州
    "福岡": "011", "佐賀": "011", "長崎": "011", "熊本": "011", "大分": "011", "宮崎": "011", "鹿児島": "011",
    "日向": "011", "有明": "011", "天草": "011", "種子": "011", "屋久": "011", "奄美": "011", "豊後": "011",
    "九州": "011", "薩摩": "011", "五島": "011", "対馬": "011", "大隅": "011", "薩南": "011", "トカラ": "011", 
    "朝鮮": "011", "黄海": "011", "中国東北部": "011", 
    # 沖縄
    "沖縄": "012", "宮古": "012", "石垣": "012", "西表": "012", "与那国": "012", "中国東部": "011", 
    "八重山": "012", "大東": "012", "東シナ海": "012", "台湾": "012", "フィリピン": "012"
    # 海外
    # 今はなし
}

REGION_NAME_TO_ID = {
    # 北海道地方
    "石狩地方北部": "001", "石狩地方中部": "002", "石狩地方南部": "003", "後志地方北部": "004", 
    "後志地方東部": "005", "後志地方西部": "006", "空知地方北部": "007", "空知地方中部": "008", 
    "空知地方南部": "009", "渡島地方北部": "010", "渡島地方東部": "011", "渡島地方西部": "012", 
    "檜山地方": "013", "奥尻島": "014", "胆振地方西部": "015", "胆振地方中東部": "016", 
    "日高地方西部": "017", "日高地方中部": "018", "日高地方東部": "019", "上川地方北部": "020", 
    "上川地方中部": "021", "上川地方南部": "022", "留萌地方中北部": "023", "留萌地方南部": "024", 
    "宗谷地方北部": "025", "宗谷地方南部": "026", "利尻礼文": "027", "網走地方": "028", 
    "北見地方": "029", "紋別地方": "030", "十勝地方北部": "031", "十勝地方中部": "032", 
    "十勝地方南部": "033", "釧路地方北部": "034", "釧路地方中南部": "035", "根室地方北部": "036", 
    "根室地方中部": "037", "根室地方南部": "038", "北海道利尻礼文": "188",
    
    # 東北地方
    "青森県津軽北部": "039", "青森県津軽南部": "040", "青森県三八上北": "041", "青森県下北": "042", 
    "岩手県沿岸北部": "043", "岩手県沿岸南部": "044", "岩手県内陸北部": "045", "岩手県内陸南部": "046", 
    "宮城県北部": "047", "宮城県中部": "048", "宮城県南部": "049", "秋田県沿岸北部": "050", 
    "秋田県沿岸南部": "051", "秋田県内陸北部": "052", "秋田県内陸南部": "053", "山形県庄内": "054", 
    "山形県最上": "055", "山形県村山": "056", "山形県置賜": "057", "福島県中通り": "058", 
    "福島県浜通り": "059", "福島県会津": "060", 

    # 関東地方
    "茨城県北部": "061", "茨城県南部": "062", "栃木県北部": "063", "栃木県南部": "064", 
    "群馬県北部": "065", "群馬県南部": "066", "埼玉県北部": "067", "埼玉県南部": "068", 
    "埼玉県秩父": "069", "千葉県北東部": "070", "千葉県北西部": "071", "千葉県南部": "072", 
    "東京都23区": "073", "東京都多摩東部": "074", "東京都多摩西部": "075", "東京都伊豆大島": "076", 
    "東京都新島": "077", "東京都神津島": "078", "東京都三宅島": "079", "東京都八丈島": "080", 
    "東京都小笠原": "081", "神奈川県東部": "082", "神奈川県西部": "083", 

    # 北陸地方
    "新潟県上越": "084", "新潟県中越": "085", "新潟県下越": "086", "新潟県佐渡": "087", 
    "富山県東部": "088", "富山県西部": "089", "石川県能登": "090", "石川県加賀": "091", 
    "福井県嶺北": "092", "福井県嶺南": "093", 

    # 甲信地方
    "山梨県東部・富士五湖": "094", "山梨県中西部": "095", "長野県北部": "096", "長野県中部": "097", "長野県南部": "098", 

    # 東海地方
    "岐阜県飛騨": "099", "岐阜県美濃東部": "100", "岐阜県美濃中西部": "101", "静岡県伊豆": "102", 
    "静岡県東部": "103", "静岡県中部": "104", "静岡県南部": "105", "愛知県東部": "106", 
    "愛知県西部": "107", 

    # 近畿地方
    "三重県北部": "108", "三重県中部": "109", "三重県南部": "110", "滋賀県北部": "111", 
    "滋賀県南部": "112", "京都府北部": "113", "京都府南部": "114", "大阪府北部": "115", 
    "大阪府南部": "116", "兵庫県北部": "117", "兵庫県南部": "118", "兵庫県淡路島": "119", 
    "奈良県": "120", "和歌山県北部": "121", "和歌山県南部": "122", 

    # 中国地方
    "鳥取県北部": "123", "鳥取県中部": "124", "鳥取県南部": "125", "島根県東部": "126", 
    "島根県西部": "127", "島根県隠岐": "128", "岡山県北部": "129", "岡山県南部": "130", 
    "広島県北部": "131", "広島県南東部": "132", "広島県南西部": "133", "山口県北部": "134", 
    "山口県東部": "135", "山口県中部": "136", "山口県西部": "137", 

    # 四国地方
    "徳島県北部": "138", "徳島県南部": "139", "香川県東部": "140", "香川県西部": "141", 
    "愛媛県東予": "142", "愛媛県中予": "143", "愛媛県南予": "144", "高知県東部": "145", 
    "高知県中部": "146", "高知県西部": "147", 

    # 九州地方
    "福岡県福岡": "148", "福岡県北九州": "149", "福岡県筑豊": "150", "福岡県筑後": "151", 
    "佐賀県北部": "152", "佐賀県南部": "153", "長崎県北部": "154", "長崎県南部": "155", 
    "長崎県島原半島": "156", "長崎県対馬": "157", "長崎県壱岐": "158", "長崎県五島": "159", 
    "熊本県阿蘇": "160", "熊本県熊本": "161", "熊本県球磨": "162", "熊本県天草・芦北": "163", 
    "大分県北部": "164", "大分県中部": "165", "大分県南部": "166", "大分県西部": "167", 
    "宮崎県北部平野部": "168", "宮崎県北部山沿い": "169", "宮崎県南部平野部": "170", "宮崎県南部山沿い": "171", 
    "鹿児島県薩摩": "172", "鹿児島県大隅": "173", "鹿児島県十島村": "174", "鹿児島県甑島": "175", 
    "鹿児島県種子島": "176", "鹿児島県屋久島": "177", "鹿児島県奄美北部": "178", "鹿児島県奄美南部": "179", 

    # 沖縄地方
    "沖縄県本島北部": "180", "沖縄県本島中南部": "181", "沖縄県久米島": "182", "沖縄県大東島": "183", 
    "沖縄県宮古島": "184", "沖縄県石垣島": "185", "沖縄県与那国島": "186", "沖縄県西表島": "187"
    }

EEW_AREA_TO_VOICE = {
    "北海道道北": 2, "北海道道央": 3, "北海道道南": 4, "北海道道東": 5,
    "北海道": 6, "青森": 7, "秋田": 8, "岩手": 9, "宮城": 10,
    "山形": 11, "福島": 12, "東北地方": 13, "茨城": 14, "栃木": 15,
    "群馬": 16, "埼玉": 17, "東京都": 18, "千葉": 19, "神奈川": 20,
    "関東地方": 21, "伊豆諸島": 22, "小笠原": 23, "新潟": 24, "富山": 25,
    "石川": 26, "福井": 27, "北陸地方": 28, "長野": 29, "山梨": 30,
    "甲信地方": 31, "岐阜": 32, "静岡": 33, "愛知": 34, "三重": 35,
    "東海地方": 36, "兵庫": 37, "京都府": 38, "滋賀": 39, "大阪府": 40,
    "奈良": 41, "和歌山": 42, "近畿地方": 43, "鳥取": 44, "島根": 45,
    "岡山": 46, "広島": 47, "山口": 48, "中国地方": 49, "香川": 50,
    "愛媛": 51, "徳島": 52, "高知": 53, "四国地方": 54, "福岡": 55,
    "大分": 56, "佐賀": 57, "長崎": 58, "熊本": 59, "宮崎": 60,
    "鹿児島": 61, "奄美群島": 62, "九州地方": 63, "沖縄本土": 64,
    "大東島": 65, "宮古島": 66, "八重山": 67, "沖縄": 68
}

TSUNAMI_REGION_TO_ID = {
    # 北海道
    "オホーツク海沿岸": "001", "北海道太平洋沿岸東部": "002", "北海道太平洋沿岸中部": "003", "北海道太平洋沿岸西部": "004", 
    "北海道日本海沿岸北部": "005", "北海道日本海沿岸南部": "006", 

    # 東北地方
    "陸奥湾": "007", "青森県太平洋沿岸": "008", "青森県日本海沿岸": "009", "岩手県": "010", 
    "宮城県": "011", "福島県": "012", "秋田県": "013", "山形県": "014",

    # 関東地方
    "茨城県": "015", "千葉県九十九里・外房": "016", "千葉県内房": "017", "東京湾内湾": "018", 
    "伊豆諸島": "019", "小笠原諸島": "020", "相模湾・三浦半島": "021",

    # 甲信地方は海なし県

    # 東海地方
    "静岡県": "022", "愛知県外海": "023", "伊勢・三河湾": "024", "三重県南部": "025",

    #北陸地方
    "新潟県上中下越": "026", "佐渡": "027", "富山県": "028", "石川県能登": "029", 
    "石川県加賀": "030", "福井県": "031",

    # 近畿地方
    "京都府": "032", "兵庫県北部": "033", 
    #"兵庫県南部": "034", 兵庫県南部は存在しない
    "兵庫県瀬戸内海沿岸": "035", "淡路島南部": "036", "大阪府": "037", "和歌山県": "038",

    # 中国地方
    "鳥取県": "039", "島根県出雲・石見": "040", "隠岐": "041", "岡山県": "042", 
    "広島県": "043", "山口県瀬戸内海沿岸": "049", "山口県日本海沿岸": "050",

    # 四国地方
    "香川県": "044", "愛媛県瀬戸内海沿岸": "045", "愛媛県宇和海沿岸": "046", "徳島県": "047", 
    "高知県": "048",

    # 九州地方
    "福岡県瀬戸内海沿岸": "051", "福岡県日本海沿岸": "052", "佐賀県北部": "053", "長崎県西方": "054", 
    "壱岐・対馬": "055", "有明・八代海": "056", "熊本県天草灘沿岸": "057", "大分県瀬戸内海沿岸": "058", 
    "大分県豊後水道沿岸": "059", "宮崎県": "060", "鹿児島県東部": "061", "鹿児島県西部": "062", 
    "種子島・屋久島地方": "063", "奄美群島・トカラ列島": "064",

    # 沖縄地方 
    "沖縄本島地方": "065", "宮古島・八重山地方": "066", "大東島地方": "067"
}

# 音声再生キュー
_audio_queue = queue.Queue()

def _audio_worker():
    # 音声再生専用スレッドの設定
    while True:
        func, args = _audio_queue.get()
        try:
            func(*args)
        except Exception as e:
            print(f"Audio worker error: {e}")
        finally:
            _audio_queue.task_done()

# 再生スレッド起動
_audio_thread = threading.Thread(target=_audio_worker, daemon=True)
_audio_thread.start()

def _enqueue_play(func, *args, is_tsunami: bool = False):
    with audio_manager.lock:
        if audio_manager.is_playing:
            if audio_manager.is_tsunami and not is_tsunami:
                # 津波再生中は津波以外をDrop
                print(f"[Audio] Dropped (tsunami is playing): {func.__name__}")
                return
            elif audio_manager.is_tsunami and is_tsunami:
                # 津波→津波はキューに積むだけ、再生中は一切触らない
                print(f"[Audio] Queuing next tsunami (current tsunami still playing)")
                _audio_queue.put((func, args))
                return
            else:
                # 通常再生中は即座に停止してリセット
                print(f"[Audio] Interrupting current playback")
                audio_manager.sequence_active = False
                pygame.mixer.stop()
                audio_manager.is_playing = False
                audio_manager.sequence_active = False

    # キューに残っている古いタスクをすべて破棄
    while not _audio_queue.empty():
        try:
            _audio_queue.get_nowait()
            _audio_queue.task_done()
        except queue.Empty:
            break

    _audio_queue.put((func, args))

def play_wav_sync(filename: str):
    # ミキサー初期化
    _ensure_mixer_initialized()
    # シーケンスがアクティブでない場合はスキップ
    if not audio_manager.is_sequence_active():
        print(f"[Audio] Skipping {filename} (no active sequence)")
        return
    
    path = os.path.join(SOUNDS_DIR, filename)
    if not os.path.exists(path):
        print(f"Sound skip (not found): {path}")
        return

    try:
        sound = pygame.mixer.Sound(path)
        channel = pygame.mixer.find_channel(True)
        audio_manager.set_channel(channel)
        channel.play(sound)
        
        while channel.get_busy():
            # シーケンスが中断されたかチェック
            if not audio_manager.is_sequence_active():
                print(f"[Audio] Sequence interrupted, stopping {filename}")
                channel.stop()
                break
            time.sleep(0.01)

    except Exception as e:
        print(f"Error playing sound {filename}: {e}")


def play_eew_sequence(area_names: list[str], is_zokuho: bool = False, event_id=None):
    # 対象地域拡大チェック
    if event_id and not audio_manager.should_play_eew_warning(event_id, area_names):
        print(f"[Audio] Skipping EEW warning (no area expansion)")
        return
    
    _enqueue_play(_play_eew_sequence_impl, area_names, is_zokuho)

def _play_eew_sequence_impl(area_names, is_zokuho):
    print(f"Playing EEW sequence for :{area_names}")

    # シーケンス開始
    audio_manager.start_sequence()
    
    try:
        play_wav_sync("EEW_alert.wav")
        time.sleep(0.5)
        for i in range(2):
            if is_zokuho:
                play_wav_sync("EEW_001_zokuho.wav")
            else:
                play_wav_sync("EEW_001.wav")
            time.sleep(0.2)
            played_nums = set()
            for area in area_names:
                num = EEW_AREA_TO_VOICE.get(area)
                if num and num not in played_nums:
                    play_wav_sync(f"EEW_{num:03}.wav")
                    played_nums.add(num)
                    time.sleep(0.1)
        play_wav_sync("EEW_099.wav")
    finally:
        # シーケンス終了
        audio_manager.end_sequence()


def get_broad_region_id(hypo_name: str):
    for keyword, region_id in BROAD_REGION_MAP.items():
        if keyword in hypo_name: return region_id
    return None

def get_forecast_region_id(hypo_name: str):
    for keyword, region_id in FORECAST_REGION_MAP.items():
        if keyword in hypo_name: return region_id
    return None

def play_eew_forecast_sequence(hypo_name: str, magnitude: float, max_scale_int: int, event_id=None):
    # 第一報チェック
    if event_id and not audio_manager.should_play_eew_forecast(event_id):
        print(f"[Audio] Skipping EEW forecast (not first report)")
        return
    
    _enqueue_play(_play_eew_forecast_sequence_impl, hypo_name, magnitude, max_scale_int)

def _play_eew_forecast_sequence_impl(hypo_name, magnitude, max_scale_int):
    print(f"Playing EEW Forecast: {hypo_name}, M{magnitude}, Scale{max_scale_int}")
    
    # シーケンス開始
    audio_manager.start_sequence()
    
    try:
        play_wav_sync("EEW_yoho.wav")
        time.sleep(0.5)
        play_wav_sync("QuakeInfo_001.wav")
        time.sleep(0.2)
        region_id = get_forecast_region_id(hypo_name)
        if region_id: play_wav_sync(f"QuakeInfo_{region_id}.wav")
        play_wav_sync("QuakeMagnitude.wav")
        if magnitude != -1.0:
            play_wav_sync(f"QuakeMagnitude_{magnitude:.1f}.wav")
        else:
            play_wav_sync("Magnitude_Unknown.wav")
        # 予想最大震度を追加
        play_wav_sync("ExpectedShindo.wav")
        if max_scale_int > 0:
            play_wav_sync(f"ExpectedShindo_{max_scale_int}.wav")
        else:
            play_wav_sync("ExpectedShindo_Unknown.wav")
    finally:
        # シーケンス終了
        audio_manager.end_sequence()

# ========================================
# 将来的に使用する可能性がある為変更しないでください。
# ========================================

# def play_eew_update_sequence(hypo_name: str, magnitude: float, max_scale_int: int):
#     _enqueue_play(_play_eew_update_sequence_impl, hypo_name, magnitude, max_scale_int)

# def _play_eew_update_sequence_impl(hypo_name, magnitude, max_scale_int):
#     print(f"Playing EEW Update: {hypo_name}")
#     play_wav_sync("EEW_yoho.wav")
#     time.sleep(0.5)
#     play_wav_sync("QuakeInfo_001.wav") # 続報扱い
#     time.sleep(0.2)
#     region_id = get_forecast_region_id(hypo_name)
#     if region_id: play_wav_sync(f"QuakeInfo_{region_id}.wav")
#     play_wav_sync("QuakeMagnitude.wav")
#     if magnitude != -1.0:
#         play_wav_sync(f"QuakeMagnitude_{magnitude:.1f}.wav")
#     else:
#         play_wav_sync("Magnitude_Unknown.wav")
#     play_wav_sync("ExpectedShindo.wav")
#     if max_scale_int > 0:
#         play_wav_sync(f"ExpectedShindo_{max_scale_int}.wav")
#     else:
#         play_wav_sync("ExpectedShindo_Unknown.wav")

# ========================================

def play_eew_cancel_sequence():
    _enqueue_play(play_wav_sync, "EEW_cancel.wav")

def play_shindo_sokuho_sequence(max_scale_int: int, region_names: list[str]):
    _enqueue_play(_play_shindo_sokuho_sequence_impl, max_scale_int, region_names)

def _play_shindo_sokuho_sequence_impl(max_scale_int, region_names):
    print(f"Playing Shindo Sokuho: Scale {max_scale_int}, Regions: {region_names}")
    
    # シーケンス開始
    audio_manager.start_sequence()
    
    try:
        # 市町村名を地域名に変換
        converted_regions = convert_city_list_to_regions(region_names)
        print(f"Converted regions: {converted_regions}")
        
        play_wav_sync("quake_info.wav")
        time.sleep(0.5)
        play_wav_sync("ShindoInfo_001.wav")
        time.sleep(0.2)
        play_wav_sync(f"ShindoInfo_shindo{max_scale_int}.wav")
        count = 0
        for region in converted_regions:
            region_id = REGION_NAME_TO_ID.get(region)
            if region_id:
                play_wav_sync(f"ShindoRegion_{region_id}.wav")
                count += 1
                if count >= 5: break
        play_wav_sync("ShindoInfo_002.wav")
    finally:
        audio_manager.end_sequence()


def play_destination_sequence(hypo_name: str, tsunami_id: str):
    _enqueue_play(_play_destination_sequence_impl, hypo_name, tsunami_id)

def _play_destination_sequence_impl(hypo_name, tsunami_id):
    print(f"Playing Destination Info: {hypo_name}")
    
    # シーケンス開始
    audio_manager.start_sequence()
    
    try:
        play_wav_sync("quake_info.wav")
        time.sleep(0.5)
        hypo_id = get_broad_region_id(hypo_name)
        if hypo_id: play_wav_sync(f"Quake_{hypo_id}.wav")
        play_wav_sync(f"WorryTsunami_{tsunami_id}.wav")
        play_wav_sync("QuakeHypocentre.wav")
    finally:
        audio_manager.end_sequence()


def play_quake_info_sequence(hypo_name: str, magnitude: float, depth: float, max_scale_int: int, max_scale_regions: list[str]):
    _enqueue_play(_play_quake_info_sequence_impl, hypo_name, magnitude, depth, max_scale_int, max_scale_regions)

def _play_quake_info_sequence_impl(hypo_name, magnitude, depth, max_scale_int, max_scale_regions):
    print(f"Playing Quake Info: {hypo_name}, Regions: {max_scale_regions}")
    
    # シーケンス開始
    audio_manager.start_sequence()
    
    try:
        # 市町村名を地域名に変換
        converted_regions = convert_city_list_to_regions(max_scale_regions)
        print(f"Converted regions: {converted_regions}")
        
        play_wav_sync("quake_info.wav")
        time.sleep(0.5)
        hypo_id = get_broad_region_id(hypo_name)
        if hypo_id: play_wav_sync(f"Quake_{hypo_id}.wav")
        play_wav_sync("QuakeMagnitude_001.wav")
        if magnitude != -1.0:
            play_wav_sync(f"QuakeMagnitude_{magnitude:.1f}.wav")
        else:
            play_wav_sync(f"QuakeMagnitude_Unknown.wav")
        play_wav_sync("QuakeDepth.wav")
        if depth == -1.0:
            # 深さ不明の場合
            play_wav_sync(f"QuakeMagnitude_Unknown.wav")
        elif depth >= 0 and depth <= 100:
            # 0～100kmの場合
            play_wav_sync(f"QuakeDepth_{int(depth)}km.wav")
        elif depth == 200 or depth == 300 or depth == 400 or depth == 500 or depth == 600 or depth == 700:
            # 〇00kmの場合
            play_wav_sync(f"QuakeDepth_{int(depth)}km.wav")
        elif depth > 100 and depth < 200:
            # 101～199kmの場合
            hundreds = 100
            remainder = int(depth) - hundreds
            play_wav_sync(f"QuakeDepth_over{hundreds}.wav")
            if remainder > 0:
                play_wav_sync(f"QuakeDepth_{remainder}km.wav")
        elif depth > 200 and depth < 300:
            # 201～299km
            hundreds = 200
            remainder = int(depth) - hundreds
            play_wav_sync(f"QuakeDepth_over{hundreds}.wav")
            if remainder > 0:
                play_wav_sync(f"QuakeDepth_{remainder}km.wav")
        elif depth > 300 and depth < 400:
            # 301～399km
            hundreds = 300
            remainder = int(depth) - hundreds
            play_wav_sync(f"QuakeDepth_over{hundreds}.wav")
            if remainder > 0:
                play_wav_sync(f"QuakeDepth_{remainder}km.wav")
        elif depth > 400 and depth < 500:
            # 401～499km
            hundreds = 400
            remainder = int(depth) - hundreds
            play_wav_sync(f"QuakeDepth_over{hundreds}.wav")
            if remainder > 0:
                play_wav_sync(f"QuakeDepth_{remainder}km.wav")
        elif depth > 500 and depth < 600:
            # 501～599km
            hundreds = 500
            remainder = int(depth) - hundreds
            play_wav_sync(f"QuakeDepth_over{hundreds}.wav")
            if remainder > 0:
                play_wav_sync(f"QuakeDepth_{remainder}km.wav")
        elif depth > 600 and depth < 700:
            # 601～699km
            hundreds = 600
            remainder = int(depth) - hundreds
            play_wav_sync(f"QuakeDepth_over{hundreds}.wav")
            if remainder > 0:
                play_wav_sync(f"QuakeDepth_{remainder}km.wav")
        elif depth > 700 and depth < 800:
            # 701～799km
            hundreds = 700
            remainder = int(depth) - hundreds
            play_wav_sync(f"QuakeDepth_over{hundreds}.wav")
            if remainder > 0:
                play_wav_sync(f"QuakeDepth_{remainder}km.wav")
        elif depth >= 800:
            # 800km～
            play_wav_sync(f"QuakeDepth_over800.wav")
        play_wav_sync("QuakeMagnitude_002.wav")
        if max_scale_int > 0:
            play_wav_sync(f"ShindoInfo_shindo{max_scale_int}.wav")
        count = 0
        for region in converted_regions:
            region_id = REGION_NAME_TO_ID.get(region)
            if region_id:
                play_wav_sync(f"ShindoRegion_{region_id}.wav")
                count += 1
                if count >= 3: break 
        if count > 0:
            play_wav_sync("ShindoInfo_002.wav")
    finally:
        audio_manager.end_sequence()


def play_tsunami_sequence(tsunami_type: str, region_names: list[str]):
    _enqueue_play(_play_tsunami_sequence_impl, tsunami_type, region_names, is_tsunami=True)

def _play_tsunami_sequence_impl(tsunami_type, region_names):
    print(f"Playing Tsunami Sequence: {tsunami_type}")
    
    # シーケンス開始
    audio_manager.start_sequence(is_tsunami=True)

    try:
        play_wav_sync("tsunami_info.wav")
        time.sleep(0.5)
        play_wav_sync(f"TsunamiInfo_{tsunami_type}_001.wav")
        time.sleep(0.2)
        count = 0
        for region in region_names:
            region_id = TSUNAMI_REGION_TO_ID.get(region)
            if region_id:
                play_wav_sync(f"TsunamiRegion_{region_id}.wav")
        play_wav_sync(f"TsunamiInfo_{tsunami_type}_002.wav")
        if tsunami_type in ["Warning", "Major"]:
            play_wav_sync("TsunamiInfo_003.wav")
    finally:
        audio_manager.end_sequence()