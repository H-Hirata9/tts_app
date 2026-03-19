"""main.py (CLI) のテスト。"""

import sys

import pytest

from tts_app.main import main
from tts_app.tts import VOICES

_DEFAULT_JA_VOICE = VOICES["ja"][0]["id"]
_DEFAULT_EN_VOICE = VOICES["en"][0]["id"]


@pytest.fixture
def mock_synthesize(mocker):
    """synthesize() をモックするフィクスチャ。"""
    return mocker.patch("tts_app.main.synthesize", return_value=b"fake_audio")


class TestMainArguments:
    """CLI 引数のパーステスト。"""

    def test_text_argument(self, mock_synthesize, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["tts", "こんにちは"])

        main()

        mock_synthesize.assert_called_once_with(
            "こんにちは", _DEFAULT_JA_VOICE, None
        )

    def test_language_en_uses_default_en_voice(self, mock_synthesize, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["tts", "--language", "en", "Hello"])

        main()

        mock_synthesize.assert_called_once_with("Hello", _DEFAULT_EN_VOICE, None)

    def test_explicit_voice(self, mock_synthesize, monkeypatch):
        monkeypatch.setattr(
            sys, "argv", ["tts", "--voice", "en-US-AriaNeural", "Hello"]
        )

        main()

        mock_synthesize.assert_called_once_with("Hello", "en-US-AriaNeural", None)

    def test_output_path(self, mock_synthesize, monkeypatch, tmp_path):
        out = str(tmp_path / "out.wav")
        monkeypatch.setattr(sys, "argv", ["tts", "--output", out, "テスト"])

        main()

        mock_synthesize.assert_called_once_with("テスト", _DEFAULT_JA_VOICE, out)


class TestMainInteractiveInput:
    """インタラクティブ入力のテスト。"""

    def test_interactive_input(self, mock_synthesize, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["tts"])
        monkeypatch.setattr("builtins.input", lambda _: "インタラクティブ入力")

        main()

        mock_synthesize.assert_called_once_with(
            "インタラクティブ入力", _DEFAULT_JA_VOICE, None
        )

    def test_empty_interactive_input_exits_with_1(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["tts"])
        monkeypatch.setattr("builtins.input", lambda _: "")

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1


class TestMainErrorHandling:
    """エラーハンドリングのテスト。"""

    def test_key_error_exits_with_1(self, mocker, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["tts", "テスト"])
        mocker.patch(
            "tts_app.main.synthesize", side_effect=KeyError("AZURE_SPEECH_KEY")
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1

    def test_runtime_error_exits_with_1(self, mocker, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["tts", "テスト"])
        mocker.patch("tts_app.main.synthesize", side_effect=RuntimeError("合成失敗"))

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1

    def test_error_message_printed_to_stderr(self, mocker, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["tts", "テスト"])
        mocker.patch("tts_app.main.synthesize", side_effect=RuntimeError("合成失敗"))

        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "合成失敗" in captured.err
