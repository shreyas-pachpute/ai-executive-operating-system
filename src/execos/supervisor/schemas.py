"""Supervisor Agent I/O schemas. PROJECT.md Section 6: the Supervisor
"does not introduce new claims of its own that aren't grounded in a
specialist's findings" -- every SynthesisClaim, fact or hypothesis, must
name which specialist finding(s) motivated it (`based_on_finding_ids`);
the fact/hypothesis split itself is the "same discipline as Project 10."
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class ClaimType(StrEnum):
    FACT = "fact"
    HYPOTHESIS = "hypothesis"


class RoutingDecision(BaseModel):
    relevant_specialists: list[Literal["revenue_ops", "data_investigation"]] = Field(
        description="Which specialist domain(s) this question/signal requires investigation from."
    )
    reasoning: str


class SynthesisClaim(BaseModel):
    claim_type: ClaimType = Field(
        description="'fact' if directly stated by a specialist's finding; 'hypothesis' if it's your own "
        "inference connecting findings across specialists."
    )
    statement: str
    based_on_finding_ids: list[str] = Field(
        description="The exact finding_id(s) (from the specialist findings you were given) this claim is based on. Never empty."
    )


class SynthesisOutput(BaseModel):
    coverage_note: str = Field(
        description="Explicitly states which domains this report covers and which it doesn't -- never implies completeness it doesn't have."
    )
    claims: list[SynthesisClaim]
    cross_domain_connection_found: bool
    connection_confidence: Literal["high", "medium", "low", "none"]
    connection_reasoning: str = Field(description="The specific evidentiary basis for the connection claim, or why none was found.")
