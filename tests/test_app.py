"""app.py (Streamlit UI) のテスト。"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

_APP_FILE = str(Path(__file__).parent.parent / "src" / "tts_app" / "app.py")


@pytest.fixture(autouse=True)
def azure_env(monkeypatch):
    """Azure 認証情報のダミー環境変数を設定するフィクスチャ。"""
    monkeypatch.setenv("AZURE_SPEECH_KEY", "dummy_key")
    monkeypatch.setenv("AZURE_SPEECH_REGION", "japaneast")


class TestPageLoad:
    """ページ読み込みのテスト。"""

    def test_loads_without_exception(self):
        at = AppTest.from_file(_APP_FILE)
        at.run()
        assert not at.exception


class TestEmptyInput:
    """テキスト未入力時のテスト。"""

    def test_empty_text_shows_error(self):
        at = AppTest.from_file(_APP_FILE)
        at.run()
        at.button[0].click().run()
        assert any("テキストを入力してください" in e.value for e in at.error)


class TestSynthesisSuccess:
    """音声合成成功時のテスト。"""

    def test_no_exception_on_success(self, mocker):
        mocker.patch("tts_app.tts.synthesize", return_value=b"RIFF_fake_wav")
        at = AppTest.from_file(_APP_FILE)
        at.run()
        at.text_area[0].input("テスト音声")
        at.button[0].click().run()
        assert not at.exception

    def test_no_error_on_success(self, mocker):
        mocker.patch("tts_app.tts.synthesize", return_value=b"RIFF_fake_wav")
        at = AppTest.from_file(_APP_FILE)
        at.run()
        at.text_area[0].input("テスト音声")
        at.button[0].click().run()
        assert len(at.error) == 0


class TestErrorHandling:
    """エラーハンドリングのテスト。"""

    def test_key_error_shows_env_error_message(self, mocker):
        mocker.patch(
            "tts_app.tts.synthesize",
            side_effect=KeyError("AZURE_SPEECH_KEY"),
        )
        at = AppTest.from_file(_APP_FILE)
        at.run()
        at.text_area[0].input("テスト")
        at.button[0].click().run()
        assert any("環境変数が設定されていません" in e.value for e in at.error)

    def test_runtime_error_shows_error_message(self, mocker):
        mocker.patch(
            "tts_app.tts.synthesize",
            side_effect=RuntimeError("合成失敗"),
        )
        at = AppTest.from_file(_APP_FILE)
        at.run()
        at.text_area[0].input("テスト")
        at.button[0].click().run()
        assert any("合成失敗" in e.value for e in at.error)
