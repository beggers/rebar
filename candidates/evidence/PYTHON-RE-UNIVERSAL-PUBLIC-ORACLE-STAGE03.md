# All three engines pass the expanded Python compatibility test

Status: **PASS** for independently written Rust, C, and Zig engines. This is a
public correctness result, not a speed measurement or a replacement for the
previously consumed hidden test.

The pinned reference is CPython **3.14.6**. The immutable version-one test
generates **8,192** cases from **16** expression families, **16** input and
buffer categories, and **32** seeded variants. Each case has **48** separately
checked observations. Python and each engine run in isolated processes.

| Preserved stage | Rust differences | C differences | Zig differences | Total comparisons | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| Initial separate runs | 693 | 368 | 355 | 1,179,648 | FAIL |
| First complete repaired run | 306 | 0 | 0 | 1,179,648 | FAIL |
| Final independently repaired run | 0 | 0 | 0 | 1,179,648 | PASS |

The final run completes **393,216** observations for each engine, with no
unexplained mismatch or worker failure. The first run records up to **256**
examples per engine; the intermediate run records **256** of its **306** Rust
differences and the digest of the complete mismatch stream. None of those
unrecorded examples are represented as individually classified.

The repairs are in the owned engines and their Python bridges. C and Zig now
preserve newline-sensitive and multiline matching, independently construct
Python's duplicate-group exception chain, and evaluate positional bounds in
Python's exact observable order. Rust preserves the same bound evaluation and
constructs the same nested duplicate-group exception without using another
regex engine.

## Immutable evidence

| Artifact | SHA-256 |
| --- | --- |
| Frozen compatibility oracle | `744876e5b8409b8d49982ccfb61d93a99f3e2d4fd64d0543b29b831bd26796a0` |
| Initial Rust failure | `2a02af3d1b6925aa3aa080a2576e4fd9fa3b1d9a123737f711eb55a866582f1b` |
| Initial C failure | `8391457aa874caf407bfa9d1629254f6148e2a2e4a3a70e5c86e72ee3e643ca2` |
| Initial Zig failure | `42940bd1824f5a10530bc951e5f1aa2ba00347b263453e155b47a77a034835ab` |
| First repaired, complete failure | `6fa4300fdd92eb96f1f8a30c3bbe55c3625bc08b49a3dfc28a56b605acb9f18e` |
| Final versioned oracle runner | `477c3f7e9955a9207b9345fc281705b6d643446b5d5c933009fa22a64b8d44ce` |
| Final complete passing report | `a7b6aea6e612de511990d446c8572aa4e1d3094f28ddd2b9f012b1083e73f208` |
| Refreshed 76-control source and native-library audit | `c78449b1153221bd0d17854c4f6682062392d19a04cfd0a424a1c6f3fa3478cb` |
| Refreshed 32-control isolated no-delegation audit | `c4605c8af5da805c099b1efb7f15e8390781768bb3014276b465a7712b4ed06b` |

The historical isolated-engine audit reports are preserved independently,
including their exact original fingerprints. The passing report covers all
**five** actually loaded native libraries and all **four** independently
owned implementation families. Neither audit asserts a reproducible compiler
build.

## Reproduce and inspect

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

"$PY" -I -B tools/python_re_universal_public_oracle_stage03.py --self-test

jq '{status, cases, total_comparisons, mismatches, comparison_complete,
     candidates: (.candidate_reports | with_entries(.value = {
       status: .value.status,
       checks: .value.checks,
       mismatches: .value.mismatches,
       comparison_complete: .value.comparison_complete
     }))}' candidates/evidence/python-re-universal-public-oracle-v3-all.json

sha256sum tools/python_re_universal_public_oracle_v1.py \
  tools/python_re_universal_public_oracle_stage03.py \
  candidates/evidence/python-re-universal-public-oracle-v2-all.json \
  candidates/evidence/python-re-universal-public-oracle-v3-all.json
```

Every compatibility report is exclusive-create. Running the same output
again correctly fails rather than overwriting preserved evidence. Current
speed, memory, the expanded public benchmark, and the fresh **65,536-case**
holdout remain **NOT MEASURED**.
