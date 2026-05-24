"""Azure AI Speech を使ったテキスト読み上げ（TTS）モジュール。

利用可能なボイス一覧と音声合成関数を提供する。
"""

import os
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk
import yaml

_MAX_CHARS = 10_000

_VOICES_FILE = Path(__file__).parent / "voices.yaml"

with _VOICES_FILE.open(encoding="utf-8") as _f:
    VOICES: dict[str, list[dict[str, str]]] = yaml.safe_load(_f)


def synthesize(text: str, voice: str, output_path: str | None = None) -> bytes:
    """テキストを音声に変換し、WAV バイト列を返す。

    Azure AI Speech を使って指定ボイスでテキストを読み上げ合成する。
    音声データはメモリ上に取得するため一時ファイルは使用しない。

    Args:
        text: 読み上げるテキスト。
        voice: 使用するボイスの ID（例: ``ja-JP-NanamiNeural``）。
        output_path: WAV ファイルの保存先パス。指定した場合はファイルにも保存する。
            ``None`` の場合は保存しない。

    Returns:
        合成した音声データの WAV バイト列。

    Raises:
        ValueError: テキストが ``_MAX_CHARS`` 文字を超える場合。
        KeyError: 環境変数 ``AZURE_SPEECH_KEY`` または ``AZURE_SPEECH_REGION``
            が設定されていない場合。
        RuntimeError: Azure Speech サービスが音声合成をキャンセルした場合。
    """
    if len(text) > _MAX_CHARS:
        raise ValueError(
            f"テキストが長すぎます ({len(text)} 文字)。"
            f"上限は {_MAX_CHARS} 文字です。"
        )

    speech_key = os.environ["AZURE_SPEECH_KEY"]
    speech_region = os.environ["AZURE_SPEECH_REGION"]

    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=speech_region
    )
    speech_config.speech_synthesis_voice_name = voice

    # audio_config=None にすることでファイルを介さずメモリ上で音声データを取得
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=None
    )

    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        raise RuntimeError(
            f"音声合成がキャンセルされました: {cancellation.reason}, "
            f"詳細: {cancellation.error_details}"
        )

    audio_bytes = result.audio_data

    if output_path:
        with open(output_path, "wb") as f:
            f.write(audio_bytes)

    return audio_bytes
