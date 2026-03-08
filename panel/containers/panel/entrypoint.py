#!/usr/bin/python3

import subprocess
import sys
import os


def run_migrations():
    """Run database migrations using Alembic."""
    print("[Entrypoint] Running migrations...", flush=True)

    # Using list for security (no shell injection)
    # Using sys.executable to ensure we use the same python interpreter
    try:
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            check=True
        )
        print("[Entrypoint] Migrations completed successfully.", flush=True)
    except subprocess.CalledProcessError as e:
        print(f"[Entrypoint] Migrations failed with exit code {e.returncode}", flush=True)
        sys.exit(e.returncode)
    except Exception as e:
        print(f"[Entrypoint] An unexpected error occurred: {e}", flush=True)
        sys.exit(1)


def start_app():
    """Replace current process with the main application."""
    print("[Entrypoint] Starting application...", flush=True)

    # os.execlp replaces the current process.
    # Arguments: (file_to_run, process_name_in_ps, *args)
    # This makes main.py PID 1.
    os.execlp(sys.executable, sys.executable, 'main.py')


if __name__ == '__main__':
    run_migrations()
    start_app()
