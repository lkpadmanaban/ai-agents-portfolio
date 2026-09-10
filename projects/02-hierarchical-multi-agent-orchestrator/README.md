# Project 02: Hierarchical Multi-Agent Enterprise Migration Orchestrator

> **Architecture Category**: Multi-Agent Systems / Supervisor-Worker Topology / Consensus Arbitration  
> **Target Engineering Role**: Forward Deployed Engineer (FDE) & Solutions Architect  
> **Author**: Lokesh Kumar Padmanaban ([@lkpadmanaban](https://github.com/lkpadmanaban))

---

## 📌 Executive Summary
Project 02 implements a production-grade **Hierarchical Multi-Agent Orchestrator** designed for Forward Deployed Engineers (FDEs) navigating enterprise workload modernization.

A **Supervisor Orchestrator** deconstructs complex enterprise architectures into specialized parallel missions assigned to 3 domain sub-agents:
1. **Topology Engineer**: Discovers microservice dependencies and sub-millisecond database latencies.
2. **Security Auditor**: Detects unencrypted PII, TLS gaps, and exercises compliance vetoes.
3. **FinOps Analyst**: Computes 3-year committed cloud TCO and sizing models.

When sub-agents disagree (e.g., FinOps cost-cutting vs. InfoSec compliance), a **Consensus Engine** arbitrates deterministically using enterprise risk priorities.

---

## 🚀 Quick Start

### 1. Run Autonomous Multi-Agent Migration Assessment
```bash
python run.py --workload "GlobalCoreBankingEngine" --client "Tier1GlobalBank"
```

### 2. Run Test Suite (100% Deterministic Pass in 0.002s)
```bash
python -m unittest discover tests -v
```

---

## 📂 Project Structure

```text
projects/02-hierarchical-multi-agent-orchestrator/
├── src/
│   ├── orchestrator.py    # Supervisor state machine & dynamic decomposition
│   ├── workers.py         # Topology, Security, and FinOps specialized sub-agents
│   ├── consensus.py       # Dispute arbitration & deterministic veto engine
│   ├── models.py          # Strongly typed inter-agent message envelopes
│   └── cli.py             # Enterprise CLI runner & dossier exporter
├── tests/
│   └── test_orchestrator.py # Comprehensive unit & arbitration tests
├── docs/
│   ├── coach-notes.md     # FDE Field Manual & interview mastery guide
│   └── run-report.md      # Engineering execution log & token economics
├── README.md              # Technical documentation
└── run.py                 # Quick execution entrypoint
```
