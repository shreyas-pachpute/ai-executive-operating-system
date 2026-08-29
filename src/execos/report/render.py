"""Renders a Supervisor run to JSON (full audit trail, PROJECT.md Section
18 -- "which specialists were invoked and why, each specialist's findings
and confidence, the Supervisor's synthesis reasoning") and Markdown (the
executive-facing report).
"""

from __future__ import annotations

import json
from pathlib import Path

from execos.supervisor.orchestrate import SupervisorTrace


def trace_to_dict(trace: SupervisorTrace) -> dict:
    return {
        "run_id": trace.run_id,
        "question": trace.question,
        "routing": trace.routing.model_dump(mode="json"),
        "findings": [f.model_dump(mode="json") for f in trace.findings],
        "unavailable": trace.unavailable,
        "synthesis": trace.synthesis.model_dump(mode="json"),
        "grounding_violations": trace.grounding_violations,
        "supervisor_llm_call_count": trace.llm_call_count,
        "supervisor_prompt_tokens": trace.llm_prompt_tokens,
        "supervisor_output_tokens": trace.llm_output_tokens,
    }


def render_markdown(trace: SupervisorTrace) -> str:
    s = trace.synthesis
    lines = [
        f"# Executive Report — {trace.run_id}",
        "",
        f"**Question:** {trace.question}",
        f"**Specialists invoked:** {trace.routing.relevant_specialists}",
        f"**Grounding:** {'PASSED' if not trace.grounding_violations else 'FAILED — ' + '; '.join(trace.grounding_violations)}",
        "",
        f"**Coverage:** {s.coverage_note}",
        "",
        f"**Cross-domain connection found:** {s.cross_domain_connection_found} (confidence: {s.connection_confidence})",
        f"**Connection reasoning:** {s.connection_reasoning}",
        "",
        "## Claims",
    ]
    for c in s.claims:
        lines.append(f"- [{c.claim_type.value.upper()}] {c.statement} (based on: {c.based_on_finding_ids})")

    lines.append("")
    lines.append("## Specialist Findings")
    for f in trace.findings:
        lines.append(f"### {f.specialist} — {f.finding_id}")
        lines.append(f"- **Context:** {f.query_context}")
        lines.append(f"- **Summary:** {f.summary}  |  **Confidence:** {f.confidence}  |  **Own grounding passed:** {f.specialist_grounding_passed}")
        lines.append(f"- **Narrative:** {f.narrative}")
        for e in f.evidence:
            lines.append(f"  - {e}")
        lines.append("")

    if trace.unavailable:
        lines.append("## Unavailable Specialists")
        for u in trace.unavailable:
            lines.append(f"- {u}")

    lines += [
        "",
        "## Observability",
        f"- Supervisor LLM calls: {trace.llm_call_count} (routing + synthesis; each specialist's own internal LLM "
        "usage is tracked separately in that specialist's own saved run)",
        f"- Supervisor prompt tokens: {trace.llm_prompt_tokens}, output tokens: {trace.llm_output_tokens}",
    ]
    return "\n".join(lines)


def save_run(trace: SupervisorTrace, runs_dir: Path) -> Path:
    run_dir = runs_dir / trace.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "trace.json").write_text(json.dumps(trace_to_dict(trace), indent=2), encoding="utf-8")
    (run_dir / "report.md").write_text(render_markdown(trace), encoding="utf-8")
    return run_dir
