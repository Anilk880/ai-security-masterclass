"""
Shared helper for every code example in this course. Loads your API key from
.env (never from a hardcoded string) and gives you a ready-to-use OpenAI
client, so each lecture's example script stays short and focused on the
security concept it's demonstrating, not on setup boilerplate.

Two backends, same interface -- no OpenAI account required to follow along:

- "openai"  -- real calls to the OpenAI API. Set LLM_BACKEND=openai and a
              real OPENAI_API_KEY in .env.
- "dummy"   -- offline, no network, no key. Set LLM_BACKEND=dummy, or just
              leave OPENAI_API_KEY unset -- that's the automatic fallback,
              so a student with no API budget can still run and read every
              example's output, not just skip them.

Every example script imports `client` and `MODEL` and never has to know or
care which backend is actually behind them -- see dummy_llm.py for why that
works (it mimics the real client's exact shape).

Usage in any example script:
    from common import client, MODEL
    resp = client.chat.completions.create(model=MODEL, messages=[...])
"""
import os

from dotenv import load_dotenv

from dummy_llm import DummyOpenAI

load_dotenv()

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

_API_KEY = os.environ.get("OPENAI_API_KEY")
_HAS_REAL_KEY = bool(_API_KEY) and not _API_KEY.startswith("sk-your-own-key-here")
_BACKEND = os.environ.get("LLM_BACKEND", "openai" if _HAS_REAL_KEY else "dummy").strip().lower()

if _BACKEND == "dummy":
    print("[common.py] LLM_BACKEND=dummy -- running offline, no API key used, static replies.")
    client = DummyOpenAI()
else:
    if not _HAS_REAL_KEY:
        import sys
        sys.exit(
            "LLM_BACKEND=openai but no real OpenAI API key found.\n"
            "1. Copy .env.example to .env (in the ai-security-masterclass folder)\n"
            "2. Put your real key in .env as OPENAI_API_KEY=sk-...\n"
            "   Get a key at https://platform.openai.com/api-keys\n"
            "-- or set LLM_BACKEND=dummy in .env to run fully offline instead."
        )
    from openai import OpenAI
    client = OpenAI(api_key=_API_KEY)
