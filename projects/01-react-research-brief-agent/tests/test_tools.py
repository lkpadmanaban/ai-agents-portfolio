"""
Unit tests for the tool registry and individual tool operations.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from tools import ToolRegistry, SearchWebArchiveTool, FetchDocumentTextTool, CalculateMetricTool
from models import ToolCall


class TestTools(unittest.TestCase):

    def setUp(self):
        self.registry = ToolRegistry()

    def test_tool_discovery(self):
        tools = self.registry.list_tools()
        names = [t["name"] for t in tools]
        self.assertIn("search_web_archive", names)
        self.assertIn("fetch_document_text", names)
        self.assertIn("calculate_metric", names)

    def test_search_web_archive(self):
        call = ToolCall(
            tool_name="search_web_archive",
            arguments={"query": "ReAct adoption benchmarks", "max_results": 2},
            call_id="c1",
        )
        result = self.registry.execute(call)
        self.assertTrue(result.success)
        self.assertIsInstance(result.output, list)
        self.assertGreater(len(result.output), 0)
        self.assertIn("title", result.output[0])

    def test_fetch_document(self):
        call = ToolCall(
            tool_name="fetch_document_text",
            arguments={"doc_id": "doc_001"},
            call_id="c2",
        )
        result = self.registry.execute(call)
        self.assertTrue(result.success)
        self.assertEqual(result.output["id"], "doc_001")
        self.assertIn("Gartner AI Research", result.output["source"])

    def test_calculate_metric_growth(self):
        call = ToolCall(
            tool_name="calculate_metric",
            arguments={"operation": "growth_rate", "values": [100.0, 150.0]},
            call_id="c3",
        )
        result = self.registry.execute(call)
        self.assertTrue(result.success)
        self.assertEqual(result.output["growth_percentage"], 50.0)

    def test_calculate_metric_cagr(self):
        call = ToolCall(
            tool_name="calculate_metric",
            arguments={"operation": "cagr", "values": [100.0, 200.0], "periods": 2},
            call_id="c4",
        )
        result = self.registry.execute(call)
        self.assertTrue(result.success)
        self.assertAlmostEqual(result.output["cagr_percentage"], 41.42, places=1)

    def test_unregistered_tool_error(self):
        call = ToolCall(
            tool_name="non_existent_tool",
            arguments={},
            call_id="c5",
        )
        result = self.registry.execute(call)
        self.assertFalse(result.success)
        self.assertIn("is not registered", result.error_message)


if __name__ == "__main__":
    unittest.main()
