"""The normalized shape every specialist adapter returns to the Supervisor
(PROJECT.md Section 6: "receiving structured, evidence-tagged findings
back"). This is the only interface the Supervisor ever sees -- it never
sees a specialist project's own internal types (revops.InvestigationReport,
investigator.FinalReport), which keeps the Supervisor decoupled from each
specialist's independent internal schema evolution, and is what makes the
permission-isolation boundary in supervisor/*.py enforceable and testable.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class SpecialistFinding(BaseModel):
    specialist: Literal["revenue_ops", "data_investigation"]
    finding_id: str
    query_context: str
    summary: str
    narrative: str
    confidence: str
    evidence: list[str]
    specialist_grounding_passed: bool
    raw_run_id: str | None = None
    available: bool = True
    error: str | None = None
