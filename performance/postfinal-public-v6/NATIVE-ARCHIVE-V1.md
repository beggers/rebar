# Preserve the exact engines from the current comparison

Status: **PASS. All five benchmarked native libraries are independently
archived and verified.**

The [8,192-case public comparison](RESULTS.md) measured these exact C,
Rust, and Zig engines and their Python bridges. Preserve the actual
binary bytes before changing the rejected Rust engine.

| Benchmarked native library | Original SHA-256 | Original bytes | Archived SHA-256 |
| --- | --- | ---: | --- |
| C engine | `6922d0869b67c82be9ae89a8f00c71777c04472d3606a33527bb13494326f18d` | 159,464 | `9092fb16cffae6aaf0a4cc502aa554de07ad8f880c976066498f303de917d06e` |
| Rust engine | `83394c5c3b5d9e9d98c8474aac60ca5a81517dc7ec7c53b3b625e6ed0a04c165` | 651,024 | `b5d856bb56b45e1e7874fabd19b864afed1b123281c9da6ecc3ae4707fa25741` |
| Rust Python bridge | `81fc4c4a92005f0588dd9b811988587d4d421dd8e1102eebcab53f4deb27cd36` | 136,096 | `1a3835d0533d17e71ac9ec189edc93735f9e9dee404e121f7abd29b98f4e12fd` |
| Zig engine | `474dde0bfb23f107f21ec4834ce15dbd1b437841bd171698de623d1c03742988` | 491,688 | `32790f81839fb33c5a88bbfacfc3fa401a88ff07ff6e60bf45768c7db509f083` |
| Zig Python bridge | `32dadc46281d13df784693f0785d4d149e6d3cd000aa3de6eb220a4a9ed50c9c` | 120,992 | `9d2ed66570b0dbad6d5cb0059812418654366a60d4cacf692939de32446e88e8` |

Each archive is deterministic gzip with compression level **9**, no
embedded filename, and a zero timestamp. The
[source-bound archive manifest](evidence/postfinal-public-v6-native-archive-v1.json)
has SHA-256
`01420e3328ba7b72a3edfd1a98dcfa1a4c0f285390dd88c6c4d2ca15a8ca149e`.
It binds all five archived files to the
[frozen benchmark](manifest.json),
[complete measurements](evidence/postfinal-public-practice-v6-summary.json),
[independent replay](evidence/postfinal-public-practice-v6-integrity.json),
and both original version-two independence audits.

The source actually benchmarked has Rust SHA-256
`398773b8542c88cfc55fe13ceac1e84a00155217b76b8461ddf9704d2f6c82c5`.
Verification reads that historical fingerprint from the frozen benchmark;
it does not require the current Rust source or current native engine to
stay unchanged. The
[earlier five-library archive](../postfinal-public-v5/NATIVE-ARCHIVE-V1.md)
remains separate. Its original Rust binary is
`c6c09ae96e3a840dc7a62870b3f8c54f6ebc4d82537b319f77520175e84a3255`,
not the Rust binary measured here.

## Preserve the first failed publication

The first archive attempt correctly created all five exclusive gzip files,
then rejected its unpublished manifest: the pinned Python-version tuple
had not yet been normalized into its JSON list representation. No
compressed file was corrupted, replaced, or removed.

Correct the representation and independently recheck every compressed
byte, original binary, frozen proof, directory entry, and archive source.
The explicit `--resume` mode exclusively creates only the missing
manifest. Its self-test passes **129** new checks plus **64** original
checks, including missing, extra, duplicated, substituted, and
interrupted archives. Both the resumed archive and the original
five-library archive independently verify.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_public_native_archive_v2.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_public_native_archive_v2.py --verify
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_public_native_archive_v1.py --verify
```

Preserving historical bytes does not prove that an archive is currently
loaded, that its build is reproducible, or that a newer engine is correct
or faster. Native memory remains **NOT MEASURED**. The **65,536**-case
final test remains **NOT OPENED**.
