from execos.specialists.schemas import SpecialistFinding
from execos.supervisor.grounding import validate_synthesis_grounding
from execos.supervisor.schemas import ClaimType, SynthesisClaim, SynthesisOutput


def _finding(specialist="revenue_ops", finding_id="revenue_ops:d1") -> SpecialistFinding:
    return SpecialistFinding(
        specialist=specialist, finding_id=finding_id, query_context="c", summary="s",
        narrative="n", confidence="high", evidence=["e"], specialist_grounding_passed=True,
    )


def _synthesis(claims, connection_found=False) -> SynthesisOutput:
    return SynthesisOutput(
        coverage_note="c", claims=claims, cross_domain_connection_found=connection_found,
        connection_confidence="none", connection_reasoning="r",
    )


def test_grounded_single_specialist_claim_passes():
    claim = SynthesisClaim(claim_type=ClaimType.FACT, statement="s", based_on_finding_ids=["revenue_ops:d1"])
    violations = validate_synthesis_grounding(_synthesis([claim]), [_finding()])
    assert violations == []


def test_claim_with_zero_finding_ids_flagged():
    claim = SynthesisClaim(claim_type=ClaimType.FACT, statement="s", based_on_finding_ids=[])
    violations = validate_synthesis_grounding(_synthesis([claim]), [_finding()])
    assert any("zero specialist findings" in v for v in violations)


def test_claim_citing_unknown_finding_id_flagged():
    claim = SynthesisClaim(claim_type=ClaimType.FACT, statement="s", based_on_finding_ids=["revenue_ops:nonexistent"])
    violations = validate_synthesis_grounding(_synthesis([claim]), [_finding()])
    assert any("nonexistent" in v for v in violations)


def test_connection_claimed_with_only_one_specialist_cited_is_flagged():
    claim = SynthesisClaim(claim_type=ClaimType.HYPOTHESIS, statement="connected", based_on_finding_ids=["revenue_ops:d1"])
    violations = validate_synthesis_grounding(_synthesis([claim], connection_found=True), [_finding()])
    assert any("fewer than 2 distinct specialists" in v for v in violations)


def test_connection_claimed_with_two_specialists_cited_passes():
    findings = [_finding("revenue_ops", "revenue_ops:d1"), _finding("data_investigation", "data_investigation:2025-04-15")]
    claims = [
        SynthesisClaim(claim_type=ClaimType.FACT, statement="a", based_on_finding_ids=["revenue_ops:d1"]),
        SynthesisClaim(claim_type=ClaimType.HYPOTHESIS, statement="connected", based_on_finding_ids=["revenue_ops:d1", "data_investigation:2025-04-15"]),
    ]
    violations = validate_synthesis_grounding(_synthesis(claims, connection_found=True), findings)
    assert violations == []


def test_no_connection_claimed_never_requires_two_specialists():
    claim = SynthesisClaim(claim_type=ClaimType.FACT, statement="s", based_on_finding_ids=["revenue_ops:d1"])
    violations = validate_synthesis_grounding(_synthesis([claim], connection_found=False), [_finding()])
    assert violations == []
