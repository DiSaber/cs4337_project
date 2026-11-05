# CS4337 Driving Scene Object Detection

A Python pipeline for detecting cars, pedestrians and traffic lights in driving
scenes. Implementation follows the [feature plan](specs/001-driving-object-detection/plan.md)
and [task list](specs/001-driving-object-detection/tasks.md).

Setup now supports verified asset sync and model readiness, including a tested
local CPU environment. See [usage](docs/usage.md), [asset sources/terms](docs/references.md),
and [setup evidence](results/experiments.md). Data preparation, training, inference
and evaluation handlers remain later tasks.

US1 is partially complete: the Linux GPU lock and teammate acceptance require
the [Colab verification steps](docs/colab-setup.md). The existing US1 branch covers
Phases 1–3; local readiness is not full pipeline or course completion.

The allowed runtime range is Python 3.10–3.14, including Colab's reported 3.13
and the local Python 3.14.7 / 3.10 interpreters. Dependency ranges in
`pyproject.toml` allow pip to select releases for the chosen interpreter; they are
not a verified environment lock or evidence of full pipeline compatibility.
The [CPU lock](requirements/cpu-lock.txt) is specific to Windows/Python 3.14.7;
the CUDA lock awaits actual Colab verification. See the
[future quickstart](specs/001-driving-object-detection/quickstart.md) for later
pipeline interfaces; its training/data/evaluation commands are not implemented yet.

Keep datasets in `data/`, model source/initial weights in `external/`, and generated
runs/media in `artifacts/`; these directories are ignored by Git. Track small
configurations in `configs/` and compact summaries/retrieval instructions in
`results/`. Keep credentials out of tracked files. The existing
`.specify/.gitignore` continues to exclude local feature state.
