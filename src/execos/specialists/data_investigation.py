"""Data Specialist adapter -- delegates to Project 09's already-built,
already-tested Root-Cause Investigation Agent (PROJECT.md Section 9:
"reused"). This module is the ONLY place in this codebase allowed to
import `investigator`; supervisor/*.py never does (enforced by
tests/test_permission_isolation.py).

`_to_finding` is split out as a pure function, same reasoning as
specialists/revenue_ops.py.
"""

from __future__ import annotations

from investigator.agent.loop import InvestigationTrace as DataInvestigationTrace
from investigator.agent.schemas import FinalReport
from investigator.config import load_config
from investigator.report.render import save_run as save_investigator_run

from execos.specialists.schemas import SpecialistFinding


def _to_finding(target_date: str, report: FinalReport, grounding_violations: list[str], run_id: str) -> SpecialistFinding:
    return SpecialistFinding(
        specialist="data_investigation",
        finding_id=f"data_investigation:{target_date}",
        query_context=f"Revenue anomaly investigation for {target_date}",
        summary=report.conclusion_category.value,
        narrative=report.conclusion_summary,
        confidence=report.confidence.value,
        evidence=[f"(query {e.query_id}) {e.finding}" for e in report.evidence],
        specialist_grounding_passed=not grounding_violations,
        raw_run_id=run_id,
    )


def investigate_revenue_anomaly(target_date: str) -> SpecialistFinding:
    """Delegates to Project 09: investigates a revenue metric anomaly on
    the given date (ISO format, e.g. '2025-04-15').
    """
    from investigator.agent.loop import run_investigation

    config = load_config()
    trace: DataInvestigationTrace = run_investigation(config, target_date)
    save_investigator_run(trace, config.runs_dir)

    return _to_finding(target_date, trace.final_report, trace.grounding_violations, trace.run_id)
