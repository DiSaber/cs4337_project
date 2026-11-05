<!--
Sync Impact Report (temporary review material; remove before committing)
Version change: unratified scaffold -> 1.0.0 (initial adoption)
Modified principles: placeholder principles replaced with I-VI below.
Added sections: six concrete Core Principles, Project Constraints,
Development Workflow and Quality Gates, and concrete Governance rules.
Removed sections: template examples and placeholder guidance only.
Follow-up TODOs: none.
-->
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

The project MUST prefer established models and libraries unless additional complexity has
a documented experimental purpose. Setup, inputs, outputs, and execution steps MUST be
documented, and team members MUST understand and be able to explain submitted code.
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

## Project Constraints

The project focuses on detecting and classifying objects in driving scenes. Specific model
versions, target classes, datasets, preprocessing services, training budgets, and dashcam
experiments MUST be defined in specs and plans rather than fixed by this constitution.

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

Changes affecting data preparation, splitting, annotations, or metrics MUST include focused
checks for data integrity and evaluation correctness. Routine changes MUST use verification
appropriate to their impact; full model training is required only when needed to validate
the change or support a reported result. Reported experiments MUST retain the records
required by Principles I, II, and IV.

## Governance

This constitution governs project specs, plans, tasks, implementation, and review, subject
to applicable course requirements. Contributors MUST check compliance when planning work
and before accepting completed changes. Conflicts MUST be resolved or documented through
an amendment before affected work is accepted.

Amendments MUST record their reason, affected principles, version change, amendment date,
and any required follow-up. Project maintainers MUST review and approve amendments.
Versions follow semantic versioning: MAJOR for incompatible removal or redefinition of
principles, MINOR for new principles or materially expanded guidance, and PATCH for
clarifications that do not change obligations. The original ratification date MUST be
preserved, and the last amended date MUST reflect the latest adopted change.

**Version**: 1.0.0 | **Ratified**: 2026-11-05 | **Last Amended**: 2026-11-05
