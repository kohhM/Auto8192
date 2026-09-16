"""
<summary>
AutoHotkey.exeをsubprocessで直接呼び出し、レシピ(.ahk)を再生する。
</summary>
"""

import subprocess

import config


def recipe_path(stage: int):
    """
    <summary>
    現在のステージからこのレシピを実行して到達する先のステージ番号でファイル名が付けられている
    （例: 最初のマップ(stage=1)用のレシピは play0002.ahk = 実行後に"1/2"へ到達することが名前）。
    存在確認はしない。
    </summary>
    """
    target = stage * 2
    return config.AHK_DIR / f"play{target:04d}.ahk"


def play(stage: int) -> bool:
    """
    <summary>
    対応するahkファイルをAutoHotkey.exeで実行する。
    標準出力にDONEが含まれ、かつ終了コード0であれば成功とみなす。
    subprocess自体の失敗(AutoHotkey未起動など)も例外にせずFalseを返す。
    </summary>
    """
    path = recipe_path(stage)
    try:
        result = subprocess.run(
            [config.AHK_EXE, str(path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        stdout = (result.stdout or "").strip()
        print(f"[input_player] stage={stage} 実行完了 rc={result.returncode} stdout={stdout!r}")
        if result.returncode != 0:
            return False
        if "ERROR" in stdout:
            return False
        return True
    except Exception as e:
        print(f"[input_player] stage={stage} 実行失敗: {e}")
        return False
