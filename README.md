# WW Check-in System

Automation for WW HR portal check-in using Python + Selenium. This repo supports both local execution and Podman-based runs, including offline usage from a prebuilt image tar.

## Features

- Selenium-based login and check-in flow
- Container-first workflow (bind-mount project for easy updates without rebuilding)
- Local (non-container) execution supported
- Cron-friendly scripts for local and Podman

## Prerequisites

- A `.env` file with credentials (copy from `env.example`)
- Podman installed (for container usage)
  - macOS: `brew install podman && podman machine init && podman machine start`
  - Windows/WSL: use the `podman-wsl` wrapper if configured; or Windows Podman Machine
  - Linux: install from your distro’s package manager

## Run from prebuilt image tar (offline friendly)

1) Load the image tar

- macOS/Linux:
```bash
podman load -i ww-check-in-offline-v1.tar
```
- WSL (with wrapper):
```bash
podman-wsl load -i ww-check-in-offline-v1.tar
```

2) Run with project bind-mounted (one-shot)

```bash
# macOS/Linux
podman run --rm \
  --env-file ./.env \
  -e HEADLESS=${HEADLESS:-true} \
  -v "$PWD:/app" \
  -v "$PWD/logs:/app/logs" \
  ww-check-in:offline-v1

# WSL
podman-wsl run --rm \
  --env-file ./.env \
  -e HEADLESS=${HEADLESS:-true} \
  -v "$PWD:/app" \
  -v "$PWD/logs:/app/logs" \
  ww-check-in:offline-v1
```

3) Keep a persistent container for interactive testing (daemon)

```bash
# macOS/Linux
podman run -d --name wwci \
  --env-file ./.env \
  -e HEADLESS=${HEADLESS:-true} \
  -v "$PWD:/app" \
  -v "$PWD/logs:/app/logs" \
  ww-check-in:offline-v1 sleep infinity

# Inspect / exec
podman exec -it wwci bash
```

For WSL, replace `podman` with `podman-wsl`.

## Environment setup (setup_env/)

- Local (no container):
  - `setup_env/setup_linux_local.sh` installs Python deps (and chromedriver where possible).
  - Then run locally:
    ```bash
    HEADLESS=true python3 ww_check_in.py
    or
    HEADLESS=true python3 test_check_in_complete_v2.py
    ```

- Podman:
  - macOS/Ubuntu: ensure Podman is installed, and Podman Machine is started on macOS.
  - WSL: prefer using the `podman-wsl` wrapper (overlay on Linux paths, vfs on /mnt paths).
  - You can also (re)build the image from source, then save/load for offline use (see Notes below).

## Cron setup (cron/)

- Local cron:
  - Script: `cron/cron_check_in_local.sh`
  - Examples: `cron/crontab_setup_local.txt`
  - Sample (Mon–Thu at 08:30):
    ```cron
    30 8 * * 1-4 PROJECT_DIR=/home/you/ww_check_in HEADLESS=true /home/you/ww_check_in/cron/cron_check_in_local.sh
    ```

- Podman cron:
  - Script: `cron/cron_check_in_podman.sh`
  - Examples: `cron/crontab_setup_podman.txt`
  - One-shot example (mac/Linux):
    ```cron
30 8 * * 1-4 PROJECT_DIR=/home/you/ww_check_in HEADLESS=true IMAGE=ww-check-in:offline-v1 /home/you/ww_check_in/cron/cron_check_in_podman.sh
    ```
  - One-shot example (WSL with wrapper):
    ```cron
    30 8 * * 1-4 PROJECT_DIR=/home/you/ww_check_in HEADLESS=true PODMAN_CMD=podman-wsl IMAGE=ww-check-in:offline-v1 /home/you/ww_check_in/cron/cron_check_in_podman.sh
    ```
  - Daemon mode: ensure container exists at boot, then exec jobs inside it (see file for details).

## Running directly (without container)

- Ensure local setup via `setup_env/setup_linux_local.sh`.
- Run:
```bash
HEADLESS=true python3 ww_check_in.py
```
