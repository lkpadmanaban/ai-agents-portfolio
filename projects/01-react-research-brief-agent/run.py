#!/usr/bin/env python3
"""
Entrypoint runner for Project 01: ReAct Research & Briefing Agent.
"""
import sys
from pathlib import Path

# Add src to python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from cli import run_cli

if __name__ == "__main__":
    run_cli()
