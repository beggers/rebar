# Recheck the original Python tests against all repaired engines

Status: **NOT RUN.** The current C, Rust, and Zig engines have not passed
this new official compatibility gate. No engine is qualified by a
historical result, a synthetic controller check, or a pickle smoke test.

## What the gate must check

Use the already frozen, unmodified Python 3.14.6 upstream test files,
manifest, and official runner. Their **152** public methods, **146**
selected methods, all **403** original regular-expression corpus cases,
and **eight** named exclusions must remain exactly as first recorded.
Run the identical selected methods separately against:

1. Pinned, unmodified CPython 3.14.6.
2. The independently implemented Rust engine.
3. The independently implemented C engine.
4. The independently implemented Zig engine.

Every engine must really pass **146/146** original tests, including the
upstream method running all **403** corpus cases. Failures, crashes,
timeouts, additional waivers, skipped tests, changed inputs, and altered
denominators are forbidden. Keep the complete individual method records
for each engine.

The two official locale tests must really run. Generate genuine
`en_US.iso88591` and `en_US.utf8` locales using the system `localedef`
and original character maps in the runner's own private temporary
directory. Prove both with isolated Python before running the unchanged
official tests. Preserve the official checks that reuse patterns
compiled before the locale changes. Do not mock or skip either locale.

## Independence must be freshly proved first

The controller is
[`tools/postfinal_cpython_locale_oracle_v2.py`](../../tools/postfinal_cpython_locale_oracle_v2.py).
It accepts only the exact real version-six source and no-delegation
reports. The actual, root-created source controller and report are:

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

Both separately produced version-six audits have genuinely passed;
their exact controller and one-use report hashes are now pinned. A
missing, stale, guessed, or substituted hash still fails before any
locale compiler, candidate, reference worker, or official test starts.
Historical version-five audits, mixed versions, changed source files,
substituted native libraries, and matching engines supplied by Python,
another candidate, or an external regex package cannot qualify the new
implementations.

Both actual reports must independently bind
the same **12** owned candidate source files, **five** real native
binaries, three distinct native matching engines, and four independent
source pipelines. Both must also prove all **48** ordinary
standard-library pickle round trips for the actually owned public
pattern and match types. The fresh no-delegation audit must preserve
all native-loader, cross-family, cached JSON-regex, and external-package
guards. The official runner, test files, manifest, and eight original
waivers are not rewritten.

## Preserve the previous result as history

The [version-one official result](evidence/postfinal-locale-v1-all.json)
is genuine evidence for its old, version-five-audited native builds. Its
unchanged SHA-256 is
`bc17ee74409543d1b57f3aee65088e990ab21ac83dc75ac46fbd1f97f04b6621`.
Its [original controller](../../tools/postfinal_cpython_locale_oracle_v1.py)
has SHA-256
`b87bbdcddef2d19a462e8c4b37bd159f6c3a30ea9b4fe5d9471eff1f51fbcb55`.

Neither result proves that the changed C, Rust, or Zig implementation
still passes. Version two verifies and preserves both original files,
records them explicitly as historical, and never overwrites their
source or result.

## Candidate-free controller checks

The prospective controls inherit at least **73** original official
poison checks and reject stale or incomplete audits, forged ownership,
missing corpus coverage, unsafe output paths, external matchers, and
native substitutions. They use only synthetic, in-memory documents;
file access, subprocesses, candidate imports, clock samples, entropy,
locale generation, and evidence writes are blocked and counted.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_cpython_locale_oracle_v2.py --self-test
```

A passing self-test does **not** run or qualify any candidate.

## One-use official compatibility gate

Run this command **only after** the version-two controller and this
protocol have been committed, both fresh version-six audits have
genuinely passed, and their four exact source and report hashes have
been pinned:

```sh
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_cpython_locale_oracle_v2.py --audit
```

The only permitted production output is the exclusively created:

```text
oracle/cpython-3.14.6/evidence/postfinal-locale-v2-all.json
```

Until a genuine four-role run has created that result, official
compatibility for the rebuilt engines remains **NOT RUN**. No speed,
memory, final-test result, or winner is measured or implied.
