import os

# rag/retrieve.py and agent/chat_loop.py create an OpenAI client at import time,
# which requires an API key to be set. Tests never hit the real API.
os.environ.setdefault("OPENAI_API_KEY", "test-key")
