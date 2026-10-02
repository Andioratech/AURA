"""Command-line entry point for the AURA research scaffold."""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(prog="aura", description="AURA scientific project tools")
    parser.add_argument(
        "command",
        choices=("status",),
        help="status reports the current scaffold state",
    )
    args = parser.parse_args()
    if args.command == "status":
        print("AURA scaffold initialized; scientific solvers are not implemented yet.")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
