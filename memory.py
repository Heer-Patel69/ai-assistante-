"""
memory.py — Persistent JSON Memory System
Stores user preferences, project paths, and context across sessions.
"""

import os
import json
from datetime import datetime

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory.json")


def _load_memory():
    """Load memory from disk."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_memory(data):
    """Save memory to disk."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save(key, value):
    """Save a key-value pair to memory."""
    data = _load_memory()
    data[key] = {
        "value": value,
        "updated": datetime.now().isoformat(),
    }
    _save_memory(data)
    return f"✅ Remembered: {key} = {value}"


def get(key):
    """Retrieve a value by key."""
    data = _load_memory()
    if key in data:
        return data[key]["value"]
    return None


def search(query):
    """Search memory for keys or values matching the query."""
    data = _load_memory()
    query_lower = query.lower()
    results = []
    for key, entry in data.items():
        val = str(entry.get("value", ""))
        if query_lower in key.lower() or query_lower in val.lower():
            results.append(f"  🧠 {key}: {val}")
    if not results:
        return f"❌ No memories matching '{query}'"
    return "🧠 Found memories:\n" + "\n".join(results)


def list_all():
    """List all stored memories."""
    data = _load_memory()
    if not data:
        return "🧠 Memory is empty."
    lines = ["🧠 All memories:"]
    for key, entry in data.items():
        val = str(entry.get("value", ""))
        lines.append(f"  • {key}: {val}")
    return "\n".join(lines)


def delete(key):
    """Delete a memory entry."""
    data = _load_memory()
    if key in data:
        del data[key]
        _save_memory(data)
        return f"✅ Forgot: {key}"
    return f"❌ Memory '{key}' not found."


def clear_all():
    """Clear all memory."""
    _save_memory({})
    return "✅ All memories cleared."


def get_context_summary():
    """Get a brief summary of stored memories for the system prompt."""
    data = _load_memory()
    if not data:
        return "No stored memories."
    lines = []
    for key, entry in list(data.items())[:10]:  # Max 10 entries in context
        val = str(entry.get("value", ""))
        if len(val) > 100:
            val = val[:100] + "..."
        lines.append(f"- {key}: {val}")
    return "\n".join(lines)
