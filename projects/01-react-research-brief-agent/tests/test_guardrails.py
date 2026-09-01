"""
Unit tests for CitationGuardrail and fact-checking verification pipeline.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from guardrails import CitationGuardrail
from models import ExecutiveBrief, KeyFinding, Citation


class TestGuardrails(unittest.TestCase):

    def setUp(self):
        self.guardrail = CitationGuardrail(min_token_overlap_ratio=0.6)

    def test_verified_grounded_citation(self):
        observations = {
            "step_1": "In 2026, 68% of enterprise AI workloads transitioned to multi-agent ReAct and MCP systems."
        }
        brief = ExecutiveBrief(
            topic="Agent Adoption",
            summary="Rapid transition to ReAct systems.",
            key_findings=[
                KeyFinding(
                    headline="Adoption Wave",
                    details="68% of enterprise workloads transitioned to ReAct systems in 2026.",
                    citations=[
                        Citation(
                            source_id="s1",
                            source_name="Gartner 2026",
                            quote_or_snippet="68% of enterprise AI workloads transitioned to multi-agent ReAct",
                            url_or_ref="https://example.com",
                        )
                    ],
                )
            ],
        )
        res = self.guardrail.verify_brief(brief, observations)
        self.assertTrue(res.passed)
        self.assertEqual(res.verdict, "PASSED_VERIFIED")
        self.assertEqual(res.grounded_claims, 1)
        self.assertTrue(brief.key_findings[0].citations[0].verified)

    def test_unverified_hallucinated_citation(self):
        observations = {
            "step_1": "Quantum computing is developing slowly in laboratory settings."
        }
        brief = ExecutiveBrief(
            topic="Space Travel",
            summary="Warp speed engines are now available for commercial flight.",
            key_findings=[
                KeyFinding(
                    headline="Warp Speed Discovery",
                    details="Interstellar travel takes 2 hours.",
                    citations=[
                        Citation(
                            source_id="s2",
                            source_name="Fake Journal",
                            quote_or_snippet="Interstellar warp drives have reached commercial production.",
                            url_or_ref="https://fake.example.com",
                        )
                    ],
                )
            ],
        )
        res = self.guardrail.verify_brief(brief, observations)
        self.assertFalse(res.passed)
        self.assertEqual(res.verdict, "REJECTED_UNGROUNDED")
        self.assertEqual(len(res.unverified_citations), 1)
        self.assertFalse(brief.key_findings[0].citations[0].verified)


if __name__ == "__main__":
    unittest.main()
