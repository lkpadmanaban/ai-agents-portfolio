"""
Actor and Critic Evaluation Engines for Project 04.
Simulates an enterprise deployment scenario where an API payload initially fails schema validation,
is critiqued by the Evaluator, and is self-healed by the Actor using reflection memory.
"""

from __future__ import annotations
import json
import re
from typing import Any, Dict, List, Tuple
from models import EvaluationFeedback, ReflectionEntry


class CriticEvaluator:
    """
    Evaluator / Critic.
    Validates enterprise API payloads against strict schema, security, and type constraints.
    """

    ENTERPRISE_TARGET_SCHEMA = {
        "tenant_id": {"type": "uuid", "regex": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"},
        "service_tier": {"type": "enum", "allowed": ["STANDARD", "PREMIUM", "ENTERPRISE_DEDICATED"]},
        "allocated_ram_mb": {"type": "int", "min": 1024, "max": 65536},
        "cmek_key_version": {"type": "string", "prefix": "projects/kms/keys/v"},
    }

    def evaluate(self, payload: Dict[str, Any]) -> EvaluationFeedback:
        """Evaluates payload and provides diagnostic feedback."""
        # 1. Check required fields
        for req_key in self.ENTERPRISE_TARGET_SCHEMA.keys():
            if req_key not in payload:
                return EvaluationFeedback(
                    passed=False,
                    score=0.2,
                    error_type="MISSING_REQUIRED_KEY",
                    diagnostics=f"Payload is missing required enterprise key '{req_key}'",
                )

        # 2. Check tenant_id UUID regex
        tenant_id = payload.get("tenant_id", "")
        if not re.match(self.ENTERPRISE_TARGET_SCHEMA["tenant_id"]["regex"], str(tenant_id)):
            return EvaluationFeedback(
                passed=False,
                score=0.4,
                error_type="INVALID_UUID_FORMAT",
                diagnostics=f"Value '{tenant_id}' for 'tenant_id' must match standard UUID format (8-4-4-4-12 hex).",
            )

        # 3. Check service_tier enum
        tier = payload.get("service_tier")
        if tier not in self.ENTERPRISE_TARGET_SCHEMA["service_tier"]["allowed"]:
            return EvaluationFeedback(
                passed=False,
                score=0.6,
                error_type="INVALID_ENUM_VALUE",
                diagnostics=f"Service tier '{tier}' is invalid. Allowed: {self.ENTERPRISE_TARGET_SCHEMA['service_tier']['allowed']}",
            )

        # 4. Check RAM limits
        ram = payload.get("allocated_ram_mb", 0)
        if not isinstance(ram, int) or ram < 1024:
            return EvaluationFeedback(
                passed=False,
                score=0.7,
                error_type="INSUFFICIENT_MEMORY_ALLOCATION",
                diagnostics=f"Allocated RAM '{ram}' MB is below enterprise baseline of 1024 MB.",
            )

        # 5. Check CMEK key prefix
        cmek = str(payload.get("cmek_key_version", ""))
        if not cmek.startswith("projects/kms/keys/v"):
            return EvaluationFeedback(
                passed=False,
                score=0.8,
                error_type="INVALID_CMEK_KEY_PREFIX",
                diagnostics=f"CMEK key version '{cmek}' must start with standard prefix 'projects/kms/keys/v'.",
            )

        return EvaluationFeedback(passed=True, score=1.0)


class ActorGenerator:
    """
    Actor Agent.
    Generates payloads and incorporates reflections from episodic memory on retry.
    """

    def generate_payload(self, objective: str, attempt: int, memory: List[ReflectionEntry]) -> Dict[str, Any]:
        """
        Generates an execution payload.
        Simulates realistic agent learning: Initial attempt has common errors; subsequent attempts
        read the episodic reflection memory and fix each flaw deterministically.
        """
        if attempt == 1:
            # Baseline naive attempt: invalid tenant format and low memory
            return {
                "workload_objective": objective,
                "tenant_id": "tenant-apex-finance-001",  # Invalid non-UUID
                "service_tier": "ENTERPRISE_DEDICATED",
                "allocated_ram_mb": 512,  # Too low (<1024)
                "cmek_key_version": "v1_key",  # Missing prefix
            }

        elif attempt == 2:
            # Attempt 2: Fixed tenant UUID and CMEK prefix from reflection, but RAM still slightly off
            return {
                "workload_objective": objective,
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                "service_tier": "ENTERPRISE_DEDICATED",
                "allocated_ram_mb": 512,  # Still needs fix
                "cmek_key_version": "projects/kms/keys/v2-prod",
            }

        else:
            # Attempt 3: Fully corrected payload incorporating all episodic memory reflections
            return {
                "workload_objective": objective,
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                "service_tier": "ENTERPRISE_DEDICATED",
                "allocated_ram_mb": 4096,  # Compliant
                "cmek_key_version": "projects/kms/keys/v2-prod",
            }

    def formulate_reflection(self, attempt: int, feedback: EvaluationFeedback) -> Tuple[str, str]:
        """Formulates self-reflection and remediation strategy based on critic diagnostics."""
        if feedback.error_type == "INVALID_UUID_FORMAT":
            reflection = "I provided a human-readable slug instead of an RFC 4122 UUID for 'tenant_id'."
            remediation = "Query enterprise tenant registry or format tenant_id as a canonical 36-character UUID."
        elif feedback.error_type == "INSUFFICIENT_MEMORY_ALLOCATION":
            reflection = "The allocated memory (512 MB) is below the production SLA minimum of 1024 MB."
            remediation = "Scale allocated_ram_mb up to 4096 MB to comply with enterprise baseline."
        elif feedback.error_type == "INVALID_CMEK_KEY_PREFIX":
            reflection = "CMEK key version was missing the fully-qualified Cloud KMS resource path prefix."
            remediation = "Prepend 'projects/kms/keys/v' to the key version string."
        else:
            reflection = f"Runtime validation failed on rule: {feedback.error_type}."
            remediation = f"Comply with evaluator diagnostic: {feedback.diagnostics}"

        return reflection, remediation
