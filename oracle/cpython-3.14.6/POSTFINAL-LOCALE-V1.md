# Real-locale CPython compatibility: strict version one

Status: **PASS. Python, Rust, C, and Zig each pass all 146 original
selected CPython public tests, with zero skips, failures, crashes, or
timeouts.**

The exclusively created, complete
[four-engine result](evidence/postfinal-locale-v1-all.json) has SHA-256
`bc17ee74409543d1b57f3aee65088e990ab21ac83dc75ac46fbd1f97f04b6621`.
Its source-bound controller has SHA-256
`b87bbdcddef2d19a462e8c4b37bd159f6c3a30ea9b4fe5d9471eff1f51fbcb55`.

| Actual isolated engine | Official public tests passed | Skips | Failures, crashes, and timeouts |
| --- | ---: | ---: | ---: |
| Pinned CPython 3.14.6 | 146/146 | 0 | 0 |
| Independently implemented Rust | 146/146 | 0 | 0 |
| Independently implemented C | 146/146 | 0 | 0 |
| Independently implemented Zig | 146/146 | 0 | 0 |

The original CPython 3.14.6 test files, runner, manifest, **152** public
methods, **146** selected methods, and all eight named exclusions stay
unchanged. The six excluded methods and two excluded private test classes
are exactly those already frozen in [`manifest.json`](manifest.json).
No selected test may fail, skip, time out, or crash.

Previously, `ReTests.test_locale_caching` and
`ReTests.test_locale_compiled` could not run because the system did not
provide `en_US.iso88591`. The original tests really require both
ISO-8859-1 and UTF-8, including matching patterns compiled before a
locale change. UTF-8 alone, mocked locale behavior, and additional
waivers cannot establish correctness.

[`tools/postfinal_cpython_locale_oracle_v1.py`](../../tools/postfinal_cpython_locale_oracle_v1.py)
solves this without installing software or changing the system. It uses
the existing system `localedef`, frozen original upstream tests, and real
system character maps. Both locales are generated inside a unique,
private `/tmp` directory; every isolated child receives its exact
`LOCPATH`.

Equivalent private-locale preparation is:

```sh
locale_root="$(mktemp -d /tmp/rebar-postfinal-official-locale-v1-XXXXXXXX)"

/usr/bin/localedef --no-archive -f ISO-8859-1 -i en_US \
  "$locale_root/en_US.iso88591"
/usr/bin/localedef --no-archive -f UTF-8 -i en_US \
  "$locale_root/en_US.utf8"
```

The actual controller makes and removes only its own validated private
directory. If a real locale source, character map, compiler, or locale
is unavailable, it fails. It never simulates a locale or changes the
original official test source.

## Candidate-free controls

Run the synthetic controls without loading an engine, reading or writing
project evidence, compiling a locale, or measuring performance:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_cpython_locale_oracle_v1.py --self-test
```

## One-use production gate

Run this gate only after the separately passing, source-bound
version-five from-scratch and no-delegation audits exist. An explicitly
supplied matching version-four pair is recognized only while every
audited source and native binary remains unchanged:

```sh
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_cpython_locale_oracle_v1.py --audit \
  --source-audit candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json \
  --strict-audit candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json
```

The gate first checks the immutable objective, original official source,
original manifest, all **12** current candidate source fingerprints,
all **five** owned native binaries, both matching independence reports,
and the exact source of both audit controllers. It then proves the two
genuinely different byte locales using
the isolated pinned Python standard library. The unmodified official
oracle must pass **146/146**, with **zero skips**, first against Python
and then independently against Rust, C, and Zig. Every exact method
identity and result is retained and matched against Python's complete
baseline.

All four independent runs passed before the gate exclusively created:

```text
oracle/cpython-3.14.6/evidence/postfinal-locale-v1-all.json
```

The result retains every original per-method outcome, both previously
skipped locale methods, and the same immutable upstream method set.
The exact SHA-256 of its **146** selected original method identities is
`d33571d09a3a9cb428a84dece5af233e66267b831d3043c90e3ad77cb8de5178`.
The frozen original CPython manifest remains
`2c89ce37e474cb6f59d61f86ad810662b50b83bbdce3610c04523fe092688597`.
None of the six public-method waivers or two named private-class
waivers changed.

The separately verified
[version-five from-scratch proof](../../candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json)
has SHA-256
`42bd73acf6831b67df9a9873fa35c1882f2af09c41933774ba841d2290e6c198`.
The locale result binds this exact proof to the current
[version-five no-delegation proof](../../candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json),
all **12** current candidate sources, and all **five** current native
binaries.

The original official runner does not itself claim to poison every
stdlib regex reference in a nested subprocess. Engine independence is
established by the separately required current version-five source,
native-mapping, and no-delegation proofs. Runtime, memory, benchmark
results, and the final test remain **NOT MEASURED** or **NOT OPENED**.
