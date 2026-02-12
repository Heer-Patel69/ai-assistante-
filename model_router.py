"""
model_router.py — Intelligent Model Router
Selects the best LLM based on task complexity.

Brain Stack:
  ⚡ qwen3:4b     → Fast Brain (80% of tasks)
  🧠 deepseek-r1:8b → Deep Brain (complex reasoning)
  🛟 gemma3:1b     → Emergency fallback
"""

import ollama

# === MODEL DEFINITIONS ===
FAST_MODEL = "qwen3:4b"
DEEP_MODEL = "deepseek-r1:8b"
FALLBACK_MODEL = "gemma3:1b"

# === MODEL OPTIONS ===
FAST_OPTIONS = {
    "num_predict": 256,      # Short responses = faster
    "temperature": 0.5,      # Lower temp = more decisive
    "num_ctx": 4096,
}

DEEP_OPTIONS = {
    "num_predict": 1024,
    "temperature": 0.5,
    "num_ctx": 4096,
}

FALLBACK_OPTIONS = {
    "num_predict": 256,
    "temperature": 0.7,
    "num_ctx": 2048,
}

# === COMPLEXITY KEYWORDS ===
# If the user's message contains these patterns, route to Deep model
COMPLEX_KEYWORDS = [
    "debug", "fix this error", "why is this failing",
    "build a project", "create an app", "architecture",
    "algorithm", "optimize", "refactor",
    "analyze", "diagnose", "investigate",
    "step by step", "explain in detail",
    "complex", "advanced",
    "math", "calculate", "equation",
    "compare", "evaluate", "trade-off",
]

# === DESTRUCTIVE COMMANDS (force Deep model validation) ===
DESTRUCTIVE_PATTERNS = [
    "delete", "remove", "format", "wipe", "uninstall",
    "overwrite", "replace all", "drop", "destroy",
    "shutdown", "restart", "kill process",
]


class ModelRouter:
    """Intelligent model selection with escalation."""

    def __init__(self):
        self.current_model = FAST_MODEL
        self.current_options = FAST_OPTIONS
        self.consecutive_failures = 0
        self.escalated = False
        self._available_models = None

    def _get_available_models(self):
        """Cache the list of available Ollama models."""
        if self._available_models is None:
            try:
                models = ollama.list()
                self._available_models = [
                    m.model.split(":")[0] + ":" + m.model.split(":")[-1]
                    if ":" in m.model else m.model
                    for m in models.models
                ]
            except Exception:
                self._available_models = []
        return self._available_models

    def _is_model_available(self, model_name):
        """Check if a model is installed."""
        available = self._get_available_models()
        # Check both exact match and base name match
        base_name = model_name.split(":")[0]
        return any(
            m == model_name or m.startswith(base_name + ":")
            for m in available
        )

    def _classify_complexity(self, query):
        """
        Fast keyword-based classification.
        Returns 'SIMPLE' or 'COMPLEX'.
        """
        query_lower = query.lower()

        # Check for destructive commands → always COMPLEX (needs validation)
        for pattern in DESTRUCTIVE_PATTERNS:
            if pattern in query_lower:
                return "COMPLEX"

        # Check for complexity keywords
        matches = sum(1 for kw in COMPLEX_KEYWORDS if kw in query_lower)
        if matches >= 1:
            return "COMPLEX"

        # Default: simple
        return "SIMPLE"

    def select_model(self, query):
        """
        Select the best model for the given query.
        Returns (model_name, options_dict, reason).
        """
        complexity = self._classify_complexity(query)

        if complexity == "COMPLEX":
            # Try deep model first
            if self._is_model_available(DEEP_MODEL):
                self.current_model = DEEP_MODEL
                self.current_options = DEEP_OPTIONS
                return DEEP_MODEL, DEEP_OPTIONS, "🧠 Deep reasoning required"
            # Fallback to fast if deep not available
            if self._is_model_available(FAST_MODEL):
                self.current_model = FAST_MODEL
                self.current_options = FAST_OPTIONS
                return FAST_MODEL, FAST_OPTIONS, "⚡ Using fast model (deep unavailable)"

        # Simple tasks → fast model
        if self._is_model_available(FAST_MODEL):
            self.current_model = FAST_MODEL
            self.current_options = FAST_OPTIONS
            return FAST_MODEL, FAST_OPTIONS, "⚡ Fast operation"

        # Emergency fallback
        if self._is_model_available(FALLBACK_MODEL):
            self.current_model = FALLBACK_MODEL
            self.current_options = FALLBACK_OPTIONS
            return FALLBACK_MODEL, FALLBACK_OPTIONS, "🛟 Emergency fallback"

        # Nothing available — return fast model and hope Ollama is running
        self.current_model = FAST_MODEL
        self.current_options = FAST_OPTIONS
        return FAST_MODEL, FAST_OPTIONS, "⚠️ No models detected, trying default"

    def escalate(self):
        """
        Escalate to the deep model after repeated failures.
        Returns (model_name, options_dict) or None if already at deepest.
        """
        self.consecutive_failures += 1

        if self.consecutive_failures >= 2 and not self.escalated:
            if self._is_model_available(DEEP_MODEL):
                self.escalated = True
                self.current_model = DEEP_MODEL
                self.current_options = DEEP_OPTIONS
                return DEEP_MODEL, DEEP_OPTIONS
        return None

    def report_success(self):
        """Reset failure counter on success."""
        self.consecutive_failures = 0
        # Don't de-escalate mid-task — keep deep model if escalated

    def reset(self):
        """Reset router state for a new conversation turn."""
        self.consecutive_failures = 0
        self.escalated = False
        self.current_model = FAST_MODEL
        self.current_options = FAST_OPTIONS

    def needs_safety_validation(self, query):
        """Check if a destructive command needs DeepSeek validation."""
        query_lower = query.lower()
        return any(p in query_lower for p in DESTRUCTIVE_PATTERNS)

    def get_status(self):
        """Get current router status for display."""
        model_icon = "⚡" if self.current_model == FAST_MODEL else "🧠"
        if self.current_model == FALLBACK_MODEL:
            model_icon = "🛟"
        return f"{model_icon} {self.current_model}"


# Global router instance
router = ModelRouter()
