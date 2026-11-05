# Feature Specification: Driving Scene Object Detection

**Feature Branch**: No branch created; specification context is independent of branch name.

**Created**: 2026-11-05

**Status**: Draft — validated for planning; no implementation is claimed.

**Input**: `cs4337_project.txt`, supplied at `C:/Users/Marc/Downloads/cs4337_project.txt`, and its three referenced course documents. Include the whole project in one specification, organized into distinct PR deliverables with dependencies and parallel work identified.

## User Scenarios & Testing *(mandatory)*

Users are student contributors preparing experiments and coursework, teammates reproducing results, and course reviewers assessing evidence. The required outcome is an understandable, reproducible driving-scene detection project and complete course handoff. This is an academic experiment; vehicle control and safety deployment are outside scope.

Each story owns one deliverable, the corresponding requirements block, and a proposed implementation PR. Priorities indicate importance; the dependency table defines execution order. Independent tests may use accepted predecessor outputs or documented fixtures without repeating the whole pipeline. Required scope remains required even though the course permits honest submission of incomplete work.

### User Story 1 - Reproduce project setup (Priority: P1)

As a teammate, I can prepare a fresh checkout and obtain documented external assets without depending on another student's machine.

**Why this priority**: Every experiment depends on accessible inputs and repeatable setup.

**Independent Test**: Follow fresh-checkout setup, check asset readiness, then repeat setup without duplicate valid downloads or damage to results.

**Acceptance Scenarios**:

1. **Given** a fresh checkout and documented prerequisites, **When** setup runs, **Then** readiness checks pass or identify the missing prerequisite and recovery action.
2. **Given** valid existing assets, **When** setup repeats, **Then** it reuses them and preserves existing outputs.
3. **Given** interrupted acquisition or missing permission, **When** assets are checked, **Then** incomplete readiness is reported instead of treating unavailable/corrupt inputs as valid.

**Owned requirements**: FR-001–FR-004. **Merge evidence**: fresh/repeat setup records, usage instructions, and AI-use entry.

### User Story 2 - Prepare trustworthy driving-scene data (Priority: P1)

As an experimenter, I can prepare driving-scene data with consistent classes and separate partitions so training and evaluation are meaningful.

**Why this priority**: Annotation errors or related frames crossing partitions invalidate later findings.

**Independent Test**: Prepare a representative sample and inspect mappings, annotations, partitions, and transformations without training a model.

**Acceptance Scenarios**:

1. **Given** images, annotations, and sequence identities, **When** preparation completes, **Then** every retained sample has a documented class mapping and exactly one partition.
2. **Given** related frames or augmented copies, **When** separation is checked, **Then** no source sequence or derived training sample crosses into validation or test data.
3. **Given** invalid boxes, unknown labels, corrupt images, or missing provenance, **When** validation runs, **Then** affected records are rejected/quarantined with reasons before use.
4. **Given** limited compute, **When** a subset is selected, **Then** selection rules, counts, class coverage, and sequence separation are recorded and repeatable.

**Owned requirements**: FR-005–FR-010. **Merge evidence**: manifest, preparation summary, integrity checks, and acquisition/preprocessing instructions.

### User Story 3 - Train a reproducible baseline (Priority: P1)

As an experimenter, I can train an established detector and preserve its configuration and outputs so teammates can explain and repeat the baseline.

**Why this priority**: Comparisons and final findings require a working baseline.

**Independent Test**: Complete a small training run, load its model, and audit its record; reported baseline results additionally require a declared full-budget run.

**Acceptance Scenarios**:

1. **Given** validated data and a declared budget, **When** training completes, **Then** it produces a loadable model and traceable training history.
2. **Given** its record, **When** a teammate repeats the procedure, **Then** all inputs/settings are identifiable and known nondeterminism is disclosed.
3. **Given** candidate checkpoints, **When** the baseline is selected, **Then** selection uses validation evidence, never held-out test results.

**Owned requirements**: FR-011–FR-014. **Merge evidence**: smoke-run verification, baseline record, model location/acquisition instructions, and training documentation.

### User Story 4 - Inspect detections on new scenes (Priority: P1)

As a teammate or reviewer, I can run a saved detector on new driving images and video and inspect labeled predictions beyond training outputs.

**Why this priority**: Inference completes the visible use case and enables demonstrations.

**Independent Test**: Run a compatible model on an image set and short video, including an empty scene, and inspect saved predictions/visual outputs.

**Acceptance Scenarios**:

1. **Given** compatible inputs and a model, **When** inference completes, **Then** outputs contain class, confidence, boxes, and annotated images/video.
2. **Given** no accepted detections, **When** inference completes, **Then** it records a valid empty result without inventing objects.
3. **Given** unreadable inputs or incompatible model/class mapping, **When** inference is attempted, **Then** it identifies the problem and partial outputs rather than silently claiming success.

**Owned requirements**: FR-015–FR-017. **Merge evidence**: image/video examples, empty-result and invalid-input checks, and instructions.

### User Story 5 - Evaluate baseline accuracy and speed (Priority: P1)

As an experimenter, I can measure accuracy/speed under declared conditions and inspect successes/failures so conclusions have evidence.

**Why this priority**: Course findings need defensible measurements rather than attractive examples alone.

**Independent Test**: Check metrics on controlled examples, evaluate baseline validation data, and audit the evidence package. Final testing follows D6 selection.

**Acceptance Scenarios**:

1. **Given** controlled predictions/labels, **When** evaluated, **Then** perfect detections, misses, false detections, and duplicates yield expected outcomes under declared matching rules.
2. **Given** a baseline and evaluation partition, **When** evaluated, **Then** aggregate/per-class measures identify the model, data, thresholds, and definitions.
3. **Given** a speed claim, **When** reported, **Then** hardware, input size, batch size, timed stages, warm-up, and sample count accompany it.
4. **Given** selected examples, **When** reviewed, **Then** both successes/failures appear and measured findings are distinguished from untested conditions.

**Owned requirements**: FR-018–FR-022. **Merge evidence**: metric checks, baseline validation results, timing record, and representative examples.

### User Story 6 - Compare a bounded improvement attempt (Priority: P2)

As an experimenter, I can compare an optimization attempt against the baseline and explain accuracy/speed tradeoffs even if it performs worse.

**Why this priority**: Optimization is requested but follows the working preparation, training, evaluation, and inference pipeline.

**Independent Test**: Compare at least one candidate under a common validation protocol/budget and inspect final selection/testing records without requiring improvement.

**Acceptance Scenarios**:

1. **Given** core acceptance, **When** a candidate is tested, **Then** its hypothesis, changed settings, budget, validation accuracy, and speed conditions are recorded alongside baseline results.
2. **Given** the comparison, **When** final selection occurs, **Then** it uses validation evidence and freezes the configuration before held-out testing.
3. **Given** final testing, **When** findings are discussed, **Then** later holdout-driven tuning is disclosed and not presented as unbiased final evaluation.

**Owned requirements**: FR-023–FR-025. **Merge evidence**: comparison, justified selection, held-out results, and unsuccessful-attempt discussion.

### User Story 7 - Prepare report and submission handoff (Priority: P1)

As a student team, we can assemble a compliant report, understandable code handoff, and submission/access records so reviewers can assess work and contributor roles.

**Why this priority**: Work must be deliverable under the implementation rubric and deadline.

**Independent Test**: Review the package against course instructions, verify intended instructor access, and distinguish repository readiness from actual submission.

**Acceptance Scenarios**:

1. **Given** evidence, **When** students finish the report, **Then** it is a three-page PDF in their own words with required sections, references, roles, links, limitations, and future work.
2. **Given** verified hosting/instructor identity, **When** checked, **Then** report/assignment comments contain required usable links and instructor access is confirmed.
3. **Given** incomplete implementation, **When** reporting, **Then** completed/incomplete scope and future plans are identified with evidence.
4. **Given** an external action awaiting a student, **When** the PR merges, **Then** its checklist item stays pending until completion evidence exists.

**Owned requirements**: FR-026–FR-032. **Merge evidence**: reviewed student-authored report or documented handoff, code documentation, course audit, and explicit pending actions.

### User Story 8 - Present findings and answer audience questions (Priority: P1)

As a student team, we can explain the problem, solution, method, and implications engagingly and complete audience follow-up.

**Why this priority**: Presentation/follow-up are required separately from the report.

**Independent Test**: Time a full recording/rehearsal, review readability/audio, test unlisted playback without login, and audit submission/response status.

**Acceptance Scenarios**:

1. **Given** project evidence, **When** recorded, **Then** the presentation lasts 5–10 minutes inclusive and addresses the problem, solution, how it was solved, and implications.
2. **Given** slides and an unlisted video, **When** checked, **Then** Canvas has the slides and video link in comments and playback works in incognito mode.
3. **Given** peer feedback and the group Response Page, **When** follow-up completes, **Then** the team reviewed responses and answered the Top 10 questions; fewer available questions are recorded and handling confirmed with the instructor.

**Owned requirements**: FR-033–FR-036. **Merge evidence**: reviewed materials, timing/readability/audio checks, and handoff with pending uploads/follow-up.

### User Story 9 - Explore team-captured dashcam footage (Priority: P3, stretch)

As an experimenter, I can optionally investigate captured footage and differences in perspective/settings to discuss generalization.

**Why this priority**: The source allows skipping this goal; it cannot delay required work.

**Independent Test**: After core acceptance, process one team-captured clip and review conditions/predictions; otherwise document the skip.

**Acceptance Scenarios**:

1. **Given** footage and a frozen detector, **When** studied, **Then** viewpoint, known settings, scene conditions, and representative errors accompany results.
2. **Given** unmatched scenes, **When** perspective/settings are discussed, **Then** causal claims are limited by lack of controlled comparisons.
3. **Given** insufficient footage/time, **When** finalizing required work, **Then** the stretch goal is skipped/incomplete without blocking acceptance/submission.

**Owned requirements**: FR-037–FR-039. **Merge evidence**: optional experiment/examples or explicit skip decision in project status.

### Deliverable boundaries and dependencies

Each row is one cohesive merge unit with its owned requirements, verification, usage updates, and AI-use record. Constitution constraints apply to every PR. This specification does not create implementation tasks or additional features.

| Deliverable | Story / requirements | Depends on | Parallel opportunity | Acceptance boundary |
| --- | --- | --- | --- | --- |
| D1 Setup/acquisition | US1 / FR-001–004 | None | Course handoff preparation | Fresh/repeat setup verified |
| D2 Prepared data | US2 / FR-005–010 | D1 | Component design using agreed data contract | Validated partitions/provenance |
| D3 Baseline training | US3 / FR-011–014 | D2 | D4/D5 after contracts fixed | Loadable baseline and run record |
| D4 Image/video inference | US4 / FR-015–017 | D1; D2 class-map/model contract | D3/D5 using a compatible reference model | Demonstrated inference; D3 integration before core acceptance |
| D5 Evaluation/evidence | US5 / FR-018–022 | D2; D3 for measured baseline | D4; metric fixtures may precede D3 | Correct metrics and baseline validation evidence |
| D6 Optimization/final testing | US6 / FR-023–025 | D3, D4, D5 | D7/D8 preparation | Comparison, frozen selection, held-out result |
| D7 Report/submission handoff | US7 / FR-026–032 | D1–D6 evidence for final claims | D8; checklist/access preparation starts immediately | Reviewed report/handoff; pending actions explicit |
| D8 Presentation/follow-up | US8 / FR-033–036 | D1–D6 evidence for final claims | D7; outline/visual design starts earlier | Reviewed materials/handoff; uploads/responses needed for course completion |
| D9 Dashcam study | US9 / FR-037–039 | D3, D4, D5 and core acceptance | D6–D8 if resources permit | Optional evidence/skip; never prerequisite for D1–D8 |

Planning must fix data, class-map, saved-model, prediction, and experiment-record contracts before parallel work relies on them. Fixtures/reference models prove component behavior, not baseline/project completion. Core acceptance means D1–D5 work together using the trained baseline; D6 follows that gate. Final report/presentation claims require evidence. Partial submissions instead describe actual D1–D6 status honestly.

Report/presentation PRs can merge with external actions explicitly pending; course completion stays separately tracked. Later audience feedback can use a focused follow-up PR. Keep each deliverable's tasks together in later planning; split only where a documented dependency or external wait makes it necessary.

### Edge Cases

- Assets/services need permission, credentials, payment, or unavailable access: identify prerequisites and document a reproducible alternative decision; keep secrets outside Git.
- Full-data training exceeds compute/storage/time: declare a repeatable subset, preserve target-class coverage, and limit claims accordingly.
- Filenames hide related frames/augmented copies: use sequence provenance and quarantine uncertainty.
- Excluded classes or no targets: apply documented mapping and preserve valid negative examples.
- Missing class coverage: flag absent examples/undefined metrics rather than implying complete three-class evaluation.
- Interrupted/failed training: preserve status/configuration/history and distinguish smoke, interrupted, and completed runs.
- Empty/duplicate predictions or boundary boxes: apply declared matching rules and flag undefined quantities.
- Corrupt/unsupported video: identify failed inputs and partial outputs without claiming complete processing.
- Worse optimization: preserve negative results and follow the declared selection rule.
- Inaccessible official test labels: reserve a labeled sequence-disjoint holdout before tuning.
- Conflicting course identities/hosting/dates: record and confirm the requirement before submission.
- Missing audience feedback/Response Page: keep follow-up pending instead of claiming completion.

## Requirements *(mandatory)*

### Functional Requirements

#### D1 — Setup and acquisition foundation

- **FR-001**: Document prerequisites, setup, inputs, outputs, and steps so another teammate can check readiness from a fresh checkout.
- **FR-002**: Required datasets, initial weights, and external assets MUST have cited origins, version/identity records, acquisition instructions, and automated acquisition/setup; manual prerequisites MUST be explicit.
- **FR-003**: Setup MUST reuse valid assets, detect incomplete/corrupt assets, and preserve results. Document unavoidable idempotency limitations.
- **FR-004**: Credentials, datasets, checkpoints, captured footage, and large outputs MUST stay outside Git. Small configurations, asset references, summaries, and review evidence MUST remain available.

#### D2 — Prepared dataset

- **FR-005**: Use BDD100K driving scenes as the primary dataset, recording version, accessible labeled portion, usage conditions, and subset selection. Replacement requires an explicit scope update.
- **FR-006**: Required classes MUST be car, pedestrian, and traffic light. Document source-label mappings and treatment of every other class. Optional additional classes MUST NOT block these three.
- **FR-007**: Check readability, annotation/image correspondence, class identifiers, boxes, duplicates, and sequence provenance; produce accepted/rejected/quarantined counts and reasons.
- **FR-008**: Fix and record training, validation, and held-out test partitions before selection. No sequence or derived copy may cross partitions. Reserve accessible labeled holdout data if official test labels are unavailable.
- **FR-009**: Record preprocessing/augmentation settings and versions. Learned preprocessing uses training data only; augmentation applies only to training. Validation/test transformations MUST preserve ground-truth geometry and avoid random training augmentation.
- **FR-010**: A repeatable manifest MUST identify samples, sequences, partitions, class counts, transformations, and subset rules. Integrity checks MUST verify zero overlap and all three classes in each evaluated partition.

#### D3 — Baseline training

- **FR-011**: Train/fine-tune an established detector on prepared training data, producing a loadable baseline and history. Planning MUST declare model/library choices and training budget.
- **FR-012**: Every reported run MUST preserve dataset versions/splits, preprocessing/augmentation settings, model/initial-weight versions, dependency versions, seeds, training settings, commands, output references, status, and known nondeterminism.
- **FR-013**: Model/checkpoint selection and tuning MUST use training/validation only. Label smoke runs separately from experiments used for reported accuracy.
- **FR-014**: Expose training completion/failure status, preserve configuration/history for unsuccessful runs, and document locating/loading a successful model.

#### D4 — Image/video inference

- **FR-015**: Apply a compatible saved detector to new images and prerecorded video, producing per-image/frame classes, confidences, boxes, and annotated outputs.
- **FR-016**: Record model identity, mapping, inputs, processing settings, confidence thresholds, and output locations; support valid empty predictions.
- **FR-017**: Identify missing/corrupt inputs, incompatible models/mappings, and failed/partial video processing with actionable status instead of silent success.

#### D5 — Evaluation and evidence

- **FR-018**: Report aggregate/per-class mAP, precision, recall, sample counts, and absent-coverage/undefined-value handling for the three classes.
- **FR-019**: Report mAP at IoU 0.50 and averaged across IoU 0.50–0.95 in 0.05 steps. Document matching rules, score thresholds, and precision/recall operating point. Controlled examples MUST verify correctness.
- **FR-020**: Results MUST identify model, partition, configuration, and run record. Baseline development uses validation data; reserve test data for final evaluation after frozen selection.
- **FR-021**: Speed claims MUST state hardware, input size, batch size, timed stages, warm-up, sample count, and latency/throughput units. Comparisons use common conditions or disclose differences.
- **FR-022**: Preserve at least one success/failure per class where available, explaining unavailable cases. Discuss lighting, weather, perspective, visibility/size, and training-to-new-scene differences without claiming untested generalization.

#### D6 — Optimization and final evaluation

- **FR-023**: After core acceptance, compare at least one bounded candidate with baseline on validation data, recording hypothesis, changes, budget, accuracy, and speed evidence.
- **FR-024**: Use a documented validation-based accuracy/speed selection rule and freeze the final configuration before held-out testing. Preserve worse/failed attempts; improvement is not a completion condition.
- **FR-025**: Preserve final configuration/held-out results. Disclose subsequent exploratory holdout use and never represent further holdout-driven tuning/testing as unbiased final evaluation.

#### D7 — Report and submission handoff

- **FR-026**: Deliver a three-page PDF with overview, introduction, methodology/setup, results, and conclusion; include actual algorithm/tools, supported findings, limitations, incomplete work, and future improvements. Apply three pages to the entire PDF as a conservative interpretation of both limits.
- **FR-027**: List contributors and individual roles on the front page. Cite reused code/models/data/references and include repository/applicable private notebook links.
- **FR-028**: Students MUST write report prose in their own words and understand/explain submitted code. The supplied policy permits AI for code generation/debugging, concept clarification, and grammar/tonality; direct copying of generated report content is prohibited. Completed AI-assisted tasks MUST have concise task/assistance/review entries in `docs/ai-use-log.md`.
- **FR-029**: Provide understandable, commented, version-controlled source and README/notebook instructions covering setup, inputs, outputs, and steps. Track the rubric's at-least-60% expectation honestly against a declared required-scope inventory; unfinished work MUST NOT be labeled complete.
- **FR-030**: A separate course deliverables checklist MUST track report, presentation, roles, references, code/notebook links, access, deadlines, designated report submitter, submission evidence, and audience follow-up. Distinguish repository readiness, actual submission, and unresolved course questions.
- **FR-031**: One team member MUST upload the PDF to Canvas by displayed December 2, 2026, 11:59 p.m., verifying current deadline/timezone. Put required repository/notebook links in report/comments as applicable and confirm instructor access before marking complete.
- **FR-032**: Record/resolve hosting/account conflicts with the instructor before affected handoff actions. Permission changes, messages, uploads, and submissions remain student actions unless separately authorized; this spec defines outcomes without executing them.

#### D8 — Presentation and audience follow-up

- **FR-033**: Record a 5–10 minute presentation addressing problem, solution, how it was solved, and implications with clear narrative and evidence.
- **FR-034**: Slides/video MUST be readable and speech audible/accurate. Full rehearsal/recording review MUST record timing, clarity, engagement, organization, visuals, and subject knowledge. Prefer useful visuals over dense text; creativity/light humor is encouraged where appropriate.
- **FR-035**: Upload slides to the Canvas presentation assignment, upload a high-quality Unlisted YouTube recording, put its link in comments, and record incognito playback success. Verify the presentation deadline in Canvas; the supplied rubric does not provide it.
- **FR-036**: Review classmates' responses and answer the Top 10 questions on the assigned group Response Page. Missing feedback/page access or fewer questions MUST remain pending instructor clarification instead of fabricated responses or silent completion.

#### D9 — Optional captured dashcam study

- **FR-037**: After core acceptance, the team MAY test captured footage, recording identity, viewpoint/mounting, known settings, resolution/frame rate, lighting/weather, and differences from training scenes. Label unknown settings unknown.
- **FR-038**: Distinguish qualitative observations from accuracy measurements. Accuracy claims require ground truth and declared evaluation; causal perspective/settings claims require controlled comparison or an explicit observational limitation.
- **FR-039**: Dashcam work MUST remain optional, excluded from required completion calculations/dependencies, and marked completed/incomplete/skipped. It MUST NOT block core work, report, or presentation.

### Key Entities *(include if feature involves data)*

- **External asset**: Origin, version, access conditions, location, and readiness of data/weights/other inputs.
- **Prepared dataset/sample**: Images, annotations, mapping, sequence, transformations, partition, integrity findings, and subset membership.
- **Experiment record**: Run identity, configuration, versions, seed, budget, commands, history, status, output references, and nondeterminism.
- **Model artifact**: Detector linked to experiment, mapping, initial weights, and selection evidence.
- **Prediction set**: Image/frame detections linked to model/configuration, with scores/boxes, empty/partial status, and visual references.
- **Evaluation/comparison**: Model/data identities, metric definitions/values, timing conditions, examples, hypothesis, and decision.
- **Course deliverable**: Owner, roles, source instruction, deadline, material/link, review/access status, evidence, and pending actions.
- **Capture record**: Optional footage and known camera/scene conditions linked to predictions and any labeled evaluation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A teammate other than the setup author completes fresh-checkout readiness and repeats setup without duplicate valid downloads or loss of outputs. Covers D1.
- **SC-002**: Every retained sample has partition/sequence provenance; checks find zero sequence/derived-copy overlap and all three classes in each evaluated partition. Covers D2.
- **SC-003**: At least one completed baseline produces a loadable detector; 100% of reported runs contain FR-012 fields. A teammate can repeat the procedure with nondeterminism explained. Covers D3.
- **SC-004**: A reviewer can inspect predictions/annotations for at least one new image set and one short video, including a no-detection example; invalid-input behavior is demonstrated. Covers D4.
- **SC-005**: Baseline validation and final held-out records each contain both mAP measures, precision, recall, coverage, experiment identity, and speed conditions; controlled metric cases produce reviewed expected results. Covers D5/D6.
- **SC-006**: At least one candidate is compared under a common validation protocol/budget, with justified selection and success/failure examples per class or missing-case explanations. Covers D5/D6.
- **SC-007**: One three-page student-authored PDF and code handoff are audited against all applicable course requirements with contributors/roles/sources identified. Submission/access items have evidence or remain pending; pending items mean course completion is not achieved. Covers D7.
- **SC-008**: One 5–10 minute recording passes readability/audio/incognito review and has slides/video-link submission evidence. Top 10 responses are recorded; unavailable feedback stays explicitly pending and prevents course-completion claims. Covers D8.
- **SC-009**: Every required deliverable has one requirement owner, dependencies, acceptance evidence, and status; completed AI-assisted tasks have reviewed log entries. No required dependency includes D9. Covers D1–D9.
- **SC-010**: If attempted, at least one captured clip has a capture record, predictions, and evidence-limited conclusions; otherwise D9 is explicitly skipped/incomplete without delaying required work.

No unsupported accuracy or real-time-speed target is invented. Completion means working, measured, explainable outcomes and honest comparisons, even when accuracy is limited or optimization fails.

## Assumptions

- This is Type I implementation, not Type II survey. Survey-only ACM template, six-page minimum, and five-paper/method comparison requirements do not apply.
- BDD100K and the three named classes define initial scope. A repeatable subset is acceptable with coverage/limitations disclosed. Planning must declare sample counts, split policy, and budget before experiments; these were not supplied.
- The brief suggests Python, YOLOv5 with PyTorch, OpenCV, and Roboflow preprocessing/augmentation. These are preferred planning starting points, not verified compatibility or mandatory implementation choices; substitutions must preserve outcomes and document rationale. The rubric suggests an established open-source model from Hugging Face without requiring that provider.
- Metric definitions and image/video inference clarify requested outcomes. Live streaming, tracking, traffic-light state recognition, service deployment, new architectures, and safety certification are outside required scope.
- New scenes differ from training samples; unlabeled demonstrations cannot establish accuracy.
- Dataset usage/access, compute/storage, and preprocessing-service availability are planning dependencies, not completed setup.
- These are logical PR boundaries within one feature. Later planning can size tasks but must preserve ownership and acceptance boundaries.
- Checklist/access preparation and presentation outlines can start early; final claims need results. Dashcam work cannot consume resources needed for submissions.

### Source coverage and course interpretations

The following local documents were read on November 5, 2026. Requirements are summarized here so the spec works without Downloads paths. Saved HTML includes unrelated account/navigation content and is not copied into the repository.

| Source | Retained requirements / interpretation |
| --- | --- |
| `cs4337_project.txt` — SHA-256 `CEB2CBDCEBBE9DD9C003205C9DFA1F0356227DFF284413FD1D771C0E9B4FC4E9` | Driving detection/classification, BDD100K, suggested tools, preprocessing/augmentation, implementation/training/new-scene testing/optimization, optional captured dashcam perspective/settings study, AI log, three referenced documents. |
| `Rubrics - Project & Report_ CS.4337_ Introduction to Computer Vision.htm` | Reuse/reproduction allowed; novelty not required. Report/setup/results, organized commented documented code, version-controlled submission/access, at least 60% completion evidence/future work, presentation, citations, AI policy. Type I weights: report 5% (clarity 2%, setup 2%, results 1%), code 5% (organization 3%, submission 2%), completion 5%, presentation 10%. |
| `Submit-ProjectReport.htm` | PDF only, maximum three pages, contributor names/roles on front page, references/repository/private Colab links, limitations/future plans, one team upload, December 2, 2026, 11:59 p.m. displayed deadline/availability cutoff. |
| `Rubrics - Presentation_ CS.4337_ Introduction to Computer Vision.htm` | 5–10 minutes (outside range not accepted), engaging visual narrative, four implementation questions, readable slides/video and audible speech, Canvas slides, Unlisted YouTube, incognito test, comments link, peer review and Top 10 responses. Four 1–5 categories: content/organization, delivery/engagement, visual aids/materials, knowledge/depth. |

**Report-length conflict resolved**: The rubric asks for 3–5 pages; the assignment allows at most three. Exactly three satisfies both and the constitution's interpretation; no governance change is needed.

**Access/hosting conflict awaiting instructor verification**: The rubric specifies `git.txstate.edu` or Google Colab and collaborator identifiers `k-b459` / `k_b459`. The assignment references GitHub account `keshavsbhandari`. Both give private Colab sharing with `keshav.s.bhandari@gmail.com`. Preserve source-specific identifiers in the course checklist and confirm platform/account before granting access. This submission dependency does not block core planning.

**Deadline interpretation**: The report date/time is from the saved assignment; its timezone is not established. Presentation/audience-response dates are absent. Verify current dates/timezone in Canvas rather than assume the report deadline applies to all work.

**Completion interpretation**: Aim for D1–D8. Permission to submit incomplete projects is a fallback reporting policy, not silent scope removal. Planning must establish a completion inventory before implementation; any percentage must identify numerator, denominator, and evidence. Exclude optional D9.
