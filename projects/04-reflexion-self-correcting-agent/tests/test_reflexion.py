"""
Unit test suite for Project 04: Loop Engineering — Self-Correcting Reflexion & Actor-Critic Agent.
Verifies failure detection, critic diagnostics, reflection formulation, episodic memory updates,
and successful self-healing convergence.
"""

import sys
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from engine import CriticEvaluator, ActorGenerator
from agent import ReflexionAgent
from models import ExecutionStatus


class TestReflexionSelfCorrection(unittest.TestCase):

    def setUp(self):
        self.critic = CriticEvaluator()
        self.actor = ActorGenerator()
        self.agent = ReflexionAgent(self.actor, self.critic, max_attempts=3)

    def test_critic_rejects_invalid_uuid(self):
        payload = {
            "tenant_id": "invalid-slug-123",
            "service_tier": "ENTERPRISE_DEDICATED",
            "allocated_ram_mb": 2048,
            "cmek_key_version": "projects/kms/keys/v1",
        }
        feedback = self.critic.evaluate(payload)
        self.assertFalse(feedback.passed)
        self.assertEqual(feedback.error_type, "INVALID_UUID_FORMAT")

    def test_critic_rejects_low_ram(self):
        payload = {
            "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
            "service_tier": "ENTERPRISE_DEDICATED",
            "allocated_ram_mb": 512,  # Too low
            "cmek_key_version": "projects/kms/keys/v1",
        }
        feedback = self.critic.evaluate(payload)
        self.assertFalse(feedback.passed)
        self.assertEqual(feedback.error_type, "INSUFFICIENT_MEMORY_ALLOCATION")

    def test_critic_approves_valid_payload(self):
        payload = {
            "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
            "service_tier": "ENTERPRISE_DEDICATED",
            "allocated_ram_mb": 4096,
            "cmek_key_version": "projects/kms/keys/v2-prod",
        }
        feedback = self.critic.evaluate(payload)
        self.assertTrue(feedback.passed)
        self.assertEqual(feedback.score, 1.0)

    def test_self_healing_reflexion_loop(self):
        state = self.agent.run("EnterpriseSettlementCore")
        
        # Must have attempted and self-corrected
        self.assertEqual(state.status, ExecutionStatus.SELF_CORRECTED)
        self.assertEqual(state.current_attempt, 3)
        self.assertEqual(len(state.episodic_memory), 2)
        
        # Verify episodic memory entries
        first_reflection = state.episodic_memory[0]
        self.assertEqual(first_reflection.iteration, 1)
        self.assertIn("RFC 4122 UUID", first_reflection.self_reflection)

        second_reflection = state.episodic_memory[1]
        self.assertEqual(second_reflection.iteration, 2)
        self.assertIn("1024 MB", second_reflection.self_reflection)

        # Verify final output is compliant
        self.assertIsNotNone(state.final_output)
        self.assertEqual(state.final_output["allocated_ram_mb"], 4096)


if __name__ == "__main__":
    unittest.main()
