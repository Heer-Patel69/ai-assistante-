import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import unified config
from config import MODEL_NAME, MODEL_OPTIONS

# Mock ollama if not available (for testing)
try:
    import ollama
except ImportError:
    st.error("Ollama is not installed. Please install it to use this app.")
    st.stop()

# Load system prompt
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read().strip()

# --- Page Config ---
st.set_page_config(
    page_title="UniVoid",
    page_icon="🧠",
    layout="centered"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #e0e0e0;
    }
    .stChatMessage {
        border-radius: 12px;
    }
    h1 {
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5em;
        text-align: center;
    }
    .subtitle {
        text-align: center;
        color: #888;
        margin-bottom: 2em;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("# 🧠 UniVoid")
st.markdown('<p class="subtitle">Your local AI assistant — 100% private, zero cloud</p>', unsafe_allow_html=True)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# --- Display Chat History ---
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🧠"):
        st.markdown(msg["content"])

# --- Chat Input ---
user_input = st.chat_input("Talk to UniVoid...")

if user_input:
    # Display user message
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get AI response
    with st.chat_message("assistant", avatar="🧠"):
        with st.spinner("Thinking..."):
            response = ollama.chat(
                model=MODEL_NAME,
                messages=st.session_state.messages,
                options=MODEL_OPTIONS
            )
            reply = response["message"]["content"]
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
