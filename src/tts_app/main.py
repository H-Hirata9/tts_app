import argparse
import sys

from dotenv import load_dotenv

load_dotenv()

from tts_app.tts import VOICES, synthesize  # noqa: E402

_DEFAULT_VOICE = {lang: voices[0]["id"] for lang, voices in VOICES.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Azure TTS CLI")
    parser.add_argument(
        "-l", "--language",
        default="ja",
        choices=list(VOICES.keys()),
        help="言語コード (デフォルト: ja)",
    )
    parser.add_argument(
        "-v", "--voice",
        metavar="VOICE_ID",
        help="音声ID (省略時は各言語のデフォルト音声)",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="WAVファイルの保存先パス (省略時はスピーカー再生)",
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="読み上げるテキスト (省略時はインタラクティブ入力)",
    )
    args = parser.parse_args()

    text = args.text
    if not text:
        text = input("テキストを入力してください: ").strip()
        if not text:
            print("テキストが空です。", file=sys.stderr)
            sys.exit(1)

    voice = args.voice or _DEFAULT_VOICE[args.language]

    try:
        synthesize(text, voice, args.output)
    except KeyError as e:
        print(f"環境変数が設定されていません: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
