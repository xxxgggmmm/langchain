import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

# --- 1. 直接配置模型（不走 os.environ） ---
# 请确保在 Streamlit Cloud 的 Secrets 设置里已经填好了这两个变量
try:
    llm = ChatOpenAI(
        model="qwen-plus", 
        openai_api_key=st.secrets["OPENAI_API_KEY"], 
        openai_api_base=st.secrets["OPENAI_BASE_URL"],
        streaming=True
    )
except Exception as e:
    st.error("密钥配置错误，请检查 Streamlit Secrets 设置")
    st.stop()

# --- 2. 界面设置 ---
st.title("🤖 我的 AI 助手")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

if prompt := st.chat_input("输入问题..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append(HumanMessage(content=prompt))

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        # 加上 error 处理，防止接口调用失败
        try:
            for chunk in llm.stream(st.session_state.messages):
                full_response += chunk.content
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
            st.session_state.messages.append(AIMessage(content=full_response))
        except Exception as e:
            st.error(f"调用接口时出错: {e}")
