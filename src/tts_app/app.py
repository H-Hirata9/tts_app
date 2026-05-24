"""Streamlit による Azure TTS Web UI モジュール。

言語・ボイスの選択、テキスト入力、音声合成・再生・保存機能を提供する。
"""

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from tts_app.tts import VOICES, synthesize  # noqa: E402

st.set_page_config(page_title="Azure TTS App", page_icon="🔊", layout="centered")
st.title("🔊 Azure TTS App")
st.caption("Azure AI Speech を使ったテキスト読み上げアプリ")

language = st.selectbox(
    "言語",
    options=["ja", "en"],
    format_func=lambda x: "🇯🇵 日本語" if x == "ja" else "🇺🇸 English",
)

voice_options = VOICES[language]
voice_labels = [v["label"] for v in voice_options]
voice_ids = [v["id"] for v in voice_options]

selected_label = st.selectbox("音声", options=voice_labels)
selected_voice = voice_ids[voice_labels.index(selected_label)]

text = st.text_area(
    "テキスト",
    placeholder="読み上げるテキストを入力してください",
    height=150,
)

with st.expander("保存オプション"):
    output_path = st.text_input(
        "WAV保存先パス（省略可）",
        placeholder="output/result.wav",
    )

if st.button("🎙️ 音声合成", type="primary", use_container_width=True):
    if not text.strip():
        st.error("テキストを入力してください")
    else:
        with st.spinner("音声合成中..."):
            try:
                save_path = output_path.strip() if output_path.strip() else None
                if save_path:
                    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                audio_bytes = synthesize(text, selected_voice, save_path)
                st.audio(audio_bytes, format="audio/wav")
                if save_path:
                    st.success(f"保存しました: {save_path}")
            except ValueError as e:
                st.error(f"エラー: {e}")
            except KeyError as e:
                st.error(f"環境変数が設定されていません: {e}")
            except RuntimeError as e:
                st.error(f"エラー: {e}")
