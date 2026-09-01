"""
Domain models and schema definitions for the ReAct Research & Briefing Agent.
Defines strongly-typed state, tool communication envelopes, and structured briefing outputs.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import json


@dataclass
class ToolCall:
    """Represents a tool execution request by the agent."""
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "call_id": self.call_id,
        }


@dataclass
class ToolResult:
    """Encapsulates the output or failure state of a tool execution."""
    tool_name: str
    call_id: str
    output: Any
    success: bool = True
    error_message: Optional[str] = None
    latency_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "call_id": self.call_id,
            "output": self.output,
            "success": self.success,
            "error_message": self.error_message,
            "latency_ms": round(self.latency_ms, 2),
        }


@dataclass
class ThoughtStep:
    """A single ReAct reasoning cycle step."""
    iteration: int
    thought: str
    action: Optional[ToolCall] = None
    observation: Optional[ToolResult] = None
    reflection: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "iteration": self.iteration,
            "thought": self.thought,
            "action": self.action.to_dict() if self.action else None,
            "observation": self.observation.to_dict() if self.observation else None,
            "reflection": self.reflection,
            "timestamp": self.timestamp,
        }


@dataclass
class Citation:
    """A verifiable reference backing a specific claim."""
    source_id: str
    source_name: str
    quote_or_snippet: str
    url_or_ref: str
    verified: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "quote_or_snippet": self.quote_or_snippet,
            "url_or_ref": self.url_or_ref,
            "verified": self.verified,
        }


@dataclass
class KeyFinding:
    """A synthesized finding backed by verifiable evidence."""
    headline: str
    details: str
    citations: List[Citation] = field(default_factory=list)
    confidence_score: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "headline": self.headline,
            "details": self.details,
            "citations": [c.to_dict() for c in self.citations],
            "confidence_score": round(self.confidence_score, 2),
        }


@dataclass
class ExecutiveBrief:
    """The final synthesized research brief with full audit trail."""
    topic: str
    summary: str
    key_findings: List[KeyFinding] = field(default_factory=list)
    methodology: str = ""
    limitations: List[str] = field(default_factory=list)
    raw_sources: List[str] = field(default_factory=list)
    validation_status: str = "PENDING_VERIFICATION"
    grounding_score: float = 0.0
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "summary": self.summary,
            "key_findings": [f.to_dict() for f in self.key_findings],
            "methodology": self.methodology,
            "limitations": self.limitations,
            "raw_sources": self.raw_sources,
            "validation_status": self.validation_status,
            "grounding_score": round(self.grounding_score, 2),
            "generated_at": self.generated_at,
        }

    def to_markdown(self) -> str:
        """Render brief as clean GitHub-flavored markdown."""
        md = [
            f"# Executive Research Brief: {self.topic}",
            f"\n**Generated**: {self.generated_at} | **Verification**: `{self.validation_status}` (Grounding: {int(self.grounding_score * 100)}%)",
            f"\n## Executive Summary\n{self.summary}\n",
            "## Key Findings\n",
        ]
        for idx, finding in enumerate(self.key_findings, 1):
            md.append(f"### {idx}. {finding.headline}")
            md.append(f"{finding.details}\n")
            if finding.citations:
                md.append("**Evidence & Citations:**")
                for cit in finding.citations:
                    v_badge = "[VERIFIED]" if cit.verified else "[UNVERIFIED]"
                    md.append(f"- {v_badge} **{cit.source_name}**: \"_{cit.quote_or_snippet}_\" ([Ref]({cit.url_or_ref}))")
                md.append("")

        if self.limitations:
            md.append("## Limitations & Caveats")
            for lim in self.limitations:
                md.append(f"- {lim}")
            md.append("")

        if self.methodology:
            md.append(f"## Methodology\n{self.methodology}\n")

        if self.raw_sources:
            md.append("## Consulted Sources")
            for src in self.raw_sources:
                md.append(f"- {src}")
            md.append("")

        return "\n".join(md)


@dataclass
class AgentState:
    """The working memory state passed through the ReAct loop."""
    topic: str
    plan: List[str] = field(default_factory=list)
    thoughts: List[ThoughtStep] = field(default_factory=list)
    collected_observations: Dict[str, str] = field(default_factory=dict)
    brief: Optional[ExecutiveBrief] = None
    iteration_count: int = 0
    max_iterations: int = 5
    is_complete: bool = False

    def add_observation(self, key: str, text: str) -> None:
        self.collected_observations[key] = text
