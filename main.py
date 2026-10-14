#!/usr/bin/env python3
"""
BrainStorm CLI
~~~~~~~~~~~~~~
An adaptive, offline terminal quiz game for Python developers.
Built 100% with the Python Standard Library (zero external dependencies).

Usage:
    python main.py
"""

import sys
from brainstorm.cli import BrainStormCLI


def configure_terminal() -> None:
    """Ensure standard output and error streams handle UTF-8 characters cleanly."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def main() -> None:
    """Entrypoint to launch the interactive BrainStorm CLI session."""
    configure_terminal()
    app = BrainStormCLI()
    app.run()


if __name__ == "__main__":
    main()
