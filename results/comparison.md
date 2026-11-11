# Candidate comparison (D6, T025–T026)

**Hypothesis.** A larger inference size (960 instead of 640) finds more small objects
(distant cars, traffic lights) with the same trained checkpoint, at a speed cost.

**Rule (declared before the run, `contracts/pipeline.md`).** Choose 960 only if
AP50:95 improves by at least 0.005 *and* mean timed latency is at most 1.5 × the 640
result. Otherwise keep 640.

**Comparable runs.** Same checkpoint `baseline-01/weights/best.pt` (`8a1f80c8…`), same
1,000 validation images (profile `618c470d…`, val manifest `73d93c05…`), same device
(CPU, AMD Ryzen 9 9950X, 16 torch threads), FP32, batch 1, same environment
(`requirements/cuda-lock.txt`, torch 2.9.1+cu128 on CPU) and the same 100 timing
samples (list hash `f89049b3…`). The configs differ only in `imgsz`.

| | Baseline 640 (`baseline-val-02`) | Candidate 960 (`candidate-val-01`) | Change |
| --- | --- | --- | --- |
| Config | `configs/evaluation/default.yaml` | `configs/evaluation/size-960.yaml` | `imgsz` only |
| AP50:95 | 0.2387 | 0.2619 | **+0.0232** (rule: >= 0.005, met) |
| AP50 | 0.5209 | 0.5771 | +0.0562 |
| AP50:95 small / medium / large | 0.097 / 0.345 / 0.421 | 0.141 / 0.345 / 0.398 | small up, large down |
| Precision / recall at 0.25 | 0.625 / 0.606 | 0.616 / 0.665 | more found, slightly more false |
| TP / FP / FN | 8,798 / 5,290 / 5,712 | 9,651 / 6,025 / 4,859 | |
| car AP50:95 | 0.373 | 0.404 | +0.031 |
| pedestrian AP50:95 | 0.188 | 0.220 | +0.032 |
| traffic light AP50:95 | 0.155 | 0.162 | +0.007 |
| Mean timed latency | 26.43 ms (37.8 images/s) | 50.47 ms (19.8 images/s) | **× 1.91** (rule: <= 1.5, not met) |
| Wall time of whole evaluation | 37 s | 64 s | |

**Decision: keep size 640.** The candidate is clearly more accurate, mainly on small
objects, but it is 1.91 times slower, beyond the declared 1.5 limit. The earlier
identical 640 run (`baseline-val-01`) timed 27.07 ms, which gives a ratio of 1.86, so
CPU timing noise does not change the outcome. The result could differ on a GPU, where
the slowdown from a larger input may be smaller; that was not measured, and the rule
is applied to the measured CPU result only.

**Notes.**
- No retraining; the candidate only changes inference size. No other candidates were
  tried, and none failed.
- Both runs recorded `uncommitted_changes: true`. `baseline-val-02` ran with the
  example-selection code committed afterwards in `c7e9c63`; `candidate-val-01` ran
  with the test-selection checks (T024), which the validation path does not use.
  Neither change affects predictions or metrics: `baseline-val-01`, run before the
  example code, has byte-identical predictions.
- Resources: about 1.5 minutes of desktop CPU in total. Run folders are on the Linux
  desktop in `artifacts/runs/` (not in Git).

The frozen selection is `results/selected.yaml`, saved before any test image was read.

The selected configuration was then run once on the held-out test subset as
`final-01` (AP50:95 0.236; see [experiments](experiments.md)).
