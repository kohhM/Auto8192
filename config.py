"""
<summary>
プロジェクト全体で使う定数(キャプチャ領域・タイムアウト・パス)。
</summary>
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

AHK_EXE = r"C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
AHK_DIR = PROJECT_ROOT / "ahk"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

# ゲームウィンドウ検索用(タイトルにこの文字列を含むウィンドウを探す)
GAME_WINDOW_TITLE = "L8192"

# 分母表示領域を、ゲームのクライアント領域に対する比率で指定する。
# ウィンドウの位置・サイズが変わっても比率なので追従する。
# 重要: テンプレート画像(300x55相当)より一回り広く取ること。同じサイズだとcv2.matchTemplateが
# 位置をスライドして探せず(探索の自由度がゼロになる)、1ピクセルのズレにも極端に弱くなる。
# 実機検証: このサイズだと"1/2"のスコアが0.97まで改善(狭い領域では0.20程度しか出なかった)。
CAPTURE_REGION_FRACTION = {"left": 600 / 1600, "top": 800 / 900, "right": 1000 / 1600, "bottom": 1.0}

# レシピ実行後、分母の変化を待つ最大秒数。表示ラグの実測値に合わせて調整する。
STAGE_CHANGE_TIMEOUT_SEC = 5.0

# レシピ実行完了後、実際に新しい表示が描画されるまでの表示ラグを考慮し、
# 判定ポーリングを始める前にこの秒数だけ待つ。
STAGE_CHANGE_SETTLE_DELAY_SEC = 1.0

# DETECTのポーリング間隔
DETECT_POLL_INTERVAL_SEC = 0.2

# テンプレートマッチングの一致とみなす閾値(0.0-1.0)
TEMPLATE_MATCH_THRESHOLD = 0.85

# 最初のマップ(stage=1、分数表示なし)判定用: この輝度を超えるピクセルを「明るい」とみなす
BRIGHT_TEXT_THRESHOLD = 200
# 「明るい」ピクセルがこの数以上あれば数字が表示されていると判定する
BRIGHT_TEXT_MIN_PIXELS = 20

# 有効なステージ値。1 = 最初のマップ(分数表示なし)、それ以外は分母の値。
VALID_STAGES = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]

# 4096到達で自動化を打ち切る境界値
MANUAL_CHECKPOINT_STAGE = 4096

RESUME_COMMAND = "/start"
