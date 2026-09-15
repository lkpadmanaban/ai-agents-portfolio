# Project 04: Loop Engineering — Self-Correcting Reflexion & Actor-Critic Agent

> **Architecture Category**: Loop Engineering / Reflexion Paradigm / Episodic Memory Self-Healing  
> **Target Role**: Forward Deployed Engineer (FDE) & Autonomous Systems Specialist  
> **Author**: Lokesh Kumar Padmanaban ([@lkpadmanaban](https://github.com/lkpadmanaban))

---

## 📌 Executive Summary
Project 04 demonstrates **Loop Engineering** via the **Reflexion Architecture** (Shinn et al.).

Instead of failing permanently when an enterprise API or database rejects a payload, the agent uses an **Actor-Critic loop with Episodic Reflection Memory** to diagnose the error, formulate a verbal self-reflection, and autonomously repair its own parameters on retry without human intervention.

---

## 🚀 Quick Start

### 1. Run Reflexion Self-Correction Demonstration
```bash
python run.py --workload "GlobalSettlementEngine"
```

### 2. Run Test Suite (100% Deterministic Pass in 0.001s)
```bash
python -m unittest discover tests -v
```

---

## 📂 Project Structure

```text
projects/04-reflexion-self-correcting-agent/
├── src/
│   ├── engine.py         # Actor generator & Critic evaluator
│   ├── agent.py          # Reflexion loop state machine & memory updates
│   ├── models.py         # ReflectionEntry & Episodic Memory schemas
│   └── cli.py            # Terminal runner & reflection trace inspector
├── tests/
│   └── test_reflexion.py # Self-healing & diagnostic unit tests
├── docs/
│   ├── coach-notes.md    # FDE Field Manual & interview mastery guide
│   └── run-report.md     # Engineering execution log & token economics
├── README.md             # Technical documentation
└── run.py                # Single-line execution entrypoint
```
