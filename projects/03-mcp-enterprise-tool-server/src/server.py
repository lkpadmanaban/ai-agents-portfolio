"""
Enterprise Model Context Protocol (MCP) Server.
Implements the official MCP methods:
- tools/list: Discover available enterprise tools
- tools/call: Safely execute an enterprise tool with input validation
- resources/list: Discover available read-only resources
- resources/read: Fetch context from an enterprise URI
"""

from __future__ import annotations
import json
import time
from typing import Any, Callable, Dict, List, Optional
from protocol import (
    JSONRPCRequest,
    JSONRPCResponse,
    MCPErrorCode,
    MCPToolDefinition,
    MCPToolParameterSchema,
    MCPResourceDefinition,
)


class EnterpriseMCPServer:
    """
    Standardized MCP Server hosting enterprise operational tools and live resources.
    """

    def __init__(self, server_name: str = "Enterprise-Core-MCP-Server", version: str = "1.0.0"):
        self.server_name = server_name
        self.version = version
        self._tools: Dict[str, MCPToolDefinition] = {}
        self._tool_handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self._resources: Dict[str, MCPResourceDefinition] = {}
        self._resource_store: Dict[str, str] = {}
        self._register_default_enterprise_catalog()

    def _register_default_enterprise_catalog(self) -> None:
        """Populates server with representative enterprise Kubernetes and incident tools."""
        # 1. Kubernetes Pod Health Tool
        self.register_tool(
            MCPToolDefinition(
                name="query_k8s_workloads",
                description="Query enterprise Kubernetes cluster for deployment status, restart counts, and OOMKilled events.",
                inputSchema=MCPToolParameterSchema(
                    properties={
                        "namespace": {"type": "string", "description": "Target K8s namespace (e.g., 'production', 'payments')"},
                        "min_restarts": {"type": "integer", "description": "Filter pods with restarts >= this threshold"},
                    },
                    required=["namespace"],
                ),
            ),
            handler=self._handle_k8s_query,
        )

        # 2. Service Incident Telemetry Tool
        self.register_tool(
            MCPToolDefinition(
                name="fetch_active_incidents",
                description="Fetch critical enterprise incident tickets from ServiceNow / PagerDuty integration.",
                inputSchema=MCPToolParameterSchema(
                    properties={
                        "severity": {"type": "string", "enum": ["P1", "P2", "P3"], "description": "Incident priority severity level"},
                        "service_name": {"type": "string", "description": "Microservice identifier (e.g. 'auth-gateway')"},
                    },
                    required=["severity"],
                ),
            ),
            handler=self._handle_incident_fetch,
        )

        # 3. Register standard Enterprise Audit Resource
        self.register_resource(
            MCPResourceDefinition(
                uri="enterprise://audit/compliance/soc2-status.json",
                name="SOC2 Compliance Audit Manifest",
                description="Live cryptographic snapshot of SOC2 Type II compliance controls across VPC regions.",
                mimeType="application/json",
            ),
            content=json.dumps({
                "audit_year": 2026,
                "status": "COMPLIANT",
                "controls_verified": 48,
                "last_evaluated": "2026-09-10T08:00:00Z",
                "auditor": "Global Enterprise Security Board",
            }),
        )

    def register_tool(self, tool_def: MCPToolDefinition, handler: Callable[[Dict[str, Any]], Any]) -> None:
        self._tools[tool_def.name] = tool_def
        self._tool_handlers[tool_def.name] = handler

    def register_resource(self, res_def: MCPResourceDefinition, content: str) -> None:
        self._resources[res_def.uri] = res_def
        self._resource_store[res_def.uri] = content

    def handle_request(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches an incoming JSON-RPC 2.0 message conforming to MCP spec."""
        req = JSONRPCRequest.from_dict(request_payload)

        # Method: initialize
        if req.method == "initialize":
            res = {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": self.server_name, "version": self.version},
                "capabilities": {"tools": {}, "resources": {}},
            }
            return JSONRPCResponse(id=req.id, result=res).to_dict()

        # Method: tools/list
        elif req.method == "tools/list":
            tools_list = [t.to_dict() for t in self._tools.values()]
            return JSONRPCResponse(id=req.id, result={"tools": tools_list}).to_dict()

        # Method: tools/call
        elif req.method == "tools/call":
            params = req.params
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            if not tool_name or tool_name not in self._tools:
                err = {"code": MCPErrorCode.METHOD_NOT_FOUND.value, "message": f"Tool '{tool_name}' not found on MCP server."}
                return JSONRPCResponse(id=req.id, error=err).to_dict()

            # Schema Validation: check required arguments
            tool_def = self._tools[tool_name]
            for req_field in tool_def.inputSchema.required:
                if req_field not in tool_args:
                    err = {
                        "code": MCPErrorCode.INVALID_PARAMS.value,
                        "message": f"Missing required parameter '{req_field}' for tool '{tool_name}'",
                    }
                    return JSONRPCResponse(id=req.id, error=err).to_dict()

            handler = self._tool_handlers[tool_name]
            try:
                output = handler(tool_args)
                result = {
                    "content": [{"type": "text", "text": json.dumps(output)}],
                    "isError": False,
                }
                return JSONRPCResponse(id=req.id, result=result).to_dict()
            except Exception as e:
                result = {
                    "content": [{"type": "text", "text": str(e)}],
                    "isError": True,
                }
                return JSONRPCResponse(id=req.id, result=result).to_dict()

        # Method: resources/list
        elif req.method == "resources/list":
            res_list = [r.to_dict() for r in self._resources.values()]
            return JSONRPCResponse(id=req.id, result={"resources": res_list}).to_dict()

        # Method: resources/read
        elif req.method == "resources/read":
            uri = req.params.get("uri")
            if not uri or uri not in self._resource_store:
                err = {"code": MCPErrorCode.INVALID_PARAMS.value, "message": f"Resource URI '{uri}' not found."}
                return JSONRPCResponse(id=req.id, error=err).to_dict()

            res_def = self._resources[uri]
            content = self._resource_store[uri]
            result = {
                "contents": [{"uri": uri, "mimeType": res_def.mimeType, "text": content}]
            }
            return JSONRPCResponse(id=req.id, result=result).to_dict()

        # Unrecognized Method
        err = {"code": MCPErrorCode.METHOD_NOT_FOUND.value, "message": f"Unsupported MCP method '{req.method}'"}
        return JSONRPCResponse(id=req.id, error=err).to_dict()

    # --- Tool Execution Handlers (Deterministic Mock / Real Integration) ---
    def _handle_k8s_query(self, args: Dict[str, Any]) -> Dict[str, Any]:
        ns = args.get("namespace", "production")
        min_restarts = args.get("min_restarts", 0)
        return {
            "cluster": "gke-enterprise-us-east1-prod",
            "namespace": ns,
            "queried_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_pods": 42,
            "unhealthy_pods": [
                {
                    "pod_name": f"payment-processor-{ns}-78d9b-x92",
                    "status": "CrashLoopBackOff",
                    "restart_count": 8,
                    "last_termination_reason": "OOMKilled (Exit 137)",
                    "memory_limit_mb": 512,
                }
            ],
        }

    def _handle_incident_fetch(self, args: Dict[str, Any]) -> Dict[str, Any]:
        severity = args.get("severity", "P1")
        service = args.get("service_name", "all")
        return {
            "incident_count": 1,
            "incidents": [
                {
                    "ticket_id": "INC-2026-9042",
                    "severity": severity,
                    "service": service,
                    "headline": "Elevated 502 Bad Gateway errors on Payment Gateway",
                    "assigned_team": "Site Reliability Engineering (SRE)",
                    "state": "INVESTIGATING",
                }
            ],
        }
