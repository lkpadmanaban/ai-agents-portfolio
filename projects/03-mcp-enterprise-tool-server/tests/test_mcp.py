"""
Unit test suite for Project 03: Model Context Protocol (MCP) Enterprise Tool Server & Client.
Tests JSON-RPC 2.0 conformance, tool discovery, parameter validation, and resource access.
"""

import sys
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from server import EnterpriseMCPServer
from client import MCPClientAgent
from protocol import JSONRPCRequest, MCPErrorCode


class TestMCPServerAndClient(unittest.TestCase):

    def setUp(self):
        self.server = EnterpriseMCPServer()
        self.client = MCPClientAgent(self.server)

    def test_mcp_initialize(self):
        result = self.client.initialize_connection()
        self.assertEqual(result["protocolVersion"], "2024-11-05")
        self.assertIn("capabilities", result)
        self.assertEqual(result["serverInfo"]["name"], "Enterprise-Core-MCP-Server")

    def test_mcp_tools_list(self):
        tools = self.client.discover_tools()
        tool_names = [t["name"] for t in tools]
        self.assertIn("query_k8s_workloads", tool_names)
        self.assertIn("fetch_active_incidents", tool_names)

    def test_mcp_resources_list_and_read(self):
        resources = self.client.discover_resources()
        self.assertGreater(len(resources), 0)
        uri = resources[0]["uri"]
        
        read_resp = self.client.read_resource(uri)
        self.assertIn("result", read_resp)
        self.assertIn("contents", read_resp["result"])
        self.assertEqual(read_resp["result"]["contents"][0]["uri"], uri)

    def test_mcp_tool_call_success(self):
        res = self.client.call_tool("query_k8s_workloads", {"namespace": "production", "min_restarts": 2})
        self.assertNotIn("error", res)
        self.assertIn("result", res)
        self.assertFalse(res["result"]["isError"])
        self.assertIn("CrashLoopBackOff", res["result"]["content"][0]["text"])

    def test_mcp_tool_call_invalid_params(self):
        # Missing required 'namespace' parameter
        res = self.client.call_tool("query_k8s_workloads", {})
        self.assertIn("error", res)
        self.assertEqual(res["error"]["code"], MCPErrorCode.INVALID_PARAMS.value)
        self.assertIn("Missing required parameter 'namespace'", res["error"]["message"])

    def test_mcp_tool_not_found(self):
        res = self.client.call_tool("non_existent_tool", {})
        self.assertIn("error", res)
        self.assertEqual(res["error"]["code"], MCPErrorCode.METHOD_NOT_FOUND.value)

    def test_autonomous_incident_triage(self):
        report = self.client.run_automated_incident_triage("payment-gateway")
        self.assertEqual(report["compliance_audit_posture"], "COMPLIANT")
        self.assertEqual(report["incident_ticket"], "INC-2026-9042")
        self.assertIn("OOMKilled", report["diagnosed_root_cause"])
        self.assertEqual(report["mcp_calls_made"], 3)


if __name__ == "__main__":
    unittest.main()
