"""
main.py — JARVIS Terminal Mode
Run the autonomous agent in terminal with full tool support.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_loop import run_agent_stream, clear_conversation
from model_router import router


def main():
    print("=" * 55)
    print("🧠 JARVIS — Autonomous Local Computer Operator")
    print("=" * 55)
    print("Type your task in natural language.")
    print("Commands:  /clear = reset  |  /exit = quit")
    print("=" * 55)

    while True:
        try:
            user_input = input("\n🫵 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 JARVIS signing off.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/exit", "exit", "quit"):
            print("\n👋 JARVIS signing off.")
            break

        if user_input.lower() in ("/clear", "clear"):
            clear_conversation()
            print("🧹 Conversation cleared.")
            continue

        # Run agent with streaming output
        print()
        current_line = ""

        for msg_type, content in run_agent_stream(user_input):
            if msg_type == "token":
                print(content, end="", flush=True)
                current_line += content

            elif msg_type == "model_info":
                print(f"\n{content}")

            elif msg_type == "status":
                print(f"\n⏳ {content}")

            elif msg_type == "tool_call":
                print(f"\n\n{content}")
                current_line = ""

            elif msg_type == "tool_result":
                preview = content[:800] + ("..." if len(content) > 800 else "")
                print(f"\n📋 {preview}")
                current_line = ""

            elif msg_type == "done":
                if current_line:
                    print()  # Ensure newline at end

        print()  # Final newline


if __name__ == "__main__":
    main()
