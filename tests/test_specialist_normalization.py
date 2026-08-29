"""Tests the pure `_to_finding` normalization functions in each specialist
adapter -- how a specialist project's own already-produced output object
maps onto this project's SpecialistFinding -- with hand-built fixtures,
zero LLM cost and zero dependency on either specialist's live agent.
"""

from revops.agents.schemas import Confidence, EvidenceCitation as RevOpsEvidence, InvestigationReport, RiskLevel
from revops.data.repository import Deal
from revops.flagging.rules import FlagReason, FlaggedDeal

from investigator.agent.schemas import (
    EvidenceCitation as DataInvEvidence,
    FinalReport,
    PriorLikelihood,
    RootCauseCategory,
)

from execos.specialists.data_investigation import _to_finding as data_investigation_to_finding
from execos.specialists.revenue_ops import _to_finding as revenue_ops_to_finding


def test_revenue_ops_normalization_maps_fields_correctly():
    deal = Deal(
        deal_id="d_test", account_id="a_test", account_name="Test Account", name="Test Deal", amount=50000.0,
        stage="negotiation", close_date="2026-09-01", created_date="2026-01-01", owner="Someone",
    )
    flagged = FlaggedDeal(deal=deal, reasons=[FlagReason.STALE], days_since_last_activity=45)
    report = InvestigationReport(
        risk_level=RiskLevel.HIGH, risk_explanation="Champion has gone quiet.",
        evidence=[RevOpsEvidence(record_type="activity", record_id="a1", note="No activity in 45 days.")],
        recommended_action="Escalate to account team.", confidence=Confidence.HIGH, open_questions=[],
        investigation_complete=True,
    )

    finding = revenue_ops_to_finding(flagged, report, grounding_violations=[], run_id="run-1")

    assert finding.specialist == "revenue_ops"
    assert finding.finding_id == "revenue_ops:d_test"
    assert "Test Deal" in finding.query_context
    assert finding.summary == "high risk"
    assert finding.narrative == "Champion has gone quiet."
    assert finding.confidence == "high"
    assert finding.evidence == ["(activity:a1) No activity in 45 days."]
    assert finding.specialist_grounding_passed is True
    assert finding.raw_run_id == "run-1"


def test_revenue_ops_normalization_reflects_grounding_failure():
    deal = Deal(
        deal_id="d_test", account_id="a_test", account_name="Test Account", name="Test Deal", amount=50000.0,
        stage="negotiation", close_date="2026-09-01", created_date="2026-01-01", owner="Someone",
    )
    flagged = FlaggedDeal(deal=deal, reasons=[], days_since_last_activity=None)
    report = InvestigationReport(
        risk_level=RiskLevel.LOW, risk_explanation="n", evidence=[],
        recommended_action="n", confidence=Confidence.LOW, open_questions=[],
        investigation_complete=True,
    )
    finding = revenue_ops_to_finding(flagged, report, grounding_violations=["hallucinated citation"], run_id="run-2")
    assert finding.specialist_grounding_passed is False


def test_data_investigation_normalization_maps_fields_correctly():
    report = FinalReport(
        conclusion_category=RootCauseCategory.GENUINE_BUSINESS_CHANGE,
        conclusion_summary="A real spike in enterprise deal closures.",
        confidence=PriorLikelihood.HIGH, confidence_score=0.9,
        evidence=[DataInvEvidence(query_id=1, finding="3 large deals closed same day.")],
        ruled_out=[], investigation_complete=True,
    )
    finding = data_investigation_to_finding("2025-07-08", report, grounding_violations=[], run_id="run-3")

    assert finding.specialist == "data_investigation"
    assert finding.finding_id == "data_investigation:2025-07-08"
    assert "2025-07-08" in finding.query_context
    assert finding.summary == "genuine_business_change"
    assert finding.narrative == "A real spike in enterprise deal closures."
    assert finding.confidence == "high"
    assert finding.evidence == ["(query 1) 3 large deals closed same day."]
    assert finding.specialist_grounding_passed is True
    assert finding.raw_run_id == "run-3"


def test_data_investigation_normalization_reflects_grounding_failure():
    report = FinalReport(
        conclusion_category=RootCauseCategory.DATA_QUALITY_ISSUE, conclusion_summary="n",
        confidence=PriorLikelihood.LOW, confidence_score=0.2, evidence=[], ruled_out=[],
        investigation_complete=False,
    )
    finding = data_investigation_to_finding("2026-02-10", report, grounding_violations=["bad citation"], run_id="run-4")
    assert finding.specialist_grounding_passed is False
