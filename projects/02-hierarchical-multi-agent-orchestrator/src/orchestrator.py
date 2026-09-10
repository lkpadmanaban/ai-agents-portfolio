"""
Lead Migration Supervisor Orchestrator.
Coordinates dynamic task decomposition, worker parallel dispatch,
consensus resolution, and executive dossier compilation.
"""

from __future__ import annotations
import uuid
from typing import Dict, List, Optional
from models import MigrationDossier, SubTask, TaskPriority, WorkerRole, WorkerReport
from workers import BaseWorker, TopologyWorker, SecurityAuditorWorker, FinOpsAnalystWorker
from consensus import ConsensusEngine


class SupervisorOrchestrator:
    """
    Lead Orchestrator Agent.
    Manages end-to-end multi-agent execution lifecycle.
    """

    def __init__(self, consensus_engine: Optional[ConsensusEngine] = None) -> None:
        self.consensus = consensus_engine or ConsensusEngine()
        self._workers: Dict[WorkerRole, BaseWorker] = {
            WorkerRole.TOPOLOGY_ENGINEER: TopologyWorker(),
            WorkerRole.SECURITY_AUDITOR: SecurityAuditorWorker(),
            WorkerRole.FINOPS_ANALYST: FinOpsAnalystWorker(),
        }

    def decompose(self, workload_name: str, client_name: str) -> List[SubTask]:
        """Deconstructs client migration inquiry into specialized worker sub-tasks."""
        return [
            SubTask(
                task_id=f"task_{uuid.uuid4().hex[:6]}",
                target_worker=WorkerRole.TOPOLOGY_ENGINEER,
                title="Service Topology & Network Discovery",
                instruction="Inspect service dependency graph, database latencies, and container readiness.",
                parameters={"workload_name": workload_name, "client_name": client_name},
                priority=TaskPriority.HIGH,
            ),
            SubTask(
                task_id=f"task_{uuid.uuid4().hex[:6]}",
                target_worker=WorkerRole.SECURITY_AUDITOR,
                title="Security & Compliance Vulnerability Audit",
                instruction="Audit CVE exposures, encryption keys, PII sovereignty, and regulatory barriers.",
                parameters={"workload_name": workload_name, "client_name": client_name},
                priority=TaskPriority.CRITICAL,
            ),
            SubTask(
                task_id=f"task_{uuid.uuid4().hex[:6]}",
                target_worker=WorkerRole.FINOPS_ANALYST,
                title="Cloud Sizing & TCO Forecasting",
                instruction="Model monthly compute, storage, egress bandwidth, and committed savings plans.",
                parameters={"workload_name": workload_name, "client_name": client_name},
                priority=TaskPriority.MEDIUM,
            ),
        ]

    def execute_plan(self, tasks: List[SubTask]) -> List[WorkerReport]:
        """Dispatches sub-tasks to specialized workers and gathers structured telemetry reports."""
        reports: List[WorkerReport] = []
        for task in tasks:
            worker = self._workers.get(task.target_worker)
            if not worker:
                reports.append(
                    WorkerReport(
                        worker_role=task.target_worker,
                        task_id=task.task_id,
                        status="UNREGISTERED_WORKER_ERROR",
                        error_details=f"No worker registered for role: {task.target_worker}",
                    )
                )
                continue
            report = worker.execute(task)
            reports.append(report)
        return reports

    def compile_dossier(
        self, workload_name: str, client_name: str, reports: List[WorkerReport]
    ) -> MigrationDossier:
        """Runs the consensus engine and compiles the complete Migration Dossier."""
        decisions, readiness_score, action_items = self.consensus.reconcile(reports)

        # Categorize migration wave based on readiness
        if readiness_score >= 80.0:
            wave = "Wave 1: Immediate Lift & Shift / Low Friction"
        elif readiness_score >= 50.0:
            wave = "Wave 2: Requires Remediation & Service Mesh Refactoring"
        else:
            wave = "BLOCKED: Critical Security & Regulatory Pre-requisites Unmet"

        # Calculate monthly TCO from FinOps report
        monthly_tco = 0.0
        for r in reports:
            if r.worker_role == WorkerRole.FINOPS_ANALYST:
                monthly_tco = r.resource_estimates.get("projected_monthly_tco_usd", 0.0)

        summary = (
            f"Autonomous multi-agent discovery of '{workload_name}' for enterprise client '{client_name}' "
            f"concluded with a composite readiness score of {readiness_score:.1f}/100. "
            f"Security audits identified critical CMEK key management prerequisites that veto shared storage "
            f"proposals. Recommended target: {wave}."
        )

        return MigrationDossier(
            dossier_id=f"dos_{uuid.uuid4().hex[:8]}",
            target_workload=workload_name,
            client_enterprise=client_name,
            overall_readiness_score=readiness_score,
            migration_wave=wave,
            worker_reports=reports,
            reconciled_decisions=decisions,
            executive_summary=summary,
            estimated_tco_monthly_usd=monthly_tco,
            action_items=action_items,
        )

    def run(self, workload_name: str, client_name: str) -> MigrationDossier:
        """Full end-to-end multi-agent orchestration execution."""
        tasks = self.decompose(workload_name, client_name)
        reports = self.execute_plan(tasks)
        return self.compile_dossier(workload_name, client_name, reports)
