"""Deterministic grounding validation for the Supervisor's synthesis
(PROJECT.md Section 6: every claim traces to a specialist's cited
evidence). Beyond per-claim citation checks, this also enforces Section
131's "false correlation" concern structurally: a claimed cross-domain
connection must actually be backed by claims spanning more than one
specialist -- the Supervisor cannot report a connection while only ever
citing evidence from a single domain.
"""

from __future__ import annotations

from execos.specialists.schemas import SpecialistFinding
from execos.supervisor.schemas import SynthesisOutput


def validate_synthesis_grounding(synthesis: SynthesisOutput, findings: list[SpecialistFinding]) -> list[str]:
    violations: list[str] = []
    findings_by_id = {f.finding_id: f for f in findings}

    cited_specialists: set[str] = set()
    for claim in synthesis.claims:
        if not claim.based_on_finding_ids:
            violations.append(f"Claim '{claim.statement[:60]}' cites zero specialist findings.")
            continue
        for fid in claim.based_on_finding_ids:
            finding = findings_by_id.get(fid)
            if finding is None:
                violations.append(
                    f"Claim '{claim.statement[:60]}' cites finding_id '{fid}', which was never "
                    "returned by any invoked specialist."
                )
            else:
                cited_specialists.add(finding.specialist)

    if synthesis.cross_domain_connection_found and len(cited_specialists) < 2:
        violations.append(
            "cross_domain_connection_found=True, but the claims cite evidence from fewer than 2 "
            f"distinct specialists ({sorted(cited_specialists)}) -- a cross-domain connection requires "
            "evidence from more than one domain."
        )

    return violations
