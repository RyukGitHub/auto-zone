# ACH Automation Project

This repository contains an automated testing suite built with Robot Framework and Playwright. Key capabilities include:
- Verifying site configurations
- Validating the join flow and modal interactions
- Secure checkout processes, focusing extensively on ACH payments.

## Project Structure

- `tests/`: Contains the test cases (e.g., `join.robot`). 
- `resources/`: Contains the core setup for the automation framework.
  - `keywords.robot`: Reusable keywords for navigating the site, interacting with modals, and filling out forms.
  - `Generator.py`: Python module providing mathematically valid routing/account numbers and dynamic test data.
  - `TelegramNotifier.py`: Python handler mapping site tags and dispatching bot notifications on completion.
  - `sites/`: Site-specific configurations and variables (e.g., `nfbusty.robot`, `momlover.robot`, `thepovgod.robot`, `deeplush.robot`).
- `.github/workflows/`: GitHub Actions workflows for running tests automatically.

## Requirements

**CRITICAL RULE:** Do not install anything globally or in your user path. Everything MUST be installed within the project's virtual environment (`.venv`).

**1. Activate the Virtual Environment:**
Depending on your terminal, run ONE of the following from the `ach` project root:
```bash
# On Git Bash / Linux / macOS
source .venv/Scripts/activate

# On Windows Command Prompt
.venv\Scripts\activate

# On Windows PowerShell
.venv\Scripts\Activate.ps1
```

**2. Install Dependencies (while activated):**
All new installations should exclusively use `python -m pip` to ensure they stay trapped in the virtual environment.

```bash
# Install requirements
python -m pip install -r requirements.txt

# Make sure Browser modules are installed
python -m Browser.entry init
```

## Telegram Notifications

A custom Python script evaluates tests on completion and sends an alert via a Telegram bot if the test passed. 
To enable this locally, create a `.env` file at the root of the project with the following variables:
```env
TELEGRAM_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```
*Note: The `.env` file is ignored by Git to prevent leaking tokens. For GitHub Actions, add `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` as Repository Secrets.*

## Running Tests

To run the test suite, ensure your **virtual environment is active**, and use the `python -m` module executor to avoid any PATH issues:

```bash
python -m robot -d results tests/
```

**Dynamic Credentials:**
By default, the framework mathematically generates a valid routing number (`RTNO`) and account number (`ACNO`) prefixed string upon each run. You can optionally override this by passing specific variables via command line or the GitHub Actions dispatch form:
```bash
python -m robot -d results -t TC01 --variable ACNO:98765432 --variable RTNO:063201875 tests/join.robot
```

Results (including `log.html`, `report.html`, and `output.xml`) will be automatically stored in the `results/` directory, which is excluded from version control.

## Render Deployment

To host this repository 24/7 as a background bot on [Render.com](https://render.com), you must deploy it as a **Web Service**. Render will shut down raw scripts unless they bind to an HTTP port, so a lightweight `app.py` Flask server has been added to keep the service "Awake".

When deploying on Render, use the following configurations:

* **Environment**: `Python 3`
* **Build Command**: `pip install -r requirements.txt && python -m Browser.entry init`
* **Start Command**: `gunicorn app:app`
* **Environment Variables**: Make sure to add `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` so production alerts work.

### Keeping the Bot Alive (Free Tier)
If you deploy on the Free Tier, Render spins down the service after 15 minutes of inactivity. To prevent this, go to a free service like [cron-job.org](https://cron-job.org) or [UptimeRobot](https://uptimerobot.com) and set up a ping every 10 minutes to:
`https://your-render-app-url.onrender.com/ping`

*(Note: The `app.py` server also has an optional `/run-tests` endpoint which you can hit via HTTP to remotely trigger tests without SSH!)*
