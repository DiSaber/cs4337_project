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

`cuda-lock.txt` has not been created: no Linux GPU runtime was available to verify
an actual environment. Follow the [Colab instructions](../docs/colab-setup.md),
return the real environment evidence, then finalize that lock with exact versions
and wheel provenance. T004 remains partially complete until then; never install
the Windows CPU lock in Colab.
