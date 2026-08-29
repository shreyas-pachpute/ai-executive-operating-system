"""Revenue Ops Specialist adapter -- delegates to Project 01's already-built,
already-tested Deal Investigation Agent (PROJECT.md Section 9: "reused").
This module is the ONLY place in this codebase allowed to import `revops`;
supervisor/*.py never does (enforced by tests/test_permission_isolation.py).

`_to_finding` is split out as a pure function so the normalization logic
(revops's InvestigationReport -> this project's SpecialistFinding) is
unit-testable with hand-built fixtures, at zero cost, independent of the
live call to Project 01's own Gemini-backed agent below it.
"""

from __future__ import annotations

import uuid

from revops.agents.grounding import validate_grounding
from revops.agents.investigation import investigate_deal
from revops.agents.llm import GeminiClient
from revops.agents.schemas import InvestigationReport
from revops.config import load_config
from revops.data.repository import Activity, SupportTicket, connect, get_deal
from revops.data.seed import REFERENCE_TODAY
from revops.flagging.rules import FlaggedDeal, flag_all_deals, flag_deal
from revops.report.render import InvestigationTrace as RevOpsTrace
from revops.report.render import save_run as save_revops_run

from execos.specialists.schemas import SpecialistFinding


def _to_finding(
    flagged: FlaggedDeal, report: InvestigationReport, grounding_violations: list[str], run_id: str | None
) -> SpecialistFinding:
    return SpecialistFinding(
        specialist="revenue_ops",
        finding_id=f"revenue_ops:{flagged.deal.deal_id}",
        query_context=f"At-risk deal investigation: {flagged.deal.name} (${flagged.deal.amount:,.0f})",
        summary=f"{report.risk_level.value} risk",
        narrative=report.risk_explanation,
        confidence=report.confidence.value,
        evidence=[f"({e.record_type}:{e.record_id}) {e.note}" for e in report.evidence],
        specialist_grounding_passed=not grounding_violations,
        raw_run_id=run_id,
    )


def investigate_deal_signal(deal_id: str | None = None) -> SpecialistFinding:
    """Delegates to Project 01: investigates a specific flagged deal, or
    the single highest-priority currently-flagged deal if none is given.
    """
    config = load_config()
    conn = connect(config)
    try:
        if deal_id:
            deal = get_deal(conn, deal_id)
            flagged = flag_deal(conn, deal, config, REFERENCE_TODAY)
        else:
            flagged_deals = flag_all_deals(conn, config, REFERENCE_TODAY)
            if not flagged_deals:
                return SpecialistFinding(
                    specialist="revenue_ops", finding_id="revenue_ops:none",
                    query_context="At-risk deal investigation: no deals currently flagged",
                    summary="no flagged deals", narrative="No deals in the pipeline are currently flagged by any risk rule.",
                    confidence="high", evidence=[], specialist_grounding_passed=True,
                )
            flagged = flagged_deals[0]

        client = GeminiClient(config)
        report, activities, tickets, tool_calls = investigate_deal(conn, config, client, flagged)
    finally:
        conn.close()

    violations = validate_grounding(report, activities, tickets)
    run_id = uuid.uuid4().hex[:12]
    trace = RevOpsTrace(
        run_id=run_id, flagged=flagged, report=report, activities_seen=activities,
        tickets_seen=tickets, tool_calls_executed=tool_calls, grounding_violations=violations,
        llm_call_count=client.call_count, prompt_tokens=client.prompt_tokens, output_tokens=client.output_tokens,
    )
    save_revops_run(trace, config.runs_dir)

    return _to_finding(flagged, report, violations, run_id)
