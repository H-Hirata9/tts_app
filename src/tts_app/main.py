"""Azure TTS CLI エントリポイント。

コマンドライン引数を解析し、テキストを音声合成する。
"""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from tts_app.tts import VOICES, synthesize  # noqa: E402

_DEFAULT_VOICE = {lang: voices[0]["id"] for lang, voices in VOICES.items()}


def _list_voices(language: str) -> None:
    """指定言語のボイス一覧を標準出力に表示する。

    Args:
        language: 言語コード ("ja" または "en")
    """
    for voice in VOICES[language]:
        print(f"{voice['id']}\t{voice['label']}")


def _process_file(input_file: str, voice: str, output_dir: str) -> None:
    """テキストファイルを1行ずつ音声合成してディレクトリに保存する。

    空行はスキップする。ファイル名は行番号の連番 (例: 01.wav, 02.wav)。

    Args:
        input_file: 読み込むテキストファイルのパス
        voice: 使用するボイスID
        output_dir: WAVファイルの保存先ディレクトリ

    Raises:
        SystemExit: ファイルが存在しない、空、またはAzureエラー時
    """
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"ファイルが見つかりません: {input_file}", file=sys.stderr)
        sys.exit(1)

    lines = [
        line.strip()
        for line in input_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not lines:
        print("テキストファイルが空です。", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    width = len(str(len(lines)))
    for i, line in enumerate(lines, 1):
        filename = f"{str(i).zfill(width)}.wav"
        output_path = out_dir / filename
        try:
            synthesize(line, voice, str(output_path))
            print(f"[{i}/{len(lines)}] {filename}: {line[:50]}")
        except KeyError as e:
            print(f"環境変数が設定されていません: {e}", file=sys.stderr)
            sys.exit(1)
        except RuntimeError as e:
            print(f"エラー: {e}", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    """CLI のメインエントリポイント。

    コマンドライン引数を解析し、指定されたテキストを音声合成する。
    テキストが省略された場合は標準入力から対話的に受け取る。
    エラー発生時は非ゼロの終了コードで終了する。
    """
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
        metavar="PATH",
        help="出力先パス。テキスト入力時はWAVファイル、--input-file 使用時はディレクトリ",
    )
    parser.add_argument(
        "-f", "--input-file",
        metavar="FILE",
        help="テキストファイルパス。1行につき1つのWAVファイルを生成する",
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="指定言語のボイス一覧を表示して終了",
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="読み上げるテキスト (省略時はインタラクティブ入力)",
    )
    args = parser.parse_args()

    if args.list_voices:
        _list_voices(args.language)
        return

    voice = args.voice or _DEFAULT_VOICE[args.language]

    if args.input_file:
        _process_file(args.input_file, voice, args.output or "output")
        return

    text = args.text
    if not text:
        text = input("テキストを入力してください: ").strip()
        if not text:
            print("テキストが空です。", file=sys.stderr)
            sys.exit(1)

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
