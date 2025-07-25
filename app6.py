# ターミナルで以下を実行
# streamlit run C:\Users\soich\PycharmProjects\langchain\app.py
import os
import random
import streamlit as st
from dotenv import load_dotenv
from agents import get_agent_by_role, ROLE_PROMPTS
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 各役割に固有のLLMインスタンスを保持する辞書
llm_models = {
    "司会者": ChatOpenAI(api_key=api_key, temperature=0.5, model="gpt-4"),
    "批判者": ChatOpenAI(api_key=api_key, temperature=0.8, model="gpt-4"),
    "指導者": ChatOpenAI(api_key=api_key, temperature=0.6, model="gpt-4-turbo-preview"),
    "楽観的な提案者": ChatOpenAI(api_key=api_key, temperature=0.9, model="gpt-3.5-turbo"),
    "批判的分析者": ChatOpenAI(api_key=api_key, temperature=0.7, model="gpt-4"),
}

if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "next_speaker" not in st.session_state:
    st.session_state.next_speaker = None
if "last_speaker" not in st.session_state:
    st.session_state.last_speaker = None


st.title("役割付きAIとグループディスカッション")

# 議題を表示する
if st.session_state.topic:
    st.markdown(f"**議題: {st.session_state.topic}**")

# 議題がまだ入力されていない場合の処理
if st.session_state.topic == "":
    def set_topic():
        st.session_state.topic = st.session_state.topic_input
        st.session_state.next_speaker = None
        st.session_state.last_speaker = None
        st.rerun()

    st.text_input(
        "議題を入力してください",
        key="topic_input",
        on_change=set_topic
    )
    st.stop()


# --- 議題入力後の通常フロー ---

participants = list(ROLE_PROMPTS.keys()) + ["人間"]

# チャットUIとして会話履歴を表示 (先頭に移動)
for entry in st.session_state.chat_log:
    display_role = entry["role"]
    chat_role = "user" if display_role == "人間" else "assistant"
    with st.chat_message(chat_role):
        st.markdown(f"**{display_role}**：{entry['message']}")

st.markdown(f"### 次の発言者: **{st.session_state.next_speaker if st.session_state.next_speaker else '準備中...'}**")


# 次の発言者が人間の場合はst.chat_inputを表示
if st.session_state.next_speaker == "人間":
    user_input = st.chat_input("あなたの発言を入力してください")
    if user_input: # ユーザーが何か入力した場合
        st.session_state.chat_log.append({"role": "人間", "message": user_input})
        st.session_state.last_speaker = "人間"
        st.session_state.next_speaker = None
        st.rerun()
# 次の発言者がAIの場合
else:
    # next_speakerがまだ決定されていない場合は決定する
    if st.session_state.next_speaker is None:
        available_participants = [p for p in participants if p != st.session_state.last_speaker]
        # 初回はlast_speakerがNoneなので、全員からランダム選択
        if not available_participants: # 全員発言済みの場合の考慮（実際には起こりにくいが念のため）
             available_participants = participants
        st.session_state.next_speaker = random.choice(available_participants)
        # 次の発言者を決めたら、自動で再実行してAIの発言に移る
        st.rerun()
    else:
        role = st.session_state.next_speaker
        history = [HumanMessage(content=msg["message"]) if msg["role"] == "人間"
                   else SystemMessage(content=f"{msg['role']}：{msg['message']}")
                   for msg in st.session_state.chat_log]

        current_llm_for_role = llm_models[role]
        agent = get_agent_by_role(role, current_llm_for_role)

        # AIの応答生成とチャットログへの追加
        response = agent(history, st.session_state.topic)
        st.session_state.chat_log.append({"role": role, "message": response})
        st.session_state.last_speaker = role
        st.session_state.next_speaker = None
        st.rerun()

st.divider()

# この部分は既に上記で移動済みのため、削除またはコメントアウト
# for entry in st.session_state.chat_log:
#     display_role = entry["role"]
#     if display_role == "人間":
#         chat_role = "user"
#     else:
#         chat_role = "assistant"
#
#     with st.chat_message(chat_role):
#         st.markdown(f"**{display_role}**：{entry['message']}")