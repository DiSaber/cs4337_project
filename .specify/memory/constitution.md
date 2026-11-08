# CS4337 Driving Scene Object Detection Constitution

## Core Principles

### I. Reproducible Experiments

Every reported experiment MUST record dataset versions and splits, preprocessing and
augmentation settings, model and initial weight versions, dependency versions, random seeds,
training settings, and commands needed to reproduce the result. Known sources of
nondeterminism MUST be documented. These records make comparisons explainable and allow
another team member to repeat the work.

### II. Reliable Evaluation

Training, validation, and test data MUST remain separate. Splits MUST prevent related frames
from the same source video or capture sequence from crossing partitions. Model selection
and tuning MUST use training and validation data; held-out test data MUST be reserved for
final evaluation. Reported detection results MUST include mAP with its IoU definition,
precision, recall, and representative successes and failures. Speed claims MUST state
hardware, input size, batch size, and which processing stages were timed. These rules
prevent leakage and misleading comparisons.

### III. Complete the Core Pipeline First

Work MUST prioritize a functioning dataset preparation, training, evaluation, and inference
pipeline before optional additions. Experiments on team-captured dashcam footage MUST
remain a stretch goal and MUST NOT block core deliverables. Specs and plans MUST distinguish
required work from stretch goals so the project remains achievable within course time and
available compute.

### IV. Evidence Supports Every Claim

Reported findings MUST be traceable to preserved experiment configurations and results.
Documentation MUST distinguish measured findings from hypotheses and MUST explain observed
limitations and relevant untested conditions, including lighting, weather, camera perspective,
and differences between training data and new footage. Incomplete work and unsuccessful
experiments MUST be reported honestly. Conclusions MUST remain within the evidence collected.

### V. Simple, Understandable Implementation

Implement only the requested solution. The project MUST prefer direct, readable code,
existing project patterns, and established models and libraries. Reusable frameworks,
configuration systems, speculative abstractions, extra features, and future-extension
scaffolding MUST NOT be added unless requested. Variables, parameters, intermediate aliases,
and configurable options MUST have a concrete need in the requested behavior or readability.
Treat this as a single-use project that ends at completion; do not design for reuse in other
projects, extension, or maintenance after delivery.

Setup, inputs, outputs, and execution steps MUST be documented, and team members MUST
understand and be able to explain submitted code.
Datasets, checkpoints, credentials, and large generated outputs MUST stay out of Git.
Required external assets MUST have documented acquisition instructions and an automated
setup mechanism, such as a download script. Setup SHOULD be idempotent: rerunning it reuses
valid existing assets without duplicate downloads or destructive changes. Any unavoidable
manual prerequisite or limitation on idempotency MUST be documented. This keeps the
repository manageable while making a fresh checkout practical to use.

### VI. Academic Integrity and AI Transparency

Reused code, models, datasets, and references MUST be cited. A concise AI-use log MUST be
maintained in `docs/` for each completed feature or task, identifying the task, assistance
used, and how the result was reviewed or verified. Exact conversations and responses do not
need to be included. Team members MUST understand AI-assisted code, and students MUST write
the report in their own words. AI assistance MUST comply with the course's stated policy.

### VII. No Additional Tests or Assertions

Contributors MUST NOT add automated tests, assertions, diagnostic-only cells, or separate
validation frameworks. Verify work through normal execution and manual review of existing
outputs. Required model evaluation, metrics, and assignment figures remain part of the
solution. Execution limits MUST be described honestly; results MUST NOT be invented, and
unexecuted work MUST NOT be reported as passing.

### VIII. Small Changes and User Review

Work MUST proceed in small, coherent changes suitable for individual commits. At each
review checkpoint, present the changed files, what changed, available execution evidence,
and a suggested commit message. Then stop until the user authorizes continuing. A workflow
that normally executes all tasks MUST still honor these stops. Commits MUST remain under
user control unless explicitly delegated.

### IX. Useful, Temporary Explanations

Comments MUST explain a choice or operation only where that helps the user understand it.
Use `AI: ` for temporary agent guidance and `SAMPLE: ` for suggested wording the user can
adapt for submission; never use both prefixes for the same explanation. Preserve
user-written explanations unless a correction is necessary. Before final submission,
remove temporary `AI: ` comments and have the user review and adapt `SAMPLE: ` explanations.
Use ordinary prose for narrative sections. Students MUST still write report prose in their
own words under Principle VI.

### X. Plain English

Use familiar words, direct sentences, and concrete explanations in replies, documentation,
reports, UI text, and comments. Explain necessary jargon when useful and remove filler.
Preserve facts, uncertainty, and technical meaning. Preserve code, commands, identifiers,
paths, URLs, and quotations unless changes are requested. When rewriting Markdown, preserve
headings, lists, tables, links, and YAML frontmatter unless asked otherwise. Match the
requested audience, format, tone, and level of detail without omitting needed explanations.

### XI. Existing Assignments as References

Consult available relevant assignments, examples, and existing solutions before introducing
a new approach. Follow useful patterns for code structure, libraries, naming, explanations,
and presentation so the work stays familiar to the user. Adapt only what fits the current
requirements; earlier experiments, parameters, features, and complexity MUST NOT be carried
over without a current need. Current assignment requirements and user instructions govern
the result, and reused material MUST be cited under Principle VI.

## Project Constraints

The project focuses on detecting and classifying objects in driving scenes. Specific model
versions, target classes, datasets, preprocessing services, training budgets, and dashcam
experiments MUST be defined in specs and plans rather than fixed by this constitution.
The active specification defines deliverables and required outputs. Possible improvements
MUST remain in discussion unless the user authorizes implementing them.

Course deliverables and submission requirements MUST be tracked in a deliverables checklist.
That checklist MUST cover the report, presentation, contributor roles, required links and
access, and deadlines. When provided course instructions conflict, the conflict and the
chosen interpretation MUST be recorded; unresolved ambiguity affecting submission MUST be
clarified with the instructor. The supplied report instructions permit a three-page
implementation report under both stated page limits.

## Development Workflow and Quality Gates

Before implementation, each feature spec and plan MUST be reviewed against these principles
and identify its required outcome, validation approach, and experiment records where relevant.
Before marking a feature or task complete, contributors MUST verify its intended behavior,
update affected usage documentation, and complete its AI-use log when AI was used.

Changes affecting data preparation, splitting, annotations, or metrics MUST be verified for
data integrity and evaluation correctness through normal execution and manual review of
existing outputs, without adding the test code or diagnostic machinery prohibited by
Principle VII. Routine changes MUST use verification appropriate to their impact; full model
training is required only when needed to validate the change or support a reported result.
Reported experiments MUST retain the records required by Principles I, II, and IV. Blockers
and incomplete work MUST be reported plainly.

Use the specification's review checkpoints when provided. Otherwise, complete one bounded
change and stop for user review before beginning another. Preserve unrelated user changes.
Before final delivery, review explanations with the user and confirm that reported results
match actual outputs. Sharing, submission, and publication require separate authorization.

## Governance

This constitution governs project specs, plans, tasks, implementation, and review, subject
to applicable course requirements. Current explicit user instructions take precedence over
this constitution and workflow defaults. Contributors MUST check compliance when planning work
and before accepting completed changes. Conflicts MUST be resolved or documented through
an amendment before affected work is accepted.

Changes to these rules require user direction; contributors MUST NOT weaken them merely to
finish a task. Amendments MUST record their reason, affected principles, version change,
amendment date, and any required follow-up. Project maintainers MUST review and approve amendments.
Versions follow semantic versioning: MAJOR for incompatible removal or redefinition of
principles, MINOR for new principles or materially expanded guidance, and PATCH for
clarifications that do not change obligations. The original ratification date MUST be
preserved, and the last amended date MUST reflect the latest adopted change.

**Version**: 2.0.0 | **Ratified**: 2026-11-05 | **Last Amended**: 2026-11-07
