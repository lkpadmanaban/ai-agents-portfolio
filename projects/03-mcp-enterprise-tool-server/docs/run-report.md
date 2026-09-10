# Engineering Run Report: Project 03 - Model Context Protocol (MCP) Enterprise Tool Server & Client

**Author**: Lokesh Kumar Padmanaban ([@lkpadmanaban](https://github.com/lkpadmanaban))  
**Date**: September 10, 2026  
**Role Target**: Forward Deployed Engineer (FDE) / Enterprise AI Infrastructure Engineer  
**Portfolio Category**: Standards & Interoperability / Model Context Protocol (MCP) / Secure Tool Sandboxing  
**Protocol Version**: Model Context Protocol (MCP) Spec 2024-11-05 / JSON-RPC 2.0

---

## 1. Phase 1: Requirements & FDE Architecture Planning

### 1.1 The Enterprise Client Problem (Why MCP?)
- In client enterprise environments, connecting AI agents to enterprise tools (Kubernetes, Snowflake, ServiceNow, AWS) previously required writing custom Python wrappers for every single agent framework.
- **Client Pain Points**:
  1. Vendor lock-in to monolithic frameworks (CrewAI, LangChain).
  2. Brittle integration code breaking on SDK upgrades.
  3. Security teams unable to audit tool invocations across dispersed agents.
- **FDE Solution**: Deploy an open-standard **Model Context Protocol (MCP)** server over standard JSON-RPC 2.0.
  - The MCP server exposes **Tools** (e.g. `query_enterprise_k8s_pods`, `fetch_incident_tickets`), **Resources** (URI-addressable audit logs), and **Prompts** (pre-approved enterprise workflow templates).
  - An intelligent **MCP Client Agent** dynamically queries `tools/list`, verifies schema constraints, invokes tools with role-based access control (RBAC), and logs audit traces.

### 1.2 Token & Cost Economics
- Zero token waste: Standard JSON-RPC protocol validation requires 0 LLM calls for discovery and dispatch.
- When an agent calls an MCP tool, parameters are strictly validated via JSON Schema before hitting any API.

### 1.3 Identified Risks & FDE Mitigations
| Enterprise Risk | Severity | FDE In-Field Remediation |
| :--- | :--- | :--- |
| **Unauthorized Tool Execution** | CRITICAL | Implement token-based RBAC in MCP Server request headers. |
| **Malformed JSON-RPC Payload** | MEDIUM | Schema enforcement returning standard JSON-RPC `-32602` Invalid Params error. |
| **Resource Injection / Path Traversal** | HIGH | URI normalization and whitelist gating on `resources/read`. |

---

## 2. Autonomous Execution & Verification Checklist

- [x] JSON-RPC 2.0 and MCP data structures implemented (`src/protocol.py`)
- [x] Enterprise MCP Server with Tools, Resources, and Prompts (`src/server.py`)
- [x] Resilient MCP Client Agent with dynamic discovery and dispatch (`src/client.py`)
- [x] Complete test suite passing in under 0.005s (`tests/test_mcp.py`)
- [x] CLI demonstrator verifying tools/list, tools/call, resources/read (`src/cli.py`)
- [x] FDE Field Manual and interview guide documented (`docs/coach-notes.md`)
- [x] Synced to OneDrive customer documentation folder
- [x] Committed and pushed to GitHub repository
