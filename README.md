# Azure TTS App

Azure AI Speech を使ったテキスト読み上げ（TTS）アプリです。
Streamlit による Web UI と CLI の両方に対応しています。

## Features

- 日本語・英語のテキストを音声に変換
- 各言語で複数のボイスを選択可能（DragonHD 高品質ボイス含む）
- ブラウザ上でそのまま再生
- WAV ファイルへの保存オプション
- CLI でのバッチ利用にも対応（テキストファイルから1行1ファイルで連続生成）

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv)
- Azure AI Speech リソース（HD ボイスを使う場合は `eastus` / `eastus2` など[対応リージョン](https://learn.microsoft.com/azure/ai-services/speech-service/regions)が必要）

## Installation

```bash
# リポジトリをクローン
git clone <repository-url>
cd tts_app

# 仮想環境を作成してパッケージをインストール
uv venv
uv pip install -e ".[dev]"

# 環境変数を設定
cp .env.example .env
# .env を編集して AZURE_SPEECH_KEY と AZURE_SPEECH_REGION を設定
```

## Configuration

`.env` ファイルに Azure のサブスクリプションキーとリージョンを設定します。

```env
AZURE_SPEECH_KEY=your_azure_speech_subscription_key_here
AZURE_SPEECH_REGION=eastus
```

> **Note:** DragonHD ボイスを使用する場合は `eastus`、`eastus2`、`westeurope` など
> HD voices 対応リージョンを指定してください。

## Usage

### Web UI (Streamlit)

```bash
.venv/Scripts/streamlit.exe run src/tts_app/app.py --server.headless true
# → http://localhost:8501 をブラウザで開く
```

または、インストール済みのスクリプトを使う場合:

```bash
tts-app
```

### CLI

```bash
# テキストを引数で渡す（デフォルトボイスで再生）
tts --language ja "こんにちは、世界"

# 音声を指定する
tts --language en --voice en-US-AriaNeural "Hello, world"

# WAV ファイルに保存する
tts --language ja --output output/hello.wav "こんにちは"

# インタラクティブ入力
tts --language ja

# 利用可能なボイス一覧を表示する
tts --language ja --list-voices
tts --language en --list-voices

# テキストファイルから1行ずつ音声ファイルを生成する
tts --language ja --input-file script.txt --output output/batch/
```

#### `--input-file` の動作

- テキストファイルの各行を1つの WAV ファイルに変換する
- 空行はスキップされる
- 出力ファイル名は連番（例: `01.wav`, `02.wav`, ...）
- `--output` でディレクトリを指定する（省略時は `output/` に保存）
- `--voice` でボイスを指定できる（省略時は言語のデフォルトボイス）

```
# script.txt の内容
こんにちは。
今日はいい天気ですね。
ありがとうございました。

# 出力: output/batch/1.wav, 2.wav, 3.wav
```

## Project Structure

```
tts_app/
├── src/
│   └── tts_app/
│       ├── __init__.py   # パッケージ初期化
│       ├── tts.py        # Azure TTS ラッパー・ボイス定義
│       ├── app.py        # Streamlit Web UI
│       ├── main.py       # CLI エントリポイント
│       └── run.py        # `tts-app` コマンドのランチャー
├── .env                  # 環境変数（Git 管理外）
├── .env.example          # 環境変数テンプレート
├── .gitignore
└── pyproject.toml        # プロジェクト設定・依存関係
```

## Available Voices

### 日本語 (ja)

| ボイス ID | 説明 |
|---|---|
| `ja-JP-NanamiNeural` | Nanami（女性） |
| `ja-JP-KeitaNeural` | Keita（男性） |
| `ja-JP-AoiNeural` | Aoi（女性） |
| `ja-JP-DaichiNeural` | Daichi（男性） |
| `ja-JP-MayuNeural` | Mayu（女性） |
| `ja-JP-ShioriNeural` | Shiori（女性） |
| `ja-JP-NaokiNeural` | Naoki（男性） |
| `ja-JP-Nanami:DragonHDLatestNeural` | Nanami HD（女性・高品質）※ |
| `ja-JP-Masaru:DragonHDLatestNeural` | Masaru HD（男性・高品質）※ |

### 英語 (en)

| ボイス ID | 説明 |
|---|---|
| `en-US-JennyNeural` | Jenny（女性） |
| `en-US-GuyNeural` | Guy（男性） |
| `en-US-AriaNeural` | Aria（女性） |
| `en-US-DavisNeural` | Davis（男性） |
| `en-US-EmmaNeural` | Emma（女性） |
| `en-US-AndrewNeural` | Andrew（男性） |
| `en-US-SaraNeural` | Sara（女性） |
| `en-US-TonyNeural` | Tony（男性） |
| `en-US-Ava:DragonHDLatestNeural` | Ava HD（女性・高品質）※ |
| `en-US-Andrew:DragonHDLatestNeural` | Andrew HD（男性・高品質）※ |

> ※ DragonHD ボイスは HD voices 対応リージョンでのみ利用可能です。

## Development

```bash
# コードスタイルチェック
uv run ruff check src/

# 自動修正
uv run ruff check --fix src/
```
