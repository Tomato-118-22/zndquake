import os
import re

# ===== 設定 =====
TARGET_PREFIX = "TsunamiInfo_"  # 対象となるファイル名の先頭
NUMBER_PATTERN = re.compile(r"_(\d+)$")  # 末尾の _001 などを検出
# =================

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files = os.listdir(base_dir)

    # 対象ファイルのみ抽出
    target_files = []
    for file in files:
        name, ext = os.path.splitext(file)
        if name.startswith(TARGET_PREFIX):
            match = NUMBER_PATTERN.search(name)
            if match:
                base_name = name[:match.start()]
                target_files.append((file, base_name, ext))

    # ベース名ごとにグループ化
    groups = {}
    for original, base_name, ext in target_files:
        key = base_name + ext
        groups.setdefault(key, []).append(original)

    # リネーム処理
    for base_file, originals in groups.items():
        base_name, ext = os.path.splitext(base_file)

        if len(originals) == 1:
            # 重複なし → 連番を消すだけ
            src = originals[0]
            dst = base_name + ext
            rename_safe(src, dst)
        else:
            # 重複あり → 新しい連番を付与
            originals.sort()
            for i, src in enumerate(originals, start=1):
                dst = f"{base_name}_{i:03d}{ext}"
                rename_safe(src, dst)

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
