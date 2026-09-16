"""
<summary>
ゲームウィンドウを検出し、その相対位置に基づいて分母表示領域をキャプチャする。
ウィンドウの位置・サイズが変わっても比率で追従する。
</summary>
"""

import numpy as np
import mss
import win32gui

import config


def _find_game_window() -> int:
    """<summary>タイトルにconfig.GAME_WINDOW_TITLEを含む可視ウィンドウのhwndを返す。</summary>"""
    found = []

    def callback(hwnd, _):
        try:
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if config.GAME_WINDOW_TITLE in title:
                    found.append(hwnd)
        except Exception:
            pass
        return True

    win32gui.EnumWindows(callback, None)
    if not found:
        raise RuntimeError(
            f"ゲームウィンドウが見つかりません(タイトルに'{config.GAME_WINDOW_TITLE}'を含むウィンドウがありません)"
        )
    return found[0]


def _game_window_rect():
    """
    <summary>
    ゲームの「クライアント領域」(タイトルバーやDWMの見えない境界線を含まない、実際の描画部分)の
    (left, top, width, height)をスクリーン座標で返す。
    GetWindowRectはDWMの見えない境界線を含んで実際の描画領域よりも大きい値を返すため使わない。
    </summary>
    """
    hwnd = _find_game_window()
    _, _, width, height = win32gui.GetClientRect(hwnd)
    left, top = win32gui.ClientToScreen(hwnd, (0, 0))
    return left, top, width, height


def grab_region() -> np.ndarray:
    """<summary>分母表示領域をキャプチャしBGR画像として返す。</summary>"""
    try:
        wx, wy, ww, wh = _game_window_rect()
        frac = config.CAPTURE_REGION_FRACTION
        left = wx + int(ww * frac["left"])
        top = wy + int(wh * frac["top"])
        width = int(ww * (frac["right"] - frac["left"]))
        height = int(wh * (frac["bottom"] - frac["top"]))
        region = {"left": left, "top": top, "width": width, "height": height}

        with mss.mss() as sct:
            shot = sct.grab(region)
            # mssはBGRA形式で返すのでBGRに変換
            frame = np.array(shot)[:, :, :3]
            return frame
    except Exception as e:
        print(f"[capture] キャプチャ失敗: {e}")
        raise
