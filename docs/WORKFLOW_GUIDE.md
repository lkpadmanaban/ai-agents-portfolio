# Enterprise Agent Development Workflow Guide

This document describes the **standardized, enterprise‑grade process** we will follow for every new AI agent we build.

---
## 1️⃣ Capture Requirements
1. Define the agent’s **Goal**, **Key Features**, **Non‑functional Requirements**, **Stakeholders**, and **Target Date**.
2. Open a **Requirements** issue (epic) using the template `agent_requirements.md`.
3. Link any related research or design docs.

---
## 2️⃣ Create Issues (Epic → Sub‑tasks)
- The epic automatically becomes the parent of all subsequent tasks.
- Use the `agent_task.md` template for each sub‑task (implementation, testing, docs, CI).  Include:
  - Description
  - Acceptance criteria
  - Owner
  - Estimated effort
  - `parent: #<epic‑number>`

---
## 3️⃣ Branching Strategy
| Type | Prefix | Example |
|------|--------|----------|
| Feature | `feat/` | `feat/graph-rag` |
| Bug fix | `fix/` | `fix/reflexion` |
| Chore/infra | `chore/` | `chore/update‑ci` |

All branch names are **lower‑case**, **kebab‑separated**, and start with the appropriate prefix.

---
## 4️⃣ Development Cycle
1. Create a branch from `main` using the naming convention.
2. Implement the code.
3. Run **unit / integration tests** locally. Coverage must be ≥80 % before PR.
4. Commit changes with conventional‑commit messages (e.g., `feat(graph-rag): add vector store`).
5. Push the branch.
6. Open a Pull Request using the PR template `agent_pr.md`.
   - Title follows: `<type>(<scope>): <short description>`
   - Body includes Related Issues (`Closes #123`) and Verification steps.
7. PR review + CI checks.
8. Merge to `main` (squash‑merge preferred).
9. After merge:
   - Run the agent’s CLI to verify end‑to‑end functionality.
   - Generate documentation (including this diagram) and commit to `docs/`.
   - Update `PORTFOLIO_STATUS.md` with the new agent entry.

---
## 5️⃣ Pull Request Naming Convention
```
<type>(<scope>): <short description>
```
- **type** – `feat`, `fix`, `chore`, `docs`, `test`
- **scope** – kebab‑case agent name (e.g., `graph-rag`)
- **short description** – imperative, ≤50 chars.

**Examples**
- `feat(graph-rag): implement vector store ingestion`
- `fix(reflexion): correct RAM validation logic`
- `docs(reflexion): add architecture diagram`

---
## 6️⃣ Diagram Overview (Mermaid)
```mermaid
flowchart TD
    A[Capture Requirements] --> B[Create Requirements Issue (Epic)]
    B --> C[Create Sub‑tasks (Issues)]
    C --> D[Create Feature Branch]
    D --> E[Implement Code]
    E --> F[Run Unit / Integration Tests]
    F --> G[Open Pull Request]
    G --> H[PR Review & CI]
    H --> I[Merge to main]
    I --> J[Generate Docs & Diagram]
    J --> K[Update PORTFOLIO_STATUS.md]
```

---
## 7️⃣ Helper Script (`scripts/create_agent.sh`)
The repository also ships a small bash script that automates steps 1‑5 for a new agent. See the script file for details.

---
### 🎉 Ready to use!
Follow this guide for every future agent to ensure consistent quality, traceability, and fast onboarding for reviewers.
