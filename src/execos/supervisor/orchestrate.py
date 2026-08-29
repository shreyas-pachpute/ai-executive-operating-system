"""The Supervisor Agent: route -> delegate -> synthesize (PROJECT.md
Section 20). Exactly two of the Supervisor's own LLM calls regardless of
how many specialists are invoked (routing, then synthesis) -- specialist
delegation itself costs whatever each specialist's own investigation costs
internally, entirely outside this module's control, which is the point:
the Supervisor doesn't reach into a specialist's own investigation depth.

`synthesize()` is exposed standalone (not just inside `run_supervisor`) so
the Supervisor's own reasoning is independently testable/runnable against
hand-built or fixture specialist findings, without needing a live call into
either underlying specialist project.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from execos.config import Config
from execos.llm import LLMClient
from execos.specialists.schemas import SpecialistFinding
from execos.supervisor.grounding import validate_synthesis_grounding
from execos.supervisor.prompts import SYSTEM_INSTRUCTION, routing_prompt, synthesis_prompt
from execos.supervisor.schemas import RoutingDecision, SynthesisOutput


@dataclass
class SupervisorTrace:
    run_id: str
    question: str
    routing: RoutingDecision
    findings: list[SpecialistFinding]
    unavailable: list[str]
    synthesis: SynthesisOutput
    grounding_violations: list[str]
    llm_call_count: int
    llm_prompt_tokens: int
    llm_output_tokens: int


def route(llm: LLMClient, question: str) -> RoutingDecision:
    return llm.generate_structured(SYSTEM_INSTRUCTION, routing_prompt(question), RoutingDecision)


def synthesize(llm: LLMClient, question: str, findings: list[SpecialistFinding], unavailable: list[str]) -> SynthesisOutput:
    return llm.generate_structured(SYSTEM_INSTRUCTION, synthesis_prompt(question, findings, unavailable), SynthesisOutput)


def _invoke_specialist(name: str, deal_id: str | None, target_date: str | None) -> SpecialistFinding:
    if name == "revenue_ops":
        from execos.specialists.revenue_ops import investigate_deal_signal

        return investigate_deal_signal(deal_id)
    if name == "data_investigation":
        from execos.specialists.data_investigation import investigate_revenue_anomaly

        if not target_date:
            raise ValueError("target_date is required to invoke the data_investigation specialist.")
        return investigate_revenue_anomaly(target_date)
    raise ValueError(f"Unknown specialist '{name}'.")


def run_supervisor(
    llm: LLMClient, question: str, deal_id: str | None = None, target_date: str | None = None
) -> SupervisorTrace:
    routing = route(llm, question)

    findings: list[SpecialistFinding] = []
    unavailable: list[str] = []
    for name in routing.relevant_specialists:
        try:
            findings.append(_invoke_specialist(name, deal_id, target_date))
        except Exception as exc:  # a specialist's own systems being unavailable must never crash the report
            unavailable.append(f"{name}: {exc}")

    synthesis = synthesize(llm, question, findings, unavailable)
    violations = validate_synthesis_grounding(synthesis, findings)

    return SupervisorTrace(
        run_id=uuid.uuid4().hex[:12],
        question=question,
        routing=routing,
        findings=findings,
        unavailable=unavailable,
        synthesis=synthesis,
        grounding_violations=violations,
        llm_call_count=llm.call_count,
        llm_prompt_tokens=llm.prompt_tokens,
        llm_output_tokens=llm.output_tokens,
    )
