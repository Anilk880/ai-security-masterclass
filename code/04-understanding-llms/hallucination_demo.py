"""
Section 4 -- Understanding LLMs & Generative AI: a live demo of hallucination.

Asks about a COMPLETELY FABRICATED research study (it does not exist -- the
title was invented for this demo). A generative model's job is to produce
fluent, plausible-sounding continuations of its input, not to fact-check
that input first. Ask it about something that sounds real but isn't, and
the risk this lecture is about becomes directly visible: it will often
invent confident, specific-sounding "findings" rather than saying it has no
information about this source.

Run: python3 code/04-understanding-llms/hallucination_demo.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import client, MODEL  # noqa: E402

# This study is entirely made up -- that's the point of the demo.
FABRICATED_QUESTION = (
    'In two sentences, what were the three main findings of the 2019 '
    'Stanford study titled "Quantum Retention Bias in Synthetic Cognition"?'
)

response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": FABRICATED_QUESTION}],
    max_tokens=120,
)

print("Question:", FABRICATED_QUESTION)
print("Reply:", response.choices[0].message.content.strip())
print()
print("Fact check: this study does not exist. Its title was invented for")
print("this demo. Any 'findings' above were generated, not retrieved.")
