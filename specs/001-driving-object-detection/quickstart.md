# Quickstart and Validation Guide

**Status**: Design guide for the future implementation. Commands/config files below are the agreed interface and will become runnable in D1–D6; the package does not exist yet. Planning has not downloaded data, installed dependencies, trained a model, or verified measured performance. See [CLI contract](contracts/cli.md), [record contract](contracts/records.md), and [pipeline semantics](contracts/pipeline.md).

Run from the repository root. Commands are PowerShell-compatible; use `.venv/bin/activate` on Linux instead of the Windows activation line. Choose new run IDs for repeated experiments.

## 1. Prerequisites and environment — D1

- Python 3.11 with venv, supported Windows/Linux x86-64, adequate disk for original archives plus extraction/prepared data and checkpoints. Check disk before downloading; do not assume the archive size equals required working space.
- Authorized BDD100K 100K images and Detection 2020 label access, with source terms reviewed; either working official URLs or existing archives. Dataset access is a manual prerequisite if the provider requires it.
- For reported training, a compatible single NVIDIA GPU, ideally >=8 GB VRAM. The user selected GPU/Colab; CPU is for fixtures/readiness. Record hardware/driver and actual VRAM. CUDA 12.1 is the initial torch profile, not an assumption about every NVIDIA device.
- On Colab, use an isolated supported Python environment and the same checked-out project/config/lock; do not silently rely on whatever package versions the notebook currently has. Copy small run records and large artifact pointers to team storage before an ephemeral session ends.

After D1 has produced and tested the profile locks:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements/cpu-lock.txt
python -m pip install --no-deps -e .
python -m driving_detection --help
python -m driving_detection assets sync --config configs/assets.yaml --only model
python -m driving_detection check --config configs/assets.yaml --device cpu
python -m driving_detection fixtures create --output data/smoke
python -m pytest tests/unit tests/contract
```

Expected: model source/official initial weights verified with identities, imports/checkpoint/CPU readiness succeed, synthetic fixture recipe emits tiny data/video, focused checks pass. Dataset readiness is reported separately and does not make model-only readiness fail. Full locks include platform-specific wheel provenance; D1 must supply a matching lock for each supported execution platform rather than reuse an incompatible wheel file.

For the Linux GPU environment, create an isolated venv with Python 3.11, install `requirements/cuda-lock.txt` and the package, then run:

```powershell
python -m driving_detection check --config configs/assets.yaml --device cuda:0
```

Expected: requested GPU is available and compatible; no silent CPU fallback. D1's tiny train/load/infer/evaluator compatibility probe must pass before the environment lock is accepted. A new device-specific matched torch/vision lock must pass the same checks before use if cu121 is unsupported.

## 2. Small CPU end-to-end smoke — D2 through D5

```powershell
python -m driving_detection data prepare --config configs/data/smoke.yaml
python -m driving_detection data validate --profile data/prepared/smoke-v1/profile.json
python -m driving_detection train --profile data/prepared/smoke-v1/profile.json --config configs/train/smoke.yaml --run-id smoke-train-01
python -m driving_detection infer --model artifacts/runs/smoke-train-01/model.json --input data/smoke/demo.mp4 --config configs/evaluation/default.yaml --device cpu --run-id smoke-video-01
python -m driving_detection evaluate --model artifacts/runs/smoke-train-01/model.json --profile data/prepared/smoke-v1/profile.json --partition val --config configs/evaluation/default.yaml --device cpu --run-id smoke-eval-01
python -m pytest tests/integration -m smoke
```

Expected: fixed 24/12/12 synthetic partitions, all three classes, zero overlap, one CPU training epoch at 320/batch 2, loadable model, readable annotated video and complete prediction records, finite supported metrics or explicit null reasons. Synthetic scores are not driving-scene accuracy. Do not force a smoke model to detect every object; metric correctness uses controlled predictions independently of training quality.

Re-run data preparation with identical inputs and verify reuse/hash stability. Interrupt a small acquisition fixture and retry, preserving already valid assets. Invalid class/box/sequence/duplicate fixtures must fail integrity checks. Wrong model mapping must fail before inference. Corrupt video must return partial/failure status; a valid no-detection image must return completed with []. Tests generate these controlled inputs; they do not require damaging actual dataset files.

## 3. Acquire, prepare, and freeze actual data — D1/D2

Configure local authorized dataset URLs if needed, without putting secrets into Git, then:

```powershell
python -m driving_detection assets sync --config configs/assets.yaml
python -m driving_detection data prepare --config configs/data/bdd-subset.yaml
python -m driving_detection data validate --profile data/prepared/bdd-subset-v1/profile.json
```

If provider download is unavailable, import existing authorized archives instead; replace these example paths with actual archive locations:

```powershell
python -m driving_detection assets sync --config configs/assets.yaml --images-archive "C:/Datasets/bdd100k_images_100k.zip" --labels-archive "C:/Datasets/bdd100k_det_20_labels.zip"
```

Expected: checksums/extracted members pass; the profile records Detection 2020, eligibility/exclusion counts, 5,000/1,000/1,000 selected sequences/images, three-class coverage in each partition, zero sequence/content overlap, negative-image counts, coordinate-conversion version, and immutable manifest hashes. Compare hash-stable repeat preparation. Official host failure, incorrect label release, insufficient eligible samples or absent class coverage must stop readiness with a reason, not silently change data.

Audit a representative box overlay, including a source one-pixel/edge fixture and YOLO/COCO roundtrip. Confirm ignored-region samples are excluded and occluded/truncated ordinary targets remain. Model training must not begin until real profile integrity is accepted/frozen.

## 4. Train and demonstrate the baseline — D3/D4

```powershell
python -m driving_detection train --profile data/prepared/bdd-subset-v1/profile.json --config configs/train/baseline.yaml --run-id baseline-01
python -m driving_detection infer --model artifacts/runs/baseline-01/model.json --input data/new-scenes/images --config configs/evaluation/default.yaml --run-id baseline-images-01
python -m driving_detection infer --model artifacts/runs/baseline-01/model.json --input data/new-scenes/demo.mp4 --config configs/evaluation/default.yaml --run-id baseline-video-01
```

Supply an actual new driving image set/video not in training at the displayed input paths and record provenance. These ordinary new-scene demonstrations do not require team-captured footage; capture is D9 only. Inspect both original and annotated outputs.

Expected: completed 20-epoch baseline at size 640/batch 8 within declared budget, or explicit interrupted/failed status. Batch fallback is resolved before the reported run and retained in configuration. Training sees train/val only, selects checkpoint by documented validation fitness, records all FR-012 fields, and produces verified model metadata/hash. Interrupted or smoke runs cannot satisfy baseline completion.

Inference must produce complete image/frame records, class/confidence/boxes, valid empty cases, and readable saved media. Confirm trained head uses the three canonical IDs. Component development can use a labeled reference COCO model earlier, but it does not satisfy this actual baseline demonstration.

## 5. Measure and accept core — D5

```powershell
python -m driving_detection evaluate --model artifacts/runs/baseline-01/model.json --profile data/prepared/bdd-subset-v1/profile.json --partition val --config configs/evaluation/default.yaml --run-id baseline-val-01
python -m driving_detection benchmark --model artifacts/runs/baseline-01/model.json --profile data/prepared/bdd-subset-v1/profile.json --config configs/evaluation/default.yaml --run-id baseline-time-01
python -m driving_detection core-check --model artifacts/runs/baseline-01/model.json --profile data/prepared/bdd-subset-v1/profile.json --inference artifacts/runs/baseline-video-01/prediction-set.json --inference artifacts/runs/baseline-images-01/prediction-set.json --evaluation artifacts/runs/baseline-val-01/evaluation.json --timing artifacts/runs/baseline-time-01/timing.json --run-id core-01
```

`--inference` is repeatable and the core gate requires both image and video evidence. Expected: AP50/AP50:95 and micro/per-class fixed-threshold P/R with counts and definitions; all 1,000 validation samples included; fixed timing subset/warm-up/stages/hardware; original and annotated class success/failure examples or documented absence. Core-check verifies all actual-data/model identities and the required evidence, producing `artifacts/runs/core-01/core-gate.json`. Synthetic/reference-only evidence is refused for reportable core acceptance.

Review controlled metric cases from [pipeline.md](contracts/pipeline.md), especially duplicate counts, negative images, absent classes, no predictions, wrong class and IoU boundary. A duplicate after full recall need not reduce interpolated AP; fixed P/R must still count its FP. Test reads are not allowed through ordinary evaluate at this point.

## 6. Compare, freeze, then test — D6

```powershell
python -m driving_detection compare --model artifacts/runs/baseline-01/model.json --profile data/prepared/bdd-subset-v1/profile.json --core-gate artifacts/runs/core-01/core-gate.json --config configs/experiments/input-size.yaml --run-id compare-01
python -m driving_detection select --comparison artifacts/runs/compare-01/comparison.json --run-id selection-01
python -m driving_detection final-evaluate --selection artifacts/runs/selection-01/selection.json --run-id final-01
```

Expected: a completed validation comparison at sizes 640/960 using the same model/membership/device/precision; select 960 only with AP gain >=0.005 and compute-latency ratio <=1.5, otherwise retain 640. Failure/negative findings remain visible. Selection freezes model/data/config/environment hashes before any held-out prediction. Final evaluation uses only the selected configuration on the 1,000 project-held-out images; it identifies results as project-subset performance.

Negative checks: test before selection, mismatched selection/config/model/profile hashes, partial predictions, or comparison using test evidence returns guard failure. Exposure is logged before processing even if final evaluation fails. Exact replay is a labeled reproduction; tuning after test exposure cannot be presented as unbiased final testing.

## 7. Course handoff — D7/D8

Review `docs/course-deliverables.md` once D7 creates it. Verify FR-001–036 ownership/status/evidence and an honest satisfied-count/36, excluding optional D9. Preserve large artifacts in team-accessible storage and test retrieval from the tracked references. Students write the report themselves; no generated report prose is a submission artifact.

Check three-page PDF and required sections, front-page names/roles, citations, findings/limits/future work, repository/private notebook links and current instructor access, one report submitter, and current Canvas report deadline/timezone. Resolve the source account/platform discrepancy before sharing. Record actual report upload and comments separately; the saved deadline is December 2, 2026, 11:59 p.m., not a verified current timezone.

Time and review a complete 5–10 minute presentation covering all four required questions. Verify readable visuals/audible speech, slides in the presentation assignment, Unlisted YouTube playback in incognito, and link in assignment comments. Verify its own deadline. Later review classmate feedback and answer the Top 10 questions on the group Response Page; missing feedback/page/fewer questions stays pending instructor clarification. Code/material PRs can merge with pending human actions explicitly documented, but course completion cannot be claimed.

## 8. Optional captured clip — D9

Only after core acceptance and if resources permit:

```powershell
python -m driving_detection capture register --input data/captured/clip.mp4 --config configs/capture/local.yaml --run-id capture-01
python -m driving_detection infer --model artifacts/runs/baseline-01/model.json --input data/captured/clip.mp4 --capture artifacts/runs/capture-01/capture.json --config artifacts/runs/selection-01/inference-config.yaml --run-id dashcam-01
```

D9 creates the local capture config from known/unknown settings. Use the selected inference config when a selection exists; otherwise the frozen baseline config. Expected: capture conditions, predictions, observational limitations and no unlabeled accuracy/causal claims. If labels exist, define an independent labeled capture evaluation profile and apply the same metric contract; do not mingle it with the original heldout. No clip/time means explicitly skipped/incomplete and does not block D1–D8.
