# Preserve the exact benchmarked native engines

Status: **PASS. All five original native libraries are preserved.**

The public 8,192-case benchmark measured five native libraries. Their
regular `.so` filenames are excluded by `.gitignore`; rebuilding an engine
would therefore destroy the original benchmarked bytes unless those bytes
are archived first.

## Original benchmarked libraries

| Engine role | Original bytes | SHA-256 |
| --- | ---: | --- |
| C engine | 159,464 | `6922d0869b67c82be9ae89a8f00c71777c04472d3606a33527bb13494326f18d` |
| Rust engine | 650,328 | `c6c09ae96e3a840dc7a62870b3f8c54f6ebc4d82537b319f77520175e84a3255` |
| Rust Python bridge | 136,096 | `81fc4c4a92005f0588dd9b811988587d4d421dd8e1102eebcab53f4deb27cd36` |
| Zig engine | 491,688 | `474dde0bfb23f107f21ec4834ce15dbd1b437841bd171698de623d1c03742988` |
| Zig Python bridge | 120,992 | `32dadc46281d13df784693f0785d4d149e6d3cd000aa3de6eb220a4a9ed50c9c` |

All five fingerprints independently agree with the original public
[benchmark manifest](manifest.json),
[results](evidence/postfinal-public-practice-v5-summary.json),
[independent replay](evidence/postfinal-public-practice-v5-integrity.json),
[76-check source audit](../../candidates/audits/FROM-SCRATCH-AUDIT.json),
and [32-check isolation audit](../../candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V1.json).

The [independently verified archive manifest](evidence/postfinal-public-v5-native-archive-v1.json)
has SHA-256
`136a64a89fed1dce245c3774539720beb171c660291d2ca0e1e1b6303115efd6`.
It authenticates all original benchmark, correctness, and audit proofs;
all **1,558,568** original native bytes; and the five deterministic,
timestamp-free gzip archives below. Their combined size is **563,840**
bytes. Each file was exclusively created and separately verified against
both its compressed fingerprint and the complete original native bytes.

| Preserved archive | Compressed SHA-256 |
| --- | --- |
| [C engine](evidence/native-archive-v1/vm-engine.elf.gz) | `9092fb16cffae6aaf0a4cc502aa554de07ad8f880c976066498f303de917d06e` |
| [Rust engine](evidence/native-archive-v1/rust-engine.elf.gz) | `02cdd2b97cd8d1a131c7bf911370075df2942ba0dd47f16fc0ecb5435cc5cd7a` |
| [Rust Python bridge](evidence/native-archive-v1/rust-bridge.elf.gz) | `1a3835d0533d17e71ac9ec189edc93735f9e9dee404e121f7abd29b98f4e12fd` |
| [Zig engine](evidence/native-archive-v1/zig-engine.elf.gz) | `32790f81839fb33c5a88bbfacfc3fa401a88ff07ff6e60bf45768c7db509f083` |
| [Zig Python bridge](evidence/native-archive-v1/zig-bridge.elf.gz) | `9d2ed66570b0dbad6d5cb0059812418654366a60d4cacf692939de32446e88e8` |

Archived bytes are historical evidence, not loaded Python extensions.
They do not prove a reproducible compiler build, active native memory
mappings, current correctness, or new speed. Restoring a historical runtime
would require a separate clean checkout of the original benchmarked source,
all five original filenames together, their original `0700` file modes,
and rechecked source and binary fingerprints. The Rust and Zig Python
bridges find their engines relative to their own location. The archiver
must never overwrite or automatically restore current engines.

Final holdout results, future optimization results, and a winner remain
**NOT MEASURED**.

## Verify the original archive

The archiver source has SHA-256
`49f9d32ff619aeb43dda5811f6f9cf3c66ce5ec819b06b74f0599c1bcf619101`.
Its **64** in-memory safety controls and complete five-file verification
can be repeated without overwriting or restoring an engine:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_public_native_archive_v1.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_public_native_archive_v1.py --verify
```

Archive verification does not read the current native-engine files. It
remains valid after future candidate changes.
