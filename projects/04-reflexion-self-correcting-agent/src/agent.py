"""
Reflexion Autonomous Loop Orchestrator for Project 04.
Coordinates Action -> Critic Evaluation -> Self-Reflection -> Memory Update -> Retry.
"""

from __future__ import annotations
import time
import uuid
from typing import Any, Dict, Optional
from models import ReflexionTaskState, ReflectionEntry, ExecutionStatus
from engine import ActorGenerator, CriticEvaluator


class ReflexionAgent:
    """
    Self-Correcting Autonomous Agent using the Reflexion architecture.
    """

    def __init__(self, actor: Optional[ActorGenerator] = None, critic: Optional[CriticEvaluator] = None, max_attempts: int = 3):
        self.actor = actor or ActorGenerator()
        self.critic = critic or CriticEvaluator()
        self.max_attempts = max_attempts

    def run(self, objective: str) -> ReflexionTaskState:
        """
        Executes the self-healing Reflexion loop until convergence or max attempts reached.
        """
        start_time = time.perf_counter()
        state = ReflexionTaskState(
            task_id=f"ref_{uuid.uuid4().hex[:8]}",
            objective=objective,
            max_attempts=self.max_attempts,
        )

        for attempt in range(1, self.max_attempts + 1):
            state.current_attempt = attempt

            # Step 1: Actor generates payload using current episodic memory
            payload = self.actor.generate_payload(objective, attempt, state.episodic_memory)

            # Step 2: Critic evaluates payload
            feedback = self.critic.evaluate(payload)

            if feedback.passed:
                state.final_output = payload
                state.status = ExecutionStatus.SELF_CORRECTED if attempt > 1 else ExecutionStatus.SUCCESS
                break

            # Step 3: Self-Reflection formulation on failure
            self_reflection, remediation = self.actor.formulate_reflection(attempt, feedback)

            # Step 4: Update episodic memory buffer
            reflection_entry = ReflectionEntry(
                iteration=attempt,
                attempted_action=f"Payload submission attempt #{attempt}",
                error_feedback=feedback.diagnostics or feedback.error_type or "Unknown error",
                self_reflection=self_reflection,
                remediation_strategy=remediation,
            )
            state.add_reflection(reflection_entry)

        if not state.final_output:
            state.status = ExecutionStatus.EXHAUSTED

        state.total_execution_ms = (time.perf_counter() - start_time) * 1000
        return state
