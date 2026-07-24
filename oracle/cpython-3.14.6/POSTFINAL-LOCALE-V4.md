# Run every original public Python regex test

Status: **PROSPECTIVE. OFFICIAL REFERENCES NOT RUN. CANDIDATES NOT
RUN.** Source-only controls are not official test results. There is no
version-four success report or compatibility-qualified candidate.
Performance and memory results are **NOT MEASURED**.

The historical version-three 146-method result used a synthetic
`test.support` shim. That shim unconditionally skipped the real
large-memory and CPU decorators and the inherited candidate runner
rewrote the original test imports. Preserve this historical result and
its exact 146-method denominator, but never describe it as a run with
authentic upstream test support or unchanged candidate test source.
Version four instead requires all **152** genuine public methods, the
real complete upstream support tree, and untouched source.

## Freeze the real CPython source

Use the exact stable CPython 3.14.6 interpreter and these actual,
unmodified upstream files:

```text
oracle/cpython-3.14.6/test_re.py
879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2

oracle/cpython-3.14.6/re_tests.py
ec04a2b2a77338d20b37d931693c7e588a2896d3c73c7b4b47973e24c13b5aab

/tmp/rebar-cpython/Python-3.14.6.tar.xz
143b1dddefaec3bd2e21e3b839b34a2b7fb9842272883c576420d605e9f30c63

complete official Lib/test/support tree: 26 actual Python source files
6cd13337b46bd6a53a32ac0c557da79b0ddd536ac82be885cc57be77e80f1632

exact complete 152-public-method AST matrix
5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a
```

Count actual methods, not class names or approximations:

| Original test class | Actual methods | Scope |
| --- | ---: | --- |
| `ReTests` | 139 | Public; all required. |
| `PatternReprTests` | 11 | Public; all required. |
| `ExternalTests` | 2 | Public; both required. |
| `DebugTests` | 4 | Named private waiver: CPython-only internal-opcode disassembly. |
| `ImplementationTest` | 9 | Named private waiver: private CPython compiler, `_sre`, and implementation internals. |
| Total actual original methods | **165** | **152 public; 13 in two private classes.** |

There are exactly two named private class waivers. There are **zero
public method waivers**. The source controller explicitly freezes all
152 public method identities, source order, original line numbers, and
individual original-method AST hashes. No bounded lookalike, extracted
assertion, property case, mock, synthetic record, alternative method,
or previous 146-method result counts toward 152.

`test.re_tests.tests` initially contains exactly **400** real tuples.
The same original file then executes one genuine `tests.extend(...)`
with **three** further real locale-related tuples. The complete
upstream corpus therefore contains **403**, not 400. Keep
`ExternalTests.test_re_tests` and its unchanged original fixture.

`ExternalTests.test_re_benchmarks` is also an original public unittest
method. Despite its inherited name, this method makes ordinary
matching correctness assertions on **11** real upstream fixture
pairs. Check that the actual loaded fixture still has all 11 pairs,
and that the actual loaded `test.re_tests.tests` still has all 403
tuples immediately before each original external-test method. Running
these original correctness assertions is not the separate project
performance oracle. Do not remove either method, execute an
independent timing suite, or describe correctness as measured speed.

## Include all six previously omitted public methods

Run the exact original methods and retain their actual outcomes:

1. `ReTests.test_re_groupref_overflow` must execute its real
   `from re._constants import MAXGROUPS`. A native candidate needs an
   independently owned compatible constant and package surface. It may
   not secretly import or use the standard-library matching engine.
2. `ReTests.test_large_search` retains its original
   `@bigmemtest(size=_2G, memuse=1)` and real two-gibibyte index.
3. `ReTests.test_large_subn` retains its exact original
   `@bigmemtest(size=_2G, memuse=16 + 2)`. Its declared allocation budget
   is **38,654,705,664 bytes**, or **36 GiB**. A smaller substitute,
   unstated resource skip, concurrent oversized worker, or host memory
   estimate is not a pass. The actual upstream decorator defaults to
   `dry_run=True`. With `real_max_memuse=0` it can quietly call the
   original method with **5,147** items and report `PASS`. Explicitly
   set the real upstream memory limit to `40G`, disable its optional
   external watchdog using upstream `support.verbose = 0`, lock to one
   isolated worker, and retain the profiled, actually delivered
   `2,147,483,648` size for **both** original big-memory methods.
4. `ReTests.test_search_anchor_at_beginning` retains its genuine
   `@requires_resource('cpu')`, ten-million-character original
   subject, upstream `Stopwatch`, and exact `0.1`-second assertion. An
   unavailable CPU resource, an actual upstream skip, or a missed
   threshold is not a pass. This upstream correctness method is
   distinct from the frozen project performance oracle.
5. `ReTests.test_regression_gh94675` retains the original
   multiprocessing process, genuine compiled pattern and substitution,
   `test.support.SHORT_TIMEOUT`, and exact upstream skip condition.
6. `ReTests.test_memory_leaks` retains the original
   `@unittest.skipUnless(hasattr(re.Pattern, '_fail_after'),
   'requires debug build')`. The currently pinned release does **not**
   provide that private debug-only hook. Its honest standard-library
   outcome is consequently **SKIP**, not PASS. Preserve this public
   method, its real decorator, exact `requires debug build` reason,
   and the named `named-private-debug-condition` classification.
   This is one explicitly disclosed private-hook applicability
   condition, not a public-method waiver. A standard release can
   therefore establish **151 actual applicable passes out of 152
   retained original records**, with precisely one named private
   condition. Record debug-build coverage as **NOT RUN**. Do not say
   that the original method passed or that a debug build was tested.

A companion bounded resource, anchor, process, or memory control may
be helpful later. Freeze and label any such check separately. It is
never an executed original upstream method and never changes an
official PASS, SKIP, failure, or denominator.

## Require authentic fixtures and current-build provenance

The pinned installed release does not bundle `test.support`. The real
CPython 3.14.6 source archive has now been independently authenticated
against the original frozen source-distribution hash. Its extracted
`Python-3.14.6/Lib/test/` contains the exact original `test_re.py`,
`re_tests.py`, package `__init__.py`, and complete 26-file
`test/support/` tree. Independently hash the archive, both test files,
`test/__init__.py`, `test/support/__init__.py`,
`test/support/warnings_helper.py`, and every support Python source.
The frozen whole-tree hash uses each sorted support-relative path,
one NUL byte, its complete real bytes, and another NUL byte. Load the
real official `test.support` and `test.re_tests` through the exact
authenticated extracted `Lib` path.

Reject `types.ModuleType` support shims, unconditional fake resource
decorators, replaced warning helpers, `.replace()` on the original
source, and injected alternative test cases. Check that both original
resource decorators actually belong to `test.support`. The genuine
upstream default `use_resources=None` **enables** the CPU resource;
do not report it as disabled or require an invented resource list.

In a guarded native role, import the real official support under the
standard-library regex first; then temporarily expose the audited
candidate as `sys.modules['re']` while importing the exact unchanged
upstream test source. The original `from re import Scanner` must
resolve normally. The official harness may expose only the already
authenticated nonmatching numeric `MAXGROUPS` constant as
`re._constants`; it must never make Python's matching parser,
compiler, executor, or `_sre` available to a candidate. Set the real
multiprocessing start method to `fork`, retain actual process startup
and upstream `SHORT_TIMEOUT=30.0`, and never alter the regression.

Require both genuinely generated private ISO-8859-1 and UTF-8 locales
for each original role; preserve the actual
`ReTests.test_locale_caching` and `ReTests.test_locale_compiled`
observations. Independently authenticate the genuinely passing
from-scratch and no-delegation source audits, refreshed current-build
edge and deep proofs, and **three actual passing** source-bound
version-seven Rust, C, and Zig campaign reports. None of the three
campaign hashes is currently published or a success.

Preserve, but do not qualify, the genuine first current-build campaign
failure:

```text
candidates/evidence/rust-v8-rust-postfinal-locale-v7-sealed-campaign-first-failure.json
62aba93fa8bdd6df7be93199aea6f58be7b24c095750c520179e96b98084b75a
schema: rebar-postfinal-campaign-v7-first-current-build-failure-v1
phase: candidate-edge-proof-validation-before-first-campaign-stage
successful campaign stages: 0
```

The version-four source-only controller records these supplied frozen
incident identifiers. Its self-test never opens, reads, or validates
the incident file. Only a future separately authenticated production
preflight can establish that the actual incident has the declared
hash. The failed current-build attempt is never a successful campaign
or an original method record.

## Preserve every real official observation

The four required independent roles are `stdlib`, `rust`, `vm`, and
`zig`. Each role must run the unchanged upstream test class and retain
exactly **152** ordered, source-bound original public method records.
Every record retains its actual identity, exact frozen method-body
hash, and original `PASS`, `SKIP`, `FAIL`, `ERROR`, `TIMEOUT`, or
`CRASH`. A skipped or failed method retains its actual reason; it
cannot be omitted or silently converted into a success.

The release-build passing report requires all four roles to
independently retain:

```text
original public methods recorded: 152
applicable original methods:      151
actual passes:                    151
actual skips:                       1
named private debug skips:          1
unexplained skips:                  0
failures:                           0
errors:                             0
timeouts:                           0
crashes:                            0
public method waivers:              0
original corpus cases:            403
debug-build coverage:             NOT RUN
```

This is **608** retained actual role-method observations, comprising
**604** executed applicable original passes and **four** truthfully
retained named private debug-condition skips; the historical shim
suite had 584 selected observations. Any different public skip,
undelivered original size, failure, timeout, unsupported locale, or
missing native guard is **BLOCKED**. An optional authentic debug build
must actually pass **152 of 152**; it is never inferred from the
release. Never claim that the release ran 152 passing methods or
covered users of private CPython debug hooks.

Native roles must independently prove their actual owned matching
engines, package surfaces, source-bound native identities, fresh
locales, and no delegation to Python `re`, `_sre`, an external package,
or another candidate. Run the standard-library reference separately.
The synthetic controller never loads or starts a candidate.

The genuine reference is separately and exclusively retained in:

```text
oracle/cpython-3.14.6/evidence/postfinal-locale-v4-self-oracle.json
schema: rebar-postfinal-cpython-full-public-locale-v4-self-oracle
```

The only prospective complete passing four-role result is:

```text
oracle/cpython-3.14.6/evidence/postfinal-locale-v4-all.json
schema: rebar-postfinal-cpython-full-public-locale-v4
```

An actual unsuccessful standard-library reference has its own
exclusive failure path:

```text
oracle/cpython-3.14.6/evidence/postfinal-locale-v4-self-oracle-failures.json
```

An actual unsuccessful native role has a separately named failure
path:

```text
oracle/cpython-3.14.6/evidence/postfinal-locale-v4-failures.json
```

No real reference, role, complete report, or failure report exists or
is created by the source controls. The support archive and complete
tree have real independently verified hashes; do not replace those
real values with fake missing-manifest blockers. Keep the refreshed
current-build edge/deep proofs and all three genuine campaign report
hashes at `None` until actually produced. Supply the actual frozen
source and protocol hashes externally after their focused commit and
push; a source file cannot safely contain a hash of itself.

## Run source-only controls

The complete additive source is
[`postfinal_cpython_locale_oracle_v4.py`](../../tools/postfinal_cpython_locale_oracle_v4.py).
Run only:

```text
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_cpython_locale_oracle_v4.py --self-test
```

The controls read the two pinned genuine official repository source
files and independently authenticate the actual pinned source
archive and all 26 real extracted support Python modules. They
inspect the real source AST, all 165 actual methods, all 152 frozen
public identities, all 13 genuinely private methods, exact original
resource decorators, the 403 real corpus cases, the default 5,147
dry-run risk, and separately labeled in-memory poison records. They
do not materialize an official report, load a candidate, launch a
native worker, compile a locale, allocate a large subject, sample a
clock, inspect performance or holdout data, or execute an official
method.

A safe, source-only prerequisite diagnosis is:

```text
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_cpython_locale_oracle_v4.py --preflight
```

The diagnosis returns **BLOCKED** and a nonzero exit until all
genuine current-build prerequisites exist. It never reads an evidence
report, starts a worker, writes a file, or treats a synthetic control
as an official observation.

## Strictly ordered real production

These commands are implemented but **NOT RUN**. They fail before
launching a worker unless the externally supplied controller/protocol
hashes match the actually committed source, the genuine archive and
26-file tree still authenticate, refreshed current-build edge/deep
proofs pass, all three real 22-stage campaigns independently qualify,
and the original first campaign failure remains preserved.

Only after the source and protocol are frozen, committed, and pushed,
publish their actual hashes. Start the one genuinely isolated,
exclusive-memory standard-library reference first:

```text
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_cpython_locale_oracle_v4.py --self-oracle \
  --source-sha256 "$V4_SOURCE_SHA256" \
  --protocol-sha256 "$V4_PROTOCOL_SHA256"
```

Independently commit, push, and pin the resulting genuine reference
before starting candidates. Only then run each separately guarded
native worker one at a time:

```text
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_cpython_locale_oracle_v4.py --candidate all \
  --source-sha256 "$V4_SOURCE_SHA256" \
  --protocol-sha256 "$V4_PROTOCOL_SHA256" \
  --reference-sha256 "$V4_REFERENCE_SHA256"
```

`--candidate rust`, `--candidate vm`, and `--candidate zig` are also
actual isolated role modes. Every output is exclusively created;
nothing overwrites prior official evidence. A real failed worker must
retain its original failure instead of fabricating missing method
records. Never execute a 40-GiB worker while another is active.

The final gate is all **152 actual original method identities** per
role, exactly **151 genuine applicable passes plus one explicitly
named private-hook skip**, the actual two-gibibyte delivered inputs,
authentic support, fresh locales, exact upstream CPU and process
requirements, and zero unexplained mismatches or public-method
waivers. An authentic full debug build, if separately run, has the
stronger 152-pass gate. Nothing in this correctness stage establishes
holdout speed: performance remains **NOT MEASURED**.
