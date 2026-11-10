# External assets and software

## Dataset

Use BDD100K **100K keyframes** with **Detection 2020** labels. The
[official download documentation](https://github.com/bdd100k/bdd100k/blob/master/doc/source/download.rst)
identifies the image archive and revised labels, expected directory layouts and
publisher MD5s. `configs/assets.yaml` records those MD5s. Legacy 2018 labels and
10K segmentation images are different inputs and are not substitutes.

The image archive's published MD5 is `5a0359c86a0b8713adab1eee9a3041cb`;
Detection 2020's is `b86a3e1b7edbcad421b7dad2b3987c94`. These are publisher
release checks, not SHA-256 signatures. Setup also records observed SHA-256.

Obtain authorized `bdd100k_images_100k.zip` and `bdd100k_det_20_labels.zip` from
the official dataset access/download route linked in that documentation. Review
the [dataset terms](https://github.com/bdd100k/bdd100k/blob/master/doc/source/license.rst)
before obtaining or redistributing data. The code repository's BSD license is
separate from the data/label terms. Any account, terms acceptance or unavailable
download access must be handled manually. Supply local archives using the CLI
flags in [usage](usage.md); no credentials or signed URLs belong in Git.

The documented public directory could not be fetched by the research browser
(HTTP 502). No dataset archive was acquired in this implementation session.
Dataset URLs are therefore unset in the config; local-archive ingestion is
automated and checksum-checked. A public HTTPS URL can be configured when its
official identity and availability are verified. Raw videos are not needed.

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
