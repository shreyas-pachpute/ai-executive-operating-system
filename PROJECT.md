# AI Executive Operating System

## 1. One-Sentence Explanation

This is an AI system that lets an executive ask "what's happening in my company and why" and get a real, evidence-backed answer pulled together across departments — instead of waiting for someone to manually compile it, or never finding out at all.

## 2. The Business Problem

An executive running a company of any real size faces a structural information problem: the facts that would let them spot a brewing issue early — a support ticket pattern signaling churn risk, a sales pipeline stalling in a specific segment, a cost line drifting off budget, a project slipping behind schedule — each live in a different department's systems (CRM, support, finance, project management, HR, analytics), and no one person or system connects them automatically. Executives today learn about cross-department problems either through scheduled reporting cadences (weekly/monthly, meaning real delay between when a signal appears and when it's noticed) or through someone escalating manually (meaning it depends on someone noticing, caring enough to escalate, and having the access to do so).

Companies address this today with executive dashboards (usually siloed by department, rarely connecting signals across them), regular business reviews (valuable but infrequent relative to how fast some problems compound), and a lot of informal synthesis that happens in an executive's own head as they sit in enough meetings across enough functions to start connecting dots themselves — which doesn't scale as a company grows past the point where one person can attend every relevant meeting.

The cost is late detection of business-impacting issues — by the time a cross-department pattern becomes visible through normal reporting cadences, it's often already had weeks or months to compound. If nothing changes, this gets worse as companies grow: more departments, more systems, more data, and a widening gap between what's technically knowable from existing company data and what any one executive can actually piece together in time to act on it.

**This is the portfolio's capstone project because it's the hardest one to get right, and it's the one where getting the human-approval and evidence-trail architecture wrong would do the most damage** — a system positioned as "here's what's happening in your company" that's actually wrong, or that fabricates confidence it doesn't have, is a uniquely dangerous kind of AI failure at the executive level. Every design decision in this document is made with that risk foregrounded.

## 3. Who Would Use This?

- **CEO / General Manager:** Wants a trustworthy, evidence-backed answer to "what's happening and why" without waiting for the next scheduled business review.
- **CFO / COO:** Wants cross-department financial and operational signals connected (e.g., a support cost spike correlated with a product issue correlated with a churn signal) faster than siloed departmental reporting would surface it.
- **Department Leaders (Sales, Support, Finance, Product, HR):** Want their department's signals to be visible at the executive level accurately and in proper context, and want a fair, evidence-based process — not a black box — behind any issue surfaced about their area.
- **Board (indirect, via the executive team):** Benefits from faster, better-informed executive decision-making, though this system's outputs are explicitly internal executive-support tools, not board-facing artifacts, without human curation first.

## 4. Current Process Without AI

```
Business review cadence arrives (weekly/monthly/quarterly)
 → Each department prepares its own report/dashboard independently
 → Executive team reviews department reports largely in isolation from each other
 → Cross-department patterns are noticed only if someone happens to connect them mentally
     during or after the review
 → Between review cycles, an emerging issue is only escalated if someone in the affected
     department notices, judges it significant enough, and has a clear path to escalate it
 → By the time a genuinely cross-functional issue surfaces at the executive level,
     it has often been building for weeks
```

The fundamental limitation isn't lack of data — most of the relevant data already exists somewhere in company systems — it's that no one is systematically connecting it across department boundaries between scheduled review cycles, because doing that manually, continuously, across a whole company, exceeds what any person or existing report cadence can do.

## 5. Proposed AI-Powered Process

```
Continuous, deterministic monitoring across connected department systems (CRM, support, finance,
   project management, HR, analytics) — anomaly/threshold detection, not AI reasoning
 ↓
Supervisor Agent receives a monitoring signal or an executive's direct question
 ↓
Supervisor Agent determines which specialist agents/workflows are relevant and delegates:
   - Revenue signal -> reuses Project 01's investigation logic
   - Support/churn signal -> reuses Project 02's investigation logic
   - Financial variance -> reuses Project 07's investigation logic
   - Data anomaly -> reuses Project 09's investigation logic
   - Operational/incident signal -> reuses Project 11's investigation logic
 ↓
Specialist agents investigate within their domain and return evidence-backed findings to the Supervisor
 ↓
Supervisor Agent synthesizes cross-department findings into a single coherent narrative,
   explicitly distinguishing confirmed evidence from inference (same fact/hypothesis discipline as Project 10),
   and assesses whether findings from different departments are actually connected or coincidental
 ↓
Executive reviews the synthesized report (or asks a follow-up/drill-down question, which re-invokes
   the relevant specialist agent for deeper investigation)
 ↓
For any recommended action, especially anything cross-department or high-impact, human approval
   is required before anything happens beyond the report itself — this system informs decisions,
   it does not make or execute them
```

## 6. What the AI Actually Does

**Reasoning:** The Supervisor Agent decides which specialist domains are relevant to a signal or question, and reasons about whether findings from different departments are meaningfully connected (a support spike and a sales stall in the same account segment might be related; a support spike and an unrelated HR metric probably aren't) — genuinely open-ended synthesis across domains.

**Retrieval:** Delegates to specialist agents (largely the same agents designed in Projects 01, 02, 07, 09, and 11) to retrieve and investigate within their own domains.

**Analysis:** Synthesizes multiple specialist findings into a single cross-department narrative, maintaining the fact-vs-hypothesis discipline established in Project 10 throughout.

**Decision support:** Surfaces what needs executive attention and why, and — where relevant — what actions might address it, explicitly framed as options for human decision, never as a decision already made.

**Tool usage:** The Supervisor Agent's primary "tool" is delegation to specialist agents; it does not directly query raw department systems itself, preserving each specialist's domain expertise and permission scope (see Section 8).

**Communication:** Produces internal, executive-facing reports and supports follow-up drill-down questions — it does not communicate externally (to the board, to customers, to the public) under any circumstance without full human authorship and approval.

**Validation:** Every claim in a synthesized report traces back to a specific specialist agent's cited evidence — the Supervisor Agent does not introduce new claims of its own that aren't grounded in a specialist's findings.

**What the AI does NOT do:** It does not execute any action in any department's systems — no CRM changes, no financial transactions, no HR actions, no production changes. It does not make a business decision. It does not communicate externally. It does not present a cross-department inference as confirmed fact. It does not replace the specialist agents' own domain-specific human-approval boundaries (defined in each of Projects 01, 02, 07, 09, 11) — this system adds a synthesis layer on top of those boundaries, it does not loosen them.

## 7. Where AI Is Used

AI is good at exactly the cross-domain synthesis problem this project targets: recognizing that a signal in one department's data might be meaningfully connected to a signal in another's, something that currently only happens when a human happens to be paying attention to both simultaneously. It's good at maintaining a continuously current, evidence-backed picture across many domains at once, which no single human executive can do by manually reviewing every department's raw data personally. It's good at answering a genuinely novel follow-up question ("does this connect to what's happening in the Northeast region specifically?") by re-invoking the right specialist investigation, rather than being limited to a fixed, pre-built report.

Deterministic software must handle the underlying monitoring/anomaly-detection in each department's data (the same deterministic-threshold principle used throughout every project this one builds on) and must handle every actual calculation (financial figures reused from Project 07's deterministic engine, in particular, must never be recomputed by any layer of this system). Any actual action in any department's systems remains subject to that department's own existing approval processes — this system never bypasses a department-level control by virtue of being "the executive system."

## 8. Agent vs Workflow vs Normal Software

- **Normal software:** Each department's underlying system of record, the monitoring/alerting infrastructure feeding signals into this system, the executive-facing UI, and — importantly — the specific deterministic calculation engines this project explicitly reuses rather than reimplements (Project 07's financial engine, Project 05's staffing scoring engine if HR/resourcing signals are in scope).
- **Deterministic workflow:** Signal detection within each department (the same threshold/anomaly-detection logic described in each underlying project) remains a fixed, rule-based trigger — this project does not change how those signals are generated, only what happens once multiple signals need cross-department synthesis.
- **AI agent (specialist level):** Each specialist agent is the corresponding agent already designed in this portfolio (Projects 01, 02, 07, 09, 11) — this project deliberately does **not** redesign domain-specific investigation logic; it reuses it, which is both good engineering practice and a demonstration of architectural coherence across this entire portfolio.
- **Multi-agent system (supervisor + specialists):** This is the one project in the entire portfolio where a genuine supervisor/specialist multi-agent architecture is fully justified, because the roles are **genuinely independent** (a revenue-operations investigation and a support-churn investigation require different data access, different domain logic, and different specialist reasoning) and because **context isolation matters enormously** — a Supervisor Agent trying to hold all of sales, support, finance, HR, and operations context simultaneously in one context window would be both unwieldy and worse at each individual domain than a dedicated specialist. This is the portfolio's clearest example of multi-agent decomposition chosen for real architectural reasons, in direct contrast to Project 05's deliberate rejection of multi-agent architecture for a problem that didn't need it — read together, these two projects demonstrate the actual judgment this portfolio is built to prove.

## 9. Agent Roles

**Supervisor Agent:** "Given a monitoring signal or an executive's question, determine which specialist domains are relevant, delegate investigation to them, and synthesize their evidence-backed findings into a single coherent, appropriately-hedged narrative — never introducing an unsourced claim of its own." **Revenue Specialist** (Project 01's Deal Investigation Agent, reused). **Support Specialist** (Project 02's Ticket Investigation Agent, reused). **Finance Specialist** (Project 07's Variance Investigation Agent, reused). **Data Specialist** (Project 09's Root-Cause Investigation Agent, reused). **Operations Specialist** (Project 11's Incident Investigation Agent, reused). Each specialist retains its own domain-specific human-approval boundaries and tool permissions exactly as defined in its originating project — the Supervisor Agent does not gain broader access by virtue of coordinating them; it only receives their already-bounded findings.

## 10. Tools the AI Needs

In business terms: the Supervisor Agent's primary capability is delegating to the specialist agents already described in Projects 01, 02, 07, 09, and 11, plus a cross-department pattern-correlation capability (comparing findings across specialists for meaningful connection) and an executive-facing report/query interface.

Technically: an internal agent-to-agent invocation mechanism (the Supervisor calling each specialist agent as a bounded subtask and receiving structured, evidence-tagged findings back — an internal orchestration pattern, not necessarily the external A2A protocol, since these are agents within one organization's own system, not independent agents crossing an organizational trust boundary per Research Notes Section 10), and a synthesis/correlation layer producing the final structured, fact-vs-hypothesis-labeled report.

## 11. MCP Opportunities

Each specialist agent's own MCP tool/resource connectors (CRM, support system, general ledger, data warehouse, observability stack — all already specified in their respective project documents) remain unchanged and are not directly accessible to the Supervisor Agent, which only interacts with each specialist's already-processed, bounded output — this is a deliberate permission-isolation design choice, not an oversight: the Supervisor coordinating five departments' worth of investigation should not itself hold five departments' worth of raw data access, both for blast-radius reasons and because it doesn't need raw access to do its actual job (synthesis of already-investigated findings). What should **not** be exposed to the Supervisor Agent: direct raw access to any department's underlying system — if the Supervisor needs deeper investigation in one domain, the correct pattern is delegating a more specific question back to that domain's specialist agent, not bypassing the specialist to query the system directly.

## 12. Human-in-the-Loop

**Low-risk (automatic):** Signal monitoring, specialist investigation (governed by each specialist's own already-defined low-risk boundary from its originating project), and cross-department synthesis into a report.

**Medium-risk (requires executive review before being treated as settled):** Every synthesized cross-department report — presented with full evidence citation and explicit fact/hypothesis labeling, reviewed by the executive before any conclusion is acted on or shared further, given how consequential a wrong "here's what's happening in your company" claim would be.

**High-risk (must never happen automatically, and inherits every underlying specialist's own high-risk boundary unchanged):** Any action within any department's systems — this system adds zero new action capability beyond what each specialist agent already has (and each specialist, per its own project document, has no ability to take irreversible or externally-visible action without human approval). Additionally, and specific to this project: no content generated by this system reaches the board, external stakeholders, or public communications without full human authorship — this system supports executive understanding, it is never the author of record for anything leaving the executive's own review.

## 13. Business Value

The clearest measurable driver is time-to-detection for cross-department issues — how quickly a pattern that currently would only surface at the next scheduled business review (potentially weeks away) gets surfaced instead, measurable by comparing detection latency for a set of known historical cross-department issues against what this system would have surfaced and when. A second driver is executive time saved synthesizing information manually across department reports — measurable via direct feedback and time tracking during a pilot. Given how significant and hard-to-isolate the value of "caught a real problem earlier" can be, we would not assign a speculative dollar figure to avoided business impact; the correct approach is the detection-latency metric in Section 14, which is directly measurable and doesn't require speculative downstream attribution.

## 14. Success Metrics

- **Cross-department detection latency** — time from when a pattern is present in underlying data to when it's surfaced to the executive, compared to the existing business-review-cadence baseline.
- **Synthesis accuracy** — on a curated set of historical cross-department issues with known causes, does the system correctly identify and connect the relevant signals?
- **Fact/hypothesis labeling integrity** — same rigorous audit standard as Project 10, applied to Supervisor-level synthesis specifically, since synthesis across specialists is exactly where an unsupported connective claim ("these are related") could slip in.
- **False correlation rate** — cases where the system connected two department signals that a human review determines were actually unrelated (a critical negative metric, since false cross-department connections could send executive attention in an unproductive or actively misleading direction).
- **Executive trust/adoption** — usage rate and satisfaction, tracked via structured feedback, given that this system only delivers value if executives actually use and trust it over the status quo.
- **Specialist-agent inherited metrics** — each specialist's own accuracy/grounding/evaluation metrics (defined in its originating project) remain tracked independently, since a synthesis layer is only as good as the specialist findings it synthesizes.

## 15. Failure Scenarios

- **False cross-department correlation:** the Supervisor connects two unrelated signals into a misleading narrative — mitigated by requiring the Supervisor to state the strength and specific evidentiary basis for any claimed connection, and by tracking false-correlation rate as a first-class metric (Section 14).
- **Specialist-level failure propagating upward:** a wrong finding from an underlying specialist agent (any of the failure modes already documented in Projects 01/02/07/09/11) flows into the executive synthesis — mitigated by the Supervisor preserving and surfacing each specialist's own confidence level rather than presenting all findings with uniform certainty, and by the underlying specialists' own evaluation and grounding requirements remaining fully in force, not superseded by this project.
- **Executive over-trust / automation complacency:** the most consequential failure mode is behavioral, not technical — an executive treating a synthesized report as more authoritative than its actual evidence supports, simply because it's comprehensive and well-written — mitigated by consistent, unavoidable fact/hypothesis labeling in the UI itself (not just available in fine print) and by the system explicitly stating investigation limitations and gaps rather than presenting artificial completeness.
- **Incomplete department coverage:** signals from a department not yet connected to the system are invisible to it — mitigated by the system explicitly stating its own coverage scope in every report ("this analysis covers Sales, Support, and Finance; HR and Product signals are not yet connected"), so absence of a finding is never mistaken for "nothing is happening" in an uncovered domain.
- **Tool/specialist failure:** a specialist agent's underlying systems are unavailable — the Supervisor should report that domain's investigation as unavailable, not silently omit it or proceed with stale data.

## 16. Safety and Security

This project inherits every safety and security requirement from Projects 01, 02, 07, 09, and 11 unchanged and unrelaxed — coordinating them at the executive level does not create an exception to any specialist's own permission scope, data-access boundary, or action restriction. The Supervisor Agent's own access is deliberately narrower than the union of its specialists' access (Section 11) — it receives bounded, already-processed findings, not raw cross-department data access, which meaningfully limits the blast radius of any Supervisor-level compromise or malfunction. Given that this system produces the single most consequential, highest-visibility output in the entire portfolio (an executive-facing "here's what's happening" narrative), audit logging must be comprehensive: every specialist invocation, every piece of evidence used in synthesis, and the full reasoning trail behind any claimed cross-department connection, retained and reviewable. Access to the executive-facing system itself should be tightly scoped — this is, by design, an executive-tier tool, and the sensitivity of having visibility into synthesized signals across every department (including HR, if in scope) requires access control at least as strict as the most sensitive underlying department system it touches.

## 17. Evaluation

- **Synthesis correctness:** on a curated set of historical cross-department scenarios with known outcomes, does the Supervisor correctly identify genuine connections and correctly avoid false ones?
- **Fact/hypothesis labeling integrity audit:** the same rigorous standard as Project 10, applied here specifically to cross-department connective claims.
- **Specialist-inherited evaluation:** each underlying specialist's own evaluation suite (defined in its originating project) continues to run independently and must pass before its findings feed into this system's synthesis — this project does not get to have a lower evaluation bar than its component parts.
- **Coverage-scope accuracy:** does the system correctly and consistently communicate what it does and doesn't have visibility into?
- **Human evaluation:** structured executive feedback on report usefulness and trustworthiness, collected regularly, given how central trust is to this system's actual adoption and value.
- **Cost and latency** per synthesized report, which will generally be higher than any single specialist project given the multi-agent delegation pattern — this needs explicit tracking and budget-awareness given the frequency executives might reasonably invoke it.

## 18. Observability

Track, per report or query: which specialists were invoked and why, each specialist's findings and confidence, the Supervisor's synthesis reasoning (specifically, the evidentiary basis for any claimed cross-department connection), and the executive's eventual feedback/action. This project's observability requirements are the union of all its component specialists' requirements (Section 16) plus a new layer specific to synthesis quality — the connections claimed between domains are the novel value this system adds over its component parts, and are exactly the place where quality needs the most scrutiny, since they're the hardest claims to verify and the most consequential if wrong. Track false-correlation rate and labeling-integrity audit results as the standing top-line quality dashboard for this project specifically, above and beyond the specialist-level dashboards each underlying project already defines.

## 19. Technology Options

**LangGraph (as the Supervisor's orchestration layer):** *Why:* the supervisor/specialist delegation pattern with structured findings flowing back for synthesis is a well-established LangGraph pattern, and durable state matters given that a full cross-department investigation may take meaningful time to complete across several specialist delegations. *Why not:* if specialists are implemented on genuinely different internal frameworks (per their own project's technology choices), the Supervisor's orchestration layer needs a clean, framework-agnostic delegation interface rather than assuming everything lives inside one LangGraph graph. *Alternative:* a lighter-weight internal delegation protocol (structured request/response) that treats each specialist as a black-box service, regardless of what framework implements it internally — arguably the more realistic real-world integration pattern given this portfolio's specialists were each designed with their own independent technology choices.

**A2A protocol:** *Why:* worth naming explicitly given this project's supervisor/specialist structure superficially resembles A2A's use case. *Why not, specifically:* per Research Notes Section 10, A2A is designed for agents crossing an organizational/trust boundary — these specialists are all internal to the same company and system, which is exactly the case Research Notes Section 10 identifies as *not* needing A2A; an internal delegation protocol is the right-sized choice, and reaching for A2A here would be adding interoperability-protocol overhead with no actual interoperability need. *Alternative (only if genuinely relevant later):* if a future version needed to delegate to a genuinely external agent (e.g., a partner company's specialist agent), A2A would become relevant at that specific boundary, not before.

**Temporal:** *Why:* a full cross-department investigation, potentially involving several specialist delegations that themselves may involve long-running or approval-gated steps (per each specialist's own project), benefits from durable execution so the overall synthesis doesn't lose state if any one specialist's investigation takes longer than expected. *Why not:* significant infrastructure investment; likely justified only once this system is handling non-trivial investigation volume and depth. *Alternative:* simpler orchestration for an MVP scoped to faster, shallower specialist delegations.

**MCP:** *Why:* not directly used by the Supervisor Agent itself (Section 11), but every specialist it delegates to already uses MCP extensively per its own project document — this project is a demonstration of MCP's compounding value across a portfolio, not a new MCP use case in its own right. *Why not more directly:* deliberately kept out of the Supervisor's own access surface for the permission-isolation reasons in Section 11.

## 20. Proposed Architecture

```
Executive Interface (report view + follow-up question capability)
        |
     API Layer -------------------------- Auth (executive-tier access control)
        |
  Supervisor Agent (LangGraph, delegation + synthesis, NO direct raw data access)
        |
   +---------------+---------------+---------------+---------------+
   |               |               |               |               |
 Revenue Ops     Support         Finance          Data            Operations
 Specialist      Specialist      Specialist       Specialist      Specialist
 (Project 01)    (Project 02)    (Project 07)     (Project 09)    (Project 11)
   |               |               |               |               |
 [each specialist retains its own full architecture, tools, and human-approval
  boundaries exactly as defined in its own PROJECT.md — unchanged by this project]
        |
  Synthesized, Evidence-Cited, Fact/Hypothesis-Labeled Report
        |
  Executive Review -> Drill-Down Questions (re-invoke relevant specialist) -> [Human-Only Decisions & Actions]
        |
  Evaluation & Observability Layer (union of all specialist requirements + synthesis-specific auditing)
```

## 21. MVP

The smallest version that proves value: connect just two specialists that are already independently built and validated (e.g., the Revenue Operations Agent from Project 01 and the Data Investigation Agent from Project 09) behind a minimal Supervisor Agent that can answer a narrow class of executive questions spanning both domains (e.g., "is this revenue dip connected to a data quality issue"), with full evidence citation and explicit fact/hypothesis labeling — no HR/Ops/Support specialists yet, no continuous monitoring, only on-demand executive queries. This validates whether cross-domain synthesis actually produces trustworthy, useful output before investing in the full five-specialist architecture — and, critically, this MVP is only realistic to build *after* at least two specialist projects already exist and have been independently validated, making this project's honest prerequisite sequencing (Section 23) a real part of its design.

## 22. Future Version

MVP (two specialists, on-demand only) → add the remaining specialists as their own projects mature and are independently validated → add continuous monitoring (proactive signal detection, not just on-demand query response) → add richer drill-down/follow-up conversation capability → add a curated, human-reviewed board-facing summary mode (still never bypassing full human authorship) → the permission-isolation between the Supervisor and each specialist's raw data access remains a permanent architectural property, not something a later version collapses for convenience, even as trust in the system grows.

## 23. What Makes This Project Difficult?

This is deliberately the hardest project in the portfolio, and its difficulty is compounding rather than merely additive: it inherits every hard problem from its five component specialist projects (document/data variety, evaluation cost, confidence calibration, permission scoping) **plus** a genuinely new hard problem — cross-domain correlation — which has no ground truth as clean as any single domain's, since "are these two signals actually related" is often a judgment call even for a human who deeply understands both domains. Context management is uniquely hard at this layer: the Supervisor has to reason about relationships between domains without holding full domain-level detail in its own context, which is precisely why the specialist-delegation architecture (Section 8) is necessary, not optional. Evaluation requires cross-domain historical incidents with confirmed connections, which are rare and hard to label even with expert review. And the honest engineering sequencing matters more here than anywhere else in the portfolio: this project is not implementable as a first project — it requires several specialist projects to already exist, be independently evaluated, and be trustworthy in their own right before a synthesis layer on top of them means anything at all; building the Supervisor first, with unvalidated or stubbed specialists underneath it, would produce an impressive-looking demo and a genuinely untrustworthy system.

## 24. What I Would Demonstrate When Implementing It

A genuine supervisor/specialist multi-agent architecture with real, justified permission isolation (not decorative role labels); reuse of independently-built and independently-evaluated specialist agents rather than reimplementing domain logic inside the supervisor; a synthesis layer with its own dedicated evaluation category (cross-domain correlation accuracy and false-correlation rate) distinct from and in addition to each specialist's own evaluation; consistent, UI-level (not just documentation-level) fact/hypothesis labeling at the point where it matters most — the executive's screen; and honest, explicit coverage-scope communication so the system never implies completeness it doesn't have.

## 25. Portfolio Story

"This is the capstone project specifically because it's where every principle in the rest of the portfolio has to hold simultaneously, under the highest stakes — a wrong 'here's what's happening in your company' claim at the executive level is a uniquely damaging kind of AI failure. I built it as a genuine supervisor/specialist architecture, but the interesting design decision wasn't adding agents, it was what the Supervisor deliberately does *not* have: raw access to any department's underlying data. It only ever receives already-investigated, already-bounded findings from specialist agents that each retain their own permission scope and approval boundaries unchanged. And I treated the sequencing as part of the design, not an implementation detail — this system isn't buildable first; it only means something once its component specialists are independently proven trustworthy on their own. That's the same judgment this whole portfolio is built to demonstrate, just at the point where getting it wrong would matter most."

## 26. Questions a CTO Might Ask Me

1. Why doesn't the Supervisor Agent have direct access to each department's data — wouldn't that be more efficient?
2. How do you evaluate a cross-domain correlation claim when there's often no clean ground truth?
3. What's your false-correlation rate, and what's the actual cost when the system connects two unrelated signals?
4. Why is this project sequenced last — couldn't it be built as the first, most impressive demo?
5. How do you prevent an executive from over-trusting a comprehensive, well-written but partially wrong report?
6. What happens when two specialist agents' findings actually conflict with each other?
7. How does permission isolation between the Supervisor and specialists actually work, concretely?
8. Why not use the A2A protocol for supervisor-specialist communication, given the multi-agent structure?
9. What's the cost and latency for a full five-specialist synthesized report, and is that sustainable at real query volume?
10. How do you communicate honestly what departments/data the system doesn't yet cover?
11. What's the audit trail if an executive acts on a synthesized report that turns out to be based on a wrong specialist finding?
12. How would you pilot this without it becoming a black box executives either blindly trust or ignore?
13. Why does this system never produce board-facing or external content directly?
14. How do you keep this system's evaluation bar as high as its component specialists', not lower?
15. What's the single hardest part of this project, in your own view, and how would you de-risk it first?

## 27. Research Sources

- [LangGraph vs LangChain 2026 — Spheron Blog](https://www.spheron.network/blog/langgraph-vs-langchain/)
- [A2A Protocol — official site](https://a2a-protocol.org/latest/)
- [Announcing the Agent2Agent Protocol (A2A) — Google Developers Blog](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
- [Temporal — AI Applications & Agents](https://temporal.io/solutions/ai)
- [LLM Agent Evaluation Metrics in 2026 — Confident AI](https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide)
- See also [../RESEARCH_NOTES.md](../RESEARCH_NOTES.md) for full ecosystem sourcing, and Projects 01, 02, 07, 09, and 11 in this portfolio, whose specialist agents this project reuses directly.
