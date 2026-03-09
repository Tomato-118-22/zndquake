import os           
import re

# ===== 設定 =====
TARGET_PREFIX = "Tsunami_Forecast_"
PATTERN = re.compile(rf"^{re.escape(TARGET_PREFIX)}(\d{{1,2}})$")
# =================

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files = os.listdir(base_dir)

    for file in files:
        name, ext = os.path.splitext(file)
        match = PATTERN.match(name)
        if not match:
            continue

        number = int(match.group(1))
        new_name = f"{TARGET_PREFIX}{number:03d}{ext}"

        rename_safe(file, new_name)

def rename_safe(src, dst):
    if src == dst:
        return

    if os.path.exists(dst):
        print(f"スキップ（既に存在）: {dst}")
        return

    os.rename(src, dst)
    print(f"{src} → {dst}")

if __name__ == "__main__":
    main()