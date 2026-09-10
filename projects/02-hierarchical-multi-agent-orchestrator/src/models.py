"""
Domain models and message communication schemas for Project 02:
Hierarchical Multi-Agent Enterprise Migration Orchestrator.
Designed for Forward Deployed Engineering (FDE) production standards.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class WorkerRole(str, Enum):
    TOPOLOGY_ENGINEER = "TOPOLOGY_ENGINEER"
    SECURITY_AUDITOR = "SECURITY_AUDITOR"
    FINOPS_ANALYST = "FINOPS_ANALYST"


@dataclass
class SubTask:
    """A decomposed mission assigned to a specialized sub-agent."""
    task_id: str
    target_worker: WorkerRole
    title: str
    instruction: str
    parameters: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "target_worker": self.target_worker.value,
            "title": self.title,
            "instruction": self.instruction,
            "parameters": self.parameters,
            "priority": self.priority.value,
            "created_at": self.created_at,
        }


@dataclass
class WorkerFinding:
    """A verified factual finding extracted by a worker sub-agent."""
    finding_id: str
    category: str
    summary: str
    impact_level: str  # LOW, MEDIUM, HIGH, BLOCKER
    recommendation: str
    evidence_telemetry: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "category": self.category,
            "summary": self.summary,
            "impact_level": self.impact_level,
            "recommendation": self.recommendation,
            "evidence_telemetry": self.evidence_telemetry,
        }


@dataclass
class WorkerReport:
    """The structured deliverable returned by a sub-agent worker to the supervisor."""
    worker_role: WorkerRole
    task_id: str
    status: str  # SUCCESS, PARTIAL_FAILURE, TIMEOUT
    findings: List[WorkerFinding] = field(default_factory=list)
    resource_estimates: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    error_details: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "worker_role": self.worker_role.value,
            "task_id": self.task_id,
            "status": self.status,
            "findings": [f.to_dict() for f in self.findings],
            "resource_estimates": self.resource_estimates,
            "execution_time_ms": round(self.execution_time_ms, 2),
            "error_details": self.error_details,
        }


@dataclass
class ReconciledRiskDecision:
    """Outcome of the Consensus Engine when sub-agent findings conflict."""
    conflict_topic: str
    contending_parties: List[str]
    winning_ruling: str
    rationale: str
    veto_applied: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_topic": self.conflict_topic,
            "contending_parties": self.contending_parties,
            "winning_ruling": self.winning_ruling,
            "rationale": self.rationale,
            "veto_applied": self.veto_applied,
        }


@dataclass
class MigrationDossier:
    """The final executive and technical migration deliverable compiled by the supervisor."""
    dossier_id: str
    target_workload: str
    client_enterprise: str
    overall_readiness_score: float  # 0.0 to 100.0
    migration_wave: str  # Wave 1 (Immediate), Wave 2 (Needs Refactoring), Blocked
    worker_reports: List[WorkerReport] = field(default_factory=list)
    reconciled_decisions: List[ReconciledRiskDecision] = field(default_factory=list)
    executive_summary: str = ""
    estimated_tco_monthly_usd: float = 0.0
    action_items: List[str] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dossier_id": self.dossier_id,
            "target_workload": self.target_workload,
            "client_enterprise": self.client_enterprise,
            "overall_readiness_score": self.overall_readiness_score,
            "migration_wave": self.migration_wave,
            "worker_reports": [r.to_dict() for r in self.worker_reports],
            "reconciled_decisions": [d.to_dict() for d in self.reconciled_decisions],
            "executive_summary": self.executive_summary,
            "estimated_tco_monthly_usd": self.estimated_tco_monthly_usd,
            "action_items": self.action_items,
            "generated_at": self.generated_at,
        }

    def to_markdown(self) -> str:
        md = [
            f"# Enterprise Workload Migration Dossier: {self.target_workload}",
            f"\n**Enterprise Client**: {self.client_enterprise} | **Generated**: {self.generated_at}",
            f"**Readiness Score**: `{self.overall_readiness_score}/100` | **Target Phase**: `{self.migration_wave}`",
            f"\n## 1. Executive Briefing\n{self.executive_summary}\n",
            f"**Estimated Monthly Cloud TCO**: `${self.estimated_tco_monthly_usd:,.2f} USD`\n",
            "## 2. Multi-Agent Worker Specialization Reports\n",
        ]
        for report in self.worker_reports:
            md.append(f"### Sub-Agent: `{report.worker_role.value}` (Execution: {report.execution_time_ms:.1f}ms)")
            md.append(f"- **Status**: `{report.status}`")
            for f in report.findings:
                md.append(f"- **[{f.impact_level}] {f.category}**: {f.summary}")
                md.append(f"  - *Action*: {f.recommendation}")
            md.append("")

        if self.reconciled_decisions:
            md.append("## 3. Consensus Engine Conflict Resolutions\n")
            for d in self.reconciled_decisions:
                veto_badge = " [SECURITY VETO]" if d.veto_applied else ""
                md.append(f"### Conflict: {d.conflict_topic}{veto_badge}")
                md.append(f"- **Contenders**: {', '.join(d.contending_parties)}")
                md.append(f"- **Ruling**: {d.winning_ruling}")
                md.append(f"- **Rationale**: {d.rationale}\n")

        if self.action_items:
            md.append("## 4. FDE Deployment Action Items\n")
            for act in self.action_items:
                md.append(f"- [ ] {act}")
            md.append("")

        return "\n".join(md)
