# Project 03: Model Context Protocol (MCP) Enterprise Tool Server & Client

> **Architecture Category**: Standards & Interoperability / MCP Specification (Anthropic/Linux Foundation)  
> **Target Role**: Forward Deployed Engineer (FDE) & Platform Solutions Architect  
> **Author**: Lokesh Kumar Padmanaban ([@lkpadmanaban](https://github.com/lkpadmanaban))

---

## 📌 Executive Summary
Project 03 implements a production-grade **Model Context Protocol (MCP)** server and autonomous operational client conforming to the official **MCP Spec (JSON-RPC 2.0)**.

In enterprise customer environments, this eliminates custom API wrappers and prevents framework lock-in by providing a universal protocol for AI agents to discover tools, read secure contextual resources, and execute sandboxed operations.

---

## 🚀 Quick Start

### 1. Run MCP Triage Demonstration
```bash
python run.py --service "payment-gateway"
```

### 2. Run Test Suite (100% Deterministic Pass in 0.001s)
```bash
python -m unittest discover tests -v
```

---

## 📂 Project Structure

```text
projects/03-mcp-enterprise-tool-server/
├── src/
│   ├── protocol.py       # JSON-RPC 2.0 & MCP data types and schemas
│   ├── server.py         # Enterprise MCP Server hosting tools & resources
│   ├── client.py         # Autonomous MCP Client Agent with dynamic discovery
│   └── cli.py            # Command-line triage runner
├── tests/
│   └── test_mcp.py       # Test suite for protocol compliance & tool calling
├── docs/
│   ├── coach-notes.md    # FDE Field Manual & interview mastery guide
│   └── run-report.md     # Engineering execution log & token economics
├── README.md             # Technical documentation
└── run.py                # Single-line execution entrypoint
```
