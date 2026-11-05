# File Record Contract

Keep only information required for reproducibility and component handoff. Use UTF-8 JSON/JSONL for outputs, YAML for configuration, and Markdown for comparisons/course tracking. See [data model](../data-model.md) and [pipeline rules](pipeline.md).

Check required values, finite numbers, class/box validity, identities and file existence where consumed. Do not introduce generic schema validation, custom canonical JSON hashing, a record registry, or a linked digest graph. SHA-256 of actual asset/manifest/checkpoint/resolved-config bytes is sufficient. Stored artifact paths should be workspace-relative; large artifact handoff needs team-accessible retrieval instructions. Never serialize secrets or signed credential-bearing URLs.

## Asset inventory

One assets.json records public source/version, expected checksum if published, observed SHA-256, path, expected members, terms/citations and verification result for each required asset. Source commit and acquired weight identity must be stable before reported experiments. A first-download observed hash is provenance, not an invented publisher signature.

## Prepared dataset

profile.json contains profile ID, BDD annotation/assets identity, class mapping, selection/seed/preprocessing rules, requested/actual counts, exclusions/reasons, integrity outcome, manifest/export references and their byte hashes.

Each manifest.train.jsonl, manifest.val.jsonl and manifest.test.jsonl line records sample ID, image path/hash/dimensions, source official partition, sequence ID/provenance, project partition, canonical/source annotations and available scene attributes. Sort membership by sample ID for repeatable bytes. Audit rejected/quarantined samples separately from eligible membership.

Canonical annotation example:

```json
{"annotation_id":"object-1","class_id":0,"bbox_xyxy":[10.0,20.0,31.0,41.0],"source_category":"car","source_bbox_xyxy":[10.0,20.0,30.0,40.0],"clipped":false}
```

Canonical IDs: car=0, pedestrian=1, traffic_light=2. Boxes use original-image half-open geometry. Empty annotations=[] is a valid negative.

YOLO export uses class 0–2 plus normalized center/size and empty label files for negatives. COCO export uses stable integer image IDs from sorted sample IDs, category IDs 1–3, bbox=[x1,y1,x2-x1,y2-y1], positive area and iscrowd=0 because ignored/crowd samples are excluded. Include negative images and preserve the sample-ID mapping. Training YAML exposes only train/val.

## One run directory

run.json records:
- ID/kind/status and timestamps; command argv and project/model source revisions.
- Source dataset/weights/checkpoint identities and hashes; split/manifests and preprocessing/augmentation.
- Saved resolved settings and their byte hashes; dependency versions/environment file, interpreter, seed and nondeterminism.
- Hardware/device, training budget/settings and actual completion; selected checkpoint/epoch/validation rule.
- Input/output references, actual model head/remapping, expected/processed/failed counts and failure reason if applicable.

Save the resolved config, upstream training log/history and weights beside the record. No separate model metadata registry, lifecycle journal, canonical record digest or resume system is required. Refuse output reuse. A stopped run stays interrupted/failed, and a new attempt gets another ID.

## Predictions and results

Each predictions.jsonl line is one image/frame, including empty results:

```json
{"input_id":"clip-a:000000","frame_index":0,"width":1280,"height":720,"status":"completed","predictions":[{"class_id":2,"score":0.91,"bbox_xyxy":[100.0,80.0,120.0,140.0]}]}
```

Still images omit frame_index and use manifest sample_id or independent input identity/hash. Video uses increasing frame indices; retain frame rate/dimensions in run.json. Each prediction uses finite score in [0,1] and a canonical original-coordinate box. Failed input/frame status includes a reason and cannot become a fabricated empty result.

Metric prediction records retain the AP confidence floor. Annotated display filtering is separate. Reject incomplete evaluation membership.

metrics.json records model/data/config references, partition/counts, evaluator version and definitions, map_50, map_50_95, precision_micro, recall_micro, TP/FP/FN, per-class results, undefined-value reasons, one timing summary and representative-example/limitation references. Undefined values are null with a reason. Never confuse COCO average recall with fixed-threshold recall.

Timing fields: hardware/device/precision, input size/batch, sample-list hash/count, warm-up count, included/excluded stages, synchronized elapsed seconds, mean ms/image and images/s. No stage traces, percentiles or separate timing record are required.

## Human-reviewed comparison and selection

results/comparison.md records hypothesis, same-model baseline/candidate validation run references, metrics/timing, declared rule, choice/reason and failed attempts. This is a table, not an experiment orchestrator.

Before final testing, results/selected.yaml identifies the chosen checkpoint/path/hash, prepared profile and manifest hashes, saved resolved evaluation config/path/hash, environment file/path/hash, validation run references, reason and recorded time. The saved evaluation config contains inference/metric/device settings; partition, run ID and output paths are separate run arguments, so reusing those settings for test does not change their identity. Test evaluation compares selected fields with actual inputs and rejects setting overrides that differ from the selection. Keep model/data/config/environment identities fixed for an unbiased selected result; disclose later changes and test exposure in ordinary experiment notes/run logs. No core-gate, selection registry or test-exposure file is required.

## Course/capture notes

docs/course-deliverables.md tracks all required FR-001–036 owners/status/evidence plus external actions, sources/conflicts, verified dates/timezones, roles, access, links, uploads and Top 10 follow-up. Optional FR-037–039 stay separate. A reported completion fraction names satisfied-count/36 and does not imply an effort percentage.

Optional capture metadata belongs in normal experiment notes with input hash, known/unknown camera/scene details, model/settings/results and limits. Unlabeled footage cannot receive an accuracy score.

