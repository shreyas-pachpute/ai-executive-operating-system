"""Eval harness for the Supervisor's own synthesis reasoning, run against
the fixture scenarios in eval/fixtures.py (PROJECT.md Section 131's "false
correlation rate" as the headline metric this eval reports).
"""

from __future__ import annotations

from dataclasses import dataclass

from execos.eval.fixtures import ALL_FIXTURES, FixtureScenario
from execos.llm import LLMClient
from execos.supervisor.grounding import validate_synthesis_grounding
from execos.supervisor.orchestrate import synthesize
from execos.supervisor.schemas import SynthesisOutput


@dataclass
class FixtureEvalResult:
    scenario: FixtureScenario
    synthesis: SynthesisOutput
    grounding_violations: list[str]
    correct: bool


@dataclass
class EvalSummary:
    results: list[FixtureEvalResult]

    @property
    def accuracy(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.correct) / len(self.results)

    @property
    def false_correlation_rate(self) -> float:
        """Of the scenarios where no connection actually exists, what
        fraction did the Supervisor incorrectly claim a connection for?
        """
        negatives = [r for r in self.results if not r.scenario.expected_connection_found]
        if not negatives:
            return 0.0
        false_positives = sum(1 for r in negatives if r.synthesis.cross_domain_connection_found)
        return false_positives / len(negatives)

    @property
    def grounding_pass_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if not r.grounding_violations) / len(self.results)


def run_synthesis_eval(llm: LLMClient) -> EvalSummary:
    results: list[FixtureEvalResult] = []
    for scenario in ALL_FIXTURES:
        synthesis = synthesize(llm, scenario.question, scenario.findings, unavailable=[])
        violations = validate_synthesis_grounding(synthesis, scenario.findings)
        correct = synthesis.cross_domain_connection_found == scenario.expected_connection_found
        results.append(FixtureEvalResult(scenario=scenario, synthesis=synthesis, grounding_violations=violations, correct=correct))
    return EvalSummary(results=results)
