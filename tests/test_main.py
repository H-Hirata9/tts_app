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


class TestListVoices:
    """--list-voices フラグのテスト。"""

    def test_prints_voice_ids(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["tts", "--list-voices"])

        main()

        out = capsys.readouterr().out
        assert "ja-JP-NanamiNeural" in out

    def test_list_en_voices(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["tts", "--language", "en", "--list-voices"])

        main()

        out = capsys.readouterr().out
        assert "en-US-" in out
        assert "ja-JP-" not in out

    def test_does_not_call_synthesize(self, mocker, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["tts", "--list-voices"])
        mock_syn = mocker.patch("tts_app.main.synthesize")

        main()

        mock_syn.assert_not_called()


class TestInputFile:
    """--input-file フラグのテスト。"""

    def test_creates_wav_per_line(self, mock_synthesize, monkeypatch, tmp_path):
        input_file = tmp_path / "input.txt"
        input_file.write_text("line1\nline2\nline3\n", encoding="utf-8")
        out_dir = tmp_path / "out"
        monkeypatch.setattr(
            sys,
            "argv",
            ["tts", "--input-file", str(input_file), "--output", str(out_dir)],
        )

        main()

        assert mock_synthesize.call_count == 3

    def test_output_filenames_are_sequential(
        self, mock_synthesize, monkeypatch, tmp_path
    ):
        input_file = tmp_path / "input.txt"
        input_file.write_text("first\nsecond\n", encoding="utf-8")
        out_dir = tmp_path / "out"
        monkeypatch.setattr(
            sys,
            "argv",
            ["tts", "--input-file", str(input_file), "--output", str(out_dir)],
        )

        main()

        paths = [call.args[2] for call in mock_synthesize.call_args_list]
        assert paths[0].endswith("1.wav")
        assert paths[1].endswith("2.wav")

    def test_skips_empty_lines(self, mock_synthesize, monkeypatch, tmp_path):
        input_file = tmp_path / "input.txt"
        input_file.write_text("line1\n\nline2\n\n", encoding="utf-8")
        out_dir = tmp_path / "out"
        monkeypatch.setattr(
            sys,
            "argv",
            ["tts", "--input-file", str(input_file), "--output", str(out_dir)],
        )

        main()

        assert mock_synthesize.call_count == 2

    def test_file_not_found_exits_with_1(self, monkeypatch):
        monkeypatch.setattr(
            sys, "argv", ["tts", "--input-file", "nonexistent.txt"]
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1

    def test_empty_file_exits_with_1(self, monkeypatch, tmp_path):
        input_file = tmp_path / "empty.txt"
        input_file.write_text("", encoding="utf-8")
        monkeypatch.setattr(
            sys, "argv", ["tts", "--input-file", str(input_file)]
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1

    def test_default_output_dir_is_output(self, mock_synthesize, monkeypatch, tmp_path):
        input_file = tmp_path / "input.txt"
        input_file.write_text("hello\n", encoding="utf-8")
        monkeypatch.setattr(
            sys, "argv", ["tts", "--input-file", str(input_file)]
        )
        monkeypatch.chdir(tmp_path)

        main()

        paths = [call.args[2] for call in mock_synthesize.call_args_list]
        assert "output" in paths[0]


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
