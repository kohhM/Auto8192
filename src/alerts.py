"""
<summary>
winsoundによる3種類の通知音。
</summary>
"""

import winsound


def alert_missing_recipe():
    """<summary>レシピ不在を知らせる(低音1回)。</summary>"""
    winsound.Beep(500, 400)


def alert_no_change():
    """<summary>実行しても分母が変化しなかったことを知らせる(中音2回)。想定外の例外もここに合流する。</summary>"""
    for _ in range(2):
        winsound.Beep(800, 250)


def alert_checkpoint_4096():
    """<summary>分母4096到達を知らせる(高音3回)。</summary>"""
    for _ in range(3):
        winsound.Beep(1200, 250)
