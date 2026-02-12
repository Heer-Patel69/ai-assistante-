# ⚡ Quick Start Cheat Sheet

## Installation (5 Minutes)

```bash
# 1. Install Ollama from ollama.com
# 2. Clone repo
git clone https://github.com/Heer-Patel69/ai-assistante-.git
cd ai-assistante-

# 3. Setup Python
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/Mac

# 4. Install dependencies
pip install -r requirements.txt

# 5. Pull AI model
ollama pull qwen3:4b

# 6. Run!
python main.py                 # CLI mode
python desktop_app.py          # GUI mode
streamlit run app.py           # Web mode
```

---

## Common Commands

### CLI Mode (`python main.py`)
```
search web for python tutorials
create a file notes.txt with my ideas
open chrome
what's my CPU usage?
remember my name is John
reset                          # Clear conversation
quit                           # Exit
```

### Desktop App (`python desktop_app.py`)
- Type or click 🎙️ to speak
- `Ctrl+Space` to show/hide
- 🔊 to toggle voice output
- 🗑️ to clear chat

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| `ollama not found` | Install from ollama.com |
| `Model not found` | `ollama pull qwen3:4b` |
| `Module not found` | `pip install -r requirements.txt` |
| GUI won't start | `pip install customtkinter Pillow` |
| Ollama won't connect | Run `ollama serve` |
| Too slow | Reduce `num_ctx` in config.py |
| Out of memory | Set `num_gpu: 0` in config.py |

---

## File Locations

- **Configuration**: `config.py`
- **AI Personality**: `system_prompt.txt`
- **Workspace**: `AI_WORKSPACE/` (auto-created)
- **Memory**: `memory.json` (auto-created)

---

## Configuration Quick Edit

Edit `config.py`:

```python
# Change model
MODEL_NAME = "qwen3:4b"

# Adjust performance
MODEL_OPTIONS = {
    "num_predict": 768,    # Tokens per response
    "num_ctx": 4096,       # Context window
    "num_gpu": 99,         # GPU layers (99=all)
    "temperature": 0.4,    # Creativity (0-1)
}
```

**Low RAM? Use:**
- `"num_ctx": 2048`
- `"num_predict": 512`
- `"num_gpu": 0`

**Want more creative?**
- `"temperature": 0.7`

---

## Verification Steps

```bash
# 1. Check Ollama
ollama list                    # Should show qwen3:4b

# 2. Test model
ollama run qwen3:4b "hi"       # Should respond

# 3. Test imports
python -c "import ollama; print('OK')"

# 4. Run assistant
python main.py
```

---

## Getting Help

📖 **Detailed Guide**: See `SETUP_GUIDE.md`
🔧 **Technical Details**: See `REFACTORING_SUMMARY.md`
📋 **Features**: See `README.md`

---

**That's it! You're ready to go! 🚀**
