"""
<summary>
テンプレートマッチングで現在のステージ(分母)を判定する。
</summary>
"""

import time

import cv2
import numpy as np

import config
import capture


def _imread_unicode(path) -> np.ndarray | None:
    """
    <summary>
    cv2.imreadは非ASCII(日本語等)パスをうまく扱えないため、
    ファイルをバイト列で読んでcv2.imdecodeする方式で代替する。
    </summary>
    """
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
        return cv2.imdecode(data, cv2.IMREAD_COLOR)
    except Exception:
        return None


def load_templates() -> dict:
    """
    <summary>
    config.TEMPLATES_DIR から {N}.png (N in config.VALID_STAGES, ただしN=1除く) を読み込む。
    stage=1(最初のマップ、文字表示なし)はテンプレート画像を使わず、明るいピクセルの有無で判定するため対象外。
    見つからないテンプレートはスキップし、警告を表示する(存在チェックはキャリブレーション時にユーザーが行う)。
    </summary>
    """
    templates = {}
    for stage in config.VALID_STAGES:
        if stage == 1:
            continue
        path = config.TEMPLATES_DIR / f"{stage}.png"
        if not path.exists():
            print(f"[stage_detect] テンプレート未作成: {path}")
            continue
        img = _imread_unicode(path)
        if img is None:
            print(f"[stage_detect] テンプレート読み込み失敗: {path}")
            continue
        templates[stage] = img
    return templates


def _has_bright_text(frame: np.ndarray) -> bool:
    """
    <summary>
    分母の数字は明るい白文字で表示されるため、明るいピクセルがある程度の数あるかで文字の有無を判定する。
    背景のちらつき等のノイズより数字表示の方が明らかに明るいため、テンプレートマッチングより安定する。
    </summary>
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    bright_count = int((gray > config.BRIGHT_TEXT_THRESHOLD).sum())
    return bright_count >= config.BRIGHT_TEXT_MIN_PIXELS


def detect_stage(frame: np.ndarray, templates: dict) -> int | None:
    """
    <summary>
    明るいピクセルが無ければ最初のマップ(stage=1)と判定する。
    あればtemplatesと照合し、閾値を超える最良一致のステージ番号を返す。無ければNone。
    </summary>
    """
    if not _has_bright_text(frame):
        return 1

    best_stage = None
    best_score = config.TEMPLATE_MATCH_THRESHOLD
    for stage, template in templates.items():
        if template.shape[0] > frame.shape[0] or template.shape[1] > frame.shape[1]:
            continue
        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        _, score, _, _ = cv2.minMaxLoc(result)
        if score > best_score:
            best_score = score
            best_stage = stage
    return best_stage


def wait_for_stage_change(
    prior_stage: int | None,
    templates: dict,
    timeout_sec: float = None,
    require_change: bool = True,
) -> int | None:
    """
    <summary>
    ステージを確信を持って読み取れるまでポーリングする。
    require_change=Trueの場合はprior_stageと異なる値のみを受理する。
    require_change=Falseの場合はprior_stageと同じ値でも(Noneでなければ)受理する
    (死亡すると必ず最初のマップ(stage=1)に戻るため、stage=1発の遷移では
    「死んで1に戻った」ことと「入力が効かず1のまま」が区別できないための救済措置)。
    実際の表示にはラグがあるため、ポーリング開始前に一定時間待つ。
    timeout_sec以内に受理できなければNoneを返す(呼び出し側で「変化なし」として扱う)。
    </summary>
    """
    if timeout_sec is None:
        timeout_sec = config.STAGE_CHANGE_TIMEOUT_SEC

    time.sleep(config.STAGE_CHANGE_SETTLE_DELAY_SEC)

    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        frame = capture.grab_region()
        stage = detect_stage(frame, templates)
        if stage is not None and (require_change is False or stage != prior_stage):
            return stage
        time.sleep(config.DETECT_POLL_INTERVAL_SEC)
    return None
