import os
import streamlit as st
import pyperclip
from openai import AzureOpenAI
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from pydantic import BaseModel

# 環境変数をロードする
load_dotenv()

# ページタイトルとアイコンを設定する。
st.set_page_config(page_title="AOAI JSON modeサンプル", page_icon="🧾", layout="wide")

# Azure OpenAIへの接続情報を設定する。※適宜編集してください
base = os.getenv('AOAI_ENDPOINT')
deployment = os.getenv('AOAI_DPLOYMENT')
api_version = os.getenv('AOAI_API_VERSION')  # 2024-08-01-preview以上にする必要あり

# Entra ID認証を使うように設定
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

# Azure OpenAIのクライアントを作成する。
client = AzureOpenAI(
    azure_endpoint=base,
    azure_ad_token_provider=token_provider,
    api_version=api_version
)


# 構造として出力してほしいスキーマのモデル
class TiketReservationRequest(BaseModel):
    dept: str
    deptDate: str
    dest: str
    adultTicketCount: int
    childTicketCount: int
    note: str


# 【ポイント！】値を動的にバインドするためのセッションステートを作成する。
if 'form' not in st.session_state:
    st.session_state.form = TiketReservationRequest(
        dept="",
        deptDate="",
        dest="",
        adultTicketCount=0,
        childTicketCount=0,
        note=""
    )

# クリップボードから値を読み取り、st.session_state.form.noteにセットする関数を定義する。
def parse_clipboard():
    with st.spinner('解析中'):
        try:
            clipboard_content = pyperclip.paste()
            if not clipboard_content:
                st.error("クリップボードが空です。")
                return
            completion = client.beta.chat.completions.parse(  # 【ポイント！】
                model=deployment,
                messages=[
                    {"role": "system", "content": """
                        ユーザの入力から各項目のJSONに変換してください。JSONのスキーマは以下の通りです。日付はYYYY/MM/DD形式に変換してください。年が含まれていない場合は2024年として扱ってください。
                        dept:出発地
                        deptDate:出発地
                        dest:目的地
                        adultTicketCount:大人のチケット枚数
                        childTicketCount:子供のチケット枚数
                        note:特に注意すべきことや連絡事項。すでに上記の項目に含まれている情報は不要です。
                    """},
                    {"role": "user", "content": clipboard_content},
                ],
                response_format=TiketReservationRequest  # 【ポイント！】
            )
            parsed = completion.choices[0].message.parsed
            st.session_state.form.dept = parsed.dept
            st.session_state.form.deptDate = parsed.deptDate
            st.session_state.form.dest = parsed.dest
            st.session_state.form.adultTicketCount = parsed.adultTicketCount
            st.session_state.form.childTicketCount = parsed.childTicketCount
            st.session_state.form.note = parsed.note
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# タイトルを表示する。
st.markdown("### Azure OpenAI JSON mode サンプル")
st.markdown("チケット手配フォームの自動入力")
st.divider()

# 入力フォームを表示する。
col1, col2, col3 = st.columns(3)
col1.text_input("出発日", value=st.session_state.form.deptDate, key='form_deptDate')
col2.text_input("出発地", value=st.session_state.form.dept, key='form_dept')
col3.text_input("目的地", value=st.session_state.form.dest, key='form_dest')

col4, col5 = st.columns(2)
col4.number_input("大人", value=st.session_state.form.adultTicketCount, key='form_adultTicketCount')
col5.number_input("子供", value=st.session_state.form.childTicketCount, key='form_childTicketCount')
st.text_input("連絡事項", value=st.session_state.form.note, key='form_note')

st.divider()

col6, col7 = st.columns(2)
col6.button("クリップボードから解析", key='parse_clipboard', use_container_width=True, type='primary', on_click=parse_clipboard)
col7.button("送信", key='submit', use_container_width=True, type='primary')

# サンプル文面 
#お世話になっております。以下のチケットの予約をお願いしたいと思っています。
#・出発地: 東京
#・目的地: 沖縄
#・旅行日程: １２月24日〜2025/１／５
#・人数: 大人４、子供１
            
#もしおすすめのフライトやお得なプランがあれば、ぜひ教えてください。
#両親と行くのですが、母が基本的には車椅子での移動になります。     
#また、その他に必要な情報があればお知らせください。
#お手数をおかけしますが、よろしくお願いします。
