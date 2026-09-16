"""
<summary>
生スクリーンショットから分母表示部分の明るいテキスト領域を自動検出してトリミングし、
templates/{ステージ番号}.png として保存する。

使い方:
    python make_template.py <入力画像パス> <ステージ番号>
    例: python make_template.py templates/2new.png 2

入力ファイルと出力ファイルが同じパスになっても安全なよう、画像は先に全てメモリへ読み込んでから書き込む。
</summary>
"""

import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import config

# 検出したバウンディングボックスに加える余白(ピクセル)。
# 大きすぎるとちらつく背景を比例的に多く含んでしまいマッチスコアが下がるため、実測に基づき小さめにしている。
PADDING_X = 10
PADDING_Y = 3
# 連結成分の面積がこれ未満ならノイズ(画面端の点や小さな反射など)とみなして無視する。
# 実際の文字ストロークは面積250以上あるのに対し、ノイズは数十程度だった実測に基づく。
MIN_BLOB_AREA = 100


def _imread_unicode(path) -> np.ndarray | None:
    """<summary>日本語パス対応の画像読み込み。</summary>"""
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
        return cv2.imdecode(data, cv2.IMREAD_COLOR)
    except Exception:
        return None


def _imwrite_unicode(path, img) -> None:
    """<summary>日本語パス対応の画像書き込み。</summary>"""
    ext = Path(path).suffix or ".png"
    ok, buf = cv2.imencode(ext, img)
    if not ok:
        raise RuntimeError(f"画像のエンコードに失敗しました: {path}")
    buf.tofile(str(path))


def make_template(input_path: Path, stage: int) -> Path:
    """<summary>入力画像から分母表示部分をトリミングしてtemplates/{stage}.pngへ保存する。</summary>"""
    img = _imread_unicode(input_path)
    if img is None:
        raise RuntimeError(f"画像を読み込めませんでした: {input_path}")

    h, w = img.shape[:2]

    # 探索範囲は画像全体ではなく、実行時のキャプチャ領域(config.CAPTURE_REGION_FRACTION)と
    # 同じ範囲(中央付近)に限定する。画像全体を探索すると、ランタン等テキストから離れた位置にある
    # 明るい光源まで拾ってしまい、境界がテキストと光源の両方を含む形に広がってしまうことが判明したため。
    frac = config.CAPTURE_REGION_FRACTION
    sx0 = int(w * frac["left"])
    sx1 = int(w * frac["right"])
    sy0 = int(h * frac["top"])
    sy1 = int(h * frac["bottom"])
    search_region = img[sy0:sy1, sx0:sx1]

    gray = cv2.cvtColor(search_region, cv2.COLOR_BGR2GRAY)
    mask = (gray > config.BRIGHT_TEXT_THRESHOLD).astype(np.uint8)

    # 連結成分解析でノイズ(画面端の1ピクセルなど孤立した点)を除外し、
    # ある程度まとまった大きさのある成分(文字のストローク)だけを対象にする。
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    valid = [i for i in range(1, num_labels) if stats[i, cv2.CC_STAT_AREA] >= MIN_BLOB_AREA]
    if not valid:
        raise RuntimeError(
            "明るいテキスト領域が見つかりませんでした。"
            "config.BRIGHT_TEXT_THRESHOLDや入力画像(数字が写っているか)を確認してください。"
        )

    x0 = min(stats[i, cv2.CC_STAT_LEFT] for i in valid) + sx0
    y0 = min(stats[i, cv2.CC_STAT_TOP] for i in valid) + sy0
    x1 = max(stats[i, cv2.CC_STAT_LEFT] + stats[i, cv2.CC_STAT_WIDTH] for i in valid) + sx0
    y1 = max(stats[i, cv2.CC_STAT_TOP] + stats[i, cv2.CC_STAT_HEIGHT] for i in valid) + sy0

    x0 = max(0, x0 - PADDING_X)
    x1 = min(w, x1 + PADDING_X)
    y0 = max(0, y0 - PADDING_Y)
    y1 = min(h, y1 + PADDING_Y)

    crop = img[y0:y1, x0:x1].copy()

    output_path = config.TEMPLATES_DIR / f"{stage}.png"
    _imwrite_unicode(output_path, crop)
    print(f"[make_template] {input_path} -> {output_path} ({crop.shape[1]}x{crop.shape[0]})")
    return output_path


def main():
    if len(sys.argv) != 3:
        print("使い方: python make_template.py <入力画像パス> <ステージ番号>")
        return

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"[make_template] 入力ファイルが見つかりません: {input_path}")
        return

    try:
        stage = int(sys.argv[2])
    except ValueError:
        print(f"[make_template] ステージ番号は整数で指定してください: {sys.argv[2]}")
        return

    try:
        make_template(input_path, stage)
    except Exception as e:
        print(f"[make_template] 失敗: {e}")


if __name__ == "__main__":
    main()
