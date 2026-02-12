"""
agent.py — UniVoid Brain (Optimized for Speed)
Loads all models ONCE. UI just calls run_agent(query).
"""

import re
import ollama
from tools import get_tool_descriptions, execute_tool
from planner import create_plan

# === SPEED CONFIG ===
# qwen3:4b  → FAST, good for chat + tools
# deepseek-r1:8b → SLOW (5-10 sec), better reasoning but has <think> overhead
MODEL = "gemma3:1b"

# Ollama options for speed
MODEL_OPTIONS = {
    "num_predict": 256,     # Limit max tokens (shorter = faster)
    "temperature": 0.7,
    "num_ctx": 2048,        # Smaller context window = faster
}

# Load system prompt ONCE
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read().strip()

# Build tool-aware system message
TOOL_PROMPT = f"""{SYSTEM_PROMPT}

You have the following tools available:
{get_tool_descriptions()}

When the user asks you to do something that requires a tool, respond with EXACTLY this format:
TOOL: tool_name | argument

Examples:
- TOOL: create_folder | my_project
- TOOL: open_vscode |
- TOOL: create_text_file | hello.py | print("Hello World")
- TOOL: organize_files |

If you need to plan a complex task, respond with:
PLAN: (and I will generate a step-by-step plan)

If no tool is needed, just respond normally as a conversational AI.
Never use markdown formatting in your response — plain text only.
Keep responses SHORT and concise. Maximum 2-3 sentences unless asked for detail.
"""

# Conversation history (keep it short for speed)
MAX_HISTORY = 10  # Keep only last N messages to reduce context size
conversation = [{"role": "system", "content": TOOL_PROMPT}]


def _trim_conversation():
    """Keep conversation history short for faster inference."""
    global conversation
    if len(conversation) > MAX_HISTORY + 1:  # +1 for system prompt
        conversation = [conversation[0]] + conversation[-(MAX_HISTORY):]


def _strip_think_tokens(text):
    """Remove <think>...</think> blocks from DeepSeek R1 responses."""
    # Remove complete think blocks
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # Remove incomplete/opening think tags
    cleaned = re.sub(r'<think>.*$', '', cleaned, flags=re.DOTALL)
    return cleaned.strip()


def run_agent_stream(query):
    """
    Send query to LLM and yield tokens as they stream.
    Filters out <think> tokens from reasoning models.
    """
    conversation.append({"role": "user", "content": query})
    _trim_conversation()

    full_reply = ""
    in_think = False
    visible_text = ""

    stream = ollama.chat(
        model=MODEL,
        messages=conversation,
        stream=True,
        options=MODEL_OPTIONS
    )

    for chunk in stream:
        token = chunk["message"]["content"]
        full_reply += token

        # Filter <think> blocks (for DeepSeek R1)
        if "<think>" in token:
            in_think = True
            continue
        if "</think>" in token:
            in_think = False
            continue
        if in_think:
            continue

        # Only yield visible tokens
        visible_text += token
        yield ("token", token)

    conversation.append({"role": "assistant", "content": full_reply})

    # Clean the visible text for tool/plan detection
    clean_reply = _strip_think_tokens(full_reply).strip()

    # Check if AI wants to use a tool
    if clean_reply.startswith("TOOL:"):
        tool_line = clean_reply.replace("TOOL:", "").strip()
        parts = tool_line.split(" | ", 1)
        tool_name = parts[0].strip()
        tool_arg = parts[1].strip() if len(parts) > 1 else ""
        result = execute_tool(tool_name, tool_arg)
        yield ("tool_result", result)

    elif clean_reply.startswith("PLAN:"):
        request = clean_reply.replace("PLAN:", "").strip()
        plan = create_plan(request or query)
        yield ("plan", plan)


def run_agent(query):
    """Non-streaming version — returns full response string."""
    result_parts = []
    tool_output = None

    for msg_type, content in run_agent_stream(query):
        if msg_type == "token":
            result_parts.append(content)
        elif msg_type == "tool_result":
            tool_output = content
        elif msg_type == "plan":
            tool_output = content

    reply = "".join(result_parts)
    if tool_output:
        reply += f"\n\n{tool_output}"
    return reply


def clear_conversation():
    """Reset conversation history."""
    global conversation
    conversation = [{"role": "system", "content": TOOL_PROMPT}]
