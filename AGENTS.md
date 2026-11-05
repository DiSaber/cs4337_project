# Repository guidance for coding agents

## Read before working

Read [.specify/memory/constitution.md](.specify/memory/constitution.md) before planning,
implementing, or reviewing changes. It defines project principles and quality gates.
Read [README.md](README.md) and any additional instructions in the directories you change.
Follow applicable agent/system instructions and the user's current request; surface conflicts
with the constitution rather than silently overriding it or changing project governance.

## Spec Kit context

For feature work, resolve the active feature from the repository root with:

```powershell
.specify/scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly
```

This mode only resolves paths and does not update local feature state. Read the returned
feature directory's `spec.md`, `plan.md`, and `tasks.md` when they exist, plus relevant
`research.md`, `data-model.md`, `contracts/`, `quickstart.md`, and `checklists/` artifacts.
Use the resolved directory rather than assuming a feature from its name, branch, or age.
If no active feature resolves, inspect the user's specified feature and existing artifacts;
ask only if the intended feature remains ambiguous. Do not invent missing requirements.

Keep changes consistent with the constitution and the feature's acceptance criteria, design,
and task dependencies. Update affected artifacts when authorized scope changes. Mark tasks
complete only after implementation and appropriate verification. Routine repository
maintenance does not require creating a feature spec unless requested.

## Skills and workflow

Repository Spec Kit skills live in [.agents/skills/](.agents/skills/). Before using one,
read its `SKILL.md` and follow its scope, prerequisites, template resolution, and hooks.
Always use a skill explicitly requested by the user. Select the relevant skill for the
current stage rather than automatically running the entire workflow:

- `speckit-constitution`: adopt or amend project principles.
- `speckit-specify` and `speckit-clarify`: define and clarify feature requirements.
- `speckit-plan`: produce the implementation plan and design artifacts.
- `speckit-tasks`: generate dependency-ordered implementation tasks.
- `speckit-checklist` and `speckit-analyze`: check requirements quality and artifact consistency.
- `speckit-implement`: execute the implementation tasks.
- `speckit-converge`: compare implementation with artifacts and capture remaining work.
- `speckit-taskstoissues`: convert tasks into GitHub issues when requested.

Use the provided scripts and template resolver as directed by the skill. Do not edit
generated integration metadata or template sources as a substitute for updating a feature
artifact. Keep `.specify/feature.json` and other ignored machine-local state out of commits.

## Completion expectations

Apply the constitution's requirements for reproducibility, data separation, honest evaluation,
and evidence. Keep the core pipeline ahead of stretch goals. Document external assets and
provide automated acquisition/setup, preferably idempotent; keep large assets and credentials
out of Git. Use verification appropriate to the change and report what was actually checked.

For each completed AI-assisted feature or task, add a concise entry to
[docs/ai-use-log.md](docs/ai-use-log.md) describing the task, assistance, and review or
verification. Exact conversations and responses are not required. Report prose must remain
in the students' own words under the course policy.
