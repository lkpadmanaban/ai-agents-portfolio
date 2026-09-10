#!/usr/bin/env python3
"""
Entrypoint runner for Project 03: Model Context Protocol (MCP) Enterprise Tool Server & Client.
"""
import sys
from pathlib import Path

# Add src to python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from cli import run_cli

if __name__ == "__main__":
    run_cli()
