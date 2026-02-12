import ollama

PLANNER_PROMPT = """You are a task planner. Given a user request, break it down into clear numbered steps.

Rules:
- Each step should be a single, concrete action
- Steps should be in logical execution order
- Keep steps simple and actionable
- If the task is simple (1 step), just list that one step
- Output ONLY the numbered steps, nothing else

User request: {request}

Steps:"""


def create_plan(user_request, model="deepseek-r1:8b"):
    """Ask the LLM to break a user request into executable steps."""
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "user", "content": PLANNER_PROMPT.format(request=user_request)}
        ]
    )
    plan_text = response["message"]["content"]
    return plan_text


def display_plan(plan_text):
    """Display the plan nicely."""
    print("\n📋 Plan:")
    print("-" * 40)
    print(plan_text)
    print("-" * 40)
    return plan_text
