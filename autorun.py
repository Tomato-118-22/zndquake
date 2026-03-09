import os
import sys
import platform
import subprocess
import traceback
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox

APP_NAME = "ZundaQuake"


# OS判定
def get_os():
    return platform.system()


# 実行対象を取得
def get_target():
    base_dir = Path(sys.argv[0]).resolve().parent
    os_name = get_os()

    if os_name == "Windows":
        target = base_dir / "ZundaQuake.exe"
    elif os_name == "Darwin":
        target = base_dir / "ZundaQuake.app"
    elif os_name == "Linux":
        target = base_dir / "ZundaQuake.run"
    else:
        return None

    return target if target.exists() else None


# Windows処理
def windows_startup_path():
    return Path(os.getenv("APPDATA")) / \
        "Microsoft/Windows/Start Menu/Programs/Startup" / f"{APP_NAME}.lnk"

def register_windows():
    import win32com.client
    startup_dir = Path(os.getenv("APPDATA")) / \
        "Microsoft/Windows/Start Menu/Programs/Startup"
    shortcut_path = startup_dir / f"{APP_NAME}.lnk"
    target = get_target()
    if not target:
        return
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(shortcut_path))
    if target.suffix == ".exe":
        shortcut.Targetpath = str(target)
        shortcut.WorkingDirectory = str(target.parent)
    else:
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = str(target.parent)
    shortcut.save()

def unregister_windows():
    path = windows_startup_path()
    if path.exists():
        path.unlink()

def is_registered_windows():
    return windows_startup_path().exists()


# macOS処理
def mac_plist_path():
    return Path.home() / "Library/LaunchAgents" / f"com.{APP_NAME}.plist"

def register_macos():
    plist_path = mac_plist_path()
    plist_path.parent.mkdir(parents=True, exist_ok=True)
    target = get_target()
    content = f"""
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.{APP_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/open</string>
        <string>{target}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
    with open(plist_path, "w") as f:
        f.write(content)
    subprocess.run(["launchctl", "load", str(plist_path)])

def unregister_macos():
    plist_path = mac_plist_path()
    if plist_path.exists():
        subprocess.run(["launchctl", "unload", str(plist_path)])
        plist_path.unlink()

def is_registered_macos():
    return mac_plist_path().exists()


# Linux処理
def linux_desktop_path():
    return Path.home() / ".config/autostart" / f"{APP_NAME}.desktop"

def register_linux():
    path = linux_desktop_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    target = get_target()
    content = f"""[Desktop Entry]
Type=Application
Exec={target}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name={APP_NAME}
"""
    with open(path, "w") as f:
        f.write(content)

def unregister_linux():
    path = linux_desktop_path()
    if path.exists():
        path.unlink()

def is_registered_linux():
    return linux_desktop_path().exists()


# メイン処理
def toggle_startup():
    os_name = get_os()

    if os_name == "Windows":
        if is_registered_windows():
            unregister_windows()
            return False
        else:
            register_windows()
            return True

    elif os_name == "Darwin":
        if is_registered_macos():
            unregister_macos()
            return False
        else:
            register_macos()
            return True

    elif os_name == "Linux":
        if is_registered_linux():
            unregister_linux()
            return False
        else:
            register_linux()
            return True

    return None


# PyQt通知
def show_message(registered):
    os_name = get_os()
    app = QApplication(sys.argv)

    if registered:
        QMessageBox.information(None, "Startup", f"スタートアップを登録しました。\nOS名: {os_name}\n設定したプログラム名: {APP_NAME}")
    else:
        QMessageBox.information(None, "Startup", f"スタートアップを解除しました。\nOS名: {os_name}\n設定したプログラム名: {APP_NAME}")

    sys.exit(0)


if __name__ == "__main__":
    try:
        result = toggle_startup()

        if result is None:
            app = QApplication(sys.argv)
            QMessageBox.warning(None, "Startup", "このOSはサポートされていません。")
            sys.exit(1)

        show_message(result)

    except Exception:
        err = traceback.format_exc()
        app = QApplication(sys.argv)
        QMessageBox.critical(None, "エラー", f"予期しないエラーが発生しました。\n\n{err}")
        sys.exit(1)