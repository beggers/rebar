# Complete the Python correctness reference before testing replacements

Status: **Python correctness oracle PASS; replacement qualification BLOCKED**.

This is an additive, separately verified phase-one transition. It does
not modify `GOAL.md`, the original compatibility matrix, the historical
version-2 certificate, the original Python test runner, any candidate,
or the unopened performance holdout.

## Exactly what passed

The frozen original CPython **3.14.6** compatibility matrix retains
exactly **31,237** case executions, **13** original test groups,
**13** named private CPython exclusions, **73** obligations, and
**34** crosswalk entries. The two independently recorded corrected
Python references agree on all **6,912** original public-type cases.

The separately preserved property and differential fuzz corpus
contains **8,244** cases, **19** case categories, **45** mapped
historical obligations, and **seven** unchanged seeds. Two genuinely
observed Python workers each ran the unchanged original
`tools/oracle_v2.py verify --module re`; each passed **8,244/8,244**
and exited successfully.

The two original result files share Python's reproducible **270**-byte
output but are different authenticated files with inodes **524693**
and **524692**. Their distinct actual process IDs, complete original
stdout, exit statuses, original module context, corpus, seed values,
and failure arrays are independently authenticated against the
**3,658**-byte, published two-worker report:

```text
8377e9c526a487c2e8838d7b8ba74e595b42d069f572bf7ed29f926f82d5b096
```

The additional **8,244** cases remain separate; **31,237** remains
the original denominator. No fuzz-private label is counted as one of
the original **13** named private exclusions. All corpus records are
verified with the existing genuinely bounded, **262,144**-byte
streaming verifier.

## What this authorizes

The Python-reference readiness gate is **PASS**. It authorizes
independently built, first-party native candidates and their
correctness tests. It does **not** claim a candidate is compatible.

The separate candidate-qualification gate remains **BLOCKED**. Its
seven genuine outstanding requirements are:

1. No replacement has passed all **31,237** original cases.
2. No replacement has passed all **8,244** supplemental cases.
3. The current public `import rebar as re` still fails its full contract.
4. Candidate callable-signature checks have not run.
5. A candidate has not passed the genuine full-size search requirement.
6. A candidate has not passed the genuine full-size substitution requirement.
7. Runtime proof that candidates never delegate matching is incomplete.

The first-party family inventory is **six**. Fully compatible
replacements: **zero**. The final **4,194,304**-case comparison
remains **NOT GENERATED** and **NOT OPENED**. Performance, memory,
confidence, and undefined behavior are **NOT MEASURED**.

The historical version-2 certificate correctly remains **BLOCKED**;
the new version-4 certificate records the actual, separately pushed
two-process reference and distinguishes a passing phase-one oracle
from the still-blocked candidate qualification.

## Reproduce without running a replacement

Independently fingerprint these three new owners:

```text
tools/verify_owned_p0_completeness_v4.py
oracle/phase1/P0-COMPLETENESS-V4.md
oracle/phase1/p0-completeness-v4.json
```

With the pinned CPython **3.14.6** executable, use both source-only
modes and repeat them in a clean environment:

```text
python3.14 -I -B tools/verify_owned_p0_completeness_v4.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

python3.14 -I -B tools/verify_owned_p0_completeness_v4.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Both runs must report phase-one readiness **PASS**, candidate
qualification **BLOCKED**, zero newly started reference or candidate
workers, **31,237** unchanged original cases, and the actual previously
recorded **8,244/8,244** two-worker Python reference. Neither command
starts a matcher, candidate, native compiler, timer, network request,
compressed archive, or holdout.
