# Course deliverables checklist

This tracks what the course needs (FR-001–036), who owns each item, its status and
the evidence. "Done" means repository work with evidence; uploads, messages and
access changes are student actions and stay pending until someone does them and
records proof here. Last updated 2026-11-11.

**Required requirements satisfied: 24 / 36.** This counts requirements, not effort or
grading credit. FR-023 and FR-024 are satisfied on the D6 branch
(`001-driving-object-detection-us6`), which is not merged yet. Optional FR-037–039
are tracked separately and never count toward the total.

## Team, roles and submitter

| GitHub account | Name | Role(s) |
| --- | --- | --- |
| DiSaber | Marc Benamou | _to fill in_ |
| Axrtx | _to fill in_ | _to fill in_ |
| aaronsisourath | _to fill in_ | _to fill in_ |

- Report submitter (one person uploads for the team): **_to decide_**
- Names and roles must also appear on the report's front page (FR-027).

## Deadlines

| Item | Date | Source | Status |
| --- | --- | --- | --- |
| Report PDF upload | December 2, 2026, 11:59 p.m. (displayed) | Saved `Submit-ProjectReport.htm` | Timezone not established; check Canvas before relying on it |
| Presentation slides and video | Not given | Presentation rubric has no date | Check the presentation assignment in Canvas |
| Top 10 audience responses | Not given | Presentation rubric | Check Canvas once peer feedback opens |

## Links and access

| Item | Value | Status |
| --- | --- | --- |
| Code repository | https://github.com/DiSaber/cs4337_project (public) | Available; instructor access needs no invite while public |
| Notebook | `notebooks/t015_baseline_colab.ipynb` in the repository | Shared through the repository; no private Colab copy is required by the code |
| Large artifacts | Linux desktop `artifacts/` and Drive `MyDrive/cs4337/runs/` | Not public; retrieval steps in `docs/usage.md` |

**Unresolved hosting/account conflict (FR-032).** The project rubric names
`git.txstate.edu` or Google Colab with collaborator IDs `k-b459` / `k_b459`. The report
assignment names GitHub account `keshavsbhandari`. Both mention private Colab sharing
with `keshav.s.bhandari@gmail.com`. Ask the instructor which platform and account to
use before granting access or submitting links. A public GitHub repository may already
be acceptable, but that is not confirmed.

## Required requirements (FR-001–036)

Status: **done** (evidence exists), **partial**, **pending** (not started or a student
action not yet done).

| FR | Topic | Owner | Status | Evidence |
| --- | --- | --- | --- | --- |
| 001 | Setup instructions from a fresh checkout | D1 | done | `docs/usage.md`, `docs/colab-setup.md`; Colab fresh-setup check in `results/experiments.md` |
| 002 | Cited, identified, automated assets | D1 | done | `configs/assets.yaml`, `docs/references.md`, `assets sync` |
| 003 | Reuse and corrupt-asset detection | D1 | done | Repeat sync reuse in `results/experiments.md` |
| 004 | Large data and credentials outside Git | D1 | done | `.gitignore`, Syncthing ignore rules |
| 005 | BDD100K with recorded version and subset | D2 | done | `bdd-subset-v2` profile; label release documented in `docs/references.md` |
| 006 | Car, pedestrian, traffic light mapping | D2 | done | `configs/data/bdd-subset.yaml`, profile class mapping |
| 007 | Integrity checks with counts and reasons | D2 | done | D2 entry in `results/experiments.md` |
| 008 | Fixed partitions, no sequence crossing | D2 | done | Session-disjoint v2 partitions, zero-overlap check |
| 009 | Preprocessing and augmentation recorded | D2/D3 | done | Profile rules; `configs/train/baseline.yaml` augmentation |
| 010 | Repeatable manifests and integrity | D2 | done | Manifest hashes repeated on Colab |
| 011 | Trained baseline with history | D3 | done | `baseline-01` (20 epochs, T4) |
| 012 | Complete run records | D3 | done | `baseline-01/run.json`; audit accepted |
| 013 | Train/val-only selection; smoke labeled | D3 | done | Smoke runs labeled `smoke`; test never passed to training |
| 014 | Completion status and loading | D3 | done | `docs/usage.md` training section |
| 015 | Inference on new images and prerecorded video | D4 | **partial** | Images done (`baseline-samples-01`); real-video demo deferred to the optional dashcam study by Marc Benamou (2026-11-11). Video code shown only with a slideshow and a truncated AVI |
| 016 | Inference records and empty results | D4 | done | `infer` `run.json`; empty gray-image result |
| 017 | Clear failures for bad inputs | D4 | done | Corrupt, unsupported and truncated-video runs |
| 018 | Aggregate and per-class metrics | D5 | done | `baseline-val-02/metrics.json` |
| 019 | AP50, AP50:95, matching rule, hand check | D5 | done | Hand count confirmed (`smoke-val-01/review/`) |
| 020 | Results tied to model, partition, config | D5 | done | `metrics.json` identities |
| 021 | Speed claims with conditions | D5 | done | Timing block: CPU, 640, batch 1, stages, warm-up, 100 samples |
| 022 | Success/failure examples and limits | D5 | done | `baseline-val-02/examples/`; limits in `docs/usage.md` |
| 023 | One bounded candidate on validation | D6 | done (branch) | `results/comparison.md` |
| 024 | Declared rule, selection frozen before test | D6 | done (branch) | `results/selected.yaml` (2026-11-11T22:06:12Z) |
| 025 | Final held-out result preserved | D6 | pending | T027 waits for selection sign-off |
| 026 | Three-page PDF with required sections | D7 | pending | Student-authored; `docs/report/` not started |
| 027 | Names/roles on front page; citations; links | D7 | pending | Needs names/roles above |
| 028 | Own-words report; AI-use log | D7 | partial | `docs/ai-use-log.md` kept per task; report prose pending |
| 029 | Commented code and README instructions; >= 60% tracked honestly | D7 | partial | README and `docs/usage.md` current as of D6; final review is T030 |
| 030 | This checklist | D7 | done | This file |
| 031 | One team member uploads the PDF on time | D7 | pending | Student action |
| 032 | Hosting/account conflict resolved with instructor | D7 | pending | See above; student action |
| 033 | 5–10 minute presentation recording | D8 | pending | Student action |
| 034 | Readable slides, audible speech, rehearsal review | D8 | pending | Student action |
| 035 | Slides in Canvas, Unlisted YouTube link, incognito test | D8 | pending | Student action |
| 036 | Top 10 audience questions answered | D8 | pending | After peer feedback |

Count: done 24 (001–014, 016–024, 030), partial 3 (015, 028, 029), pending 9 (025,
026, 027, 031–036); 24 + 3 + 9 = 36.

## Optional (FR-037–039, D9)

| FR | Topic | Status |
| --- | --- | --- |
| 037 | Team-captured dashcam footage test | not started; now also carries the deferred FR-015 video demo |
| 038 | Observations kept separate from measured accuracy | not started |
| 039 | Optional, never blocking | respected |

## Submission evidence

Record each student action here with date, who did it and proof (receipt, link,
screenshot location):

- Report upload: _pending_
- Instructor access confirmation: _pending_
- Slides upload: _pending_
- YouTube link in comments and incognito playback check: _pending_
- Top 10 responses: _pending_
