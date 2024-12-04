import json
import os
import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import prompty
import prompty.azure

# 環境変数をロードする
load_dotenv()

# Azure OpenAIへの接続情報を設定する。
base = os.getenv('AOAI_ENDPOINT')
deployment = os.getenv('AOAI_DEPLOYMENT')
api_version = os.getenv('AOAI_API_VERSION')

# Managed IDでのトークン取得
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    azure_endpoint=base,
    azure_ad_token_provider=token_provider,
    api_version=api_version
)

# ページタイトルとアイコンを設定する。
st.set_page_config(page_title="Custom ChatGPT", page_icon="💬", layout="wide")

# タイトルを表示する。
st.markdown("# Propmty サンプル")

# Promptyの読み込みと変数の設定
st.sidebar.markdown("# セットアップ")
user_name = st.sidebar.text_input("あなたの名前")
if st.sidebar.button("Clear chat & Set name"):
    prompt = prompty.load("./template.prompty")
    st.session_state.messages = prompty.prepare(prompt, {"userName": user_name})

# チャットログを保存したセッション情報を初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

if prompt := st.chat_input("What is up?"):
    # 以前のチャットログを表示
    for chat in st.session_state.messages:
        if chat["role"] == "system":
            with st.expander("システムプロンプト"):
                st.write(chat["content"])
        else:
            with st.chat_message(chat["role"]):
                st.write(chat["content"])

    # 最新の���ッセージを表示
    with st.chat_message("user"):
        st.write(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model=deployment,
        messages=st.session_state.messages,
        stream=True,
        temperature=0,
    )

    with st.chat_message("assistant"):
        assistant_msg = ""
        assistant_response_area = st.empty()
        for chunk in response:
            if len(chunk.choices) == 0:
                continue

            if chunk.choices[0].finish_reason == "stop":
                break

            # 回答を逐次表示
            assistant_msg += chunk.choices[0].delta.content
            assistant_response_area.write(assistant_msg)

    st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
