# External assets and software

## Dataset

Use the BDD100K **100K keyframes** with the original **2018 per-image labels**
(`bdd100k_labels.zip`, files `100k/<split>/<video name>.json`). The plan first
chose the revised Detection 2020 labels, but they can no longer be downloaded
(checked 2026-11-10):

- The documented host `dl.cv.ethz.ch` returns NXDOMAIN from public DNS, and
  `bdd-data.berkeley.edu` is unreachable. Other users report the same outage in
  [BDD100K issue #356](https://github.com/bdd100k/bdd100k/issues/356) and
  [#369](https://github.com/bdd100k/bdd100k/issues/369).
- The Internet Archive holds no copy of `bdd100k_det_20_labels_trainval.zip`.
  No Hugging Face repository with "bdd" in its name has a `det_20` file.
- The author mirror's `bdd100k_det_20_labels.zip` (231,196,019 bytes, MD5
  `e72531b982bbb42efbaaf93223527284`) does not match the published Detection 2020
  MD5 `b86a3e1b7edbcad421b7dad2b3987c94`. It contains about 2,000 JPEG frames and
  no label JSON, so it was rejected.

Research allowed a separately identified legacy-label profile before the
manifests were frozen. `bdd-subset-v1` records its label release
(`BDD100K-2018-labels-per-image`) in `profile.json`. The 2018 labels cover the same
100K keyframes and use the categories `car`, `person` and `traffic light`. The 2020
quality-check corrections are absent, and there are no ignored-region categories,
so no image is excluded for that reason. `rider` stays a separate non-target class.

Both archives come from the dataset lead author's mirror,
`http://dl.yf.io/bdd100k/`. It serves plain HTTP only because its HTTPS
certificate has expired. Integrity therefore rests on the pinned hashes:

| Archive | Publisher MD5 | Measured SHA-256 |
| --- | --- | --- |
| `bdd100k_images_100k.zip` (5,669,071,832 bytes) | `5a0359c86a0b8713adab1eee9a3041cb` | see `configs/assets.yaml` |
| `bdd100k_labels.zip` (189,638,612 bytes) | none published | `7f1f9043c70a6ff0788a323cfb914aeced109a37b7150740d670a347c881394a` |

The image MD5 comes from the [official download documentation](https://github.com/bdd100k/bdd100k/blob/master/doc/source/download.rst).
An [archived 2022 copy of the download page](https://web.archive.org/web/2022/https://doc.bdd100k.com/download.html)
lists no checksum for the per-image label archive, so its SHA-256 is the
project's own measured identity, not a publisher signature. `assets sync`
downloads both archives automatically and checks them against these values.

Review the [dataset terms](https://github.com/bdd100k/bdd100k/blob/master/doc/source/license.rst)
before obtaining or redistributing data. The code repository's BSD license is
separate from the data/label terms. Downloading means agreeing to the BDD100K
license. No account or credentials are needed for the mirror. Raw videos are not needed.

## Detector

- [YOLOv5 v7.0 source](https://github.com/ultralytics/yolov5/commit/915bbf294bb74c859f0b41f1c23bc395014ea679):
  commit `915bbf294bb74c859f0b41f1c23bc395014ea679`, acquired as an immutable
  [official archive](https://github.com/ultralytics/yolov5/archive/915bbf294bb74c859f0b41f1c23bc395014ea679.zip).
- [Official yolov5s.pt](https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt):
  COCO-pretrained 80-class reference checkpoint, not a trained three-class baseline.
- [Release license](https://github.com/ultralytics/yolov5/blob/v7.0/LICENSE):
  GPL-3.0; the original license and notices remain in the downloaded source.
  Review applicable obligations before distributing derived code/weights.

The config pins SHA-256 values measured after downloading from those official
sources. These measured values are shared project identities, not claimed
publisher signatures. Upstream source remains byte-for-byte unchanged. Readiness
uses explicit legacy full-model loading only after verifying source/checkpoint
identity. It also supplies the removed Pillow font `getsize` method through
`getbbox`; this is a small process-local compatibility adaptation.

## Runtime and evaluator

The [pinned YOLO requirements](https://github.com/ultralytics/yolov5/blob/915bbf294bb74c859f0b41f1c23bc395014ea679/requirements.txt)
explain the additional runtime dependencies declared in `pyproject.toml`.
External trackers, export packages and TensorBoard are not required by this setup.
`setuptools<81` retains the old source's `pkg_resources` import. See the
[PyTorch installation profiles](https://pytorch.org/get-started/previous-versions/),
[torchvision pairing matrix](https://github.com/pytorch/vision),
[torch serialization behavior](https://docs.pytorch.org/docs/stable/notes/serialization),
and [Pillow API removals](https://pillow.readthedocs.io/en/stable/deprecations.html).

`requirements/cpu-lock.txt` and `cpu-wheels.json` preserve the actual local CPU
versions and wheel URLs/SHA-256. `requirements/cuda-lock.txt` and `cuda-wheels.json`
record the verified Colab GPU environment; see [setup steps](colab-setup.md).
Record environment changes before comparisons.
Future metrics use [pycocotools](https://github.com/cocodataset/cocoapi/tree/master/PythonAPI).
