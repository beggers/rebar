# Recheck that rebuilt matching engines are genuinely independent

Status: the independently produced version-seven source audit has
**PASSED**. The new strict independence audit and a successful rerun of
the complete original Python tests are **NOT RUN**. No synthetic
controller check, historical result, or previously passing native binary
qualifies a rebuilt implementation. Performance, memory, holdout
results, and any winner are **NOT MEASURED**.

## Preserve the real failure

The separately frozen official Python 3.14.6 controller and protocol are:

```text
tools/postfinal_cpython_locale_oracle_v2.py
e6858d00747645c6f81cad66e2d6ca957c374e88718abc356fc5367b5be100e1

oracle/cpython-3.14.6/POSTFINAL-LOCALE-V2.md
a515d2a81d8d02df523316d8315ca3617fe3f4330d33745f536ed15917ff20c5
```

The original upstream `ReTests.test_match_repr` exposed an actual Rust
native-match representation mismatch. Keep that genuine failure in the
separately created, never overwritten report:

```text
oracle/cpython-3.14.6/evidence/postfinal-locale-v2-rust-failures.json
```

Root has now genuinely and exclusively preserved that observed result;
its actual SHA-256 is:

```text
a77f47cbfb992aa9ae3ced5394bffb75575e6f305f0d2bd0fe2677092517654f
```

The source and protocol used to preserve it are:

```text
tools/postfinal_cpython_locale_v2_failure.py
42069714991730daff44351eb76ef2fe44478720eb0c51d76b9ea162600b96a5

oracle/cpython-3.14.6/POSTFINAL-LOCALE-V2-FAILURE.md
75e9a2709c7755de96ae23106db536a38bfd97a80fb37c5ea3f6a98139e26818
```

Never fabricate the failure, claim original stdout was retained, weaken the
146-test upstream denominator, claim that Rust passed, or hide the fact
that the C and Zig official suites were not run. The strict version-seven
audit must fail before reading production inputs or starting a worker if
that exact genuine failure is not pinned.

## Keep the actual version-six evidence as history

The previously passing source and no-delegation reports apply to their
exact old native binaries, not to rebuilt engines:

```text
tools/postfinal_from_scratch_audit_v6.py
77e7ea97f96280019b3be9abfeeb8fc6ff27ca6ecd13189e611586af5719c18f

candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V6.json
0314e3e5de3386d7c9c1e7f8fa4648554ff53cb53e3aafcecc4cb8e4923ddcbb

tools/postfinal_no_delegation_audit_v6.py
a936abe91d67169ea361b6770404ffe7bc925fdb3275aef854fbe12fe68a8649

candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V6.json
93f174f0861b0ee6e9feadf6e49bf222f0766b393ff74179219e65452b03d84f
```

Authenticate and preserve all four before a new audit. Do not replace,
modify, delete, or present them as evidence for changed C, Rust, or Zig
source files or native binaries.

## Independently verify the rebuilt engines

The new strict controller is
[`postfinal_no_delegation_audit_v7.py`](../../tools/postfinal_no_delegation_audit_v7.py).
It requires the independently produced:

```text
tools/postfinal_from_scratch_audit_v7.py
defa306e47a0d325af7d4c7fabb54324f6cb6d4653a494c46846838f5e2cf487

candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json
efae1f94fb06a1eabbab352794410c4d8e20a78202dcbf769b08ff9c7cee130a
```

Root pinned the source only after its controller was finalized and the
report only after its genuine, exclusively created source audit passed.
The report verifies 12 owned sources, five native binaries, three native
families, four pipelines, 48 real pickle round trips, and six actual
owned-type match-representation checks. It is a passing source audit,
not a passing strict audit or a rerun of the official Python test suite.
The source report must independently prove all 12 owned candidate source
files, all five real native binaries, three actual native matching
families, four separate source pipelines, no external Python or Rust
regular-expression packages, all 48 ordinary standard-library pickle
round trips, and six successful native-owned match-representation
observations.

Rerun the unchanged original 32 no-delegation controls and inherit all 76
original native-isolation controls. Prove the real Rust and Zig bridge
runpaths are exactly `$ORIGIN`; the three engine runpaths must be empty.
Reject foreign dynamic dependencies, calls to Python `re` or `_sre`,
third-party matchers, another candidate, all five `ctypes` native-loader
aliases, and the `enum`/cached-JSON-decoder bypass. Native fingerprints
and package manifests in the source and strict results must agree
exactly.

Run three fresh, isolated, guarded candidate workers. Each must verify
both genuinely owned native `Pattern` and `Match` types, execute 16 real
ordinary `pickle.dumps`/`pickle.loads` generic-alias round trips, and
perform the original `abracadabra` matching example with both `str` and
`bytes`. Confirm the actual native match representation uses the real
owned type and exact span; reject hardcoded `re.Match`, imported
matchers, synthetic answers, cross-family native mappings, and changed
match text. All six fresh strict representations must match the
independent version-seven source observations.

The sole allowed output is atomically and exclusively created:

```text
candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json
```

## Check the controller without running candidates

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_no_delegation_audit_v7.py --self-test
```

The synthetic check may inspect only in-memory test objects. Block and
count all file access, subprocesses, candidate imports, clock samples,
entropy, evidence writes, and performance or holdout access. Its passing
result proves controller safeguards only; it never represents a real
candidate audit.

Run an actual audit only after this source and protocol are committed and
pushed, the genuine prior failure is retained, and root pins both
independently produced version-seven source fingerprints. Until that
actual one-use audit has passed, all rebuilt candidates remain
**NOT QUALIFIED**, and performance remains **NOT MEASURED**.
