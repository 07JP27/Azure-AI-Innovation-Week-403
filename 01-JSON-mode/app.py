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

# Azure OpenAIへの接続情報を設定する。
base = os.getenv('AOAI_ENDPOINT')
deployment = os.getenv('AOAI_DEPLOYMENT')
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
class TicketReservationRequest(BaseModel):
    dept: str
    dest: str
    dept_date: str
    return_date: str
    adult_ticket_count: int
    child_ticket_count: int
    note: str


# 値を動的にバインドするためのセッションステートを作成する。
if 'form' not in st.session_state:
    st.session_state.form = TicketReservationRequest(
        dept="",
        dest="",
        dept_date="",
        return_date="",
        adult_ticket_count=0,
        child_ticket_count=0,
        note=""
    )

# クリップボードから値を読み取り、フォームにセットする関数を定義する。
def parse_clipboard():
    with st.spinner('解析中'):
        try:
            clipboard_content = pyperclip.paste()
            if not clipboard_content:
                st.error("クリップボードが空です。")
                return
            completion = client.beta.chat.completions.parse(
                model=deployment,
                temperature=0,
                messages=[
                    {"role": "system", "content": """
                        ユーザの入力から各項目のJSONに変換してください。JSONのスキーマは以下の通りです。日付はYYYY/MM/DD形式に変換してください。年が含まれていない場合は2024年として扱ってください。
                        dept: 出発地
                        dest: 目的地
                        dept_date: 出発日
                        return_date: 帰着日
                        adult_ticket_count: 大人のチケット枚数
                        child_ticket_count: 子供のチケット枚数
                        note: 特に注意すべきことや連絡事項。すでに上記の項目に含まれている情報は不要です。
                    """},
                    {"role": "user", "content": clipboard_content},
                ],
                response_format=TicketReservationRequest  # 【ポイント!】
            )
            parsed = completion.choices[0].message.parsed
            st.session_state.form.dept = parsed.dept
            st.session_state.form.dest = parsed.dest
            st.session_state.form.dept_date = parsed.dept_date
            st.session_state.form.return_date = parsed.return_date
            st.session_state.form.adult_ticket_count = parsed.adult_ticket_count
            st.session_state.form.child_ticket_count = parsed.child_ticket_count
            st.session_state.form.note = parsed.note
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# タイトルを表示する。
st.markdown("### Azure OpenAI JSON mode サンプル")
st.markdown("チケット手配フォームの自動入力")
st.divider()

# 入力フォームを表示する。
col11, col12, col13, col14 = st.columns(4)
col11.text_input("出発日", value=st.session_state.form.dept_date, key='form_dept_date')
col12.text_input("帰着日", value=st.session_state.form.return_date, key='form_return_date')
col13.text_input("出発地", value=st.session_state.form.dept, key='form_dept')
col14.text_input("目的地", value=st.session_state.form.dest, key='form_dest')

col21, col22 = st.columns(2)
col21.number_input("大人", value=st.session_state.form.adult_ticket_count, key='form_adult_ticket_count')
col22.number_input("子供", value=st.session_state.form.child_ticket_count, key='form_child_ticket_count')
st.text_input("連絡事項", value=st.session_state.form.note, key='form_note')

st.divider()

col31, col32 = st.columns(2)
col31.button("クリップボードから解析", key='parse_clipboard', use_container_width=True, type='primary', on_click=parse_clipboard)
col32.button("送信", key='submit', use_container_width=True, type='primary')

# サンプル文面
# お世話になっております。以下のチケットの予約をお願いしたいと思っています。
# ・出発地: 東京
# ・目的地: 沖縄
# ・旅行日程: １２月24日〜2025/１／５
# ・人数: 大人４、子供１
# 
# もしおすすめのフライトやお得なプランがあれば、ぜひ教えてください。
# 両親と行くのですが、母が基本的には車椅子での移動になります。
# また、その他に必要な情報があればお知らせください。
# お手数をおかけしますが、よろしくお願いします。
