# Quickstart and Validation Guide

**Status**: Future implementation guide. These commands are agreed interfaces, not evidence of installed code or completed experiments. See [CLI](contracts/cli.md), [files](contracts/records.md), and [pipeline rules](contracts/pipeline.md).

Run from the repository root. Use the tested CPU environment locally and the tested GPU environment on Linux/Colab. Record actual versions/hardware; dependency targets in the plan still require implementation-time verification.

## 1. Setup — D1

Prerequisites: Python 3.11, sufficient archive/extraction/output disk space, authorized BDD100K image/Detection 2020 label access, and a compatible NVIDIA GPU for reported training. Official download access may require manual terms/access steps; existing authorized archives are supported.

After D1 supplies tested environment files:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements/cpu-lock.txt
python -m pip install --no-deps -e .
python -m driving_detection assets sync --config configs/assets.yaml --only model
python -m driving_detection check --config configs/assets.yaml --device cpu
```

Expected: pinned source/official weights and hashes, successful imports/checkpoint load, readable device/readiness report. Dataset readiness is separate from model-only readiness. Repeat setup to verify valid assets are reused and earlier outputs preserved; check an interrupted/invalid small download fixture recovers or fails clearly.

On Linux/Colab use Python 3.11 with an isolated environment, source its bin/activate, install requirements/cuda-lock.txt and the project, then run check with --device cuda:0. Confirm the actual GPU/driver works; never silently fall back to CPU. Preserve outputs outside ephemeral notebook storage. No training probe is duplicated in setup.

## 2. Prepare real data — D2

```powershell
python -m driving_detection assets sync --config configs/assets.yaml
python -m driving_detection data prepare --config configs/data/bdd-subset.yaml
python -m pytest tests/test_data.py tests/test_metrics.py
```

If data downloads are unavailable, import authorized archives instead, replacing these example paths:

```powershell
python -m driving_detection assets sync --config configs/assets.yaml --images-archive "C:/Datasets/bdd100k_images_100k.zip" --labels-archive "C:/Datasets/bdd100k_det_20_labels.zip"
```

Expected: preparation validates itself, records exclusions and negative counts, freezes profile/manifests with byte hashes, and selects 5,000 train / 1,000 val / 1,000 project-held-out images/sequences. Confirm three-class coverage and zero sequence/content overlap. Repeat identical preparation to verify reuse/stable manifests. Unknown labels, invalid boxes/provenance, insufficient eligible counts or coverage fail clearly. Inspect a sample label overlay and focused one-pixel/boundary geometry cases. The holdout is a subset of official labeled val, not the official benchmark test.

## 3. One optional CPU smoke — D3–D5

Once the connected commands exist and model assets are available:

```powershell
$env:RUN_MODEL_SMOKE = "1"
python -m pytest tests/test_smoke.py
Remove-Item Env:RUN_MODEL_SMOKE
```

On Linux use RUN_MODEL_SMOKE=1 for that invocation. The smoke test privately generates a few BDD-shaped images/labels and short video, prepares them through the same importer, trains one CPU epoch at size 320/batch 2, loads the checkpoint, infers images/video and runs evaluation. It checks usable outputs and failure/empty behavior without requiring a trained model to achieve a particular accuracy.

Default pytest runs skip this model smoke unless explicitly enabled. Run it when the pipeline first connects or materially changes; do not add separate contract/integration layers or retrain for routine document/config edits. Synthetic scores are not driving-scene findings.

## 4. Actual baseline and demonstrations — D3/D4

On the selected GPU environment:

```powershell
python -m driving_detection train --profile data/prepared/bdd-subset-v1/profile.json --config configs/train/baseline.yaml --run-id baseline-01
python -m driving_detection infer --model artifacts/runs/baseline-01/weights/best.pt --input data/new-scenes/images --config configs/evaluation/default.yaml --run-id baseline-images-01
python -m driving_detection infer --model artifacts/runs/baseline-01/weights/best.pt --input data/new-scenes/demo.mp4 --config configs/evaluation/default.yaml --run-id baseline-video-01
```

Supply new driving images/video at those paths with provenance; ordinary demonstrations need not be team-captured. Expected: a completed declared 20-epoch baseline or an honest interrupted/failed status, a loadable checkpoint, full FR-012 settings in run.json and saved configs/logs. Batch fallback is recorded before the reported run.

Inspect original/annotated images and video, per-input predictions, valid empty results and failed-input diagnostics. Component development may use the official checkpoint with --reference-coco, but baseline acceptance requires the trained project model.

## 5. Evaluate and manually review core — D5

```powershell
python -m driving_detection evaluate --model artifacts/runs/baseline-01/weights/best.pt --profile data/prepared/bdd-subset-v1/profile.json --partition val --config configs/evaluation/default.yaml --run-id baseline-val-01
```

Expected: predictions, run.json and metrics.json with AP50/AP50:95, micro/per-class P/R at the documented operating point, coverage/counts and null reasons where relevant. One synchronized interval measures preprocessing+transfer+forward+NMS over the fixed validation timing subset; record mean latency/throughput, hardware/input/batch/precision, warm-up/counts and excluded decoding/drawing/encoding. This does not claim full video-processing speed.

A reviewer confirms D1–D5 real-data/model identities, baseline, image/video outputs, metric tests, validation results/timing and success/failure examples or missing-case explanations. Record the acceptance in experiment notes. No core command or generated gate file.

## 6. Compare and save the selection — D6

The size-960 configuration differs only in inference size; compare against baseline-val-01:

```powershell
python -m driving_detection evaluate --model artifacts/runs/baseline-01/weights/best.pt --profile data/prepared/bdd-subset-v1/profile.json --partition val --config configs/evaluation/size-960.yaml --run-id candidate-val-01
```

Review identical model/validation membership/device/precision/environment and timing samples. Record both results, hypothesis and tradeoff in results/comparison.md. Choose 960 only with AP50:95 gain>=0.005 and mean latency ratio<=1.5; otherwise retain 640. Failed/worse attempts remain evidence; an incomplete comparison is labeled partial.

Before reading final test results, save results/selected.yaml with chosen checkpoint and hash, profile/manifest hashes, saved resolved evaluation config and hash, environment file and hash, validation run references, choice reason and time. Point config_path to the chosen validation run's saved resolved config, so final evaluation reuses the actual selected values.

```powershell
python -m driving_detection evaluate --model artifacts/runs/baseline-01/weights/best.pt --profile data/prepared/bdd-subset-v1/profile.json --partition test --config artifacts/runs/baseline-val-01/resolved-config.yaml --selection results/selected.yaml --run-id final-01
```

The example assumes size 640 won. If 960 won, use candidate-val-01/resolved-config.yaml instead. Expected: selected fields/hashes match actual inputs before processing; final results use all project-held-out samples and record any failure/attempt in ordinary run.json. There is no exposure ledger. Later changes after test inspection are exploratory on that holdout, while exact reruns are labeled reproduction.

## 7. Report/presentation handoff — D7/D8

Review docs/course-deliverables.md when created: FR-001–036 owner/status/evidence and honest satisfied-count/36, optional D9 separate, team-accessible artifact retrieval. Students write the three-page PDF with required sections, front-page contributors/roles, citations/links, supported results, limitations and future work.

Verify current Canvas deadlines/timezones, hosting/instructor identity conflict, access and one report submitter. The saved report cutoff is December 2, 2026, 11:59 p.m.; presentation/audience-response dates need separate verification. Actual uploads and assignment comments require evidence.

Review a readable/audible 5–10 minute recording covering problem/solution/method/implications, Canvas slides, Unlisted YouTube link in comments and incognito playback. Later review classmates' feedback and answer Top 10 questions on the group Response Page; missing feedback/access or fewer questions stays pending clarification. Materials can merge while these external actions remain explicitly pending.

## 8. Optional captured footage — D9

After core acceptance and only if resources permit, record known/unknown viewpoint/settings/resolution/frame rate/scene conditions and footage identity in ordinary experiment notes. Reuse infer with that clip and the selected config. Quantitative accuracy requires real labels and an independent prepared evaluation profile; unlabeled footage supports observations only. No capture command or new infrastructure. Missing clip/time is an explicit skip and never blocks required work.

