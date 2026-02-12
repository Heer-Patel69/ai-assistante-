"""
desktop_app.py — UniVoid Desktop Chat Window
Native always-on-top chat with voice + streaming + hotkey.
"""

import customtkinter as ctk
import threading
import time
import os
import sys

# Ensure we can import from the project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_loop import run_agent_stream, reset_conversation
from voice_input import record_audio, transcribe_audio
from voice_output import speak

# ============================================
# APPEARANCE
# ============================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Colors
BG_DARK = "#0f0c29"
BG_PANEL = "#1a1a2e"
BG_INPUT = "#16213e"
ACCENT = "#667eea"
ACCENT_HOVER = "#764ba2"
USER_BUBBLE = "#2d2d5e"
AI_BUBBLE = "#1a1a3e"
TEXT_COLOR = "#e0e0e0"
MUTED_COLOR = "#888888"


class UniVoidApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("🧠 UniVoid")
        self.geometry("480x700")
        self.minsize(400, 500)
        self.configure(fg_color=BG_DARK)
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # State
        self.voice_enabled = True
        self.is_recording = False
        self.is_processing = False
        self.topmost = True

        # Build UI
        self._build_header()
        self._build_chat_area()
        self._build_input_area()
        self._build_status_bar()

        # Welcome message
        self.after(500, lambda: self.add_message(
            "ai", "Hello! I'm UniVoid, your local AI assistant.\n"
                  "Type a message or click 🎙️ to speak.\n"
                  "Press Ctrl+Space to toggle this window."
        ))

        # Hotkey (Ctrl+Space to show/hide)
        self._setup_hotkey()

    # ============================================
    # HEADER
    # ============================================
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=60)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        # Title
        title_label = ctk.CTkLabel(
            header, text="🧠 UniVoid",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=ACCENT
        )
        title_label.pack(side="left", padx=15, pady=10)

        # Pin button (toggle always-on-top)
        self.pin_btn = ctk.CTkButton(
            header, text="📌", width=35, height=35,
            fg_color="transparent", hover_color=BG_INPUT,
            font=ctk.CTkFont(size=16),
            command=self.toggle_topmost
        )
        self.pin_btn.pack(side="right", padx=5, pady=10)

        # Clear chat button
        clear_btn = ctk.CTkButton(
            header, text="🗑️", width=35, height=35,
            fg_color="transparent", hover_color=BG_INPUT,
            font=ctk.CTkFont(size=16),
            command=self.clear_chat
        )
        clear_btn.pack(side="right", padx=5, pady=10)

        # Voice toggle
        self.voice_btn = ctk.CTkButton(
            header, text="🔊", width=35, height=35,
            fg_color="transparent", hover_color=BG_INPUT,
            font=ctk.CTkFont(size=16),
            command=self.toggle_voice
        )
        self.voice_btn.pack(side="right", padx=5, pady=10)

    # ============================================
    # CHAT AREA
    # ============================================
    def _build_chat_area(self):
        self.chat_frame = ctk.CTkScrollableFrame(
            self, fg_color=BG_DARK,
            scrollbar_button_color=ACCENT,
            scrollbar_button_hover_color=ACCENT_HOVER
        )
        self.chat_frame.pack(fill="both", expand=True, padx=8, pady=(5, 0))

    def add_message(self, role, text):
        """Add a message bubble to the chat."""
        is_user = role == "user"

        # Container for alignment
        container = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        container.pack(fill="x", padx=5, pady=3)

        # Bubble
        bubble = ctk.CTkFrame(
            container,
            fg_color=USER_BUBBLE if is_user else AI_BUBBLE,
            corner_radius=15
        )

        if is_user:
            bubble.pack(anchor="e", padx=(60, 5), pady=2)
        else:
            bubble.pack(anchor="w", padx=(5, 60), pady=2)

        # Label
        label_text = ctk.CTkLabel(
            bubble, text=text,
            wraplength=320,
            justify="left",
            text_color=TEXT_COLOR,
            font=ctk.CTkFont(size=13),
            anchor="w"
        )
        label_text.pack(padx=12, pady=8)

        # Auto-scroll to bottom
        self.chat_frame.after(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    # ============================================
    # STREAMING MESSAGE
    # ============================================
    def start_ai_message(self):
        """Create an AI message bubble for streaming tokens into."""
        container = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        container.pack(fill="x", padx=5, pady=3)

        bubble = ctk.CTkFrame(container, fg_color=AI_BUBBLE, corner_radius=15)
        bubble.pack(anchor="w", padx=(5, 60), pady=2)

        label = ctk.CTkLabel(
            bubble, text="",
            wraplength=320, justify="left",
            text_color=TEXT_COLOR,
            font=ctk.CTkFont(size=13),
            anchor="w"
        )
        label.pack(padx=12, pady=8)
        return label

    def update_ai_message(self, label, text):
        """Update the streaming message label."""
        label.configure(text=text)
        self._scroll_to_bottom()

    # ============================================
    # INPUT AREA
    # ============================================
    def _build_input_area(self):
        input_frame = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=60)
        input_frame.pack(fill="x", padx=0, pady=0)
        input_frame.pack_propagate(False)

        # Mic button
        self.mic_btn = ctk.CTkButton(
            input_frame, text="🎙️", width=42, height=42,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            corner_radius=21,
            font=ctk.CTkFont(size=18),
            command=self.on_voice_click
        )
        self.mic_btn.pack(side="left", padx=(10, 5), pady=9)

        # Send button
        send_btn = ctk.CTkButton(
            input_frame, text="➤", width=42, height=42,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            corner_radius=21,
            font=ctk.CTkFont(size=18),
            command=self.on_send
        )
        send_btn.pack(side="right", padx=(5, 10), pady=9)

        # Text input
        self.input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type a message...",
            fg_color=BG_INPUT,
            border_color=ACCENT,
            text_color=TEXT_COLOR,
            font=ctk.CTkFont(size=13),
            height=42,
            corner_radius=21
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=5, pady=9)
        self.input_entry.bind("<Return>", lambda e: self.on_send())

    # ============================================
    # STATUS BAR
    # ============================================
    def _build_status_bar(self):
        self.status_label = ctk.CTkLabel(
            self, text="Ready • Ctrl+Space to toggle",
            font=ctk.CTkFont(size=11),
            text_color=MUTED_COLOR,
            height=20
        )
        self.status_label.pack(fill="x", padx=10, pady=(0, 5))

    def set_status(self, text):
        self.status_label.configure(text=text)

    # ============================================
    # ACTIONS
    # ============================================
    def on_send(self):
        """Handle text send."""
        text = self.input_entry.get().strip()
        if not text or self.is_processing:
            return

        self.input_entry.delete(0, "end")
        self.add_message("user", text)
        self._run_agent_threaded(text)

    def on_voice_click(self):
        """Handle voice button click — push to talk."""
        if self.is_recording or self.is_processing:
            return

        self.is_recording = True
        self.mic_btn.configure(fg_color="#e74c3c", text="⏺️")
        self.set_status("🎙️ Recording... (5 seconds)")

        def voice_worker():
            try:
                file = record_audio(duration=5)
                self.after(0, lambda: self.set_status("📝 Transcribing..."))
                text = transcribe_audio(file)

                self.is_recording = False
                self.after(0, lambda: self.mic_btn.configure(fg_color=ACCENT, text="🎙️"))

                if text.strip():
                    self.after(0, lambda: self.add_message("user", f"🎙️ {text}"))
                    self._run_agent_threaded(text)
                else:
                    self.after(0, lambda: self.set_status("Couldn't hear anything. Try again."))
            except Exception as e:
                err_msg = str(e)
                self.is_recording = False
                self.after(0, lambda: self.mic_btn.configure(fg_color=ACCENT, text="🎙️"))
                self.after(0, lambda m=err_msg: self.set_status(f"❌ Voice error: {m}"))

        threading.Thread(target=voice_worker, daemon=True).start()

    def _run_agent_threaded(self, query):
        """Run the agent in a background thread with streaming."""
        self.is_processing = True
        self.set_status("🧠 Thinking...")

        def agent_worker():
            try:
                # Create streaming label on UI thread
                label = [None]
                full_text = [""]

                def create_label():
                    label[0] = self.start_ai_message()
                self.after(0, create_label)
                import time
                time.sleep(0.1)  # Wait for label creation

                for msg_type, content in run_agent_stream(query):
                    if msg_type == "token":
                        full_text[0] += content
                        text_snapshot = full_text[0]
                        self.after(0, lambda t=text_snapshot: self.update_ai_message(label[0], t))

                    elif msg_type == "tool_call":
                        self.after(0, lambda c=content: self.add_message("ai", c))
                        # Reset streaming label for next LLM output
                        full_text[0] = ""
                        def new_label():
                            label[0] = self.start_ai_message()
                        self.after(0, new_label)
                        time.sleep(0.1)

                    elif msg_type == "tool_result":
                        # Show tool result as a separate message
                        result_preview = content[:500] + ("..." if len(content) > 500 else "")
                        self.after(0, lambda c=result_preview: self.add_message("ai", f"📋 {c}"))
                        # New label for reflection
                        full_text[0] = ""
                        def new_label2():
                            label[0] = self.start_ai_message()
                        self.after(0, new_label2)
                        time.sleep(0.1)

                    elif msg_type == "error":
                        self.after(0, lambda c=content: self.add_message("ai", f"❌ {c}"))

                    elif msg_type == "warning":
                        self.after(0, lambda c=content: self.add_message("ai", f"⚠️ {c}"))

                    elif msg_type == "done":
                        pass

                # Voice output
                final_text = full_text[0]
                if self.voice_enabled and final_text.strip():
                    self.after(0, lambda: self.set_status("🔊 Speaking..."))
                    speak_text = final_text[:200] + ("..." if len(final_text) > 200 else "")
                    speak(speak_text)

                self.after(0, lambda: self.set_status("Ready • Ctrl+Space to toggle"))
                self.is_processing = False

            except Exception as e:
                err_msg = str(e)
                self.after(0, lambda m=err_msg: self.add_message("ai", f"❌ Error: {m}"))
                self.after(0, lambda: self.set_status("Ready"))
                self.is_processing = False

        threading.Thread(target=agent_worker, daemon=True).start()

    def toggle_topmost(self):
        self.topmost = not self.topmost
        self.attributes("-topmost", self.topmost)
        self.pin_btn.configure(text="📌" if self.topmost else "📍")
        self.set_status(f"{'Pinned' if self.topmost else 'Unpinned'} • Ctrl+Space to toggle")

    def toggle_voice(self):
        self.voice_enabled = not self.voice_enabled
        self.voice_btn.configure(text="🔊" if self.voice_enabled else "🔇")
        self.set_status(f"Voice {'ON' if self.voice_enabled else 'OFF'}")

    def clear_chat(self):
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
        reset_conversation()
        self.add_message("ai", "Chat cleared. How can I help?")
        self.set_status("Ready")

    def _setup_hotkey(self):
        """Ctrl+Space to show/hide window using pynput (no admin needed)."""
        try:
            from pynput import keyboard as kb

            self._ctrl_pressed = False
            self._hotkey_listener = None

            def on_press(key):
                if key in (kb.Key.ctrl_l, kb.Key.ctrl_r):
                    self._ctrl_pressed = True
                elif key == kb.Key.space and self._ctrl_pressed:
                    self._toggle_visibility()

            def on_release(key):
                if key in (kb.Key.ctrl_l, kb.Key.ctrl_r):
                    self._ctrl_pressed = False

            self._hotkey_listener = kb.Listener(on_press=on_press, on_release=on_release)
            self._hotkey_listener.daemon = True
            self._hotkey_listener.start()
        except Exception:
            pass

    def _toggle_visibility(self):
        """Toggle window visibility from hotkey."""
        if self.state() == "withdrawn":
            self.after(0, self.deiconify)
            self.after(50, self.lift)
            self.after(100, self.focus_force)
        else:
            self.after(0, self.withdraw)

    def on_close(self):
        """Clean exit."""
        try:
            if hasattr(self, '_hotkey_listener') and self._hotkey_listener:
                self._hotkey_listener.stop()
        except Exception:
            pass
        self.destroy()


# ============================================
# LAUNCH
# ============================================
if __name__ == "__main__":
    app = UniVoidApp()
    app.mainloop()
