"""
Consensus Engine & Conflict Resolution Subsystem.
Forward Deployed Engineers face cross-cutting disagreements (e.g. Security vs. Cost).
This module resolves inter-agent contention deterministically with transparent rationale.
"""

from __future__ import annotations
from typing import List, Tuple
from models import WorkerReport, ReconciledRiskDecision, WorkerRole


class ConsensusEngine:
    """
    Arbitrates conflicts between specialized workers.
    Enforces enterprise priority hierarchies:
    1. Security & Compliance (Non-negotiable veto power)
    2. Architecture Topology & SLA Viability
    3. FinOps & Cost Optimization
    """

    def reconcile(self, reports: List[WorkerReport]) -> Tuple[List[ReconciledRiskDecision], float, List[str]]:
        decisions: List[ReconciledRiskDecision] = []
        action_items: List[str] = []
        
        # Look for the classic enterprise conflict: FinOps wants shared multi-tenant, Security requires strict isolation
        has_security_blocker = False
        has_finops_shared_tenant_proposal = False
        security_rationale = ""

        for report in reports:
            if report.worker_role == WorkerRole.SECURITY_AUDITOR:
                for f in report.findings:
                    if f.impact_level == "BLOCKER":
                        has_security_blocker = True
                        security_rationale = f.recommendation
                        action_items.append(f"CRITICAL: {f.recommendation}")
                    elif f.impact_level == "HIGH":
                        action_items.append(f"HIGH: {f.recommendation}")

            elif report.worker_role == WorkerRole.FINOPS_ANALYST:
                for f in report.findings:
                    if "shared" in f.summary.lower() or "shared" in f.recommendation.lower():
                        has_finops_shared_tenant_proposal = True

            elif report.worker_role == WorkerRole.TOPOLOGY_ENGINEER:
                for f in report.findings:
                    if f.impact_level in ("HIGH", "BLOCKER"):
                        action_items.append(f"ARCHITECTURE: {f.recommendation}")

        # Arbitration logic: Security VETO overrides FinOps multi-tenant cost saving
        if has_security_blocker and has_finops_shared_tenant_proposal:
            decisions.append(
                ReconciledRiskDecision(
                    conflict_topic="Multi-Tenant Storage vs. Dedicated CMEK Encryption",
                    contending_parties=["FINOPS_ANALYST (Cost Minimization)", "SECURITY_AUDITOR (PII Compliance)"],
                    winning_ruling="SECURITY_AUDITOR: Dedicated CMEK Cloud Storage Enforced",
                    rationale=(
                        "Security Auditor exercised strict regulatory veto. Saving $400/month by using shared multi-tenant "
                        "storage violates client data sovereignty and PCI-DSS compliance requirements for PII."
                    ),
                    veto_applied=True,
                )
            )

        # Compute composite enterprise readiness score
        # Base: 100. Deduct 35 for each BLOCKER, 15 for each HIGH, 5 for each MEDIUM
        score = 100.0
        for report in reports:
            for f in report.findings:
                if f.impact_level == "BLOCKER":
                    score -= 35.0
                elif f.impact_level == "HIGH":
                    score -= 15.0
                elif f.impact_level == "MEDIUM":
                    score -= 5.0

        score = max(0.0, min(100.0, score))
        return decisions, score, action_items
