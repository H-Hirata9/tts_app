import os

import azure.cognitiveservices.speech as speechsdk

VOICES: dict[str, list[dict[str, str]]] = {
    "ja": [
        {"id": "ja-JP-NanamiNeural", "label": "Nanami（女性）"},
        {"id": "ja-JP-KeitaNeural", "label": "Keita（男性）"},
        {"id": "ja-JP-AoiNeural", "label": "Aoi（女性）"},
        {"id": "ja-JP-DaichiNeural", "label": "Daichi（男性）"},
        {"id": "ja-JP-MayuNeural", "label": "Mayu（女性）"},
        {"id": "ja-JP-ShioriNeural", "label": "Shiori（女性）"},
        {"id": "ja-JP-NaokiNeural", "label": "Naoki（男性）"},
        {"id": "ja-JP-Nanami:DragonHDLatestNeural", "label": "Nanami HD（女性・高品質）"},
        {"id": "ja-JP-Masaru:DragonHDLatestNeural", "label": "Masaru HD（男性・高品質）"},
    ],
    "en": [
        {"id": "en-US-JennyNeural", "label": "Jenny（女性）"},
        {"id": "en-US-GuyNeural", "label": "Guy（男性）"},
        {"id": "en-US-AriaNeural", "label": "Aria（女性）"},
        {"id": "en-US-DavisNeural", "label": "Davis（男性）"},
        {"id": "en-US-EmmaNeural", "label": "Emma（女性）"},
        {"id": "en-US-AndrewNeural", "label": "Andrew（男性）"},
        {"id": "en-US-SaraNeural", "label": "Sara（女性）"},
        {"id": "en-US-TonyNeural", "label": "Tony（男性）"},
        {"id": "en-US-Ava:DragonHDLatestNeural", "label": "Ava HD（女性・高品質）"},
        {"id": "en-US-Andrew:DragonHDLatestNeural", "label": "Andrew HD（男性・高品質）"},
    ],
}


def synthesize(text: str, voice: str, output_path: str | None = None) -> bytes:
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
