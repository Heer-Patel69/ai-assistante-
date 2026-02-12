"""
agent_loop.py — JARVIS Autonomous Agent Loop
Observe → Think → Act → Reflect → Repeat

The brain of the operator. Handles:
- Planning multi-step tasks
- Executing tools via JSON format
- Reflecting on results and self-correcting
- Streaming tokens to the UI
- Model routing (fast vs deep)
"""

import re
import json
import os
import ollama
from tools_core import execute_tool, get_tool_descriptions
from model_router import router
from memory import get_context_summary

# === CONFIG ===
MAX_STEPS = 10          # Max tool calls per user message
MAX_RETRIES = 3         # Max retries per failed step
MAX_HISTORY = 20        # Conversation history length

# Load system prompt
_prompt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system_prompt.txt")
with open(_prompt_path, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read().strip()

# Conversation history
conversation = []


def _build_system_message():
    """Build the full system message with tools + memory context."""
    memory_ctx = get_context_summary()
    memory_section = ""
    if memory_ctx and memory_ctx != "No stored memories.":
        memory_section = f"\n\nUSER MEMORIES:\n{memory_ctx}"

    return f"""{SYSTEM_PROMPT}

TOOL DESCRIPTIONS:
{get_tool_descriptions()}{memory_section}"""


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


def _extract_json_tool_call(text):
    """
    Extract a JSON tool call from the LLM response.
    Looks for {"tool": "...", "args": {...}}
    Returns (tool_name, args_dict) or (None, None).
    """
    # Try to find JSON in the text
    # Pattern 1: Standalone JSON
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

    # Pattern 2: Try parsing the entire cleaned text as JSON
    clean = text.strip()
    # Remove markdown code fences if present
    if clean.startswith("```"):
        lines = clean.split("\n")
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

    # Pattern 3: Legacy format (TOOL: name | arg)
    if text.strip().startswith("TOOL:"):
        tool_line = text.strip().replace("TOOL:", "").strip()
        parts = tool_line.split(" | ", 1)
        tool_name = parts[0].strip()
        tool_arg = parts[1].strip() if len(parts) > 1 else ""
        # Convert to simple args
        return tool_name, {"command": tool_arg} if tool_arg else {}

    return None, None


def _build_reflection_prompt(tool_name, tool_args, tool_result):
    """Build the reflection prompt sent after each tool execution."""
    return f"""Tool '{tool_name}' result:
{tool_result}

Is the task complete? If yes, give a one-line confirmation. If another tool is needed, output the JSON tool call."""


# ============================================
# MICRO-ROUTER — Deterministic fast path
# ============================================

def _micro_route(query):
    """
    Deterministic micro-router for obvious commands.
    Returns (tool_name, tool_args) or (None, None).
    Bypasses LLM entirely for instant execution.
    """
    q = query.strip().lower()

    # --- OPEN APP patterns ---
    open_prefixes = ["open ", "launch ", "start ", "run ", "play "]
    for prefix in open_prefixes:
        if q.startswith(prefix):
            target = query.strip()[len(prefix):].strip()
            # Check if it's a URL
            if any(kw in target.lower() for kw in [".com", ".org", ".net", ".io", ".dev", "http", "www."]):
                return "app_opener", {"url": target}
            # It's an app name
            return "app_opener", {"app": target}

    # --- LIST FILES patterns ---
    if q in ("list files", "show files", "ls", "dir"):
        return "file_manager", {"action": "list", "path": ""}
    if q.startswith("list files in ") or q.startswith("show files in "):
        path = query.strip().split(" in ", 1)[1].strip()
        return "file_manager", {"action": "list", "path": path}

    # --- SYSTEM INFO patterns ---
    if q in ("system info", "sys info", "system status"):
        return "system_info", {"query": "all"}
    if q in ("disk space", "disk usage", "storage"):
        return "system_info", {"query": "disk"}
    if q in ("cpu usage", "cpu"):
        return "system_info", {"query": "cpu"}
    if q in ("ram usage", "memory usage", "ram"):
        return "system_info", {"query": "ram"}
    if q in ("battery", "battery status"):
        return "system_info", {"query": "battery"}

    # --- No match → let LLM handle it ---
    return None, None


def run_agent_stream(query):
    """
    Main autonomous agent loop with streaming.
    Yields tuples of (msg_type, content):
        ("token", text)         — streaming token
        ("status", text)        — status update for UI
        ("tool_call", text)     — tool being executed
        ("tool_result", text)   — result of tool execution
        ("model_info", text)    — which model is being used
        ("done", text)          — final message
    """
    global conversation

    # Reset router for new query
    router.reset()

    # === MICRO-ROUTER: Instant execution for obvious commands ===
    micro_tool, micro_args = _micro_route(query)
    if micro_tool is not None:
        yield ("model_info", "⚡ Instant execution")
        yield ("tool_call", f"🔧 {micro_tool}")
        yield ("status", f"Executing {micro_tool}...")

        tool_result = execute_tool(micro_tool, micro_args)
        yield ("tool_result", tool_result)

        # Add to conversation for context
        conversation.append({"role": "user", "content": query})
        conversation.append({"role": "assistant", "content": f"Executed {micro_tool}: {tool_result}"})
        _trim_conversation()

        yield ("token", f"Done. {tool_result.split(chr(10))[0]}")
        yield ("done", "")
        return

    # === NORMAL LLM PATH ===

    # Select model based on query complexity
    model, options, reason = router.select_model(query)
    yield ("model_info", f"{router.get_status()} — {reason}")

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
            stream = ollama.chat(
                model=model,
                messages=messages,
                stream=True,
                options=options,
            )

            for chunk in stream:
                token = chunk["message"]["content"]
                full_reply += token

                # Filter <think> blocks (DeepSeek R1)
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
            yield ("token", f"\n❌ Model error: {error_msg}")
            conversation.append({"role": "assistant", "content": f"Error: {error_msg}"})
            return

        # Clean response
        clean_reply = _strip_think_tokens(full_reply).strip()

        # Store in conversation
        conversation.append({"role": "assistant", "content": full_reply})
        messages.append({"role": "assistant", "content": full_reply})

        # Check for tool call
        tool_name, tool_args = _extract_json_tool_call(clean_reply)

        if tool_name is None:
            # No tool call — agent is done (normal response or final summary)
            yield ("done", "")
            return

        # === EXECUTE TOOL ===
        yield ("tool_call", f"🔧 Step {step_count}: {tool_name}")
        yield ("status", f"Executing {tool_name}...")

        # Safety validation for destructive commands
        if router.needs_safety_validation(json.dumps(tool_args)):
            yield ("status", "🛡️ Safety validation...")

        tool_result = execute_tool(tool_name, tool_args)
        yield ("tool_result", tool_result)

        # === REFLECT ===
        reflection_prompt = _build_reflection_prompt(tool_name, tool_args, tool_result)
        reflection_msg = {"role": "user", "content": reflection_prompt}
        messages.append(reflection_msg)
        conversation.append(reflection_msg)

        # Check if tool failed → maybe escalate model
        if "❌" in tool_result or "BLOCKED" in tool_result:
            escalation = router.escalate()
            if escalation:
                model, options = escalation
                yield ("model_info", f"🔺 Escalated to {router.get_status()}")
        else:
            router.report_success()

        _trim_conversation()

        # Continue loop — LLM will reflect and decide next action

    # Max steps reached
    yield ("status", f"⚠️ Reached max {MAX_STEPS} steps")
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


def clear_conversation():
    """Reset conversation history."""
    global conversation
    conversation = []
    router.reset()
