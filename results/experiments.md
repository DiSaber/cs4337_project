# Experiment and setup evidence

## 2026-11-05: US1 local CPU setup

Status: **author-verified local setup; US1 acceptance completed with the Colab evidence and review recorded below**.
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
