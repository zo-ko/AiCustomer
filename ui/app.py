import html
import sys
from pathlib import Path

# 将项目根目录加入 Python 路径，确保能导入 agent、rag 等模块
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st

from agent.react_agent import ReactAgent


def _get_agent() -> ReactAgent:
    """复用 Agent 单例，避免重复初始化。"""
    if "_agent" not in st.session_state:
        st.session_state._agent = ReactAgent()
    return st.session_state._agent


st.set_page_config(
    page_title="扫地机器人智能客服",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 扫地机器人智能客服")
st.caption("基于 ReAct + RAG 的 AI 客服助手，支持产品咨询、故障排查、保养建议与使用报告")

# ---------- 会话状态 ----------
if "messages" not in st.session_state:
    # 每条消息: {"role": "user" | "ai", "content": str}
    st.session_state.messages = []


# ---------- 样式 ----------
st.markdown(
    """
    <style>
    .chat-bubble-ai {
        background-color: #E3F2FD;
        padding: 12px 16px;
        border-radius: 16px;
        max-width: 80%;
        display: inline-block;
        text-align: left;
        word-wrap: break-word;
    }
    .chat-bubble-user {
        background-color: #DCF8C6;
        padding: 12px 16px;
        border-radius: 16px;
        max-width: 80%;
        display: inline-block;
        text-align: left;
        word-wrap: break-word;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- 历史对话（左右布局） ----------
for msg in st.session_state.messages:
    left, right = st.columns([1, 1])
    content_escaped = html.escape(msg["content"]).replace("\n", "<br>")

    if msg["role"] == "user":
        with right:
            st.markdown(
                f"<div style='text-align: right;'>"
                f"<span class='chat-bubble-user'><b>🧑 用户</b><br>{content_escaped}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        with left:
            st.markdown(
                f"<div style='text-align: left;'>"
                f"<span class='chat-bubble-ai'><b>🤖 AI</b><br>{content_escaped}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
    # 清除浮动，避免列高度不一致导致错位
    st.markdown("<div style='clear: both;'></div>", unsafe_allow_html=True)


# ---------- 输入区域 ----------
user_input = st.chat_input("请输入您的问题，例如：扫地机器人如何保养？")

if user_input:
    # 1) 即时显示用户消息（右侧）
    left, right = st.columns([1, 1])
    with right:
        user_escaped = html.escape(user_input).replace("\n", "<br>")
        st.markdown(
            f"<div style='text-align: right;'>"
            f"<span class='chat-bubble-user'><b>🧑 用户</b><br>{user_escaped}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
    st.markdown("<div style='clear: both;'></div>", unsafe_allow_html=True)

    # 2) 保存用户消息到历史
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 3) 流式输出 AI 回复（左侧）
    agent = _get_agent()
    left, right = st.columns([1, 1])
    with left:
        placeholder = st.empty()
        full_response = ""

        # execute_stream 在 stream_mode="values" 下每次 yield 的是当前完整内容快照，
        # 因此直接覆盖 placeholder 即可实现"打字机"效果。
        for chunk in agent.execute_stream(user_input):
            full_response = chunk.strip()
            response_escaped = html.escape(full_response).replace("\n", "<br>")
            placeholder.markdown(
                f"<div style='text-align: left;'>"
                f"<span class='chat-bubble-ai'><b>🤖 AI</b><br>{response_escaped}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # 4) 保存 AI 完整回复到历史
    st.session_state.messages.append({"role": "ai", "content": full_response})
