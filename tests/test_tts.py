"""tts.py のテスト。"""

import azure.cognitiveservices.speech as speechsdk
import pytest

from tts_app.tts import VOICES, synthesize


class TestVoices:
    """VOICES 定数のデータ構造テスト。"""

    def test_has_required_languages(self):
        assert "ja" in VOICES
        assert "en" in VOICES

    def test_entries_have_id_and_label(self):
        for voices in VOICES.values():
            for voice in voices:
                assert "id" in voice
                assert "label" in voice
                assert voice["id"] != ""
                assert voice["label"] != ""

    def test_id_prefix(self):
        for voice in VOICES["ja"]:
            assert voice["id"].startswith("ja-JP-")
        for voice in VOICES["en"]:
            assert voice["id"].startswith("en-US-")

    def test_labels_are_unique_per_language(self):
        for lang, voices in VOICES.items():
            labels = [v["label"] for v in voices]
            assert len(labels) == len(set(labels)), f"{lang}: ラベルが重複している"


@pytest.fixture
def mock_sdk(mocker):
    """Azure SDK の SpeechConfig / SpeechSynthesizer をモックするフィクスチャ。"""
    mock_result = mocker.MagicMock()
    mock_result.reason = speechsdk.ResultReason.SynthesizingAudioCompleted
    mock_result.audio_data = b"RIFF_fake_wav_data"

    mock_synth = mocker.MagicMock()
    mock_synth.speak_text_async.return_value.get.return_value = mock_result

    mocker.patch("tts_app.tts.speechsdk.SpeechConfig")
    mocker.patch("tts_app.tts.speechsdk.SpeechSynthesizer", return_value=mock_synth)

    return mock_synth, mock_result


class TestSynthesize:
    """synthesize() 関数のテスト。"""

    def test_returns_bytes(self, mock_sdk, monkeypatch):
        monkeypatch.setenv("AZURE_SPEECH_KEY", "dummy_key")
        monkeypatch.setenv("AZURE_SPEECH_REGION", "eastus")

        result = synthesize("テスト", "ja-JP-NanamiNeural")

        assert isinstance(result, bytes)
        assert result == b"RIFF_fake_wav_data"

    def test_uses_correct_voice(self, mocker, monkeypatch):
        monkeypatch.setenv("AZURE_SPEECH_KEY", "dummy_key")
        monkeypatch.setenv("AZURE_SPEECH_REGION", "eastus")

        mock_result = mocker.MagicMock()
        mock_result.reason = speechsdk.ResultReason.SynthesizingAudioCompleted
        mock_result.audio_data = b"data"
        mock_synth = mocker.MagicMock()
        mock_synth.speak_text_async.return_value.get.return_value = mock_result

        mock_config = mocker.MagicMock()
        mocker.patch("tts_app.tts.speechsdk.SpeechConfig", return_value=mock_config)
        mocker.patch("tts_app.tts.speechsdk.SpeechSynthesizer", return_value=mock_synth)

        synthesize("テスト", "ja-JP-NanamiNeural")

        assert mock_config.speech_synthesis_voice_name == "ja-JP-NanamiNeural"

    def test_saves_file_when_output_path_given(self, mock_sdk, monkeypatch, tmp_path):
        monkeypatch.setenv("AZURE_SPEECH_KEY", "dummy_key")
        monkeypatch.setenv("AZURE_SPEECH_REGION", "eastus")

        output_file = tmp_path / "output.wav"
        synthesize("テスト", "ja-JP-NanamiNeural", str(output_file))

        assert output_file.exists()
        assert output_file.read_bytes() == b"RIFF_fake_wav_data"

    def test_no_file_when_output_path_none(self, mock_sdk, monkeypatch, tmp_path):
        monkeypatch.setenv("AZURE_SPEECH_KEY", "dummy_key")
        monkeypatch.setenv("AZURE_SPEECH_REGION", "eastus")

        synthesize("テスト", "ja-JP-NanamiNeural", None)

        assert list(tmp_path.iterdir()) == []

    def test_raises_key_error_without_env(self, monkeypatch):
        monkeypatch.delenv("AZURE_SPEECH_KEY", raising=False)
        monkeypatch.delenv("AZURE_SPEECH_REGION", raising=False)

        with pytest.raises(KeyError):
            synthesize("テスト", "ja-JP-NanamiNeural")

    def test_raises_runtime_error_on_cancel(self, mocker, monkeypatch):
        monkeypatch.setenv("AZURE_SPEECH_KEY", "dummy_key")
        monkeypatch.setenv("AZURE_SPEECH_REGION", "eastus")

        mock_cancellation = mocker.MagicMock()
        mock_cancellation.reason = "Error"
        mock_cancellation.error_details = "Unsupported voice"

        mock_result = mocker.MagicMock()
        mock_result.reason = speechsdk.ResultReason.Canceled
        mock_result.cancellation_details = mock_cancellation

        mock_synth = mocker.MagicMock()
        mock_synth.speak_text_async.return_value.get.return_value = mock_result

        mocker.patch("tts_app.tts.speechsdk.SpeechConfig")
        mocker.patch("tts_app.tts.speechsdk.SpeechSynthesizer", return_value=mock_synth)

        with pytest.raises(RuntimeError, match="音声合成がキャンセルされました"):
            synthesize("テスト", "ja-JP-NanamiNeural")
