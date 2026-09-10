"""
Command-line Interface and Runner for Project 02.
Provides interactive inspection of inter-agent messages, consensus arbitration,
and dossier markdown export.
"""

from __future__ import annotations
import sys
import os
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

from orchestrator import SupervisorOrchestrator


def run_cli():
    parser = argparse.ArgumentParser(description="Hierarchical Multi-Agent Enterprise Migration Orchestrator")
    parser.add_argument(
        "--workload",
        type=str,
        default="Global Core Banking Transaction Engine",
        help="Target enterprise workload / system to analyze",
    )
    parser.add_argument(
        "--client",
        type=str,
        default="Apex Financial Global Group",
        help="Enterprise customer organization name",
    )
    parser.add_argument(
        "--output-md",
        type=str,
        default="migration_dossier.md",
        help="Path to save generated markdown dossier",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default="multi_agent_trace.json",
        help="Path to save full inter-agent communication trace",
    )

    args = parser.parse_args()

    print("=" * 75)
    print("HIERARCHICAL MULTI-AGENT ENTERPRISE MIGRATION ORCHESTRATOR")
    print("=" * 75)
    print(f"Target Workload    : {args.workload}")
    print(f"Enterprise Client  : {args.client}\n")

    orchestrator = SupervisorOrchestrator()

    print("[PHASE 1: DYNAMIC TASK DECOMPOSITION]")
    tasks = orchestrator.decompose(args.workload, args.client)
    for t in tasks:
        print(f"  [DISPATCH] Target Worker: {t.target_worker.value:<20} | Priority: {t.priority.value:<8} | Mission: {t.title}")

    print("\n[PHASE 2: SPECIALIZED SUB-AGENT EXECUTION]")
    reports = orchestrator.execute_plan(tasks)
    for r in reports:
        print(f"  [RECEIVED] Worker: {r.worker_role.value:<20} | Status: {r.status} | Findings: {len(r.findings)} | Latency: {r.execution_time_ms:.1f}ms")

    print("\n[PHASE 3: CONSENSUS ENGINE & ARBITRATION]")
    dossier = orchestrator.compile_dossier(args.workload, args.client, reports)
    print(f"  Readiness Score    : {dossier.overall_readiness_score:.1f}/100")
    print(f"  Target Phase       : {dossier.migration_wave}")
    print(f"  Projected TCO      : ${dossier.estimated_tco_monthly_usd:,.2f} USD/mo")

    if dossier.reconciled_decisions:
        for dec in dossier.reconciled_decisions:
            veto = " [VETO ENFORCED]" if dec.veto_applied else ""
            print(f"  [ARBITRATION]{veto} {dec.conflict_topic}")
            print(f"     Winning Ruling  : {dec.winning_ruling}")

    print("\n[PHASE 4: DOSSIER COMPILATION]")
    print("-" * 75)
    print(dossier.to_markdown())
    print("-" * 75)

    # Save artifacts
    with open(args.output_md, "w", encoding="utf-8") as f:
        f.write(dossier.to_markdown())
    print(f"\n[FILE] Saved Markdown Dossier -> {args.output_md}")

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(dossier.to_dict(), f, indent=2)
    print(f"[FILE] Saved Inter-Agent Trace -> {args.output_json}")


if __name__ == "__main__":
    run_cli()
