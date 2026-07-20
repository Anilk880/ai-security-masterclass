"""
Section 0 -- Setup: confirm your OpenAI API key actually works before the
course relies on it for live demos.

Run: python3 code/00-setup/hello_openai.py
Expected: a short, ordinary reply from the model, proving your .env is
wired up correctly. If this fails, fix it now -- every later live-demo
script in this course assumes this step already passed.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import client, MODEL  # noqa: E402

response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Reply with exactly: setup ok"}],
    max_tokens=10,
)

print("Model used:", MODEL)
print("Model replied:", response.choices[0].message.content.strip())
