"""
Command-line Interface and Interactive Runner for the ReAct Research Agent.
Provides step-by-step trace visualization, verification badges, and file exports.
"""

from __future__ import annotations
import sys
import os
import argparse
import json
from pathlib import Path

# Ensure UTF-8 stdout on Windows terminals
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add parent directory of src to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from agent import ReActResearchAgent, DeterministicMockLLMProvider, GeminiLLMProvider
from tools import ToolRegistry
from guardrails import CitationGuardrail


def format_step_trace(step) -> str:
    """Format a single ReAct step for terminal visualization."""
    out = [f"\n--- [Iteration {step.iteration}] ---"]
    out.append(f"  [THOUGHT]     : {step.thought}")
    if step.action:
        out.append(f"  [ACTION]      : Call '{step.action.tool_name}' with {json.dumps(step.action.arguments)}")
    if step.observation:
        status_sym = "SUCCESS" if step.observation.success else "FAILED"
        out.append(f"  [OBSERVATION] : ({status_sym} - {step.observation.latency_ms:.1f}ms) {json.dumps(step.observation.output)[:120]}...")
    if step.reflection:
        out.append(f"  [REFLECTION]  : {step.reflection}")
    return "\n".join(out)


def run_cli():
    parser = argparse.ArgumentParser(description="Autonomous ReAct Research & Briefing Agent")
    parser.add_argument(
        "--topic",
        type=str,
        default="State of Agentic AI 2026 & Token Economics",
        help="Research topic or question to investigate",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum ReAct reasoning loops",
    )
    parser.add_argument(
        "--output-md",
        type=str,
        default="executive_brief.md",
        help="Path to save generated markdown briefing",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default="agent_trace.json",
        help="Path to save full agent trace and state",
    )
    parser.add_argument(
        "--live-gemini",
        action="store_true",
        help="Use live Gemini API instead of deterministic mock provider",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Print real-time reasoning steps and tool execution",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("AUTONOMOUS RESEARCH & BRIEFING AGENT (ReAct + Guardrails)")
    print("=" * 70)
    print(f"Research Topic : '{args.topic}'")
    print(f"Engine         : {'Live Gemini API' if args.live_gemini else 'Deterministic Grounded Mock'}")
    print(f"Max Iterations : {args.max_iterations}\n")

    provider = GeminiLLMProvider() if args.live_gemini else DeterministicMockLLMProvider()
    agent = ReActResearchAgent(
        llm_provider=provider,
        tool_registry=ToolRegistry(),
        guardrail=CitationGuardrail(),
        max_iterations=args.max_iterations,
    )

    print("[PHASE 1: PLANNING] Formulating research inquiries...")
    brief, guardrail_result, state = agent.run(args.topic)

    for step_num, plan_item in enumerate(state.plan, 1):
        print(f"  {step_num}. {plan_item}")

    print("\n[PHASE 2: REACT EXECUTION LOOP] Executing grounded investigation...")
    if args.verbose:
        for step in state.thoughts:
            print(format_step_trace(step))

    print("\n[PHASE 3: GUARDRAILS & CITATION VERIFICATION]")
    status_icon = "[PASS]" if guardrail_result.passed else "[FAIL]"
    print(f"  Status             : {status_icon} {guardrail_result.verdict}")
    print(f"  Grounding Score    : {int(guardrail_result.grounding_score * 100)}%")
    print(f"  Verified Citations : {guardrail_result.grounded_claims}/{guardrail_result.total_claims}")

    if guardrail_result.flagged_inconsistencies:
        print("  [!] Flagged Inconsistencies:")
        for flag in guardrail_result.flagged_inconsistencies:
            print(f"    - {flag}")

    print("\n[PHASE 4: EXECUTIVE BRIEFING]")
    print("-" * 70)
    print(brief.to_markdown())
    print("-" * 70)

    # Save artifacts
    with open(args.output_md, "w", encoding="utf-8") as f:
        f.write(brief.to_markdown())
    print(f"\n[FILE] Saved Markdown Briefing -> {args.output_md}")

    trace_data = {
        "topic": args.topic,
        "plan": state.plan,
        "steps": [s.to_dict() for s in state.thoughts],
        "brief": brief.to_dict(),
        "guardrail_result": {
            "passed": guardrail_result.passed,
            "verdict": guardrail_result.verdict,
            "grounding_score": guardrail_result.grounding_score,
            "unverified_citations": guardrail_result.unverified_citations,
            "flagged_inconsistencies": guardrail_result.flagged_inconsistencies,
        },
    }
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(trace_data, f, indent=2)
    print(f"[FILE] Saved Full Trace JSON   -> {args.output_json}")


if __name__ == "__main__":
    run_cli()
