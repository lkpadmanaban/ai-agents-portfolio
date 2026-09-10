"""
Unit and integration test suite for Project 02:
Hierarchical Multi-Agent Enterprise Migration Orchestrator.
100% deterministic test execution for continuous delivery.
"""

import sys
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from models import SubTask, WorkerRole, TaskPriority
from workers import TopologyWorker, SecurityAuditorWorker, FinOpsAnalystWorker
from consensus import ConsensusEngine
from orchestrator import SupervisorOrchestrator


class TestMultiAgentOrchestrator(unittest.TestCase):

    def setUp(self):
        self.orchestrator = SupervisorOrchestrator()
        self.consensus = ConsensusEngine()

    def test_task_decomposition(self):
        tasks = self.orchestrator.decompose("PaymentGatewayMonolith", "Fortune500Bank")
        self.assertEqual(len(tasks), 3)
        roles = {t.target_worker for t in tasks}
        self.assertEqual(roles, {WorkerRole.TOPOLOGY_ENGINEER, WorkerRole.SECURITY_AUDITOR, WorkerRole.FINOPS_ANALYST})

    def test_topology_worker_execution(self):
        worker = TopologyWorker()
        task = SubTask(
            task_id="t1",
            target_worker=WorkerRole.TOPOLOGY_ENGINEER,
            title="Discovery",
            instruction="Analyze",
            parameters={"workload_name": "TestMonolith"},
        )
        report = worker.execute(task)
        self.assertEqual(report.status, "SUCCESS")
        self.assertEqual(report.worker_role, WorkerRole.TOPOLOGY_ENGINEER)
        self.assertGreater(len(report.findings), 0)
        self.assertIn("total_cores_needed", report.resource_estimates)

    def test_security_worker_execution(self):
        worker = SecurityAuditorWorker()
        task = SubTask(
            task_id="t2",
            target_worker=WorkerRole.SECURITY_AUDITOR,
            title="Security Audit",
            instruction="Inspect",
            parameters={},
            priority=TaskPriority.CRITICAL,
        )
        report = worker.execute(task)
        self.assertEqual(report.status, "SUCCESS")
        has_blocker = any(f.impact_level == "BLOCKER" for f in report.findings)
        self.assertTrue(has_blocker)

    def test_finops_worker_execution(self):
        worker = FinOpsAnalystWorker()
        task = SubTask(
            task_id="t3",
            target_worker=WorkerRole.FINOPS_ANALYST,
            title="FinOps TCO",
            instruction="Model",
            parameters={},
        )
        report = worker.execute(task)
        self.assertEqual(report.status, "SUCCESS")
        self.assertIn("projected_monthly_tco_usd", report.resource_estimates)
        self.assertGreater(report.resource_estimates["projected_monthly_tco_usd"], 0)

    def test_consensus_engine_veto(self):
        tasks = self.orchestrator.decompose("TestBankingCore", "TestBank")
        reports = self.orchestrator.execute_plan(tasks)
        decisions, score, action_items = self.consensus.reconcile(reports)
        
        # Verify that security vetoes shared multi-tenant proposal
        self.assertTrue(any(d.veto_applied for d in decisions))
        self.assertGreater(len(action_items), 0)
        self.assertLess(score, 100.0)  # Penalized due to security blocker

    def test_end_to_end_orchestrator(self):
        dossier = self.orchestrator.run("GlobalPaymentCore", "EnterpriseFinTech")
        self.assertEqual(dossier.target_workload, "GlobalPaymentCore")
        self.assertEqual(len(dossier.worker_reports), 3)
        self.assertGreater(dossier.estimated_tco_monthly_usd, 0.0)
        self.assertTrue(len(dossier.action_items) > 0)
        
        md = dossier.to_markdown()
        self.assertIn("# Enterprise Workload Migration Dossier", md)
        self.assertIn("## 1. Executive Briefing", md)
        self.assertIn("Consensus Engine Conflict Resolutions", md)


if __name__ == "__main__":
    unittest.main()
