"""
JSON-RPC 2.0 and Model Context Protocol (MCP) Specification Types.
Strict adherence to Anthropic & Linux Foundation MCP Specifications.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import json


class MCPErrorCode(int, Enum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    UNAUTHORIZED = -32001


@dataclass
class MCPToolParameterSchema:
    """JSON Schema defining arguments for an MCP tool."""
    type: str = "object"
    properties: Dict[str, Any] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "properties": self.properties,
            "required": self.required,
        }


@dataclass
class MCPToolDefinition:
    """Defines a discoverable tool exposed by an MCP server."""
    name: str
    description: str
    inputSchema: MCPToolParameterSchema

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.inputSchema.to_dict(),
        }


@dataclass
class MCPResourceDefinition:
    """Defines an addressable contextual resource exposed by an MCP server."""
    uri: str
    name: str
    description: str
    mimeType: str = "application/json"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mimeType,
        }


@dataclass
class JSONRPCRequest:
    """A standard JSON-RPC 2.0 request envelope."""
    method: str
    params: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = "1"
    jsonrpc: str = "2.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "jsonrpc": self.jsonrpc,
            "id": self.id,
            "method": self.method,
            "params": self.params,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> JSONRPCRequest:
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id"),
            method=data.get("method", ""),
            params=data.get("params", {}),
        )


@dataclass
class JSONRPCResponse:
    """A standard JSON-RPC 2.0 response or error envelope."""
    id: Optional[str]
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    jsonrpc: str = "2.0"

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"jsonrpc": self.jsonrpc, "id": self.id}
        if self.error is not None:
            payload["error"] = self.error
        else:
            payload["result"] = self.result
        return payload
