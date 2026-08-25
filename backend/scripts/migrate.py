"""Database migration runner — convenience script for common Alembic operations.

Usage:
    python -m scripts.migrate              # Run all pending migrations
    python -m scripts.migrate --downgrade  # Downgrade one revision
    python -m scripts.migrate --reset      # Drop all tables and re-apply
"""
import subprocess
import sys
import os


def run_alembic(*args: str) -> int:
    """Run an alembic command from the backend directory."""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cmd = [sys.executable, "-m", "alembic"] + list(args)
    result = subprocess.run(cmd, cwd=backend_dir)
    return result.returncode


def main():
    if "--downgrade" in sys.argv:
        print("⬇️  Downgrading one revision...")
        run_alembic("downgrade", "-1")
    elif "--reset" in sys.argv:
        print("🗑️  Resetting database (downgrade to base)...")
        run_alembic("downgrade", "base")
        print("⬆️  Re-applying all migrations...")
        run_alembic("upgrade", "head")
    else:
        print("⬆️  Running pending migrations...")
        run_alembic("upgrade", "head")

    print("✅ Done!")


if __name__ == "__main__":
    main()
