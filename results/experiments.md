# Experiment and setup evidence

## 2026-11-05: US1 local CPU setup

Status: **author-verified local setup; US1 acceptance pending Colab/teammate**.
No training, predictions, accuracy measurements or speed benchmarks were run.

| Item | Observed result |
| --- | --- |
| Platform | Windows amd64; CPython 3.14.7, Anaconda-provided interpreter |
| Installation | New isolated `.venv`, without system site packages; global pip 26.1.2 populated it |
| Main libraries | torch 2.15.0+cpu, torchvision 0.29.2+cpu, NumPy 2.5.4, Pillow 12.3.0, OpenCV 4.14.0.94, PyYAML 6.0.3, pycocotools 2.0.11 |
| Complete dependency record | 57 external distributions in `requirements/cpu-lock.txt`; exact wheel origins/SHA-256 in `requirements/cpu-wheels.json` |
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

## Remaining US1 acceptance

- T004: CPU lock/provenance complete; Linux GPU environment and `cuda-lock.txt`
  pending actual Colab verification. No speculative CUDA lock is supplied.
- T007: Author CPU fresh/repeat and operational recovery checks complete;
  independent teammate review and real Linux GPU check pending. The user selected
  Colab and requested [commands to run](../docs/colab-setup.md). Return its evidence
  bundle and reviewer notes before marking T004/T007 complete.
- No real dataset acquisition or preparation is claimed. Data preparation is US2.
- Preserve any failed Colab setup, actual hardware/driver, interpreter, wheel
  provenance, successful readiness outputs and independent reviewer identity/date.
