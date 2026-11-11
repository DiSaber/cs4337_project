# Environment records

`cpu-lock.txt` is the resolved **Windows amd64 / Python 3.14.7 CPU** environment
used for real import/checkpoint readiness checks. It lists 54 external runtime
distributions with wheel SHA-256; install the project itself separately with
`--no-deps -e .`. `cpu-wheels.json` preserves all wheel origins, including the
official CPU PyTorch wheel URLs. Installation steps are in [usage](../docs/usage.md).

On 2026-11-10, `pytest`, `pluggy` and `iniconfig` were removed from both locks
because constitution Principle VII rules out automated tests; no other locked
package depends on them. The verified environments contained them (57 CPU / 74
CUDA distributions), and both `*-wheels.json` files still record those original
installs. The trimmed CPU lock passed a hash-checked `pip install --dry-run`
against the verified environment; the trimmed CUDA lock was not reinstalled.

This is a platform/interpreter-specific lock, not a Python 3.10–3.14 or Linux
compatibility claim. Other allowed Python versions need their own environment
resolution and readiness check. The original Python-3.11 targets were superseded
when the user authorized the locally installed interpreters and Colab 3.13.

`cuda-lock.txt` records the supplied, successful **Colab Linux x86_64 / Python
3.13.16 / Tesla T4 / CUDA 12.8** environment: 71 external distributions with exact
wheel URLs and SHA-256. `cuda-wheels.json` preserves the corresponding provenance.
The dependency set matches both the freeze file and installed-package inspection;
versions/origins come from the initial pip reports. Two missing generic-wheel
hashes reuse identical official wheel records from CPU setup; the Linux MarkupSafe
wheel hash was measured from its official recorded URL during evidence review.

Follow the [Colab instructions](../docs/colab-setup.md) to reproduce it; never
install the Windows CPU lock in Colab or the Linux CUDA lock on Windows. The lock
captures a GPU environment that passed first/repeated readiness checks; reinstalling
the finalized lock in another Colab runtime has not been separately performed.
This is setup evidence, not training or broader GPU compatibility evidence.

On 2026-11-11, `tensorboard` 2.21.0 and its six new dependencies (absl-py, grpcio,
Markdown, protobuf, tensorboard-data-server, Werkzeug) were added to
`cuda-lock.txt` from a Colab pip install report. Pinned YOLOv5 imports tensorboard
unconditionally, so training failed without it. The updated lock passed a
hash-checked dry run on that runtime and matched its 78 installed packages.
`cuda-wheels.json` still records only the original installs. `cpu-lock.txt` does
not include tensorboard yet; resolve and add it on Windows before CPU training.
