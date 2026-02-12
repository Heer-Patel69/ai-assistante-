"""
config.py — Single Source of Truth for All Settings
Centralized configuration for the AI assistant.
"""

import os
import psutil

# === MODEL CONFIGURATION ===
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen3:4b")

MODEL_OPTIONS = {
    "num_predict": 768,      # Increased from 256 for more detailed responses
    "temperature": 0.4,      # Lower for more focused responses
    "num_ctx": 4096,         # Increased from 2048 for better context
    "top_p": 0.9,
    "repeat_penalty": 1.1,
    "num_gpu": 99,           # Force ALL layers to GPU (RTX 3050 Ti)
}

# === PATH CONFIGURATION ===
DESKTOP = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
HOME = os.path.expanduser("~")
WORKSPACE = os.path.join(DESKTOP, "AI_WORKSPACE")
MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory.json")

# === AGENT CONFIGURATION ===
MAX_STEPS = 10           # Max tool calls per user message
MAX_RETRIES = 2          # Max retries per failed Ollama call
MAX_HISTORY = 30         # Conversation history length
CONFIRM_DESTRUCTIVE = True

# === UTILITY FUNCTION ===
def print_config():
    """Print system configuration info at startup."""
    ram = psutil.virtual_memory()
    print(f"  🧠 RAM: {ram.total // 1024 // 1024} MB ({ram.percent}% used)")
    print(f"  🤖 Model: {MODEL_NAME}")
    print(f"  📝 Max tokens: {MODEL_OPTIONS['num_predict']}")
    print(f"  📐 Context: {MODEL_OPTIONS['num_ctx']}")
    print(f"  🎮 GPU layers: {MODEL_OPTIONS.get('num_gpu', 'auto')}")
