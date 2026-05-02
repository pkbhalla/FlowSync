"""Gemini AI wrapper functions for FlowSync."""
import os, json

_client = None

def _get_client():
    global _client
    if _client is None:
        import google.generativeai as genai
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return None
        genai.configure(api_key=api_key)
        _client = genai.GenerativeModel('gemini-2.0-flash')
    return _client

def generate_subtasks(task_title: str, task_description: str = '') -> list[dict]:
    """Use Gemini to break a task into subtasks. Returns list of {title, description}."""
    model = _get_client()
    if not model:
        return []
    prompt = f"""You are a project management assistant. Break the following task into 3-5 actionable subtasks.

Task Title: {task_title}
Task Description: {task_description or 'N/A'}

Return ONLY valid JSON — an array of objects with "title" and "description" keys.
Example: [{{"title": "...", "description": "..."}}, ...]"""
    try:
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        # Strip markdown fences if present
        if text.startswith('```'):
            text = text.split('\n', 1)[1]
            text = text.rsplit('```', 1)[0]
        return json.loads(text)
    except Exception as e:
        print(f"[AI] subtask generation error: {e}")
        return []

def summarize_chat(message_list: list[dict]) -> str:
    """Summarize a list of chat messages into 3 bullet points."""
    model = _get_client()
    if not model:
        return "AI not configured."
    formatted = "\n".join([f"{m['sender']}: {m['content']}" for m in message_list])
    prompt = f"""Summarize the following team chat into exactly 3 concise bullet points.
Focus on decisions made, action items, and key information shared.

Chat transcript:
{formatted}

Return ONLY the 3 bullet points, one per line, starting with "•"."""
    try:
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        return f"AI summarization failed: {e}"
