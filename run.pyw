import subprocess
import sys
import time
import os
import tkinter as tk
import tkinter.messagebox as messagebox
import cv2
import pygame
from PyQt6.QtCore import QTimer
from PyQt6.QtNetwork import QLocalSocket
from PyQt6.QtWidgets import QApplication, QMessageBox
import urllib.request
import json
import webbrowser

# 現在のバージョン
VERSION = "Beta 1.0.0"

# 更新確認URL
UPDATE_URL = "https://www.tomato-tts.com/officez/products/zndquake/update.json"

# ダウンロードページ
WEBSITE_URL = "https://www.tomato-tts.com/officez/products/zndquake/dl"

if getattr(sys, 'frozen', False) or '__compiled__' in dir():
    # Nuitka/PyInstallerでコンパイル済み: sys.argv[0]が元のexeパス
    BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
else:
# .pyで直接実行
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

main_exe = os.path.join(BASE_DIR, "main.dist", "main.exe")

img_path = os.path.join(BASE_DIR, "run", "start.jpg")
img = cv2.imread(img_path)
if img is None:
    import numpy as np
    img = np.zeros((360, 480, 3), dtype=np.uint8)
img = cv2.resize(img, (480, 360))

img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

h, w = img_rgb.shape[:2]

pygame.init()

screen = pygame.display.set_mode((w, h), pygame.NOFRAME)
pygame.display.set_caption("Starting up now...")

surface = pygame.surfarray.make_surface(img_rgb.swapaxes(0, 1))

screen.blit(surface, (0, 0))
pygame.display.flip()

root = tk.Tk()
root.withdraw()

def check_update():
    try:
        req = urllib.request.Request(
            UPDATE_URL,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        latest_version = data.get("latest", "").strip()

        # 文字列として完全一致比較（最新版と異なる場合に通知）
        if latest_version and latest_version != VERSION:
            root.deiconify()
            result = messagebox.askyesno(
                "アップデート通知",
                f"新しいバージョンがあります。\n\n"
                f"現在: {VERSION}\n"
                f"最新: {latest_version}\n\n"
                "Webサイトを開きますか?"
            )
            root.withdraw()
            if result:
                webbrowser.open(WEBSITE_URL)

    except Exception as e:
        print("更新確認失敗:", e)

check_update()

if not os.path.exists(main_exe):
    root.deiconify()
    messagebox.showerror(
        "エラー",
        f"起動時に問題が発生しました。お手数ですが、もう一度お試しください。\nもし複数回試しても起動できない場合は、開発者にお問い合わせください。\n\n{main_exe}"
    )
    sys.exit(1)

p = subprocess.Popen(
    [main_exe],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=os.path.dirname(main_exe) # main.exeのフォルダをカレントディレクトリに設定
)

# 画像表示時間
time.sleep(10)

# 確認時間
STARTUP_GRACE_TIME = 1.5

start_time = time.time()
stderr_output = ""


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
    
    # このインスタンスは終了
    QTimer.singleShot(0, lambda: QApplication.instance().quit())

test_socket.close()
# sys.exit(1)

while True:
    # 生きているか確認
    if p.poll() is not None:
        # 即死の場合失敗
        _, stderr_output = p.communicate()
        break

    # 一定時間生存の場合起動
    if time.time() - start_time > STARTUP_GRACE_TIME:
        # ランチャー終了
        sys.exit(0)

    time.sleep(0.05)

# 失敗時
error_message = (
    "起動時に問題が発生しました。お手数ですが、もう一度お試しください。\nもし複数回試しても起動できない場合は、開発者にお問い合わせください。\n\n"
    + stderr_output.strip()
)

root.withdraw()
messagebox.showerror("エラー", error_message)
sys.exit(1)