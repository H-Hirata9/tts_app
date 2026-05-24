"""run.py のテスト。"""

import sys

from tts_app.run import main


class TestRunMain:
    """main() 関数のテスト。"""

    def test_calls_streamlit_run(self, mocker, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["tts-app"])
        mock_call = mocker.patch("tts_app.run.subprocess.call", return_value=0)
        mock_exit = mocker.patch("tts_app.run.sys.exit")

        main()

        args = mock_call.call_args[0][0]
        assert args[0] == "streamlit"
        assert args[1] == "run"
        assert args[2].endswith("app.py")
        mock_exit.assert_called_once_with(0)

    def test_passes_additional_args(self, mocker, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["tts-app", "--server.port", "8502"])
        mock_call = mocker.patch("tts_app.run.subprocess.call", return_value=0)
        mocker.patch("tts_app.run.sys.exit")

        main()

        args = mock_call.call_args[0][0]
        assert "--server.port" in args
        assert "8502" in args

    def test_propagates_exit_code(self, mocker, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["tts-app"])
        mocker.patch("tts_app.run.subprocess.call", return_value=1)
        mock_exit = mocker.patch("tts_app.run.sys.exit")

        main()

        mock_exit.assert_called_once_with(1)
