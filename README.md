# ACH Automation Project

This repository contains an automated testing suite built with Robot Framework and Playwright. Key capabilities include:
- Verifying site configurations
- Validating the join flow and modal interactions
- Secure checkout processes, focusing extensively on ACH payments.

## Project Structure

- `tests/`: Contains the test cases (e.g., `join.robot`). 
- `resources/`: Contains the core setup for the automation framework.
  - `keywords.robot`: Reusable keywords for navigating the site, interacting with modals, and filling out forms.
  - `sites/`: Site-specific configurations and variables (e.g., `nfbusty.robot`, `momlover.robot`, `anilos.robot`).
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

## Discord Notifications

A custom Python script evaluates tests on completion and sends an alert to a Discord channel if the test passed. 
To enable this locally, create a `.env` file at the root of the project with the following variable:
```env
ACH_DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```
*Note: The `.env` file is ignored by Git to prevent leaking webhooks. For GitHub Actions, add `ACH_DISCORD_WEBHOOK_URL` as a Repository Secret.*

## Running Tests

To run the test suite, ensure your **virtual environment is active**, and use the `python -m` module executor to avoid any PATH issues:

```bash
python -m robot -d results tests/
```

Results (including `log.html`, `report.html`, and `output.xml`) will be automatically stored in the `results/` directory, which is excluded from version control.
