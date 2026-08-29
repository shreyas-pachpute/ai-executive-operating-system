"""Fixture specialist findings for exercising the Supervisor's own
synthesis reasoning (routing + cross-domain correlation) independent of a
live call into either underlying specialist project. This is what makes
the Supervisor's genuinely new logic live-testable via Ollama even though
Project 01 and Project 09 (built before the dual-provider pattern existed)
are Gemini-only -- see README's "Implementation Status" for the honest
constraint this works around.

Two scenarios, matching this project's two most consequential correctness
directions (PROJECT.md Section 131, 137):

- CONNECTED: findings that share a real, stated entity and time window
  (the same account, an overlapping date) -- a genuine basis for a
  cross-domain connection claim. The correct answer is
  cross_domain_connection_found=True.
- UNRELATED: findings with no shared entity, account, or time window --
  the correct answer is cross_domain_connection_found=False. This is the
  more important case to get right: inventing a connection here is exactly
  the "most damaging failure mode" this project's grounding architecture
  exists to prevent.

Project 01's own synthetic CRM data and Project 09's own synthetic revenue
warehouse data were built independently, weeks apart, with no shared entity
keys between them -- so a *real* connected case isn't naturally available
from live specialist calls without fabricating one, which is honestly
disclosed rather than manufactured. These fixtures fill that gap for
testing the Supervisor's own reasoning specifically.
"""

from __future__ import annotations

from dataclasses import dataclass

from execos.specialists.schemas import SpecialistFinding


@dataclass
class FixtureScenario:
    name: str
    question: str
    findings: list[SpecialistFinding]
    expected_connection_found: bool


CONNECTED = FixtureScenario(
    name="connected",
    question="Is the revenue dip on 2026-07-05 connected to any at-risk deals?",
    findings=[
        SpecialistFinding(
            specialist="revenue_ops", finding_id="revenue_ops:d_meridian",
            query_context="At-risk deal investigation: Meridian - Platform Expansion ($180,000)",
            summary="high risk",
            narrative=(
                "Meridian Health Systems' champion Dana Whitfield went quiet after flagging a budget-approval "
                "blocker on 2026-07-01; no activity since. A support ticket was opened on 2026-07-05 reporting a "
                "billing discrepancy on the Meridian invoice."
            ),
            confidence="high",
            evidence=[
                "(activity:a_meridian_1) Champion flagged a budget-approval blocker on 2026-07-01.",
                "(support_ticket:t_meridian_1) Ticket opened 2026-07-05: 'Billing discrepancy on Meridian invoice'.",
            ],
            specialist_grounding_passed=True,
        ),
        SpecialistFinding(
            specialist="data_investigation", finding_id="data_investigation:2026-07-05",
            query_context="Revenue anomaly investigation for 2026-07-05",
            summary="data_quality_issue",
            narrative=(
                "The revenue dip on 2026-07-05 traces to a batch of 3 invoice credit adjustments totaling $42,000 "
                "for account 'Meridian Health Systems', issued following a billing-system reconciliation."
            ),
            confidence="high",
            evidence=["(query 1) 3 invoice credit adjustments totaling $42,000 for account 'Meridian Health Systems' recorded on 2026-07-05."],
            specialist_grounding_passed=True,
        ),
    ],
    expected_connection_found=True,
)

UNRELATED = FixtureScenario(
    name="unrelated",
    question="Is the revenue dip on 2025-11-28 connected to any at-risk deals?",
    findings=[
        SpecialistFinding(
            specialist="revenue_ops", finding_id="revenue_ops:d_bramwell",
            query_context="At-risk deal investigation: Bramwell - Core License ($95,000)",
            summary="medium risk",
            narrative=(
                "Bramwell Logistics' deal has recent activity, but the economic buyer contact Morgan Lee has zero "
                "engagement recorded at any point -- a single-threaded deal risk."
            ),
            confidence="medium",
            evidence=["(activity:a_bramwell_1) 4 recent activities logged, all with champion Jamie Ortiz; zero activities with economic buyer Morgan Lee."],
            specialist_grounding_passed=True,
        ),
        SpecialistFinding(
            specialist="data_investigation", finding_id="data_investigation:2025-11-28",
            query_context="Revenue anomaly investigation for 2025-11-28",
            summary="seasonal_expected_variation",
            narrative="The revenue spike on 2025-11-28 (Black Friday) matches the same seasonal pattern observed in prior years.",
            confidence="high",
            evidence=["(query 1) Revenue on 2025-11-28 is within 5% of the prior-year Black Friday value for the same date."],
            specialist_grounding_passed=True,
        ),
    ],
    expected_connection_found=False,
)

ALL_FIXTURES = [CONNECTED, UNRELATED]
