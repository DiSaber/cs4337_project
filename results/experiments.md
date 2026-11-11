# Experiment and setup evidence

## 2026-11-05: US1 local CPU setup

Status: **author-verified local setup; US1 acceptance completed with the Colab evidence and review recorded below**.
No training, predictions, accuracy measurements or speed benchmarks were run.

| Item | Observed result |
| --- | --- |
| Platform | Windows amd64; CPython 3.14.7, Anaconda-provided interpreter |
| Installation | New isolated `.venv`, without system site packages; global pip 26.1.2 populated it |
| Main libraries | torch 2.15.0+cpu, torchvision 0.29.2+cpu, NumPy 2.5.4, Pillow 12.3.0, OpenCV 4.14.0.94, PyYAML 6.0.3, pycocotools 2.0.11 |
| Complete dependency record | 64 external distributions in `requirements/cpu-lock.txt` (57 at setup, plus tensorboard's 7 added 2026-11-11); exact wheel origins/SHA-256 in `requirements/cpu-wheels.json` |
| Source | Official YOLOv5 archive at commit `915bbf294bb74c859f0b41f1c23bc395014ea679`; 144 extracted files, upstream files unchanged |
| Source archive SHA-256 | `5aac5c8c40f89831fee611621b5ef3dbd7a7633278713b4dd0d059e1a631c7b0` (measured official download) |
| Checkpoint SHA-256 | `8b3b748c1e592ddd8868022e8732fde20025197328490623cc16c6f24d0782ee` (measured official v7.0 download) |
| CPU readiness | Imports, CPU tensor allocation, torchvision NMS, official checkpoint load and COCO head identity passed |
| Repeat setup | Source/weights content checks passed and printed reuse; no duplicate model downloads; lock dry run proposed zero installs |
| Dependency integrity | `pip check` reported no broken requirements |
| CUDA request | Correctly exited nonzero: requested `cuda:0` unavailable in CPU-only environment; no GPU success claimed |
| Dataset | Not acquired; full sync reports missing authorized image archive, while model-only check succeeds |

The environment differs from the original Python-3.11 research pins because the
user authorized local Python 3.14/3.10 and Colab 3.13. Upstream requires additional
plotting/scientific libraries and `pkg_resources`; these are now declared, with
`setuptools<81`. Runtime adaptation scopes full-model loading to verified official
weights and restores Pillow font sizing. A small font check passed. This verifies
setup/loading only; the later connected pipeline smoke still must verify training.

Operational small-file checks passed for local archive import/reuse, changed
extracted contents, failed SHA-256, missing expected members, unsafe paths,
Windows backslashes/reserved names, symlinks, duplicate/case-colliding names,
interrupted download retry, failed inventory status and missing access guidance.
Download interruptions were simulated with in-memory response streams; real
official source/weight acquisition was also performed. Fixtures are not dataset
readiness or model accuracy evidence. No permanent extra test suite was added.

Initial failures and fixes: the sandbox blocked network sockets; authorized network
commands acquired dependencies/model assets. Windows private temporary-directory
ACLs made the first promoted assets inaccessible to sandboxed reads; inherited
permissions were restored, and staging now inherits normal parent permissions.
An initial scoped torch adapter interacted with upstream wildcard imports; loading
the source module before the adapter fixed it. ZIP original-header validation was
added after an operational fixture exposed Windows filename normalization.

Repeat commands are in [usage](../docs/usage.md). Local machine evidence resides
in ignored `artifacts/assets.json`, `artifacts/asset-receipts/`,
`artifacts/phase3-torch-install.json`, `artifacts/phase3-project-install.json`,
`artifacts/phase3-lock-repeat.json` and `artifacts/phase3-check/`. No team-accessible
artifact upload has occurred. Teammates can reacquire model assets from the pinned
public config; the tracked CPU lock/wheel records preserve dependency identities.
BDD archives require authorized access as described in [references](../docs/references.md).

## 2026-11-05: Supplied Colab GPU evidence and US1 acceptance

Status: **accepted setup evidence; T001–T007 complete**. Marc Benamou confirmed
review completion in this session. The supplied bundle contains machine evidence;
review completion is a user attestation, not a separate signed reviewer document.

| Item | Supplied evidence |
| --- | --- |
| Project revision | `67833246d48678336e5ebef0b8b33ee9fae88c24` |
| Platform/interpreter | Linux x86_64, glibc 2.39, Python 3.13.16 (GCC 13.3.0) |
| GPU/driver | Tesla T4, 15,360 MiB; NVIDIA driver 580.82.07 |
| CUDA | torch runtime 12.8; nvidia-smi reports driver capability 13.0 |
| Matched model libraries | torch 2.9.1+cu128 / torchvision 0.24.1+cu128 |
| First GPU readiness | `completed`, device `cuda:0`, 80-class reference checkpoint; 23:47:38 UTC |
| Repeated GPU readiness | `completed`, same device/head/settings/hardware; 23:50:43 UTC |
| Asset reuse/integrity | Both asset records identical; source/weight SHA-256 match project pins; source tree hash stable within Colab |
| Exact dependencies | 74 external distributions agree between freeze and installed inspection, with matching initial install-report records |
| Reviewer | Marc Benamou; review complete, confirmed by the user |
| Dataset | Images/labels absent in both checks; correctly separate from model readiness |

`requirements/cuda-lock.txt` now captures exact platform wheel URLs and SHA-256;
`cuda-wheels.json` preserves the provenance. The reports omitted hashes for three
wheels: Jinja2/setuptools use the same immutable URLs/hashes as the accepted CPU
record; Linux MarkupSafe was fetched from its recorded official URL to measure
its missing hash. Every final frozen dependency has a matching version and wheel
record. No Linux CUDA packages were installed on Windows to claim this validation.

The readiness `installed` list also exposes setuptools-vendored distributions
and duplicate project/version entries after upstream imports. The lock uses the
74 actual external distributions agreed by `cuda-freeze.txt` and pip's installed
inspection, rather than incorrectly treating those vendored entries as separately
installed packages. Windows/Colab extracted tree hashes use native path ordering
and are not compared across platforms; archive/checkpoint byte hashes match.

The compact [Colab evidence record](us1-colab-evidence.json) preserves readiness,
asset/hardware identities, user-confirmed review and SHA-256/size for every supplied
file. Original files were copied byte-for-byte to ignored
`artifacts/us1-colab-evidence/`; the supplied originals remain at
`C:/Users/Marc/Downloads/us1-colab-evidence/colab-evidence/`. No separate
team-accessible upload has been performed. Share that original small bundle or
use the tracked compact record and lock/provenance for repository review.
Reproduction commands are in [Colab setup](../docs/colab-setup.md).

Limits: the bundle does not include console reuse logs or a separate result-file
preservation log; acceptance combines stable asset/readiness records, earlier
local operational checks and the user's completed-review confirmation. The final
hashed CUDA lock was derived and checked against the accepted installation, not
reinstalled in another fresh Colab runtime. Training compatibility still requires
the later connected smoke; no dataset preparation, trained baseline, accuracy or
speed measurements are claimed. US2 and later task markers remain unchecked.

## 2026-11-10: US1 merge review decisions

Status: **US1 accepted for merge to `main`; no new pipeline runs**.

- SC-001 reviewer: SC-001 asks for "a teammate other than the setup author".
  Marc Benamou ran the Colab fresh-setup check and accepted it as the independent
  check. No second teammate repeated setup. This is a recorded deviation, not
  evidence from a different person.
- Test-only packages: `pytest`, `pluggy` and `iniconfig` were removed from both
  locks and the `dev` extra was removed from `pyproject.toml` under constitution
  Principle VII. The 57 CPU / 74 CUDA counts above describe the environments as
  verified; the locks now list 54 / 71. See [requirements](../requirements/README.md).
- Rechecked locally on Windows/Python 3.14.7 CPU: `assets sync --only model`
  reused source/weights (exit 0); `check --device cpu` loaded the 80-class
  reference checkpoint (exit 0); full sync without BDD archives and the
  unimplemented `train` handler both exited 1 with clear messages. The trimmed CPU
  lock passed a hash-checked `pip install --dry-run`.
- Dataset settings: the BDD100K MD5s and extracted layouts in `configs/assets.yaml`
  match the official download documentation. Real dataset archives have still not
  been synced; D2 will be the first real check.

## 2026-11-10: D2 data preparation (T009–T012)

Status: **`bdd-subset-v2` prepared, checked and frozen**. Run on the Linux
desktop (Debian 13, Python 3.13.5, CPU only) with a data-only `.venv` holding
PyYAML 6.0.3 and Pillow 12.3.0 from the hash-pinned Linux lock.

**Assets.** Both BDD archives were downloaded from the author mirror and matched
their pinned SHA-256 values (images `afd149ea…`, labels `7f1f9043…`). The first
`assets sync` extracted and fully hashed 100,000 files per archive in 35 s
(images 5,791,783,234 bytes, tree `df88363e…`; labels 1,828,490,347 bytes, tree
`473f38a8…`). A repeat sync, which now checks file count and size only, took
2.3 s. The YOLO source receipt synced from Windows failed here only because of
path ordering: recomputed with Windows ordering, it matched exactly
(`220d504b…`, 144 files). The source was re-extracted from its cached,
checksum-verified archive; the Windows copy is kept in
`external/moved-aside-windows-receipt/`.

**v1 rejected before use.** The first real run (`bdd-subset-v1`, full filename
stem as sequence ID) passed every built-in check, but review found that 121
filename prefixes (`<session>-<clip>`) appeared in both project val and test.
Official train/val share only 1 of 42,167 train prefixes, the 6 exact-duplicate
images formed pairs within one prefix, and two viewed val/test pairs showed the
same camera, day and city on different streets. At the user's direction,
`bdd-subset-v2` uses the prefix as a recording-session sequence ID and selects one
image per session. v1 was never trained on or reported; it was deleted locally.

**Counts (`bdd-subset-v2`).** Source: 70,000 train and 10,000 val image/label
pairs, no missing pairs. Eligible: 69,993 train images in 42,164 sessions;
9,991 val images in 5,930 sessions. Quarantined (16): 4 train + 5 val images from
sessions in both official splits, 2 train + 4 val exact-duplicate images, 1 train
image whose box was empty after clipping. No unknown categories, unreadable
files or ignored regions.

| Partition | Images (requested) | Negatives | car boxes / images | pedestrian | traffic_light | Clipped boxes |
|---|---|---|---|---|---|---|
| train | 5,000 (5,000) | 15 | 51,500 / 4,947 | 6,481 / 1,541 | 12,909 / 2,758 | 873 |
| val | 1,000 (1,000) | 8 | 10,607 / 985 | 1,232 / 312 | 2,671 / 553 | 166 |
| test | 1,000 (1,000) | 7 | 10,240 / 985 | 1,249 / 302 | 2,665 / 580 | 159 |

**Integrity.** Zero cross-partition sequence and image-content overlap, all three
classes in each partition, all 7,000 selected images fully decoded. A scratch
check (not committed) found each session contributes at most one image and every
sequence ID equals the name prefix. Rerunning `data prepare` printed "Reusing
identical frozen profile".

**Geometry review.** Converting all YOLO train/val labels back to pixels matched
the manifest boxes within 0.001 px (6-decimal rounding); COCO val/test boxes
matched exactly, with category IDs 1–3. Viewed overlays: a busy all-class scene,
a night scene with a box clipped at the right edge (source x2 1279.36 → 1280), a
negative image (traffic signs only), and the smallest box. Boxes fit their
objects. Limits found: the smallest boxes come from zero-size source labels
(x1 = x2 or y1 = y2) that the inclusive +1 rule turns into 1-pixel-wide slivers
on empty road (26 train, 2 val, 5 test of about 100,000 boxes); one traffic-light
label in the busy scene looks doubtful. Both are source-label noise kept as
annotated, not conversion errors.

**Retrieval.** Frozen output: `data/prepared/bdd-subset-v2/` on the Linux desktop
(not in Git). Regenerate anywhere with the pinned archives and
`python -m driving_detection data prepare --config configs/data/bdd-subset.yaml`;
compare the `exports` hashes in `profile.json`, for example
`manifest.train.jsonl` `0f3b35bf…`, `manifest.val.jsonl` `73d93c05…`,
`manifest.test.jsonl` `42286df2…`, `coco.val.json` `26f8e1b9…`, YOLO train labels
tree `b351ebac…`. `profile.json` itself also holds a creation time, so its own
hash differs per run. Preparation has not yet been repeated on Windows.

## 2026-11-11: D3 smoke training on Colab (T014)

Status: **smoke run `smoke-03` completed**. This proves that training works end to
end. Its accuracy is not a project result and is not reported.

**Environment.** Fresh Colab GPU runtime started from the Linux desktop with the
Colab CLI: Python 3.13.16, Tesla T4 (driver 580.82.07), torch 2.9.1+cu128. The
hash-checked `requirements/cuda-lock.txt` installed cleanly with `pip check` passing.
This is the first real reinstall of that lock.

**Data.** `assets sync` downloaded and verified the source, weights and both BDD
archives. `check --device cuda:0` passed, and `data prepare` rebuilt `bdd-subset-v2`.
Sync plus preparation took 15 min. The manifest hashes for train (`0f3b35bf…`),
val (`73d93c05…`) and test (`42286df2…`), plus `yolo/dataset.yaml` (`fd880cae…`) and
`coco.val.json` (`26f8e1b9…`), all match the Linux-desktop D2 run, so the frozen
profile reproduces on a second machine.

**Attempts.** All three are kept in `artifacts/runs/` on the Linux desktop:

| Run | Status | Cause / result |
| --- | --- | --- |
| `smoke-01` | failed | `ModuleNotFoundError: tensorboard`. Pinned YOLOv5 imports it unconditionally, but it was missing from the locks and `pyproject.toml`. Added `tensorboard>=2.4.1,<3` and its 7 locked wheels. |
| `smoke-02` | failed | The epoch trained, then upstream validation called `np.trapz`, which NumPy 2.4 removed (lock has 2.5.4). Fixed with a one-line launcher that sets `numpy.trapz = numpy.trapezoid` before running unchanged `train.py`. |
| `smoke-03` | completed | 1 epoch, size 320, batch 2 (accumulate 32), seed 4337, `cuda:0`; 0.065 h. |

**Review of `smoke-03`.**
- `run.json` has all FR-012 fields: label `smoke`, `reportable_accuracy: false`,
  project commit `fdbf091`, source/weights/profile/manifest hashes, exact upstream
  command, effective batch, seeds, nondeterminism notes, 80 installed packages,
  hardware and budget use.
- `uncommitted_changes: true` is correct: the VM ran the NumPy fix before it was
  committed.
- `results.csv` has 1 epoch. The chosen epoch is 0, and `best.pt` (`cca32174…`) loaded
  on `cuda:0` with head names car, pedestrian, traffic_light and 3 classes.
- In the log, upstream transferred 343/349 weight tensors (the class layers are
  replaced for 3 classes), autoanchor stayed off, AMP checks passed, and the GitHub
  check was skipped.
- Strict deterministic mode raised no error on the T4.
- Upstream's validation of `best.pt` after fusing layers differed from the in-training
  value only in the fourth decimal of mAP@0.5:0.95. Small differences like this should
  be expected between repeats.
- The log holds 2,503 harmless `FutureWarning`s about deprecated `torch.cuda.amp`
  calls in upstream.

**CPU lock.** tensorboard and its 6 dependencies (same versions as the CUDA lock)
were added to `requirements/cpu-lock.txt` and `cpu-wheels.json` on the Windows
machine on 2026-11-11; a hash-checked dry-run install of the lock and `pip check`
passed. Training was not run on CPU. Colab storage was released when the session stopped, so the
baseline (T015) must sync and prepare again (about 15 min).

**Lost baseline setup attempt (2026-11-11).** A T4 session started from the Windows
machine with the Colab CLI (officially Linux/macOS only) installed the CUDA lock
(`pip check` passed) and verified source, weights and images. About 20 minutes in,
while labels were downloading, the session disappeared from the server; the cause is
unknown. Preparation and training never started, so no run directory exists and
`baseline-01` is still unused.

**Retrieval.** `artifacts/runs/smoke-0{1,2,3}/` on the Linux desktop (not in Git;
about 30 MB). Repeat with the Colab steps in [colab-setup](../docs/colab-setup.md).

## 2026-11-11: D4 inference development check (T016–T017)

Status: **inference code works on images, folders and video, including the failure
cases**. These are development runs with the official COCO reference checkpoint and
the `smoke-03` checkpoint. None of their accuracy is a project result.

**Environment.** Linux desktop, CPU only (no GPU), Python 3.13.5. The hash-checked
`requirements/cuda-lock.txt` was installed into the existing `.venv` (torch
2.9.1+cu128 runs on CPU); `pip check` found no broken requirements. This is the
lock's first install outside Colab.

**Inputs** (kept in a temporary folder, not in the repository): five BDD official
`100k/test` images (`cabc30fc-e7726578`, `cabc30fc-eb673c5a`, `cabc30fc-fd79926f`,
`cabc9045-1b8282ba`, `cabc9045-581f64de`). The official test split is not used by
any project partition. Also a corrupt `.jpg` (text bytes), a `.txt` file, a plain
gray 640 × 360 PNG, a 20-frame slideshow MP4 made from the five images, and an MJPG
AVI cut in half (reports 10 frames, decodes 5). The slideshow only exercises the
video code; it is not the T018 demo video.

| Run | Model | Input | Result |
| --- | --- | --- | --- |
| `dev-ref-images-01` | reference | 5 test images | completed; 113–300 boxes each at the 0.001 floor |
| `dev-ref-gray-01` | reference | gray PNG | completed; valid empty result `"predictions": []` |
| `dev-smoke-edge-01` | smoke-03 | corrupt jpg, gray png, txt | failed, exit 1; corrupt and txt have failed lines with reasons, gray png still processed |
| `dev-smoke-video-01` | smoke-03 | 20-frame MP4 | completed; annotated MP4 reads back as 1280×720, 20 frames |
| `dev-ref-truncated-01` | reference | half AVI | failed, exit 1; 5 frames processed, 5 failed lines "Decoder stopped after 5 of 10 reported frames" |
| `dev-missing-01`, `dev-noflag-01`, `dev-flag-01` | — | — | refused before loading: missing input; official weights without `--reference-coco`; trained weights with it |

Reusing an existing run ID was refused without touching the earlier run.

**Review.** In `dev-ref-images-01/annotated/cabc30fc-fd79926f.jpg` the boxes sit on
the cars and pedestrians, which shows the letterbox and the mapping back to
original pixels are right. The reference model also boxes the ego car's hood and
dashboard as "car 0.32", a real false detection. Box x-coordinates reach exactly
1280, so clipping keeps boxes inside the half-open image. The 1-epoch smoke model
still gives 275 low-score boxes on the gray image and drops zero-size boxes
(25 in the edge run, 47 over the 20 video frames) as `invalid_boxes`, as expected for an almost untrained model.

**Retrieval.** `artifacts/runs/dev-*` on the Linux desktop (not in Git).

## 2026-11-11: D5 evaluator and connected smoke pipeline (T020–T022)

Status: **the pipeline connects end to end with the smoke checkpoint**. Smoke scores
below show the evaluator runs; they are not findings and are never reported.

**Runs** (Linux desktop CPU, AMD Ryzen 9 9950X, 16 torch threads, Python 3.13.5,
torch 2.9.1+cu128 on CPU):

- `smoke-images-01`: `infer` with `smoke-03` on the five BDD official-test images;
  completed. With `dev-smoke-edge-01` (empty/invalid inputs) and
  `dev-smoke-video-01` (MP4) from the D4 check, this covers images, video, invalid
  inputs and empty results.
- `smoke-val-01`: `evaluate --partition val` with `smoke-03` at size 640; completed
  in about 1 minute. 1,000 of 1,000 images processed, 8 negatives, 295,515
  predictions at the 0.001 floor, 4,485 zero-size boxes dropped. No undefined values.
  TP + FN equals the label count overall (14,510) and for each class (car 10,607,
  pedestrian 1,232, traffic light 2,671). The run predates the CPU-model field, so its
  timing says only "CPU"; smoke makes no speed claim.
- `dev-test-nosel-01`, `dev-test-sel-01`: `--partition test` without `--selection` is
  refused by the argument parser; with one it is refused before any image is read.

**Hand count** (overlays in `artifacts/runs/smoke-val-01/review/`, labels green,
predictions at score 0.25 and above red). Counted by Claude Code from the overlays;
a team member still needs to confirm them:

| Sample | Labels | Predictions >= 0.25 | Hand count | Reported |
| --- | --- | --- | --- | --- |
| `b3039ada-2ef2a725` (no objects) | none | none | nothing | nothing |
| `b2156f8e-72e1547c` | 3 traffic lights | none | FN 3 | FN 3 |
| `b23c9e00-5506ddfb` (night) | 3 cars | car 0.62 on the van, car 0.41 on a tunnel mouth | TP 1, FP 1, FN 2 | TP 1, FP 1, FN 2 |
| `b4a8e0fd-7ca55075` (duplicate) | 3 cars | car 0.68 and 0.55 on the same car (IoU 0.67 and 0.75), car 0.30 on nothing | TP 1, FP 2, FN 2 | TP 1, FP 2, FN 2 |

In the duplicate case the higher-scored box takes the label even though the second
box overlaps it more, as the score-first rule requires.
