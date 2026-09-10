"""
CLI Runner and Interactive Demonstrator for Project 03:
Model Context Protocol (MCP) Enterprise Tool Server & Client.
"""

from __future__ import annotations
import sys
import argparse
import json
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).parent))

# Ensure UTF-8 stdout on Windows terminals
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from server import EnterpriseMCPServer
from client import MCPClientAgent


def run_cli():
    parser = argparse.ArgumentParser(description="Model Context Protocol (MCP) Enterprise Tool Server & Client")
    parser.add_argument("--service", type=str, default="payment-gateway", help="Target microservice for MCP triage")
    parser.add_argument("--output-json", type=str, default="mcp_triage_report.json", help="Path to save report")

    args = parser.parse_args()

    print("=" * 75)
    print("MODEL CONTEXT PROTOCOL (MCP) ENTERPRISE TOOL SERVER & CLIENT")
    print("=" * 75)
    print(f"Target Service   : {args.service}")
    print(f"Protocol Standard: Model Context Protocol (MCP) Spec 2024-11-05 (JSON-RPC 2.0)\n")

    # Instantiate MCP Server
    server = EnterpriseMCPServer()
    client = MCPClientAgent(server)

    print("[STEP 1: MCP HANDSHAKE & INITIALIZATION]")
    init_res = client.initialize_connection()
    print(f"  Server Name    : {init_res.get('serverInfo', {}).get('name')}")
    print(f"  Protocol Ver   : {init_res.get('protocolVersion')}")

    print("\n[STEP 2: MCP DISCOVERY - tools/list & resources/list]")
    tools = client.discover_tools()
    for t in tools:
        print(f"  [TOOL] {t['name']:<25} : {t['description']}")

    resources = client.discover_resources()
    for r in resources:
        print(f"  [RESOURCE] {r['uri']:<40} : {r['name']}")

    print("\n[STEP 3: AUTONOMOUS FDE INCIDENT TRIAGE WORKFLOW]")
    report = client.run_automated_incident_triage(args.service)
    print(f"  Incident Ticket: {report['incident_ticket']}")
    print(f"  Audit Posture  : {report['compliance_audit_posture']}")
    print(f"  Root Cause     : {report['diagnosed_root_cause']}")
    print(f"  Remediation    : {report['recommended_fde_action']}")

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n[FILE] Saved Triage Report -> {args.output_json}")


if __name__ == "__main__":
    run_cli()
