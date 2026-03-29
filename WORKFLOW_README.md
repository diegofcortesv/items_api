# items_api — Multi-Agent Workflow Documentation

## 1. Workflow Design

### Task Decomposition

The project was decomposed into three sequential tasks with explicit
dependency ordering. Each task produces a verifiable artifact that the
next task depends on.

| Bead   | Task                              | Validation Command                     | Result   |
|--------|-----------------------------------|----------------------------------------|----------|
| ia-5is | Scaffold + GET /health            | curl -s http://localhost:8000/health   | PASSED   |
| ia-3k8 | POST /items + pytest suite        | pytest test_items.py -v                | PASSED   |
| ia-kow | Lint + README + CHANGELOG         | ruff check .                           | PASSED   |

Convoy: `hq-cv-er5ld` — items_api v0.1.0

### Decomposition Rationale

Tasks were ordered by hard dependency: the test suite (TASK-02) requires
the endpoints to exist (TASK-01), and linting/documentation (TASK-03)
requires working, tested code. No task can execute before the previous
one is merged and validated on main.

This sequencing is enforced by the Mayor Orchestration Protocol defined
in CLAUDE.md — the Mayor does not sling the next bead until the validation
command for the current bead passes.

### Spec-Driven Development

All task specifications were written in AGENT_SPEC.md and committed to
the repo before any bead was created. Each specification includes a context
packet (current state, objective, constraints, prior outputs), acceptance
criteria with exact validation commands, output artifacts, and failure modes.

When the Mayor created the beads, it copied the spec content verbatim into
the bead description. This ensures that any engineer can reconstruct what
the agent was asked to do by reading `bd show <bead-id>` alone, without
requiring context from the operator.

---

## 2. Coordination Strategy

### Agent Roles

| Role             | Agent                  | Lifecycle                                     |
|------------------|------------------------|-----------------------------------------------|
| Orchestrator     | Mayor (Claude Code)    | Persistent, town-level, reads CLAUDE.md        |
| Worker           | Polecat `obsidian`     | Ephemeral — spawns on sling, terminates on merge |
| Merge processor  | Refinery               | Persistent, per-rig, processes MRs              |
| Health monitor   | Witness                | Persistent, per-rig, detects stuck agents       |

### Orchestration Flow

The Mayor executed the full pipeline autonomously using the protocol
defined in CLAUDE.md. The human operator issued a single instruction:

```
Follow the Mayor Orchestration Protocol in CLAUDE.md.
Read AGENT_SPEC.md and create the beads and convoy as specified.
Then execute the full convoy sequentially.
```

The Mayor then executed without further human intervention:

1. Read AGENT_SPEC.md, created 3 beads with specs copied verbatim
2. Created convoy `hq-cv-er5ld` with beads in dependency order
3. For each bead: sling → monitor → pull → validate → close → next

TASK-01 and TASK-02 were dispatched to polecat `obsidian`. TASK-01
required a polecat retry (first MR ia-wisp-gxz was superseded by
ia-wisp-z7s) — the system self-corrected without human intervention.
TASK-03 was executed directly by the Mayor after the Claude API rate
limit blocked further polecat spawns. This is graceful degradation —
the Mayor adapted its execution strategy without losing the validation
discipline.

### Context Control

Each polecat receives context through two channels:

1. The bead description (copied verbatim from AGENT_SPEC.md)
2. The repo state on main (via isolated git worktree)

The polecat does not have access to the Mayor's conversation history,
previous polecat sessions, or other beads' descriptions. Context boundaries
are enforced by Gastown's architecture — polecats run in isolated worktrees
under `polecats/` and their only input is the hooked bead plus the repo.

CLAUDE.md provides additional behavioral constraints: read before writing,
do not invent file contents, include validation output in MR descriptions,
implement the minimal interpretation if the spec is ambiguous.

### Validation Controls

No agent self-validates. The Mayor runs each validation command independently
after the merge lands on main:

- TASK-01: `curl -s http://localhost:8000/health` → `{"status":"ok"}`
- TASK-02: `pytest test_items.py -v` → 6 passed, 0 failed
- TASK-03: `ruff check .` → All checks passed (exit 0)

The Mayor does not advance the convoy until validation passes. This is the
primary control against accumulated errors across phases.

---

## 3. Observability

### Progress Tracking

| Signal           | Command                          | What it shows                              |
|------------------|----------------------------------|--------------------------------------------|
| Convoy progress  | `gt convoy list`                 | Active and recently landed convoys          |
| Convoy detail    | `gt convoy status <convoy-id>`   | Per-bead open/closed state                  |
| Active agents    | `gt feed`                        | Real-time agent tree, convoy panel, events  |
| Stuck agents     | `gt feed --problems`             | Agents needing intervention                 |
| Bead state       | `bd show <bead-id>`              | Full history, assignee, close reason        |
| System health    | `gt doctor`                      | 80+ checks across workspace components      |
| Context recovery | `gt prime` (inside Mayor)        | Restores workspace context after restart    |

### Bead Audit Trail

Every closed bead contains a complete record. The close reason reveals
which closure path was used:

```
bd show ia-5is  (TASK-01)
→ Status: CLOSED
→ Close reason: Merged in ia-wisp-z7s
→ Comments: MR created: ia-wisp-gxz, MR created: ia-wisp-z7s

bd show ia-3k8  (TASK-02)
→ Status: CLOSED
→ Close reason: Merged and validated: 6 tests passed
→ Comments: MR created: ia-wisp-axy

bd show ia-kow  (TASK-03)
→ Status: CLOSED
→ Close reason: Merged and validated: ruff check All checks passed
→ Comments: (none — Mayor executed directly, no polecat involved)
```

The close reasons show two distinct closure paths operating in the same
pipeline (see Bead Closure Paths below). Any engineer can reconstruct
the full workflow state from bead records alone without querying the
operator who ran the pipeline.

### Known Display Limitation

`gt convoy status` may show 0/0 for progress due to a cross-rig display
limitation (GH #2624). Use `bd show <bead-id>` as the authoritative source
for individual bead state.

---

## 4. Failure Recovery

### Failure Mode Registry

| Failure                  | Detection               | Recovery                                         |
|--------------------------|-------------------------|--------------------------------------------------|
| Polecat stuck mid-task   | `gt feed --problems`    | `gt nudge <agent>` or `gt polecat nuke --force`  |
| Polecat MR rejected      | Second MR comment in bead | Polecat retries automatically (observed in TASK-01)|
| Refinery rejects MR      | Event stream shows error | Polecat reads error, fixes, resubmits            |
| Session crash (Mayor)    | Mayor missing from `gt agents` | `gt mayor attach` → `gt prime`            |
| Workspace inconsistency  | `gt doctor` warnings    | `gt doctor --fix`                                |
| Rate limit blocks sling  | Sling timeout or error  | Mayor executes task directly (observed in TASK-03)|
| Bead stuck in HOOKED     | `bd show` shows HOOKED after merge | Mayor closes with `bd close` (Path B) |

### Recovery Procedure

```bash
gt mayor attach          # re-attach to Mayor tmux session
gt prime                 # restore workspace context from disk
gt convoy list           # identify active convoys
bd show <bead-id>        # verify state of each bead
gt sling <bead-id> items_api  # resume from last open bead
```

State survives session crashes because beads are stored in Dolt
(git-backed SQL), not in session memory. Each polecat works in an
isolated git worktree. `gt prime` reads workspace state from disk,
not from conversation history.

### Bead Closure Paths

Two independent closure mechanisms operated during this pipeline:

**Path A — Refinery automatic closure.** When a polecat submits an MR and
the refinery merges it, Gastown can close the bead automatically with a
close reason of `Merged in <wisp-id>`. This worked for TASK-01 (ia-5is)
despite the `bd agent state` errors during sling. The refinery path does
not depend on `bd agent state`.

**Path B — Mayor explicit closure.** The Mayor runs the validation command
after merge, then executes `bd close <id> --reason "Merged and validated: <output>"`.
This was used for TASK-02 (ia-3k8) and TASK-03 (ia-kow). The close reason
contains the actual validation output, making it auditable.

The Mayor Orchestration Protocol in CLAUDE.md always executes Path B as
step 5 of the cycle. If Path A already closed the bead, `bd close` on an
already-closed bead is a no-op. This makes Path B a redundant safety net —
it guarantees closure regardless of whether the refinery path succeeded.

### Known Limitation: bd agent state

`bd agent state` is not implemented in beads v0.62+. Gastown 0.12.1 calls
this command during sling to track polecat lifecycle state, producing
`SetAgentState attempt N failed` warnings. These warnings are non-fatal —
the polecat spawns and executes correctly despite them. The actual impact
is that bead state transitions after polecat completion may not occur
through the standard Gastown path, which is why the Mayor's explicit
`bd close` (Path B) exists as a documented workaround in CLAUDE.md.

TASK-01 also demonstrated polecat retry behavior: the first MR
(ia-wisp-gxz) was created but a second MR (ia-wisp-z7s) was the one
that ultimately merged. The system self-corrected without human intervention.

---

## 5. Production Improvements

These are deliberate scope decisions for a time-boxed exercise.
Each is production-ready as a follow-on.

| Improvement                        | Rationale                                                  |
|------------------------------------|------------------------------------------------------------|
| Gastown Formula (TOML)             | Encode the full convoy as a formula for one-command reproducibility |
| Automated HITL gates via CI        | Replace manual validation with GitHub Actions pre-merge checks |
| Parallel polecat execution         | Tasks without hard dependencies run concurrently            |
| Model specialization per task      | Sonnet for implementation, Haiku for lint/docs              |
| OTEL metrics to dashboard          | Wire gastown.done.total, gastown.polecat.spawns.total to Grafana |
| Polecat health SLA                 | Max execution time per task type; Witness auto-nukes if exceeded |
| Structured bead templates          | Enforce AGENT_SPEC.md format as a bd create template        |
| Upstream bd agent state fix        | Track beads project for implementation of automatic bead closure |

---

## 6. Architectural Principles

Six principles governed every decision in this design:

**P1 — Specs precede execution.** AGENT_SPEC.md was committed before any
bead was created. The spec is the contract, not the conversation.

**P2 — Context is bounded, not assumed.** Each agent receives only what it
needs via the bead description. No inherited conversation history.

**P3 — Validation is external, not self-reported.** The Mayor runs validation
commands independently. An agent claiming success is not evidence.

**P4 — State lives in the system, not in memory.** Beads in Dolt, worktrees
in git. Nothing lives in a terminal session.

**P5 — Failure is a designed state.** Every task spec includes failure modes.
The system blocks and preserves state rather than recovering silently.

**P6 — The architect writes specs, agents execute them.** The human engineer
is responsible for decomposition and validation criteria. Agents implement.

---

*Executed on 2026-03-29 using Gastown 0.12.1, beads 0.62.0, Claude Code 2.1.86.*
*Environment: POP OS (Ubuntu-based), Python 3.10, FastAPI 0.115+.*
