"""
openai_client.py -- Sends the sanitized prompt to OpenAI's Chat Completions
API and returns the model's reply text.

Adapted for this course: the real, deployed gateway fetches its API key
from a shared secret store, common to every server instance. This course
has no shared server to hold a key like that -- each student runs this
locally with their own key, so this copy delegates to code/common.py, the
same real/dummy client every other example in this course uses. Set your
own OPENAI_API_KEY in .env (see the setup section), or leave it unset to
run fully offline against the dummy backend -- this file doesn't know or
care which one it's actually talking to, same as everywhere else in this
course.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from common import client, MODEL  # noqa: E402


class OpenAIError(Exception):
    """Raised when the call to OpenAI fails for any reason (network, timeout, bad response)."""
    pass


def ask(prompt):
    """Sends `prompt` to the configured model and returns its reply text,
    or raises OpenAIError if the request fails.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
    except Exception:
        # Deliberately not chaining/logging the original exception: it can
        # contain request details, including the Authorization header, in
        # its message. Never let a secret-bearing string reach logs or a
        # response body -- same discipline as the real gateway's version.
        raise OpenAIError("openai_request_failed") from None

    return response.choices[0].message.content
