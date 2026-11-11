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

## D3 smoke training on Colab (T014)

Status: **run on 2026-11-11** (`smoke-03` completed; see
[experiments](../results/experiments.md)). These steps prepare the data in Colab and
run the one-epoch smoke training. Select a GPU runtime and clone the branch that contains the train
command (`001-driving-object-detection-us3` until it is merged), using the clone
cell above with that branch name. The CUDA lock is for Python 3.13; if Colab now
has another version, stop and record it instead of forcing the lock.

```bash
%%bash
set -euo pipefail
cd /content/cs4337_project
python --version
python -m venv --without-pip .venv-colab
python -m pip --python .venv-colab/bin/python install -r requirements/cuda-lock.txt
python -m pip --python .venv-colab/bin/python install --no-deps -e .
# Downloads about 5.9 GB (images 5.67 GB, labels 0.19 GB) from the BDD author mirror, then verifies and extracts it.
.venv-colab/bin/python -m driving_detection assets sync --config configs/assets.yaml
.venv-colab/bin/python -m driving_detection check --config configs/assets.yaml --device cuda:0
.venv-colab/bin/python -m driving_detection data prepare --config configs/data/bdd-subset.yaml
```

Preparation must reproduce the frozen Linux-desktop profile exactly. Compare these
`exports` entries in `data/prepared/bdd-subset-v2/profile.json` before training:

| Export | SHA-256 from the D2 run |
| --- | --- |
| `manifest.train.jsonl` | `0f3b35bfc1ded48c55ebf4d6b30cb8e55089f4e51461fd9865d36e2ca2a15251` |
| `manifest.val.jsonl` | `73d93c05c045119cf276fd7f131fbd3181503bbb4103e335119a26cc72f495e0` |
| `manifest.test.jsonl` | `42286df26bc61943244c51aa51e5702a65dec4e8a7a3d2611a08abe14d6a76fb` |
| `yolo/dataset.yaml` | `fd880cae4bd4604e5c458d0c9c7c8e7ebb9230251e9b2ae6917c0a6b4f4e4b8d` |

If any differ, stop: the data is not the frozen profile. Then run the smoke training:

```bash
%%bash
set -euo pipefail
cd /content/cs4337_project
.venv-colab/bin/python -m driving_detection train \
  --profile data/prepared/bdd-subset-v2/profile.json \
  --config configs/train/smoke.yaml --run-id smoke-04 --device cuda:0
```

Expected: exit 0, `status: completed` and `label: smoke` in
`artifacts/runs/<run-id>/run.json`, one row in `results.csv`, and a `head` entry
with the three canonical class names. Download the run before the runtime expires
(about 30 MB with both checkpoints):

```python
import shutil
from google.colab import files

bundle = shutil.make_archive('/content/smoke-04', 'zip',
                             root_dir='/content/cs4337_project/artifacts/runs',
                             base_dir='smoke-04')
files.download(bundle)
```

If training fails, keep the run directory (its `run.json` and `train.log` show the
reason) and return it as well; a retry needs a new run ID such as `smoke-05`. IDs 01–03 are used.

## D3 baseline training on Colab (T015)

Status: **not yet run**. One attempt on 2026-11-11 lost its session during asset sync
(see [experiments](../results/experiments.md)); `baseline-01` is unused.

The ready-made notebook [`notebooks/t015_baseline_colab.ipynb`](../notebooks/t015_baseline_colab.ipynb)
contains the steps below as cells (upload it with File > Upload notebook).

Run this from a Colab notebook in the browser, not the Colab CLI: the CLI could not
mount Drive (it needs the browser consent prompt). Free Colab can end a session
without warning, so the run folder is copied to Drive while training runs. Only the
run folder goes to Drive (expected well under 100 MB: two YOLOv5s checkpoints of about
14 MB, logs, `results.csv`, plots). The 5.9 GB dataset stays on the VM; it can be
downloaded and prepared again.

1. Select a T4 GPU runtime, clone `001-driving-object-detection-us3` with the clone
   cell above, then mount Drive:

   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```

2. Run the install/sync/prepare cell and the hash comparison from the smoke section
   above. Stop if any hash differs.

3. Start a copy loop that keeps Drive up to date every 10 minutes. Training writes to
   local disk; only the copy touches Drive.

   ```bash
   %%bash
   mkdir -p /content/drive/MyDrive/cs4337/runs
   nohup bash -c 'while true; do
     [ -d /content/cs4337_project/artifacts/runs/baseline-01 ] && \
       rsync -a /content/cs4337_project/artifacts/runs/baseline-01 /content/drive/MyDrive/cs4337/runs/
     sleep 600
   done' > /content/drive-sync.log 2>&1 &
   ```

4. Train in the foreground. A running cell keeps the runtime busy; keep the tab open.

   ```bash
   %%bash
   set -euo pipefail
   cd /content/cs4337_project
   .venv-colab/bin/python -m driving_detection train \
     --profile data/prepared/bdd-subset-v2/profile.json \
     --config configs/train/baseline.yaml --run-id baseline-01 --device cuda:0
   ```

5. After it exits (success or failure), make a final copy before the runtime ends:

   ```bash
   %%bash
   rsync -a /content/cs4337_project/artifacts/runs/baseline-01 /content/drive/MyDrive/cs4337/runs/
   ls -la /content/drive/MyDrive/cs4337/runs/baseline-01 /content/drive/MyDrive/cs4337/runs/baseline-01/weights
   ```

Expected: exit 0, `status: completed` and the baseline label in `run.json`, 20 rows in
`results.csv`, and `weights/best.pt` with the three canonical class names. If the
session drops, the Drive copy holds the last checkpoints and log up to 10 minutes
old; that partial folder is evidence of a failed/interrupted `baseline-01`, and the
retry uses `baseline-02` (no resume). Then copy the folder from Drive to
`artifacts/runs/` on the review machine for the T015 audit.
