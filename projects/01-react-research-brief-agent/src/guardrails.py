"""
Verification Guardrails and Hallucination Prevention Pipeline.
Ensures factual grounding, citation authenticity, and evidence integrity before publication.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple
from models import ExecutiveBrief, Citation, KeyFinding


@dataclass
class GuardrailResult:
    """Outcome of safety, citation grounding, and fact-checking checks."""
    passed: bool
    grounding_score: float
    total_claims: int
    grounded_claims: int
    unverified_citations: List[Dict[str, str]] = field(default_factory=list)
    flagged_inconsistencies: List[str] = field(default_factory=list)
    verdict: str = "PASS"


class CitationGuardrail:
    """
    Validates that cited quotes and numerical claims in the generated Executive Brief
    directly originate from the agent's actual tool observations.
    """

    def __init__(self, min_token_overlap_ratio: float = 0.65) -> None:
        self.min_overlap = min_token_overlap_ratio

    def _normalize(self, text: str) -> List[str]:
        """Convert string to normalized lower-case token list."""
        return re.findall(r"\b\w{3,}\b", text.lower())

    def _calculate_ngram_containment(self, snippet: str, corpus: str) -> float:
        """Computes word-level overlap ratio between a citation snippet and observation corpus."""
        snippet_tokens = self._normalize(snippet)
        if not snippet_tokens:
            return 1.0  # Empty or trivial snippet

        corpus_tokens = set(self._normalize(corpus))
        matched = sum(1 for tok in snippet_tokens if tok in corpus_tokens)
        return matched / len(snippet_tokens)

    def verify_brief(
        self, brief: ExecutiveBrief, observations: Dict[str, str]
    ) -> GuardrailResult:
        """
        Verify every citation across all key findings in the ExecutiveBrief against collected observations.
        """
        corpus = " \n ".join(observations.values())
        total_citations = 0
        verified_citations_count = 0
        unverified: List[Dict[str, str]] = []
        flagged: List[str] = []

        for finding in brief.key_findings:
            for citation in finding.citations:
                total_citations += 1
                overlap = self._calculate_ngram_containment(citation.quote_or_snippet, corpus)

                if overlap >= self.min_overlap:
                    citation.verified = True
                    verified_citations_count += 1
                else:
                    citation.verified = False
                    unverified.append({
                        "source": citation.source_name,
                        "quote": citation.quote_or_snippet,
                        "overlap_score": f"{round(overlap * 100, 1)}%",
                        "finding": finding.headline,
                    })
                    flagged.append(
                        f"Citation '{citation.source_name}' snippet has low evidence overlap ({round(overlap * 100, 1)}%): '{citation.quote_or_snippet}'"
                    )

        # Check numerical assertions in details
        brief_numbers = set(re.findall(r"\b\d+(?:\.\d+)?%?", brief.summary + " " + " ".join(f.details for f in brief.key_findings)))
        corpus_numbers = set(re.findall(r"\b\d+(?:\.\d+)?%?", corpus))

        # Check for ungrounded hallucinated numbers
        hallucinated_numbers = brief_numbers - corpus_numbers
        # Filter out common standard numbers (like 1, 2, 3 list enumerations, 2026 current year)
        hallucinated_numbers = {n for n in hallucinated_numbers if n not in {"1", "2", "3", "4", "5", "2026"}}

        if hallucinated_numbers:
            for num in hallucinated_numbers:
                flagged.append(f"Potential ungrounded numerical assertion detected: '{num}' was not present in tool observations.")

        # Compute aggregate grounding score
        if total_citations == 0:
            # If no citations were attached, score based on finding details containment
            finding_text = " ".join(f.details for f in brief.key_findings)
            grounding_score = self._calculate_ngram_containment(finding_text, corpus)
        else:
            grounding_score = verified_citations_count / total_citations

        passed = grounding_score >= 0.70 and len(unverified) == 0

        verdict = "PASSED_VERIFIED" if passed else "REJECTED_UNGROUNDED"
        brief.grounding_score = grounding_score
        brief.validation_status = verdict

        return GuardrailResult(
            passed=passed,
            grounding_score=grounding_score,
            total_claims=total_citations,
            grounded_claims=verified_citations_count,
            unverified_citations=unverified,
            flagged_inconsistencies=flagged,
            verdict=verdict,
        )
