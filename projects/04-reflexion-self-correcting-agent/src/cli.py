"""
CLI Runner and Interactive Visualizer for Project 04:
Self-Correcting Reflexion & Actor-Critic Agent.
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

from agent import ReflexionAgent


def run_cli():
    parser = argparse.ArgumentParser(description="Self-Correcting Reflexion & Actor-Critic Agent")
    parser.add_argument(
        "--workload",
        type=str,
        default="Enterprise Payment Settlement Engine",
        help="Target workload deployment objective",
    )
    parser.add_argument("--output-json", type=str, default="reflexion_trace.json", help="Path to save execution trace")

    args = parser.parse_args()

    print("=" * 75)
    print("LOOP ENGINEERING: SELF-CORRECTING REFLEXION & ACTOR-CRITIC AGENT")
    print("=" * 75)
    print(f"Objective Target : {args.workload}\n")

    agent = ReflexionAgent()
    state = agent.run(args.workload)

    print(f"Execution Status : {state.status.value}")
    print(f"Total Attempts   : {state.current_attempt}/{state.max_attempts}")
    print(f"Latency          : {state.total_execution_ms:.2f}ms\n")

    print("[EPISODIC MEMORY: SELF-CORRECTION REFLECTIONS]")
    for r in state.episodic_memory:
        print(f"\n--- [Iteration {r.iteration} Reflection] ---")
        print(f"  ❌ Critic Diagnosis  : {r.error_feedback}")
        print(f"  🧠 Self-Reflection   : {r.self_reflection}")
        print(f"  🛠️  Remediation Patch : {r.remediation_strategy}")

    print("\n[FINAL CONVERGED SPECIFICATION]")
    print(json.dumps(state.final_output, indent=2))

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, indent=2)
    print(f"\n[FILE] Saved Reflexion Trace -> {args.output_json}")


if __name__ == "__main__":
    run_cli()
