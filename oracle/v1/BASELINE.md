# CPython correctness and performance baseline

## Gate result

The version-selection and source-integrity gate passes. Interpreter build
provenance and all behavioral gates remain **NOT MEASURED** until their own
chunks are committed.

## Selection

The release snapshot is 2026-07-21 UTC. CPython 3.14.6, released 2026-06-10,
was the latest stable CPython feature release on that date. CPython 3.15.0b4
was a pre-release; the next 3.14 maintenance release was scheduled after the
snapshot.

Authoritative sources:

- <https://www.python.org/downloads/>
- <https://www.python.org/downloads/source/>
- <https://www.python.org/downloads/release/python-3146/>
- <https://peps.python.org/pep-0745/>
- <https://peps.python.org/pep-0790/>

## Artifact lock

- Archive: `Python-3.14.6.tar.xz`
- URL: <https://www.python.org/ftp/python/3.14.6/Python-3.14.6.tar.xz>
- SHA-256: `143b1dddefaec3bd2e21e3b839b34a2b7fb9842272883c576420d605e9f30c63`
- Sigstore bundle: <https://www.python.org/ftp/python/3.14.6/Python-3.14.6.tar.xz.sigstore>
- SPDX SBOM: <https://www.python.org/ftp/python/3.14.6/Python-3.14.6.tar.xz.spdx.json>
- Annotated Git tag: `v3.14.6` (`8594736f5057fdc979d42d2135895d56274589a8`)
- Peeled source commit: `c63aec69bd59c55314c06c23f4c22c03de76fe45`

The downloaded archive passed both `sha256sum` and `xz -t` locally. The
machine-readable lock is [`baseline.json`](baseline.json).

## Reproducible build contract

Build from the verified archive with:

```sh
./configure \
  --prefix=/absolute/path/to/cpython-3.14.6 \
  --with-ensurepip=no \
  --enable-optimizations \
  --with-lto=full
make -j8
make altinstall
```

`make altinstall` is mandatory so the build cannot replace a system Python.
The absolute installed interpreter is used for both the stdlib oracle and
every benchmark process. The standard-library baseline is the unmodified
`re` shipped in this archive.

Each frozen run must set `PYTHONHASHSEED=0`, `LC_ALL=C.UTF-8`, `TZ=UTC`, and
start a fresh interpreter with `-I -S -E -B`. Candidate and oracle work occurs
in separate `exec`-started processes; no candidate process may inherit a
loaded `re` or `_sre` module.

## Denominator policy

This chunk freezes no behavioral obligation or benchmark denominator. Those
denominators remain 0/0 and **NOT MEASURED** until their dedicated frozen
manifests land. A future release never silently changes this v1 pin.
