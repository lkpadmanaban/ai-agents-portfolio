"""Minimal Graph RAG agent.

- Loads an edge list CSV (source,target) into an adjacency list.
- Provides a simple sub‑graph extraction based on a start node and depth.
- Stub `generate_answer` returns a formatted string; replace with real LLM call later.
"""
import csv
from pathlib import Path
from typing import Dict, List, Set

class GraphRAG:
    def __init__(self, edge_csv: str):
        self.graph: Dict[str, Set[str]] = {}
        self._load_edges(Path(edge_csv))

    def _load_edges(self, csv_path: Path) -> None:
        with csv_path.open(newline="") as f:
            reader = csv.reader(f)
            for src, dst in reader:
                self.graph.setdefault(src, set()).add(dst)
                self.graph.setdefault(dst, set()).add(src)  # undirected for demo

    def subgraph(self, start: str, depth: int = 1) -> Set[str]:
        visited: Set[str] = {start}
        frontier: Set[str] = {start}
        for _ in range(depth):
            next_frontier: Set[str] = set()
            for node in frontier:
                next_frontier.update(self.graph.get(node, []))
            visited.update(next_frontier)
            frontier = next_frontier
        return visited

    def generate_answer(self, query: str, start_node: str) -> str:
        # Very naive: just list the sub‑graph nodes.
        nodes = self.subgraph(start_node)
        return f"Query: {query}\nRelevant nodes (depth≈1): {', '.join(sorted(nodes))}"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run minimal Graph‑RAG demo")
    parser.add_argument("--graph", required=True, help="Path to edge CSV file")
    parser.add_argument("--query", required=True, help="User question")
    parser.add_argument("--start", required=True, help="Start node for sub‑graph")
    args = parser.parse_args()
    rag = GraphRAG(args.graph)
    print(rag.generate_answer(args.query, args.start))
