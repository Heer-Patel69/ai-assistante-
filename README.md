# 🧠 UniVoid — Your Local AI Assistant

A powerful, fully local AI assistant running **qwen3:4b** via [Ollama](https://ollama.com) with GPU acceleration, web search, document creation, and voice control.

**100% Local · No Cloud · Fully Private**

---

## 🚀 Quick Start

### 1. Install Prerequisites

**Python 3.8+**
- Download from [python.org](https://www.python.org/downloads/)

**Ollama**
- Download from [ollama.com](https://ollama.com)
- Install and ensure it's running

### 2. Clone & Install

```bash
# Clone the repository
git clone https://github.com/Heer-Patel69/ai-assistante-.git
cd ai-assistante-

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Pull the AI Model

```bash
ollama pull qwen3:4b
```

### 4. Run UniVoid

**Option A: Desktop App (Recommended)**
```bash
python desktop_app.py
```

**Option B: Terminal/CLI Mode**
```bash
python main.py
```

**Option C: Web Interface**
```bash
streamlit run app.py
```

---

## ✨ Features

### 🛠️ 7 Powerful Tools
- **terminal_executor** — Run shell commands safely
- **file_manager** — Create, read, edit, delete files
- **web_search** — Search the internet (DuckDuckGo)
- **document_creator** — Create txt, md, html, py, docx files
- **app_opener** — Launch apps and URLs
- **system_info** — Monitor CPU, RAM, disk, processes
- **memory_store** — Remember user preferences

### 🎯 Key Capabilities
- ⚡ **GPU Accelerated** — All model layers on GPU for maximum speed
- 🌐 **Web Search** — Real-time information from the internet
- 📄 **Document Creation** — Generate formatted documents
- 🎙️ **Voice Control** — Speak your commands (desktop app)
- 🔊 **Voice Output** — Hear responses (desktop app)
- ⌨️ **Hotkey** — `Ctrl+Space` to toggle window (desktop app)
- 🧠 **Persistent Memory** — Remembers your preferences
- 🔒 **Safe Execution** — Blocklist prevents dangerous commands

### 🎨 Multiple Interfaces
- **Desktop App** — Native GUI with always-on-top window
- **CLI Mode** — Terminal-based interaction
- **Web UI** — Browser-based interface (Streamlit)

---

## 📋 System Requirements

### Minimum
- **CPU**: Multi-core processor (4+ cores recommended)
- **RAM**: 8 GB
- **GPU**: Optional but recommended (NVIDIA with 4GB+ VRAM)
- **Storage**: 5 GB free space
- **OS**: Windows 10+, Linux, or macOS

### Recommended (Optimized For)
- **CPU**: AMD Ryzen 5 5600H or better
- **RAM**: 8 GB
- **GPU**: NVIDIA RTX 3050 Ti (4GB VRAM) or better
- **Storage**: 10 GB free space

---

## 📁 Project Structure

```
ai-assistante-/
├── config.py              # Centralized configuration
├── agent_loop.py          # Single-model agent with tool execution
├── tools_core.py          # 7 unified tools
├── main.py                # CLI entry point
├── desktop_app.py         # Desktop GUI
├── app.py                 # Streamlit web UI
├── system_prompt.txt      # UniVoid personality
├── memory.py              # Persistent memory system
├── voice_input.py         # Speech recognition
├── voice_output.py        # Text-to-speech
├── requirements.txt       # Python dependencies
├── AI_WORKSPACE/          # Default workspace for files
└── memory.json            # Stored memories
```

---

## ⚙️ Configuration

Edit `config.py` to customize:

```python
MODEL_NAME = "qwen3:4b"    # Change AI model
MODEL_OPTIONS = {
    "num_predict": 768,     # Max output tokens
    "num_ctx": 4096,        # Context window
    "num_gpu": 99,          # GPU layers (99 = all)
    "temperature": 0.4,     # Creativity (0.0-1.0)
}
```

---

## 🎮 Usage Examples

### CLI Commands
```
You: open chrome
You: search web for python tutorials
You: create a file called notes.txt with some ideas
You: what's my CPU usage?
You: remember my name is John
You: reset (clear conversation)
You: quit (exit)
```

### Desktop App
1. Launch: `python desktop_app.py`
2. Type or click 🎙️ to speak
3. Press `Ctrl+Space` to show/hide
4. Toggle voice output with 🔊 button

---

## 🔧 Troubleshooting

### "ollama not found"
- Install Ollama from [ollama.com](https://ollama.com)
- Ensure it's running: `ollama serve`

### "Model qwen3:4b not found"
```bash
ollama pull qwen3:4b
```

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### GPU not detected
- Ensure NVIDIA drivers are installed
- Check with: `nvidia-smi` (should show GPU info)

### Voice input not working
- Install PyAudio: `pip install PyAudio`
- Windows: Download from [Unofficial Windows Binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)

### Desktop app won't start
```bash
# Install GUI dependencies
pip install customtkinter Pillow
```

---

## 🔄 Updates

To update to the latest version:
```bash
git pull
pip install -r requirements.txt --upgrade
```

---

## 📚 Documentation

- **REFACTORING_SUMMARY.md** — Detailed architecture and changes
- **system_prompt.txt** — AI personality and behavior
- **config.py** — All configurable settings

---

## 💡 Tips

1. **First run**: Let Ollama download the model (takes a few minutes)
2. **Performance**: Close other GPU-intensive apps for best speed
3. **Memory**: Use `memory_store` tool to save preferences
4. **Safety**: Dangerous commands are automatically blocked
5. **Workspace**: Files are saved to `AI_WORKSPACE/` by default

---

## 🤝 Contributing

Issues and pull requests welcome!

---

## 📄 License

MIT License - See LICENSE file for details

---

**Built with**: Python · Ollama · CustomTkinter · DuckDuckGo · python-docx
