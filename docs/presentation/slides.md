# Presentation outline (D8, T032)

Draft structure for the 5–10 minute recorded presentation. The rubric asks four
questions: what is the problem, what is the proposed solution, how was it solved,
and what are the implications. It scores content/organization, delivery/engagement,
visual aids and subject knowledge, each from 1 to 5. Recordings outside 5–10 minutes
are not accepted.

How to use this file:
- Each slide lists what to **show** and the **facts** behind it, with sources.
- Lines starting with `SAMPLE:` are suggested wording only. Rewrite them in your own
  words before the slides and recording (course AI policy and constitution
  Principles VI and IX).
- Every number comes from `results/experiments.md`, `results/comparison.md` or a run
  folder named next to it. Do not add numbers that are not measured there.
- Image paths under `artifacts/` are on the Linux desktop (not in Git); copy the ones
  you use into the slide deck.

The slide times below add up to about 8.5 minutes, leaving room on both sides of the limits.

---

## 1. Title (0:15)

**Show:** project title, team names and roles (from `docs/course-deliverables.md`),
one striking annotated frame such as
`artifacts/runs/baseline-samples-01/annotated/` (a night street with lights and cars).

SAMPLE: "We built a detector that finds cars, pedestrians and traffic lights in
dashcam images, and measured honestly how well it works."

## 2. The problem (0:45)

**Show:** a raw dashcam frame with many objects (busy city street), then the same frame
annotated.

**Facts:**
- Driving scenes are crowded, objects are often tiny and far away, and lighting
  changes from day to night.
- Three target classes: car, pedestrian, traffic light. Detecting a traffic light's
  color/state is out of scope.
- This is a course experiment, not a safety system.

SAMPLE: "A driver-assist system first has to know what is in front of the car. Our
question was how far a small, off-the-shelf detector gets on real dashcam footage."

## 3. Data: BDD100K and a fair split (1:00)

**Show:** a small diagram: 100K BDD keyframes → 5,000 train / 1,000 val / 1,000 test,
one image per recording session.

**Facts** (D2, `results/experiments.md`):
- BDD100K 100K keyframes with the 2018 per-image labels (the 2020 labels are no
  longer downloadable).
- `bdd-subset-v2`: 5,000 train, 1,000 validation, 1,000 held-out test images.
- One image per recording session, so near-identical frames cannot leak between
  train and test. The first split (v1) had 121 sessions crossing val and test and
  was rebuilt before any training.
- Val has 10,607 cars, 1,232 pedestrians and 2,671 traffic lights; 559 day, 361
  night, 74 dawn/dusk images.

SAMPLE: "The hardest part of a fair test is making sure the test images are really
new. We found a leak in our first split and fixed it before training anything."

## 4. Solution: fine-tune YOLOv5s (1:00)

**Show:** pipeline diagram with the six commands:
`assets sync` → `data prepare` → `train` → `infer` / `evaluate`.

**Facts** (D3):
- YOLOv5s v7.0 (an established open-source detector), starting from its official
  COCO weights, with the class layer replaced for our 3 classes.
- 20 epochs, image size 640, batch 8, seed 4337, on a free Colab Tesla T4:
  0.82 hours (budget 8 hours).
- Augmentation: horizontal flip and color jitter only.
- Everything is pinned and hashed (source, weights, data, configs), so a teammate can
  repeat it.

SAMPLE: "We did not invent a new model. We took a proven one and focused on training
it carefully and measuring it honestly."

## 5. How it was evaluated (0:45)

**Show:** one review overlay with labels in green and predictions in color, for example
`artifacts/runs/smoke-val-01/review/review-dup-b4a8e0fd-7ca55075.jpg`, with the
counts written next to it.

**Facts** (D5):
- mAP (COCO standard): AP50 counts a box as correct at 50% overlap; AP50:95 averages
  stricter overlaps up to 95%.
- Precision and recall at one fixed point: score at least 0.25, overlap at least 50%.
- The metric code was checked by hand-counting hits, misses, false and duplicate
  boxes on four images; they matched.
- Speed: timed from resizing through NMS on 100 images, batch 1.

SAMPLE: "Before trusting our numbers, we counted boxes by hand on a few images to
make sure the evaluation code counts the way we think it does."

## 6. Results (1:15)

**Show:** a bar chart of AP50:95 per class (validation and test side by side) and the
headline table.

| | Validation AP50 | Validation AP50:95 | Test AP50 | Test AP50:95 |
| --- | --- | --- | --- | --- |
| All | 0.521 | 0.239 | 0.526 | 0.236 |
| car | 0.660 | 0.373 | 0.656 | 0.367 |
| pedestrian | 0.446 | 0.188 | 0.452 | 0.192 |
| traffic light | 0.457 | 0.155 | 0.469 | 0.150 |

**Facts:**
- Test precision 0.624, recall 0.607 at the fixed point.
- Speed: 26.5 ms per image (about 38 images/s) on a desktop CPU (Ryzen 9 9950X).
  No GPU speed was measured.
- Test and validation agree closely, so the validation numbers were not optimistic.
- Sources: `baseline-val-02`, `final-01`.

SAMPLE: "Cars are found best. Pedestrians and traffic lights are harder, mostly
because they are small."

## 7. Successes and failures (1:15)

**Show:** two or three overlays side by side:
- Success: `artifacts/runs/final-01/examples/car-success-b257f482-cf55d35c.jpg`
- Crowd failure: `artifacts/runs/final-01/examples/pedestrian-failure-b1ca2e5d-84cf9134.jpg`
  (10 of 18 people missed on a bright night street)
- Glare failure: `artifacts/runs/baseline-val-02/examples/traffic_light-failure-b1e2346e-c5f98707.jpg`
  (5 of 6 traffic lights missed behind windshield glare at night)

**Facts:**
- Small objects: AP50:95 about 0.10 for small boxes against 0.34 medium.
- Other confusions seen: a pedestrian countdown signal boxed as a traffic light, a
  truck or bus called a car (trucks and buses are not target classes in our labels).

SAMPLE: "The model's mistakes are not random. Crowds, glare and tiny distant objects
cause most of them."

## 8. One experiment: a bigger input (1:00)

**Show:** the two-row comparison table from `results/comparison.md`, with an arrow to
the rule.

**Facts** (D6):
- Same model, input size 960 instead of 640, on validation.
- Accuracy up: AP50:95 0.262 against 0.239 (+0.023), mostly small objects
  (0.141 against 0.097).
- Speed down: 50.5 ms against 26.4 ms per image on CPU (1.91 times slower).
- Rule fixed in advance: switch only if AP50:95 gains at least 0.005 *and* it is at
  most 1.5 times slower. Speed failed, so we kept 640, then ran the test set once.

SAMPLE: "Bigger images helped the small objects, but cost almost twice the time. We
decided the rule before seeing the result, and we followed it."

## 9. Implications and limits (0:45)

**Facts:**
- A small pretrained detector, trained for under an hour on free hardware, finds most
  nearby cars but misses many small or crowded objects.
- Untested: fog, other cameras or mounting heights, places outside the US cities BDD
  covers, GPU speed, and real prerecorded video from our own dashcam.
- Per-condition accuracy (day against night, rain, snow) was not measured; the
  failure patterns above are observations.

SAMPLE: "Our numbers describe this dataset and this camera setup. They do not prove
the model works everywhere."

## 10. Future work and wrap-up (0:30)

**Facts / options** (none of these were done):
- Measure accuracy per condition (night, rain, snow) with the existing labels.
- Train longer, or at a larger input size, aimed at small objects.
- Test GPU speed, where the 960 trade-off may differ.
- Try the optional team dashcam study (also gives the video demo).

**Show:** repository link https://github.com/DiSaber/cs4337_project and the
references slide.

## 11. References (shown, not read)

- BDD100K: F. Yu et al., "BDD100K: A Diverse Driving Dataset for Heterogeneous
  Multitask Learning", CVPR 2020. https://bdd-data.berkeley.edu/
- YOLOv5 v7.0, Ultralytics. https://github.com/ultralytics/yolov5 (GPL-3.0 for v7.0)
- COCO evaluation: pycocotools. https://github.com/cocodataset/cocoapi
- Full source and terms list: `docs/references.md`.

---

## Checklist before recording

- [ ] Rewrite every `SAMPLE:` line in your own words; delete the prefix.
- [ ] Fill in names and roles on the title slide.
- [ ] Copy the chosen images from `artifacts/` into the deck.
- [ ] Make the per-class chart from the table on slide 6.
- [ ] Rehearse once with a timer (target about 8.5 minutes, must be 5–10).
- [ ] Check slide text is readable on the recording and the audio is clear.
