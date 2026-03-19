"""``tts-app`` コマンドのランチャーモジュール。

Streamlit アプリを subprocess 経由で起動する。
"""

import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Streamlit アプリを起動するエントリポイント。

    ``tts-app`` コマンドの実体。``streamlit run app.py`` を subprocess で呼び出す。
    追加の CLI 引数はそのまま streamlit に渡される。
    """
    app_path = Path(__file__).parent / "app.py"
    sys.exit(subprocess.call(["streamlit", "run", str(app_path)] + sys.argv[1:]))
