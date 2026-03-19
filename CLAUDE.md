# TTS_APP

## about
- TTSのAIをAPI呼び出すためのアプリ
- ユーザーが入力した自然言語を音声化する。
- 日本語と英語に対応
- AIはAzureを使う。

## language
- Python

## package management
- use uv
- use Virtual environment.

## Code Style
- PEP8
- check with ruff
- Docstring: Google スタイル（すべての public 関数・モジュールに記述）

## VCS
- Git / GitHub
- ブランチ戦略: GitHub Flow（シンプルな小規模向け）
  - `main`: 常にデプロイ可能な状態を保つ
  - 作業ブランチ: `feature/xxx`（機能追加）、`fix/xxx`（バグ修正）、`docs/xxx`（ドキュメント）
  - 作業ブランチは `main` から切り、完了後は Pull Request を経由して `main` にマージ
  - `main` への直接プッシュは禁止
- コミットメッセージ: Conventional Commits
  - フォーマット: `<type>(<scope>): <subject>`
  - 主なtype: `feat`（機能追加）, `fix`（バグ修正）, `docs`（ドキュメント）, `refactor`（リファクタ）, `chore`（雑務・設定変更）
  - 例: `feat(tts): add DragonHD voice support`
  - 例: `fix(app): resolve temp file permission error on Windows`
