import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

# --- 1. 配置 AI 模型 ---
# 设置环境变量以对接通义千问 API
os.environ["OPENAI_API_KEY"] = "sk-ab40d0805e144392a106254d5c8bf540"
os.environ["OPENAI_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 初始化模型：使用 qwen-plus
llm = ChatOpenAI(
    model="qwen-plus",
    streaming=True  # 开启流式传输
)

# --- 2. 页面设置 ---
st.set_page_config(page_title="通义千问 AI 助手", page_icon="☁️")
st.title("🤖 你的专属 AI 助手")
st.caption("基于 LangChain + Streamlit + 通义千问")

# --- 3. 管理对话历史 ---
# Streamlit 每次交互都会重跑代码，session_state 用于持久化存储数据
if "messages" not in st.session_state:
    st.session_state.messages = []

# 在页面上渲染之前的聊天记录
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# --- 4. 处理用户输入 ---
if prompt := st.chat_input("说点什么吧..."):
    # 1. 展示并保存用户输入
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append(HumanMessage(content=prompt))

    # 2. 调用 AI 生成回答
    with st.chat_message("assistant"):
        # 创建一个空占位符，用于放置流式输出的内容
        response_placeholder = st.empty()
        full_response = ""

        # 使用 stream 方法获取数据流
        for chunk in llm.stream(st.session_state.messages):
            # chunk.content 是当前收到的文本片段
            full_response += chunk.content
            # 实时刷新占位符的内容
            response_placeholder.markdown(full_response + "▌")

        # 结束后显示最终完整内容
        response_placeholder.markdown(full_response)

    # 3. 保存 AI 回答到历史记录
    st.session_state.messages.append(AIMessage(content=full_response))
