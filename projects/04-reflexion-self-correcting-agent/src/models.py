"""
Domain Models and Episodic Memory Schemas for Project 04:
Loop Engineering — Self-Correcting Reflexion & Actor-Critic Agent.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class ExecutionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SELF_CORRECTED = "SELF_CORRECTED"
    EXHAUSTED = "EXHAUSTED"


@dataclass
class ReflectionEntry:
    """An episodic memory entry capturing a specific execution failure and learned correction."""
    iteration: int
    attempted_action: str
    error_feedback: str
    self_reflection: str
    remediation_strategy: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "iteration": self.iteration,
            "attempted_action": self.attempted_action,
            "error_feedback": self.error_feedback,
            "self_reflection": self.self_reflection,
            "remediation_strategy": self.remediation_strategy,
            "timestamp": self.timestamp,
        }


@dataclass
class EvaluationFeedback:
    """Critic evaluation of an action attempt."""
    passed: bool
    score: float  # 0.0 to 1.0
    error_type: Optional[str] = None
    diagnostics: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "score": round(self.score, 2),
            "error_type": self.error_type,
            "diagnostics": self.diagnostics,
        }


@dataclass
class ReflexionTaskState:
    """The working and episodic memory state tracked across retry loops."""
    task_id: str
    objective: str
    current_attempt: int = 0
    max_attempts: int = 3
    episodic_memory: List[ReflectionEntry] = field(default_factory=list)
    final_output: Optional[Dict[str, Any]] = None
    status: ExecutionStatus = ExecutionStatus.FAILED
    total_execution_ms: float = 0.0

    def add_reflection(self, entry: ReflectionEntry) -> None:
        self.episodic_memory.append(entry)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "objective": self.objective,
            "current_attempt": self.current_attempt,
            "max_attempts": self.max_attempts,
            "episodic_memory": [r.to_dict() for r in self.episodic_memory],
            "final_output": self.final_output,
            "status": self.status.value,
            "total_execution_ms": round(self.total_execution_ms, 2),
        }
