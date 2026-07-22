# Setup Guide (Section 1)

This is the full, beginner-friendly setup guide for **Section 1** of the AI
Security Masterclass. If you've never set up a Python project before, or
you're new to WSL/Linux, follow every step in order — nothing here is
optional except the OpenAI API key.

For a quick command-only reference (no explanations), see
[`RUN-COMMANDS.md`](./RUN-COMMANDS.md). For the short version, see the
[Setup section of the README](./README.md#setup-section-1-do-this-once-before-section-2).

> **Scope note:** this guide covers **Windows (via WSL) and
> Ubuntu/Linux** — the two environments this course is built and tested on.
> macOS users can follow the Ubuntu/Linux steps almost verbatim (swap `apt`
> for `brew`); there's nothing OS-specific in this course's code.

---

## What you'll accomplish in this section

By the end of Section 1, you will have:

1. A real Linux terminal environment (WSL on Windows, or native on
   Ubuntu/Linux) ready for the rest of this course.
2. Git and Python 3.9+ installed and verified.
3. This repository cloned onto your machine.
4. A project-local **virtual environment** with every Python dependency this
   course needs, installed and isolated from your system Python.
5. VS Code installed and connected to that environment.
6. A working `.env` file — either with your own OpenAI API key, or
   configured to run every example fully offline in **dummy mode**.
7. A verified, working setup, confirmed by running one real script.

## The environment you're building

Every code example in this course is a small, self-contained Python script.
There's no database, no Docker, no cloud account required. The stack is
deliberately minimal:

| Piece | Purpose |
|---|---|
| **WSL (Windows only)** | A real Linux environment inside Windows. Python packages with native extensions install more reliably here, and it matches what real production AI security tooling runs on. |
| **Python 3.9+** | The language every example is written in. |
| **`venv`** | An isolated, project-local set of installed packages, so this course's dependencies never collide with anything else on your machine. |
| **`pip` + `requirements.txt`** | Installs the handful of packages this course depends on (`openai`, `python-dotenv`, `tiktoken`, `pytest`). |
| **Git** | Used to clone this repository (and optionally track your own changes). |
| **VS Code** (recommended) | The editor used throughout the course's lectures. Any editor works — VS Code is just what's shown on screen. |
| **`.env` file** | Holds your OpenAI API key (optional) and a couple of config flags. Never committed to git. |

Once this is done, **every later section in this course reuses this exact
setup** — you won't repeat any of this.

---

## Step 1 — Windows users: install WSL first

> **Skip this step entirely if you're on Ubuntu/Linux (or macOS).** Go to
> [Step 2](#step-2--install-and-verify-git).

WSL (Windows Subsystem for Linux) gives you a genuine Ubuntu terminal running
inside Windows. Do every remaining step of this guide *inside* that Ubuntu
terminal — not PowerShell or Command Prompt.

1. Open **PowerShell as Administrator** (right-click the Start button →
   "Terminal (Admin)" or "Windows PowerShell (Admin)").
2. Run:
   ```powershell
   wsl --install
   ```
3. Restart your computer when prompted.
4. After restart, an Ubuntu terminal window opens automatically the first
   time (or search "Ubuntu" in the Start menu). It will ask you to create a
   **UNIX username and password** — this is separate from your Windows
   login and only exists inside WSL. Pick anything memorable; you'll use
   this password for `sudo` commands later.

**Verify it worked:**
```bash
wsl --version
```
Expected output: version numbers for WSL, the kernel, and Ubuntu — no
errors.

Inside the Ubuntu terminal, also confirm the distribution:
```bash
lsb_release -a
```
Expected output includes a line like `Distributor ID: Ubuntu`.

> **Tip:** From now on, open "Ubuntu" (or your WSL distro) from the Start
> menu whenever you want to work on this course — that's your Linux
> terminal.

> **Troubleshooting:**
> - `wsl --install` fails with "WSL is not supported" → your Windows version
>   is too old, or virtualization is disabled in your BIOS/UEFI. Enable
>   "Virtualization Technology" (sometimes called Intel VT-x / AMD-V) in
>   your BIOS settings, then retry.
> - Nothing opens after restart → open Start menu, search "Ubuntu", launch
>   it manually.
> - `wsl --install` says the command isn't recognized → your Windows build
>   is outdated; run Windows Update first, then retry.

---

## Step 2 — Install and verify Git

**Ubuntu/Linux (and inside WSL):**
```bash
sudo apt update
sudo apt install -y git
```

**Verify:**
```bash
git --version
```
Expected output: something like `git version 2.43.0` (exact version
doesn't matter, any recent version works).

Set your identity once (used for commit authorship if you make your own
commits — optional, but good practice):
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

> **Troubleshooting:**
> - `sudo apt update` fails with a network error → check your internet
>   connection; if you're behind a corporate proxy, you'll need to configure
>   `apt`'s proxy settings first.
> - `git: command not found` after installing → close and reopen your
>   terminal, or run `hash -r` to refresh your shell's command cache.

---

## Step 3 — Clone the course repository

Pick a folder you're comfortable working in, then:

```bash
git clone https://github.com/Anilk880/ai-security-masterclass.git
cd ai-security-masterclass
```

No git, or don't want to install it? On the GitHub page for this repo,
click the green **"Code"** button → **"Download ZIP"**, then extract it and
open a terminal inside the extracted folder instead.

**Verify:**
```bash
ls code
```
Expected output includes `common.py`, `00-setup/`, and a folder per course
section (`02-ai-security-fundamentals/`, `05-rate-limiting/`, etc.).

> Every command in the rest of this course assumes your terminal is sitting
> inside this `ai-security-masterclass/` folder.

---

## Step 4 — Check (or install) Python 3.9+

**Check what you already have:**
```bash
python3 --version
```
Expected output: `Python 3.9.x` or newer. Anything below 3.9, install a
newer version (below).

**Install/upgrade on Ubuntu/WSL, if needed:**
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

**Verify `venv` and `pip` are available:**
```bash
python3 -m venv --help
python3 -m pip --version
```
Both should print usage/version info with no errors.

> **Troubleshooting:**
> - `python3: command not found` → Ubuntu/WSL images usually ship Python 3
>   already; if genuinely missing, `sudo apt install -y python3` fixes it.
> - `python3 -m venv` fails with "ensurepip is not available" → run
>   `sudo apt install -y python3-venv`, then retry.
> - Version shows below 3.9 → `sudo apt install -y python3.11` (or whatever
>   recent version your distro offers), then use `python3.11` in place of
>   `python3` for the remaining steps.

---

## Step 5 — Install VS Code (recommended)

Any editor works for this course — VS Code is simply what the lectures show
on screen.

**Windows users (WSL setup):** install VS Code on the **Windows side**
(download from https://code.visualstudio.com/), then install the
**"WSL"** extension from the Extensions panel (`Ctrl+Shift+X`, search
"WSL"). From your WSL terminal, inside the cloned repo folder, run:
```bash
code .
```
The first time, this installs a small VS Code server inside WSL and opens
the folder in a window connected to your Linux environment — confirmed by
`WSL: Ubuntu` shown in the bottom-left corner of the VS Code window.

**Ubuntu/Linux users:** download and install VS Code for Linux from
https://code.visualstudio.com/, or `sudo snap install code --classic`, then
run `code .` from inside the repo folder.

**Verify:**
```bash
code --version
```
Expected output: a version number and commit hash, no errors.

> **Troubleshooting:**
> - `code: command not found` inside WSL → reopen VS Code on Windows once,
>   ensure the WSL extension is installed, then reopen your WSL terminal
>   (the `code` shim is added to your WSL `PATH` automatically on first
>   connect).

---

## Step 6 — Create and activate a virtual environment

From inside the `ai-security-masterclass/` folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Verify it's active:** your terminal prompt should now start with
`(.venv)`. You can also confirm with:
```bash
which python3
```
Expected output: a path ending in `ai-security-masterclass/.venv/bin/python3`
— not a system path like `/usr/bin/python3`.

> **Note:** you need to run `source .venv/bin/activate` again every time you
> open a new terminal to work on this course. If you close and reopen your
> terminal and commands start failing with "module not found" errors, this
> is almost always why — reactivate the virtual environment.

> **Troubleshooting:**
> - `.venv` folder created but activation does nothing / prompt unchanged →
>   make sure you used `source` (not just running the script directly), and
>   that you're in a `bash` or `zsh` shell, not `sh`.
> - `permission denied` when activating → run
>   `chmod +x .venv/bin/activate`, then retry.

---

## Step 7 — Install dependencies

With the virtual environment active:

```bash
pip install -r requirements.txt
```

Expected output ends with a line like:
```
Successfully installed openai-2.46.0 python-dotenv-1.2.2 tiktoken-0.8.0 pytest-8.3.0 ...
```
(exact versions may differ). This installs everything this course needs:
`openai`, `python-dotenv`, `tiktoken`, and `pytest`.

**Verify:**
```bash
pip list | grep -Ei "openai|dotenv|tiktoken|pytest"
```
Expected output: four lines, one per package, each with a version number.

> **Troubleshooting:**
> - `pip: command not found` → your virtual environment isn't active; redo
>   Step 6.
> - Install hangs or fails downloading → check your internet connection; if
>   you're behind a proxy, set `HTTPS_PROXY`/`HTTP_PROXY` environment
>   variables first.
> - A package fails to build with compiler errors → run
>   `sudo apt install -y build-essential python3-dev`, then retry — some
>   packages compile small native extensions and need basic build tools.
> - `pip` warns it's outdated → optional, but safe to fix with
>   `pip install --upgrade pip`.

---

## Step 8 — Configure environment variables and your API key

Copy the example file:
```bash
cp .env.example .env
```

Open `.env` in VS Code (`code .env`) or any text editor, and you'll see:
```
OPENAI_API_KEY=sk-your-own-key-here
OPENAI_MODEL=gpt-4o-mini
LLM_BACKEND=openai
```

**Option A — use a real OpenAI API key** (recommended if you have one):

1. Sign in at https://platform.openai.com/api-keys.
2. Click **"+ Create new secret key"** (top right).
3. Give it a name (e.g. "course key"), leave permissions on "All", click
   **"Create secret key"**.
4. **Copy the key immediately** — OpenAI shows it exactly once. If you
   navigate away before copying it, you must create a new key.
5. Paste it into `.env`, replacing the placeholder:
   ```
   OPENAI_API_KEY=sk-...your real key...
   ```
6. Leave `LLM_BACKEND=openai`.

A few dollars of credit is more than enough for every live demo in this
course.

**Option B — run fully offline, no key needed:**

Set:
```
LLM_BACKEND=dummy
```
or simply leave `OPENAI_API_KEY` as the placeholder / blank — that's the
automatic fallback. Every example still runs, with clearly-labeled
simulated replies instead of real model output.

> **⚠️ Warning:** `.env` is already listed in this repo's `.gitignore` and
> will never be committed. Never paste your API key into any other file,
> commit message, or chat — treat it like a password.

**Verify the file exists and is not tracked by git:**
```bash
cat .env
git check-ignore -v .env
```
Expected: `.env`'s contents print, and the second command prints a matching
`.gitignore` rule (confirming git will never commit it).

---

## Step 9 — Verify your entire setup

Run the course's setup-check script:

```bash
python3 code/00-setup/hello_openai.py
```

**Expected output, with a real key (`LLM_BACKEND=openai`):**
```
Model used: gpt-4o-mini
Model replied: setup ok
```

**Expected output, in dummy/offline mode:**
```
[common.py] LLM_BACKEND=dummy -- running offline, no API key used, static replies.
Model used: gpt-4o-mini
Model replied: setup ok
```

Either output means **you're fully set up** for the rest of this course.

> **Troubleshooting:**
> - `LLM_BACKEND=openai but no real OpenAI API key found` → your `.env`
>   still has the placeholder key, or `LLM_BACKEND` is set to `openai` with
>   no key. Either paste a real key or set `LLM_BACKEND=dummy`.
> - `AuthenticationError` / `401` from OpenAI → your key is invalid,
>   revoked, or has a typo. Generate a new key and paste it in again.
> - `ModuleNotFoundError: No module named 'openai'` → your virtual
>   environment isn't active, or Step 7 didn't complete. Run
>   `source .venv/bin/activate` then re-run Step 7.
> - `RateLimitError` / `429` → your OpenAI account has no credit. Add a
>   small amount of billing credit, or switch to `LLM_BACKEND=dummy`.
> - Script hangs with no output → check your network/firewall isn't
>   blocking `api.openai.com`; or switch to `LLM_BACKEND=dummy` to confirm
>   the rest of your setup is fine.

---

## System Ready Checklist

Before moving on to Section 2, confirm every box below:

- [ ] `wsl --version` succeeds (Windows only — skip on Ubuntu/Linux/macOS)
- [ ] `git --version` prints a version number
- [ ] Repository cloned; `ls code` shows `common.py` and per-section folders
- [ ] `python3 --version` shows 3.9 or newer
- [ ] `.venv` created; terminal prompt shows `(.venv)` after
      `source .venv/bin/activate`
- [ ] `pip list` shows `openai`, `python-dotenv`, `tiktoken`, and `pytest`
      installed
- [ ] `.env` exists (copied from `.env.example`) and either has a real
      `OPENAI_API_KEY` or `LLM_BACKEND=dummy`
- [ ] `python3 code/00-setup/hello_openai.py` prints
      `Model replied: setup ok`
- [ ] (Optional) `code --version` works, and `code .` opens this folder in
      VS Code connected to WSL/Linux

If every box is checked, you're ready for Section 2. For the full list of
commands used throughout the rest of the course, see
[`code/RUN-COMMANDS.md`](./code/RUN-COMMANDS.md).
