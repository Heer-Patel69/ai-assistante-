# 🧠 UniVoid — Local AI Desktop Assistant

A native desktop AI assistant powered by **Qwen3:4B** via [Ollama](https://ollama.com), with voice control, tool execution, and task planning.

**100% Local · No Cloud · Private**

## Architecture

```
User (Voice/Text)
    ↓
UniVoid Brain (System Prompt + Memory)
    ↓
Planner → Tool Selector → Executor
    ↓
Streaming Response → Voice Reply
```

## Features

- 🖥️ **Desktop Window** — Native always-on-top chat (customtkinter)
- ⚡ **Token Streaming** — See responses as they generate (feels 3× faster)
- 🎙️ **Voice Input** — Push-to-talk via Whisper (offline STT)
- 🔊 **Voice Output** — AI talks back (toggleable)
- ⌨️ **Hotkey** — `Ctrl+Space` to show/hide window
- 🧠 **Agent Brain** — System prompt + conversation memory
- 📋 **Planner** — Breaks complex tasks into steps
- 🔧 **Auto Tool Selection** — AI picks the right tool
- 🔒 **Sandbox** — File ops default to `AI_WORKSPACE/`

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install ollama pyautogui requests
pip install faster-whisper sounddevice scipy pyttsx3
pip install langchain-community streamlit python-docx
pip install customtkinter keyboard
```

**Prerequisites:**
- [Ollama](https://ollama.com) installed and running
- `ollama pull qwen3:4b`

## Usage

### Desktop App (Recommended)
```bash
python desktop_app.py
```

### Terminal Mode
```bash
python main.py
```

### Web UI (Streamlit)
```bash
streamlit run app.py
```

## Project Structure

```
ai-assistant/
├── desktop_app.py       # 🖥️ Native desktop chat window
├── agent.py             # 🧠 Core brain (models loaded once)
├── main.py              # Terminal agent loop
├── app.py               # Streamlit web UI
├── tools.py             # 10 tools + auto-selection registry
├── planner.py           # Step-by-step task planner
├── system_prompt.txt    # UniVoid personality
├── voice_input.py       # Whisper STT
├── voice_output.py      # pyttsx3 TTS
├── AI_WORKSPACE/        # 🔒 Sandbox
├── venv/
└── README.md
```

## Performance

- Whisper: `base` (int8, ~1GB RAM)
- Qwen3: 4B (~3GB RAM)
- Total: ~6–7GB RAM
- Expected latency: Whisper 1–2s → LLM 2–6s → TTS 1s
