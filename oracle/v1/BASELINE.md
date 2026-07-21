# Correctness baseline v1

The oracle and later performance baseline are pinned to **CPython 3.14.6**, the latest stable feature-series maintenance release checked on 2026-07-21. Python 3.15 is still a pre-release. The authoritative references are the [3.14.6 release page](https://www.python.org/downloads/release/python-3146/) and the [3.14 `re` documentation](https://docs.python.org/3.14/library/re.html).

The official source archives are pinned by SHA-256:

- `Python-3.14.6.tar.xz`: `143b1dddefaec3bd2e21e3b839b34a2b7fb9842272883c576420d605e9f30c63`
- `Python-3.14.6.tgz`: `74d0d71d0600e477651a077101d6e62d1e2e69b8e992ba18c993dd643b7ba222`

The Linux runtime used to freeze this oracle is Astral's reproducible, stripped build `cpython-3.14.6+20260623-x86_64-unknown-linux-gnu-install_only_stripped`. Install it in an isolated directory with:

```sh
UV_PYTHON_INSTALL_DIR=/tmp/rebar-cpython UV_CACHE_DIR=/tmp/rebar-uv-cache uv python install 3.14.6 --no-progress
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
"$PY" --version
```

The measured runtime reports `CPython 3.14.6 (main, Jun 23 2026, 15:18:23) [Clang 22.1.3]`, Unicode database `16.0.0`, 64-bit x86-64 Linux/glibc 2.39. Its executable SHA-256 is `255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016`; `libpython3.14.so.1.0` is `a45d463c0110b0ddc9258c1eec7cc52533622421ed9f93a600f8b2c09376de47`.

No older interpreter is an oracle. Candidate and performance processes must use this same pinned runtime.
