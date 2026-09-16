"""
<summary>
メインの状態遷移ループ。DETECT -> (4096ゲート) -> LOOKUP -> EXECUTE -> VERIFY を繰り返す。
想定外の例外が起きてもプロセスは落とさず、alert_no_changeと同じ一時停止経路に合流させる。
</summary>
"""

import time

import config
import capture
import stage_detect
import input_player
import alerts


def _wait_for_resume():
    """<summary>コンソールで/startが入力されるまでブロックする。</summary>"""
    print(f"[orchestrator] 一時停止中。再開するには {config.RESUME_COMMAND} と入力してEnterを押してください。")
    while True:
        try:
            line = input().strip()
        except EOFError:
            # 標準入力が閉じている場合の暴走スピンを避ける
            time.sleep(1)
            continue
        if line == config.RESUME_COMMAND:
            print("[orchestrator] 再開します。")
            return


def run():
    """<summary>ボットのメインループ。Ctrl+Cで終了する。</summary>"""
    templates = stage_detect.load_templates()
    if not templates:
        print("[orchestrator] テンプレートが1つも読み込めませんでした。templates/ を確認してください。")
        return

    prior_stage = None
    print("[orchestrator] 自動運転を開始します。終了するにはCtrl+Cを押してください。")

    while True:
        try:
            frame = capture.grab_region()
            stage = stage_detect.detect_stage(frame, templates)

            if stage is None:
                # 検知失敗は「変化なし」経路に合流させる(4つ目のアラート種別は作らない)
                print("[orchestrator] ステージを検知できませんでした。")
                alerts.alert_no_change()
                _wait_for_resume()
                continue

            if stage != prior_stage:
                print(f"[orchestrator] 現在のステージ: {stage}")

            if stage == config.MANUAL_CHECKPOINT_STAGE:
                print(f"[orchestrator] 分母{config.MANUAL_CHECKPOINT_STAGE}に到達しました。ここから先は手動でプレイしてください。")
                alerts.alert_checkpoint_4096()
                _wait_for_resume()
                prior_stage = None
                continue

            recipe = input_player.recipe_path(stage)
            if not recipe.exists():
                print(f"[orchestrator] レシピが見つかりません: {recipe}")
                alerts.alert_missing_recipe()
                _wait_for_resume()
                prior_stage = None
                continue

            success = input_player.play(stage)
            if not success:
                print(f"[orchestrator] レシピ実行に失敗しました(stage={stage})。")
                alerts.alert_no_change()
                _wait_for_resume()
                prior_stage = None
                continue

            # stage=1(最初のマップ)は死亡すると必ず1に戻るため、1→1も正常な結果として受理する
            new_stage = stage_detect.wait_for_stage_change(
                stage, templates, require_change=(stage != 1)
            )
            if new_stage is None:
                print(f"[orchestrator] stage={stage} 実行後、分母が変化しませんでした。")
                alerts.alert_no_change()
                _wait_for_resume()
                prior_stage = None
                continue

            print(f"[orchestrator] stage={stage} -> {new_stage}")
            prior_stage = new_stage

        except KeyboardInterrupt:
            print("[orchestrator] 終了します。")
            return
        except Exception as e:
            # 想定外の例外でプロセスを落とさない
            print(f"[orchestrator] 想定外のエラー: {e}")
            alerts.alert_no_change()
            _wait_for_resume()
            prior_stage = None
