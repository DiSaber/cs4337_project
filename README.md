# CS4337 Driving Scene Object Detection

A Python pipeline for detecting cars, pedestrians and traffic lights in driving
scenes. Implementation follows the [feature plan](specs/001-driving-object-detection/plan.md)
and [task list](specs/001-driving-object-detection/tasks.md).

Setup now supports verified asset sync and model readiness, including a tested
local CPU environment. See [usage](docs/usage.md), [asset sources/terms](docs/references.md),
and [setup evidence](results/experiments.md). Data preparation, training, inference
and evaluation handlers remain later tasks.

US1 setup is complete through Phase 3: CPU and Colab GPU readiness evidence and
Marc Benamou's confirmed review are recorded. See the
[Colab setup steps](docs/colab-setup.md). Data preparation and the rest of the
pipeline remain later phases; setup acceptance is not full course completion.

The allowed runtime range is Python 3.10–3.14, including Colab's reported 3.13
and the local Python 3.14.7 / 3.10 interpreters. Dependency ranges in
`pyproject.toml` allow pip to select releases for the chosen interpreter; they are
not a verified environment lock or evidence of full pipeline compatibility.
The [CPU lock](requirements/cpu-lock.txt) is specific to Windows/Python 3.14.7;
the [CUDA lock](requirements/cuda-lock.txt) records verified Colab/Python 3.13.16
on a Tesla T4 with CUDA 12.8. See the
[future quickstart](specs/001-driving-object-detection/quickstart.md) for later
pipeline interfaces; its training/data/evaluation commands are not implemented yet.

Keep datasets in `data/`, model source/initial weights in `external/`, and generated
runs/media in `artifacts/`; these directories are ignored by Git. Track small
configurations in `configs/` and compact summaries/retrieval instructions in
`results/`. Keep credentials out of tracked files. The existing
`.specify/.gitignore` continues to exclude local feature state.
