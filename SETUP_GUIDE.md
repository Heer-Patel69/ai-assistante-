# 📖 UniVoid Setup Guide

Complete step-by-step guide to get UniVoid running on your PC.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Running UniVoid](#running-univoid)
4. [Platform-Specific Instructions](#platform-specific-instructions)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Configuration](#advanced-configuration)

---

## Prerequisites

### 1. Install Python 3.8 or Higher

**Windows:**
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Click "Install Now"
5. Verify: Open CMD and type `python --version`

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
```

**macOS:**
```bash
# Using Homebrew
brew install python
python3 --version
```

### 2. Install Ollama

**Windows:**
1. Download from [ollama.com](https://ollama.com)
2. Run the installer
3. Ollama will start automatically

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS:**
```bash
# Download from ollama.com or use:
brew install ollama
```

**Verify Ollama is running:**
```bash
ollama list
```

### 3. Install Git (Optional)

**Windows:**
- Download from [git-scm.com](https://git-scm.com/downloads)

**Linux:**
```bash
sudo apt install git
```

**macOS:**
```bash
brew install git
```

---

## Installation

### Step 1: Get the Code

**Option A: Using Git**
```bash
git clone https://github.com/Heer-Patel69/ai-assistante-.git
cd ai-assistante-
```

**Option B: Download ZIP**
1. Go to GitHub repository
2. Click "Code" → "Download ZIP"
3. Extract to a folder
4. Open terminal/CMD in that folder

### Step 2: Create Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**If you get errors**, install packages individually:
```bash
pip install ollama
pip install psutil
pip install requests
pip install duckduckgo-search
pip install python-docx
pip install customtkinter
pip install Pillow
pip install pyttsx3
pip install SpeechRecognition
```

### Step 4: Download AI Model

```bash
ollama pull qwen3:4b
```

This will download ~2.3GB. Wait for it to complete.

**Verify model is downloaded:**
```bash
ollama list
```

You should see `qwen3:4b` in the list.

---

## Running UniVoid

### Option 1: Desktop App (Recommended)

```bash
python desktop_app.py
```

**Features:**
- 🖥️ Always-on-top window
- 🎙️ Voice input (click microphone)
- 🔊 Voice output (toggleable)
- ⌨️ `Ctrl+Space` hotkey to show/hide
- 🎨 Modern GUI

**First Launch:**
1. Window appears with welcome message
2. Type a message or click 🎙️ to speak
3. Press Enter or click ➤ to send

### Option 2: Terminal/CLI Mode

```bash
python main.py
```

**Features:**
- 💻 Command-line interface
- ⚡ Lightweight
- 📊 Shows system info on startup

**Commands:**
- Type your message and press Enter
- Type `reset` to clear conversation
- Type `quit` or `exit` to close

### Option 3: Web Interface

```bash
streamlit run app.py
```

**Features:**
- 🌐 Opens in web browser
- 💬 Chat interface
- 📱 Accessible from any device on local network

Browser should auto-open to `http://localhost:8501`

---

## Platform-Specific Instructions

### Windows

**Install PyAudio for Voice (Optional):**

1. Check your Python version:
   ```cmd
   python --version
   ```

2. Download matching wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
   - Example: `PyAudio‑0.2.11‑cp310‑cp310‑win_amd64.whl` for Python 3.10, 64-bit

3. Install:
   ```cmd
   pip install PyAudio‑0.2.11‑cp310‑cp310‑win_amd64.whl
   ```

**GPU Acceleration:**
- Ensure NVIDIA drivers are installed
- Verify with: `nvidia-smi`

### Linux

**Install System Dependencies:**
```bash
sudo apt install portaudio19-dev python3-pyaudio
sudo apt install espeak  # For voice output
```

**GPU Acceleration (NVIDIA):**
```bash
# Install NVIDIA drivers
sudo apt install nvidia-driver-525  # or latest version
nvidia-smi  # Verify
```

### macOS

**Install System Dependencies:**
```bash
brew install portaudio
```

**GPU Note:**
- Apple Silicon Macs: Ollama uses Metal for acceleration
- Intel Macs: CPU only (slower)

---

## Verification

### Test 1: Check Ollama

```bash
ollama list
```
✅ Should show `qwen3:4b`

### Test 2: Test Ollama Model

```bash
ollama run qwen3:4b "Hello, how are you?"
```
✅ Should get a response

### Test 3: Test Python Environment

```bash
python -c "import ollama, psutil, requests; print('✅ All imports work')"
```

### Test 4: Test Tool System

```bash
python -c "from tools_core import TOOL_REGISTRY; print(f'✅ {len(TOOL_REGISTRY)} tools loaded')"
```

### Test 5: Run Main Program

```bash
python main.py
```

Type: `what's my system info?`

✅ Should show OS, CPU, RAM info

---

## Troubleshooting

### Issue: "Command 'python' not found"

**Solution:**
- Try `python3` instead of `python`
- Or add Python to PATH (Windows)

### Issue: "ollama: command not found"

**Solution:**
1. Ensure Ollama is installed
2. Restart terminal
3. Windows: Check if `ollama.exe` is in `C:\Users\<YourName>\AppData\Local\Programs\Ollama\`

### Issue: "Model not found"

**Solution:**
```bash
# Pull the model
ollama pull qwen3:4b

# Verify
ollama list
```

### Issue: "Module not found" errors

**Solution:**
```bash
# Make sure virtual environment is activated
# You should see (venv) in prompt

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Desktop app won't start

**Solution:**
```bash
# Install GUI dependencies
pip install customtkinter Pillow

# If still failing, check for errors:
python desktop_app.py
# Read error message
```

### Issue: "Connection refused" or Ollama errors

**Solution:**
```bash
# Start Ollama service
# Windows: It should auto-start, or run Ollama app
# Linux: 
ollama serve

# In another terminal, test:
ollama list
```

### Issue: Voice input not working

**Solution:**
```bash
# Install PyAudio
# Windows: Download wheel file (see Windows section)
# Linux:
sudo apt install python3-pyaudio portaudio19-dev
pip install PyAudio

# macOS:
brew install portaudio
pip install PyAudio
```

### Issue: GPU not being used

**Check:**
```bash
# NVIDIA
nvidia-smi

# In Python:
python -c "import torch; print(torch.cuda.is_available())"
```

**Solution:**
1. Install/update NVIDIA drivers
2. In `config.py`, ensure `num_gpu: 99`
3. Restart Ollama: `ollama serve`

### Issue: Too slow / Out of memory

**Solution:**

Edit `config.py`:
```python
MODEL_OPTIONS = {
    "num_predict": 512,      # Reduce from 768
    "num_ctx": 2048,         # Reduce from 4096
    "num_gpu": 0,            # Use CPU if GPU too small
}
```

Or use a smaller model:
```bash
ollama pull qwen3:1.5b  # Smaller, faster
```

Then edit `config.py`:
```python
MODEL_NAME = "qwen3:1.5b"
```

---

## Advanced Configuration

### Customize Model Settings

Edit `config.py`:

```python
MODEL_NAME = "qwen3:4b"  # Change model

MODEL_OPTIONS = {
    "num_predict": 768,   # Max output tokens (higher = longer responses)
    "temperature": 0.4,   # Creativity (0.0-1.0, higher = more creative)
    "num_ctx": 4096,      # Context window (higher = more memory)
    "top_p": 0.9,         # Nucleus sampling
    "repeat_penalty": 1.1,# Reduce repetition
    "num_gpu": 99,        # GPU layers (99 = all, 0 = CPU only)
}
```

### Change Workspace Directory

Edit `config.py`:

```python
WORKSPACE = "/path/to/your/workspace"  # Custom workspace
```

### Customize AI Personality

Edit `system_prompt.txt` to change how the AI behaves.

### Use Different Models

```bash
# List available models
ollama list

# Pull other models
ollama pull llama3:8b
ollama pull mistral:7b
ollama pull codellama:7b

# Update config.py
MODEL_NAME = "llama3:8b"
```

---

## Next Steps

1. ✅ Run `python main.py` to test CLI
2. ✅ Run `python desktop_app.py` for GUI
3. ✅ Try commands:
   - "search web for latest news"
   - "create a file called todo.txt"
   - "what's my CPU usage?"
   - "remember my name is [YourName]"
4. ✅ Explore `config.py` for customization
5. ✅ Read `REFACTORING_SUMMARY.md` for architecture details

---

## Getting Help

- 📖 Check [README.md](README.md) for quick reference
- 🔧 Review [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) for technical details
- 🐛 Report issues on GitHub
- 💬 Read error messages carefully — they usually tell you what's wrong!

---

**Enjoy your local AI assistant! 🎉**
