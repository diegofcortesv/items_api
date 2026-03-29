# items_api — Agent Rules

## Polecat Rules (worker agents)

Read AGENT_SPEC.md before starting any task.
Work only within the scope of your assigned bead.
Read existing files before writing — do not invent file contents.
If the spec conflicts with existing code, report the conflict in the MR description.

Run the acceptance criteria command from your bead before submitting.
Do not submit if validation fails.
Include exact validation output in your MR description.

Every MR description must contain:
- Files created or modified
- Validation command and exact output
- Any deviations from the spec and why

Do not assume project structure, installed packages, or import paths.
Read requirements.txt and the repo before writing code.
If the spec is ambiguous, implement the minimal interpretation and flag it.

## Mayor Orchestration Protocol

### Bead Creation
Read AGENT_SPEC.md. Create one bead per TASK section.
Copy the full spec (context packet, specification, acceptance criteria,
output artifacts, failure modes, handoff) into the bead description verbatim.
Do not summarize or rephrase. Create a convoy with all beads in task order.

### Execution Cycle
For each bead in convoy order, execute this cycle:

1. `gt sling <bead-id> items_api` — dispatch to polecat
2. Monitor: poll `bd show <bead-id>` until a wisp/MR reference appears,
   or watch `gt feed` for merge events
3. After merge: `cd mayor/rig && git pull origin main`
4. Run the validation command from AGENT_SPEC.md for that task
5. If validation passes: `bd close <bead-id> --reason "Merged and validated"`
6. Proceed to next bead

If validation fails, stop. Do not sling the next bead. Report the failure.

### Known Limitation
`bd agent state` is not implemented in beads v0.62+.
Bead state does not transition automatically after polecat completion.
Step 5 (explicit `bd close`) is required after every validated merge.
This is not optional — without it the convoy cannot track progress.
