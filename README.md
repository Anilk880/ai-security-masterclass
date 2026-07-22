# AI Security Masterclass: Secure LLMs & AI Agents

A 15-section course on AI security. Sections 0-4 are conceptual grounding
(what AI is, how it differs from traditional AppSec, ML/LLM foundations).
Sections 5-14 are entirely code-grounded: each one teaches a real,
production-grade AI gateway guard — rate limiting, prompt injection,
secrets detection, PII redaction, evasion-resistant scanning, cost/DoS
guarding, safe audit logging, supply chain checking, and agent tool
guardrails — by reading, running, and breaking its actual source in
[`code/production-reference/`](./code/production-reference), not a
simplified teaching toy. The capstone section wires all nine guards into
one real request pipeline and runs its real 84-test suite live. See
[`COURSE-OUTLINE.md`](./COURSE-OUTLINE.md) for the full curriculum.

Every section ships a runnable Python example under [`code/`](./code) —
**that folder is what this repo's GitHub page is really for.** The lecture
videos live on Udemy; this repo exists so you can clone it, read the exact
code shown on screen, and run it yourself, with or without your own OpenAI
key. Everything else in this repo (`script-*.md`, `*.pptx`, `shared/`) is
course-production material, not something you need to touch as a student —
`code/` is the actual deliverable here.

**Public repo:** https://github.com/Anilk880/ai-security-masterclass — **code
only.** Only the `code/` folder (plus `README.md`, `requirements.txt`, and
`.env.example` so it's runnable on its own) gets pushed there. Course
material — `script-*.md`, `*.pptx`, `audio/`, `video/`, `shared/`,
`COURSE-OUTLINE.md` — stays out of that push; it's production material, not
something a student browsing the public repo needs to see.

## Setup (Section 1, do this once before Section 2)

Section 1 is a short, one-time setup session, not course content — its whole
job is to get you from "just cloned this repo" to "every later lecture's
code just runs" in five steps. By the end of it you'll have a real Linux
terminal (WSL on Windows, native on Ubuntu/Linux), Python 3.9+, this repo's
dependencies installed in an isolated virtual environment, and either a real
OpenAI API key or fully offline **dummy mode** configured and verified with
a live test run. Nothing here is course-specific to AI security yet — it's
the same setup any Python project would need.

- **Full, beginner-friendly walkthrough** (every step explained, with
  troubleshooting and a readiness checklist): [`SETUP.md`](./SETUP.md)
- **Command-only quick reference** for this setup session: [`RUN-COMMANDS.md`](./RUN-COMMANDS.md)

The condensed version, if you just want the commands:

**Windows users: install WSL first.** If you're on Windows, set up
[WSL](https://learn.microsoft.com/windows/wsl/install) (`wsl --install` in an
administrator PowerShell, then restart) before doing anything else below, and
do the rest of this setup *inside* the WSL terminal (e.g. Ubuntu), not
PowerShell/CMD. Nearly every package this course and its code examples touch
— Python build tooling, `pip` packages with native extensions, `ffmpeg` if you
later generate audio/video versions of the lectures — installs more reliably
and matches what real Linux servers run in production, which is where AI
security tooling actually gets deployed. Ubuntu/Linux users can skip straight
to step 1.

1. **Python 3.9+** — check with `python3 --version`.
2. **Create a virtual environment and install dependencies:**
   ```bash
   cd ai-security-masterclass
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Get an OpenAI API key** at https://platform.openai.com/api-keys (a few
   of this course's live demos call a real model — a `gpt-4o-mini`-scale key
   with a few dollars of credit is more than enough for every example here).
   This is optional — every example also runs fully offline against a dummy
   backend with zero key, zero network call, and zero cost. Most of Sections
   5-14's guard demos don't call a model at all; they're pure pattern-
   matching functions, so they're identical either way.
4. **Copy `.env.example` to `.env`** and put your real key in it:
   ```bash
   cp .env.example .env
   # then edit .env and set OPENAI_API_KEY=sk-...
   ```
   `.env` is gitignored — your key never gets committed, even if you fork
   and push this repo yourself.
5. **Confirm it works:**
   ```bash
   python3 code/00-setup/hello_openai.py
   ```
   Expected output ends with `Model replied: setup ok`. If that printed, you're
   ready for every code example in this course.

Stuck on any step? [`SETUP.md`](./SETUP.md) has the detailed version of
each one plus a troubleshooting entry for the most common errors.

## Run the capstone gateway

[`code/production-reference/`](./code/production-reference) is a real,
production-grade AI gateway's actual source — not a simplified rebuild.
`src/handler.py` wires every guard this course covers (rate limiting,
prompt injection, secrets detection, PII redaction, cost guarding, and
egress scanning) into one real request pipeline.

Run its real test suite — 84 tests, no cloud account, no OpenAI key required:

```bash
cd code/production-reference
python3 -m pytest tests/ -v
```

Or drive the pipeline directly, the same way Section 14's lectures do:

```bash
python3 code/14-capstone-mini-gateway/handler_demo.py
```

That sends four real requests through `handler.handler()` — one with no
auth, one carrying a prompt injection attempt, one carrying a leaked AWS
key, and one ordinary request carrying an email address — and prints each
guard's real, live verdict.

## Repo layout

```
ai-security-masterclass/
  COURSE-OUTLINE.md       <- full curriculum, section by section
  README.md               <- this file
  requirements.txt
  .env.example             <- copy to .env, add your own key
  code/
    common.py               <- shared OpenAI client helper, used by every example
    00-setup/
      hello_openai.py         <- verifies your setup
    NN-section-slug/
      *.py                     <- runnable examples for Sections 2-13, one demo per section
    production-reference/
      src/                     <- the real gateway's guard modules, unmodified
      scripts/                 <- check_dependencies.py, the supply-chain check
      tests/                   <- its real 84-test suite
  <NN-section-slug>/
    script-LN.md             <- narration/slide script for each lecture
    slides-LN.pptx             <- generated slide deck
```
