"""
Section 3 -- Tokens & Embeddings: a live demo of both.

Part 1: real tokenization with tiktoken, the same tokenizer OpenAI's
models use -- shows a common word splitting into multiple tokens.

Part 2: real embeddings via the OpenAI API (or the dummy backend's
deterministic stand-in), showing that semantically similar sentences
land close together in vector space, and an unrelated one lands far away
-- the exact mechanism RAG and vector databases are built on.

Run: python3 code/03-ai-ml-foundations/tokens_embeddings_demo.py
"""
import math
import os
import sys

import tiktoken

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import client, MODEL  # noqa: E402

# --- Part 1: tokenization ---
encoding = tiktoken.encoding_for_model("gpt-4o-mini")

WORD = "cybersecurity"
tokens = encoding.encode(WORD)

print("=== Tokenization ===")
print(f"Word: {WORD!r}")
print(f"Token count: {len(tokens)}")
print("Token pieces:", [encoding.decode([t]) for t in tokens])

SENTENCE = "AI security is a genuinely new discipline."
sentence_tokens = encoding.encode(SENTENCE)
print()
print(f"Sentence: {SENTENCE!r}")
print(f"Token count: {len(sentence_tokens)} (for {len(SENTENCE)} characters)")

# --- Part 2: embeddings + cosine similarity ---


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


SENTENCES = [
    "The dog ran across the park.",
    "A puppy sprinted through the yard.",
    "Quarterly revenue exceeded analyst expectations.",
]

response = client.embeddings.create(model="text-embedding-3-small", input=SENTENCES)
vectors = [d.embedding for d in response.data]

print()
print("=== Embeddings + Cosine Similarity ===")
for s in SENTENCES:
    print(" -", s)

sim_dog_puppy = cosine_similarity(vectors[0], vectors[1])
sim_dog_revenue = cosine_similarity(vectors[0], vectors[2])

print()
print(f"similarity(dog sentence, puppy sentence)    = {sim_dog_puppy:.4f}")
print(f"similarity(dog sentence, revenue sentence)  = {sim_dog_revenue:.4f}")
print()
if sim_dog_puppy > sim_dog_revenue:
    print("The two semantically related sentences scored higher -- this is")
    print("the exact mechanism RAG retrieval and vector databases run on.")
else:
    print("(Running in dummy mode: these vectors are a deterministic hash,")
    print("not real embeddings, so similarity here isn't semantically meaningful.)")
