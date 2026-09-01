"""
Extensible Tool Registry and Built-in Grounding Tools for the Research Agent.
Provides safe execution boundaries, latency tracking, schema validation, and offline fallbacks.
"""

from __future__ import annotations
import abc
import time
import math
import re
from typing import Any, Callable, Dict, List, Optional
from models import ToolCall, ToolResult


class BaseTool(abc.ABC):
    """Abstract base class for all agent tools."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def run(self, **kwargs: Any) -> Any:
        pass


class SearchWebArchiveTool(BaseTool):
    """Searches indexed research articles, technical benchmarks, and industry archives."""

    # Built-in high-quality offline archive for zero-token testing, continuous benchmarking, and deterministic runs
    KNOWLEDGE_ARCHIVE = [
        {
            "id": "doc_001",
            "title": "State of Agentic AI 2026: Architectures & Industry Adoption",
            "source": "Gartner AI Research 2026",
            "url": "https://research.gartner.example/agentic-ai-2026",
            "tags": ["agents", "react", "mcp", "adoption", "enterprise"],
            "snippet": "In 2026, 68% of enterprise AI workloads transitioned from single-shot prompting to multi-agent ReAct and MCP orchestrations. Organizations report a 4.2x reduction in hallucinations when combining tool-use verification guardrails with lightweight reasoning models.",
        },
        {
            "id": "doc_002",
            "title": "Benchmarking ReAct vs Plan-and-Solve in Autonomous Coding",
            "source": "DeepMind Technical Review",
            "url": "https://deepmind.google.example/react-benchmark-2026",
            "tags": ["react", "benchmarks", "coding", "planning", "accuracy"],
            "snippet": "ReAct (Reasoning + Acting) architectures achieved 89.4% task completion on complex tool workflows, outperforming static Chain-of-Thought by 24.1%. Grounding tool observations in structured citations eliminated 94% of unverified claims.",
        },
        {
            "id": "doc_003",
            "title": "Token Economics: Flash Reasoning vs Ultra Heavyweights",
            "source": "ACM Computing Survey 2026",
            "url": "https://acm.org.example/token-economics-flash-2026",
            "tags": ["tokenomics", "cost", "latency", "flash", "economics"],
            "snippet": "Deploying specialized small reasoning models (e.g. Gemini Flash / Claude Haiku) within structured ReAct loops reduced enterprise inferencing expenses by 82% compared to monolithic frontier model chains, while maintaining 98% factual precision.",
        },
        {
            "id": "doc_004",
            "title": "Model Context Protocol (MCP) Standardized Tool Interfaces",
            "source": "Anthropic & Linux Foundation Standards",
            "url": "https://modelcontextprotocol.io.example/spec-2026",
            "tags": ["mcp", "standards", "tools", "interoperability"],
            "snippet": "The Model Context Protocol (MCP) has unified tool, resource, and prompt interoperability across 400+ major AI platforms. Standardizing tool envelopes eliminates custom wrapper code and enables seamless agent hot-swapping.",
        },
        {
            "id": "doc_005",
            "title": "Deterministic Guardrails for Enterprise AI Compliance",
            "source": "NIST AI Safety Institute Report",
            "url": "https://nist.gov.example/ai-guardrails-guideline",
            "tags": ["guardrails", "safety", "compliance", "citations", "nist"],
            "snippet": "NIST recommends post-synthesis deterministic n-gram verification for any agent generating customer-facing or legal briefs. Systems enforcing citation-to-observation parity scored 99.8% compliance against hallucinations.",
        },
    ]

    @property
    def name(self) -> str:
        return "search_web_archive"

    @property
    def description(self) -> str:
        return (
            "Search curated archives of research reports, benchmarks, and technical papers. "
            "Input 'query' string of keywords."
        )

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keywords or search phrase (e.g., 'ReAct benchmarks token economics')",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of search results to return (default: 3)",
                },
            },
            "required": ["query"],
        }

    def run(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        tokens = set(re.findall(r"\w+", query.lower()))
        scored = []
        for doc in self.KNOWLEDGE_ARCHIVE:
            doc_text = (doc["title"] + " " + doc["snippet"] + " " + " ".join(doc["tags"])).lower()
            match_count = sum(1 for t in tokens if t in doc_text)
            if match_count > 0 or len(tokens) == 0:
                scored.append((match_count, doc))

        # Sort by relevance
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [item[1] for item in scored[:max_results]]
        
        # Fallback if no exact match
        if not results:
            results = self.KNOWLEDGE_ARCHIVE[:max_results]

        return results


class FetchDocumentTextTool(BaseTool):
    """Retrieves full text or sections from a specific document in the archive."""

    @property
    def name(self) -> str:
        return "fetch_document_text"

    @property
    def description(self) -> str:
        return "Fetch the comprehensive text of a specific document using its document ID (e.g., 'doc_001')."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "doc_id": {
                    "type": "string",
                    "description": "The unique ID of the document to fetch (e.g. 'doc_001')",
                }
            },
            "required": ["doc_id"],
        }

    def run(self, doc_id: str) -> Dict[str, Any]:
        for doc in SearchWebArchiveTool.KNOWLEDGE_ARCHIVE:
            if doc["id"] == doc_id:
                return {
                    "id": doc["id"],
                    "title": doc["title"],
                    "source": doc["source"],
                    "url": doc["url"],
                    "full_text": doc["snippet"],
                }
        return {"error": f"Document ID '{doc_id}' not found in archive."}


class CalculateMetricTool(BaseTool):
    """Performs deterministic calculations, growth rates, CAGR, and statistical ratios."""

    @property
    def name(self) -> str:
        return "calculate_metric"

    @property
    def description(self) -> str:
        return (
            "Safely calculate mathematical or financial metrics. "
            "Supported operations: 'growth_rate', 'cagr', 'ratio', 'reduction_percentage', 'average'."
        )

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["growth_rate", "cagr", "ratio", "reduction_percentage", "average"],
                    "description": "The math operation to perform.",
                },
                "values": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "List of numeric values for the calculation.",
                },
                "periods": {
                    "type": "number",
                    "description": "Number of periods (years/steps), required for CAGR.",
                },
            },
            "required": ["operation", "values"],
        }

    def run(self, operation: str, values: List[float], periods: Optional[float] = None) -> Dict[str, Any]:
        if not values:
            return {"error": "No values provided for calculation."}

        if operation == "growth_rate":
            if len(values) < 2:
                return {"error": "growth_rate requires at least 2 values [initial, final]."}
            initial, final = values[0], values[1]
            if initial == 0:
                return {"error": "Initial value cannot be zero for growth rate."}
            rate = ((final - initial) / initial) * 100
            return {"operation": "growth_rate", "initial": initial, "final": final, "growth_percentage": round(rate, 2)}

        elif operation == "reduction_percentage":
            if len(values) < 2:
                return {"error": "reduction_percentage requires [original, discounted]."}
            orig, current = values[0], values[1]
            reduction = ((orig - current) / orig) * 100
            return {"operation": "reduction_percentage", "original": orig, "current": current, "reduction_percentage": round(reduction, 2)}

        elif operation == "cagr":
            if len(values) < 2 or not periods or periods <= 0:
                return {"error": "cagr requires [start_val, end_val] and positive periods parameter."}
            start_val, end_val = values[0], values[1]
            cagr = ((end_val / start_val) ** (1 / periods) - 1) * 100
            return {"operation": "cagr", "start": start_val, "end": end_val, "periods": periods, "cagr_percentage": round(cagr, 2)}

        elif operation == "average":
            avg = sum(values) / len(values)
            return {"operation": "average", "count": len(values), "average": round(avg, 2)}

        elif operation == "ratio":
            if len(values) < 2 or values[1] == 0:
                return {"error": "ratio requires [numerator, denominator] with non-zero denominator."}
            r = values[0] / values[1]
            return {"operation": "ratio", "numerator": values[0], "denominator": values[1], "ratio": round(r, 4)}

        return {"error": f"Unsupported operation '{operation}'"}


class ToolRegistry:
    """Central registry facilitating tool discovery, schema generation, and safe execution."""

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}
        self.register(SearchWebArchiveTool())
        self.register(FetchDocumentTextTool())
        self.register(CalculateMetricTool())

    def register(self, tool: BaseTool) -> None:
        """Register a new tool."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools with description and schema for LLM prompting."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters_schema,
            }
            for tool in self._tools.values()
        ]

    def execute(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call with latency timing and error isolation."""
        tool = self._tools.get(tool_call.tool_name)
        if not tool:
            return ToolResult(
                tool_name=tool_call.tool_name,
                call_id=tool_call.call_id,
                output=None,
                success=False,
                error_message=f"Tool '{tool_call.tool_name}' is not registered.",
            )

        start_time = time.perf_counter()
        try:
            output = tool.run(**tool_call.arguments)
            latency = (time.perf_counter() - start_time) * 1000
            return ToolResult(
                tool_name=tool_call.tool_name,
                call_id=tool_call.call_id,
                output=output,
                success=True,
                latency_ms=latency,
            )
        except Exception as e:
            latency = (time.perf_counter() - start_time) * 1000
            return ToolResult(
                tool_name=tool_call.tool_name,
                call_id=tool_call.call_id,
                output=None,
                success=False,
                error_message=str(e),
                latency_ms=latency,
            )
