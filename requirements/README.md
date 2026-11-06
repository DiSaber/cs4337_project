# Environment records

`cpu-lock.txt` is the resolved **Windows amd64 / Python 3.14.7 CPU** environment
used for real import/checkpoint readiness checks. It lists 57 external runtime/dev
distributions with wheel SHA-256; install the project itself separately with
`--no-deps -e .`. `cpu-wheels.json` preserves all wheel origins, including the
official CPU PyTorch wheel URLs. Installation steps are in [usage](../docs/usage.md).

This is a platform/interpreter-specific lock, not a Python 3.10–3.14 or Linux
compatibility claim. Other allowed Python versions need their own environment
resolution and readiness check. The original Python-3.11 targets were superseded
when the user authorized the locally installed interpreters and Colab 3.13.

`cuda-lock.txt` records the supplied, successful **Colab Linux x86_64 / Python
3.13.16 / Tesla T4 / CUDA 12.8** environment: 74 external distributions with exact
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
