# AI-use log

Record a concise entry for each completed AI-assisted feature or task: date, task,
assistance used, and review or verification performed. Exact conversations and responses
do not need to be included.

## 2026-11-05: US1 asset setup and CPU verification (T005–T006; partial T004/T007)

- Tasks: Define external asset sources/checksums/terms (T005); implement verified
  acquisition and model readiness (T006). Resolve the local CPU portion of T004
  and perform the author-run portion of T007; those tasks remain unchecked until
  actual Colab GPU evidence and independent teammate review exist.
- Assistance: Codex consulted official BDD/YOLO/PyTorch/Pillow documentation,
  implemented staged ZIP/file acquisition, receipts/inventory, integrity/reuse and
  clear recovery errors; added scoped checkpoint/Pillow compatibility adapters.
  Installed an isolated CPU environment, recorded 57 exact dependencies with wheel
  hashes/provenance, and wrote setup/reference/evidence docs and a Colab handoff.
- Verification: All 16 requirements checklist items passed. Official source and
  weights downloaded and hashed, imports/CPU allocation/NMS/checkpoint head loading
  passed, repeated sync reused valid model assets, dependency check passed and
  repeat hashed-lock dry run proposed no installs. Small operational cases checked
  local import/reuse, checksum/member failures, changed extractions, traversal,
  links/collisions, interrupted response/retry and failure inventory. A font-sizing
  check passed. Git ignores bulk assets and environments; upstream source unchanged.
- Corrections: Fixed Windows staging ACL inheritance, a temporary torch adapter's
  interaction with upstream wildcard imports, and ZIP original-header validation
  exposed by Windows filename normalization. Evidence scripts/build outputs remain
  ignored; no extra permanent test framework or training run was added.
- Limitations: No BDD archives, Linux GPU runtime, independent teammate verification,
  training or accuracy/speed evidence. Requested CUDA correctly failed locally.
  The user will run Colab commands and return evidence; instructions alone do not
  complete T004/T007 or US1. No course report prose, uploads or external messages.

## 2026-11-05: Phase 2 CLI and shared file helpers (T003)

- Task: Implement the six-command argparse interface and small shared file helpers
  on the existing `001-driving-object-detection-us1` branch.
- Assistance: Codex implemented lazy component dispatch, YAML/config persistence,
  byte SHA-256, safe new-run directories, explicit device resolution and terminal
  run statuses. Updated README, CLI implementation status and current usage docs.
- Verification: All 16 requirements checklist items passed. Operational probes
  with temporary handlers checked paths with spaces, YAML mapping/errors, exact
  config hashes, run reuse/traversal/reserved-name rejection, preserved handler
  fields, completed/failed/interrupted statuses and unavailable-CUDA/missing-config
  failures on Python 3.14.7. Standard-library-only subprocesses verified every help
  level, accepted/invalid arguments and missing-handler errors on 3.14.7 and 3.10.4.
  Built a wheel and installed it without dependencies in an isolated local venv;
  console and module help worked. Git whitespace checks passed and confirmed the
  US1 branch. Python ignore rules remain adequate; no extension hooks exist.
- Limitations: Python 3.10.4 lacks PyYAML, so its config/run probes were not completed;
  an initial operational probe stopped there. Model/device behavior used a fake
  unavailable CUDA module, not real GPU validation. No model dependencies/assets,
  training or predictions were installed/run. Component handlers and real environment
  readiness remain later tasks. Operational probe files/builds stay under ignored
  `artifacts/`; no extra permanent test suite was added.

## 2026-11-05: Allow Colab and local Python versions

- Task: Allow user-reported Colab Python 3.13 and the installed local interpreters.
- Assistance: Codex changed package metadata to Python >=3.10,<3.15 and bounded
  dependency ranges, updated README/plan/tasks/quickstart, and recorded the runtime
  revision and primary compatibility sources in research. D1 must resolve exact
  environment locks and handle modern torch/Pillow integration with pinned YOLO.
- Verification: Observed local Python 3.14.7 and launcher Python 3.10.4. Built the
  package wheel with Python 3.14.7 without installing dependencies; checked metadata
  accepts 3.10–3.14 and excludes 3.9/3.15, parsed dependency requirements, and imported
  the package on both installed interpreters. No extension hooks are configured.
- Limitations: Colab 3.13 was reported by the user, not inspected remotely. Full
  dependency resolution, checkpoint loading and pipeline smoke remain D1/later
  integration work. Package build/import checks do not establish model compatibility.

## 2026-11-05: Phase 1 package and ignore rules (T001–T002)

- Task: Initialize the Python 3.11 package metadata (T001) and protect local
  assets, outputs, credentials and caches from Git (T002).
- Assistance: Codex added setuptools metadata, the planned dependency pins and
  CLI entry point, a package initializer, root ignore rules and README status/path
  guidance on branch `001-driving-object-detection-phase-1`.
- Verification: Parsed metadata with Python's TOML reader, imported the package,
  and checked setuptools package discovery. Used Git to verify ignored asset,
  environment, credential/cache and `.specify/feature.json` paths; confirmed
  configs, results, example environment and package files remain trackable.
  Git whitespace checks passed. The requirements checklist passed all 16 items;
  no extension hook configuration exists.
- Limitations: Available interpreters were Python 3.14.7 and 3.10, not the target
  Python 3.11. No dependency installation or runtime compatibility claim was made;
  tested environment locks remain T004. CLI dispatch is T003, so the declared
  entry point is not runnable yet. No training or model/data downloads occurred.

## 2026-11-05: Default agent instructions

- Task: Add repository instructions directing coding agents to the constitution, feature
  artifacts, and Spec Kit skills.
- Assistance: Codex inspected the constitution, installed skills, and feature-resolution
  script, then wrote shared guidance and entry points for Claude Code and GitHub Copilot.
- Verification: Checked the new Markdown files' local links, referenced skill paths, and
  feature-discovery command flags against the installed repository files. No application
  code changed.

## 2026-11-05: Driving-scene project specification

- Task: Specify `cs4337_project.txt` and referenced coursework as cohesive PR deliverables
  with dependencies and parallel work opportunities.
- Assistance: Codex read the brief, three saved course pages, constitution, and resolved
  Spec Kit template; drafted nine deliverables, acceptance scenarios, requirements,
  measurable outcomes, source interpretations, and a quality checklist.
- Verification: Reviewed source coverage, constitution compliance, requirement ownership,
  dependency order, core/stretch separation, and submission conflicts; checked requirement
  identifiers, local links, template sections, and active feature resolution. No model
  training, application tests, access changes, or external submissions occurred. Students
  must review the specification and write report prose in their own words.
- Limitation: Git status/diff checks were blocked by Git's repository-ownership check;
  direct document checks verified whitespace, conflict markers, and feature-pointer content.

## 2026-11-05: Implementation planning and design contracts

- Task: Plan the nine project deliverables for single-NVIDIA-GPU/Colab training with CPU
  smoke validation, preserving cohesive PR ownership and parallel development boundaries.
- Assistance: Codex used the Spec Kit plan workflow and two research agents to consult
  primary dataset/model/evaluator documentation; drafted the plan, research decisions,
  data model, CLI/file/pipeline contracts, and future quickstart validation guide.
- Verification: Reviewed all constitutional gates, requirement ownership/dependencies,
  class/coordinate conversion, dataset separation, evaluation/timing semantics, final-test
  guards, and course handoffs. Checked document links, required sections, identifiers,
  example JSON, quickstart command coverage, and active feature resolution. Dependency
  pins remain implementation targets requiring D1 compatibility checks; no installs,
  training, benchmarks, course submissions, or application tests were performed.

## 2026-11-05: Post-plan specification clarification review

- Task: Review the active specification for material ambiguities before task generation.
- Assistance: Codex applied the Spec Kit clarification taxonomy to the specification,
  constitution, existing plan, data model, and CLI contract. No questions were needed;
  existing scope/acceptance rules and planned technical decisions provide sufficient
  coverage. Instructor account/deadline verification remains an explicit course prerequisite.
- Verification: Re-evaluated all 16 specification-quality criteria with no state changes;
  checked requirement ownership, acceptance coverage, placeholders, and document links.
  Specification and checklist content remain unchanged. No application tests were run.

## 2026-11-05: Scope and review-cost assessment

- Task: Identify unnecessary planned components and tests before implementation.
- Assistance: Codex reviewed the plan and contracts against required outcomes and the
  constitution's simplicity principle; identified removable backend abstractions, generic
  record validation/lifecycle infrastructure, workflow commands, exposure tracking,
  detailed profiling, and duplicate test layers.
- Verification: Confirmed recommendations preserve data separation, reproducibility,
  focused data/metric correctness checks, baseline/inference/evaluation evidence, and
  course deliverables. This was a design review; no implementation tests were needed.

## 2026-11-05: Simplify implementation scope after review

- Task: Apply the approved reductions to the implementation design before task generation.
- Assistance: Codex revised the plan, research, data model, three contracts and quickstart
  to use direct wrappers, six command handlers, compact metadata, documented human
  comparison/selection, one inference timer and focused data/metric tests with one opt-in
  CPU smoke check. Removed requirements for backend/schema frameworks, orchestrators,
  custom lifecycle/exposure/resume systems, public fixture generation and duplicate suites.
- Verification: Checked consistency across the seven artifacts, command examples, links,
  requirement ownership, preserved evaluation/data safeguards and constitution compliance.
  All nine deliverables and 39 functional requirements remain. No implementation, dependency
  installation, application tests, training or course submissions occurred.

## 2026-11-05: Dependency-ordered implementation tasks

- Task: Generate tasks from the approved simplified design, grouped into complete PR
  deliverables with explicit dependencies and limited verification scope.
- Assistance: Codex used the Spec Kit task setup/template and feature artifacts to draft
  38 tasks across nine stories, shared setup/foundation and a final handoff audit; retained
  only focused data/metric tests and one opt-in CPU smoke, with student actions explicit.
- Verification: Checked task format/IDs/story labels/paths, all 39 requirement owners,
  dependencies, parallel examples, acceptance checkpoints and removed-scope exclusions.
  Generated tasks remain unchecked; no implementation, application tests, installations,
  model runs, messages, permission changes or course submissions were performed.
