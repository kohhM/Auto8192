"""
<summary>
エントリポイント。srcとプロジェクトルートをsys.pathに追加してorchestratorを起動する。
</summary>
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import orchestrator  # noqa: E402


if __name__ == "__main__":
    orchestrator.run()
