"""
An offline, no-network, no-API-key dummy LLM backend -- lets any student
without OpenAI budget or access still run and read the output of every code
example in this course. It mimics the exact shape of the real OpenAI client
(`.chat.completions.create(...)` -> `.choices[0].message.content`), so no
example script needs an if/else for which backend it's talking to -- see
common.py, which picks the backend once and hands back whichever client
matches this same interface.

Replies are static, clearly labeled as simulated, and never claim to be a
real model's judgment -- the point is "you can run and read the code," not
"this imitates GPT accurately."
"""

STATIC_REPLY = (
    "[DUMMY LLM -- offline mode, no API key used] "
    "This is a fixed placeholder reply, not a real model's output. "
    "Set LLM_BACKEND=openai in your .env (with a real OPENAI_API_KEY) "
    "to see this example run against an actual model."
)


class _Message:
    def __init__(self, content):
        self.content = content


class _Choice:
    def __init__(self, content):
        self.message = _Message(content)


class _ChatCompletionResponse:
    def __init__(self, content):
        self.choices = [_Choice(content)]


class _Completions:
    def create(self, model=None, messages=None, **kwargs):
        reply = self._reply_for(messages or [])
        return _ChatCompletionResponse(reply)

    @staticmethod
    def _reply_for(messages):
        # One deliberate exception to "always static": the Section 1 setup
        # verification script asks the model to echo an exact phrase back --
        # honoring that keeps "run the setup check" meaningful in dummy mode
        # instead of always failing it.
        last_user_text = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_text = m.get("content", "")
                break
        marker = "reply with exactly:"
        lower = last_user_text.lower()
        if marker in lower:
            idx = lower.index(marker) + len(marker)
            return last_user_text[idx:].strip()
        return STATIC_REPLY


class _Chat:
    def __init__(self):
        self.completions = _Completions()


class _EmbeddingData:
    def __init__(self, embedding):
        self.embedding = embedding


class _EmbeddingResponse:
    def __init__(self, vectors):
        self.data = [_EmbeddingData(v) for v in vectors]


class _Embeddings:
    def create(self, model=None, input=None, **kwargs):
        texts = input if isinstance(input, list) else [input]
        return _EmbeddingResponse([self._fake_vector(t) for t in texts])

    @staticmethod
    def _fake_vector(text, dims=16):
        # Deterministic, offline stand-in -- hashes the text into a fixed
        # vector so cosine-similarity code runs and produces *a* number,
        # but this is NOT a real embedding: it carries no semantic meaning,
        # unlike the real API's vectors, which land similar text nearby.
        import hashlib

        digest = hashlib.sha256(text.encode()).digest()
        return [b / 255.0 for b in digest[:dims]]


class DummyOpenAI:
    """Drop-in stand-in for openai.OpenAI() -- same attribute shape, zero
    network calls, zero API key required."""

    def __init__(self, *args, **kwargs):
        self.chat = _Chat()
        self.embeddings = _Embeddings()
