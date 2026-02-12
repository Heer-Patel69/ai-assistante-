"""
main.py — UniVoid Terminal Mode
Clean CLI entry point for the AI assistant.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_loop import run_agent, reset_conversation
from config import print_config, MODEL_NAME


def main():
    print("=" * 60)
    print("🧠 UniVoid — Your Local AI Assistant")
    print("=" * 60)
    print_config()
    print("=" * 60)
    print("Type your message or command.")
    print("Commands:  reset = clear chat  |  quit/exit/bye = exit")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n🫵 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 UniVoid signing off.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "bye"):
            print("\n👋 UniVoid signing off.")
            break

        if user_input.lower() == "reset":
            reset_conversation()
            print("🧹 Conversation cleared.")
            continue

        # Run agent and print response
        print()
        response = run_agent(user_input)
        print(response)
        print()


if __name__ == "__main__":
    main()
