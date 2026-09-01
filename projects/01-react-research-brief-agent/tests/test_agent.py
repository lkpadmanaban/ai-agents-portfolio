"""
End-to-end integration and lifecycle tests for the ReAct research agent.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from agent import ReActResearchAgent, DeterministicMockLLMProvider
from tools import ToolRegistry
from guardrails import CitationGuardrail


class TestReActResearchAgent(unittest.TestCase):

    def setUp(self):
        self.agent = ReActResearchAgent(
            llm_provider=DeterministicMockLLMProvider(),
            tool_registry=ToolRegistry(),
            guardrail=CitationGuardrail(),
            max_iterations=5,
        )

    def test_full_agent_lifecycle(self):
        topic = "Agentic AI Architectures and Token Economics 2026"
        brief, guardrail_result, state = self.agent.run(topic)

        # Verify Plan Phase
        self.assertEqual(len(state.plan), 3)
        self.assertIn("benchmarks", state.plan[0].lower())

        # Verify ReAct Loop Execution
        self.assertGreaterEqual(state.iteration_count, 3)
        self.assertTrue(state.is_complete)
        self.assertGreater(len(state.thoughts), 0)

        # Verify Tool Observations Ingested
        self.assertGreater(len(state.collected_observations), 0)
        self.assertTrue(any("search_web_archive" in k for k in state.collected_observations.keys()))

        # Verify Brief Structure
        self.assertEqual(brief.topic, topic)
        self.assertGreater(len(brief.key_findings), 0)
        self.assertTrue(len(brief.raw_sources) > 0)

        # Verify Guardrail Verification Passed
        self.assertTrue(guardrail_result.passed)
        self.assertEqual(guardrail_result.verdict, "PASSED_VERIFIED")
        self.assertGreaterEqual(guardrail_result.grounding_score, 0.70)
        self.assertEqual(len(guardrail_result.unverified_citations), 0)

    def test_markdown_export(self):
        topic = "Test Topic"
        brief, _, _ = self.agent.run(topic)
        md = brief.to_markdown()
        self.assertIn("# Executive Research Brief", md)
        self.assertIn("## Executive Summary", md)
        self.assertIn("## Key Findings", md)
        self.assertIn("[VERIFIED]", md)


if __name__ == "__main__":
    unittest.main()
