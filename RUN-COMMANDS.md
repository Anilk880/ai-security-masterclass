# Setup Session — Run Commands (Section 1)

Every command you need to complete Section 1's setup, in order. For the
detailed, explained walkthrough of each step, see
[`SETUP.md`](./SETUP.md). For the run command of every later course
section (2 onward), see [`code/RUN-COMMANDS.md`](./code/RUN-COMMANDS.md) —
that file is out of scope for this setup session.

> **Windows users:** run every command below inside a **WSL/Ubuntu**
> terminal, not PowerShell or Command Prompt. See `SETUP.md` Step 1 to
> install WSL first.

---

### 1. Install WSL (Windows only — skip on Ubuntu/Linux)

| | |
|---|---|
| **Purpose** | Gives Windows a real Linux terminal, matching what this course's Python tooling expects. |
| **Command** | `wsl --install` (run in an **Administrator** PowerShell), then restart your PC. |
| **Expected output** | Windows installs the WSL kernel and Ubuntu; after restart, an Ubuntu terminal opens and prompts you to create a UNIX username/password. |
| **Common errors** | `WSL is not supported`; `wsl --install` not recognized. |
| **Troubleshooting** | Enable virtualization (Intel VT-x / AMD-V) in your BIOS/UEFI; run Windows Update, then retry. |

---

### 2. Install Git

| | |
|---|---|
| **Purpose** | Needed to clone the course repository. |
| **Command** | `sudo apt update && sudo apt install -y git` |
| **Expected output** | Package list updates, then `git` installs with a "Setting up git ..." confirmation line. |
| **Common errors** | Network/DNS errors during `apt update`. |
| **Troubleshooting** | Check your internet connection; if on a corporate network, configure `apt`'s proxy settings first. |

**Verify:**

| | |
|---|---|
| **Command** | `git --version` |
| **Expected output** | `git version 2.x.x` (any recent version) |
| **Common errors** | `git: command not found` |
| **Troubleshooting** | Close and reopen your terminal, or run `hash -r`. |

---

### 3. Clone the repository

| | |
|---|---|
| **Purpose** | Downloads this course's code and docs onto your machine. |
| **Command** | `git clone https://github.com/Anilk880/ai-security-masterclass.git && cd ai-security-masterclass` |
| **Expected output** | `Cloning into 'ai-security-masterclass'...` followed by object/receive progress, then a shell prompt back inside the new folder. |
| **Common errors** | `Repository not found`; `Could not resolve host`. |
| **Troubleshooting** | Double-check the URL; check your network connection. No git available? Use GitHub's "Code" → "Download ZIP" button instead and extract it. |

---

### 4. Verify Python version

| | |
|---|---|
| **Purpose** | Confirms Python 3.9+ is available before installing anything else. |
| **Command** | `python3 --version` |
| **Expected output** | `Python 3.9.x` or newer |
| **Common errors** | `python3: command not found`; version below 3.9 |
| **Troubleshooting** | `sudo apt install -y python3 python3-venv python3-pip`; if too old, install a newer version (e.g. `sudo apt install -y python3.11`) and use that binary name in place of `python3` below. |

---

### 5. Create the virtual environment

| | |
|---|---|
| **Purpose** | Creates an isolated, project-local Python environment so this course's packages don't collide with anything else on your system. |
| **Command** | `python3 -m venv .venv` |
| **Expected output** | No output on success; a new `.venv/` folder appears in the repo root. |
| **Common errors** | `ensurepip is not available` |
| **Troubleshooting** | `sudo apt install -y python3-venv`, then retry. |

---

### 6. Activate the virtual environment

| | |
|---|---|
| **Purpose** | Switches your terminal to use the project's isolated Python and packages. |
| **Command** | `source .venv/bin/activate` |
| **Expected output** | Your prompt now starts with `(.venv)` |
| **Common errors** | Prompt doesn't change; `permission denied` |
| **Troubleshooting** | Make sure you used `source` (not executing the script directly) in `bash`/`zsh`; if permission denied, `chmod +x .venv/bin/activate` then retry. |

> **Note:** you must re-run this command every time you open a new terminal
> for this course. Forgetting it is the #1 cause of "module not found"
> errors below.

---

### 7. Install dependencies

| | |
|---|---|
| **Purpose** | Installs the packages every code example needs: `openai`, `python-dotenv`, `tiktoken`, `pytest`. |
| **Command** | `pip install -r requirements.txt` |
| **Expected output** | Ends with `Successfully installed openai-... python-dotenv-... tiktoken-... pytest-...` |
| **Common errors** | `pip: command not found`; network timeout; native-extension build failure |
| **Troubleshooting** | Re-activate the venv (Step 6) if `pip` isn't found; check your connection/proxy for timeouts; `sudo apt install -y build-essential python3-dev` if a package fails to compile. |

**Verify:**

| | |
|---|---|
| **Command** | `pip list \| grep -Ei "openai\|dotenv\|tiktoken\|pytest"` |
| **Expected output** | Four lines, each package name with a version number |

---

### 8. Configure environment variables

| | |
|---|---|
| **Purpose** | Creates your local `.env` file (gitignored) from the tracked template. |
| **Command** | `cp .env.example .env` |
| **Expected output** | No output; `.env` now exists in the repo root. |
| **Common errors** | `.env.example: No such file or directory` |
| **Troubleshooting** | Make sure you're in the repo root (`ls` should show `README.md`, `requirements.txt`, `.env.example`). |

Then edit `.env` (`code .env`, `nano .env`, or any editor) and either:

- Paste a real key: `OPENAI_API_KEY=sk-...` (get one at
  https://platform.openai.com/api-keys), keep `LLM_BACKEND=openai`, **or**
- Run fully offline: set `LLM_BACKEND=dummy` (no key needed).

**Verify `.env` is gitignored (your key will never be committed):**

| | |
|---|---|
| **Command** | `git check-ignore -v .env` |
| **Expected output** | Prints the matching `.gitignore` rule and the path `.env` |
| **Common errors** | No output at all |
| **Troubleshooting** | No output means `.env` is *not* ignored — stop and check you're inside the correct cloned repo before continuing; do not commit a real key. |

---

### 9. Run the verification script (first example)

| | |
|---|---|
| **Purpose** | Confirms every previous step worked end-to-end, with either a real OpenAI call or a fully offline dummy reply. |
| **Command** | `python3 code/00-setup/hello_openai.py` |
| **Expected output (real key)** | `Model used: gpt-4o-mini` then `Model replied: setup ok` |
| **Expected output (dummy mode)** | `[common.py] LLM_BACKEND=dummy -- running offline, no API key used, static replies.` then `Model used: gpt-4o-mini` and `Model replied: setup ok` |
| **Common errors** | `LLM_BACKEND=openai but no real OpenAI API key found`; `AuthenticationError`/`401`; `ModuleNotFoundError: No module named 'openai'`; `RateLimitError`/`429` |
| **Troubleshooting** | Paste a real key or set `LLM_BACKEND=dummy`; regenerate an invalid/revoked key; re-activate the venv and reinstall dependencies (Steps 6–7); add billing credit to your OpenAI account or switch to dummy mode. |

If you see `Model replied: setup ok`, Section 1 is complete — you're ready
for Section 2. Every later section's run command lives in
[`code/RUN-COMMANDS.md`](./code/RUN-COMMANDS.md).
