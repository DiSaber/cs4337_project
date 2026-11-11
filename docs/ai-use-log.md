# AI-use log

Record a concise entry for each completed AI-assisted feature or task: date, task,
assistance used, and review or verification performed. Exact conversations and responses
do not need to be included.

## 2026-11-11: D3 baseline audit (T015)

- Task: Check and record the completed `baseline-01` training run.
- Assistance: Claude Code checked checkpoint hashes, loaded `best.pt`, recomputed the
  chosen epoch from `results.csv`, compared the resolved config, scanned the log and
  wrote the experiment record and retrieval notes.
- Verification: All checks above passed (details in `results/experiments.md`). The
  Marc Benamou reviewed and accepted the FR-012 audit.

## 2026-11-11: Colab notebook for the baseline run (T015 setup)

- Task: Give the T015 baseline training a notebook that can be uploaded and run in
  the browser.
- Assistance: Claude Code wrote `notebooks/t015_baseline_colab.ipynb` from the
  T015 steps in `docs/colab-setup.md`: clone, Drive mount, install/sync/prepare, a
  hash check against the D2 profile that stops on a mismatch, a 10-minute run-folder
  copy to Drive, training, and a final copy and check.
- Verification: The notebook parses as valid JSON, and the `run.json` fields it
  prints (`status`, `label`, `head`) match `train.py`. Marc Benamou started it in
  Colab on 2026-11-11; the training result is not yet known.

## 2026-11-11: Windows CPU lock gets tensorboard

- Task: Bring the Windows CPU lock in line with the tensorboard dependency added for
  the Colab smoke run.
- Assistance: Claude Code installed `tensorboard>=2.4.1,<3` into the local `.venv`
  and added the 7 resolved wheels and hashes to `requirements/cpu-lock.txt` and
  `cpu-wheels.json`.
- Verification: Same versions as the CUDA lock; a hash-checked dry-run install of the
  lock and `pip check` passed on Windows/CPython 3.14.7.

## 2026-11-11: D3 smoke training on Colab (T014)

- Task: Run the T014 smoke training on a Colab GPU.
- Assistance: Claude Code drove a Colab T4 session through the Colab CLI: it
  installed the CUDA lock, synced assets, prepared data, and ran three smoke
  attempts. It diagnosed the two failures: tensorboard was missing from the lock,
  and NumPy 2.4 removed `trapz`. It fixed them by adding tensorboard to
  `pyproject.toml` and the CUDA lock, and by adding a one-line launcher shim, with
  upstream left unchanged. It downloaded the runs and stopped the session.
- Verification: The manifest hashes matched D2. `smoke-03` completed, and its
  `run.json`, log, history and `best.pt` head were reviewed (details in
  `results/experiments.md`). The CPU lock was not updated.

## 2026-11-10: D3 training wrapper (T014)

- Task: Implement `train` around the pinned YOLOv5 v7.0 `train.py`.
- Assistance: Claude Code read the pinned upstream source and wrote
  `src/driving_detection/train.py`. It runs `train.py` as a subprocess with an
  argument list, checks verified assets and profile hashes first, refuses
  installed trackers, saves the log/history/checkpoints and FR-012 fields in
  `run.json`, picks the epoch from `results.csv` (upstream erases it from
  `best.pt`) and loads `best.pt` to check its three-class head. It found two
  upstream incompatibilities with the locked torch 2.9/Pillow 12 and worked around
  them without editing upstream (`TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1`, `--noplots`).
  It also generalized the model loader in `assets.py`, mapped budget stops to
  `interrupted`, added a `label` key to both training configs, and documented
  training and the Colab smoke steps.
- Verification: The code compiles and `train --help` works. On the Linux desktop
  (no torch), a real `train` call passed the asset, profile-hash and dataset-path
  checks, then failed at the torch import and was recorded as `failed`; that
  throwaway run was deleted. Training itself was verified the next day on Colab (entry above).

## 2026-11-10: D3 training configs (T013)

- Task: Write `configs/train/baseline.yaml` and `configs/train/smoke.yaml`.
- Assistance: Claude Code wrote them from the pipeline contract and the pinned
  `hyp.scratch-low.yaml`.
- Verification: A YAML comparison showed smoke differs from baseline only in epochs,
  image size and batch, and baseline differs from upstream hyperparameters only in the
  disabled translate/scale/mosaic augmentations. In the pinned source, `patience: 0`
  disables early stopping and a strict `fi > best_fitness` keeps the earliest epoch on
  ties. No training has been run yet; the wrapper (T014) consumes these files.

## 2026-11-10: Cheap asset reuse check

- Task: At user request, stop re-hashing every extracted file each time large data
  is reused.
- Assistance: Claude Code changed `_verified` in `src/driving_detection/assets.py`.
  The first extraction still records the archive SHA-256 and full per-file tree
  hash, and now also the total bytes. Reuse checks expected members, file count
  and total bytes only. Weights and older receipts keep the full check. Updated
  the `data prepare` message and `docs/usage.md`.
- Why: On the Windows PC, hashing was fast (1.74 GB/s) but repeat runs still read
  every file; the user chose one full pass, then size-only reuse checks.
- Limits: A same-size edit to an extracted file is not detected on reuse.

## 2026-11-10: D2 data acquisition and preparation (T009–T012)

- Task: Obtain BDD100K data, implement `data prepare` (conversion, selection,
  integrity checks, YOLO/COCO exports), run it and review the result.
- Assistance: Claude Code searched for the Detection 2020 labels. The official hosts
  are offline and no copy matching the published MD5 exists, so it switched to the
  2018 per-image labels from the author mirror (recorded in `docs/references.md` and
  research R2). It allowed HTTP asset URLs only with a pinned SHA-256. The mirror's
  image archive does not match the published MD5 either: it is a repack with images
  at `100k/<split>/`; a fresh re-download of the first 1.5 GB matched and all 100,000
  member CRCs passed, so its measured SHA-256 is pinned. Claude Code wrote
  `src/driving_detection/data.py` and `configs/data/bdd-subset.yaml`, ran preparation
  on the Linux desktop, and found during review that v1 let 121 recording-session
  name prefixes cross val/test. At the user's direction it added
  `sequence_identity: name_prefix` (one image per session) and produced
  `bdd-subset-v2`, updating research R4, the pipeline contract, tasks and quickstart.
- Verification: Both archives matched their pinned SHA-256. `data prepare` passed its
  built-in checks (exact counts, three classes per partition, zero sequence/content
  overlap, 7,000 decoded images) and a second run reused the identical profile.
  Scratch checks (not committed) confirmed one image per session, zero shared
  prefixes, YOLO/COCO boxes matching the manifest, and overlays of a busy scene, a
  clipped edge box, a negative and the smallest box. Details in `results/experiments.md`.
- Limits: About 30 zero-size source boxes are kept as 1-pixel slivers. Preparation was
  not repeated on Windows. No training has used the data yet.

## 2026-11-10: Constitution 2.1.0 and large-data sync exclusions

- Task: At user direction, limit review stops to commit points, and keep large data
  out of Git and Syncthing before any downloads.
- Assistance: Claude Code amended Principle V, Principle VIII and the workflow
  section (version 2.1.0, with an amendment record). It added archive/video
  patterns to `.gitignore`, a sync note to `docs/usage.md`, and project
  `data/`, `external/`, `artifacts/` and `build/` rules to the College folder's
  Syncthing `.stignore` (outside this repository).
- Verification: Syncthing's local REST API (`/rest/db/ignores`) returned the new
  patterns for the College folder with no parse error. Confirmed no tracked file
  matches the new Git patterns.
- Limits: Files already synced to other devices before this change stay there;
  Syncthing does not delete ignored files remotely.

## 2026-11-10: US1 merge review and Principle VII reconciliation

- Task: Review the spec and US1 implementation for merge to `main`; resolve the
  conflict between constitution v2.0.0 Principle VII (no automated tests) and the
  plan's test modules; record the user's decision on the SC-001 reviewer.
- Assistance: Claude Code reviewed the constitution, spec, plan, tasks and US1
  code. It rewrote the testing parts of `spec.md` (FR-019, US5, SC-005),
  `plan.md`, `tasks.md` (T008/T019 removed; T012/T013/T014/T022/T024 reworded),
  `quickstart.md`, `contracts/pipeline.md` and `research.md` to use normal runs,
  manual review and one short smoke training run. It removed the pytest `dev`
  extra and the `pytest`/`pluggy`/`iniconfig` lock entries, and recorded the
  decisions in `results/experiments.md` and `requirements/README.md`.
- Verification: Reran `assets sync --only model` and `check --device cpu` on the
  local Windows/Python 3.14.7 environment (both exit 0, assets reused); confirmed
  clear exit-1 errors for a full sync without BDD archives and for the
  unimplemented `train` handler. The trimmed CPU lock passed a hash-checked
  `pip install --dry-run`. Compared the BDD100K MD5s and layouts in
  `configs/assets.yaml` with the official download documentation (they match).
  Searched spec artifacts for leftover test references.
- Limits: The trimmed CUDA lock was not reinstalled in Colab. No real BDD archive
  has been synced. The SC-001 check was run by the setup author and accepted by
  the user, not repeated by a second teammate. US1 code was not changed.

## 2026-11-07: Bash setup and constitution merge

- Task: Add Bash support without overwriting project work, retain PowerShell references
  for the team, and fold the supplied senior-year constitution into this project's rules.
- Assistance: Codex initialized Spec Kit 1.0.13 in a temporary copy, reviewed the diff,
  copied the generated Bash scripts and integration changes, and kept both platform
  commands in shared skills and repository guidance. Merged the supplied v1.1.0 rules
  into project constitution v2.0.0 while preserving experiment and course requirements.
- Verification: Initialization preserved the existing constitution and templates;
  reviewed changed files before copying. Bash template resolution and active-feature
  discovery succeeded. Integration status confirmed complete managed files; the nine
  skills are intentional customizations to retain both platform commands. Reviewed the
  merged rules against both source documents and checked the change for whitespace.
- Review: Removed the temporary constitution review comment before staging. Confirmed
  unrelated changes contain only line-ending differences and left them unstaged.
- Limits: PowerShell execution was not checked because pwsh is unavailable. No pipeline
  execution, new tests, commits, or submissions. Reconcile the active feature's plan,
  tasks, and quickstart with Principle VII before implementing automated test/fixture
  instructions, including T008, T012, T019, and T022. Preserve required model evaluation
  and experiment evidence.

## 2026-11-05: Accept supplied Colab setup evidence (T004/T007)

- Task: Review the user's Colab evidence, finalize the CUDA environment records,
  and close the remaining US1 setup acceptance items.
- Assistance: Codex compared first/repeated GPU readiness and asset identities,
  reconciled the freeze file with installed inspection and initial install reports,
  produced a 74-dependency hashed CUDA lock/provenance, preserved a compact evidence
  record and updated setup documentation/task status. Marc Benamou confirmed review
  completion in this session.
- Verification: Confirmed both checks completed on Python 3.13.16/Tesla T4/CUDA
  12.8, matching pinned source/checkpoint hashes and unchanged Colab asset records.
  Every frozen external package has matching installed/report versions. Reused
  two identical official generic-wheel hashes from CPU provenance and fetched the
  recorded Linux MarkupSafe wheel to measure its missing hash. Original evidence
  remains unchanged; raw copies stay ignored and compact records preserve file hashes.
- Limits: GPU execution was performed in the supplied Colab session, not locally.
  Review completion is user-attested; the bundle lacks separate reviewer/console
  result-preservation logs. The finalized lock has not been reinstalled in another
  runtime. No training, data preparation or measured model results are claimed.

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
