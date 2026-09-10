"""
Enterprise MCP Client & Autonomous Operational Agent.
Demonstrates how AI agents dynamically discover tools, read context resources,
and invoke remote MCP methods over standard JSON-RPC 2.0.
"""

from __future__ import annotations
import json
from typing import Any, Dict, List, Optional
from protocol import JSONRPCRequest
from server import EnterpriseMCPServer


class MCPClientAgent:
    """
    Intelligent Agent Client that communicates with any standard MCP Server.
    Decoupled from specific LLM models; can execute deterministic remediation workflows.
    """

    def __init__(self, mcp_server: EnterpriseMCPServer):
        self.server = mcp_server
        self.session_id = "sess_mcp_client_01"
        self._discovered_tools: List[Dict[str, Any]] = []
        self._discovered_resources: List[Dict[str, Any]] = []

    def initialize_connection(self) -> Dict[str, Any]:
        """Performs MCP protocol handshake."""
        req = JSONRPCRequest(method="initialize", params={"clientInfo": {"name": "FDE-Incident-Agent", "version": "1.0.0"}})
        resp = self.server.handle_request(req.to_dict())
        return resp.get("result", {})

    def discover_tools(self) -> List[Dict[str, Any]]:
        """Queries the server for available tools via tools/list."""
        req = JSONRPCRequest(method="tools/list")
        resp = self.server.handle_request(req.to_dict())
        self._discovered_tools = resp.get("result", {}).get("tools", [])
        return self._discovered_tools

    def discover_resources(self) -> List[Dict[str, Any]]:
        """Queries the server for available resources via resources/list."""
        req = JSONRPCRequest(method="resources/list")
        resp = self.server.handle_request(req.to_dict())
        self._discovered_resources = resp.get("result", {}).get("resources", [])
        return self._discovered_resources

    def read_resource(self, uri: str) -> Dict[str, Any]:
        """Fetches resource text/context via resources/read."""
        req = JSONRPCRequest(method="resources/read", params={"uri": uri})
        resp = self.server.handle_request(req.to_dict())
        return resp

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Calls a remote tool on the MCP server via tools/call."""
        req = JSONRPCRequest(method="tools/call", params={"name": name, "arguments": arguments})
        resp = self.server.handle_request(req.to_dict())
        return resp

    def run_automated_incident_triage(self, target_service: str) -> Dict[str, Any]:
        """
        Forward Deployed Engineering autonomous workflow:
        1. Handshake with MCP Server
        2. Read compliance posture resource
        3. Query active P1/P2 incidents
        4. Query cluster workload health for offending service
        5. Formulate root cause assessment
        """
        self.initialize_connection()
        self.discover_tools()
        self.discover_resources()

        # Step 1: Read SOC2 resource
        audit_res = self.read_resource("enterprise://audit/compliance/soc2-status.json")
        audit_status = "UNKNOWN"
        if "result" in audit_res:
            raw_text = audit_res["result"]["contents"][0]["text"]
            audit_status = json.loads(raw_text).get("status", "UNKNOWN")

        # Step 2: Fetch incidents
        inc_res = self.call_tool("fetch_active_incidents", {"severity": "P1", "service_name": target_service})
        inc_data = {}
        if not inc_res.get("error"):
            raw_content = inc_res["result"]["content"][0]["text"]
            inc_data = json.loads(raw_content)

        # Step 3: Query Kubernetes workload
        k8s_res = self.call_tool("query_k8s_workloads", {"namespace": "production", "min_restarts": 1})
        k8s_data = {}
        if not k8s_res.get("error"):
            raw_content = k8s_res["result"]["content"][0]["text"]
            k8s_data = json.loads(raw_content)

        # Step 4: Synthesize root cause analysis
        unhealthy_pods = k8s_data.get("unhealthy_pods", [])
        pod_root_cause = "No unhealthy pods found"
        if unhealthy_pods:
            p = unhealthy_pods[0]
            pod_root_cause = f"Pod '{p['pod_name']}' is failing with {p['status']} ({p['last_termination_reason']}). Restart count: {p['restart_count']}."

        return {
            "triage_summary": f"Incident analysis for '{target_service}' concluded.",
            "compliance_audit_posture": audit_status,
            "incident_ticket": inc_data.get("incidents", [{}])[0].get("ticket_id", "N/A"),
            "diagnosed_root_cause": pod_root_cause,
            "recommended_fde_action": "Increase memory limit from 512Mi to 1Gi in Helm values.yaml and trigger rolling deployment.",
            "mcp_calls_made": 3,
        }
