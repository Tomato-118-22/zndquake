'''
ClaudeによるWin→mac変換
'''

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import sys
import shutil
import zipfile
import urllib.request
import subprocess
import getpass
import json
from pathlib import Path

# 多言語辞書(日本語、英語、中国語繁体字、スペイン語ラテンアメリカ、韓国語)
LANG = {
    "ja": {
        "title": "ZundaQuakeセットアップ",
        "lang_select_title": "Language selection",
        "lang_select_label": "Please select the language you want to use during installation. インストール時に使用する言語を選択してください。",
        "next": "次へ(N) >",
        "back": "< 戻る(B)",
        "cancel": "キャンセル",
        "finish": "完了",
        "agree": "同意する(A)",
        "disagree": "同意しない(D)",
        "install": "インストール",
        "uninstall": "アンインストール",
        "reinstall": "再インストール",
        "close": "閉じる",

        # ページタイトル
        "page_lang": "言語選択 Language selection",
        "page_license": "使用許諾契約書",
        "page_install_type": "インストールの種類",
        "page_installing": "インストール中",
        "page_advanced": "詳細設定",
        "page_finish": "インストール完了",
        "page_already": "既存のインストールを検出",

        # 使用許諾
        "license_header": "使用許諾契約書をお読みください。",
        "license_body": (
            "============================================================\nZundaQuake エンドユーザー使用許諾契約書(EULA)\n============================================================\n\n本日はZundaQuakeをインストールしていただき、誠にありがとうございます。Tomato Office Z Development Teamが提供するサービスをお客様がご利用になる場合は、お客様とTomato Office Z Development Teamの間で以下の契約に同意する必要がございます。以下に記載された全てまたは一部の内容に同意されない場合、ZundaQuakeのインストールを完了できず、サービスを提供できません。\n\n第1条(ライセンス)\n1. 本エンドユーザー使用許諾契約書(以下、「本契約」といいます)は、Tomato Office Z Development Team(以下、「トマト」といいます)が提供する「ZundaQuake」(以下「本製品」といいます)並びに付随して提供されるサービス(以下、本製品を含め全て「本ソフトウェア」とします)をお客様が使用する条件を定める物となります。\n2. 本ソフトウェアに含まれるZundaQuake API機能については、本契約に加え、「ZundaQuake API利用規約」に同意の上ご利用ください。\n\n第2条(契約の成立)\n1. お客様は、本契約の内容に同意した上で、本ソフトウェアを利用する物とします。\n2. 本ソフトウェアのインストールプログラムを起動後、本契約の内容を理解して同意する旨のボタンを押下した時点で、お客様が本契約に同意した物とみなされ、お客様とトマトとの間で本契約を内容とする契約が成立します。\n\n第3条(禁止事項)\nお客様は、次に掲げる行為をしてはならない物とします。\n(1)本ソフトウェアを使用して悪意を持ち、虚偽の情報や古い情報を拡散する事\n(2)本ソフトウェアをバックアップ以外の目的で複製、有･無料に限らず譲渡、貸与又はその方法を問わず使用させる事\n(3)本ソフトウェアのリバースエンジニアリング、逆コンパイル等の行為(オープンデータを使用する事)\n(4)トマト又は第三者の著作権、特許権、商標権その他の知的財産権又は肖像権その他一切の権利若しくは利益を侵害する行為又はその恐れのある行為\n(5)本ソフトウェアの画像･音声データの一部または全てをバックアップ以外の目的で複製、有･無料に限らず譲渡、貸与又はその方法を問わず使用させる事\n(6)本ソフトウェアを使用して公序良俗に反する行為を行う事\n(7)本ソフトウェア上のトマトその他著作権者を示す表記を削除し、変更しその他不明確にする事\n(8)その他、トマトが不適切であると合理的に判断する行為\n\n第4条(知的財産権)\n本ソフトウェアに関する著作権及びその他の知的財産権は、全てトマトに帰属します。\n\n第5条(免責)\n1. 本ソフトウェアによって提供されるあらゆる情報の正確性について、トマトは一切保証いたしません。また、利用によるいかなる損害についても、一切の責任を負いません。\n2. 本ソフトウェアに起因する損害の責任は、トマトはその損害について、一切の責任を負いません。\n\n第6条(契約終了)\n1. トマトは、お客様が本契約の条件を違反した場合、本契約を何らの催告なく解除する事ができます。\n2. 本契約が解除された場合、以後本ソフトウェアを使用してはならず、本ソフトウェア及びその複製物を全て破棄し、コンピュータの記憶領域から完全に消去する物とします。\n3. 本契約の解除によりお客様又は第三者が被る損害について、トマトは一切の責任を負いません。\n4. 第5条、本条、第7条及び第8条の規定は、本契約の終了後も有効に存続する物とします。\n\n第7条(準拠法、管轄)\n1. 本契約は、日本法に準拠し、解釈される物とします。\n2. 本ソフトウェアに関する一切の紛争については、札幌地方裁判所を第一審の専属的合意管轄裁判所とします。\n\n第8条(本契約の変更)\nトマトは、法令等を遵守するために必要な時、お客様の一般の利益に適合する時、トマトが合理的に必要と考える時には、本契約を変更する旨及び変更後の内容並びにその変更の効力発生時期を、お客様への通知、インターネットの利用その他の適切な方法により周知する事によって、本契約の内容を変更する事ができる物とします。\n\n2026年2月6日　制定\n============================================================\nCopyright (C) 2026 Tomato. All rights reserved."
        ),
        "license_agree_check": "使用許諾契約書の条件に同意します(A)",

        # インストール種類
        "install_type_header": "インストール先を選択してください。",
        "install_type_user": "現在のユーザーにインストール(管理者権限不要)",
        "install_type_user_path": "インストール先: /Users/{user}/Applications/{app}",
        "install_type_all": "すべてのユーザーにインストール(管理者権限が必要)",
        "install_type_all_path": "インストール先: /Applications/{app}",
        "admin_required": "すべてのユーザーへのインストールには管理者権限が必要です。\n管理者パスワードを入力して続行しますか?",
        "admin_restart": "管理者として続行",

        # インストール中
        "downloading": "ダウンロード中...",
        "extracting": "展開中...",
        "copying": "ファイルをコピー中...",
        "registering": "登録中...",
        "install_done": "インストールが完了しました。",
        "install_failed": "インストールに失敗しました:\n{error}",
        "progress": "{percent}%",

        # 詳細設定
        "advanced_header": "詳細設定を選択してください。",
        "opt_dock": "Dockに追加する",
        "opt_launchpad": "Launchpadに表示する",
        "opt_website": "公式サイトを開く",
        "website_url": "https://www.tomato-tts.com/officez/products/zndquake/about",

        # 既存インストール検出
        "already_title": "既存のインストールが検出されました。",
        "already_body": "このソフトウェアはすでにインストールされています。\n操作を選択してください:",

        # 完了
        "finish_title": "セットアップ完了",
        "finish_body": "セットアップウィザードが完了しました。\n「完了」をクリックしてウィザードを閉じてください。",
        "launch_after": "セットアップ完了後にアプリケーションを起動する",

        # アンインストール
        "uninstall_confirm": "本当にアンインストールしますか?",
        "uninstall_done": "アンインストールが完了しました。",
        "uninstall_failed": "アンインストールに失敗しました:\n{error}",
    },
    "en-UK": {
        "title": "ZundaQuake Setup",
        "lang_select_title": "Language selection",
        "lang_select_label": "Please select the language you want to use during installation. インストール時に使用する言語を選択してください。",
        "next": "Next(N) >",
        "back": "< Back(B)",
        "cancel": "Cancel",
        "finish": "Finish",
        "agree": "Agree(A)",
        "disagree": "Disagree(D)",
        "install": "Install",
        "uninstall": "Uninstall",
        "reinstall": "Reinstall",
        "close": "Close",

        "page_lang": "言語選択 Language selection",
        "page_license": "Licence",
        "page_install_type": "Install type",
        "page_installing": "Installing",
        "page_advanced": "Advanced",
        "page_finish": "Installation complete",
        "page_already": "Detected a known install",

        "license_header": "Please read the licence agreement.",
        "license_body": (
            "============================================================\nZundaQuake エンドユーザー使用許諾契約書(EULA)\n============================================================\n\n本日はZundaQuakeをインストールしていただき、誠にありがとうございます。Tomato Office Z Development Teamが提供するサービスをお客様がご利用になる場合は、お客様とTomato Office Z Development Teamの間で以下の契約に同意する必要がございます。以下に記載された全てまたは一部の内容に同意されない場合、ZundaQuakeのインストールを完了できず、サービスを提供できません。\n\n第1条(ライセンス)\n1. 本エンドユーザー使用許諾契約書(以下、「本契約」といいます)は、Tomato Office Z Development Team(以下、「トマト」といいます)が提供する「ZundaQuake」(以下「本製品」といいます)並びに付随して提供されるサービス(以下、本製品を含め全て「本ソフトウェア」とします)をお客様が使用する条件を定める物となります。\n2. 本ソフトウェアに含まれるZundaQuake API機能については、本契約に加え、「ZundaQuake API利用規約」に同意の上ご利用ください。\n\n第2条(契約の成立)\n1. お客様は、本契約の内容に同意した上で、本ソフトウェアを利用する物とします。\n2. 本ソフトウェアのインストールプログラムを起動後、本契約の内容を理解して同意する旨のボタンを押下した時点で、お客様が本契約に同意した物とみなされ、お客様とトマトとの間で本契約を内容とする契約が成立します。\n\n第3条(禁止事項)\nお客様は、次に掲げる行為をしてはならない物とします。\n(1)本ソフトウェアを使用して悪意を持ち、虚偽の情報や古い情報を拡散する事\n(2)本ソフトウェアをバックアップ以外の目的で複製、有･無料に限らず譲渡、貸与又はその方法を問わず使用させる事\n(3)本ソフトウェアのリバースエンジニアリング、逆コンパイル等の行為(オープンデータを使用する事)\n(4)トマト又は第三者の著作権、特許権、商標権その他の知的財産権又は肖像権その他一切の権利若しくは利益を侵害する行為又はその恐れのある行為\n(5)本ソフトウェアの画像･音声データの一部または全てをバックアップ以外の目的で複製、有･無料に限らず譲渡、貸与又はその方法を問わず使用させる事\n(6)本ソフトウェアを使用して公序良俗に反する行為を行う事\n(7)本ソフトウェア上のトマトその他著作権者を示す表記を削除し、変更しその他不明確にする事\n(8)その他、トマトが不適切であると合理的に判断する行為\n\n第4条(知的財産権)\n本ソフトウェアに関する著作権及びその他の知的財産権は、全てトマトに帰属します。\n\n第5条(免責)\n1. 本ソフトウェアによって提供されるあらゆる情報の正確性について、トマトは一切保証いたしません。また、利用によるいかなる損害についても、一切の責任を負いません。\n2. 本ソフトウェアに起因する損害の責任は、トマトはその損害について、一切の責任を負いません。\n\n第6条(契約終了)\n1. トマトは、お客様が本契約の条件を違反した場合、本契約を何らの催告なく解除する事ができます。\n2. 本契約が解除された場合、以後本ソフトウェアを使用してはならず、本ソフトウェア及びその複製物を全て破棄し、コンピュータの記憶領域から完全に消去する物とします。\n3. 本契約の解除によりお客様又は第三者が被る損害について、トマトは一切の責任を負いません。\n4. 第5条、本条、第7条及び第8条の規定は、本契約の終了後も有効に存続する物とします。\n\n第7条(準拠法、管轄)\n1. 本契約は、日本法に準拠し、解釈される物とします。\n2. 本ソフトウェアに関する一切の紛争については、札幌地方裁判所を第一審の専属的合意管轄裁判所とします。\n\n第8条(本契約の変更)\nトマトは、法令等を遵守するために必要な時、お客様の一般の利益に適合する時、トマトが合理的に必要と考える時には、本契約を変更する旨及び変更後の内容並びにその変更の効力発生時期を、お客様への通知、インターネットの利用その他の適切な方法により周知する事によって、本契約の内容を変更する事ができる物とします。\n\n2026年2月6日　制定\n============================================================\nCopyright (C) 2026 Tomato. All rights reserved."
        ),
        "license_agree_check": "I agree to the conditions of licence.(A)",

        "install_type_header": "Please select the installation destination.",
        "install_type_user": "Install for the current user (no administrator rights required)",
        "install_type_user_path": "Install destination: /Users/{user}/Applications/{app}",
        "install_type_all": "Install for all users (administrator rights required)",
        "install_type_all_path": "Install destination: /Applications/{app}",
        "admin_required": "Administrator privileges are required to install for all users.\nDo you want to continue with an administrator password?",
        "admin_restart": "Continue as administrator",

        "downloading": "Downloading...",
        "extracting": "Extracting...",
        "copying": "Copying files...",
        "registering": "Registering...",
        "install_done": "The installation has been completed.",
        "install_failed": "The install failed:\n{error}",
        "progress": "{percent}%",

        "advanced_header": "Please select the advanced settings.",
        "opt_dock": "Add to Dock",
        "opt_launchpad": "Show in Launchpad",
        "opt_website": "Open official website",
        "website_url": "https://www.tomato-tts.com/officez/products/zndquake/about_en",

        "already_title": "An existing installation has been detected",
        "already_body": "This software has already been installed.\nPlease select an operation:",

        "finish_title": "Setup completed",
        "finish_body": 'The setup wizard has been completed.\nClick "Finish" to exit the wizard.',
        "launch_after": "Launch the application after the setup is complete",

        "uninstall_confirm": "Do you really want to uninstall this software?",
        "uninstall_done": "The uninstallation has been completed.",
        "uninstall_failed": "The uninstallation failed:\n{error}",
    },
    "ko-KR": {
        "title": "ZundaQuake 설치",
        "lang_select_title": "Language selection",
        "lang_select_label": "Please select the language you want to use during installation. 설치 시에 사용할 언어를 선택해 주시기 바랍니다.",
        "next": "다음(N) >",
        "back": "< 뒤로(B)",
        "cancel": "취소",
        "finish": "완료",
        "agree": "동의하기(A)",
        "disagree": "안 동의하기(D)",
        "install": "설치",
        "uninstall": "제거",
        "reinstall": "재설치",
        "close": "닫기",

        "page_lang": "언어 선택 Language selection",
        "page_license": "사용 허가 계약서",
        "page_install_type": "설치 종류",
        "page_installing": "설치 중",
        "page_advanced": "상세 설정",
        "page_finish": "설치 완료",
        "page_already": "기존 설치를 감지",

        "license_header": "사용 허가 계약서를 읽어 주시기 바랍니다",
        "license_body": (
            "============================================================\nZundaQuake エンドユーザー使用許諾契約書(EULA)\n============================================================\n\n本日はZundaQuakeをインストールしていただき、誠にありがとうございます。Tomato Office Z Development Teamが提供するサービスをお客様がご利用になる場合は、お客様とTomato Office Z Development Teamの間で以下の契約に同意する必要がございます。以下に記載された全てまたは一部の内容に同意されない場合、ZundaQuakeのインストールを完了できず、サービスを提供できません。\n\n第1条(ライセンス)\n1. 本エンドユーザー使用許諾契約書(以下、「本契約」といいます)は、Tomato Office Z Development Team(以下、「トマト」といいます)が提供する「ZundaQuake」(以下「本製品」といいます)並びに付随して提供されるサービス(以下、本製品を含め全て「本ソフトウェア」とします)をお客様が使用する条件を定める物となります。\n2. 本ソフトウェアに含まれるZundaQuake API機能については、本契約に加え、「ZundaQuake API利用規約」に同意の上ご利用ください。\n\n第2条(契約の成立)\n1. お客様は、本契約の内容に同意した上で、本ソフトウェアを利用する物とします。\n2. 本ソフトウェアのインストールプログラムを起動後、本契約の内容を理解して同意する旨のボタンを押下した時点で、お客様が本契約に同意した物とみなされ、お客様とトマトとの間で本契約を内容とする契約が成立します。\n\n第3条(禁止事項)\nお客様は、次に掲げる行為をしてはならない物とします。\n(1)本ソフトウェアを使用して悪意を持ち、虚偽の情報や古い情報を拡散する事\n(2)本ソフトウェアをバックアップ以外の目的で複製、有･無料に限らず譲渡、貸与又はその方法を問わず使用させる事\n(3)本ソフトウェアのリバースエンジニアリング、逆コンパイル等の行為(オープンデータを使用する事)\n(4)トマト又は第三者の著作権、特許権、商標権その他の知的財産権又は肖像権その他一切の権利若しくは利益を侵害する行為又はその恐れのある行為\n(5)本ソフトウェアの画像･音声データの一部または全てをバックアップ以外の目的で複製、有･無料に限らず譲渡、貸与又はその方法を問わず使用させる事\n(6)本ソフトウェアを使用して公序良俗に反する行為を行う事\n(7)本ソフトウェア上のトマトその他著作権者を示す表記を削除し、変更しその他不明確にする事\n(8)その他、トマトが不適切であると合理的に判断する行為\n\n第4条(知的財産権)\n本ソフトウェアに関する著作権及びその他の知的財産権は、全てトマトに帰属します。\n\n第5条(免責)\n1. 本ソフトウェアによって提供されるあらゆる情報の正確性について、トマトは一切保証いたしません。また、利用によるいかなる損害についても、一切の責任を負いません。\n2. 本ソフトウェアに起因する損害の責任は、トマトはその損害について、一切の責任を負いません。\n\n第6条(契約終了)\n1. トマトは、お客様が本契約の条件を違反した場合、本契約を何らの催告なく解除する事ができます。\n2. 本契約が解除された場合、以後本ソフトウェアを使用してはならず、本ソフトウェア及びその複製物を全て破棄し、コンピュータの記憶領域から完全に消去する物とします。\n3. 本契約の解除によりお客様又は第三者が被る損害について、トマトは一切の責任を負いません。\n4. 第5条、本条、第7条及び第8条の規定は、本契約の終了後も有効に存続する物とします。\n\n第7条(準拠法、管轄)\n1. 本契約は、日本法に準拠し、解釈される物とします。\n2. 本ソフトウェアに関する一切の紛争については、札幌地方裁判所を第一審の専属的合意管轄裁判所とします。\n\n第8条(本契約の変更)\nトマトは、法令等を遵守するために必要な時、お客様の一般の利益に適合する時、トマトが合理的に必要と考える時には、本契約を変更する旨及び変更後の内容並びにその変更の効力発生時期を、お客様への通知、インターネットの利用その他の適切な方法により周知する事によって、本契約の内容を変更する事ができる物とします。\n\n2026年2月6日　制定\n============================================================\nCopyright (C) 2026 Tomato. All rights reserved."
        ),
        "license_agree_check": "사용 허가 계약서의 조건에 동의합니다(A)",

        "install_type_header": "설치 위치를 선택해 주시기 바랍니다.",
        "install_type_user": "현재 사용자에게 설치(관리자 권한 불필요)",
        "install_type_user_path": "설치 위치: /Users/{user}/Applications/{app}",
        "install_type_all": "모든 사용자에게 설치(관리자 권한 필요)",
        "install_type_all_path": "설치 위치: /Applications/{app}",
        "admin_required": "모든 사용자에게 설치하려면 관리자 권한이 필요합니다.\n관리자 암호를 입력하여 계속하시겠습니까?",
        "admin_restart": "관리자로서 계속",

        "downloading": "다운로드 중...",
        "extracting": "압축 해제 중...",
        "copying": "파일을 복사 중...",
        "registering": "등록 중...",
        "install_done": "설치가 완료되었습니다.",
        "install_failed": "설치에 실패했습니다:\n{error}",
        "progress": "{percent}%",

        "advanced_header": "상세 설정을 선택해 주시기 바랍니다.",
        "opt_dock": "Dock에 추가하기",
        "opt_launchpad": "Launchpad에 표시하기",
        "opt_website": "공식 사이트를 열기",
        "website_url": "https://www.tomato-tts.com/officez/products/zndquake/about_kr",

        "already_title": "기존 설치가 감지되었습니다",
        "already_body": "이 소프트웨어는 이미 설치되어 있습니다.\n조작을 선택해 주십시오:",

        "finish_title": "설치 완료",
        "finish_body": "설정 마법사가 완료되었습니다.\n「완료」를 클릭하여 마법사를 닫아 주시기 바랍니다.",
        "launch_after": "설정 완료 후에 애플리케이션을 실행합니다",

        "uninstall_confirm": "정말로 제거하시겠습니까?",
        "uninstall_done": "제거가 완료되었습니다.",
        "uninstall_failed": "제거에 실패했습니다:\n{error}",
    },
    "zh-TW": {
        "title": "ZundaQuake 安裝程式",
        "lang_select_title": "Language selection",
        "lang_select_label": "Please select the language you want to use during installation. 請選擇安裝時使用的語言。",

        "next": "下一步(N) >",
        "back": "< 上一步(B)",
        "cancel": "取消",
        "finish": "完成",
        "agree": "同意(A)",
        "disagree": "不同意(D)",
        "install": "安裝",
        "uninstall": "解除安裝",
        "reinstall": "重新安裝",
        "close": "關閉",

        "page_lang": "語言選擇",
        "page_license": "授權合約",
        "page_install_type": "安裝類型",
        "page_installing": "正在安裝",
        "page_advanced": "進階設定",
        "page_finish": "安裝完成",
        "page_already": "偵測到已安裝版本",

        "license_header": "請閱讀授權合約",
        "license_body": (
            "============================================================\nZundaQuake エンドユーザー使用許諾契約書(EULA)\n============================================================\n\n本日はZundaQuakeをインストールしていただき、誠にありがとうございます。Tomato Office Z Development Teamが提供するサービスをお客様がご利用になる場合は、お客様とTomato Office Z Development Teamの間で以下の契約に同意する必要がございます。以下に記載された全てまたは一部の内容に同意されない場合、ZundaQuakeのインストールを完了できず、サービスを提供できません。\n\n第1条(ライセンス)\n1. 本エンドユーザー使用許諾契約書(以下、「本契約」といいます)は、Tomato Office Z Development Team(以下、「トマト」といいます)が提供する「ZundaQuake」(以下「本製品」といいます)並びに付随して提供されるサービス(以下、本製品を含め全て「本ソフトウェア」とします)をお客様が使用する条件を定める物となります。\n2. 本ソフトウェアに含まれるZundaQuake API機能については、本契約に加え、「ZundaQuake API利用規約」に同意の上ご利用ください。\n\n第2条(契約の成立)\n1. お客様は、本契約の内容に同意した上で、本ソフトウェアを利用する物とします。\n2. 本ソフトウェアのインストールプログラムを起動後、本契約の内容を理解して同意する旨のボタンを押下した時点で、お客様が本契約に同意した物とみなされ、お客様とトマトとの間で本契約を内容とする契約が成立します。\n\n第3条(禁止事項)\nお客様は、次に掲げる行為をしてはならない物とします。\n(1)本ソフトウェアを使用して悪意を持ち、虚偽の情報や古い情報を拡散する事\n(2)本ソフトウェアをバックアップ以外の目的で複製、有･無料に限らず譲渡、貸与又はその方法を問わず使用させる事\n(3)本ソフトウェアのリバースエンジニアリング、逆コンパイル等の行為(オープンデータを使用する事)\n(4)トマト又は第三者の著作権、特許権、商標権その他の知的財産権又は肖像権その他一切の権利若しくは利益を侵害する行為又はその恐れのある行為\n(5)本ソフトウェアの画像･音声データの一部または全てをバックアップ以外の目的で複製、有･無料に限らず譲渡、貸与又はその方法を問わず使用させる事\n(6)本ソフトウェアを使用して公序良俗に反する行為を行う事\n(7)本ソフトウェア上のトマトその他著作権者を示す表記を削除し、変更しその他不明確にする事\n(8)その他、トマトが不適切であると合理的に判断する行為\n\n第4条(知的財産権)\n本ソフトウェアに関する著作権及びその他の知的財産権は、全てトマトに帰属します。\n\n第5条(免責)\n1. 本ソフトウェアによって提供されるあらゆる情報の正確性について、トマトは一切保証いたしません。また、利用によるいかなる損害についても、一切の責任を負いません。\n2. 本ソフトウェアに起因する損害の責任は、トマトはその損害について、一切の責任を負いません。\n\n第6条(契約終了)\n1. トマトは、お客様が本契約の条件を違反した場合、本契約を何らの催告なく解除する事ができます。\n2. 本契約が解除された場合、以後本ソフトウェアを使用してはならず、本ソフトウェア及びその複製物を全て破棄し、コンピュータの記憶領域から完全に消去する物とします。\n3. 本契約の解除によりお客様又は第三者が被る損害について、トマトは一切の責任を負いません。\n4. 第5条、本条、第7条及び第8条の規定は、本契約の終了後も有効に存続する物とします。\n\n第7条(準拠法、管轄)\n1. 本契約は、日本法に準拠し、解釈される物とします。\n2. 本ソフトウェアに関する一切の紛争については、札幌地方裁判所を第一審の専属的合意管轄裁判所とします。\n\n第8条(本契約の変更)\nトマトは、法令等を遵守するために必要な時、お客様の一般の利益に適合する時、トマトが合理的に必要と考える時には、本契約を変更する旨及び変更後の内容並びにその変更の効力発生時期を、お客様への通知、インターネットの利用その他の適切な方法により周知する事によって、本契約の内容を変更する事ができる物とします。\n\n2026年2月6日　制定\n============================================================\nCopyright (C) 2026 Tomato. All rights reserved."
        ),
        "license_agree_check": "我同意授權合約條款(A)",

        "install_type_header": "請選擇安裝位置",
        "install_type_user": "僅為目前使用者安裝（不需要管理員權限）",
        "install_type_user_path": "安裝位置: /Users/{user}/Applications/{app}",
        "install_type_all": "為所有使用者安裝（需要管理員權限）",
        "install_type_all_path": "安裝位置: /Applications/{app}",
        "admin_required": "為所有使用者安裝需要管理員權限。\n是否輸入管理員密碼繼續？",
        "admin_restart": "以管理員身分繼續",

        "downloading": "下載中...",
        "extracting": "解壓縮中...",
        "copying": "正在複製檔案...",
        "registering": "正在註冊...",
        "install_done": "安裝已完成。",
        "install_failed": "安裝失敗：\n{error}",
        "progress": "{percent}%",

        "advanced_header": "請選擇進階設定。",
        "opt_dock": "加入 Dock",
        "opt_launchpad": "在 Launchpad 顯示",
        "opt_website": "開啟官方網站",
        "website_url": "https://www.tomato-tts.com/officez/products/zndquake/about_zh",

        "already_title": "偵測到已安裝版本",
        "already_body": "此軟體已安裝。\n請選擇操作：",

        "finish_title": "安裝完成",
        "finish_body": "安裝精靈已完成。\n請按「完成」關閉安裝程式。",
        "launch_after": "安裝完成後啟動應用程式",

        "uninstall_confirm": "確定要解除安裝嗎？",
        "uninstall_done": "解除安裝完成。",
        "uninstall_failed": "解除安裝失敗：\n{error}",
    },
    "es-LA": {
        "title": "Instalador de ZundaQuake",
        "lang_select_title": "Selección de idioma",
        "lang_select_label": "Please select the language you want to use during installation. Seleccione el idioma que desea utilizar durante la instalación.",

        "next": "Siguiente(N) >",
        "back": "< Atrás(B)",
        "cancel": "Cancelar",
        "finish": "Finalizar",
        "agree": "Aceptar(A)",
        "disagree": "No aceptar(D)",
        "install": "Instalar",
        "uninstall": "Desinstalar",
        "reinstall": "Reinstalar",
        "close": "Cerrar",

        "page_lang": "Selección de idioma",
        "page_license": "Licencia",
        "page_install_type": "Tipo de instalación",
        "page_installing": "Instalando",
        "page_advanced": "Opciones avanzadas",
        "page_finish": "Instalación finalizada",
        "page_already": "Instalación existente detectada",

        "license_header": "Por favor lea el acuerdo de licencia",
        "license_body": (
            "============================================================\nZundaQuake エンドユーザー使用許諾契約書(EULA)\n============================================================\n\n本日はZundaQuakeをインストールしていただき、誠にありがとうございます。Tomato Office Z Development Teamが提供するサービスをお客様がご利用になる場合は、お客様とTomato Office Z Development Teamの間で以下の契約に同意する必要がございます。以下に記載された全てまたは一部の内容に同意されない場合、ZundaQuakeのインストールを完了できず、サービスを提供できません。\n\n第1条(ライセンス)\n1. 本エンドユーザー使用許諾契約書(以下、「本契約」といいます)は、Tomato Office Z Development Team(以下、「トマト」といいます)が提供する「ZundaQuake」(以下「本製品」といいます)並びに付随して提供されるサービス(以下、本製品を含め全て「本ソフトウェア」とします)をお客様が使用する条件を定める物となります。\n2. 本ソフトウェアに含まれるZundaQuake API機能については、本契約に加え、「ZundaQuake API利用規約」に同意の上ご利用ください。\n\n第2条(契約の成立)\n1. お客様は、本契約の内容に同意した上で、本ソフトウェアを利用する物とします。\n2. 本ソフトウェアのインストールプログラムを起動後、本契約の内容を理解して同意する旨のボタンを押下した時点で、お客様が本契約に同意した物とみなされ、お客様とトマトとの間で本契約を内容とする契約が成立します。\n\n第3条(禁止事項)\nお客様は、次に掲げる行為をしてはならない物とします。\n(1)本ソフトウェアを使用して悪意を持ち、虚偽の情報や古い情報を拡散する事\n(2)本ソフトウェアをバックアップ以外の目的で複製、有･無料に限らず譲渡、貸与又はその方法を問わず使用させる事\n(3)本ソフトウェアのリバースエンジニアリング、逆コンパイル等の行為(オープンデータを使用する事)\n(4)トマト又は第三者の著作権、特許権、商標権その他の知的財産権又は肖像権その他一切の権利若しくは利益を侵害する行為又はその恐れのある行為\n(5)本ソフトウェアの画像･音声データの一部または全てをバックアップ以外の目的で複製、有･無料に限らず譲渡、貸与又はその方法を問わず使用させる事\n(6)本ソフトウェアを使用して公序良俗に反する行為を行う事\n(7)本ソフトウェア上のトマトその他著作権者を示す表記を削除し、変更しその他不明確にする事\n(8)その他、トマトが不適切であると合理的に判断する行為\n\n第4条(知的財産権)\n本ソフトウェアに関する著作権及びその他の知的財産権は、全てトマトに帰属します。\n\n第5条(免責)\n1. 本ソフトウェアによって提供されるあらゆる情報の正確性について、トマトは一切保証いたしません。また、利用によるいかなる損害についても、一切の責任を負いません。\n2. 本ソフトウェアに起因する損害の責任は、トマトはその損害について、一切の責任を負いません。\n\n第6条(契約終了)\n1. トマトは、お客様が本契約の条件を違反した場合、本契約を何らの催告なく解除する事ができます。\n2. 本契約が解除された場合、以後本ソフトウェアを使用してはならず、本ソフトウェア及びその複製物を全て破棄し、コンピュータの記憶領域から完全に消去する物とします。\n3. 本契約の解除によりお客様又は第三者が被る損害について、トマトは一切の責任を負いません。\n4. 第5条、本条、第7条及び第8条の規定は、本契約の終了後も有効に存続する物とします。\n\n第7条(準拠法、管轄)\n1. 本契約は、日本法に準拠し、解釈される物とします。\n2. 本ソフトウェアに関する一切の紛争については、札幌地方裁判所を第一審の専属的合意管轄裁判所とします。\n\n第8条(本契約の変更)\nトマトは、法令等を遵守するために必要な時、お客様の一般の利益に適合する時、トマトが合理的に必要と考える時には、本契約を変更する旨及び変更後の内容並びにその変更の効力発生時期を、お客様への通知、インターネットの利用その他の適切な方法により周知する事によって、本契約の内容を変更する事ができる物とします。\n\n2026年2月6日　制定\n============================================================\nCopyright (C) 2026 Tomato. All rights reserved."
        ),
        "license_agree_check": "Acepto los términos del acuerdo de licencia(A)",

        "install_type_header": "Seleccione la ubicación de instalación",
        "install_type_user": "Instalar solo para el usuario actual (no requiere permisos de administrador)",
        "install_type_user_path": "Destino de instalación: /Users/{user}/Applications/{app}",
        "install_type_all": "Instalar para todos los usuarios (requiere permisos de administrador)",
        "install_type_all_path": "Destino de instalación: /Applications/{app}",
        "admin_required": "Se requieren permisos de administrador para instalar para todos los usuarios.\n¿Desea continuar con una contraseña de administrador?",
        "admin_restart": "Continuar como administrador",

        "downloading": "Descargando...",
        "extracting": "Extrayendo...",
        "copying": "Copiando archivos...",
        "registering": "Registrando...",
        "install_done": "La instalación se ha completado.",
        "install_failed": "La instalación falló:\n{error}",
        "progress": "{percent}%",

        "advanced_header": "Seleccione las opciones avanzadas.",
        "opt_dock": "Agregar al Dock",
        "opt_launchpad": "Mostrar en Launchpad",
        "opt_website": "Abrir el sitio web oficial",
        "website_url": "https://www.tomato-tts.com/officez/products/zndquake/about_es",

        "already_title": "Se detectó una instalación existente",
        "already_body": "Este software ya está instalado.\nSeleccione una opción:",

        "finish_title": "Instalación completada",
        "finish_body": "El asistente de instalación ha finalizado.\nHaga clic en «Finalizar» para salir.",
        "launch_after": "Iniciar la aplicación después de finalizar",

        "uninstall_confirm": "¿Realmente desea desinstalar?",
        "uninstall_done": "La desinstalación se ha completado.",
        "uninstall_failed": "La desinstalación falló:\n{error}",
    },
}

# 追加言語はここに辞書を追加する

# 定数
APP_NAME        = "ZundaQuake"
APP_VERSION     = "Beta 1.0.0"
UPDATE_URL      = "https://www.tomato-tts.com/officez/products/zndquake/update.json"
WEBSITE_URL     = "https://www.tomato-tts.com/officez/products/zndquake/dl"
# ★ macOS用: ZundaQuake4Mac.zip.001〜004 (4分割)
DOWNLOAD_URLS   = [
    "https://www.tomato-tts.com/officez/products/zndquake/ZundaQuake4Mac.zip.001",
    "https://www.tomato-tts.com/officez/products/zndquake/ZundaQuake4Mac.zip.002",
    "https://www.tomato-tts.com/officez/products/zndquake/ZundaQuake4Mac.zip.003",
    "https://www.tomato-tts.com/officez/products/zndquake/ZundaQuake4Mac.zip.004",
]
ZIP_PASSWORD    = b"zunda0311"
UNINSTALL_INFO  = "uninstall.json"  # インストール先に保存するアンインストール情報

WINDOW_W, WINDOW_H = 640, 480
SIDEBAR_W = 180


# ── macOSユーティリティ ──────────────────────────────────────────

def is_admin() -> bool:
    """macOSでは root (uid==0) かどうかで判定する"""
    return os.geteuid() == 0


def run_as_admin():
    """osascriptでsudoを使って自分自身を管理者として再起動する"""
    script = (
        f'do shell script "python3 {sys.argv[0]}" '
        f'with administrator privileges'
    )
    try:
        subprocess.run(["osascript", "-e", script])
    except Exception:
        pass
    sys.exit()


def get_install_path(install_type: str) -> Path:
    """macOSのインストール先パスを返す"""
    if install_type == "user":
        # ~/Applications/ZundaQuake
        return Path.home() / "Applications" / APP_NAME
    else:
        # /Applications/ZundaQuake
        return Path("/Applications") / APP_NAME


def check_installed(install_type: str = None) -> Path | None:
    """インストール済みかチェックする"""
    for t in ("user", "all"):
        p = get_install_path(t) / UNINSTALL_INFO
        if p.exists():
            return get_install_path(t)
    return None


def add_to_dock(app_path: Path):
    """
    macOS の Dock に .app を追加する。
    PlistBuddy + killall Dock で永続的に追加。
    """
    app_bundle = app_path / f"{APP_NAME}.app"
    if not app_bundle.exists():
        return
    plist = Path.home() / "Library/Preferences/com.apple.dock.plist"
    entry = (
        f'<dict><key>tile-data</key><dict>'
        f'<key>file-data</key><dict>'
        f'<key>_CFURLString</key><string>{app_bundle}</string>'
        f'<key>_CFURLStringType</key><integer>0</integer>'
        f'</dict></dict>'
        f'<key>tile-type</key><string>file-tile</string></dict>'
    )
    try:
        subprocess.run(
            ["/usr/libexec/PlistBuddy", "-c",
             f"Add :persistent-apps: dict", str(plist)],
            capture_output=True
        )
        subprocess.run(["killall", "Dock"], capture_output=True)
    except Exception:
        pass


def register_login_item(app_path: Path):
    """
    macOS のログイン項目に登録するサンプル (osascript)。
    ここでは opt_launchpad の代替として使用。
    """
    app_bundle = app_path / f"{APP_NAME}.app"
    if not app_bundle.exists():
        return
    script = (
        f'tell application "System Events" to make login item '
        f'at end with properties {{path:"{app_bundle}", hidden:false}}'
    )
    try:
        subprocess.run(["osascript", "-e", script], capture_output=True)
    except Exception:
        pass


def save_uninstall_info(install_path: Path, install_type: str):
    """アンインストール情報をJSONで保存する"""
    info = {
        "app": APP_NAME,
        "version": APP_VERSION,
        "install_type": install_type,
        "install_path": str(install_path),
    }
    (install_path / UNINSTALL_INFO).write_text(
        json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ── メイン画面 ────────────────────────────────────────────────────

class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.lang_code    = "ja"
        self.t            = LANG[self.lang_code]
        self.install_type = tk.StringVar(value="user")
        self.opt_dock      = tk.BooleanVar(value=True)
        self.opt_launchpad = tk.BooleanVar(value=False)
        self.opt_website   = tk.BooleanVar(value=False)
        self.opt_launch    = tk.BooleanVar(value=True)
        self.install_path: Path | None = None
        self.existing_path: Path | None = check_installed()

        self.title(self.t["title"])
        self.resizable(False, False)
        self._center(WINDOW_W, WINDOW_H)
        self.configure(bg="#f0f0f0")

        # スタイル
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Sidebar.TFrame",  background="#1a3a5c")
        style.configure("Sidebar.TLabel",  background="#1a3a5c",
                        foreground="white", font=("Helvetica", 9))
        style.configure("Title.TLabel",    background="#1a3a5c",
                        foreground="white", font=("Helvetica", 14, "bold"))
        style.configure("Step.TLabel",     background="#1a3a5c",
                        foreground="#aac4e0", font=("Helvetica", 9))
        style.configure("ActiveStep.TLabel", background="#1a3a5c",
                        foreground="white", font=("Helvetica", 9, "bold"))
        style.configure("Header.TLabel",   background="white",
                        font=("Helvetica", 11, "bold"), foreground="#1a3a5c")
        style.configure("Body.TLabel",     background="white",
                        font=("Helvetica", 9), foreground="#333")
        style.configure("White.TFrame",    background="white")
        style.configure("Main.TFrame",     background="#f0f0f0")
        style.configure("Accent.TButton",  font=("Helvetica", 9, "bold"))
        style.configure("TRadiobutton",    background="white",
                        font=("Helvetica", 9))
        style.configure("TCheckbutton",    background="white",
                        font=("Helvetica", 9))
        style.configure("TProgressbar",    troughcolor="#ddd",
                        background="#1a3a5c", thickness=18)

        self._build_layout()

        # 最初のページ
        if self.existing_path:
            self._show_page("already")
        else:
            self._show_page("lang")

    def _center(self, w, h):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build_layout(self):
        self.outer = ttk.Frame(self, style="Main.TFrame")
        self.outer.pack(fill="both", expand=True)

        # サイドバー
        self.sidebar = ttk.Frame(self.outer, width=SIDEBAR_W, style="Sidebar.TFrame")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ttk.Label(self.sidebar, text=APP_NAME, style="Title.TLabel",
                  wraplength=SIDEBAR_W-20).pack(anchor="w", padx=16, pady=(28, 4))
        ttk.Label(self.sidebar, text=f"v{APP_VERSION}", style="Sidebar.TLabel"
                  ).pack(anchor="w", padx=16, pady=(0, 24))

        self.step_labels: dict[str, ttk.Label] = {}
        steps = [
            ("lang",         "1. 言語選択"),
            ("license",      "2. 使用許諾"),
            ("install_type", "3. インストール種類"),
            ("installing",   "4. インストール"),
            ("advanced",     "5. 詳細設定"),
            ("finish",       "6. 完了"),
        ]
        for key, text in steps:
            lbl = ttk.Label(self.sidebar, text=text, style="Step.TLabel",
                            wraplength=SIDEBAR_W-28)
            lbl.pack(anchor="w", padx=18, pady=3)
            self.step_labels[key] = lbl

        # コンテンツエリア
        self.content_frame = ttk.Frame(self.outer, style="White.TFrame")
        self.content_frame.pack(side="left", fill="both", expand=True)

    def _clear_content(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

    def _highlight_step(self, page_key: str):
        for k, lbl in self.step_labels.items():
            lbl.configure(style="ActiveStep.TLabel" if k == page_key
                          else "Step.TLabel")

    def _show_page(self, page: str):
        self._clear_content()
        self._highlight_step(page)
        getattr(self, f"_page_{page}")()

    # ── ページ: 言語選択 ──────────────────────────────────────────
    def _page_lang(self):
        t = self.t
        self._header(t["page_lang"], t["lang_select_label"])

        body = ttk.Frame(self.content_frame, style="White.TFrame")
        body.pack(fill="both", expand=True, padx=24, pady=8)

        lang_var = tk.StringVar(value=self.lang_code)
        langs = [
            ("日本語",                    "ja"),
            ("English(UK)",              "en-UK"),
            ("中文(臺灣)",                "zh-TW"),
            ("Español(América Latina)",  "es-LA"),
            ("한국어(한국)",               "ko-KR"),
        ]
        for label, code in langs:
            ttk.Radiobutton(body, text=label, variable=lang_var,
                            value=code, style="TRadiobutton"
                            ).pack(anchor="w", pady=4)

        def apply_lang():
            self.lang_code = lang_var.get()
            self.t = LANG[self.lang_code]
            self._show_page("license")

        self._footer(on_next=apply_lang, on_cancel=self.destroy)

    # ── ページ: 使用許諾 ──────────────────────────────────────────
    def _page_license(self):
        t = self.t
        self._header(t["page_license"], t["license_header"])

        body = ttk.Frame(self.content_frame, style="White.TFrame")
        body.pack(fill="both", expand=True, padx=24, pady=8)

        frame = ttk.Frame(body, style="White.TFrame")
        frame.pack(fill="both", expand=True)
        sb = tk.Scrollbar(frame)
        sb.pack(side="right", fill="y")
        txt = tk.Text(frame, yscrollcommand=sb.set, wrap="word",
                      font=("Helvetica", 9), relief="solid", bd=1,
                      bg="#fafafa", fg="#333", height=12)
        txt.insert("1.0", t["license_body"])
        txt.configure(state="disabled")
        txt.pack(side="left", fill="both", expand=True)
        sb.configure(command=txt.yview)

        agree_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(body, text=t["license_agree_check"],
                        variable=agree_var, style="TCheckbutton"
                        ).pack(anchor="w", pady=(8, 0))

        def on_next():
            if not agree_var.get():
                msg = {
                    "ja":    "使用許諾契約書に同意してください。",
                    "en-UK": "Please agree to the license agreement.",
                    "ko-KR": "사용 허가 계약서에 동의해 주시기 바랍니다.",
                    "zh-TW": "請同意授權合約條款。",
                    "es-LA": "Por favor, acepte el acuerdo de licencia.",
                }
                messagebox.showwarning(t["title"],
                    msg.get(self.lang_code, "Please agree to the license agreement."))
                return
            self._show_page("install_type")

        self._footer(on_next=on_next,
                     on_back=lambda: self._show_page("lang"),
                     on_cancel=self.destroy)

    # ── ページ: インストール種類 ──────────────────────────────────
    def _page_install_type(self):
        t = self.t
        self._header(t["page_install_type"], t["install_type_header"])

        body = ttk.Frame(self.content_frame, style="White.TFrame")
        body.pack(fill="both", expand=True, padx=24, pady=8)

        user = getpass.getuser()

        # ユーザーインストール (~/)
        f1 = ttk.Frame(body, style="White.TFrame", relief="groove", borderwidth=1)
        f1.pack(fill="x", pady=6)
        ttk.Radiobutton(f1, text=t["install_type_user"],
                        variable=self.install_type, value="user",
                        style="TRadiobutton"
                        ).pack(anchor="w", padx=12, pady=(8, 0))
        ttk.Label(f1, text=t["install_type_user_path"].format(user=user, app=APP_NAME),
                  style="Body.TLabel", foreground="#666"
                  ).pack(anchor="w", padx=28, pady=(0, 8))

        # 全ユーザー (/Applications)
        f2 = ttk.Frame(body, style="White.TFrame", relief="groove", borderwidth=1)
        f2.pack(fill="x", pady=6)
        ttk.Radiobutton(f2, text=t["install_type_all"],
                        variable=self.install_type, value="all",
                        style="TRadiobutton"
                        ).pack(anchor="w", padx=12, pady=(8, 0))
        ttk.Label(f2, text=t["install_type_all_path"].format(app=APP_NAME),
                  style="Body.TLabel", foreground="#666"
                  ).pack(anchor="w", padx=28, pady=(0, 8))

        def on_next():
            if self.install_type.get() == "all" and not is_admin():
                if messagebox.askyesno(t["title"], t["admin_required"]):
                    run_as_admin()
                return
            self.install_path = get_install_path(self.install_type.get())
            self._show_page("installing")

        self._footer(on_next=on_next,
                     on_back=lambda: self._show_page("license"),
                     on_cancel=self.destroy)

    # ── ページ: インストール中 ────────────────────────────────────
    def _page_installing(self):
        t = self.t
        self._header(t["page_installing"], "")

        body = ttk.Frame(self.content_frame, style="White.TFrame")
        body.pack(fill="both", expand=True, padx=24, pady=16)

        self.status_var   = tk.StringVar(value=t["downloading"])
        self.progress_var = tk.DoubleVar(value=0)

        ttk.Label(body, textvariable=self.status_var, style="Body.TLabel"
                  ).pack(anchor="w", pady=(0, 8))
        self.pbar = ttk.Progressbar(body, variable=self.progress_var,
                                    maximum=100, length=380)
        self.pbar.pack(fill="x")
        self.pct_lbl = ttk.Label(body, text="0%", style="Body.TLabel")
        self.pct_lbl.pack(anchor="e")

        self.detail_var = tk.StringVar(value="")
        ttk.Label(body, textvariable=self.detail_var,
                  style="Body.TLabel", foreground="#666",
                  wraplength=380
                  ).pack(anchor="w", pady=(12, 0))

        btn_frame = ttk.Frame(self.content_frame, style="White.TFrame")
        btn_frame.pack(fill="x", padx=24, pady=12)
        self._separator(self.content_frame)
        self.next_btn = ttk.Button(btn_frame, text=t["next"],
                                   state="disabled", style="Accent.TButton")
        self.next_btn.pack(side="right", padx=(6, 0))
        ttk.Button(btn_frame, text=t["cancel"],
                   command=self.destroy).pack(side="right")

        threading.Thread(target=self._do_install, daemon=True).start()

    def _update_progress(self, pct: float, status: str = None, detail: str = None):
        self.progress_var.set(pct)
        self.pct_lbl.configure(text=f"{int(pct)}%")
        if status:
            self.status_var.set(status)
        if detail is not None:
            self.detail_var.set(detail)

    def _do_install(self):
        t = self.t
        try:
            install_path = self.install_path
            install_path.mkdir(parents=True, exist_ok=True)

            n = len(DOWNLOAD_URLS)
            # ★ ZundaQuake4Mac.zip.001〜004
            part_paths = [
                install_path / f"ZundaQuake4Mac.zip.{i+1:03d}"
                for i in range(n)
            ]
            zip_path = install_path / "ZundaQuake4Mac.zip"

            # 1. 分割ファイルをダウンロード (0〜45%)
            for i, (url, part_path) in enumerate(zip(DOWNLOAD_URLS, part_paths)):
                prog_start = i / n * 45
                prog_end   = (i + 1) / n * 45
                self.after(0, self._update_progress, prog_start,
                           t["downloading"], url)
                self._download(url, part_path, prog_start, prog_end)

            # 2. 分割ファイルを結合 (45〜50%)
            total_size = sum(p.stat().st_size for p in part_paths)
            written = 0
            with open(zip_path, "wb") as out:
                for part_path in part_paths:
                    with open(part_path, "rb") as f:
                        while chunk := f.read(1024 * 1024):
                            out.write(chunk)
                            written += len(chunk)
                            pct = 45 + (written / total_size) * 5
                            self.after(0, self._update_progress, min(pct, 50),
                                       t["extracting"], part_path.name)
            for part_path in part_paths:
                part_path.unlink(missing_ok=True)

            # 3. 解凍 (50〜85%)
            self.after(0, self._update_progress, 50, t["extracting"],
                       str(zip_path))
            self._extract_zip(zip_path, install_path, prog_start=50, prog_end=85)
            zip_path.unlink(missing_ok=True)

            # 4. アンインストール情報を保存 (85〜92%)
            self.after(0, self._update_progress, 85, t["registering"])
            save_uninstall_info(install_path, self.install_type.get())

            # 5. macOS: .app に実行権限を付与 (92〜100%)
            self.after(0, self._update_progress, 92, t["registering"])
            app_bundle = install_path / f"{APP_NAME}.app"
            if app_bundle.exists():
                subprocess.run(
                    ["chmod", "-R", "755", str(app_bundle)],
                    capture_output=True
                )
                # Gatekeeper の隔離属性を除去 (署名なし配布時に必要)
                subprocess.run(
                    ["xattr", "-rd", "com.apple.quarantine", str(app_bundle)],
                    capture_output=True
                )

            self.after(0, self._update_progress, 100,
                       t["install_done"], "")
            self.after(0, self._on_install_success)

        except Exception as e:
            self.after(0, self._on_install_fail, str(e))

    def _download(self, url: str, dest: Path, prog_start: float, prog_end: float):
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                   "AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            with open(dest, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = prog_start + (downloaded / total) * (prog_end - prog_start)
                        self.after(0, self._update_progress, min(pct, prog_end),
                                   None, f"{min(downloaded, total):,} / {total:,} bytes")

    def _extract_zip(self, zip_path: Path, dest: Path,
                     prog_start: float = 50, prog_end: float = 85):
        def _try_extract(pwd=None):
            with zipfile.ZipFile(zip_path, "r") as zf:
                members = zf.infolist()
                total = len(members)
                for i, member in enumerate(members, 1):
                    zf.extract(member, dest, pwd=pwd)
                    pct = prog_start + (i / total) * (prog_end - prog_start)
                    self.after(0, self._update_progress, pct,
                               None, member.filename)

        try:
            _try_extract(pwd=None)
        except RuntimeError:
            _try_extract(pwd=ZIP_PASSWORD)
        except zipfile.BadZipFile:
            raise RuntimeError("ZIP ファイルが壊れているか、対応していない形式です。")

        # zip 内にサブフォルダが1つある場合、中身を dest に平坦化する
        entries = [p for p in dest.iterdir()
                   if p.name != zip_path.name and p.name != UNINSTALL_INFO]
        if len(entries) == 1 and entries[0].is_dir():
            sub = entries[0]
            for item in sub.iterdir():
                shutil.move(str(item), str(dest / item.name))
            sub.rmdir()

    def _on_install_success(self):
        self.next_btn.configure(
            state="normal",
            command=lambda: self._show_page("advanced")
        )

    def _on_install_fail(self, err: str):
        t = self.t
        self.status_var.set(t["install_failed"].format(error=err))
        self.detail_var.set("")
        messagebox.showerror(t["title"], t["install_failed"].format(error=err))

    # ── ページ: 詳細設定 ──────────────────────────────────────────
    def _page_advanced(self):
        t = self.t
        self._header(t["page_advanced"], t["advanced_header"])

        body = ttk.Frame(self.content_frame, style="White.TFrame")
        body.pack(fill="both", expand=True, padx=24, pady=8)

        # macOS固有: Dock / Launchpad（ログイン項目）/ 公式サイト
        checks = [
            (t["opt_dock"],      self.opt_dock),
            (t["opt_launchpad"], self.opt_launchpad),
            (t["opt_website"],   self.opt_website),
        ]
        for label, var in checks:
            ttk.Checkbutton(body, text=label, variable=var,
                            style="TCheckbutton").pack(anchor="w", pady=5)

        ttk.Label(body, text=f"    → {t['website_url']}",
                  style="Body.TLabel", foreground="#0066cc"
                  ).pack(anchor="w")

        ttk.Separator(body, orient="horizontal").pack(fill="x", pady=12)
        ttk.Checkbutton(body, text=t["launch_after"],
                        variable=self.opt_launch,
                        style="TCheckbutton").pack(anchor="w", pady=4)

        def on_next():
            if self.opt_dock.get():
                add_to_dock(self.install_path)
            if self.opt_launchpad.get():
                register_login_item(self.install_path)
            if self.opt_website.get():
                import webbrowser
                webbrowser.open(t["website_url"])
            self._show_page("finish")

        self._footer(on_next=on_next,
                     on_back=lambda: self._show_page("installing"),
                     on_cancel=self.destroy)

    # ── ページ: 完了 ──────────────────────────────────────────────
    def _page_finish(self):
        t = self.t
        self._highlight_step("finish")
        self._clear_content()

        body = ttk.Frame(self.content_frame, style="White.TFrame")
        body.pack(fill="both", expand=True, padx=24, pady=24)

        ttk.Label(body, text="✔", font=("Helvetica", 36),
                  foreground="#2e8b57", background="white"
                  ).pack(pady=(8, 0))
        ttk.Label(body, text=t["finish_title"], style="Header.TLabel"
                  ).pack(pady=(4, 8))
        ttk.Label(body, text=t["finish_body"], style="Body.TLabel",
                  wraplength=360, justify="center"
                  ).pack(pady=4)

        ttk.Checkbutton(body, text=t["launch_after"],
                        variable=self.opt_launch,
                        style="TCheckbutton").pack(pady=(16, 0))

        def on_finish():
            if self.opt_launch.get():
                app_bundle = self.install_path / f"{APP_NAME}.app"
                if app_bundle.exists():
                    subprocess.Popen(["open", str(app_bundle)])
                else:
                    # .app がない場合は直接バイナリを探す
                    exe = self.install_path / APP_NAME
                    if exe.exists():
                        subprocess.Popen([str(exe)])
            self.destroy()

        self._separator(self.content_frame)
        btn_frame = ttk.Frame(self.content_frame, style="White.TFrame")
        btn_frame.pack(fill="x", padx=24, pady=12)
        ttk.Button(btn_frame, text=t["finish"],
                   command=on_finish, style="Accent.TButton"
                   ).pack(side="right")

    # ── ページ: 既存インストール検出 ──────────────────────────────
    def _page_already(self):
        t = self.t
        self._highlight_step("lang")
        self._clear_content()

        body = ttk.Frame(self.content_frame, style="White.TFrame")
        body.pack(fill="both", expand=True, padx=24, pady=24)

        ttk.Label(body, text="⚠", font=("Helvetica", 32),
                  foreground="#e67e22", background="white"
                  ).pack(pady=(8, 0))
        ttk.Label(body, text=t["already_title"], style="Header.TLabel"
                  ).pack(pady=(4, 4))
        ttk.Label(body, text=t["already_body"], style="Body.TLabel",
                  wraplength=360, justify="center"
                  ).pack(pady=4)
        ttk.Label(body, text=str(self.existing_path),
                  style="Body.TLabel", foreground="#666"
                  ).pack(pady=(0, 16))

        btn_row = ttk.Frame(body, style="White.TFrame")
        btn_row.pack()
        ttk.Button(btn_row, text=t["uninstall"],
                   command=self._do_uninstall, width=16
                   ).pack(side="left", padx=6)
        ttk.Button(btn_row, text=t["reinstall"],
                   command=lambda: self._show_page("lang"),
                   width=16, style="Accent.TButton"
                   ).pack(side="left", padx=6)
        ttk.Button(btn_row, text=t["cancel"],
                   command=self.destroy, width=12
                   ).pack(side="left", padx=6)

    def _do_uninstall(self):
        t = self.t
        if not messagebox.askyesno(t["title"], t["uninstall_confirm"]):
            return
        try:
            path = self.existing_path
            # Dock からの削除 (PlistBuddy でエントリを検索して削除するのは複雑なため
            # ユーザーに案内するのみ)
            # ファイル削除
            shutil.rmtree(path, ignore_errors=True)
            messagebox.showinfo(t["title"], t["uninstall_done"])
            self.destroy()
        except Exception as e:
            messagebox.showerror(t["title"],
                                 t["uninstall_failed"].format(error=str(e)))

    # ── 共通ウィジェット ──────────────────────────────────────────
    def _header(self, title: str, subtitle: str):
        hf = ttk.Frame(self.content_frame, style="White.TFrame")
        hf.pack(fill="x", padx=24, pady=(20, 4))
        ttk.Label(hf, text=title, style="Header.TLabel").pack(anchor="w")
        if subtitle:
            ttk.Label(hf, text=subtitle, style="Body.TLabel",
                      wraplength=400).pack(anchor="w", pady=(2, 0))
        ttk.Separator(self.content_frame, orient="horizontal").pack(
            fill="x", padx=0, pady=(4, 0))

    def _separator(self, parent):
        ttk.Separator(parent, orient="horizontal").pack(fill="x")

    def _footer(self, on_next=None, on_back=None, on_cancel=None,
                next_text=None, cancel_text=None):
        t = self.t
        self._separator(self.content_frame)
        bf = ttk.Frame(self.content_frame, style="White.TFrame")
        bf.pack(fill="x", padx=24, pady=10)

        if on_cancel:
            ttk.Button(bf, text=cancel_text or t["cancel"],
                       command=on_cancel).pack(side="left")
        if on_next:
            ttk.Button(bf, text=next_text or t["next"],
                       command=on_next,
                       style="Accent.TButton").pack(side="right", padx=(6, 0))
        if on_back:
            ttk.Button(bf, text=t["back"],
                       command=on_back).pack(side="right")


# ── エントリポイント ──────────────────────────────────────────────

if __name__ == "__main__":

    # アップデート確認
    def check_update():
        try:
            req = urllib.request.Request(
                UPDATE_URL,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
            latest_version = data.get("latest", "").strip()
            if latest_version and latest_version != APP_VERSION:
                import webbrowser
                root = tk.Tk()
                root.withdraw()
                result = messagebox.askyesno(
                    "アップデート通知",
                    f"新しいバージョンがあります。\n\n"
                    f"現在: {APP_VERSION}\n"
                    f"最新: {latest_version}\n\n"
                    "Webサイトを開きますか?"
                )
                root.destroy()
                if result:
                    webbrowser.open(WEBSITE_URL)
        except Exception:
            pass  # ネットワーク不可時は無視

    check_update()

    # --uninstall オプション (macOS では /uninstall ではなく -- 形式を推奨)
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("--uninstall", "/uninstall"):
        root = tk.Tk()
        root.withdraw()
        existing = check_installed()
        if existing:
            t = LANG["ja"]
            if messagebox.askyesno(t["title"], t["uninstall_confirm"]):
                try:
                    shutil.rmtree(existing, ignore_errors=True)
                    messagebox.showinfo(t["title"], t["uninstall_done"])
                except Exception as e:
                    messagebox.showerror(t["title"],
                                         t["uninstall_failed"].format(error=str(e)))
        root.destroy()
        sys.exit()

    app = InstallerApp()
    app.mainloop()