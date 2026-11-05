# CS4337 Driving Scene Object Detection

A Python pipeline for detecting cars, pedestrians and traffic lights in driving
scenes. Implementation follows the [feature plan](specs/001-driving-object-detection/plan.md)
and [task list](specs/001-driving-object-detection/tasks.md).

Phases 1–2 supply packaging, local asset/output ignore rules, CLI help/dispatch and
shared config/run-file helpers. See [current usage](docs/usage.md) for setup and
help commands. Asset, data, training, inference and evaluation handlers are still
pending and return a clear nonzero error until implemented.

The allowed runtime range is Python 3.10–3.14, including Colab's reported 3.13
and the local Python 3.14.7 / 3.10 interpreters. Dependency ranges in
`pyproject.toml` allow pip to select releases for the chosen interpreter; they are
not a verified environment lock or evidence of full pipeline compatibility.
Tested CPU/GPU locks and
asset acquisition instructions follow in D1. See the [future quickstart](specs/001-driving-object-detection/quickstart.md)
for the planned workflow; its commands require later implementation tasks.

Keep datasets in `data/`, model source/initial weights in `external/`, and generated
runs/media in `artifacts/`; these directories are ignored by Git. Track small
configurations in `configs/` and compact summaries/retrieval instructions in
`results/`. Keep credentials out of tracked files. The existing
`.specify/.gitignore` continues to exclude local feature state.
