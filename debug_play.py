"""
<summary>
デバッグ用ツール。3秒待ってから指定したahkファイルを実行する。
待っている間にゲームウィンドウにフォーカスを合わせる/観察の準備をする時間として使う。
デバッグ対象を変えたい場合は引数のファイル名を変えるだけでよい。
</summary>

使い方:
    python debug_play.py play0002.ahk
    python debug_play.py _test_one_mode.ahk Input L8192   (追加引数はそのままahkに渡す)
"""

import sys
import time
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import config


def main():
    if len(sys.argv) < 2:
        print("使い方: python debug_play.py <ahkファイル名(ahk/フォルダ内)> [追加引数...]")
        return

    target = sys.argv[1]
    extra_args = sys.argv[2:]
    path = config.AHK_DIR / target
    if not path.exists():
        print(f"[debug_play] ファイルが見つかりません: {path}")
        return

    print(f"[debug_play] 3秒後に {target} を実行します。ゲームウィンドウを見てください...")
    for i in range(3, 0, -1):
        print(i)
        time.sleep(1)

    try:
        result = subprocess.run(
            [config.AHK_EXE, str(path), *extra_args],
            capture_output=True,
            text=True,
            timeout=30,
        )
        print(f"[debug_play] 実行完了 rc={result.returncode} stdout={result.stdout.strip()!r} stderr={result.stderr.strip()!r}")
    except Exception as e:
        print(f"[debug_play] 実行失敗: {e}")


if __name__ == "__main__":
    main()
