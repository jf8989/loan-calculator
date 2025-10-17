# Path: docs/RUNBOOK.md

````markdown
# Loan Calculator — Runbook (Local & Vercel)

A tiny checklist to run locally on any machine and redeploy to Vercel without guessing.

---

## Prerequisites
- **Python 3.12** installed (important: pandas 2.2.2 doesn’t have wheels for 3.13 on Windows).
- Git + VS Code (optional but recommended).
- (For CLI deploys) Node.js + `vercel` CLI.

---

## First-Time Setup (per machine)

### 1) Create a Python 3.12 virtual environment
**Windows (PowerShell):**
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
````

**macOS / Linux:**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

### 2) Install Python dependencies

```bash
pip install --only-binary=:all: pandas==2.2.2 Flask==3.0.3 gunicorn==20.1.0
# or simply:
pip install -r requirements.txt
```

> If you see pandas trying to “compile Cython source,” you’re on the wrong Python (3.13). Use 3.12.

### 3) (VS Code) Select the interpreter

Command Palette → **Python: Select Interpreter** → pick the one inside `.venv`.

Optional pin:

```json
// .vscode/settings.json
{ "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe" }
```

(macOS/Linux: `.../.venv/bin/python`)

---

## Everyday Use — Local Run

1. Activate the venv
   **Windows**

   ```powershell
   .\.venv\Scripts\activate
   ```

   **macOS/Linux**

   ```bash
   source .venv/bin/activate
   ```

2. Start the app

```bash
python app.py
```

3. Open the app

   * ES: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
   * EN: [http://127.0.0.1:5000/en](http://127.0.0.1:5000/en)

4. Stop the app: `Ctrl+C` in the terminal.

5. Deactivate venv (optional): `deactivate`.

---

## Vercel Deploy

You can use **GitHub auto-deploys** or the **Vercel CLI**. This repo already includes `vercel.json`.

### A) GitHub → Vercel (recommended)

1. Commit & push to your main branch.
2. In Vercel, link the repo (if not already).
3. Each push triggers a build and deploy automatically.

### B) Vercel CLI

```bash
# one-time login
npm i -g vercel
vercel login

# preview deployment
vercel

# production deployment
vercel --prod
```

**Notes**

* Vercel reads `requirements.txt` and builds a Python serverless entry from `app.py` per `vercel.json`.
* `gunicorn` is present for other hosts, but on Vercel you just keep `app.py` and `vercel.json` as is.

---

## Troubleshooting Cheatsheet

* **Pylance: “Import ‘flask/pandas’ could not be resolved”**
  VS Code is pointing at the wrong interpreter. Re-select the `.venv` one.

* **Pandas tries to compile on Windows**
  You’re using Python 3.13. Recreate the venv with 3.12:

  ```powershell
  deactivate; Remove-Item -Recurse -Force .venv
  py -3.12 -m venv .venv
  .\.venv\Scripts\activate
  pip install -r requirements.txt
  ```

* **Port already in use**
  Something else is on `5000`. Either stop it or run:

  ```bash
  set FLASK_RUN_PORT=5050  # Windows PowerShell: $env:FLASK_RUN_PORT=5050
  python app.py
  ```

* **Windows run vs Vercel**
  Locally you run `python app.py`. On Vercel, deployment is handled via `vercel.json`; no `gunicorn` command needed.

---

## Quick Sanity Test (math)

Try:

* Principal: 10,000
* APR: 12%
* Term: 24 months
* Fixed: leave empty (or computed)
* Extra: 0

Base payment should be ≈ **$470.73**, original interest ≈ **$1,297.63**.
Add **$100 extra** → payoff ≈ **~20 months**, interest smaller.

---

## Clean Up

* Remove venv:
  **Windows:** `deactivate; Remove-Item -Recurse -Force .venv`
  **macOS/Linux:** `deactivate; rm -rf .venv`
