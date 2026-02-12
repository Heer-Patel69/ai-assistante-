"""
agent_loop.py — UniVoid Autonomous Agent Loop
Single-model (qwen3:4b) agent with JSON tool calling.
Observe → Think → Act → Reflect → Repeat

Handles:
- Multi-step task execution
- JSON-based tool calling
- Streaming tokens to UI
- Auto-retry on Ollama failures
"""

import re
import json
import os
import time
import ollama
from tools_core import execute_tool, get_tool_descriptions
from memory import get_context_summary
from config import MODEL_NAME, MODEL_OPTIONS, MAX_STEPS, MAX_RETRIES, MAX_HISTORY

# Load system prompt
_prompt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system_prompt.txt")
with open(_prompt_path, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read().strip()

# Conversation history
conversation = []


def _build_system_message():
    """Build the full system message with tools + memory context + JSON format examples."""
    memory_ctx = get_context_summary()
    memory_section = ""
    if memory_ctx and memory_ctx != "No stored memories.":
        memory_section = f"\n\nUSER MEMORIES:\n{memory_ctx}"

    tool_examples = """
TOOL CALLING EXAMPLES:
{"tool": "web_search", "args": {"query": "weather today"}}
{"tool": "file_manager", "args": {"action": "create", "path": "hello.py", "content": "print('Hello')"}}
{"tool": "terminal_executor", "args": {"command": "pip list"}}
{"tool": "document_creator", "args": {"filename": "report.md", "content": "# Report\\nContent here", "format": "md"}}
{"tool": "app_opener", "args": {"app": "chrome"}}
{"tool": "system_info", "args": {"query": "all"}}
{"tool": "memory_store", "args": {"action": "save", "key": "name", "value": "Heer"}}
"""

    return f"""{SYSTEM_PROMPT}

TOOL DESCRIPTIONS:
{get_tool_descriptions()}

{tool_examples}{memory_section}"""


def _trim_conversation():
    """Keep conversation history short."""
    global conversation
    if len(conversation) > MAX_HISTORY:
        conversation = conversation[-(MAX_HISTORY):]


def _strip_think_tokens(text):
    """Remove <think>...</think> blocks from DeepSeek R1 responses."""
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    cleaned = re.sub(r'<think>.*$', '', cleaned, flags=re.DOTALL)
    return cleaned.strip()


def _extract_tool_call(text):
    """
    Extract a JSON tool call from the LLM response.
    Looks for {"tool": "...", "args": {...}}
    Returns (tool_name, args_dict) or (None, None).
    """
    # Pattern 1: Find JSON objects with tool and args
    json_patterns = [
        r'\{[^{}]*"tool"\s*:\s*"[^"]+"\s*,\s*"args"\s*:\s*\{[^{}]*\}[^{}]*\}',
        r'\{[^{}]*"tool"\s*:\s*"[^"]+"\s*,\s*"args"\s*:\s*\{.*?\}\s*\}',
    ]

    for pattern in json_patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                if "tool" in data and "args" in data:
                    return data["tool"], data["args"]
            except json.JSONDecodeError:
                continue

    # Pattern 2: Try parsing entire cleaned text as JSON
    clean = text.strip()
    # Remove markdown code fences if present
    if clean.startswith("```"):
        lines = clean.split("\n")
        if len(lines) > 1:
            clean = "\n".join(lines[1:])
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()

    try:
        data = json.loads(clean)
        if isinstance(data, dict) and "tool" in data and "args" in data:
            return data["tool"], data["args"]
    except (json.JSONDecodeError, TypeError):
        pass

    return None, None


def _build_reflection_prompt(tool_name, tool_args, tool_result):
    """Build the reflection prompt sent after each tool execution."""
    return f"""Tool '{tool_name}' result:
{tool_result}

Is the task complete? If yes, give a one-line confirmation. If another tool is needed, output the JSON tool call."""


def _ollama_chat(messages, stream=True):
    """
    Wrapper for ollama.chat with auto-retry on failures.
    Retries up to MAX_RETRIES times with 1 second pause between attempts.
    """
    for attempt in range(MAX_RETRIES):
        try:
            return ollama.chat(
                model=MODEL_NAME,
                messages=messages,
                stream=stream,
                options=MODEL_OPTIONS
            )
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)  # Pause before retry
                continue
            else:
                raise e  # Re-raise on final attempt


def run_agent_stream(query):
    """
    Main autonomous agent loop with streaming.
    Yields tuples of (msg_type, content):
        ("token", text)         — streaming token
        ("tool_call", text)     — tool being executed
        ("tool_result", text)   — result of tool execution
        ("error", text)         — error message
        ("warning", text)       — warning message
        ("done", text)          — final message
    """
    global conversation

    # Build messages
    system_msg = {"role": "system", "content": _build_system_message()}
    conversation.append({"role": "user", "content": query})
    _trim_conversation()

    messages = [system_msg] + conversation

    # === MAIN AGENT LOOP ===
    step_count = 0

    while step_count < MAX_STEPS:
        step_count += 1

        # Stream LLM response
        full_reply = ""
        visible_text = ""
        in_think = False

        try:
            stream = _ollama_chat(messages, stream=True)

            for chunk in stream:
                token = chunk["message"]["content"]
                full_reply += token

                # Filter <think> blocks (for reasoning models)
                if "<think>" in token:
                    in_think = True
                    continue
                if "</think>" in token:
                    in_think = False
                    continue
                if in_think:
                    continue

                visible_text += token
                yield ("token", token)

        except Exception as e:
            error_msg = str(e)
            yield ("error", f"Model error: {error_msg}")
            conversation.append({"role": "assistant", "content": f"Error: {error_msg}"})
            return

        # Clean response
        clean_reply = _strip_think_tokens(full_reply).strip()

        # Store in conversation
        conversation.append({"role": "assistant", "content": full_reply})
        messages.append({"role": "assistant", "content": full_reply})

        # Check for tool call
        tool_name, tool_args = _extract_tool_call(clean_reply)

        if tool_name is None:
            # No tool call — agent is done (normal response or final summary)
            yield ("done", "")
            return

        # === EXECUTE TOOL ===
        yield ("tool_call", f"🔧 Step {step_count}: {tool_name}")

        tool_result = execute_tool(tool_name, tool_args)
        yield ("tool_result", tool_result)

        # === REFLECT ===
        reflection_prompt = _build_reflection_prompt(tool_name, tool_args, tool_result)
        reflection_msg = {"role": "user", "content": reflection_prompt}
        messages.append(reflection_msg)
        conversation.append(reflection_msg)

        _trim_conversation()

        # Continue loop — LLM will reflect and decide next action

    # Max steps reached
    yield ("warning", f"Reached max {MAX_STEPS} steps")
    yield ("done", "")


def run_agent(query):
    """Non-streaming version — returns full response string."""
    result_parts = []
    tool_outputs = []

    for msg_type, content in run_agent_stream(query):
        if msg_type == "token":
            result_parts.append(content)
        elif msg_type == "tool_result":
            tool_outputs.append(content)
        elif msg_type == "tool_call":
            tool_outputs.append(content)

    reply = "".join(result_parts)
    if tool_outputs:
        reply += "\n\n" + "\n".join(tool_outputs)
    return reply


def reset_conversation():
    """Reset conversation history."""
    global conversation
    conversation = []
