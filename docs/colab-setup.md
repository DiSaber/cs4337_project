# US1 Colab verification handoff

Status: **verified from the supplied Colab evidence** on 2026-11-05: Python
3.13.16, Tesla T4, torch 2.9.1+cu128/torchvision 0.24.1+cu128. Both readiness
checks passed; Marc Benamou confirmed review completion. See
[evidence](../results/experiments.md). These steps check setup/loading, not training.

Select a GPU runtime in Colab. Use Python 3.10–3.14; record the actual version
rather than assuming Colab still supplies 3.13. First make this implementation
available on `001-driving-object-detection-us1` in the shared repository. Then run:

```python
from pathlib import Path
import os
import subprocess

checkout = Path('/content/cs4337_project')
if not checkout.exists():
    subprocess.run([
        'git', 'clone', '--branch', '001-driving-object-detection-us1',
        'https://github.com/DiSaber/cs4337_project.git', str(checkout)
    ], check=True)
os.chdir(checkout)
subprocess.run(['git', 'status', '--short', '--branch'], check=True)
```

Confirm the checkout includes `configs/assets.yaml` and `assets.py`. The following
CUDA 12.8 profile passed the supplied checks and comes from the
[official PyTorch version table](https://pytorch.org/get-started/previous-versions/).
It uses a matched torch/torchvision pair compatible with Python 3.13. Actual
driver/GPU compatibility must pass `check`; if it fails, retain the failure and
choose a documented official profile for the provided hardware. Do not fall back
to CPU and label it GPU verification. Do not use the Windows CPU lock here.

To reproduce the recorded environment, replace the two install commands below
with these commands, keeping the readiness/reuse checks:

```bash
python -m pip --python .venv-colab/bin/python install -r requirements/cuda-lock.txt
python -m pip --python .venv-colab/bin/python install --no-deps -e .
```

The finalized hashed lock has been checked against the supplied installation
records; a separate reinstall of that exact lock has not been run. The original
resolution commands below document how the accepted environment was obtained.

```bash
%%bash
set -euo pipefail
cd /content/cs4337_project
mkdir -p artifacts/colab-evidence
python --version > artifacts/colab-evidence/python.txt
nvidia-smi > artifacts/colab-evidence/nvidia-smi.txt
git rev-parse HEAD > artifacts/colab-evidence/project-revision.txt
python -m venv --without-pip .venv-colab
python -m pip --python .venv-colab/bin/python install \
  torch==2.9.1 torchvision==0.24.1 \
  --index-url https://download.pytorch.org/whl/cu128 \
  --report artifacts/colab-evidence/torch-install.json
python -m pip --python .venv-colab/bin/python install -e '.[dev]' \
  --report artifacts/colab-evidence/project-install.json
python -m pip --python .venv-colab/bin/python check
.venv-colab/bin/python -m driving_detection assets sync \
  --config configs/assets.yaml --only model
.venv-colab/bin/python -m driving_detection check \
  --config configs/assets.yaml --device cuda:0
cp artifacts/assets.json artifacts/colab-evidence/first-assets.json
```

The expected result is successful CUDA allocation/NMS and official reference
checkpoint loading. Absent dataset archives are reported separately. If a cell
fails, stop and return its error output; do not mark the task complete.

Repeat model setup to check reuse and save environment evidence:

```bash
%%bash
set -euo pipefail
cd /content/cs4337_project
.venv-colab/bin/python -m driving_detection assets sync \
  --config configs/assets.yaml --only model
.venv-colab/bin/python -m driving_detection check \
  --config configs/assets.yaml --device cuda:0
cp artifacts/assets.json artifacts/colab-evidence/repeated-assets.json
python -m pip --python .venv-colab/bin/python freeze --all --exclude-editable \
  > artifacts/colab-evidence/cuda-freeze.txt
python -m pip --python .venv-colab/bin/python inspect \
  > artifacts/colab-evidence/installed.json
```

Repetition must print reuse messages and keep the same source/checkpoint hashes.
Pip reports preserve wheel origins/hashes from the initial resolution; retain
them even if repeated pip installs later produce empty reports. The freeze file
is evidence for a future `requirements/cuda-lock.txt`, not an already reviewed
GPU lock. The returned freeze/install evidence has now been reviewed and finalized
as `requirements/cuda-lock.txt`. For future reruns, retain reviewer name/date,
fresh/repeat outcomes, any existing result
files preserved, and failures/recovery in `results/experiments.md`. The teammate
must actually perform/review these steps; generated notes cannot satisfy T007.

Download the small evidence bundle before the runtime expires:

```python
import shutil
from google.colab import files

bundle = shutil.make_archive('/content/us1-colab-evidence', 'zip',
                             root_dir='/content/cs4337_project/artifacts',
                             base_dir='colab-evidence')
files.download(bundle)
```

Return the bundle and reviewer notes. Preserve large data/weights outside ephemeral
runtime storage if needed, following dataset/model terms. Keep credentials and
large artifacts out of Git. New data preparation and training remain later phases.
