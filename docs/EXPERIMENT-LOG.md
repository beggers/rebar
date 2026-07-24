# Experiment log

This log preserves the chronological work behind the concise [README](../README.md). Every linked report keeps its raw measurements, generated charts, losses, and reproduction details.

Historical entries describe the state when they were written. In particular,
older statements that the final benchmark was sealed or had not yet run are
historical: that benchmark subsequently opened exactly once, found the Zig
`split` mismatch recorded below, and remains irreversibly **FALSIFIED**.

## Freeze the rebuilt engines' complete official Python tests

After pushing both actual independence reports and the genuine
three-engine generic-alias comparison, independently inspect the new
[official Python compatibility protocol](../oracle/cpython-3.14.6/POSTFINAL-LOCALE-V2.md)
and [controller](../tools/postfinal_cpython_locale_oracle_v2.py).
Their respective SHA-256 values are
`a515d2a81d8d02df523316d8315ca3617fe3f4330d33745f536ed15917ff20c5`
and `e6858d00747645c6f81cad66e2d6ca957c374e88718abc356fc5367b5be100e1`.

Freeze the original CPython **152** public methods, the exact
**146** selected tests, all **403** upstream regular-expression corpus
patterns, the exact **eight** named private or resource exclusions,
and both genuinely compiled locale tests. Require independent
processes for unmodified Python, Rust, C, and Zig.

Independently run the candidate-free controller self-test:
**113/113 PASS**, retaining all **73** previous controls and starting
no candidates, official tests, locales, clock, or workers. Separately
verify all four real V6 audit fingerprints, all **12** exact source
files, all **five** native binaries, all **48** pickle checks, and the
genuine historical-only original official result. Preserve the
historical reports without reusing them as proof of new correctness.

The actual full official test is **NOT RUN** at this checkpoint.
Commit and push this frozen source and protocol before starting the
one-time real four-role official test.

## Verify all three repaired engines against the failed Python contract

First push the independently passing Python reference in `e991d991`.
Then run the actual three-candidate correctness command once:

```sh
env PYTHONDONTWRITEBYTECODE=1 \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/python_re_generic_alias_public_oracle_stage12.py \
  --candidate all
```

The exclusively created
[passing all-engine report](../candidates/evidence/python-re-generic-alias-public-oracle-v12-all.json)
has SHA-256
`6b0188e22f80a64e79252660d6b308d16d7a38ec01c45013bf67484b8d49be8c`.
Rust, C, and Zig each pass all **128/128** original public type and
serialization cases. All **384/384** candidate observations match the
actual two-process Python reference, with **zero** failures.

Every independent process verifies the genuinely audited native binary,
public pattern and match owner, Python-matcher block, cross-candidate
block, external-package block, and all five native-loader blocks.
The original **16** Stage 11 Rust failures remain unchanged and
recorded. No benchmark, memory sample, hidden case, or final case
is accessed.

The complete official Python test suite remains **NOT RUN**. Expanded
performance remains **NOT FROZEN** and **NOT MEASURED**.

## Verify two independent Python references for the repaired contract

Commit and push the frozen Stage 12 source and protocol in `2715e306`
before starting either reference. Run the exact real two-reference
command once:

```sh
env PYTHONDONTWRITEBYTECODE=1 \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/python_re_generic_alias_public_oracle_stage12.py \
  --self-oracle
```

The actual
[passing two-Python reference](../oracle/cpython-3.14.6/evidence/public-generic-alias-v12-self-oracle.json)
has SHA-256
`b235bd68afbbfa9b8e7e046d0e007385617c976c6e5a5f5b614cc7d93b891aff`.
The two separately started CPython 3.14.6 workers agree on all
**128** frozen cases and **256/256** observations, with **zero**
mismatches. The complete source, protocol, matrix, and both actual
V6 independence proofs remain hash-bound. The reference starts no
candidate and performs no timing.

All three rebuilt Stage 12 candidate runs are **NOT RUN** at this
baseline checkpoint. Commit and push the genuine Python reference
before starting any candidate.

## Freeze the repaired public Python type contract

First commit and push both real V6 source and no-delegation audits.
Preserve the original Stage 11 passing two-Python baseline and all
**16** real Rust pickle failures. Never reuse the earlier candidate
results to qualify modified source files.

Independently verify the new
[128-case Stage 12 protocol](../oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V12.md)
and [source](../tools/python_re_generic_alias_public_oracle_stage12.py).
Their respective SHA-256 values are
`1cec5253aabb5464c16d0de461bdd11463ddf11fafea9da6347b8a0af3d30cb1`
and `361e080a0475f5ee7fd7d5da0386a4e2443775069aadca84e053bac357554aaa`.
The **128** exact frozen obligations retain all four original groups;
the fresh matrix is
`65c93cfbbc337ecd762a6b201bacc77e35eb72d201a9e8bc222d730714885aef`.

The candidate-free synthetic design passes **86/86** safety controls.
A separately executed real source-only preflight verifies both genuine
V6 audit controllers and reports, all **12** current production sources,
all **five** native binaries, and the real saved Stage 11 Rust failure.
Neither check starts a Python reference, candidate worker, benchmark,
or final test.

The Stage 12 two-Python reference and all three candidates remain
**NOT RUN** at the design checkpoint. Freeze and push this protocol
and source before starting the actual two-reference self-oracle;
separately push its real results before testing any candidate.

## Verify the repaired engines cannot delegate matching

Commit and push the independent-execution audit design in `b2196421`
before running it. Its exact source SHA-256 is
`a936abe91d67169ea361b6770404ffe7bc925fdb3275aef854fbe12fe68a8649`.
Both the root and an independent reviewer verify **75/75** new,
candidate-free controls and all **676** inherited malicious-input
controls.

Run the real, separately guarded audit exactly once:

```sh
env PYTHONDONTWRITEBYTECODE=1 \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_no_delegation_audit_v6.py --audit
```

The exclusively created
[passing no-delegation evidence](../candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V6.json)
has SHA-256
`93f174f0861b0ee6e9feadf6e49bf222f0766b393ff74179219e65452b03d84f`.
It is bound to the genuine from-scratch report
`0314e3e5de3386d7c9c1e7f8fa4648554ff53cb53e3aafcecc4cb8e4923ddcbb`,
all **12** current sources, all **five** actually mapped native
binaries, and all **48** real pickle checks. Each independent engine
blocks Python's `re` and `_sre`, external matching packages, the other
families, all five unowned native-loading entry points, and the cached
JSON-module access route. Both reports carry the exact same genuine
native and dependency evidence.

Complete official Python tests and the renewed full public
compatibility suite remain **NOT RUN**. The larger comparison is
**NOT FROZEN**, and current speed and memory remain **NOT MEASURED**.

## Predeclare independent execution for the repaired engines

First commit and push the real from-scratch report in `c1ef8102`.
Independently verify its exact SHA-256
`0314e3e5de3386d7c9c1e7f8fa4648554ff53cb53e3aafcecc4cb8e4923ddcbb`
and its source SHA-256
`77e7ea97f96280019b3be9abfeeb8fc6ff27ca6ecd13189e611586af5719c18f`.

Bind both real values in the independently reviewed, new
[no-delegation audit design](../tools/postfinal_no_delegation_audit_v6.py),
with source SHA-256
`a936abe91d67169ea361b6770404ffe7bc925fdb3275aef854fbe12fe68a8649`.
Its candidate-free self-test passes **75/75** checks and preserves all
**676** genuine previous malicious-input checks. It requires each engine
to block Python's matcher, external matching packages, the other
candidates, all five foreign native-library entry points, and cached
standard-library access. It authenticates the exact current source
report, all **12** implementation files, all **five** actual native
binaries, and both genuinely owned public type identities.

The actual no-delegation audit is **NOT RUN** at this source checkpoint.
Complete official tests, the renewed all-engine compatibility suite,
and expanded speed measurements are also **NOT RUN**.

## Verify all three repaired engines were built from scratch

Commit and push the candidate repairs and complete source-audit design
in `22d09eed` before starting the actual audit. The source has SHA-256
`77e7ea97f96280019b3be9abfeeb8fc6ff27ca6ecd13189e611586af5719c18f`.
Its independent, candidate-free self-test passes **324/324** controls,
including all **198** earlier controls.

Run the actual audit exactly once using the pinned Python:

```sh
env PYTHONDONTWRITEBYTECODE=1 \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_from_scratch_audit_v6.py --audit
```

The exclusively created
[real passing report](../candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V6.json)
has SHA-256
`0314e3e5de3386d7c9c1e7f8fa4648554ff53cb53e3aafcecc4cb8e4923ddcbb`.
It verifies all **12** current source files, all **five** genuine native
binaries, **three** independent native engines, **four** independently
owned pipelines, and all **48** real standard-library pickle checks.
Pattern ownership is genuinely local to each candidate; match ownership
is genuinely local to its native bridge. All five foreign native-loader
entry points remain blocked. The exact earlier passing reference and
failed Rust experiment are preserved.

The fresh no-delegation audit, complete official tests, and full
128-case all-engine compatibility run remain **NOT RUN**. Expanded
benchmark inputs remain **NOT FROZEN**; current speed and memory are
**NOT MEASURED**.

## Repair all three engines' real Python type ownership

Keep the [original passing two-Python reference](../oracle/cpython-3.14.6/evidence/public-generic-alias-v11-self-oracle.json)
and [actual first Rust failure](../candidates/evidence/python-re-generic-alias-public-oracle-v11-rust-failures.json)
unchanged. The failure is a real replacement defect: a class claiming to
come from Python's `re` module cannot be saved and restored by normal
Python `pickle` when it is actually implemented in another module. Do not
fake Python's module, replace its pickler, add a regex fallback, or weaken
the independent-engine checks.

Repair the separately owned Python and native type declarations in
[Rust](../candidates/rust_candidate.py) and its
[native bridge](../candidates/rust/py_bridge.c),
[C](../candidates/vm_candidate.py) and its
[native implementation](../candidates/_vm_native.c), and
[Zig](../candidates/zig_candidate.py) and its
[native bridge](../candidates/zig/py_bridge.c). Each public type now
identifies its real implementing module. The independently implemented
regular-expression matchers are not replaced by an external package or
Python's own matcher.

Run only targeted real checks: both `Pattern` and `Match`, both `str`
and `bytes`, pickle protocols **0, 2, 4, and 5**, and all three engines.
All **48** ordinary standard-library pickle round trips succeed; six
actual text-and-bytes matching smoke checks also succeed. These are
smoke checks, not a passing correctness campaign or audit.

The preserved version-five source and no-delegation audits, official
**146/146** test results, and **22-stage** campaigns apply only to the
fingerprinted earlier builds. None qualifies any of the six modified
source files. A fresh
[from-scratch audit design](../tools/postfinal_from_scratch_audit_v6.py)
must be committed before its real one-time report is generated. The
fresh source audit, fresh independent-execution audit, renewed full
official-test results, and a passing all-engine **128-case** replacement
comparison are **NOT RUN**. The genuine earlier Rust **16/128** failure
remains recorded, and the earlier test did not reach C or Zig.

The independently reviewed source-audit design passes **324/324**
candidate-free safety checks, including all **198** previous checks.
It verifies the five exact native-loader protections, distinguishes
candidate-owned patterns from native-owned matches, and rejects
substituted pickle protocols. Its source has SHA-256
`77e7ea97f96280019b3be9abfeeb8fc6ff27ca6ecd13189e611586af5719c18f`.
The actual source audit remains **NOT RUN** at this design checkpoint.

The archived speed graphs remain historical. The corrected expanded
comparison is **NOT FROZEN**, current-engine speed and memory remain
**NOT MEASURED**, and the independent final test for the rebuilt engines
remains **NOT OPENED**. The earlier, already-falsified final result
remains preserved. There is no winner.

## Preserve the first real generic-alias candidate failure

Commit and push the generic-alias source and protocol in `3e3df8d4`,
then the independently passing two-Python baseline in `6a480067`,
before starting any candidate. The source has SHA-256
`2d8b0417e837d830c3b01495657305536a9d14e289aeb61d503278f5944b16f3`,
the protocol has SHA-256
`b9d93b2ee18d33ad3e474c7e7d9bf7f94cd612526e39982fec0c2a0d0a4d096e`,
and the actual **128**-case, **256/256**-observation Python baseline
has SHA-256
`31245bf7864ae76e46e676a3a35d0fae399d1f6446af482db9f7aa47b5426f8a`.

Run the actual isolated candidate command:

```sh
env PYTHONDONTWRITEBYTECODE=1 \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/python_re_generic_alias_public_oracle_stage11.py \
  --candidate all
```

It exits **1** on the first candidate. The exclusively created
[actual Rust generic-alias failures](../candidates/evidence/python-re-generic-alias-public-oracle-v11-rust-failures.json)
have SHA-256
`5d0fce04b95a6d15e4aaff28d2c59337136660a248616672928f7aa85f7efa36`.
Exactly **16/128** actual Rust observations disagree with Python:
all **4** pickle protocols, both public `Pattern` and `Match` origins,
and both `str` and `bytes` arguments. Real Python successfully
restores every actual generic alias. Rust instead raises
`PicklingError: Can't pickle <class 're.Pattern'>: stage-07 blocked unowned matching import: re`,
or the equivalent error for `re.Match`. Its other **112/128**
observations agree, but the Rust candidate **FAILS** the frozen
complete contract.

The gate correctly stops on the first failing engine. C and Zig are
**NOT RUN** against this contract; there is no passing three-engine
report. The three engines therefore remain unqualified under the
expanded public correctness requirements. No speed or memory has been
measured, no final test is opened, and no winner has been established.
Preserve the separately recorded V8 and V10 public-benchmark failures
and all earlier failed drafts below; do not rerun or overwrite the
exclusive failure evidence.

## Establish the genuine two-Python generic-alias baseline

First commit and push the generic-alias source and protocol in
`3e3df8d4`. The frozen correctness source has SHA-256
`2d8b0417e837d830c3b01495657305536a9d14e289aeb61d503278f5944b16f3`;
the frozen protocol has SHA-256
`b9d93b2ee18d33ad3e474c7e7d9bf7f94cd612526e39982fec0c2a0d0a4d096e`.
The complete **128**-case public matrix has SHA-256
`7e5adbf2ca9c0f752a0c9dddaabe812a780cf58ca9b60efc178bafbaceee7e65`.

Run the actual pinned, isolated Python baseline once:

```sh
env PYTHONDONTWRITEBYTECODE=1 \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/python_re_generic_alias_public_oracle_stage11.py \
  --self-oracle
```

Two independently started, candidate-free CPython **3.14.6** processes
actually agree on all **128** cases and **256/256** observations,
with **zero** mismatches. The exclusively created
[actual public generic-alias baseline](../oracle/cpython-3.14.6/evidence/public-generic-alias-v11-self-oracle.json)
has SHA-256
`31245bf7864ae76e46e676a3a35d0fae399d1f6446af482db9f7aa47b5426f8a`.
Do not rerun or overwrite the existing exclusive evidence.

The Rust, C, and Zig candidate comparisons are still **NOT RUN**;
the passing Python baseline does not qualify an engine or establish
a speed. Preserve the earlier real source-provenance and unsafe-draft
failures below. Current speed remains **NOT MEASURED**, the independent
final test remains **NOT OPENED**, and no winner has been established.

## Predeclare the missing public generic-alias compatibility check

Python **3.14.6** documents actual runtime `re.Pattern[str]`,
`re.Pattern[bytes]`, `re.Match[str]`, and `re.Match[bytes]` generic
aliases. The **146** selected official regular-expression tests and
existing **3,584**-case public suite do not establish that the three
independently written Rust, C, and Zig engines implement this public
behavior. Preserve their existing proven results without inventing an
additional compatibility pass.

The [predeclared generic-alias correctness source](../tools/python_re_generic_alias_public_oracle_stage11.py)
has SHA-256
`2d8b0417e837d830c3b01495657305536a9d14e289aeb61d503278f5944b16f3`.
Its [complete prospective public contract](../oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V11.md)
has SHA-256
`b9d93b2ee18d33ad3e474c7e7d9bf7f94cd612526e39982fec0c2a0d0a4d096e`.
The exact **128**-obligation case matrix has SHA-256
`7e5adbf2ca9c0f752a0c9dddaabe812a780cf58ca9b60efc178bafbaceee7e65`:
**40** normal aliases, **48** unusual arguments, **16** actual
`isinstance` and `issubclass` checks, and **24** copying and pickling
observations.

The first real, candidate-free source-provenance check genuinely
failed with
`the passed three-engine report is not bound to both real Python references`.
The authentic earlier stage-ten report stores its passing baseline
bindings in each candidate's actual record, not in an invented
top-level baseline hash. Correct the source to verify all **41**
genuine stage-ten fields and the actual per-role Python-reference
bindings. The corrected source-only provenance check reports **PASS**
without starting either Python reference worker, importing a candidate,
recording evidence, or sampling a clock.

Preserve the real rejected development failures. An early synthetic
draft imported the Rust candidate in an isolated child; it performed
no matching, measurement, or evidence recording but was unsafe and
rejected. A fake-`re` synthetic pickle also inherited a metadata
inspector; a later lazy `argparse` route still loaded `inspect`.
Neither draft is a passing independence check. The final strictly
passive, candidate-free source self-test passes **74/74** without
`argparse`, `inspect`, `tokenize`, real candidate imports, workers,
clocks, evidence files, or performance measurements.

The required independently isolated, two-Python reference is
**NOT RUN**. All three independent candidate comparisons are
**NOT RUN**. The candidate-free synthetic source pass is not an
official-test pass, a Python-reference result, or proof of candidate
compatibility. The genuinely falsified expanded public benchmarks
remain preserved; current speed remains **NOT MEASURED**, the
independent final test remains **NOT OPENED**, and no winner has been
established.

## Record all genuine original-case collisions without benchmarking

The [complete recorded V10 public freeze failure](../performance/postfinal-public-v10/evidence/postfinal-public-freeze-failure-v10.json)
has SHA-256
`92e340bd4440ab77b59a07bfb0849c1147d3ac6dcb2adfe86888f9dd92ada38e`.
Its [independently verified public failure recorder](../tools/postfinal_public_expansion_v10_failure.py)
has SHA-256
`c7af74479586f46bb120b6b0474cfd96940228f539fcc630651038dda2725e33`.
Actual exclusive recording preserves the design verdict **FAIL** and
all **87** original collision classes. Independent report verification
passes all **31/31** actual-evidence checks. The recorder's
candidate-free synthetic safety test independently passes **55/55**;
this recorder-safety result does not turn the failed design into a
passing benchmark.

Authenticate all **10,312** public records, including **9,731**
eligible and **581** genuine but ineligible records, while skipping all
**10,312** opaque history values without decoding them. Preserve all
**8,192** distinct required parent case IDs and their **7,900** actual
matching-behavior identities: **87** collision classes, **379**
participating cases, **292** excess cases, a maximum class of **65**,
and **zero** inconsistent reference-result digests. Keep the first
collision, the genuine V8 failure, and the separately passing
stage-ten compatibility proofs independently bound to the evidence.

Reproduce only the safe, isolated synthetic check and read-only public
diagnosis:

```sh
env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_public_expansion_v10_failure.py --self-test
env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_public_expansion_v10_failure.py --diagnose
```

The failure evidence is created exclusively with `--record`; the
report now exists, so do not rerun recording. The recorded actual
failed design command remains
`env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/postfinal_public_practice_v10.py --freeze`.
Neither the failure nor its recorder creates a V10 manifest, runs a
candidate, starts a reference worker, samples a clock, reads a final
case, or measures performance. The V7 public manifest remains frozen,
with speed **NOT MEASURED**. The independent final test remains
**NOT OPENED**, and no winner has been established.

## Preserve the real original-case collision in the corrected design

Commit and push the corrected public design in `1fe0452f` before its
first actual freeze. Run the pinned interpreter with the exact real
command:

```sh
env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_public_practice_v10.py --freeze
```

The actual command exits **1**. Public-case selection fails at
`tools/postfinal_public_expansion_v10.py:814` with
`tools.postfinal_public_expansion_v8.PublicExpansionError: an original public case or semantic identity was repeated`.
Distinct required original case identities can legitimately describe
the same regular-expression behavior. Rejecting their shared semantic
identity incorrectly rejects genuine required public cases. Do not
remove original examples to make the design pass.

An independent, read-only reconstruction authenticates all **8,192**
distinct frozen parent case IDs and descriptors but finds exactly
**7,900** distinct matching-behavior identities. There are **87**
collision classes, **379** participating original cases, and **292**
extra cases; the largest class contains **65** cases. The first
collision occurs at original positions **136** and **137**:
`cal.large.long-ending.00` and `cal.large.long-ending.01`, both genuine
`search` cases in the `large-long-ending` category. Their reference
answers remain consistent: there are **zero** inconsistent result
digests. A first read-only forensic attempt separately raised
`TypeError: cannot use 'list' as a set element`; using a canonical
bytes token corrects the diagnostic without starting a worker,
running a candidate, or creating a file.

Any future valid **33,280**-case public design must retain all
**8,192** distinct original case IDs and all **25,088** distinct
generated case IDs. It must allow the originals' real shared
identities, for exactly **32,988** distinct matching behaviors:
**7,900** original and **25,088** newly generated. This is a
prospective requirement, not a created manifest or benchmark result.

The prior successful, read-only **10,312/10,312** original-record
authentication remains valid, including **9,731** eligible records,
**581** authenticated oversized records, **10,312** skipped opaque
history values, and exact **8,192**-case V6 and V7 descriptor parity.
The genuine **198/198** and **330/330** candidate-free synthetic
safety tests also remain valid. None proves that actual case selection
or freezing succeeds; the actual V10 freeze is **FALSIFIED**. The
earlier V8 UTF-8 failure likewise remains **FALSIFIED**, with all
**577/10,312** failures and **483/48/46** operation counts preserved.

The actual V10 freeze fails before either Python reference worker,
any candidate, manifest creation, clock sampling, or performance
measurement. Its larger manifest is **NOT CREATED** and **NOT FROZEN**.
The **8,192**-case V7 public manifest remains frozen and published;
its speed is **NOT MEASURED**. A corrected broader public comparison
remains **NOT FROZEN** and **NOT MEASURED**. The independent final
test remains **NOT OPENED**, and no winner has been established.

## Correct the public-data design without running a benchmark

Preserve the genuinely falsified **33,280**-case V8 expansion, its
complete failure report, and all **577/10,312** wrong ASCII-encoded
comparisons: **483** `findall`, **48** `escape`, and **46** `split`.
Do not edit its already-published sources or disguise the failure as a
passing benchmark.

The first real corrected-design probe also fails with
`public subject exceeds its predeclared limit`: some authentic public
archive records exceed the declared safe benchmark-input size. Preserve
that result rather than silently discarding the records. The actual
corrected public-only verification then exits **0** and reports **PASS**:
all **10,312/10,312** original public results authenticate with their
original UTF-8 encoding. Exactly **9,731** records are safe to select;
**581** are authenticated but explicitly excluded from measurement.
All **10,312** opaque history entries are skipped without decoding
their values. Both independently frozen **8,192**-case V6 and V7
public descriptors match exactly. No candidate, worker, clock, output
file, timing result, hidden case, or final test is accessed.

The [corrected public-case generator](../tools/postfinal_public_expansion_v10.py)
has SHA-256
`ae0ff9664939b4d86a25fb860d93c02119a9a195ccf3fc32cbb805170a242065`.
The [corrected public protocol](../performance/postfinal-public-v10/PROTOCOL.md)
has SHA-256
`e918053c99255e1a528102738e02a1e5979d65eadf0049ef3beed84d26941257`.
The separately authored [prospective measurement runner](../tools/postfinal_public_practice_v10.py)
has SHA-256
`e99a4241ceb69c6f5e685fd05dab134f585670418738f0bc5cb0da0b61ffa02d`.
The generator's candidate-free synthetic safety test passes
**198/198**; the runner's candidate-free synthetic safety test passes
**330/330**, including **212** inherited controls. These test the
proposed source, not candidate correctness or performance.

The corrected design prospectively retains the exact **8,192** original
public examples and expands to **33,280** cases across **260** workload
categories. The Rust, C, and Zig engines are separately implemented
from scratch; none may wrap another regular-expression package, call
Python's matching engine, or delegate to another candidate. The
one-time manifest is **NOT CREATED** and **NOT FROZEN**. Source and
protocol must be committed and pushed before freezing; the manifest
must be separately committed and pushed before any timing. The already
frozen and published **8,192**-case V7 benchmark also remains
**NOT MEASURED**. No new speed, memory, confidence interval, ranking,
or slowdown has been measured. The independent final test remains
**NOT OPENED**, and no winner has been established.

## Preserve the genuine failure of the larger public benchmark

After committing and pushing the larger benchmark source and protocol
in `a28eff8f`, attempt its first actual isolated freeze:

```sh
env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_public_practice_v8.py --freeze
```

This exits **1** with `ModuleNotFoundError: No module named 'tools'`.
The exact isolated module retry preserves the pinned interpreter,
environment, and public source:

```sh
env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -c \
  'import sys;sys.path.insert(0,".");from tools.postfinal_public_practice_v8 import main;main(["freeze"])'
```

It also exits **1**, after passing source provenance but before creating
a manifest, with the real production error
`tools.postfinal_public_expansion_v8.PublicExpansionError: corrupt public reference answer`.
The larger public design is **FALSIFIED**. Its earlier **177/177** and
**212/212** synthetic checks do not constitute a passing production
freeze or a passing public-data comparison.

Twice independently stream and selectively decode only the **10,312**
previously frozen, explicitly public rows, skipping all **10,312**
opaque-history rows without deserializing them or opening a secret
test. The original UTF-8 JSON encoding with
`ensure_ascii=False` reproduces **10,312/10,312** saved answers. The
larger benchmark's ASCII encoding with `ensure_ascii=True` incorrectly
rejects **577/10,312** genuine public answers: **483** `findall`,
**48** `escape`, and **46** `split` cases, all text. The first failure
is `cal.unicode.words`: the correct saved digest is
`21f3db7cbb6c5d5bb6fcaf4dc6847779d647399a97f9e62a62861733a4fa1949`,
while the incorrect ASCII digest is
`af46c189444aa11a5f11a6894aaac409e79913384e82e6ea96e6668468f10885`.

The [actual public freeze-failure report](../performance/postfinal-public-v8/evidence/postfinal-public-freeze-failure-v8.json)
has SHA-256
`e46a5b0482293a016c1ba6d0bcadb4c5bcf97ea15af9a2027734ac855c688aba`.
Its [public-only failure recorder](../tools/postfinal_public_expansion_v8_failure.py)
has SHA-256
`800963bc33227c936a2f8506fa80057672acb1c831b772a1bb412aec6540eb94`.
The actual exclusive recorder exits **0**, reports **RECORDED**, and
preserves the real design verdict **FAIL**. Its independently isolated
synthetic self-test passes **48/48** without starting an engine,
writing evidence, measuring time, or opening a secret test; that
recorder-safety result does not turn the falsified design into a pass.
The report preserves the mismatch without modifying the published generator
`e921d5962746d564381a0a11d22eb125b080370b572ffd0f630e925025f1ec97`,
protocol
`e19d504f6d7504b4052f2bbfbc0a584596178919c5396e076d3e6261356a2095`,
or runner
`7818577b36bb822cc99e02a07fcd5ba74e20f1ecf6f0dcb3c0913d2a97bd244f`.
Neither actual attempt creates a larger manifest, starts a candidate,
measures time, reads final cases, or changes the frozen and published
**8,192**-case public benchmark. A corrected **33,280**-case public
comparison remains **NOT FROZEN** and **NOT MEASURED**. The independent
final test remains **NOT OPENED**, and no winner has been established.

## Prepare a larger public comparison without freezing or timing it

Preserve the previously pushed **8,192**-case public source, protocol,
and one-time manifest in `4096efbc`. Its manifest remains **FROZEN**;
its speed remains **NOT MEASURED**. The earlier actual freeze failure
and successful retry remain recorded without alteration below.

The [larger public-case generator](../tools/postfinal_public_expansion_v8.py)
has SHA-256
`e921d5962746d564381a0a11d22eb125b080370b572ffd0f630e925025f1ec97`.
The [prospective larger public protocol](../performance/postfinal-public-v8/PROTOCOL.md)
has SHA-256
`e19d504f6d7504b4052f2bbfbc0a584596178919c5396e076d3e6261356a2095`.
The [prospective public benchmark runner](../tools/postfinal_public_practice_v8.py)
has SHA-256
`7818577b36bb822cc99e02a07fcd5ba74e20f1ecf6f0dcb3c0913d2a97bd244f`.
Their direct, isolated, candidate-free synthetic safety tests pass
**177/177** and **212/212**, respectively, without creating files,
starting engines, reading final tests, or measuring time.

The prospective public design specifies exactly **33,280** cases:
**128** cases in each of **260** workload categories, retaining all
**8,192** existing public cases. It covers **12** Python operations,
**4** actual input types, and **13** paired trials. Its **1,730,560**
timing rows, **5,191,680** correctness gates, **99,843** confidence
intervals, **266,248** safeguards, and **99,840** untimed candidate
prequalification checks are prospective denominators, not observations.
Every speed, memory result, confidence interval, ranking, and slowdown
remains **NOT MEASURED**.

The previously passing independent baseline
`5207ca3829216b9482f0b5a2928b339261e2c51d673cce7d80da0f4f4622a8f9`
and three-engine compatibility report
`0af512f940ce7c28e50c1977794e3fbb8a2c33206e77dd2379d4fa12b391fec7`
remain mandatory. Preserve both actual earlier **32** baseline failures
and **256** harness failures. The larger source and protocol must be
committed and pushed before the one-time manifest may be frozen. No
engine may be timed until that manifest is separately committed and
pushed. The larger manifest is **NOT FROZEN**. These cases are public,
not secret final-test examples. The independent **65,536**-case final
test remains **NOT OPENED**, and no winner has been established.

## Freeze the public comparison without measuring the engines

First commit and push the exact public benchmark source and protocol in
`0b673fe4`. The first direct, isolated freeze genuinely fails with
`AssertionError: PYTHONPATH=. or the canonical root is mandatory`
because the command omitted the inherited deep-contract environment.
That failed attempt creates no manifest, starts no candidate, and
takes no measurement. Preserve the failure; do not describe it as a
successful freeze or a candidate error.

The actual one-time retry succeeds with the exact required environment:

```sh
env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_public_practice_v7.py --freeze
```

Its exit status is **0**. The resulting
[public benchmark manifest](../performance/postfinal-public-v7/manifest.json)
has SHA-256
`465c751c6756cbea73bc3dc6d4397e2777d04a107b9a607241697b148c9c5f26`.
It authenticates the previously pushed benchmark source
`cc5b79daf3a0d018d15c76d01665cf94a30d3838c5a5c21389cba51444e96e7e`
and protocol
`c8fed02bde3d2b096905a44db99405b47801743749053e8dc402cb70cc1f51c0`.
The one-time manifest is **FROZEN**. Timing is permitted only after
the source, protocol, and manifest are committed and pushed. Creation
is exclusive and one-time; do not repeat the command.

The frozen public plan contains exactly **8,192** unique preserved
examples, **260** categories, **12** operations, **13** paired trials,
**4** warmups, and **2,000** confidence resamples. The **425,984**
timing rows, **1,277,952** correctness checks, **24,579** confidence
intervals, and **65,544** process and native-library guards remain
planned denominators, **NOT MEASURED** results. The freeze starts no
candidate or timing clock and never accesses the independent final
test. The separate **33,280**-case expansion remains **NOT FROZEN**;
the **65,536**-case final test remains **NOT OPENED**. There is no
winner. Preserve the earlier actual **32** Python self-oracle failures
and **256** Rust harness failures below.

## Prepare the public speed comparison without freezing or running it

Preserve the previously pushed **1,190,400** successful three-engine
public correctness comparisons, all **146/146** genuine official tests,
and all **22/22** independently verified compatibility stages. The
earlier **32** Python self-oracle failures and **256** harness-side Rust
failures remain visible below; neither is concealed or reclassified as
a matching regression.

The standalone [prospective public benchmark](../tools/postfinal_public_practice_v7.py)
has SHA-256
`cc5b79daf3a0d018d15c76d01665cf94a30d3838c5a5c21389cba51444e96e7e`.
Its [prospective protocol](../performance/postfinal-public-v7/PROTOCOL.md)
has SHA-256
`c8fed02bde3d2b096905a44db99405b47801743749053e8dc402cb70cc1f51c0`.
A direct, isolated synthetic safety test passes **346/346** checks
without starting an engine, touching benchmark evidence, measuring
speed, or opening the final test.

The prospective design specifies **8,192** preserved public examples,
**260** categories, **12** operations, and **13** paired trials. The
**425,984** timing rows, **1,277,952** correctness checks, **24,579**
confidence intervals, and **65,544** process and native-library guards
are planned denominators, **NOT MEASURED** results. Every slowdown must
be published.

This checkpoint authenticates source and protocol only. The one-time
benchmark manifest is **NOT CREATED** and **NOT FROZEN**; no engine has
been benchmarked. The proposed **33,280**-case broader public suite is
**NOT FROZEN**. The independent **65,536**-case final test remains
**NOT OPENED**, and no winner has been selected.

## Pass all three engines under independently guarded signature checks

First commit and push the actual passing two-Python baseline in
`931f8b01`. Then run the separately frozen stage-ten comparison
against each current, independently written Rust, C, and Zig engine.
Each passes all **3,584** cases across all **8** test groups, for
**10,752** new comparisons and **zero** mismatches. The total
verified public comparison count becomes **1,190,400**.

The [complete three-engine result](../candidates/evidence/python-re-universal-public-oracle-v10-all.json)
has SHA-256
`0af512f940ce7c28e50c1977794e3fbb8a2c33206e77dd2379d4fa12b391fec7`.
It independently authenticates the frozen controller
`a24cfa72f44931c76b425ea3eb6568ff67dc87236c8d5fe930837a14c2f58f08`,
protocol
`c0194ee2ef1e32bd64dc646e2f395bee6036b9c053e31d95ebb3cfbc52b0a543`,
and previously pushed baseline
`5207ca3829216b9482f0b5a2928b339261e2c51d673cce7d80da0f4f4622a8f9`.
Every engine independently produces the same exact observation
digest,
`0d6a74b1f923436c14569bfdd84431e4251f3bb8dd3129fbbcaf82a47f906b94`.

Each actual matching worker blocks Python's regex engine, all
external matching packages, both other candidates, and all **5**
native-loader aliases. Real public signatures are observed in a
separate isolated process. Preserve the actual earlier **32**
Python-versus-Python failures and **256** Rust harness failures; do
not attribute either to this new result or weaken the guard.

This is correctness evidence, not a benchmark. The planned
**8,192**- and **33,280**-case speed comparisons remain
**NOT FROZEN** and **NOT MEASURED**. The independent final test
remains **NOT OPENED**; no winner has been established.

## Independently pass the frozen isolated-signature Python baseline

First freeze and push the exact stage-ten controller and protocol in
`0dc80fc`. Then run two independently isolated CPython 3.14.6
processes against all **3,584** unchanged cases. The actual
[complete passing two-Python baseline](../oracle/cpython-3.14.6/evidence/public-contract-v10-self-oracle.json)
preserves **7,168** observations with **zero** mismatches.

Its one-use, exclusively created report has SHA-256
`5207ca3829216b9482f0b5a2928b339261e2c51d673cce7d80da0f4f4622a8f9`.
Both independently generated observation streams have canonical
SHA-256
`0d6a74b1f923436c14569bfdd84431e4251f3bb8dd3129fbbcaf82a47f906b94`.
The report binds the frozen source
`a24cfa72f44931c76b425ea3eb6568ff67dc87236c8d5fe930837a14c2f58f08`
and protocol
`c0194ee2ef1e32bd64dc646e2f395bee6036b9c053e31d95ebb3cfbc52b0a543`.

Preserve both historical failures: all **32** process-dependent
pattern hashes and all **256** guard-triggered surface checks. Do
not overwrite the new baseline; its `--self-oracle` invocation is a
one-shot operation that rejects an existing report.

Exactly **zero** candidate processes or imports run in this
checkpoint. Rust, C, and Zig remain **NOT RUN** against the frozen
stage-ten contract. Commit and push the passing baseline before any
candidate. Performance remains **NOT MEASURED**, and the independent
final test is **NOT OPENED**.

## Freeze independently isolated Python-signature inspection

Preserve the exact **32**-mismatch stage-seven Python failure and
the actual **256**-mismatch stage-eight Rust harness failure. The
first is a process-dependent Python hash; the second is the harness
importing `inspect` inside a correctly guarded native worker.
Neither establishes that an independently implemented candidate
delegated regex matching.

The additive [isolated-signature protocol](../oracle/cpython-3.14.6/PUBLIC-CONTRACT-V10.md)
has SHA-256
`c0194ee2ef1e32bd64dc646e2f395bee6036b9c053e31d95ebb3cfbc52b0a543`.
The independently verified
[candidate-free signature controller](../tools/python_re_universal_public_oracle_stage10.py)
has SHA-256
`a24cfa72f44931c76b425ea3eb6568ff67dc87236c8d5fe930837a14c2f58f08`.
Its direct, isolated self-test passes **793/793** synthetic controls,
without metadata workers, candidate processes, evidence writes,
timing, or final-test access.

Keep all **3,584** unchanged public cases, all **8** groups, and
every **256**-case public-signature obligation. Authenticate genuine
signatures in a separate isolated process; never import Python's
matcher into a matching worker, omit signatures, or guess metadata.
The actual stage-ten two-Python baseline is **NOT RUN**. Rust, C,
and Zig are each **NOT RUN** against this corrected design.

Freeze, commit, and push this exact source and protocol before
starting any production worker. New **8,192**- and **33,280**-case
speed comparisons remain **NOT FROZEN** and **NOT MEASURED**. The
independent final test remains **NOT OPENED**.

## Preserve the first Rust candidate's harness-side failure

After committing and pushing the actual passing two-Python baseline,
run the first candidate only. Rust records **256** mismatches among
the **3,584** frozen cases; all **256** are in the
`public-surface` test group. Every actual exception is
`ImportError: stage-07 blocked unowned matching import: re`.

The test harness's `_surface_obligation` imports `inspect` after
the strict native-engine guard is installed; that introspection
indirectly requests Python's `re`. The guard correctly rejects the
unowned matching engine. This demonstrates a test-harness
introspection bug, not a Rust matching error, fallback, external
package, or delegation.

The [complete exclusive Rust failure report](../candidates/evidence/python-re-universal-public-oracle-v8-rust-failures.json)
retains all **256** case identities, expected values, actual
exceptions, and matching-source guards. Its SHA-256 is
`f509cedf5f58d1c211b63177fb843bfba3dc0b132469a392df43a9c802e323b1`.
It independently binds the passing Python-baseline report
`efcf0f661363e9032ce8c0afe7ea06a4762b783eec4c4ee6ec7c7059c14994df`,
the immutable stage-eight source, and the exact case matrix.

The historical **32**-mismatch stage-seven Python failure remains
unchanged at
`765e635745a7e332a1bd22426065c43fd52036d013add0d88d840d8fde1121e0`.
C and Zig are **NOT RUN** against stage eight. Do not weaken the
guard, discard failures, alter frozen evidence, or claim candidate
success before an additive harness correction is frozen. Performance
is **BLOCKED** and **NOT MEASURED**; the independent final test is
**NOT OPENED**.

## Independently pass the corrected two-Python baseline

Only after committing and pushing the corrected compatibility design,
run its **3,584** unchanged obligations against two separately
isolated pinned CPython 3.14.6 processes. All **7,168** observations
agree: **zero** mismatches, crashes, or skipped cases.

The [complete new Python-baseline evidence](../oracle/cpython-3.14.6/evidence/public-contract-v8-self-oracle.json)
has SHA-256
`efcf0f661363e9032ce8c0afe7ea06a4762b783eec4c4ee6ec7c7059c14994df`.
It binds the frozen controller
`10464ca347e6eab248a2887a6fd0625cff63497173024616ca8338af0801b0aa`,
protocol
`502f300e8ffbd33cf3cbbf6fde7e9cb5e81ed3f87f83634f47068015cdd9dbdd`,
matrix
`0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db`,
and seed `2026072437`. The original stage-seven **32**-mismatch
failure and its `765e635745a7e332a1bd22426065c43fd52036d013add0d88d840d8fde1121e0`
report remain unchanged.

Exactly **zero** candidates were imported or started. Rust, C, and
Zig are each **NOT RUN** against the corrected contract. Commit and
push the complete passing baseline before starting any candidate.
New performance remains **NOT MEASURED** and the independent final
test remains **NOT OPENED**.

## Freeze portable compatibility checks without erasing the real failure

Keep the [actual stage-seven Python-versus-Python failure](../oracle/cpython-3.14.6/evidence/public-contract-v7-self-oracle-failures.json)
unchanged at SHA-256
`765e635745a7e332a1bd22426065c43fd52036d013add0d88d840d8fde1121e0`.
All **32** process-dependent pattern-hash mismatches, all **7,168**
Python observations, all original cases, and the unchanged frozen
source remain preserved. No replacement engine ran that failed suite.

Reject an intermediate `bfccb` late-bound implementation before
freezing it. The final additive
[portable compatibility controller](../tools/python_re_universal_public_oracle_stage08.py)
has SHA-256
`10464ca347e6eab248a2887a6fd0625cff63497173024616ca8338af0801b0aa`.
Its direct, independently verified candidate-free safety test passes
**597/597** checks. It neither starts a Python self-comparison nor
imports a candidate, creates production evidence, takes a timing, or
opens the final test.

The final [portable compatibility protocol](../oracle/cpython-3.14.6/PUBLIC-CONTRACT-V8.md)
has SHA-256
`502f300e8ffbd33cf3cbbf6fde7e9cb5e81ed3f87f83634f47068015cdd9dbdd`.
It preserves all **8** original groups, all **3,584** obligations,
and the immutable case matrix
`0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db`.
Real pattern-hash consistency and dictionary behavior are retained;
process-specific numeric hashes are not compared. Lone Unicode
surrogates are preserved losslessly in portable evidence, with no
dropped or rewritten historical cases.

Commit and push the exact corrected protocol and source before any
production worker runs. The stage-eight Python self-comparison is
**NOT RUN**. Rust, C, and Zig are each **NOT RUN** against the new
portable contract. No stage-eight passing production result,
benchmark, or memory measurement exists. The independent final test
remains **NOT OPENED**.

## Preserve the actual failed two-Python reference comparison

After freezing and pushing the expanded compatibility design, run its
two isolated CPython 3.14.6 references exactly once. The self-oracle
**FAILS**: **32** of the **3,584** case comparisons disagree, while
the remaining **3,552** agree. Preserve all **7,168** independent
Python observations and all **32** mismatches in the
[complete exclusive failure report](../oracle/cpython-3.14.6/evidence/public-contract-v7-self-oracle-failures.json).
Its exact SHA-256 is
`765e635745a7e332a1bd22426065c43fd52036d013add0d88d840d8fde1121e0`.

All **32** failures are object-contract cases `0000`, `0008`,
through `0248`. The two real Python processes report different raw
hashes for the same compiled-pattern value:
`-4908800511453295329` and `-7040912458813119187`, even with
`PYTHONHASHSEED=0`. The other **3,552** cases agree, including
genuine locales, threads, and callbacks. This is a mismatch between
Python references, not a failure by any replacement engine.

The failure authenticates the frozen source
`150abcfc597658f48d64c04053889bd4b299c75ad7413bc1cafa5f864e9e7c25`,
protocol
`b4d719609179dde5f582695393539e7a320c09438e4bc635ca843627ac9d7524`,
matrix
`0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db`,
and seed `2026072437`. A strict `jq` reader separately rejects a
retained escaped lone surrogate; pinned Python can inspect the exact
original file without dropping or rewriting a record.

Exactly **zero** candidates were imported or started. Rust, C, and
Zig are **NOT RUN** against the failed expansion. Preserve and push
this real failure before proposing a separate additive fix; never
mutate the frozen stage-seven source or claim that a new suite already
exists. Expanded benchmarks remain **BLOCKED** and
**NOT MEASURED**. The independent final test is **NOT OPENED**.

## Freeze expanded compatibility checks only after fixing their safeguards

The three complete **22**-stage, source-bound correctness campaigns
were already committed and pushed in `df68898`. Preserve their
passing results, the original **1,179,648** current-engine checks,
and all historical performance graphs.

The first proposed controller fails its actual direct, isolated
self-test with exit **137** and **zero** output. An earlier pipe into
`jq` masks the failure; its cause is **NOT ESTABLISHED**. Independent
review also finds that Python-baseline and candidate mismatches are
raised before durable failure evidence is written. Preserve both
failures instead of claiming a prematurely frozen suite.

The corrected [public compatibility protocol](../oracle/cpython-3.14.6/PUBLIC-CONTRACT-V7.md)
has SHA-256
`b4d719609179dde5f582695393539e7a320c09438e4bc635ca843627ac9d7524`.
The corrected [candidate-free controller](../tools/python_re_universal_public_oracle_stage07.py)
has SHA-256
`150abcfc597658f48d64c04053889bd4b299c75ad7413bc1cafa5f864e9e7c25`.
Its direct, unpiped self-test actually exits **0** and passes
**429/429** synthetic controls without starting an engine, comparing
Python against itself, writing evidence, measuring speed, or accessing
the final test.

The frozen design defines **8** groups and **3,584** obligations.
Its canonical matrix SHA-256 is
`0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db`.
The corrected gate separately reserves four exclusively created
`O_EXCL` baseline and candidate failure files and verifies all
**5** protected loader-alias routes. No failure file is created during
the safety test.

Commit and push this frozen design before any production comparison.
The actual two-Python self-comparison is **NOT RUN**. Rust, C, and
Zig are each **NOT RUN** against the new **3,584** obligations. No new
production correctness result is claimed. Separate speed benchmarks
remain **NOT FROZEN** and **NOT MEASURED**; the independent
**65,536**-case final test remains **NOT OPENED**.

## Run every official Python test in genuine locales

The completed six-graph comparison still describes only the
[five archived benchmarked native libraries](../performance/postfinal-public-v6/NATIVE-ARCHIVE-V1.md).
The C, Rust, and Zig engines have since changed. Preserve the old
**8,192** cases, all **5,940** slowdowns, and both original archives;
never present their measurements as results for the current engines.

The earlier **144/146** official-test result exposed two genuine missing
locale cases. Generate real, private `en_US.iso88591` and
`en_US.utf8` locales, retain both original named tests, and verify
patterns compiled before an actual locale change. The
[new official evidence](../oracle/cpython-3.14.6/evidence/postfinal-locale-v1-all.json)
has SHA-256
`bc17ee74409543d1b57f3aee65088e990ab21ac83dc75ac46fbd1f97f04b6621`.
Python, Rust, C, and Zig each pass **146/146**, with **zero** failures,
crashes, or skips. No test is removed, mocked, approximated, or waived.

Preserve both initial source-audit failures. First, Rust lifetime
apostrophes were incorrectly treated as character literals, concealing
its independently owned parser and executor. Correct the tokenizer
without weakening either required component. A later complete
five-library audit child exits with **SIGKILL**; isolate each actual
safety-control subprocess and preserve the observed signal without
guessing its cause.

The intermediate version-four source proof,
`5677065d42ba0c4f135182cb681533181e57de823a367fdd54fde3d90120f87a`,
is retained strictly as historical. The first version-four strict
attempt stops with
`refusing a private, holdout, final, benchmark, or unapproved input`.
After narrowing the allowed path, the next stops with
`the original pinned 76 controls no longer pass in isolation`.
Neither attempt creates an accepted strict report. Correct both guards;
subsequent C and Zig source changes still make the version-four source
proof historical. Never treat it as current or fabricate a missing
strict report. The accepted
[version-five source audit](../candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json)
passes **198** synthetic controls and has SHA-256
`42bd73acf6831b67df9a9873fa35c1882f2af09c41933774ba841d2290e6c198`.
The accepted
[version-five independence audit](../candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json)
passes **676** synthetic controls and has SHA-256
`50031133a2aa20b1ef91b126a883a622d916f582fdcbea4ba1763267199c03bb`.
Together they bind all **12** current source files and all **5**
current native roles. The rebuilt Rust engine passes **44** native
tests; the rebuilt Zig engine is **456,192** bytes.

The initial locale-aware campaign controller had SHA-256
`12860418d1c7ea8251c215d2138fed1145927aa716d791b97d939912489b18e7`.
Its candidate-free self-test passes **93** new synthetic controls,
retains **43** hardened controls and **46** original controls, and
requires the actual version-five audits and all four genuine-locale
results. Its fingerprint belongs to that first controller, not to the
corrected later controller. A passing synthetic self-test is not an
executed engine campaign or a performance measurement.

Preserve two actual invocation failures. The first C Python-object run
rejects an evidence filename without the required `-C-` family marker.
The first Zig run lacks its explicitly required environment. Neither
failed attempt writes an output or discovers an engine mismatch.
Correct the evidence path and environment before recording results.

The first complete C campaign then stops before writing any report:
the inherited hardened verifier omits the C engine's actual owned
native-source artifact. This is an artifact-accounting bug in the
verifier, not a C matching failure. Preserve the failure, correct the
adapter without dropping any native-source requirement, and do not
invent a passing full C campaign.

An intermediate C-aware controller correction has SHA-256
`e27099f45b5daa490d5e891a76aa8cf770d93861ca4769e17f559b20fe656c1a`.
Its candidate-free self-test passes **120** synthetic controls,
including the inherited **43** hardened and **46** original checks.
It verifies the actual Rust, C, and Zig native-source roles without
omitting C's independently owned source. The original Rust campaign
below was generated by the initial controller, not by this
intermediate source. The original controller cannot currently be
reconstructed byte-for-byte; do not falsely claim that it was restored
or independently reproduced. Prepare a separate additive controller
and uniquely named fresh results for all three engines without
overwriting either earlier campaign. Neither intermediate correction
constitutes a fresh, independently reproducible engine campaign.

The [actual frozen version-four controller](../tools/rust_v8_multi_candidate_campaign_postfinal_v4.py)
has SHA-256
`67a7555976ab60c371c9aad1b7f94c112bd1c6aaf990e39c02f4484f3010e799`.
It is neither the historical `128604` controller that produced the
first Rust report nor the rejected `e27099` intermediate. Do not
substitute its bytes into an earlier proof. Current engine
qualification requires separate, fresh additive version-five
campaigns.

The [new immutable additive campaign controller](../tools/rust_v8_multi_candidate_campaign_postfinal_v5.py)
has SHA-256
`50a39f8338b176b9376cac1437a7c0aaeb343594af0ebfea797a7beea04e86d9`.
It binds the actual frozen version-four ancestor, passes **131**
candidate-free synthetic controls, and inherits all **93**, **43**,
and **46** existing control groups. It requires genuine **146/146**
official locale results and independently source-bound C, Rust, and
Zig evidence. Its passing self-test is not a campaign result: each
engine must exclusively create and pass its own new **22**-stage
report without replacing any historical evidence.

The current Rust engine independently passes
[223,198 matching and parser checks](../candidates/evidence/rust-v7-edge-oracle-rust-postfinal-locale-v1.json.gz),
with report SHA-256
`8569275c5b705870bde368ee20981be1a90c07675b12fe53b64f19c7e765b408`;
[393 Python-object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-LOCALE-V1.json.gz),
with SHA-256
`ca437ae8e2dc46f4d0b8e259f304a402efc6f0817dfe89600d92728a86c2ce9f`;
and
[479 callback, iterator, scanner, and buffer checks](../candidates/evidence/rust-v8-observability-rust-qualified-postfinal-locale-v1.json.gz),
with SHA-256
`db139cf63dfe6605120a9e36db16b749f060fc31961fe6215397623b454929fa`.
Every proof is bound to the rebuilt locale-aware Rust source and native
binary; none measures speed.

The independently rebuilt C engine also passes its own
[223,198 matching and parser checks](../candidates/evidence/rust-v7-edge-oracle-vm-postfinal-locale-v1.json.gz),
with report SHA-256
`0c07fdbf8848f4236735c97bbda4969c4de0ceb6e10c11fdac0c674d5efd303b`;
[393 Python-object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-C-POSTFINAL-LOCALE-V1.json.gz),
with SHA-256
`9d8aa10cd07d4bee48b021f26fbb66e5d2f3293f6c1d8a0d1039a9087af932de`;
and
[479 callback, iterator, scanner, and buffer checks](../candidates/evidence/rust-v8-observability-vm-qualified-postfinal-locale-v1.json.gz),
with SHA-256
`35c63238162f420c41a5b021641530344d91ddc036b15dac73705b3f144ee43b`.
All three reports are bound to the independently written current C
engine; none measures speed.

The independently rebuilt Zig engine also passes
[223,198 matching and parser checks](../candidates/evidence/rust-v7-edge-oracle-zig-postfinal-locale-v1.json.gz),
with report SHA-256
`8a8f76a85e2888dc0eb19e07c7343dd5c8caeab8745baf8a277f68beea1424a6`;
[393 Python-object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-LOCALE-V1.json.gz),
with SHA-256
`f522ae69bea26792b8406254360809ae9cfddeb03cc012dc579f2397c7e8813d`;
and
[479 callback, iterator, scanner, and buffer checks](../candidates/evidence/rust-v8-observability-zig-qualified-postfinal-locale-v1.json.gz),
with SHA-256
`43053dd764ee9b6c40ccfee72107b1e1ebe56e1081b951ec026c3ab8c124e15d`.
The Python-object proof transparently preserves **36** differences in
private garbage-collection internals, separate from **zero** public
mismatches. None is hidden, claimed to affect documented Python
behavior, or counted as an unexplained failure.

The [historical observed Rust compatibility campaign](../candidates/evidence/rust-v8-rust-postfinal-locale-v4-sealed-campaign.json)
has SHA-256
`0311663e7e7c501d660f2dab8a8cd877795c35cfe507c65f7f92d9f0913d4540`.
Its **22/22** stages pass against the exact rebuilt Rust source,
including all **146/146** official tests, **zero** skips, and
**4,494,555** full-Unicode comparisons. It does not run a benchmark
or access the final test. It was generated under the original
`12860418d1c7ea8251c215d2138fed1145927aa716d791b97d939912489b18e7`
controller, whose exact source cannot now be reconstructed. Preserve
the observed report honestly; do not attribute it to either changed
controller or present it as a newly reproducible result.

The [fresh, source-bound version-five Rust campaign](../candidates/evidence/rust-v8-rust-postfinal-locale-v5-sealed-campaign.json)
has SHA-256
`bdc10bbdf1f6a7711283826b04c1fe7f4ab700a7cf97d4c8f0595d20cab80024`.
It independently authenticates the actual `50a39f` version-five
controller and `67a755` version-four ancestor. All **22/22** stages,
all **146/146** official locale-aware tests, and all **4,494,555**
Unicode comparisons pass against the exact current Rust source and
native binary. There are no skipped tests, timings, or final-test
accesses.

The [fresh, source-bound version-five C campaign](../candidates/evidence/rust-v8-vm-postfinal-locale-v5-sealed-campaign.json)
has SHA-256
`3156b02d4dd428b82c6c3947b620fa046330234b1ce0fd66058dff4a3d0c6d16`.
It independently authenticates the same `50a39f` controller and
`67a755` ancestor, together with all **3** actual C source and native
roles. All **22/22** stages, **146/146** official tests, and
**4,494,555** Unicode comparisons pass, with no skips, timing, or
final-test access.

The [fresh, source-bound version-five Zig campaign](../candidates/evidence/rust-v8-zig-postfinal-locale-v5-sealed-campaign.json)
has SHA-256
`e9a096349fd3b3cd9c91464b6033880ef9f2d30dece18e04d0c2a79efc6812cf`.
It independently authenticates the same `50a39f` controller and
`67a755` ancestor, together with all **5** actual Zig source and
native roles. All **22/22** stages, **146/146** official tests, and
**4,494,555** Unicode comparisons pass, with **zero** skips, timing,
or final-test access. Rust, C, and Zig are therefore independently
correctness-qualified for their exact current builds.

The [new source-bound all-engine public comparison](../candidates/evidence/python-re-universal-public-oracle-v6-all.json)
has SHA-256
`bf4f7cc82c876ee54e55c0971c65db209f6fdf0c8b00baa8c57fbc5f460b1528`.
All three current engines match Python in **1,179,648** comparisons,
with **zero** mismatches and no external matching engine. The fresh,
source-bound Rust, C, and Zig **22**-stage campaigns all pass.
Keep the fair **8,192**-case public comparison comparable to the
original. Separately plan **33,280** expanded public cases:
**260** categories with **128** cases each, including **25,088** new
cases. A proposed **266,240**-case independently blinded test cannot
be claimed: its separate steward and protected random seed are not
available. No new manifest is frozen, no speed is measured, and no
public case is described as a blind final test. The independent
**65,536**-case final test was not accessed and remains **NOT OPENED**.

## Rebuild Rust and disclose both new verification failures

Preserve the [five engines from the latest completed comparison](../performance/postfinal-public-v6/NATIVE-ARCHIVE-V1.md)
and the [five original engines](../performance/postfinal-public-v5/NATIVE-ARCHIVE-V1.md)
before rebuilding Rust. The actual new Rust source is
`94de5c9ea872bb3649a24a49e99abf5f4e4acd42cfd6d2695f7d17d101f6b888`;
the new native engine is
`1d0851d461fcb4caf4873a4c6fb30c1fd133dfb2140b0602622b9d06e9c1f0d1`;
and the unchanged native bridge is
`81fc4c4a92005f0588dd9b811988587d4d421dd8e1102eebcab53f4deb27cd36`.

An initial isolated version-three safety-control child exited with
**SIGKILL**. Release memory retained by completed workers and rerun the
controls successfully. The signal does not establish why the child was
killed; do not label it an out-of-memory event.

Independently verify both fresh
[from-scratch](../candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V3.json)
and
[independent-execution](../candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V3.json)
audits. The rebuilt engine passes **33** native tests,
[223,198 matching checks](../candidates/evidence/rust-v7-edge-oracle-rust-postfinal-assertion-snapshot-v1.json.gz),
[393 Python-object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-ASSERTION-SNAPSHOT-V1.json.gz),
and
[479 callback and scanner checks](../candidates/evidence/rust-v8-observability-rust-qualified-postfinal-assertion-snapshot-v1.json.gz).
All three current engines pass
[1,179,648 direct comparisons against Python](../candidates/evidence/python-re-universal-public-oracle-v5-all.json)
with zero mismatches.

The first new 22-stage run stops without writing a result:
`AssertionError: complete from-scratch audit failed`. Its controller
invoked the historical `audit_from_scratch.run_audit()` instead of the
already passing, source-specific version-three audit.

The first [complete intermediate campaign](../candidates/evidence/rust-v8-rust-postfinal-assertion-snapshot-v1-sealed-campaign.json)
has SHA-256
`9e744de16c6c627715303bcf27ae9ef628b04fcdc078e3ebe9e936204b719db2`.
It passes all 22 stages, but independent review finds that its additive
controller could fall back to the historical audit when the required
current proof is missing. Reject that controller, preserve its report,
and add explicit checks rejecting missing and symlinked proof.

The [accepted, separately preserved campaign](../candidates/evidence/rust-v8-rust-postfinal-assertion-snapshot-v2-sealed-campaign.json)
has SHA-256
`9015b2a02bdf32e1f4dfdb3eb0c8fb8e67d07b78649ccb1ba3ba4da6cd4b76e8`.
Its hardened additive controller has SHA-256
`cdabec673a905b122c474a8279b84f194534fda77a0c70555fb9aa9fd299592d`,
passes **43** synthetic safety controls, and refuses missing or
symlinked evidence without falling back. The original campaign
controller remains unchanged.

All **22** accepted stages pass, including **4,494,555** complete
Unicode comparisons. The official Python test step records **146**
named methods: **144** pass and **2** are skipped because the required
`en_US.iso88591` locale is unavailable. The skipped methods are
`ReTests.test_locale_caching` and `ReTests.test_locale_compiled`;
neither is hidden or counted as passed. No new speed was measured; the
independent final test was not accessed and remains **NOT OPENED**.

## Preserve all five measured engines before rebuilding Rust

Independently preserve the exact **five** C, Rust, and Zig native
libraries from the completed **8,192**-case public benchmark. Bind every
original binary and deterministic compressed archive to the frozen
manifest, all measurements, the complete independent replay, and both
version-two independence proofs. Preserve the earlier five original
native libraries separately; their Rust engine is not the Rust engine
measured in the newer comparison.

Record the first actual archive failure. All five compressed files are
successfully and exclusively created, but the final proof is rejected
before publication because Python's version is a tuple in memory and a
list in JSON. Independently verify every original and compressed byte;
normalize the version; and complete the exact interrupted archive with
an explicitly guarded, one-use recovery. Never replace an archived
file or discard the failed attempt.

The corrected tool passes **129** adverse-input checks plus **64**
original checks. The new and original archives both independently
verify. Archive verification never reads the live Rust source or native
engine, never starts a candidate, and never measures performance. The
[complete native preservation record](../performance/postfinal-public-v6/NATIVE-ARCHIVE-V1.md)
records all original and compressed hashes. The **65,536**-case final
test remains **NOT OPENED**.

## Prepare fresh proof slots before the next Rust architecture

Preserve the complete, independently replayed **8,192**-case public
comparison and the rejected first Rust engine before preparing another
architecture. The current source, native binary, **5,940** slowdowns,
both independence reports, all Python comparisons, all **12** graphs,
and every previous archive remain unchanged.

Prepare separate, exclusively created version-three source and isolation
audits and an independently versioned Python-comparison report. Preserve
all **76** original independence checks, all **32** isolation checks,
all **five** genuine native roles, all three independent engines, and the
unchanged **8,192 × 48 × 3** public comparison. The
[new requalification record](../candidates/audits/POSTFINAL-REQUALIFICATION-V3.md)
does not claim that a new engine, production report, timing, or holdout
already exists.

No future architecture or speed is guessed. The final **65,536**-case test
remains **NOT OPENED**.

## Measure and reject the first Rust matching-state architecture

Run the current Python, Rust, C, and Zig engines only after pushing their
exact, source-bound **8,192**-case protocol. Preserve all **425,984**
observations, **1,277,952** exact-answer checks, **24,579** independently
recomputed confidence intervals, and **65,544** native-isolation checks.
The replay confirms all **12** original operations and **260** workload
categories without importing a candidate or opening the final test.

The current Zig engine reaches **1.213742×** Python and **4,680** clearly
faster cases; C reaches **1.124233×** and **4,511**; the rebuilt Rust
engine reaches **0.957154×** and **2,444**. None meets the **1.5×** or
**4,916/8,192** targets. Retain all **5,940** slowdowns: **1,401** Zig,
**1,433** C, and **3,106** Rust.

Reject the Rust inline-state hypothesis without hiding its passing
correctness proofs or its negative result. Its confidence interval,
**0.947638–0.967306×**, is below Python's baseline. The archived prior
Rust engine was measured in a separate run; do not claim a paired
before-and-after significance that was never measured.

Generate and validate all six clear current-result graphs plus six standard
graphs directly from the independently verified replay. The
[complete current results](../performance/postfinal-public-v6/RESULTS.md)
preserve every case, source fingerprint, confidence interval, slowdown,
and memory limitation. The **65,536**-case final test is **NOT OPENED**;
there is no winner.

## Correct the inherited current-result chart audit

The first standard-graph production run rejects the real, independently
verified current results before creating an output. Its frozen, inherited
chart validator still expects the original `FROM-SCRATCH-AUDIT.json`,
while the current benchmark correctly uses
`POSTFINAL-FROM-SCRATCH-AUDIT-V2.json`.

Preserve the failure and both independence checks. Rebind only the
inherited, source-verified chart context to the exact passing version-two
audit; restore the original context afterward. Add an explicit test that
rejects the historical audit path. The corrected renderer passes all
**168** synthetic adverse-input checks and separately validates the real
frozen manifest, measured summary, and independent replay without timing
an engine or generating a standard graph. The separate clear presentation
already passes all **84** of its own checks.

The inherited detailed memory graph initially also describes whole-process
memory as unmeasured. Preserve the reviewed discrepancy and correct only
the source-bound memory graph: worker RSS and high-water observations
are measured, while per-allocation native attribution and final memory
remain **NOT MEASURED**. Four independent synthetic checks reject the
old wording and any false claim that native memory was measured.

No correctness test, candidate, benchmark observation, historical result,
or hidden final test is changed.

## Prepare clear graphs for the exact current engines

Complete the frozen **8,192**-case public measurement before running any
chart self-test or changing an engine. Preserve every original observation
and require an independently replayed, source-bound result before either
renderer can produce a graph or claim a speed.

The original standard six-graph renderer passes **163** in-memory adverse-input
checks. The plain-language six-graph renderer separately passes **84**.
Both preserve the exact current Rust, C, and Zig engine fingerprints;
all **12** compatibility proofs; both fresh independence audits; all
**260** case categories; and all frozen case weights.

Derive the candidate rankings, **1.5×** speed target, **60%** faster-case
target, and every slowdown from the actual independently verified result.
Do not copy the archived **5,173** slowdowns or any historical ranking.
Keep the older graphs unchanged, mark exact native memory **NOT MEASURED**,
and leave the **65,536**-case final test **NOT OPENED**.

## Freeze a fair comparison for the newly rebuilt Rust engine

Keep all **8,192** original public cases, **260** workload categories,
**12** Python operations, equal weights, original seeds, **four** warmups,
**13** paired trials, and **2,000** confidence resamples. Bind the pinned
Python baseline, unchanged C and Zig engines, newly rebuilt Rust engine,
all **12** source-bound compatibility proofs, both fresh independence
audits, and **1,179,648** passing Python comparisons.

Preserve the first failed freeze. It stops before creating a manifest,
starting a worker, timing an operation, or accessing the final test.
The unchanged deep-contract validator correctly requires the explicit
`PYTHONPATH=.` environment even when isolated Python already has the
canonical repository on `sys.path`. Independently rerun the exact
unmodified validator with that environment: all **12** mixed Rust, C,
and Zig proof roles pass. Change no test, evidence, engine, or validator.

The corrected freeze exclusively creates the public manifest with SHA-256
`65e024a1a79d13b03e4e5ad0f3d4ae010dbb6e4f09b52a8542837a2ea4c6198a`.
Its source-bound runner passes **43** additional adverse-input controls,
**seven** Unicode framing controls, all inherited safety checks, and the
complete three-engine proof chain. It refuses timing until its runner,
manifest, and [frozen public protocol](../performance/postfinal-public-v6/PROTOCOL.md)
are clean, committed, and pushed to `main`.

This freeze performs no benchmark. All current speed, memory, regressions,
and confidence intervals remain **NOT MEASURED**. The **65,536**-case
final test is **NOT OPENED**.

## Requalify Rust's first from-scratch matching-state optimization

Preserve the original, exactly archived C, Rust, and Zig native engines
and their **8,192** public speed measurements before changing any source.
Keep those charts and speed results explicitly historical: they do not
measure the new Rust engine.

Change only Rust's owned matching executor. Store up to **eight** active
recursion guards and repeat states in local stack arrays instead of
allocating a separate heap vector for each match. Preserve the original
heap-backed behavior for larger patterns, the unchanged Python bridge,
independent Rust parser and executor, and zero external regex packages.

Rebuild the Rust engine offline, pass all **20** owned Rust release tests,
and qualify all three current candidates with fresh **76**-control source
and **32**-control isolation reports.
The frozen public Python oracle passes **1,179,648** comparisons with
zero mismatches. The changed Rust engine separately passes **223,198**
matching checks, **393** Python-object checks, **479** callback, buffer,
and scanner checks, and all **22** compatibility stages, including
**4,494,555** Unicode checks.

An inherited, read-only Rust formatting check reports unrelated existing
formatting differences; do not reformat or modify those original lines.
The first observability invocation also rejects an incorrectly named
output before creating a file. Preserve that failure and pass the
unmodified suite using its required `rust-v8-observability-rust-qualified`
output prefix. Record every passing source-bound report and exact binary
fingerprint in the [Rust optimization report](../candidates/evidence/RUST-POSTFINAL-INLINE-STATE-V1.md).

This chunk records no timings. The new Rust speed and memory remain
**NOT MEASURED**; the **65,536**-case final test remains **NOT OPENED**.
There is no winner.

## Preserve the exact original native binaries

The five native libraries used in the 8,192-case public comparison are
excluded by the repository's `*.so` rule. Verify their exact recorded
contents, original `0700` modes, public source proofs, and both
independence audits before attempting to archive them.

The first archive attempt genuinely fails closed: its general **16 MiB**
JSON bound rejects the independently recorded public results, which occupy
exactly **18,125,531 bytes**. Neither the one-use archive directory nor its
manifest is created. Preserve the failure and correct only the explicit,
hash-pinned public-summary limit; do not increase the limit for other
inputs, change any existing engine, or claim that the failed attempt
produced an archive.

The corrected, independently reviewed archiver passes all **64** in-memory
corruption controls. Its single successful production run preserves all
five original libraries, their exact **1,558,568** bytes and `0700`
permissions, and all original source and proof fingerprints in **563,840**
bytes of deterministic, timestamp-free compressed evidence. An independent
bounded verification authenticates all five archives without reading a
current native library, importing a candidate, or running a benchmark.
The [complete historical archive](../performance/postfinal-public-v5/NATIVE-ARCHIVE-V1.md)
does not claim reproducible compiler output, a current loaded engine,
new correctness, a hidden test result, or improved performance.

## Preserve independent checks before changing any engine

The complete public correctness and performance evidence authenticates
exact native-library and Rust, C, and Zig source fingerprints. Running the
original audit after an optimization would overwrite the historical
76-control proof; the original compatibility runner also exclusively owns
already published result files. Do not change an engine or reuse those
certificates.

Prepare separate, exclusively created paths for a fresh **76**-control
source audit, a fresh **32**-control native-isolation audit, and the
unchanged **8,192**-case Python comparison. Retain the original Python
case distribution, **48** documented observations per case, and all
**1,179,648** candidate comparisons. Require all original source hashes,
actual native mappings, and candidate-free poison controls before any
production report. The
[append-only requalification plan](../candidates/audits/POSTFINAL-REQUALIFICATION-V2.md)
does not claim a new report, changed engine, measured speed, or opened
final test.

The source-audit wrapper reruns all **76** original controls and passes
**52** additional in-memory checks. The independently reviewed isolation
wrapper passes **56** checks and rejects a substituted historical report.
The Python comparison passes **66** checks without reading a source file
during its candidate-free self-test. Production audit records are
exclusively created and synced through their containing directory; every
actual audit requires the pinned isolated Python **3.14.6** interpreter.
All three future production reports remain **NOT CREATED**.

A read-only build-command search also unintentionally matched unrelated
legacy final-runner source. It did not open final benchmark evidence,
materialize a case, read a private guard or key, or measure performance.
Subsequent architecture inspection is restricted to explicitly named,
currently owned production files and public audit sources.

## Audit and exercise a real four-engine final-test adapter

Implement a separate four-channel adapter, standalone native statistics
helper, independently written source auditor, and fixed-public-key verifier.
Keep the **65,536-case** production holdout unopened. The adapter preserves
the original isolation guard byte for byte while independently comparing
compiled metadata, results and captures, exception details, and callback,
converter, warning, and scanner behavior.

The first standalone auditor repeatedly exits `137`; preserve and diagnose
the failure instead of accepting its JSON as a passing process. Replace its
benchmark-runner dependency with bounded direct verification of the two
existing public audits, all **16** owned source files, and all **five**
native libraries. Verify the complete auditor under a **192 MiB** memory
limit; it passes all **63** source and anti-delegation controls without a
worker, holdout, or timing.

Exercise the four actual isolated Python, Rust, C, and Zig workers on
**2,176** publicly generated fixed-key cases. All **16** expression
families, **16** input categories, and **nine** applicable regex operations
pass **26,112** independently reconstructed behavior checks and **17,416**
native-mapping checks with zero mismatches. Preserve the original audits,
the independently generated new source proof, all exact smoke-test counts,
and the from-scratch C statistics helper in the
[four-channel adapter audit](../performance/postfinal-fresh-holdout-v1/ADAPTER-AUDIT.md).

The first independently passing audit and public run exposed one trailing
space in the new native statistics source when the final formatting gate ran.
Preserve both original evidence files exactly. Correct the single space,
independently rerun all **63** audit controls and all **2,176** four-worker
public cases, and exclusively create version-two audit and public-run
records. The version-two audit checks the exact fingerprints of both retained
version-one records. The corrected native helper separately passes all
**38** synthetic statistical controls; no final cases are generated.

A fresh attempt to rerun the original public-results replay also correctly
refuses to overwrite its existing independently verified evidence. Record
that no-write failure and remove the non-repeatable command from the README.
Instead, recheck the entire original uncompressed observation fingerprint
and use the source-bound, repeatable presentation check to authenticate all
**425,984** original observations, **24,579** recorded confidence intervals,
**5,173** slowdowns, and all six unchanged headline graphs. Preserve the
original passing replay and every measurement unchanged.

The production controller is still not integrated or frozen. The fresh
one-use guard, production randomness, cases, timing, and winner remain
**NOT MEASURED** and **NOT OPENED**.

## Make all verified benchmark graphs clear and readable

Create six new, accessible graphs directly from the independently verified
**8,192-case** results. The headline compares Zig, C, and Rust with Python
and explicitly marks both the **1×** baseline and **1.5×** goal. The
outcome chart shows every clearly faster, uncertain, and slower case and the
**60%** goal. Detailed charts preserve all **12** operations, actual
Python-visible memory, and the exact ranking.

Replace the impractically tall slowdown view with one compact graph
containing all **5,173** genuine, individually labeled slowdowns. Verify
every original case, candidate, frozen weight, native-isolation proof,
confidence interval, memory limitation, and raw-evidence fingerprint before
rendering. Reject **37** independently poisoned inputs in a candidate-free
synthetic self-test. Preserve the original graphs without overwriting them.

The [verified public result](../performance/postfinal-public-v5/RESULTS.md)
continues to disclose the failed speed target and unopened final test; no
measurement, held-out case, or new candidate behavior is inferred from a
presentation change.

## Measure and independently replay all 8,192 public cases

Complete the prospectively frozen, Unicode-safe public comparison against
unmodified Python **3.14.6** and all three independently written engines.
Record all **425,984** paired timings, **1,277,952** exact-answer checks,
**24,579** independently recomputed confidence intervals, and **65,544**
native-library and process-isolation guards. All **8,192** cases, all
**12** Python regex operations, and all **260** workload categories pass
for Rust, C, and Zig, with zero correctness failures.

The verified overall public speeds are **1.217×** for Zig, **1.136×** for
C, and **1.010×** for Rust. Their clearly faster case counts are
**4,689/8,192**, **4,709/8,192**, and **2,866/8,192**, respectively. None
reaches the required **1.5×** speed or **4,916/8,192** faster-case
threshold. Preserve all **5,173** regressions of more than 20%, including
their operation and exact case, in the raw data, independently verified
summary, operation table, and six reproducible graphs.

Record the complete results and source-bound evidence in the
[verified 8,192-case public comparison](../performance/postfinal-public-v5/RESULTS.md).
Keep the failed earlier run, its **310,700** original observations, and the
historical failed one-use final unchanged. The separate **65,536-case**
holdout remains unopened; its complete four-channel isolated executor is
still **NOT IMPLEMENTED**. There is no final replacement or winner.

## Freeze the Unicode-safe public comparison before measuring

Freeze the corrected **8,192-case** public comparison separately from its
failed predecessor. Preserve the same **260** workload categories,
**12** operations, **13** paired trials, random seeds, equally weighted
cases, Python baseline, and three independently written Rust, C, and Zig
engines. Change only the private JSON communication so that Python strings
containing lone Unicode surrogates cross the worker pipe without corruption.

Authenticate all **310,700** preserved failed-run rows, both candidate
isolation audits, five actual native libraries, all **12** current-source
compatibility proofs, and **1,179,648** zero-difference Python comparisons.
The candidate-free runner passes **13** Unicode and framing controls; the
six-chart renderer passes **94** integrity and evidence-poisoning controls.
Freeze **425,984** paired observations, **1,277,952** correctness checks,
**24,579** confidence intervals, and **65,544** runtime integrity checks
before timing begins.

Record the exact manifest, source hashes, operation counts, unchanged
seeds, preserved predecessor, memory limitations, and slowdown policy in
the [Unicode-safe public speed protocol](../performance/postfinal-public-v5/PROTOCOL.md).
The final **65,536-case** holdout remains unopened and its isolated
executor remains **NOT IMPLEMENTED**. No speed or winner is inferred from
this freeze.

## Preserve a failed public run and its Unicode transport defect

The fully frozen **8,192-case** public speed comparison writes exactly
**310,700** complete, source-bound timing rows for **5,975** cases before
stopping. The next case contains a lone Unicode surrogate. Its strict UTF-8
worker pipe rejects the runner's `ensure_ascii=False` request before Python,
Rust, C, or Zig can execute matching. Independently reproduce the identical
`UnicodeEncodeError` in all four isolated workers without taking another
timing or importing an engine into the controller.

Preserve the valid, incomplete gzip stream, frozen manifest and source,
prepare-only diagnostic, exact failure position, and original trial and case
denominators in the
[complete interrupted public result](../performance/postfinal-public-v4/RESULTS.md).
There is no final summary, confidence interval, overall speed, memory
conclusion, chart, or winner. Fix the transport only in a separately frozen
benchmark version; never overwrite the existing slot. The fresh holdout
remains unopened.

## Freeze a larger, fully qualified public speed comparison

Freeze **8,192** unique public cases, all **260** workload categories, all
**12** public regex operations, and exactly **13** paired trials before
recording any timing. The four isolated engines must eventually produce all
**425,984** observations, **1,277,952** correctness gates, **24,579**
confidence intervals, and **65,544** runtime integrity checks. Freeze the
selection, ordering, bootstrap seeds, five actual native libraries, both
source-ownership audits, the complete zero-mismatch larger oracle, and all
**12** current candidate proofs.

The first freeze intentionally fails closed: the strict source allowlist
omits the project's already audited root `pyproject.toml`. Add only that
exact resolved, nonsymlinked build file; continue rejecting root traversal,
absolute paths, alternate names, and unowned sources. The passing freeze
creates the separately fingerprinted manifest without running a candidate,
timing an operation, or opening a holdout.

Record the exact manifest, source hashes, all operation counts, memory
limitations, and future slowdown policy in the
[expanded public speed protocol](../performance/postfinal-public-v4/PROTOCOL.md).
The fresh **65,536-case** holdout adapter is not implemented; no final
performance or winner is inferred.

## All current engines pass the complete Python and Unicode campaign

Run the unchanged **22-stage** resource-limited compatibility campaign
against the repaired Rust, C, and Zig implementations. All three pass every
stage, including official Python tests, the complete public module surface,
callbacks and replacements, independent source and native-library ownership,
crash and depth controls, and **4,494,555** full-Unicode comparisons per
engine. Every report verifies the matching, object, tracing, native, and
immutable-goal fingerprints.

An initial concurrent Zig invocation stops before creating evidence because
its freshly executed static audit fails under contention. Verify that the
current independently stored source audit is unchanged and passing, then run
Zig alone. Its complete solo report genuinely passes **22/22** stages. Do not
discard the incident, claim the incomplete attempt passed, or weaken any
audit.

Preserve all three exact campaign hashes in the
[full matching, object, tracing, and Unicode evidence](../candidates/evidence/POSTFINAL-UNIVERSAL-STAGE05-EDGE.md).
No expanded performance comparison, hidden case, memory result, or one-use
holdout is opened or measured.

## All repaired engines preserve Python's visible behavior

Run all **479** frozen callback, scanner, warning, buffer, error, argument,
and object-lifetime checks independently against Rust, C, and Zig. Each
engine matches Python's complete observation digest, passes all **34**
native argument-binding controls, and has zero candidate, reference,
iterator, or binder failures. The three proofs are cross-linked to the
current matching, object, source, and native-library evidence.

Record all three passing source-bound reports in the
[matching, object, and visible-behavior evidence](../candidates/evidence/POSTFINAL-UNIVERSAL-STAGE05-EDGE.md).
The independent full Unicode campaign remains a separate gate. No candidate
timing, memory, hidden fixture, or fresh holdout is accessed.

## All repaired engines pass the independent object contract

Run the unchanged **393-case** pattern and match object suite separately
against the current Rust, C, and Zig implementations. Each passes all **393**
observations with zero public differences, zero standard-library
self-mismatches, **13** forbidden-regex controls, and **10** cross-engine
guards. Every proof is linked to that engine's newly passing matching report
and the exact current source and native libraries.

One initial C invocation correctly rejected an incorrect `VM` report name
before running the suite or creating any evidence. The immutable test names
the C family `C`; preserve the correct `C` proof and require the expanded
benchmark and chart renderer to validate that exact file.

Record all three report hashes in the
[matching and object-contract evidence](../candidates/evidence/POSTFINAL-UNIVERSAL-STAGE05-EDGE.md).
Current timing, tracing, and final Unicode qualification are not inferred.

## All repaired engines pass the frozen matching and parser test

Run the unchanged **223,198-check** matching oracle separately against the
current Rust, C, and Zig sources. Each candidate passes every byte, Unicode,
scanner, bounded-window, parser, and object case, including the independently
generated **14,783-case** object and **20,480-case** parser suites. All three
match Python's complete observation digest and produce new deterministic,
source-bound evidence.

Preserve the three exact reports and fingerprints in the
[full matching and parser evidence](../candidates/evidence/POSTFINAL-UNIVERSAL-STAGE05-EDGE.md).
The broader standalone public-object, tracing, and **22-stage** campaign
remain separate gates. No speed, memory, hidden fixture, or new holdout is
accessed.

## All three engines pass the larger public compatibility test

The original frozen **8,192-pattern** test exposed **693** Rust, **368** C,
and **355** Zig differences. The first complete, independently repaired run
preserves all **1,179,648** comparisons: C and Zig pass, while Rust retains
**306** differences. Its first **256** records all concern the nested
exception Python creates for a repeated named group; the remaining **50**
records are counted and fingerprinted, not silently assumed to be the same.

Direct, isolated CPython checks also show that all six compiled matching
operations evaluate `pos`, then `endpos`, before validating a string or
acquiring a buffer. Independently repair the Rust, C, and Zig bridges and
their owned duplicate-group handling. Repair the C and Zig matchers so
newline quotes and multiline anchors cannot enter an invalid quote shortcut.

The next separately versioned full run passes **393,216/393,216** checks
for each candidate: **1,179,648** comparisons, zero mismatches, zero crashed
workers. Refresh the **76** source/native-library controls and **32**
isolated anti-delegation controls against the exact current sources. Preserve
the initial failures, intermediate complete failure, both historical audit
reports, immutable oracle, versioned runners, and final passing report in the
[complete expanded correctness evidence](../candidates/evidence/PYTHON-RE-UNIVERSAL-PUBLIC-ORACLE-STAGE03.md).

No candidate uses Python's regex engine, another candidate, or an external
regex package. Current speed, current memory, and the fresh **65,536-case**
holdout remain **NOT MEASURED**. The historical hidden failure remains
unchanged.

## A broader public oracle finds real failures in all three engines

The new
[universal public oracle](../candidates/evidence/PYTHON-RE-UNIVERSAL-PUBLIC-ORACLE-V1.md)
independently generates **8,192** cases from **16** regex families,
**16** input and buffer strata, and **32** deterministic variants. Every case
has exactly **48** checks covering pattern errors, all public regex
operations, captures, replacements, scanners, Unicode, bytes, invalid
buffers, callbacks, warning details, and observable argument evaluation.

Each candidate and the pinned Python reference run in separate guarded
processes. The complete **393,216-check** comparisons fail for Rust
(**693** mismatches), C (**368**), and Zig (**355**). Preserve all three
source-bound failure reports, exact seeds, mismatch digests, and bounded
reproducers. The first recorded Rust differences concern Python's observable
argument-conversion ordering; C and Zig also expose newline-sensitive
lookahead and duplicate-name exception chaining.

An initial Zig harness failure is
[separately preserved with its complete traceback](../candidates/evidence/PYTHON-RE-UNIVERSAL-V1-INITIAL-ZIG-WORKER-FAILURE.md).
It was fixed by initializing standard-library `ctypes` before installing the
permanent native-loader guard. The subsequent **355** mismatches are genuine
candidate results, not that harness failure. No candidate qualifies, no
performance or hidden case was run, and the expanded benchmark intentionally
refuses to freeze until every candidate passes all **1,179,648** checks.

## A fresh 65,536-case final is specified, not opened

The new
[one-time holdout protocol](../performance/postfinal-fresh-holdout-v1/PROTOCOL.md)
fixes **16** independently generated expression families, **16** input and
lifecycle strata, and **256** cryptographically separated variants: exactly
**65,536** previously unseen cases. Its eventual four-engine, **19-trial**
comparison would contain **4,980,736** observations, **14,942,208**
four-channel candidate-correctness checks, and **196,611** prospectively
specified confidence intervals.

The generator's independently run self-test passes all exact population and
one-use invariants using only a public, nonproduction key. It creates no
guard, draws no secret, imports no candidate, measures no operation, and
generates no real holdout case. The actual freeze first requires the current
source-bound Rust, C, and Zig proofs and a passing, freshly generated
all-candidate public differential. The sole production key cannot be drawn
until the source and manifest are committed, pushed, and rechecked against
the remote, with a durable exclusive one-use guard already in place.

The eventual four-channel executor has **NOT BEEN IMPLEMENTED**. Its opening
therefore fails closed; final accuracy, timing, memory, and rankings remain
**NOT MEASURED**. This additive prospective protocol never reopens or
repairs the failed original hidden final.

## Separate engine processes close the hidden-wrapper loophole

The historical **76-control** independence check is retained and still
passes. An independent review found that checking a separate short-lived
process did not prevent a measured engine from discovering Python's already
loaded regex module through `enum`, `json`, or an aliased module registry.

The new
[32-control isolation audit](../candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V1.json)
rejects direct, cached, conditional, reflective, third-party, and
cross-candidate delegation. All **32** adversarial controls and all **76**
original controls pass. The four engine families each complete **18**
callback-safe operations in their own guarded process; all five loaded
native libraries are individually checked against their exact source-bound
fingerprints.

The first genuine audit exposed a false positive: a positional replacement
count triggered Python's deprecation-warning formatter, which itself imports
`re`. Changing the audit's own smoke call to the equivalent `count=1`
keyword fixes that legitimate warning path without permitting engine
imports or weakening any guard. The audit explicitly does **not** claim a
hermetic compiler build or mathematical proof of future unexecuted paths.
No performance or held-out input was used.

## A from-scratch direct Rust matcher passes the complete compatibility gate

Rust now classifies its own compiled bytecode once. Expressions containing
only validated straight-line instructions and fixed-count repetitions run
through a new, allocation-free Rust interpreter. Branches, assertions,
variable repetition, and every uncertain instruction continue through the
original Rust backtracking engine. Neither path calls Python's regex engine,
another candidate, or an external package.

The exact source passes **223,198** independent edge comparisons,
**393** family-bound public-object checks, **479** tracing and lifetime
checks, all **22** sealed correctness and safety stages, and another
**83,968** quote-specific comparisons. All **20** optimized Rust unit tests
also pass. The original 76-control audit binds the current sources and five
loaded native libraries. Complete hashes and reports are in the
[direct Rust evidence](../candidates/evidence/POSTFINAL-RUST-DETERMINISTIC-04.md).

Preserved diagnostics include an overly broad static control that mistook the
CPython-compatible scanner's displayed `_sre.SRE_Scanner` type name for an
engine import, and preliminary object and tracing reports that were correct
but did not identify the candidate family strongly enough. The subsequently
passing sealed campaign uses the family-bound proof and retains all three
diagnostics; no failure was removed or silently converted into a pass.

Speed is **NOT MEASURED**. The existing **4,096-case** public results remain
the latest measured comparison. A larger **8,192-case** public comparison
and a separately generated **65,536-case** one-use holdout are being
prepared, not claimed as measured. The original consumed hidden final
remains **FALSIFIED**.

## One-pass Rust metadata is measured and independently verified

The prospectively frozen
[version-3 public experiment](../performance/postfinal-public-v3/RESULTS.md)
compares pinned Python 3.14.6 against the separately written C, Rust, and Zig
engines on **4,096** identical public cases, all **260** workload categories,
all **12** operations, and **13** paired trials. Its
[complete raw dataset](../performance/postfinal-public-v3/evidence/postfinal-public-practice-v3-raw.jsonl.gz)
contains **212,992** observations. All **638,976** correctness gates pass;
the independent, candidate-free
[integrity replay](../performance/postfinal-public-v3/evidence/postfinal-public-practice-v3-integrity.json)
recomputes all **12,291** confidence intervals and retains all **2,313**
cases that were more than 20% slower than Python.

C is **1.217×** as fast as Python (95% interval **1.200–1.233×**;
**2,637/4,096** clearly faster; **461** substantial slowdowns), Zig is
**1.215×** (**1.196–1.236×**; **2,156/4,096** faster; **786** slowdowns),
and Rust is **1.115×** (**1.096–1.135×**; **1,664/4,096** faster;
**1,066** slowdowns). No engine reaches **1.5×**. C's and Zig's intervals
overlap; their ranking does not establish that either is reliably faster than
the other.

Rust's single-pass bridge changes only its own compiled-pattern metadata
handling. All **54/54** quote-aware splitting cases remain clearly faster,
averaging **11.81×** without a substantial slowdown. The earlier Rust
snapshot was **1.100×**, with **1,116** substantial slowdowns; these runs
are separately measured, so no paired cross-run improvement or causal claim
is made. Native process memory remains **NOT MEASURED**. The consumed
original hidden test remains failed and was not reopened.

## The next Rust bridge removes repeated metadata work

The last complete public result identifies **1,041** substantial Rust
slowdowns among **3,173** compiled-pattern calls. The next experiment changes
only Rust's independently written native Python bridge: eligible compiled
patterns now collect metadata in one strongly referenced, version-guarded
pass. Splitting and replacement use the same mechanism. Partial slot reads
roll back safely and use the original descriptor-aware fallback; template
creation, subclass observations, audit hooks, Python signatures, buffer
lifetimes, and free-threaded safety remain unchanged.

The precise new source passes the original **76-control**, five-library
from-scratch audit, its fresh
[223,198-case matching oracle](../candidates/evidence/rust-v7-edge-oracle-rust-post-final-stage-03-slot-batch.json.gz),
[393 public-object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POST-FINAL-STAGE-03-SLOT-BATCH.json.gz),
[479 tracing and argument checks](../candidates/evidence/rust-v8-observability-rust-qualified-post-final-stage-03-slot-batch.json.gz),
and
[all 22 original correctness stages](../candidates/evidence/rust-v8-rust-post-final-stage-03-slot-batch-sealed-campaign.json).
A fresh, separately isolated
[83,968-observation quote oracle](../candidates/evidence/rust-postfinal-quote-parity-stage-03-slot-batch-oracle.json)
also passes with zero mismatches.

The
[version-3 prospective protocol](../performance/postfinal-public-v3/PROTOCOL.md)
fixes the same **4,096** public case IDs, all four engines, **13** paired
trials, and **2,000** confidence draws. Its manifest SHA-256 is
`5f49f255271b8f71786e7fa67a61827b53c1330e1ad7afe29c8750991df4b90f`.
Its actual speed, confidence, memory, rankings, and slowdowns are **NOT
MEASURED** until the protocol is committed and pushed before the complete
run. The one-time hidden final remains falsified and unopened.

## The Rust quote matcher fixes all 54 target cases, not the overall goal

The version-2
[complete independently verified public result](../performance/postfinal-public-v2/RESULTS.md)
measures pinned Python, C, Zig, and the independently implemented quote-aware
Rust engine on the same **4,096** previously selected public cases. The
complete
[212,992-observation raw dataset](../performance/postfinal-public-v2/evidence/postfinal-public-practice-v2-raw.jsonl.gz)
passes all **638,976** correctness gates. The
[candidate-free replay](../performance/postfinal-public-v2/evidence/postfinal-public-practice-v2-integrity.json)
recomputes all **12,291** confidence intervals, verifies all five native
libraries and the original **76** anti-delegation controls, and retains every
one of **2,366** substantial slowdowns.

In the same paired run, Zig is **1.216×** (range **1.197–1.237×**,
**2,130/4,096** faster, **771** slowdowns); C is **1.213×** (range
**1.196–1.229×**, **2,597/4,096** faster, **479** slowdowns); and Rust is
**1.100×** (range **1.082–1.120×**, **1,589/4,096** faster, **1,116**
slowdowns). **No candidate reaches 1.5×.** All six
[prospectively fixed graphs](../tools/postfinal_public_practice_charts_v2.py)
are generated from the independently replayed observations.

The Rust change succeeds on its actual target: all **54/54** formerly slow
quote-aware CSV cases are statistically faster than Python, with **11.205×**
geometric-average public speed and zero slowdowns. The
[separate 83,968-observation property oracle](../candidates/evidence/rust-postfinal-quote-parity-stage-02-oracle.json)
also records zero mismatches. The previous and current snapshots were
measured separately; no paired cross-run confidence or causality is claimed.
The hidden final remains failed and was not reopened.

## A from-scratch Rust quote matcher is qualified; its speed is not measured

The version-1 public run exposed 54 substantial Rust slowdowns in a category
using quote-aware delimiters. The next candidate recognizes the equivalent
pattern from its **own parsed Rust expression**, verifies captures, character
classes, scoped flags, repeat modes, and newline-sensitive anchors, and scans
the suffix with Rust's own existing byte-search code. It does not call Python's
regex implementation, C, Zig, or an external package. All uncertain patterns,
wide Unicode representations, and unsupported flags retain the original Rust
matcher.

The original **76-control**, **five-native-library** independence audit passes.
The
[first failed sandboxed audit and explicitly authorized unchanged retry](../performance/v7/evidence/POSTFINAL-RUST-QUOTE-PARITY-INDEPENDENCE-INCIDENT.md)
are both retained. The changed source also passes its fresh
[223,198-case matching proof](../candidates/evidence/rust-v7-edge-oracle-rust-post-final-stage-02-parity.json.gz),
[393 public-object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POST-FINAL-STAGE-02-PARITY.json.gz),
[479 observability checks](../candidates/evidence/rust-v8-observability-rust-qualified-post-final-stage-02-parity.json.gz),
and the
[original complete 22-stage campaign](../candidates/evidence/rust-v8-rust-post-final-stage-02-parity-sealed-campaign.json),
including **4,494,555** Unicode checks.

The separate
[quote-parity differential oracle](../tools/rust_postfinal_quote_parity_oracle.py)
adds **83,968** exact Python-versus-Rust observations across **1,312**
deterministic cases. Its
[complete source-bound evidence](../candidates/evidence/rust-postfinal-quote-parity-stage-02-oracle.json)
records **zero mismatches**, separately isolated standard-library and Rust
workers, all original native-library fingerprints, six anti-delegation
controls, all text and buffer representations, scanner and split edge cases,
invalid expressions, scoped flags, captures, escaped separators, and
newline-sensitive anchors. Its synthetic controls pass without importing a
candidate, opening a benchmark, or reading a hidden case.

The
[version-2 prospective public protocol](../performance/postfinal-public-v2/PROTOCOL.md)
freezes exactly the same **4,096** public case IDs, all **260** categories,
the same **12** operations, Python, C, Rust, and Zig, **13** paired trials,
and **2,000** confidence draws before timing. Its manifest SHA-256 is
`2228e444ae142494def731d8b94ba5fcf08c69aa8a7e04cc1c47cbebeb149b4a`.
Its selection, source hashes, original independence proof, native libraries,
and all three candidates' matching proofs are fixed. New speed, confidence,
memory, rankings, and slowdowns are **NOT MEASURED**. The failed hidden final
is not reopened or retried.

## The frozen 4,096-case public benchmark exposes much smaller speedups

The new [post-final public protocol](../performance/postfinal-public-v1/PROTOCOL.md)
fixes **4,096** equal-weight public cases, **260** workload categories, all
**12** regex operations, pinned CPython **3.14.6**, and the existing
independently written Rust, C, and Zig engines. Its
[prospectively frozen manifest](../performance/postfinal-public-v1/manifest.json)
uses only the audited **10,312-case public calibration archive** and its
**9,731** safely bounded cases. It generates and decodes **zero** hidden
records and leaves the original 700-case pilot unchanged.

The protocol fixes **13** shuffled paired trials, **2,000** confidence draws,
at most **16** real calls per sample, **212,992** complete observations, and
**638,976** mandatory correctness checks. Its runner verifies the original
76-control, five-native-library audit and all three frozen edge proofs before
importing a candidate for timing. Source, seeds, coverage, candidate hashes,
case weights, regression thresholds, and full result reporting were committed
and pushed at `5a65274dc1f2e4190e16ee5c193d6379515666bd` before timing.

The [complete public run](../performance/postfinal-public-v1/evidence/postfinal-public-practice-v1-summary.json)
then genuinely completed all **4,096** cases and
[all **212,992** compressed raw observations](../performance/postfinal-public-v1/evidence/postfinal-public-practice-v1-raw.jsonl.gz).
Every sample passed its three correctness gates. The
[candidate-free independent replay](../performance/postfinal-public-v1/evidence/postfinal-public-practice-v1-integrity.json)
verified all **638,976** checks, all **12,291** recomputed confidence ranges,
the exact manifest, all five current native libraries, and every one of
**2,548** substantial slowdowns.

In the same run, C is **1.222×** (range **1.205–1.238×**,
**2,689/4,096** clearly faster, **449** slowdowns); Zig is **1.215×**
(range **1.196–1.236×**, **2,188/4,096** clearly faster, **797** slowdowns);
and Rust is **1.033×** (range **1.017–1.048×**, **1,504/4,096** clearly
faster, **1,302** slowdowns). **No engine reaches 1.5×.** The
[complete result](../performance/postfinal-public-v1/RESULTS.md) links all six
graphs and names every regression. These are public development results, not
an unseen final test. The original hidden final remains failed and is not
retried.

## Post-final Rust batching is correct but does not prove a speed improvement

This experiment happened strictly **after** the one-time final failure. It
changes only the independently written Rust bridge to collect up to 16 split
matches from its own Rust engine per native call. The original 76-control,
five-library independence audit and all frozen public gates pass: **223,198**
matching checks, **393** public-object checks, **479** observability checks,
and the complete **22-stage** correctness campaign, including all
**4,494,555** Unicode comparisons. The original final candidates, failure,
one-time marker, and hidden cases are not changed or reopened.

The [single fresh four-way public run](../performance/v7/evidence/postfinal-rust-batched-split-01-summary.json)
uses **624** shared public cases, **7** paired trials, **499** confidence
draws, [all **17,472** observations](../performance/v7/evidence/postfinal-rust-batched-split-01-raw.jsonl.gz),
and **52,416** exact correctness checks. Its
[independent integrity replay](../performance/v7/evidence/postfinal-rust-batched-split-01-integrity.json)
checks all five actually loaded native libraries, all three complete
correctness chains, all **1,875** confidence intervals, and all **255**
substantial slowdowns. In that same run, C is **1.335×**, Zig is **1.282×**,
and Rust is **1.136×** as fast as Python; Rust retains **119/624** substantial
slowdowns, including **11/47** split cases. The batched split is therefore
**rejected as a speed improvement**, not described as a final winner.

The [full post-final report](../performance/v7/evidence/POSTFINAL-RUST-BATCHED-SPLIT-01.md)
links all six generated graphs and every regression. The
[preserved independence incident](../performance/v7/evidence/POSTFINAL-RUST-BATCHED-SPLIT-INDEPENDENCE-INCIDENT.md)
records the first actual failed audit, both failed campaign preflights, the
observed `-9` child status, and the unchanged, authorized **22/22** passing
retry. No failed check is removed or silently rerun. The subsequent
[4,096-case public benchmark](../performance/postfinal-public-v1/RESULTS.md)
confirms that the Rust change does not achieve the 1.5× target.

## The one-time hidden benchmark falsifies compatibility

After the three independently built candidates were [frozen before opening](../performance/v9/evidence/FINAL-CANDIDATE-FREEZE.md), the original **24,576-case** protocol ran once. It rejected the Zig engine on the genuine hidden case `v9.split.literal-and-long-prefix.006:warmup:candidates.zig_candidate`: Zig's `split` did not match pinned CPython. The [complete failure report](../performance/v9/evidence/FINAL-HOLDOUT-FAILURE.md) preserves the actual exit status, all frozen candidate and protocol fingerprints, and the [irreversible no-retry marker](../performance/v9/evidence/V9-FINAL-HOLDOUT-24576-UNSEAL-MARKER.json). The [valid compressed partial raw stream](../performance/v9/evidence/V9-FINAL-HOLDOUT-24576-RAW.jsonl.gz) contains exactly **1,778,408** genuine paired rows, covering **14,342/24,576** completed cases before the failure. The [independent failed-run replay](../performance/v9/evidence/V9-FINAL-HOLDOUT-24576-FAILURE.json) verifies the evidence without rerunning a candidate, opening the secret again, or fabricating a complete result. Final speed, confidence intervals, memory, all-case regressions, rankings, and the **1.5×** target are **NOT MEASURED**. **The experiment is falsified; there is no winning replacement.**

The [failure-graph self-test incident](../performance/v9/evidence/FINAL-FAILURE-CHART-SELFTEST-INCIDENT.md) preserves the first actual failed synthetic check: a proposed ranking image did not visibly say **NOT ESTABLISHED**. The graph was corrected without relaxing the check; the final renderer passed all **58** synthetic controls and generated six honest failure graphs from the independently audited, incomplete final run.

## The frozen final runner is repaired without opening the benchmark

The [complete pre-unseal incident report](../performance/v9/evidence/FINAL-PREUNSEAL-MISSING-TIME-INCIDENT.md) preserves the exact first attempted final command and its actual `NameError`: the frozen runner referred to Python's standard-library `time` module before importing it. The failure occurred **before the first worker started, before the one-time marker, and before any hidden case or timing**. The original [final protocol](../tools/rust_v9_holdout_protocol.py), manifest, proofs, stopping commit, and freeze remain byte-for-byte unchanged. The independent [five-check, no-opening launcher](../tools/run_frozen_v9_final.py) verifies the original protocol's exact SHA-256 and runs that identical code with only the genuine standard-library `time` module supplied. At that historical stage, the **24,576-case** final benchmark had not yet run. It subsequently ran exactly once and failed; complete final speed remains **NOT MEASURED**.

## Final candidates are fixed before the hidden benchmark

After the nine complete public practice runs, the [candidate stopping-point report](../performance/v9/evidence/FINAL-CANDIDATE-FREEZE.md) records pushed commit `89e550923ede9cbd558c02f91b235aa17ffaff97`. The unchanged original final protocol created the [exclusive candidate freeze](../performance/v9/evidence/V9-FINAL-CANDIDATE-SELECTION-FREEZE.json) for CPython **3.14.6** and the independently written C, Rust, and Zig engines. At that stopping point it validated all three original matching, public-object, and genuine **22-stage** correctness proofs, the original no-delegation audit, and all five then-loaded native libraries. The freeze correctly records **zero** hidden cases, `opening_read=false`, and `performance_measured=false` **at the time of freezing**. The final subsequently ran once and failed. There is no final winner, and complete final speed is **NOT MEASURED**.

## The C engine safely skips impossible alternative matches

The [independent C matching experiment](../performance/v7/evidence/C-STAGE-21-SINGLETON-SPLIT-MEMCHR.md) first asks its own conservative regex parser whether every branch can begin with exactly the same byte. Only then can it use an ordinary bounded byte search to skip positions that the existing engine already rejects. An independent review checked anchors, empty matches, capture order, memory views, one-byte Unicode, window limits, scanner ownership, and the final match position. The unchanged original oracle passes [223,198 matching comparisons](../candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-21-singleton-split-memchr.json.gz), [393 public-object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-21-SINGLETON-SPLIT-MEMCHR.json.gz), [479 observation and callback checks](../candidates/evidence/rust-v8-observability-vm-qualified-stage-21-singleton-split-memchr.json.gz), and the [complete 22-stage correctness campaign](../candidates/evidence/rust-v8-vm-stage-21-singleton-split-memchr-sealed-campaign.json). The [original from-scratch audit](../candidates/audits/FROM-SCRATCH-AUDIT.json) verifies all independent engines and actual native libraries.

The [ninth public practice run](../performance/v7/evidence/three-qualified-engines-public-practice-v9-summary.json) retains [all 17,472 observations](../performance/v7/evidence/three-qualified-engines-public-practice-v9-raw.jsonl.gz), all **52,416** passing correctness checks, and all **256** substantial slowdowns. C measures **1.334×** (range **1.286–1.389×**, **441/624** clearly faster, **46** slowdowns); Zig measures **1.257×** (range **1.209–1.305×**, **341/624** clearly faster, **96** slowdowns); and Rust measures **1.150×** (range **1.104–1.196×**, **260/624** clearly faster, **114** slowdowns). The [independent replay](../performance/v7/evidence/three-qualified-engines-public-practice-v9-integrity.json) checks all observations, confidence intervals, eight earlier practice runs, both preserved incidents, five native libraries, and three complete correctness campaigns. This run is **public practice version nine**, stored under `performance/v7/evidence`; it is not the separate, sealed final benchmark under `performance/v9`. No paired cross-run improvement or final winner is claimed. The **24,576-case** final benchmark remains unopened and **NOT MEASURED**.

## The Rust engine initializes capture state once

The [Rust capture-initialization experiment](../performance/v7/evidence/RUST-OWNED-CAPTURE-INITIALIZATION-HOIST.md) moves three existing resets outside the independently written matcher's candidate-position loop. Failed attempts already restore every capture, and an independent review checked nested assertions, atomic groups, public visibility, callback ownership, and private compiled-bytecode invariants. The unchanged original matching oracle passes [223,198/223,198 comparisons](../candidates/evidence/rust-v7-edge-oracle-rust-owned-capture-init-hoist.json.gz), [393 public-object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-OWNED-CAPTURE-INIT-HOIST.json.gz), [479 observation and callback checks](../candidates/evidence/rust-v8-observability-rust-qualified-owned-capture-init-hoist.json.gz), and the [complete 22-stage original correctness campaign](../candidates/evidence/rust-v8-rust-owned-capture-init-hoist-sealed-campaign.json). The [original from-scratch audit](../candidates/audits/FROM-SCRATCH-AUDIT.json) verifies all four independent families and five actual native libraries.

The [fresh four-way practice run](../performance/v7/evidence/three-qualified-engines-public-practice-v8-summary.json) preserves [all 17,472 observations](../performance/v7/evidence/three-qualified-engines-public-practice-v8-raw.jsonl.gz), **52,416** passing correctness checks, and every one of **261** substantial slowdowns. C measures **1.328×** (range **1.282–1.382×**, **441/624** clearly faster, **46** slowdowns); Zig measures **1.283×** (range **1.238–1.331×**, **363/624** clearly faster, **96** slowdowns); and Rust measures **1.150×** (range **1.104–1.196×**, **274/624** clearly faster, **119** slowdowns). The [independent replay](../performance/v7/evidence/three-qualified-engines-public-practice-v8-integrity.json) checks all cases, confidence calculations, seven historical runs, both disclosed verification incidents, all five actual native libraries, and three full campaigns. The Rust change remains correctness-qualified, but separately measured practice runs **do not establish a statistically demonstrated end-to-end speed improvement**. The **24,576-case** final benchmark remains unopened and **NOT MEASURED**.

## The Zig engine reuses native attribute names

The [independent Zig bridge experiment](../performance/v7/evidence/ZIG-STAGE-13-INTERNED-DISPATCH.md) reuses seven existing Python attribute names instead of repeatedly recreating them while calling the from-scratch Zig engine. It still performs Python's full attribute lookup, preserving custom objects, descriptors, callbacks, error handling, and scanner ownership. Its [223,198 matching comparisons](../candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-13.json.gz), [393 public-object comparisons](../candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-13.json.gz), [479 tracing and unusual-argument checks](../candidates/evidence/rust-v8-observability-zig-qualified-stage-13.json.gz), and [complete 22-stage correctness campaign](../candidates/evidence/rust-v8-zig-stage-13-sealed-campaign.json) all pass. The unchanged original [from-scratch audit](../candidates/audits/FROM-SCRATCH-AUDIT.json) independently verifies all four implementations, all five actual native libraries, and all **76** anti-delegation checks.

The [fresh four-way practice run](../performance/v7/evidence/three-qualified-engines-public-practice-v7-summary.json) preserves [all 17,472 observations](../performance/v7/evidence/three-qualified-engines-public-practice-v7-raw.jsonl.gz), all **52,416** passing correctness checks, and all **259** substantial slowdowns. C measures **1.316×** (range **1.270–1.369×**, **438/624** clearly faster, **48** slowdowns); Zig measures **1.281×** (range **1.234–1.330×**, **361/624** clearly faster, **95** slowdowns); and Rust measures **1.141×** (range **1.095–1.187×**, **264/624** clearly faster, **116** slowdowns). Every comparison is within this same paired run. Previous measurements, including all **407** slowdowns in the preceding run, remain preserved; no paired performance improvement between separate runs is asserted. The [independent verifier](../performance/v7/evidence/three-qualified-engines-public-practice-v7-integrity.json) checks all observations, losses, confidence calculations, complete campaigns, native libraries, and six earlier measurement histories.

The [reviewer incident record](../performance/v7/evidence/ZIG-STAGE-13-VERIFIER-INCIDENTS.md) discloses a read-only subagent's brief role confusion and access to the already-public final-manifest fingerprint. No opening, hidden case, final timing, candidate mutation, or verification change occurred; the subagent was stopped and excluded from all final-benchmark work. The **24,576-case** final benchmark remains unopened and **NOT MEASURED**.

## The C engine creates native search iterators directly

The [independent C scanner experiment](../performance/v7/evidence/C-STAGE-20-NATIVE-SCANNER-CMETHOD.md) removes one attribute lookup when creating a match iterator. It directly constructs the same native `search` method, keeping Python's exact method ownership, calling convention, scanner lifetime, and matching behavior. Its [223,198 matching comparisons](../candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-20-native-scanner-cmethod.json.gz), [393 public-object comparisons](../candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-20-NATIVE-SCANNER-CMETHOD.json.gz), [479 tracing and unusual-argument checks](../candidates/evidence/rust-v8-observability-vm-qualified-stage-20-native-scanner-cmethod.json.gz), and [complete 22-stage correctness campaign](../candidates/evidence/rust-v8-vm-stage-20-native-scanner-cmethod-sealed-campaign.json) all pass. The [original from-scratch audit](../candidates/audits/FROM-SCRATCH-AUDIT.json) independently verifies all four implementations and all five loaded native libraries without allowing Python's matching engine or an external regex package.

The [fresh four-way practice run](../performance/v7/evidence/three-qualified-engines-public-practice-v6-summary.json) preserves [all 17,472 observations](../performance/v7/evidence/three-qualified-engines-public-practice-v6-raw.jsonl.gz), all **52,416** correctness checks, and all **407** substantial slowdowns. C measures **1.330×** (range **1.283–1.383×**, **429/624** clearly faster, **47** slowdowns), Rust **1.151×** (range **1.104–1.196×**, **262/624** clearly faster, **125** slowdowns), and Zig **1.015×** (range **0.967–1.062×**, **231/624** clearly faster, **235** slowdowns). The [independent verifier](../performance/v7/evidence/three-qualified-engines-public-practice-v6-integrity.json) rechecks all observations, slowdowns, confidence calculations, candidate proofs, current native libraries, and preserved practice history. These are one-run practice comparisons against Python, not paired comparisons between experiments. They do not establish that the C change caused an improvement or that any engine meets the final target. The **24,576-case** final benchmark remains unopened and **NOT MEASURED**.

The [preserved independence-audit retry](../performance/v7/evidence/C-STAGE-20-INDEPENDENCE-AUDIT-RETRY.md) also records the original unsuccessful parallel malicious-control subprocess and the subsequent passing, unchanged **76-control** audit in isolation. No audit rule, candidate, frozen test, or final result was weakened or concealed.

## A safe Rust common-prefix engine does not prove a speed improvement

The [owned Rust common-prefix experiment](../performance/v7/evidence/RUST-OWNED-MANDATORY-COMMON-PREFIX.md) adds a bounded, independently written analysis of the engine's own parsed expression. Only when every alternative requires the same case-sensitive starting bytes can the ordinary matcher skip an impossible position. The existing Rust-to-Python bridge, C engine, and Zig engine remain unchanged. Its [223,198 matching comparisons](../candidates/evidence/rust-v7-edge-oracle-rust-owned-mandatory-common-prefix.json.gz), [393 public-object comparisons](../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-OWNED-MANDATORY-COMMON-PREFIX.json.gz), [479 tracing and unusual-argument checks](../candidates/evidence/rust-v8-observability-rust-qualified-owned-mandatory-common-prefix.json.gz), and [complete 22-stage correctness campaign](../candidates/evidence/rust-v8-rust-owned-mandatory-common-prefix-sealed-campaign.json) all pass.

The [fresh four-way practice result](../performance/v7/evidence/three-qualified-engines-public-practice-v5-summary.json) retains [all 17,472 observations](../performance/v7/evidence/three-qualified-engines-public-practice-v5-raw.jsonl.gz), all **52,416** correctness checks, and all **407** substantial slowdowns. C measures **1.318×** (range **1.270–1.372×**, **51** slowdowns), Rust **1.143×** (range **1.099–1.189×**, **113** slowdowns), and Zig **1.006×** (range **0.960–1.051×**, **243** slowdowns). The [independent data replay](../performance/v7/evidence/three-qualified-engines-public-practice-v5-integrity.json) checks every loss, all **1,875** confidence intervals, all historical evidence, and the current native libraries. The additional Rust matching complexity has **no demonstrated end-to-end speed advantage** over the separately measured simpler design. No paired cross-run improvement is claimed. The **24,576-case** final benchmark remains unopened and **NOT MEASURED**.

The [complete verification-incident record](../performance/v7/evidence/RUST-OWNED-MANDATORY-COMMON-PREFIX-VERIFIER-INCIDENTS.md) preserves the initial failed synthetic self-test, its exact corrected 119-control rerun, and a quarantined reviewer's overly broad read-only protocol-source search. No secret, hidden case, marker, or final result was accessed; the reviewer was removed and the final benchmark remained sealed.

## Zig removes matching stack probes but does not prove a speed improvement

The [independent Zig stack experiment](../performance/v7/evidence/ZIG-STAGE-12-SPAN-256.md) reduces the owned native matching span buffer from 514 to 256 words. Inspection of the actual native code confirms that compiled matching, scanner matching, and the low-level matcher no longer perform a **4 KB** stack-page probe on entry. The existing checked heap fallback still handles large capture counts. The original [223,198-check matching oracle](../candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-12.json.gz), [deep public-object test](../candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-12.json.gz), [observation and binder checks](../candidates/evidence/rust-v8-observability-zig-qualified-stage-12.json.gz), and unchanged [complete 22-stage campaign](../candidates/evidence/rust-v8-zig-stage-12-sealed-campaign.json) all pass.

The fresh [four-engine run](../performance/v7/evidence/three-qualified-engines-public-practice-v4-summary.json) preserves [all 17,472 observations](../performance/v7/evidence/three-qualified-engines-public-practice-v4-raw.jsonl.gz), **52,416** passing correctness checks, and all **402** substantial slowdowns. C measures **1.319×** (range **1.273–1.373×**, **48** slowdowns), Rust **1.146×** (range **1.100–1.191×**, **112** slowdowns), and Zig **1.001×** (range **0.955–1.046×**, **242** slowdowns). Zig's interval includes Python. The low-level stack improvement is therefore **rejected as proof of an end-to-end speed improvement**; its complete source, correctness results, all slowdowns, and [independent measurement replay](../performance/v7/evidence/three-qualified-engines-public-practice-v4-integrity.json) remain visible. The final **24,576-case** benchmark remains unopened and **NOT MEASURED**.

## A smaller Rust search buffer and a preserved initial audit failure

The [smaller Rust buffer experiment](../performance/v7/evidence/RUST-FINDALL-CAPACITY-16.md) changes one existing native collection limit from 128 to 16. The inspected stack buffer decreases from **9,216** to **1,152** bytes; the engine, capture handling, and result continuation remain independently implemented from scratch. Its first complete correctness campaign failed at an isolated independence audit even though the separate original audit had passed. The [exact failure, unchanged source, sealed diagnostic, unknown cause, and successful retry](../candidates/evidence/RUST-FINDALL-CAPACITY-16-INITIAL-AUDIT-FAILURE.md) are retained. The unchanged [complete 22-stage retry](../candidates/evidence/rust-v8-rust-findall-capacity-16-sealed-campaign.json) genuinely passes all **4,494,555** Unicode comparisons, matching, public-object, replacement, callback, and isolated-safety checks.

A new, separately recorded [four-engine practice run](../performance/v7/evidence/three-qualified-engines-public-practice-v3-summary.json) preserves [all 17,472 observations](../performance/v7/evidence/three-qualified-engines-public-practice-v3-raw.jsonl.gz), **52,416** passing correctness gates, and all **387** substantial slowdowns. C measures **1.325×** (range **1.278–1.379×**, **46** slowdowns), Rust **1.151×** (range **1.106–1.197×**, **109** slowdowns), and Zig **1.011×** (range **0.965–1.057×**, **232** slowdowns). The [independent replay](../performance/v7/evidence/three-qualified-engines-public-practice-v3-integrity.json) checks every observation, all **1,875** confidence intervals, the preserved first failure, both historical runs, all native-library identities, and every loss. The earlier **1.136×** Rust result belongs to a separate run; no cross-run paired confidence interval is claimed. The hidden **24,576-case** final benchmark remains **NOT MEASURED** and unopened.

## A fully checked Rust improvement and a fresh four-engine comparison

The [fused Rust experiment](../performance/v7/evidence/RUST-FUSED-VECTORCALL.md) reduces repeated bookkeeping between Python and the independently written Rust matching engine. Its [223,198 frozen matching comparisons](../candidates/evidence/rust-v7-edge-oracle-rust-fused-vectorcall.json.gz), [393 public-object comparisons](../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-FUSED-VECTORCALL.json.gz), [479 unusual-argument and tracing checks](../candidates/evidence/rust-v8-observability-rust-qualified-fused-vectorcall.json.gz), and [complete 22-stage campaign](../candidates/evidence/rust-v8-rust-fused-vectorcall-sealed-campaign.json) all pass. The unchanged [independence auditor](../candidates/audits/FROM-SCRATCH-AUDIT.json) verifies all four separately written implementations, all five actual native libraries, and all 76 controls against hidden engine delegation and external packages.

One fresh run compares current Python, Rust, C, and Zig on the same 624 public cases. It retains [all 17,472 timing rows](../performance/v7/evidence/three-qualified-engines-public-practice-v2-raw.jsonl.gz), [all 52,416 successful correctness checks and 401 substantial losses](../performance/v7/evidence/three-qualified-engines-public-practice-v2-summary.json), and an [independent replay of all 1,875 confidence intervals](../performance/v7/evidence/three-qualified-engines-public-practice-v2-integrity.json). C measures **1.316×** (range **1.269–1.371×**, **49** substantial slowdowns), Rust **1.136×** (range **1.090–1.183×**, **112** slowdowns), and Zig **1.003×** (range **0.957–1.050×**, **240** slowdowns). The original 1.121× Rust measurement remains a historical result from a separate run; it is not a paired comparison against this experiment. All six current graphs use only the new four-engine run. Native-specific memory and final performance are **NOT MEASURED**; the 24,576 final cases remain unopened.

## The first fair public comparison of all three qualified engines

Only after the larger final test was genuinely sealed, the [original public practice runner](../performance/v7/evidence/THREE-QUALIFIED-ENGINES-PUBLIC-PRACTICE.md) compared standard Python, Rust, C, and Zig together on exactly the same **624** public cases. The single actual run preserves [all **17,472** raw timing rows](../performance/v7/evidence/three-qualified-engines-public-practice-v1-raw.jsonl.gz), [all case summaries and **426** substantial losses](../performance/v7/evidence/three-qualified-engines-public-practice-v1-summary.json), and **52,416** successful before, memory, and after correctness checks.

The independent [public-data verifier](../performance/v7/evidence/three-qualified-engines-public-practice-v1-integrity.json) recalculates all **1,875** per-case and overall confidence intervals from the raw measurements, verifies all five native binaries and the from-scratch audit as they existed for that historical run, and separately passes [**28** corrupted-data controls](../performance/v7/evidence/three-qualified-engines-public-practice-v1-integrity-self-test.json). The generated graphs pass [**33** additional synthetic tampering checks](../performance/v7/evidence/three-qualified-engines-public-practice-v1-chart-self-test.json). Practice-only overall results against Python are C **1.315×** (range **1.269–1.368×**, **49** substantial slowdowns), Rust **1.121×** (range **1.076–1.165×**, **139** slowdowns), and Zig **1.007×** (range **0.960–1.054×**, **238** slowdowns). Zig's range includes **1×**. All timings use one shared process: Python allocation samples are not isolated native memory measurements. No final case is generated, opened, or measured, and no final winner is chosen.

## The expanded final benchmark is genuinely sealed before optimization

After the independently audited Rust, C, and Zig engines each passed all **22** original correctness stages, a [small, from-scratch custodian](../tools/rust_v9_opening_custodian.py) first passed [all **27** synthetic security checks](../performance/v9/evidence/HOLDOUT-CUSTODIAN-SELF-TEST.json). A separate one-time process then created exactly one **32-byte** opening at the frozen owner-only path, synchronized the new file and directory, erased its working buffer, and returned only its public SHA-256 fingerprint. Its [complete public attestation](../performance/v9/evidence/HOLDOUT-CUSTODIAN-ATTESTATION.json) explicitly states that same-user blindness is procedural, not a cryptographic or operating-system security boundary.

The unchanged frozen performance tool generated the exact [prospective 24,576-case manifest](../performance/v9/holdout-manifest.json) from that public fingerprint. Its [first original manifest verification](../performance/v9/evidence/HOLDOUT-PROTOCOL-MANIFEST-VERIFY.json) passes. The stronger [manifest-bound self-test](../performance/v9/evidence/HOLDOUT-PROTOCOL-SELF-TEST.json) passes **75** checks, including **70** poisoned controls, without reading the opening, generating a final case, importing a candidate, or measuring performance. The actual [final no-opening verification](../performance/v9/evidence/HOLDOUT-PROTOCOL-VERIFIED.json) recomputes and validates the exact committed proof. It freezes all **12** operations, **eight** equally weighted workloads, **256** cases per cell, **31** paired rounds, **9,999** bootstrap draws, and the unchanged **1.5×** and **14,746-case** success requirements. All candidate optimization remains paused until this protocol and evidence are committed and pushed. Final performance remains **NOT MEASURED**.

## Zig becomes the third independently qualified engine

The [corrected from-scratch Zig engine](../candidates/evidence/ZIG-STAGE-11-QUALIFIED.md) moves Python recursion protection into its own C bridge and passes checked callbacks directly into its own Zig parser. It retains the required original compiler interface, independently owned parser and bytecode executor, valid deep-pattern handling, and the nonrecursive literal-branch optimization. The original [four-family independence audit](../candidates/audits/FROM-SCRATCH-AUDIT.json) now passes all **76** controls and verifies all **five** actual loaded native libraries. The [preserved diagnosis of the preceding failure](../candidates/audits/FROM-SCRATCH-AUDIT-ZIG-STAGE-10-STATIC-DIAGNOSTIC.json) identifies the two forbidden direct Zig imports; no frozen auditor, allowed dependency, or matching test was weakened.

The genuine [single complete correctness campaign](../candidates/evidence/rust-v8-zig-stage-11-sealed-campaign.json) executes and passes all **22** required stages. Separate original checks confirm [**4,494,555** full-Unicode comparisons](../candidates/evidence/rust-v8-zig-stage-11-unicode-fullplane.json), [**223,198** matching and edge checks](../candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-11.json.gz), [**72,248** extended behavior checks](../candidates/evidence/rust-v8-zig-stage-11-extended-original.json), [**20,480** parser cases](../candidates/evidence/rust-v7-grammar-zig-v8-deep-stage-11.json.gz), [**393** public-object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-11.json.gz), and [**479** unusual-argument and tracing checks](../candidates/evidence/rust-v8-observability-zig-qualified-stage-11.json.gz). The extended report exactly matches the full campaign's original embedded evidence; an additional [lossless diagnostic](../candidates/evidence/rust-v8-zig-stage-11-extended-path-failures.json.gz) separately confirms all **72,248** cases. Both [**8,862**](../candidates/evidence/rust-v8-replacement-zig-stage-11-from-scratch-failures.json.gz) and [**11,266**](../candidates/evidence/rust-v8-replacement-zig-stage-11-from-scratch-deep-failures.json.gz) replacement suites pass. The original [**254-case** safety suite](../candidates/evidence/rust-v8-zig-stage-11-isolated-safety.json) and [**348-case** deep-recursion suite](../candidates/evidence/rust-v8-zig-stage-11-depth-safety.json) have zero failures, crashes, timeouts, or Python-reference disagreements. Rust, Zig, and C are now all **CORRECTNESS-QUALIFIED**. The expanded final benchmark remains sealed and every final speed result remains **NOT MEASURED**.

## Zig fixes all 602 safety checks but fails native-library verification

The then-proposed [independent Zig engine](../candidates/evidence/ZIG-STAGE-10-REJECTED-NATIVE-PROVENANCE.patch) moves large temporary branch buffers out of recursive compiler calls without discarding the fast literal-branch implementation. Its original [254-case isolated safety run](../candidates/evidence/rust-v8-zig-stage-10-isolated-safety.json) passes **254/254** across all **10** categories. Its original [348-case deep-recursion run](../candidates/evidence/rust-v8-zig-stage-10-depth-safety.json) passes **348/348** across all **nine** categories, including both legal patterns that previously caused native crashes. Both runs have **zero** failures, crashes, timeouts, or Python-reference failures.

The unchanged independence auditor passes all **76** self-checks. Its first real run then [fails the Zig verification](../candidates/audits/FROM-SCRATCH-AUDIT-ZIG-STAGE-10-FAILURE.json). All **five** native files pass static inspection, and Rust, C, and the independent Python engine pass, but Zig does not. The original failure output does not identify a loaded path or hash. A later [read-only diagnostic](../candidates/audits/FROM-SCRATCH-AUDIT-ZIG-STAGE-10-STATIC-DIAGNOSTIC.json) establishes the exact cause: two direct Python recursion imports in the Zig source fail the original static-independence rules, so the runtime mapping check is correctly skipped. Because the auditor writes its canonical report only after a passing run, its then-existing passing report verified the previous Zig implementation and could not certify this proposal. The [full rejection report](../candidates/evidence/ZIG-STAGE-10-REJECTED-NATIVE-PROVENANCE.md) preserves the first failure, both safety results, the exact source patch, and all relevant hashes. This proposal was **NOT QUALIFIED**; its complete correctness campaign and final speed were **NOT MEASURED**.

## Zig fixes 22 initial failures but still crashes at legal deep recursion

The [new from-scratch Zig proposal](../candidates/evidence/ZIG-STAGE-09-REJECTED-DYNAMIC-RECURSION.patch) replaces fixed capture and group-name buffers with checked, dynamically sized storage; preserves nested-lookaround capture rollback; fixes escaped Unicode error positions and variable-width possessive repeats; and adds balanced public-API recursion protection without importing `sys`, Python's regex engine, or another candidate. The single original [254-case isolated safety run](../candidates/evidence/rust-v8-zig-stage-09-isolated-safety.json) passes **254/254** with **zero** failures, crashes, timeouts, or Python-reference failures. This eliminates all **22** original Stage-08 safety differences, including its **three** crashes and 1,024-capture-group failure.

The unchanged larger [348-case depth and overflow run](../candidates/evidence/rust-v8-zig-stage-09-depth-safety.json) nevertheless records **two** genuine `SIGSEGV` crashes, both for valid patterns with recursion limit **4,096** and nesting depth **2,040**. Python correctly compiles both patterns. The exact cause is large branch-optimization scratch buffers in every recursive Zig compiler call; rejecting or lowering the recursion limit would be incorrect. The [complete rejection report](../candidates/evidence/ZIG-STAGE-09-REJECTED-DYNAMIC-RECURSION.md) preserves both true crash records, all **348** cases, the successful smaller safety run, and the complete source patch. Zig remains **NOT QUALIFIED**; a fresh independence audit, full campaign, and performance comparison are **NOT MEASURED**.

## C passes the complete 22-stage Python compatibility campaign

The final [from-scratch C implementation](../candidates/evidence/C-STAGE-19-QUALIFIED.md) preserves its independent Python parser, bytecode compiler, native C execution, complete Unicode case components, runtime-aware recursion, bounded repeat compilation, and Python's exact valid and inverted matching-window behavior. Its [single genuine full campaign](../candidates/evidence/rust-v8-vm-stage-19-sealed-campaign.json) executes and passes all **22** frozen correctness stages. The separate [complete Unicode report](../candidates/evidence/rust-v8-vm-stage-19-unicode-fullplane.json) passes **4,494,555/4,494,555**, including all **1,114,112** code points, all **50** special case-fix keys, all **56** links, and every previously failing seeded case. Both [348-case deep safety](../candidates/evidence/rust-v8-vm-stage-19-depth-safety.json) and [254-case isolated safety](../candidates/evidence/rust-v8-vm-stage-19-isolated-safety.json) pass without crashes, timeouts, or oracle failures.

The unchanged frozen standalone checks also pass [**72,248** extended cases](../candidates/evidence/rust-v8-vm-stage-19-extended-path-failures.json.gz), [**223,198** edge cases](../candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-19.json.gz), [**20,480** independent parser cases](../candidates/evidence/rust-v7-grammar-vm-v8-deep-stage-19.json.gz), [all **393** public-object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-19.json.gz), [all **479** observability checks](../candidates/evidence/rust-v8-observability-vm-qualified-stage-19.json.gz), and [both **8,862**](../candidates/evidence/rust-v8-replacement-vm-stage-19.json.gz) and [**11,266**](../candidates/evidence/rust-v8-replacement-vm-deep-stage-19.json.gz) replacement suites. The [refreshed original independence audit](../candidates/audits/FROM-SCRATCH-AUDIT.json) verifies all four genuine engine families, all five actual native libraries, and all **76** anti-delegation controls. The updated headline graph is regenerated from the actual **223,198-case** C evidence without changing another engine's denominator. No performance benchmark or hidden test is opened. C is now **CORRECTNESS-QUALIFIED**, not a measured speed winner.

## C window guard fixes two cases but rejects six real boundary matches

The [next proposed native C change](../candidates/evidence/C-STAGE-18-REJECTED-INVERTED-BOUNDARY.patch) rejects `pos > endpos` in its common matching path. A single original [4,494,555-case full-Unicode run](../candidates/evidence/rust-v8-vm-stage-18-unicode-fullplane.json) confirms that all four **1,114,112-code-point** partitions still match pinned Python's exact hashes, and all **50** case-fix keys, **56** links, **280** extra-case checks, and **1,455** equivalence checks remain correct. Both previous `seeded-332` failures disappear.

The same complete worker reveals **six new real failures**: for three frozen seeded patterns, Python legitimately accepts an empty `\b|\B` or `(\b|\B)` word-boundary match even when `pos > endpos`. The proposed general guard incorrectly returns no match for both `match` and `scanner.match`. The [full rejection report](../candidates/evidence/C-STAGE-18-REJECTED-INVERTED-BOUNDARY.md) retains every original expected and actual result, the exact worker denominator, and the complete source patch. C remains **NOT QUALIFIED**; exact-source standalone safety, a refreshed independence audit, a full campaign, and final performance are **NOT MEASURED**.

## C fixes all Unicode case groups but fails two inverted-window cases

The [next proposed native C implementation](../candidates/evidence/C-STAGE-17-REJECTED-WINDOW.patch) implements every pinned Python Unicode case-equivalence component directly in its own matcher. It retains all **24** extra equivalence groups, all **50** case-fix keys and **56** links, the existing ASCII and locale behavior, and the same character-class logic for real matching and search filters. The original standalone [full-plane correctness worker](../candidates/evidence/rust-v8-vm-stage-17-unicode-fullplane.json) completes the actual **4,494,555** checks in one run. All four **1,114,112-code-point** category and case-insensitive-range partitions match the pinned Python observation hashes exactly; all **280** extra-case controls and **1,455** broader equivalence checks pass.

The same complete frozen worker nevertheless exposes **two** genuine seeded failures. For pattern `(?:\w|\W)*?` with `ASCII | IGNORECASE`, subject `" "`, `pos=1`, and `endpos=0`, C returns an empty match where Python correctly returns no match; both compiled `match` and `scanner.match` are affected. The [full rejection report](../candidates/evidence/C-STAGE-17-REJECTED-WINDOW.md) retains both complete expected and actual observations and the exact lossless source patch. The candidate is **NOT QUALIFIED**. Stage-17 safety, a fresh independence audit, the complete campaign, and final performance are **NOT MEASURED**; no frozen correctness or sealed performance benchmark was changed or opened.

## C fixes recursion but fails the final full-Unicode stage

The [next proposed C implementation](../candidates/evidence/C-STAGE-16-REJECTED-UNICODE.patch) uses its own public-API native recursion guard, accounts for Python's dynamically changing recursion limit and conditional-group depth, and removes unnecessary compiler recursion without changing emitted matching instructions. Its [four-family independence audit](../candidates/audits/FROM-SCRATCH-AUDIT-C-STAGE-16-PASS.json) passes all **76** original controls and verifies all **five** loaded native libraries. The unchanged frozen gates pass [**348/348** deeper safety cases](../candidates/evidence/rust-v8-vm-stage-16-depth-safety.json), [**254/254** crash and input-safety cases](../candidates/evidence/rust-v8-vm-stage-16-isolated-safety.json), [**72,248/72,248** extended cases](../candidates/evidence/rust-v8-vm-stage-16-extended-path-failures.json.gz), [**223,198/223,198** matching cases](../candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-16.json.gz), [**20,480/20,480** independent parser cases](../candidates/evidence/rust-v7-grammar-vm-v8-deep-stage-16.json.gz), [all **393** public-object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-16.json.gz), [all **479** tracing and argument checks](../candidates/evidence/rust-v8-observability-vm-qualified-stage-16.json.gz), and [all **8,862**](../candidates/evidence/rust-v8-replacement-vm-stage-16.json.gz) and [**11,266**](../candidates/evidence/rust-v8-replacement-vm-deep-stage-16.json.gz) replacement checks. The public-object report explicitly retains one permitted private garbage-collection topology difference; it records **zero** public behavior differences.

The genuine [single full 22-stage campaign](../candidates/evidence/rust-v8-vm-stage-16-sealed-campaign-failure.json) passes its first **21** stages, including its own fresh safety and recursion checks, but fails the final full-Unicode comparison. Its original clipped error output preserves **nine** complete case-insensitive Greek character-class differences and one partial record. The frozen Unicode suite requires **4,494,555** cases; because the original worker aborts, the number actually completed and its total mismatch count remain **NOT MEASURED**. The [complete rejection report](../candidates/evidence/C-STAGE-16-REJECTED-UNICODE.md) preserves the exact first run, rejected source, independence audit, and every passing standalone report. C remains **NOT QUALIFIED**; the sealed final performance benchmark was not opened.

## Independent C fix passes ordinary tests but fails deeper recursion safety

The [next exact C implementation](../candidates/evidence/C-STAGE-15-REJECTED-RECURSION.patch) retains its own parser, compiler, and native matching engine. It removes the preceding forbidden `sys` import, computes native integer width through `struct`, and passes the [unchanged four-engine independence audit](../candidates/audits/FROM-SCRATCH-AUDIT-C-STAGE-15-PASS.json). Its frozen tests pass [**254/254** initial safety cases](../candidates/evidence/rust-v8-vm-stage-15-isolated-safety.json), [**72,248/72,248** extended cases](../candidates/evidence/rust-v8-vm-stage-15-extended-path-failures.json.gz), [**223,198/223,198** matching cases](../candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-15.json.gz), [**20,480/20,480** parser cases](../candidates/evidence/rust-v7-grammar-vm-v8-deep-stage-15.json.gz), [all **393** public-object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-15.json.gz), [all **479** tracing and argument checks](../candidates/evidence/rust-v8-observability-vm-qualified-stage-15.json.gz), and [all **8,862**](../candidates/evidence/rust-v8-replacement-vm-stage-15.json.gz) and [**11,266**](../candidates/evidence/rust-v8-replacement-vm-deep-stage-15.json.gz) replacement checks.

The single [complete 22-stage campaign](../candidates/evidence/rust-v8-vm-stage-15-sealed-campaign-failure.json) nevertheless fails the original deeper recursion-safety stage: **50/348** differences, **zero** crashes, **zero** timeouts, and **zero** Python-reference failures. One separate, unchanged 348-case diagnostic preserves [every original failing case and Python's exact answer](../candidates/evidence/rust-v8-vm-stage-15-depth-safety-original-worker-mismatches.json). These comprise **28** changed-recursion-limit differences, **14** deeply nested parser differences, **five** seeded nested-pattern differences, and **three** incorrect malformed-pattern errors. The [complete rejection report](../candidates/evidence/C-STAGE-15-REJECTED-RECURSION.md) records both successful and failing evidence, source hashes, and the exact rejected patch. C remains **NOT QUALIFIED**; the expanded final test and performance remain **NOT MEASURED**.

## C passes every standalone feature but fails the unchanged independence audit

The next [proposed compact-repeat implementation](../candidates/evidence/C-STAGE-14-REJECTED-INDEPENDENCE.patch) corrects all **10** previous Unicode-range and possessive-repeat failures. Its unchanged, frozen gates pass [**254/254** isolated safety cases](../candidates/evidence/rust-v8-vm-stage-14-isolated-safety.json), [**72,248/72,248** extended cases](../candidates/evidence/rust-v8-vm-stage-14-extended-path-failures.json.gz), [**223,198/223,198** matching cases](../candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-14.json.gz), [**20,480/20,480** independent parser cases](../candidates/evidence/rust-v7-grammar-vm-v8-deep-stage-14.json.gz), [all **393** public object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-14.json.gz), [all **479** tracing and scanner checks](../candidates/evidence/rust-v8-observability-vm-qualified-stage-14.json.gz), and [all **8,862**](../candidates/evidence/rust-v8-replacement-vm-stage-14.json.gz) and [**11,266**](../candidates/evidence/rust-v8-replacement-vm-deep-stage-14.json.gz) replacement checks.

The [strict four-family independence audit](../candidates/audits/FROM-SCRATCH-AUDIT-C-STAGE-14-FAILURE.json) nevertheless correctly rejects the proposal: it imported `sys` to obtain the maximum native-sized integer. The original auditor forbids that module because it can reveal interpreter internals and other loaded implementations. The failing check is `forbidden_indirection_import`, and the refused native-runtime check is not misrepresented as a pass. No rule, poison control, or forbidden-module list is weakened. The [rejection report](../candidates/evidence/C-STAGE-14-REJECTED-INDEPENDENCE.md) preserves the exact source patch, all eight real successes, and the complete audit failure. No full campaign or final timing was run.

## C compact repeats pass the extended tests but fail isolated safety

The [second proposed compact C implementation](../candidates/evidence/C-STAGE-13-REJECTED-SAFETY.patch) fixes the first rejected capture regression, compiles enormous multi-character patterns only once, preserves the existing small-repeat path, and resumes lazy matches incrementally. Its [complete 16-pattern bounded test](../candidates/evidence/rust-v8-vm-stage-13-bounded-manual-path-diagnostic.json) passes all **784/784** frozen comparisons. The exact same candidate also passes the entire unchanged [**72,248-case extended Python suite**](../candidates/evidence/rust-v8-vm-stage-13-extended-path-failures.json.gz); both independent Python references agree, and there are no timeout, missing-phase, or answer differences.

A subsequent single [full 254-case isolated safety check](../candidates/evidence/rust-v8-vm-stage-13-isolated-safety.json) exposes **10** remaining differences: **8** inaccurate escaped-surrogate error messages or positions and **2** incorrect possessive-repeat matches. It records **zero** crashes, **zero** timeouts, and **zero** Python-reference failures. The proposed source remains archived as an exact patch rather than being merged into the production C engine. Its [complete rejection report](../candidates/evidence/C-STAGE-13-REJECTED-SAFETY.md) preserves every actual expected and observed result. No final test or performance was accessed.

## Rejected first C compact-repeat implementation

The [first proposed compact C repeat](../candidates/evidence/C-STAGE-12-REJECTED-COMPACT-REPEAT.patch) adds a real native instruction and avoids expanding large multi-character patterns, but its first genuine [bounded frozen verification](../candidates/evidence/rust-v8-vm-stage-12-bounded-manual-path-diagnostic.json) exposes **two** capture differences in **98** checks. For frozen `((a)?)*` with an inverted matching window, standard Python preserves an empty first capture; the proposed C implementation incorrectly returns an unmatched capture in both `match` and `scanner.match`.

The exact failed implementation, native source hashes, complete observed outcomes, original two-reference self-test, and timeout bounds are preserved. Only **2/16** manual patterns were reached, so the remaining cases are **NOT MEASURED**. The candidate is rejected rather than merged into `main`; no complete campaign, performance, or final-test result is claimed. The [rejection report](../candidates/evidence/C-STAGE-12-REJECTED-COMPACT-REPEAT.md) records the exact backtracking and zero-repeat problem.

## Latest C investigation: bounded diagnosis of a large-repeat hang

The preserved C campaign failed its frozen extended Python check, but the original runner discarded the actual failing case. The previous [unbounded diagnostic](../tools/rust_v8_extended_paths_diagnostic_unbounded_v1.py) is archived byte-for-byte. The [updated diagnostic](../tools/rust_v8_extended_paths_diagnostic.py) keeps the exact same frozen Python tests, answers, errors, and compiled-pattern representation while imposing a **three-second isolated case limit**, a **60-second global limit**, flushed progress, and a maximum of **16** original manual patterns.

Its [bounded self-test](../candidates/evidence/rust-v8-extended-path-diagnostic-bounded-self-test.json) executes both independent Python references against all **16** patterns: **784/784** checks for each reference, zero disagreements, and passing timeout, failure-reporting, and answer-preservation controls. The [one genuine C diagnosis](../candidates/evidence/rust-v8-vm-stage-11-bounded-manual-path-diagnostic.json) passes the first **441** checks over **nine** patterns. The tenth frozen pattern, `(?:ab){4294967294}` against `abab`, exceeds its actual **three-second** limit. The report retains the exact worker output and honestly records its match result as **NOT OBSERVED**.

Inspection of the independently owned C front-end shows that single-character huge repeats use a compact instruction, whereas this two-character repeat is incorrectly expanded in Python before the C engine runs. This is a real compatibility and resource-safety failure, not a timing benchmark. C is **NOT QUALIFIED**; the [diagnostic report](../candidates/evidence/C-STAGE-11-BOUNDED-REPEAT-DIAGNOSTIC.md) does not claim that all **72,248** extended cases were tested or that hidden performance was measured.

## Latest Zig improvement: fix Unicode and preserve real safety failures

The preceding independently written Zig engine recorded [308 real differences on the frozen extended Python tests](../candidates/evidence/rust-v8-zig-stage-07-extended-path-failures.json.gz). Its Unicode matcher already compared case-insensitive characters correctly, but both of its start-character filters accidentally skipped high-Unicode literals that can match ordinary bytes. The native Zig compiler now computes both filters using its own existing character-equivalence operation. It calls no other matching engine and does not change Python's frozen tests.

The unchanged extended tests now pass [**72,248/72,248** comparisons](../candidates/evidence/rust-v8-zig-stage-08-extended-path-failures.json.gz); both separately run Python references agree on all cases. The exact source and rebuilt native library also pass [all **39,512** repeat checks](../candidates/evidence/rust-v8-zig-stage-08-repeat-motif-controls.json), [all **223,198** matching checks](../candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-08.json.gz), [all **20,480** parser checks](../candidates/evidence/rust-v7-grammar-zig-v8-deep-stage-08.json.gz), [all **393** object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-08.json.gz), [all **479** tracing checks](../candidates/evidence/rust-v8-observability-zig-qualified-stage-08.json.gz), and the [**8,862-case**](../candidates/evidence/rust-v8-replacement-zig-stage-08-from-scratch-failures.json.gz) and [**11,266-case**](../candidates/evidence/rust-v8-replacement-zig-stage-08-from-scratch-deep-failures.json.gz) replacement suites.

The genuine one-shot [full Zig campaign](../candidates/evidence/rust-v8-zig-stage-08-sealed-campaign-failure.json) nevertheless stops at the **254-case isolated resource-safety check**: **22** differences, **three** native crashes, **zero** timeouts, and **zero** Python-reference failures. The original full-campaign output records category totals but not individual cases. A separately executed [complete frozen safety diagnostic](../candidates/evidence/rust-v8-zig-stage-08-isolated-safety-baseline.json) preserves all **254** cases, all **22** actual failures, exact expected answers, and all **three** real signal-11 crashes without rerunning or modifying the campaign. The actual counts are **8** deeply nested patterns, **8** reversed surrogate ranges, **3** seeded malformed patterns, **2** extreme repeats, and **1** allocation boundary. Full-Unicode results for this Zig campaign remain **NOT MEASURED** because the failure occurred first.

The [refreshed four-engine audit](../candidates/audits/FROM-SCRATCH-AUDIT.json) independently verifies the exact new Zig source, its two native libraries, the current Rust, C, and Python engines, and all **76** anti-delegation checks. The [previous exact audit](../candidates/audits/FROM-SCRATCH-AUDIT-BEFORE-ZIG-STAGE-08.json) and all original Zig failures are preserved. The [full Zig report](../candidates/evidence/ZIG-STAGE-08-UNICODE-SAFETY.md) records what passed, what genuinely failed, and what remains unmeasured. Zig is **NOT QUALIFIED**; final performance and hidden cases are **NOT MEASURED / NOT ACCESSED**.

## Latest Rust improvement: remove an unnecessary pattern allocation

The previous correctly qualified Rust search filter allocated a small character-search table for every eligible compiled pattern. The independently written Rust compiler now stores the one required character directly inside its own compiled pattern and searches with its existing safely bounded native byte scan. The required prefix, character flags, captures, Unicode checks, windows, and full matching engine remain unchanged; the engine does not call Python `re`, another implementation, or an external regular-expression package.

The exact new source and loaded native engine pass the entire [22-stage compatibility campaign](../candidates/evidence/rust-v8-rust-inline-singleton-sealed-campaign.json), including all **4,494,555** Unicode comparisons, all **72,248** extended cases, all [**223,198** matching checks](../candidates/evidence/rust-v7-edge-oracle-rust-mandatory-prefix-inline-singleton.json.gz), all [**393** object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-MANDATORY-PREFIX-INLINE-SINGLETON.json.gz), all [**479** tracing checks](../candidates/evidence/rust-v8-observability-rust-qualified-mandatory-prefix-inline-singleton.json.gz), and both [standard](../candidates/evidence/rust-v8-rust-mandatory-prefix-inline-singleton-replacement-adversarial.json.gz) and [deeper](../candidates/evidence/rust-v8-rust-mandatory-prefix-inline-singleton-replacement-adversarial-deep.json.gz) replacement suites. The complete [30,800-case focused comparison](../candidates/evidence/rust-v8-rust-mandatory-prefix-inline-singleton-focused-controls.json) passes. The [39,000-case direct control](../candidates/evidence/rust-v8-rust-mandatory-prefix-inline-singleton-direct-replacement-controls.json) retains all **504** unrelated prototype differences.

The [complete 624-case practice report](../performance/v7/evidence/RUST-INLINE-SINGLETON.md) measures **1.1209×** Python's speed, with **1.0773–1.1652×** confidence, **265** significantly faster cases, and all **143** slowdowns exceeding **20%**. Compilation measures **2.4222×** and match-object operations **2.2003×**. The previous search-filter design measured **1.1094×** and **142** substantial slowdowns; the additional slowdown is not omitted. Each design is separately paired against Python, not directly paired against the other design.

The [independent 39-control timing audit](../performance/v7/evidence/rust-v7-calibration-inline-singleton-integrity.json) verifies all **8,736** timing records, **26,208** correctness checks, **625** recalculated confidence intervals, and the exact loaded native code. The [current four-family audit](../candidates/audits/FROM-SCRATCH-AUDIT.json) verifies the actual Rust, committed Zig, C, and Python implementations and all **five** loaded native libraries against **76** anti-delegation controls; the [preceding audit](../candidates/audits/FROM-SCRATCH-AUDIT-BEFORE-RUST-INLINE-SINGLETON.json) is archived unchanged. All eight Rust designs and every slowdown remain in the generated graphs. The **24,576-case** final test remains unopened and final performance is **NOT MEASURED**.

## Correctness

- The [original matrix](../oracle/v1/P0.md) freezes 2,048 CPython 3.14.6 cases and 38 obligations. The original fixture SHA-256 is `983885ee6411fd806edf3d72efbcc989f9b9f7775a6d127dc7c865673eeb0fed`.
- The [expanded matrix](../oracle/v2/P0.md) freezes 8,244 cases and 45 obligations, adding bytes-like inputs, standard object behavior, warnings/errors, lookbehind references, and deeper seeded cases. Fixture SHA-256 is `ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2`.
- The [initial expanded check](../oracle/v2/evidence/INITIAL.md) preserves the 42 native/Python and 386 Rust gaps it exposed. The [native](../oracle/v2/evidence/NATIVE-QUALIFIED.md), [Python](../oracle/v2/evidence/AST-QUALIFIED.md), and [Rust](../oracle/v2/evidence/RUST-QUALIFIED.md) qualification reports close every gap. Both native engines pass sanitizer checks; all three pass the no-delegation audit.
- The [official CPython 3.14.6 `re` test gate](../oracle/cpython-3.14.6/README.md) adds 146 public test methods, 403 historical patterns, and 11 upstream benchmark patterns. Stdlib self-check is clean (144 pass, two locale skips). Initial results reveal 46 native, 50 Python, and 50 Rust failures, including two native timeouts and three Rust crashes. This invalidates a general drop-in claim until buffer behavior, Unicode/error edge cases, `Scanner`, overflow safety, and historical regressions are fixed.

## Candidate discovery

The [discovery report](../candidates/evidence/DISCOVERY.md) preserves rejected binding experiments and their raw losses. The three independent families are the [Python backtracker](../candidates/AST.md), [native bytecode/C engine](../candidates/VM.md), and [Rust continuation/FFI engine](../candidates/RUST.md). Their parsers and executors are independent.

The broader [engine and language survey](../candidates/evidence/ENGINE-SURVEY.md) records 32 focused semantic checks and all 403 official historical patterns across PCRE2, Oniguruma, ICU, POSIX through Zig, Go/RE2, Node, and Perl, plus separate checks of the Python `regex` package. Current PCRE2 comes closest on spans/syntax (399/403) but still differs on important Python rules; Zig/POSIX is incompatible (212/403). These are discovery-only probes: the clarified scope requires every production candidate, including Zig, to implement its parser/compiler/executor from scratch.

The separate [from-scratch Zig architecture probe](../candidates/evidence/ZIG-PROBE.md) implements its own parser, character classes, repeats, alternatives, anchors, a tree executor, and an independently compiled/backtracking executor with general one/two-character start filters. Both paths pass **5,856/5,856** seeded span comparisons in optimized and safety-checked builds, and the binary links no regex engine. On six paired tasks the compiled matcher is **2.92×** as fast overall when repeated work crosses Python only once, but only **0.143×** with one FFI call per match; the tree executor is **0.022×**. This isolates boundary cost and rejects the tree design. Zig is not correctness-qualified: captures, full Unicode, lookaround/references, replacements, and the public object/API surface remain deliberately unimplemented.

## Original performance experiments

The [original protocol](../performance/v1/PROTOCOL.md) freezes 16 practice and 16 holdout tasks. Each experiment retains all 1,152 paired rows and every loss.

| Experiment | Result and evidence |
| --- | --- |
| Discovery pilot | [Pilot](../performance/v1/evidence/PILOT.md) exposes repeated Python/native boundary cost; [native-search follow-up](../performance/v1/evidence/PILOT-NATIVE-SEARCH.md) measures moving the search into C. |
| First paired run | [Initial results](../performance/v1/evidence/INITIAL-RESULTS.md): native C is 0.1141× overall on holdout and clearly faster on 1/16; Python and Rust are much slower. |
| Native batching | [Native batch](../performance/v1/evidence/NATIVE-BATCH.md): repeated calls cross into C once; native C improves to 0.3291× and 2/16 clearly faster. |
| Rejected stack state | [Rejected experiment](../performance/v1/evidence/STACK-STATE-REJECTED.md): correctness-clean but slower at 0.2435×; the slower executor is removed and the result is preserved. |
| Native public API | [Native public API](../performance/v1/evidence/NATIVE-PUBLIC.md): result construction and common paths move to C; 1.1178× overall, 8/16 clearly faster, four large slowdowns. |
| Compact native paths | [Compact paths](../performance/v1/evidence/COMPACT-PATH.md): 1.3067× overall, 10/16 clearly faster, no large holdout slowdown. |
| One-pass and structured loop | [One-pass](../performance/v1/evidence/ONE-PASS.md) and [structured-loop](../performance/v1/evidence/ONE-PASS-LOOP.md) preserve two near misses. |
| Final original run | [Final result](../performance/v1/evidence/FINAL-CANDIDATE.md): native C reaches **1.5597×** holdout speed (1.5363–1.5840× measured range), clearly faster on **14/16**, with **zero** large holdout slowdowns. One practice slowdown is Unicode word-boundary scanning. |

## Expanded performance oracle

The [expanded protocol](../performance/v2/PROTOCOL.md) freezes 28 practice and 28 distinct holdout tasks, covering more APIs, inputs, compilation, scanning, empty matches, backreferences, conditionals, and Python/native boundary costs. Its fixture SHA-256 is `ec2f7194e8bfb4f5438a61abc3d893e18e5fcada13d2de583801b7e28e7b8f1a`.

The [initial expanded result](../performance/v2/evidence/INITIAL.md) retains all 2,464 correctness-gated rows and 119 large slowdowns. Native C is **1.1619×** overall on holdout (1.1482–1.1758× measured range), clearly faster on **19/28**, with four holdout slowdowns: empty-position iteration, escaping bytes, scanning, and repeated match-object access/expansion. Practice adds general token/Unicode matching and controlled branches. Python and Rust are clearly faster only on cold compilation and are much slower on matching calls. These measurements motivate profiling the native boundaries and general paths before the next run.

The [broader v3 protocol](../performance/v3/PROTOCOL.md) expands coverage to **72 practice + 72 holdout tasks**, preserving the first 56 records exactly and adding realistic logs/URLs/configuration/text-cleanup/input/API/window cases. It increases paired trials to 13 and bootstrap samples to 5,000. The frozen fixture SHA-256 is `f3ab490e351648118e522035c8624976203c777d9c1a7f7d44ad98233f2056bf`. Its first correctness gate passes 568/576 comparisons and exposes six unsupported windowed-scanner calls plus two native multiline first-line misses; raw failures are preserved. v3 performance is **NOT MEASURED** until those and the official-suite gaps are resolved.

The [window and multiline follow-up](../performance/v3/evidence/WINDOW-QUALIFIED.md) closes all eight new cases and passes **576/576** pre-timing comparisons. It adds documented compiled-pattern keyword/window handling to all engines and corrects an unsafe native multiline shortcut. Full official-suite reruns improve native to 99/144 and Python/Rust to 95/144 runnable methods; remaining failures, crashes, and timeouts are preserved and continue to block timing.

The [public API surface follow-up](../performance/v3/evidence/SURFACE-QUALIFIED.md) fixes canonical flags/representations, unknown-flag preservation, immutable group indexes, weak references, index-like group arguments, exact argument errors, and warning locations. All three engines fix the same 11 official methods with no unrelated changes: native reaches 110/144 and Python/Rust 106/144 runnable methods. Seeded and pre-timing checks remain clean; official safety/semantic gaps still block timing.

The [inline/scoped-flags follow-up](../performance/v3/evidence/FLAGS-QUALIFIED.md) fixes repeated global flags at the true start, verbose spaces/comments and alternatives, scoped mode switching, incompatible combinations, and exact malformed-flag errors. All three independent parsers fix the same six official methods with no unrelated changes: native reaches 116/144 and Python/Rust 112/144 runnable methods. Seeded and pre-timing checks remain clean; official safety/semantic gaps still block timing.

The [Unicode case-equivalence follow-up](../performance/v3/evidence/UNICODE-QUALIFIED.md) fixes case-insensitive literals, sets, and ranges in all three independent executors. It replaces unsafe endpoint folding with input-variant checks and covers CPython's special Unicode closures while preserving ASCII/bytes behavior. The same three official methods now pass in every engine: native reaches 119/144 and Python/Rust 115/144 runnable methods. Seeded and pre-timing checks remain clean; official safety/semantic gaps still block timing.

The [pattern/replacement-escape follow-up](../performance/v3/evidence/ESCAPES-QUALIFIED.md) fixes octal and hexadecimal pattern escapes, invalid class escapes, named Unicode characters, character-range errors, replacement-string escapes, and validation with empty inputs. All three independently implemented parsers now pass the same seven additional official methods: native reaches 126/144 and Python/Rust 122/144 runnable methods. Seeded, sanitizer, no-delegation, and all 576 pre-timing checks remain clean; remaining official gaps still block timing.

The [repeated-pattern syntax follow-up](../performance/v3/evidence/REPEAT-QUALIFIED.md) fixes valid brace quantifiers with no preceding expression and nested quantifier combinations without rejecting ordinary literal braces. All 136 upstream combinations now match CPython's error and position in each independent parser; native reaches 128/144 and Python/Rust 124/144 runnable methods. Seeded, sanitizer, no-delegation, and all 576 pre-timing checks remain clean; remaining official gaps still block timing.

The [groups/lookarounds/references follow-up](../performance/v3/evidence/GROUPS-QUALIFIED.md) fixes group lifetimes, forward conditionals, same-lookbehind references, malformed group/template names and extensions, global-flag repetition, and the full 403-pattern historical corpus in all three independent engines. The same eight official methods now pass everywhere: native reaches 136/144 and Python/Rust 132/144 runnable methods. Seeded, sanitizer, no-delegation, and all 576 pre-timing checks remain clean; remaining official gaps still block timing.

The [public-scanner follow-up](../performance/v3/evidence/SCANNER-QUALIFIED.md) adds the missing `Scanner` tokenizer independently to every engine and verifies token order, callbacks/captures, constants/skips, bytes, flags, remainder, anchors/lookahead, and zero-length stopping against CPython. The official scanner method now passes everywhere: native reaches 137/144 and Python/Rust 133/144 runnable methods. Seeded, sanitizer, no-delegation, and all 576 pre-timing checks remain clean; remaining official gaps still block timing.

The [buffer/input-safety follow-up](../performance/v3/evidence/BUFFERS-QUALIFIED.md) adds arbitrary contiguous buffers, byte-length semantics, iterator-held buffer locks, safe shrink-after-match slicing, and exact invalid-input errors. It passes 120 differential public-API checks plus all targeted upstream methods and sanitizers: native reaches 141/144 and Python/Rust 136/144 runnable methods. Seeded, no-delegation, and all 576 pre-timing checks remain clean; remaining official gaps still block timing.

The [result-types/representations follow-up](../performance/v3/evidence/RESULTS-QUALIFIED.md) aligns the public match type and representation with CPython and normalizes results from custom string/bytes subclasses with overridden slicing. The remaining result-surface methods now pass everywhere: native reaches 142/144 and Python/Rust 139/144 runnable methods. Seeded, sanitizer, no-delegation, and all 576 pre-timing checks remain clean; the remaining long-input gaps still block timing.

The [long-repeat, lookbehind, and overflow follow-up](../performance/v3/evidence/LONG-REPEAT-QUALIFIED.md) removes every remaining failure, timeout, and Rust crash. Compact/iterative matching now handles long repeated groups and deep fixed-width lookbehind without recursion or unrolling, oversized counts fail safely, and Rust accepts valid surrogate character-set members. All three independent engines pass **144/144** runnable official methods, all **3,060** seeded differential controls, both correctness matrices, sanitizers, delegation audits, and all **576/576** pre-timing checks. The broader holdout remains **NOT MEASURED**, and is now correctness-qualified for timing.

The [initial broader performance result](../performance/v3/evidence/INITIAL.md) retains all **7,488** correctness-gated timing rows and all **329** large slowdowns. Native C is **0.8997×** overall on the 72-task holdout (0.8927–0.9068× measured range), clearly faster on **30/72**, with **25** holdout slowdowns. The new everyday/branch/lookaround/scanner tasks expose general-backtracking and boundary costs that the smaller holdouts missed; the worst native loss is searching many absent alternatives (0.074×). Python and Rust are clearly faster only on cold compilation and remain dominated by Python execution or conversion/FFI overhead (2/72 faster, 70 slowdowns each). All cases, confidence ranges, memory, explanations, and generated plain-language graphs are preserved.

The [API-boundary follow-up](../performance/v3/evidence/BOUNDARY-QUALIFIED.md) profiles and removes three measured costs: per-character Python escaping, reparsing every match-expansion template, and the Python scanner wrapper. It also fixes previously uncovered mixed scanner `search`/`match` sequences and empty matches in all three engines. The [full paired result](../performance/v3/evidence/BOUNDARY.md) improves native C to **0.9735×** holdout speed (0.9676–0.9795×), **37/72** clearly faster and **19** large slowdowns. On holdout, native escaping improves 0.184→0.966× and 24.36→0.68× memory; expansion 0.267→1.090×; scanners 0.509–0.541→1.062–1.257×. All 7,488 rows, losses, sanitizers, upstream checks, and 2,223 new seeded controls are preserved.

The [native start/class-filter follow-up](../performance/v3/evidence/START-FILTER-QUALIFIED.md) adds general one/two-character start filters for alternatives, lazy ASCII character-class tables, and precomputed safe greedy-repeat choices. The [full paired result](../performance/v3/evidence/START-FILTER.md) raises native holdout speed to **1.0967×** (1.0897–1.1037×), with **37/72** clearly faster and **12** large slowdowns. Searching absent alternatives improves **0.074→0.748×**, request-log matching **0.271→0.833×**, repeated paths **0.760→1.058×**, and negative-lookbehind tags **0.613→1.067×**. Compile memory rises on two cold tasks; all memory/regressions, 7,488 rows, sanitizer/upstream results, and 1,800 new seeded controls are preserved.

The [literal-prefix experiment](../performance/v3/evidence/LITERAL-PREFIX-REJECTED.md) tries skipping directly to a fixed starting word before entering the native matcher. It passes every correctness gate and helps line-comment and simple-word searches, but its full paired result lowers overall holdout speed from **1.0967× to 1.0908×** (1.0837–1.0977×), while leaving **12** large slowdowns. The optimization is removed; every timing row, chart, and loss is retained so the rejection is reproducible.

The [replacement-behavior follow-up](../oracle/v2/evidence/REPLACEMENT-QUALIFIED.md) adds **39,000** differential checks across `sub`, `subn`, `Match.expand`, text/bytes/buffers, callbacks, no-match/empty inputs, valid/invalid templates, and exact errors. It exposes **19,088** initial gaps, then fixes template-type selection, delayed mismatch errors, buffer callbacks, validation order, and join behavior independently in all three engines. Every new check, frozen suite, sanitizer, upstream method, and pre-timing comparison passes. The [full paired result](../performance/v3/evidence/REPLACEMENT.md) keeps all 7,488 rows and raises native holdout speed to **1.1132×** (1.1054–1.1206×), **46/72** clearly faster, with **11** large slowdowns.

The [native structured-path follow-up](../performance/v3/evidence/STRUCTURED-QUALIFIED.md) profiles the remaining slow tasks, then removes heap-backed lookaround states, repeated suffix scans, redundant collection calls, and repeated Unicode-layout checks. General paths now handle zero-width alternatives, balanced delimiters, excluded word prefixes, quoted/multi-line blocks, comments, fields, and tags. The [full paired result](../performance/v3/evidence/STRUCTURED.md) raises native holdout speed to **1.2918×** (1.2833–1.2999×), clearly faster on **50/72**, with **zero** large holdout slowdowns. CSV improves **0.356→2.387×**, empty/zero matches **0.557–0.656→2.218–2.235×**, multi-line blocks **0.657→1.498×**, quotes **0.681→1.511×**, and formatted fields **0.670→2.386×**. All rows, profiles, losses, sanitizers, upstream checks, and **13,230** new seeded controls are preserved. A full-literal alternative filter is measured and rejected as slower.

The [final native execution/collection follow-up](../performance/v3/evidence/FINAL-QUALIFIED.md) removes repeated boundary and character work broadly: class tables initialize only the required mode, direct run loops handle repeated classes/dots/literals, iterator subjects are cached, direct/triple start filters avoid impossible searches, and general line/path/separator/literal/escape paths batch work safely. The **6,720-case** collection control catches and fixes trailing-newline and windowed-backtracking gaps. The [final full paired result](../performance/v3/evidence/FINAL.md) reaches **1.5572×** holdout speed (1.5475–1.5670×), is clearly faster on **70/72**, and has **zero** large holdout slowdowns. All 7,488 rows, pilots, losses, sanitizers, upstream tests, and **66,033** total focused checks are preserved. Native C is selected as the simplest fully compatible winner and is exposed through `import rebar as re`.

## Python, Rust, and Zig follow-up

The [initial engine pilot](../performance/v3/evidence/engine-pilot-before.json) rechecks all **72** broader holdout tasks with five paired trials and up to eight operations per timing. All **1,296** pre/post-timing comparisons pass. Python reaches **0.0135×** of stdlib overall (3/72 faster, 69 large slowdowns); Rust reaches **0.0157×** (3/72 faster, 68 large slowdowns). Profiling identifies the main costs before optimization: Python recreates and validates its executor at every possible starting position, while Rust repeatedly builds three per-character Python arrays before each FFI call. The reproducible pilot is [tools/engine_pilot.py](../tools/engine_pilot.py); it is for iteration and does not replace the frozen full protocol.

The [Python engine follow-up](../performance/v3/evidence/PYTHON-ENGINE.md) adds general literal/class/alternative start skipping, reusable immutable-input executors, cached repeat tables, direct literal runs, and cheaper collection paths. The 72-task pilot improves Python **2.37× overall** to **0.0303×** of stdlib: long final-marker search improves **1,335×**, request logs **8.24×**, absent alternatives **5.92×**, whitespace cleanup **4.82×**, and email-like matching **2.66×**. All raw rows and the readable before/after chart are retained. Both frozen suites, all **66,033** focused checks, the 144 runnable upstream methods, and delegation audit remain clean.

The [Rust engine follow-up](../performance/v3/evidence/RUST-ENGINE.md) replaces repeated Python/`ctypes` character conversion with a dependency-free CPython bridge, direct borrowed byte views, batched collection, safe start/class filters, in-place sequence atoms, cheaper repeats, and reusable replacement templates. Rust improves **12.90× overall** to **0.1845×** of stdlib in the 72-task pilot: long byte-buffer collection improves **551×**, long final-marker search **298×**, literal replacement **45×**, request logs **31×**, and token collection **28×**. An inline-capture-state experiment is correctness-clean but mixed/slower and is rejected with control/raw rows retained. Both frozen suites, all **66,033** focused checks, 144 runnable upstream methods, delegation audits, and instrumented overflow/address/undefined-behavior checks remain clean.

The [Zig native-boundary follow-up](../candidates/evidence/ZIG-NATIVE-BRIDGE.md) replaces its per-call `ctypes` boundary with a dependency-free CPython bridge while keeping the independent bytecode matcher. On six paired tasks, individual Zig calls improve **8.35× overall** from **0.143×** to **1.190×** of stdlib and are clearly faster on **5/6**; the sole loss is absent-literal search at **0.899×**. All **8,784** differential span checks pass in optimized and safety-checked builds, linkage and delegation checks are clean, and all rows/charts are preserved. Zig remains an architecture probe until captures, Unicode, advanced syntax, and the full public surface are implemented.

The [Zig captures/boundaries follow-up](../candidates/evidence/ZIG-CAPTURES.md) adds numbered, nested, repeated, and optional captures with correct backtracking restoration/`lastindex`, plus ASCII word boundaries, to the independently written bytecode engine and native bridge. It passes **3,660/3,660** new capture comparisons and **8,820/8,820** expanded span checks in optimized and safety-checked builds. On six paired tasks that return every capture span, Zig reaches **3.008×** of stdlib overall and is clearly faster on **6/6**. All rows/charts and remaining compatibility gaps are explicit; Zig is still not a complete replacement.

The [Zig references/public-API follow-up](../candidates/evidence/ZIG-REFERENCES.md) adds named/numbered references, conditionals, atomic/possessive control, lookaround, escapes, and batched `findall`/`split`/replacement/iterator paths. The frozen compatibility result improves from **1,058** to **2,651/8,244** and the broader fixture from **118** to **134/144**; all failures and ten unsupported Unicode tasks remain explicit. A full **13-trial**, **3,484-row**, correctness-gated holdout reaches **0.460×** of stdlib (0.459–0.462×), while the capture-returning core reaches **2.631×** on eight tasks. The official suite catches and helps remove a recursive-prefix stack crash; the final run passes **85/144** methods with **zero** crashes/timeouts, and Debug plus address/undefined-behavior and delegation checks are clean. Zig remains incomplete and is not ranked with the three correctness-qualified engines.

The [refreshed full performance run](../performance/v3/evidence/ENGINES-FINAL-NOTES.md) measures all three correctness-qualified engines after the Python/Rust optimizations using the unchanged **144-task**, **13-trial**, **7,488-row** protocol. Native C reaches **1.568×** holdout speed (1.560–1.576×), is clearly faster on **68/72**, and has **zero** large slowdowns. Rust improves **13.03×** over its earlier full result to **0.178×** of stdlib; Python improves **2.38×** to **0.027×**. The complete report/charts retain all **274** remaining Python/Rust slowdowns and group their causes by single-call setup, multi-result construction, and cold compilation. All frozen, upstream, focused, and delegation gates remain clean.

## Larger correctness and performance holdouts

The [large correctness holdout v3](../oracle/v3/P0.md) preserves all **8,244** earlier cases byte-for-byte and freezes **35,840** previously unused cases: **16,384** deep text, **8,192** deep bytes/buffers, **6,144** everyday patterns, **1,024** scanner/mutation sequences, **2,048** cross-API properties, and **2,048** invalid-input cases. Public APIs and module/compiled surfaces are balanced, stable seeds/IDs and a one-second case guard are recorded, and the generator removes one experimentally observed ambiguous nested-repeat shape that could hang stdlib. Two CPython passes agree exactly; the self-check is **44,084/44,084**, **51/51** obligations mapped, zero failures. Fixture SHA-256 is `782c41ff0b1239eeb0bb5312b4a893b41d7882c7fdcf64b29587518839e51669`.

The [large-holdout qualification](../oracle/v3/evidence/QUALIFIED.md) exposes **12** initial native gaps and **one** shared Python/Rust gap, then fixes three general behaviors: choosing the valid suffix before a bounded separator, multiline/final-newline configuration matching, and CPython's locale-aware case handling for negated byte sets. All three independent engines now pass **44,084/44,084** frozen cases and **89,280/89,280** new deterministic regression controls, bringing the focused total to **155,313**. Initial and final results, seeds, safety/upstream/delegation gates, and the readable coverage chart are retained. The expanded performance holdout remains **NOT MEASURED** until its freeze and correctness gate.

The [large performance holdout v4](../performance/v4/PROTOCOL.md) expands coverage to **1,224 practice + 1,224 distinct holdout tasks**, preserving the earlier 144 records exactly and adding **2,304** deterministic cases across **36** balanced families. It exercises every common API, text/bytes/buffers, compilation and caching, Unicode, captures/replacements, scanners/windows, realistic data, hits/misses, and short/long inputs. Its frozen fixture SHA-256 is `cccb7372b724975bea2de63edfbcd559522384d2d1ea57b8d2a07a32cd36f906`, pinned to the 44,084-case correctness oracle. All **9,792/9,792** pre-timing comparisons pass. Each full run retains **127,296** correctness-gated paired rows; performance was **NOT MEASURED** in the freeze chunk.

The [initial large performance result](../performance/v4/evidence/INITIAL-NOTES.md) retains all **127,296** paired rows and **7,344** candidate/task results. Native C reaches **1.5613×** on the **1,224-task** holdout (1.5589–1.5638× measured range), is clearly faster on **1,130/1,224 (92%)**, and has **11** large holdout slowdowns. All 11 are email-like `findall` calls. The correctness-checked native profile records **26–230** character-class checks, **60–518** repeated-character checks, and **20–160** steps per call with **zero** general states/clones, explaining the collection loss. Practice is consistent at **1.5267×**, 1,133 clearly faster, with 43 losses (the same email cases plus 32 short window searches). Rust reaches **0.1814×** holdout speed (72 clearly faster, 1,124 losses), and Python reaches **0.0329×** (36 clearly faster, 1,157 losses). The full report, readable family/all-case charts, memory, every interval, every one of the **4,616** slowdowns, and their causes are preserved. Native C remains the simplest fully compatible winner exposed through `import rebar as re`.

The [Zig allocation follow-up](../candidates/evidence/ZIG-ALLOCATION.md) studies allocation patterns in Zig's bundled TRE sources, then replaces worst-case capture/result allocation with a small stack-backed buffer that grows only when full and resumes matching without rescanning. Long misses and sparse calls fall from roughly **1.5–2.8 MB** to **8 B–66 KB** while dense-result memory also falls; speed is broadly unchanged. The full **13-trial**, **3,484-row** Zig pilot reaches **0.468×** on its 67 qualified holdout tasks, with every correctness comparison passing and every loss retained. Frozen failure IDs, the 202 unsupported large-performance tasks, all 59 official failures, safety checks, and the zero-delegation audit remain unchanged. Zig is still incomplete and unranked.

The [Zig Unicode/large-holdout follow-up](../candidates/evidence/ZIG-UNICODE.md) adds a zero-copy one/two/four-byte text path, wide literals/ranges, Unicode categories/boundaries/case handling, and named characters to the independent parser/executor. It fixes **4,232** expanded-matrix and **17,378** large-holdout cases with zero new failures, qualifies **all 2,448** performance tasks, and improves official coverage **85→102/144** with zero crashes/timeouts. A full-plane/seeded/case-equivalence control passes **12,877/12,877** checks; span/capture and instrumented safety/delegation checks remain clean. The full **13-trial**, **63,648-row** paired result reaches **0.463×** on **1,224** unseen tasks (103 clearly faster, 963 large slowdowns); cold compilation and some cleanup/splitting paths win, while scanners and short searches remain costly. Readable correctness, overall/family speed, memory, and win/loss graphs plus every raw row/failure are retained. The fixed compiled-program allocation rises **283,544→415,000 B**, recorded as the next allocation target; exact errors, large repeats, and deeper behavior still block qualification.

The [Zig scoped-flags follow-up](../candidates/evidence/ZIG-FLAGS.md) adds nested local add/remove modes for case, dot, line, verbose, ASCII/Unicode/locale behavior to its independent parser/compiler/executor. It fixes another **978** expanded and **4,088** large-holdout cases with zero new failures, reaching **7,861/8,244** and **34,378/35,840**; official coverage rises **102→106/144** with zero crashes/timeouts. A **16,552-case** differential control catches and reproduces CPython's surprising scoped-category search-prefix behavior; focused, full-plane, instrumented, and delegation checks pass. The full **13-trial**, **63,648-row** rerun remains **0.463×** on **1,224** unseen tasks (94 clearly faster, 973 large slowdowns), with memory unchanged and all family movement/losses retained. Remaining gaps are exact invalid-pattern errors, fixed-width lookbehind references, and bounded nested-repeat execution.

The [Zig pattern-error follow-up](../candidates/evidence/ZIG-ERRORS.md) adds an independent syntax validator with exact error type, message, pattern, position, line, column, and multi-line display, and makes the Zig parser reject malformed escapes, repeats/assertions, and references directly. It fixes **256** expanded and all **1,024** invalid-pattern holdout cases with zero new failures, reaching **8,117/8,244**, **35,402/35,840**, and **124/144** official methods with zero crashes/timeouts. A new **34,682-case** text/bytes/frozen/official/historical/seeded differential control, full-plane/focused checks, instrumented safety, and delegation gates pass. Eager validation is measured and rejected after slowing the compilation family **1.792→1.367×**; a small allocation-light screen plus native rejection restores it to **1.755×**. The final **13-trial**, **63,648-row** rerun is **0.467×** overall on **1,224** unseen tasks (108 clearly faster, 971 large slowdowns); all five pilots, three full runs, every loss, and readable graphs are preserved. Remaining gaps are fixed-width lookbehind references and bounded nested-repeat execution.

The [Zig fixed-width lookbehind/reference follow-up](../candidates/evidence/ZIG-LOOKBEHIND.md) infers earlier capture widths from the independent syntax tree and enforces the same-lookbehind reference rule, including exact variable-width/error positions. It fixes the final **4** expanded cases in this category with zero new failures, reaching **8,121/8,244**, **35,402/35,840**, and **125/144** official methods with zero crashes/timeouts. A new **32,912-case** text/bytes/Unicode/API/seeded differential control improves from **4,230** initial failures to zero; all existing focused, instrumented, and delegation gates pass. The full **13-trial**, **63,648-row** rerun is **0.459×** overall on **1,224** unseen tasks (91 clearly faster, 979 large slowdowns); cold compilation/references remain stable, every loss and readable graph is preserved. Remaining gaps are bounded nested-repeat execution and larger patterns/classes.

The [Zig nullable/long-repeat follow-up](../candidates/evidence/ZIG-NULLABLE.md) adds guarded empty-loop progress with correct backtracking restoration, stack-backed growing executor storage, and CPython-compatible locale-aware negated byte sets. It fixes all **123** expanded and **438** large-holdout failures, reaching **44,084/44,084** frozen cases, **2,448/2,448** performance tasks, and **129/144** official methods with zero crashes/timeouts. A new **16,589-case** differential/50,000-character control, all focused and instrumented checks, and the delegation audit pass. The full **13-trial**, **63,648-row** rerun is **0.443×** on **1,224** unseen tasks (73 clearly faster, 1,005 large slowdowns). Three full layouts and three shorter pilots, every loss, and readable graphs are preserved; specialization adds complexity without improving speed and is rejected. The remaining 15 official gaps are valid patterns limited by the parser/compiler or still-unsupported syntax.

The [Zig common-syntax follow-up](../candidates/evidence/ZIG-SYNTAX.md) implements inline comments, literal braces, octal/backreference disambiguation, and numeric forward conditionals directly in the from-scratch parser. A new **18,168-case** differential control improves from **11,916** initial failures to zero; all frozen, focused, safety, and delegation gates pass. Official coverage rises **129→135/144** with zero crashes/timeouts. The full **13-trial**, **63,648-row** correctness-gated run is **0.447×** on **1,224** unseen tasks (78 clearly faster, 992 large slowdowns), and every loss and readable graph is preserved. The remaining nine official gaps are large patterns/classes/repeats or more than 128 groups.

The [expanded performance holdout v5](../performance/v5/PROTOCOL.md) preserves all **2,448** earlier records byte-for-byte and adds **3,840** deterministic cases across **40** balanced everyday families, bringing the unseen set to **3,144** tasks with **3,144** matching practice tasks. New coverage includes logs, JSON/markup/Markdown/source/config, URLs/email/IP/versions/dates/phones/paths, CSV/quotes, cleanup/redaction/replacement, multilingual/emoji/bytes/buffers, lookaround/references/conditionals/controlled and empty matches, alternatives/classes/windows/scanners, cold calls, and match details. Stable seeds, equal weights, a readable coverage graph, and the full protocol are frozen; two CPython passes agree exactly and all **31,440/31,440** pre-timing comparisons across stdlib, native C, Python, Rust, and Zig pass. Fixture SHA-256 is `67a4d07ee260bc58456290d76e040b78ba769d1b63cd3b21f0879daa063c2f92`. Performance is **NOT MEASURED**.

The [initial expanded performance result](../performance/v5/evidence/INITIAL-NOTES.md) retains all **408,720** correctness-gated paired rows, **25,152** candidate/task results, memory, intervals, and **17,416** large slowdowns. On **3,144** unseen tasks, native C is **1.3507×** (1.3494–1.3520×), clearly faster on **2,482/3,144 (79%)**, with **226** large losses; the larger holdout falsifies the earlier **1.5×** success claim. Correctness-checked native counters explain every loss family: empty/nullable matches (**48**, 1,178 state copies and 5,829 steps/call), quoted escapes (**48**, 342 copies), many alternatives (**42**, 304 direct steps), CSV (**36**, 377 copies), long literal scans (**17**, direct-path overhead), paths (**16**), controlled repeats (**9**), and earlier email collection (**10**). Zig reaches **0.4807×** (370 clearly faster, 2,486 losses), Rust **0.1492×** (167, 2,948), and Python **0.0241×** (86, 3,021). The preserved portion reproduces the earlier ranking; new tasks expose the difference. Readable overall/family/all-case/memory/regression/ranking graphs, eight profiles, every loss, and the independent **31,440/31,440** post-run gate are preserved.

The [Zig large-set/group follow-up](../candidates/evidence/ZIG-GROUPS.md) packs wide character ranges into a shared program arena, supports UTF-8 group names and 256 captures, fixes backreference search filtering, and widens the dependency-free native bridge. The new **8,953-case** differential control improves from **6,164** initial failures to zero; all **44,084** frozen, **6,288** performance, **101,573** focused, **53,269** instrumented safety, and delegation checks pass. Official coverage rises **135→139/144** with zero crashes/timeouts. The full **13-trial**, **163,488-row** expanded paired rerun reaches **0.443×** on **3,144** unseen tasks (263 clearly faster, 2,644 large slowdowns); compilation/cleanup/splitting win, while empty matching, scanners, short searches, references, and collection remain costly. The readable family, memory, and win/loss graphs plus every row/failure are preserved. Five valid large-pattern/repeat compiler limits remain.

The [Zig large-program/repeat follow-up](../candidates/evidence/ZIG-LARGE-PATTERNS.md) replaces fixed program arrays and repeat unrolling with one growable Zig arena, balanced syntax trees, wide indexes/lookbehind, compact single-character/fixed-layout runs, and exact overflow errors. The new **8,275-case** differential control improves from **4,559** initial failures to zero; all **44,084** frozen, **6,288** performance, **109,848** focused, **54,376** instrumented safety, and delegation checks pass. Official coverage reaches **144/144** with zero failures/crashes/timeouts. Real compiled memory falls **423,960 B fixed → 26,688–55,740 B**, median **30,966 B** across all tasks. The full **13-trial**, **163,488-row** rerun improves Zig **0.443→0.462×** on **3,144** unseen tasks (262 clearly faster, 2,654 large slowdowns); nullable work improves **15×**, and cold compilation reaches **1.90–2.57×**. The sanitizer's initial recursive-stack finding, its balanced-tree fix, every loss, and readable memory/speed/win-loss graphs are preserved.

The [Zig allocation/execution/boundary follow-up](../candidates/evidence/ZIG-OPTIMIZED.md) studies Zig's bundled TRE allocation patterns, then independently adds compact safe runs, exact ASCII caches, direct scans, packed/right-sized state, a small prefix filter, native match/results/iterators/replacements/callbacks, exact-size byte output, warm-cache paths, and a fast literal search boundary. Matching frames fall about **2.1 MB→20 KB** and compiled memory **30,966→23,308 B** median. The frozen **44,084**, **6,288** performance, **144/144** official, **109,848** focused, **21,457** sanitizer, invalid-input, and delegation gates pass. The larger gates catch and close 21 assertion-repeat, two writable-buffer scanner, and four resize/type/verbose regressions; findings are preserved. The full **13-trial**, **163,488-row** rerun improves Zig **0.462→1.381×** on **3,144** unseen tasks (95% range **1.358–1.403×**), clearly faster on **2,290/3,144 (73%)**, with **259** large slowdowns. All 29 pilot architectures, rejected branch/lazy/literal-choice paths, executor counters, memory, readable graphs, and [every large slowdown](../candidates/evidence/zig-opt-regressions.md) are preserved.

The [Zig public-boundary and allocation follow-up](../candidates/evidence/ZIG-BOUNDARY.md) binds common pattern calls directly to native paths, lazily caches methods/templates, safely batches a compact iterator, uses growable **32/64/32** matcher state, initializes read-only patterns natively, and speeds native match methods/`regs` while restoring exact signatures and direct class calls. A new **190-case** text/bytes public-surface differential passes with a clean stdlib self-check; the initial 561 large-group iterator failures and their fix are preserved. All **44,084** frozen, **6,288** performance, **144/144** official, **109,848** focused, **23,396** instrumented safety, and delegation checks pass. The confirmed **13-trial**, **163,488-row** expanded rerun reaches **1.539×** on **3,144** unseen tasks (95% range **1.517–1.561×**), clearly faster on **2,635/3,144 (83.8%)**, with **93** explained large slowdowns, meeting the goal. The report preserves 25 pilots, repeated and slower full runs, every loss, the separate 96-case actual-hit control, memory, and readable graphs. `import rebar as re` now selects this independent Zig winner.

The [Zig alternative/delimiter follow-up](../candidates/evidence/ZIG-DISPATCH.md) adds conservative two-sided start masks for alternatives and positive sets/ranges (including Python's special Unicode folds), capture-safe leading-run skipping, and a narrow DOTALL lazy-delimiter jump. Wider masks, all-run skipping, backreference jumps, and full-delimiter scans are measured and rejected. The frozen **44,084**, **6,288** performance, **144/144** official, **109,848** focused, **190** public-surface, **163,960** new dispatch, and **105,472** debug/sanitizer checks pass; self-oracle and delegation checks are clean, and the initial 82-case literal-field finding and its fix are preserved. The final **13-trial**, **163,488-row** rerun improves the same **3,144-task** holdout **1.539→1.681×** (95% range **1.657–1.705×**), clearly faster on **2,813/3,144 (89.5%)**, with only **4** explained large slowdowns. Alternatives, match-detail misses, multi-line blocks, and verbose/multi-line tasks improve **0.473–0.860×→1.457–2.542×**; the separate successful-match control reaches **1.063×** and the capture core **3.645×**. All 12 pilots, raw rows, memory, readable current graphs, and every loss are preserved; the README now shows only the current state.

The [Zig direct-scanning follow-up](../candidates/evidence/ZIG-EXECUTOR.md) compacts safe lazy-empty repeats and lookarounds, removes unnecessary capture execution, and adds from-scratch linear scans for balanced quoted fields, zero-width choices, excluded words, quoted captures, and common two/three-part fields. The frozen **44,084**, **6,288** performance, **144/144** official, **109,848** focused, **190** public-surface, **163,960** dispatch, **156,484** new executor, and **142,982** debug/sanitizer checks pass; stdlib self-checks and delegation audits are clean. The final **13-trial**, **163,488-row** rerun is **1.683×** on the same **3,144-task** holdout (95% range **1.660–1.705×**), clearly faster on **2,931/3,144 (93.2%)**, with **zero** large slowdowns. Quoted fields, lazy-empty and empty-position work, readable fields, structured text, scanners, and windowed fields improve **0.736–1.934×→1.186–3.316×**; counters confirm repeated executor calls are removed. All 18 pilots, raw rows, memory, readable current graphs, and rejected boundary/build experiments are preserved; the README shows only the current state.

The [broader performance holdout v6](../performance/v6/PROTOCOL.md) preserves all **6,288** earlier records byte-for-byte and adds **6,144** deterministic cases across **48** balanced families, bringing the unseen set to **6,216** tasks with **6,216** matching practice tasks. New coverage includes requests/errors/headers/markup/source/config, IDs/dates/paths/quoted data, multilingual/wide/non-ASCII buffers, dense and empty results, chained assertions/references/conditionals/controlled repeats, long hits/misses, module/cold calls, windows/scanners, and match details. Stable seeds, equal weights, a readable coverage graph, and the full protocol are frozen; two CPython passes agree exactly and all **62,160/62,160** pre-timing comparisons across stdlib, Python, native C, Rust, and Zig pass. Fixture SHA-256 is `c8e32e879cc7a134748f8f3f29fed49678895745fdecebe63ceec46b6a3b5335`. Performance is **NOT MEASURED**.

The first v6 timing attempt stops before writing any row because the new runner omitted its post-batch memory read. The measurement-only error is fixed, the runner hash is refreshed, and the unchanged fixture prefix/hash plus all pre-timing checks are revalidated before retrying; no partial timing is retained or summarized.

The [initial broader performance result](../performance/v6/evidence/INITIAL.md) retains all **808,080** paired rows and **49,728** engine/task results. On **6,216** unseen tasks, Zig / `rebar` reaches **1.5825×** (1.5812–1.5837× measured range), is clearly faster on **5,333/6,216 (85.8%)**, and has **243** large slowdowns; the larger holdout falsifies the earlier zero-loss result. All are exposed and explained: filenames (**64**), dense literal collection (**63**), shared-prefix alternatives (**56**), Unicode word lines (**32**), case-insensitive money/units (**22**), backreferences (**5**), and branch alternatives (**1**). Native C reaches **1.2830×** (4,577 clearly faster, 653 losses), Rust **0.1344×** (229, 5,892), and Python **0.0207×** (195, 5,918). Zig uses at most the baseline's traced Python memory on **5,714/6,216** tasks (0.54× median ratio). A dependency-free streaming analyzer validates every raw row and reproduces the frozen Python bootstrap draws/ranges exactly; its self-test passes. Clear overall, workload, memory, win/loss, and ranking graphs, every individual result, and compressed raw data are preserved. README now leads with the broader headline and keeps experiment notes here.

The [Zig broader-holdout optimization](../candidates/evidence/ZIG-V6-OPTIMIZED.md) profiles the 243 new losses, then adds a one-call literal collector, ordered shared-prefix factoring, correctly normalized prepared-class flags/safe ASCII paths, and direct multiline-start skipping. The final **13-trial**, **323,232-row** paired rerun reaches **1.7334×** on **6,216** unseen tasks (95% range **1.7321–1.7346×**), clearly faster on **5,691/6,216 (91.6%)**, with **two** explained large slowdowns. Filenames, shared prefixes, dense literals, Unicode lines, and units improve **0.495–0.899×→1.032–2.492×**, eliminating all 237 new-family losses; earlier backreference/branch losses also disappear. The full-plane gate catches and fixes the four Unicode-only C0 whitespace characters; both frozen/official/focused suites, **230,337** new differential checks, **264,775** sanitizer checks, **646,464** timing checks, and delegation audits pass. The original five-engine result, two complete paired reruns, interrupted five-engine attempt, 46 pilots/rejections, profiles, raw rows, memory, and clear current graphs are preserved; README again shows only the current state.

The [Rust broader-holdout baseline](../candidates/evidence/RUST-V6-BASELINE.md) freezes the new optimization campaign's honest starting point without changing the fixture, workload weights, candidate families, or success threshold. The existing five-engine comparison puts Rust at **0.1344×** on all **6,216** unseen cases (95% range **0.1343–0.1345×**), with **229** clearly faster cases and **5,892** large slowdowns; fresh compilation is already **1.633–1.733×** and must remain protected. Isolated, correctness-gated execution and allocation profiles expose up to **1,288,260 allocations/165.8 MB per action**, tracing the losses to eager match-state/capture copying, whole-string Unicode preprocessing, and Python/native result construction. New stdlib-self-checked API/property and Unicode oracles expose **7,281/44,659** and **554/3,495** previously hidden mismatches respectively; a surrogate-pattern gate finds another **100/380**. Coverage includes all Python special-case folds, expanding uppercase, nullable captures, windows, and scanners; the full-plane control passes **4,494,555/4,494,555** checks and all findings are retained without waivers. Exact paired Rust measurement/merging/pilot tools preserve all frozen weights, **13** trials, seeds, memory, incomplete-run rejection, and every other candidate. Initial source, fixture, raw data, profiles, findings, and summary hashes are preserved. Improved Rust performance is **NOT MEASURED**.

The [independent Rust search experiment](../candidates/evidence/RUST-V6-SEARCH-LAB.md) tests five from-scratch literal-search strategies and four arbitrary **256-byte** character-class strategies with **557,056** seeded correctness checks, **665** measured component rows, runtime-detected vector instructions, and portable fallbacks. On this host, the vectorized general class filter is **5.90–11.46×** faster than a scalar class scan for **64–262,144-byte** inputs. System byte search is **175–196×** faster for rare first characters but **0.50×** for common-first misses, so both the benefit and counterexample are preserved. This is an architecture experiment, not a Python end-to-end speed claim; frozen Rust candidate performance remains **NOT MEASURED**.

The [extended Rust compatibility oracle](../candidates/evidence/RUST-V6-EXTENDED-ORACLE.md) adds **1,260** complete invalid-window comparisons, **380** raw-surrogate pattern comparisons, and **1,645** numbered, named, scoped, and ASCII backreference comparisons. Its pinned stdlib control passes **47,944/47,944**; the original Rust engine fails **7,471**, and the first faster virtual-machine checkpoint reproduces exactly the same finding and SHA-256 rather than concealing the old bugs. Every special Unicode fold, expanding-uppercase character, nullable capture, scanner/window rule, and backreference distinction remains visible. Both exact self/failure artifacts, deterministic compression, seed, and reproduction commands are preserved. Improved, correctness-qualified Rust performance remains **NOT MEASURED**.

The [Rust benchmark integrity audit](../candidates/evidence/RUST-V6-RUNNER-INTEGRITY.md) verifies all **808,080** historical rows, extracts and analyzes all **323,232** exact Rust/stdlib pairs, reproduces all **12,432** speeds, memory ratios, and large losses, retains all other candidate results, and rejects **15/15** corrupted inputs. It also exposes an honest bootstrap-stream distinction: measuring one candidate instead of four changes one near-boundary significance decision (**229→228**) even though every time and speed is identical. Future results must report their own paired confidence ranges and all **6,216** holdout cases. This is validation of existing data; optimized Rust performance is **NOT MEASURED**.

The [Rust crash and resource-safety oracle](../candidates/evidence/RUST-V6-SAFETY.md) isolates **254** malformed, surrogate, deeply nested, overflowing, windowed, and buffered inputs in bounded subprocesses. The stdlib self-control passes **254/254** with zero crashes or timeouts; the original Rust engine produces **89** real mismatches, including **20 Python-process terminations** from reversed surrogate ranges. Every signal, syntax error, denominator, timeout/resource bound, seed, and category is preserved. No Rust architecture qualifies until this independent safety gate passes with zero crashes, timeouts, or unexplained failures. Optimized Rust performance remains **NOT MEASURED**.

The [Rust native-allocation checkpoint](../candidates/evidence/RUST-V6-NATIVE-PROFILE.md) compares the original matcher with the first ordered-backtracking rewrite on **137** correctness-gated sample tasks. Its reproducible native allocator records **11,279,427→31,868** allocation calls (**99.72% fewer**) and **1.902 GB→138.9 MB** of requests; the sample runs **3.610×** faster than the original Rust. All **six** sample regressions, including dense literal collection and long searches, and the unresolved **18.49 MB** wide-iterator cost are listed. Self-tests, native-binary drift guards, six deliberate corrupted-profile rejections, case hashes, Python-memory limitations, and exact sample confidence intervals are retained. This is a **137-task diagnostic**, not the full **6,216-task** result; optimized holdout performance is **NOT MEASURED**.

The [Rust calibration-only optimization plan](../candidates/evidence/RUST-V6-CALIBRATION-PILOT.md) selects **108** deterministic practice tasks covering all **48** broader workload families, all **12** operations, all **three** lifecycles, four result densities, text/bytes/buffers, and **12** independently selected older slow families. It contains **zero holdout tasks**. Every paired diagnostic checks the original result before and after timing, preserves the four frozen warmups, memory, confidence data, and native-binary hashes, and rejects incomplete or changed runs. This protects the unseen **6,216-task** holdout during iterative Rust optimization; final performance is **NOT MEASURED**.

The [Rust Python API compatibility oracle](../candidates/evidence/RUST-V6-SURFACE.md) independently freezes **1,198** public-interface checks. The pinned Python self-control passes every check; the original Rust interface has **40** real differences, including explicit `None` windows, native match results, group behavior, and exact exception handling. Cases also cover **350** custom-index/window checks, **72** split/replacement counts, subclass and buffer identity, hostile hashing, pickling, and weak references. Findings remain separate from matching performance; every optimized native boundary must pass all **1,198**.

The [second Rust native-allocation checkpoint](../candidates/evidence/RUST-V6-NATIVE-SECOND-CHECKPOINT.md) repeats the same **137** diagnostic tasks and records all **3,014** matching checks. Relative to the original Rust candidate, native allocations fall from **11,279,427 to 26,181**, a **99.77%** reduction; diagnostic speed is **5.481×** (95% range **4.320–6.975×**). Every raw allocation, task, confidence interval, and binary hash is retained. The report explicitly lists all **five** large regressions against the original Rust and records that **96/137** diagnostic tasks remain more than 20% slower than Python. This is a diagnostic sample, not a candidate ranking; rewritten Rust performance on the complete frozen holdout is **NOT MEASURED**.

The [Rust recursion and stack-safety oracle](../candidates/evidence/RUST-V6-DEPTH-SAFETY.md) freezes **348** independently bounded, reproducible cases covering changing recursion limits, nesting through **32,768** levels, huge repetitions, overflowing numeric conditionals, and adversarial matching. Python passes **348/348**, without crashes, timeouts, or reference errors. The original Rust candidate differs on **154** cases and crashes **31** isolated processes. All generated inputs, outcomes, resource limits, signals, and seeds are retained. No optimized Rust implementation qualifies until this entire independent gate passes without unexplained failures.

The [Rust Unicode table experiment](../candidates/evidence/RUST-V6-UNICODE-TABLE-LAB.md) independently generates Python 3.14.6's exact Unicode behavior without importing a regex engine. It compares **14** native table architectures across **72,417,280** character checks and separately verifies all **13,369,344** production properties, including **2,048** surrogates, special case-folds, expanding uppercase, and identifier rules. Every result agrees with Python. The selected compact table is **1.463×** faster than the component baseline (95% range **1.430–1.499×**); a larger alternative is **1.9%** faster still but requires **49,152** additional bytes, and one small nonsignificant slowdown is preserved. These are isolated Unicode measurements, not whole-program benchmark results; full Rust holdout performance is **NOT MEASURED**.

The [historical slowdown-threshold audit](../performance/v6/evidence/REGRESSION-THRESHOLD-AUDIT.md) corrects an important reporting error without changing any frozen workload, measurement, raw result, ranking, or confidence interval. Because speed is Python's time divided by the candidate's time, a task takes more than **20%** longer exactly when its speed is below **5/6**, not **0.8**. On all **6,216** unseen tasks, the corrected large-slowdown counts are Zig **7**, native C **742**, Rust **5,892**, and Python **5,919**. All **seven** final Zig losses, including the **five** previously hidden 20–25% slowdowns, are individually disclosed. Reproducible replacement graphs retain every original observation and display the corrected counts.

The [larger frozen benchmark](../performance/v7/PROTOCOL.md) preserves every version-6 case and adds **64** balanced workload families, producing **20,624** cases and **10,312** genuinely unseen examples. A rejected first draft exposed **1,216** practice-to-holdout duplicates and **2,552** within-family duplicates; the final fixture independently proves that all generated examples are unique. Python generates every answer twice, and all four from-scratch candidates reproduce all answers: **103,120/103,120** checks. The protocol freezes seeds, **13** paired trials, **2,000** confidence samples, the corrected **5/6** slowdown boundary, memory observations, and all five competitors before timing. A separate [no-delegation audit](../performance/v7/evidence/delegation-audit.jsonl) confirms that none of the candidates uses an external regex engine and Rust has zero external dependencies. All version-7 speed, memory, regression, and ranking results are **NOT MEASURED**.

The [Rust replacement experiment](../candidates/evidence/RUST-V6-NATIVE-REPLACEMENT.md) preserves an initially faster but incorrect native replacement design, not a claimed winner. Its full independent oracle exposes **2,132/11,266** observable errors in callback order, mutable buffers, hashing, exact template diagnostics, object identity, and Python's buffer protocol. Every original failure and both reference controls are retained. On **697 practice cases**, the rejected path changes from **0.265× to 0.794×** relative to Python but still has **316** correctly counted large slowdowns; all raw trials and earlier incorrect flags remain visible. The corrected native implementation passes **11,266/11,266**, but its larger-holdout replacement speed is **NOT MEASURED**.

The [complete rewritten Rust engine](../candidates/evidence/RUST-V6-VM-ARCHITECTURE.md) removes the retained syntax-tree interpreter, optional `ctypes` execution, repeated subject conversion, and matching fallbacks. Its independently implemented bytecode, inline backtracking state, exact Python Unicode properties, portable vector search, and native Python bridge pass **21/21** gate steps: **4,494,555** whole-plane checks, **72,248** matching-path comparisons, **11,266** replacements, **420** group-name errors, **738** native-interface cases, the full frozen correctness suites, all official runnable CPython tests, and zero-crash safety and recursion gates. The intermediate **277** Unicode class failures, **21** path failures, original source, and corrected outputs remain archived. Complete expanded-holdout speed and memory are **NOT MEASURED**.

The [Unicode group-name error oracle](../candidates/evidence/RUST-V6-GROUP-NAMES.md) freezes **420** exact definitions, references, and conditionals against pinned Python, including surrogates, zero-width joiners, and unassigned Unicode-16 characters. The original Rust formatter fails **416** cases; the first fix still fails **12**. Both complete failure reports remain archived. The final formatter passes **420/420**, including Python's exact error type, text, original pattern, position, line, and column. Both Python self-controls have zero failures; runtime is **NOT MEASURED**.

The [independent Rust native-interface laboratory](../candidates/evidence/RUST-V6-FFI-LAB.md) freezes **738** exact native-call, Python API, Unicode, buffer, callback, cache, and object-lifetime comparisons. Python's independent self-control passes **546/546**. The first native bridge fails **two** scanner and iterator cycle-lifetime checks; all failures, references, and object-retention traces remain in the compressed evidence. The fixed bridge preserves correct match-object collection and exactly reproduces Python for all **738/738** cases. It uses the project's own native Rust engine, not an external library. Timing, memory, and end-to-end ranking are **NOT MEASURED**.

The [complete Rust correctness campaign](../candidates/evidence/RUST-V6-CAMPAIGN-GATE.md) independently reruns and archives all **21** required static and executable gates against the exact rebuilt production binary. Every gate passes, including zero package delegation, **4,494,555** Unicode operations, **44,084** frozen compatibility cases, all **20,624** expanded benchmark answers, **11,266** replacements, exact scanners and Python object lifetimes, group-name errors, and every bounded crash and recursion check. The **144** official successes and **two** named, unavailable-locale skips are reported separately. The gate is deterministic, isolated, fail-fast, and does not measure performance; Rust's final ranking remains **NOT MEASURED**.

The [from-scratch Rust repetition laboratory](../candidates/evidence/RUST-V6-REPEAT-LAB.md) preserves the actual source, all original timing rows, **35** gate and rejection records, and **59** exactly reproducible research files. Failed counted-repeat attempts expose **24**, then **8**, differences; the corrected engine passes **343,436** independently seeded comparisons. A further possible lazy-search improvement passes **219,587** difficult comparisons but is not selected or timed. Four complete practice-only experiments retain every true **20%** slowdown, including slower counter and short-input alternatives. The unseen benchmark is not accessed, and final speed is **NOT MEASURED**.

The [independent Rust automata laboratory](../candidates/evidence/RUST-V6-AUTOMATA-LAB.md) implements and compares **four** distinct, from-scratch execution strategies: ordered bytecode, exact first-character branch dispatch, fixed-offset literal search, and priority-preserving automaton threads. All **87,408** differential results match pinned Python, and all **12** deliberately unsupported nonregular patterns are explicitly rejected rather than approximated. The raw evidence retains Pike's extra instruction cost and every alternative, exact Unicode case, seed, and failure control. No performance test or unseen input was run; architecture and holdout speed are **NOT MEASURED**.

The [larger native Unicode-table alternative](../candidates/evidence/RUST-V6-UNICODE-TABLE-LAB.md) retains a separately reproducible basic-plane design alongside the selected compact Rust tables. The alternate passes all **13,369,344** independent Unicode-16 checks, preserving exact group rules, folds, surrogates, and invalid values without using a regex library. Component measurements find a **1.9%** improvement with **49,152** additional bytes; whole-engine speed and memory are **NOT MEASURED**. The generator refuses to overwrite the production table, even through an alias or symbolic link, and preserves both independently hashed implementations.

The [Rust compiler and native-boundary experiment](../candidates/evidence/RUST-V6-BUILD-LAB.md) records **68** independently attempted build architectures; **67** compile, import, and pass all correctness checks, while the incompatible LLVM attempt remains documented. All **248,640** paired practice timings, **497,280** result checks, original profiles, and **992** properly counted large slowdowns are archived. The fastest portable practice option improves the current Rust build by **1.100×** but has one **21.36%** slowdown; the fastest regression-free option improves by **1.094×**. GCC, Clang, Zig, link-time and profile-guided builds, machine portability, memory, and every rejection are retained. No holdout or final candidate ranking is measured in this isolated experiment.

## Complete larger benchmark

The [complete expanded benchmark](../performance/v7/PROTOCOL.md) records **20,624** different cases, exactly **10,312** independently held-back cases, all five engines, **13** seeded paired trials, **1,340,560** complete timing records, and every traced-memory and process-memory observation. An [independent full-result audit](../performance/v7/evidence/initial-integrity.json) checks every original observation, all **82,496** candidate case results, all source and native-binary hashes, all **12** cohort rankings, and every process-memory field. The complete [raw timing data](../performance/v7/evidence/initial-raw.jsonl.gz) and [result summary](../performance/v7/evidence/initial-summary.json.gz) are deterministic, verifiable archives; the seven graphs in the [README](../README.md) regenerate directly from those results.

On all **10,312 unseen cases**, Zig is **1.6093×** as fast as Python (95% range **1.6083–1.6103×**), clearly faster on **8,868** cases, and more than 20% slower on **105**. Native C is **1.2710×**, clearly faster on **7,369**, with **1,116** large slowdowns. Rust is **0.9252×**, clearly faster on **3,623**, with **3,905** large slowdowns. The independently implemented Python engine is **0.0222×**, clearly faster on **271**, with **9,884** large slowdowns. The [complete slowdown audit](../performance/v7/evidence/REGRESSION-AUDIT.md) individually reports all **105** unseen Zig losses; the [complete machine-readable regression archive](../performance/v7/evidence/initial-regressions.json.gz) preserves all **29,771** losses across every candidate and cohort. Boundary self-tests independently reject five corrupted results and verify the exact `5/6` cutoff. The raw process-resident memory fields are complete, but the single shared measurement process prevents attributing process memory to an individual engine; only the Python-traced per-candidate ratios can support candidate-specific memory claims.

All candidates passed the original frozen performance answers, but further independent parser, object-identity, buffer, Unicode, and error-behavior oracles subsequently exposed compatibility differences in **every** current candidate. The performance results above remain valid for the frozen cases; none establishes that a candidate is a universal drop-in replacement. Original failures are being preserved and the stronger correctness suite must pass before selecting a winner.

## Frozen full-compatibility baseline

The [expanded cross-engine compatibility oracle](../candidates/evidence/RUST-V7-EDGE-ORACLE.md) freezes **223,198** checks before changing any implementation. The pinned CPython 3.14.6 self-control passes all **223,198** with zero failures and expected-result SHA-256 `b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526`. On exactly the same cases, the original Zig implementation fails **5,281**, Rust fails **24,462**, native C fails **52,655**, and the independent Python engine fails **52,151**. All five complete, deterministically compressed baseline reports preserve every actual and expected outcome, input, seed, category, exception, and candidate source and binary hash.

The frozen matrix covers the original **74,652** edge cases, **69,260** full Unicode and scoped-mode whitespace cases, **19,600** byte-object identity cases, all quantified lookarounds and inverted search windows, observable cache and hashing side effects, **14,783** independent object-contract checks, and the complete **20,480-case** independently generated parser grammar. Every original candidate fails this stronger test. No candidate is promoted, benchmarked as correctness-qualified, or presented as a universal replacement until it passes the complete unchanged oracle; no external regular-expression package, matching fallback, performance case, or held-back input is used by this correctness test.

The [independently frozen grammar oracle](../candidates/evidence/RUST-V7-GRAMMAR-ORACLE.md) separately generates **20,480** deterministic patterns across **16** balanced syntax families, preserving all **14,818** valid patterns and all **5,662** invalid patterns. Two independent CPython reference passes produce the identical full-answer SHA-256 `740e4602f67fa1cfc1ba65d176453009470316a5653cceb19b3c62853a7faab7`; neither has a discrepancy, crash, or timeout. On exactly those original cases, Zig has **279** differences, Rust **5,535**, C **5,587**, and the independent Python implementation **5,573**. All ten deterministic archives retain the complete fixture, seed, two reference runs, four candidate results, every exact error and source position, and the concise failure triage. No timing, performance holdout, external regex engine, or candidate fix is used in freezing this category.

The [independent object and public-API oracle](../candidates/evidence/RUST-V7-OBJECT-ORACLE.md) freezes **14,783** checks covering match-object and complete-subject identity, custom group indexes, mutable and read-only buffers, scanner lifetimes, exact signatures, callbacks, warnings, hash side effects, copy behavior, exceptions, and search windows. Pinned Python agrees with itself on all **14,783** cases. The original Zig engine differs on **541**, Rust on **507**, native C on **10,707**, and the independent Python engine on **11,034**. All five deterministic archives preserve every original observation and difference. An address-only false positive from the initial prototype is normalized and recorded, while lone Unicode surrogates are encoded losslessly so ordinary JSON tools can verify the evidence. No implementation is changed, no performance is measured, and no held-back benchmark case is read.

## Sealed Rust practice experiment

The [practice-data isolation report](../candidates/evidence/RUST-V7-CALIBRATION-ISOLATION.md) identifies and preserves a rejected first approach that filtered practice results only after reading mixed practice and unseen data. Its replacement freezes exactly **10,312 practice cases**, **41,248** previously measured practice results, and a balanced **624-case**, **260-category** optimization plan without generating or decoding a single unseen case. Poisoned-input tests prove that hidden generators, hidden records, mixed results, changed native binaries, and stale correctness reports are rejected. Every Rust measurement must first prove that the exact loaded Python module, native bridge, native engine, and both native sources passed the unchanged **223,198-case** correctness oracle. Original mixed-input evidence is retained, not used to select an improvement. Improved Rust speed is **NOT MEASURED**.

## Corrected Rust baseline

The [fully corrected Rust baseline](../candidates/evidence/RUST-V7-CORRECTED-V4.md) fixes the original **24,462** compatibility differences directly in the from-scratch Rust parser and engine, native Python bindings, and public interface. The actual production module and both loaded native libraries pass all **223,198** frozen compatibility checks, all **20,480** independent grammar checks, all **14,783** independently frozen object checks, and the entire **4,494,555-check** Unicode probe. Earlier frozen correctness versions, all runnable upstream Python tests, replacement and callback tests, error positions, buffers, native-boundary controls, and isolated resource and recursion probes also pass. A [regenerated compatibility graph](../candidates/evidence/rust-v7-correctness.svg) shows every original failure and the corrected result on the unchanged **223,198-case** denominator; six poisoned-result checks prevent dropping a candidate, changing the denominator, or displaying stale native binaries. Both original candidate failures and all corrected complete reports are preserved.

The normal full-campaign runner historically included older and current performance fixtures that overlap the final unseen workloads. A new fail-closed practice-only mode preserves all **17** mandatory compatibility, upstream, Unicode, and safety gates while explicitly excluding all **three** performance-reading steps. Its self-test poisons benchmark-file opens, imports, and child processes and rejects unknown future performance steps. It leaves the existing final full-campaign behavior unchanged. The corrected baseline uses zero external Rust packages and no fallback or candidate delegation. Improved Rust speed remains **NOT MEASURED**; unseen performance cases are **NOT ACCESSED**.

## First corrected-Rust practice measurement

The [complete practice-only baseline](../performance/v7/evidence/RUST-CALIBRATION-BASELINE.md) runs the fully correctness-qualified Rust engine and pinned Python on all **624** frozen practice cases, covering **260** workload categories and all **12** public operations. Seven randomized paired trials produce exactly **8,736** raw observations, with four warmups and **26,208** clean per-operation correctness checks. Overall Rust is **0.993845×**, with 95% confidence interval **0.955726–1.033812×**. The interval includes **1×**, so this is not evidence of an overall improvement.

All **245** individually faster cases, **263** slower cases, **116** unresolved cases, and **175** slowdowns exceeding 20% are preserved. Inspection of match objects is the largest measured weakness (**0.327×**, **48/48** large slowdowns), followed by scanners (**0.827×**, **25/48**) and result collection (**0.906×**, **31/80**). Compilation is already **2.432×** with no large slowdowns. These are practice results only; each subsequent architecture must first pass the same unchanged **223,198-check** compatibility oracle and then be compared on the complete, unchanged practice plan. The **10,312-case** final holdout remains inaccessible and **NOT MEASURED**.

The independently frozen [architecture-comparison control](../performance/v7/evidence/rust-v7-calibration-baseline-variant-control-integrity.json) verifies the actual five Rust source and native-library mappings, all **8,736** original timing records, all **624** cases, every baseline slowdown, and all **625** case and overall confidence intervals. Its self-test rejects **39** deliberate changes, including hidden holdout cases, omitted regressions, modified native libraries, different trial counts, and falsified case comparisons. Future architecture runs must use the identical seven-trial practice plan and preserve the original baseline; measurements from different runs are never mislabeled as directly paired confidence intervals.

## Historical-data isolation incident

The [historical benchmark isolation report](../candidates/evidence/RUST-V7-ISOLATION-INCIDENT.md) preserves an auxiliary research branch's immediately disclosed, read-only exposure to old version-6 benchmark text after the practice baseline was published. That complete branch and all of its proposed architectures are quarantined and excluded from candidate selection. No final fixture was generated or decoded, no candidate was timed, and no source or existing benchmark record was changed. Subsequent experiments are restricted to independently developed, correctness-qualified candidates and the separately frozen practice-only plan.

## Frozen tracing and callback compatibility

The independently frozen [Python-visible behavior oracle](../candidates/evidence/RUST-V7-OBSERVABILITY-ORACLE.md) records **479** complete cases covering Python tracing, `sys.monitoring`, recursive replacement callbacks, custom index conversions, exact exception behavior, and object lifetimes. Two isolated runs of pinned CPython agree on every case; the corrected Rust engine also passes all **479**. The oracle separately verifies all **34** malformed native-call controls and actively blocks all **13** routes into Python's or a third party's regex engine. Two apparent iterator mismatches are fully preserved and rejected: their private class names differ, but all publicly visible matches, iteration, argument side effects, and exceptions are identical. A future canonical Rust build must present its own unchanged **223,198-case**, five-artifact correctness proof before this frozen suite accepts it. The six full evidence archives remain verifiable after production binaries change; no benchmark or final test is read.

## Rejected native match-object optimization

The [first native match-object experiment](../performance/v7/evidence/RUST-CALIBRATION-MATCH-REJECTED.md) uses direct compact integers, exact-string known hashes, independently sized fresh result dictionaries, and correct complete-string identity. It passes all **223,198** compatibility checks, all independent grammar and object checks, the full **479-case** tracing oracle, and all safety probes. The frozen seven-trial practice comparison nevertheless measures **0.983540×** overall, down from the original **0.993845×**. The targeted match-object workload remains **48/48** more than 20% slower. All **172** new large slowdowns and all **175** original ones are preserved; neither separately measured run establishes an overall speedup. The optimization is rejected and the baseline restored. The unseen final benchmark remains **NOT ACCESSED**.

## Stronger real-user object and lifetime compatibility

The separately frozen [deep public-contract oracle](../tools/rust_v8_deep_contract_oracle.py) adds **393** independently generated object, buffer, garbage-collection, callback, copying, iterator, scanner, introspection, tracing, and warning checks, including **64** fixed-seed adversarial cases. Two isolated runs of pinned CPython agree on every case. All **13** attempts to make the production engine delegate to Python or an external regex package are blocked.

The [complete original Rust failure archive](../candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz) preserves **104** real public mismatches: **48** scanner and iterator copying failures, **32** method-information failures, **four** mutable-buffer failures, **three** lifetime and finalization failures, **three** object-information failures, and **14** corresponding seeded failures. A further **64** private garbage-collector topology differences are fully recorded and are not presented as public mismatches. The unchanged **223,198-check** suite continues to pass, which is precisely why the independently frozen, stronger test is necessary. The new oracle fails explicitly until every real public difference is fixed; no failure is waived, no held-back performance case is read, and speed is **NOT MEASURED**.

The [variant-safe deep-contract gate](../tools/rust_v8_deep_contract_variant.py) allows a repaired Rust engine to be tested against the exact same frozen **393** cases without changing or overwriting the original **104-failure** archive. It independently verifies all **223,198** original checks, the actual five loaded Rust source and native artifacts, both Python reference answers, all **13** anti-delegation checks, all **64** separately recorded private diagnostics, and all **12** stale-result, wrong-artifact, and overwrite controls. Its baseline self-test reproduces the complete original failure report byte-for-byte. Every improved or rejected implementation must produce a separately named, complete evidence archive; a remaining real mismatch still exits unsuccessfully.

## First independent Rust scanner and lifetime repair

The [complete original-test result](../candidates/evidence/rust-v8-edge-oracle-rust-scanner-lifetimes.json.gz) verifies that the first scanner repair still passes **223,198 of 223,198** frozen checks on the exact pinned Python baseline. Its own Rust code retains buffer owners during iteration, exposes a genuine Python callable iterator, and implements the ordinary object reconstruction protocol without importing Python `re`, `_sre`, or an external matching engine. Python's `copyreg` supplies only generic object-copying rules; importing it in isolated Python loads none of those regex modules.

The separately preserved [stronger-test result](../candidates/audits/RUST-V8-DEEP-CONTRACT-SCANNER-LIFETIMES.json.gz) contains all **393** original cases, all **13** active no-delegation guards, the exact source and loaded native-library hashes, and both complete Python reference answers. Public failures fall from **104 to 62** without dropping a case or changing an expected answer. The **62** remaining differences comprise **17** ordinary and seeded scanner-copy cases, **40** ordinary and seeded public-method cases, **three** ordinary and seeded finalization cases, and **two** object-information cases. All **39** remaining implementation-private collector observations are retained separately, not counted as public failures. The report correctly exits unsuccessfully; performance is **NOT MEASURED**, and the sealed final test is **NOT ACCESSED**.

The historical tracing oracle previously required two old, private iterator-class differences to remain reproducible even after the new implementation fixed them. Its original source, baseline, and rejected diagnostics remain unchanged. The additive [frozen-behavior variant](../tools/rust_v7_observability_variant.py) instead checks the same **479** complete public observations, **34** malformed-binding controls, **13** live anti-delegation guards, **two** standard-Python references, and **five** actual source and native-library identities. Both repaired iterators are genuine `callable_iterator` objects with Python-equivalent public results. The [complete passing archive](../candidates/evidence/rust-v8-observability-scanner-lifetimes.json.gz) also independently retains **10** historical artifact poisons and **16** new observation, iterator, native-artifact, and delegation poisons. It neither drops a frozen test nor counts private class names as public regex behavior.

The independently generated [Rust-only source and native-code certificate](../candidates/audits/RUST-V8-SCANNER-FROM-SCRATCH.json) ties the exact scanner build to all **223,198** original checks. Its [reproducible verifier](../tools/audit_rust_from_scratch.py) verifies all **five** source and native artifacts; the Rust-owned parser, compiler, and matching engine; zero external Cargo packages; both native libraries; and their actual mappings in a separate Python process. All **76** independently isolated shared anti-delegation controls and all **49** Rust-specific poisoned-input controls pass. The three new shared controls permit only generic `copyreg` in the exact Rust binding and reject the same import from another candidate or a lookalike package. The certificate does not inspect another candidate, run a benchmark, or open the final test.

## Genuine native Rust scanner and object protocol

The second Rust scanner implementation uses a genuine Python C-API `PyCMethod`, a real `callable_iterator`, and the same scanner garbage-collection rules as pinned CPython. It still invokes only the independent Rust engine, never `_sre`, Python `re`, or another candidate. The [complete edge proof](../candidates/evidence/rust-v8-edge-oracle-rust-scanner-cmethod.json.gz) again passes **223,198/223,198**. The [fully preserved deep result](../candidates/audits/RUST-V8-DEEP-CONTRACT-SCANNER-CMETHOD.json.gz) reduces user-visible failures from **104**, to **62**, to **43**, eliminating every scanner-copy mismatch. The remaining **43** comprise **40** method-information cases, **two** weak-reference finalization cases, and **one** pattern-identity case.

The [new tracing evidence](../candidates/evidence/rust-v8-observability-scanner-cmethod.json.gz) preserves all **479** public observations, **34** native-boundary checks, **13** blocked regex entry points, both genuine Python-compatible iterators, **31** new poisoned inputs, **10** historical controls, and **four** self-reference checks. Its [additive verifier](../tools/rust_v8_observability_variants.py) retains the first scanner evidence unchanged. The [exact-build provenance certificate](../candidates/audits/RUST-V8-CMETHOD-FROM-SCRATCH.json) verifies all **five** source and native artifacts, zero external Rust dependencies, both actual mapped libraries, **104** variant checks, **49** preserved scanner checks, and **76** shared anti-delegation controls. Concurrent poison runs once failed closed under process contention; a serialized complete rerun passes without removing any test or overwriting a failure. Performance is **NOT MEASURED**, and the held-back test is **NOT ACCESSED**.

## Fully compatible from-scratch Rust implementation

The first native-pattern-descriptor experiment preserves all **223,198** frozen matching checks but exposes [**32 real remaining differences**](../candidates/audits/RUST-V8-DEEP-CONTRACT-NATIVE-DESCRIPTORS.json.gz). Genuine built-in Python methods, a correctly based native `re.Pattern` type, accurate public method descriptions, and exact scanner and match-object lifetimes remove every remaining difference. A [first complete native-heap result](../candidates/audits/RUST-V8-DEEP-CONTRACT-NATIVE-HEAP.json.gz) matches Python on all **393** cases but is correctly rejected by the strict native-source auditor: it includes a standard header outside the auditor's previously frozen approved list. Neither the failed **32-case** experiment nor the rejected-header pass is hidden or certified.

The final implementation removes the extra header without changing the auditor. Its exact [final matching evidence](../candidates/evidence/rust-v8-edge-oracle-rust-native-heap-final.json.gz) passes all **223,198** cases and **49** categories; its [independent parser evidence](../candidates/evidence/rust-v7-grammar-rust-v8-native-heap-final.json.gz) passes all **20,480** cases; and its [complete deep-contract evidence](../candidates/audits/RUST-V8-DEEP-CONTRACT-NATIVE-HEAP-FINAL.json.gz) passes all **393** cases with both standard-Python references in complete agreement. The [full tracing and native-call evidence](../candidates/evidence/rust-v8-observability-native-heap-final.json.gz) independently passes all **479** observations, **34** native boundary controls, **13** active regex-delegation guards, **40** poisoned-evidence controls, and **six** archive and source-identity controls.

The separately generated [strict native-code certificate](../candidates/audits/RUST-V8-NATIVE-HEAP-FROM-SCRATCH.json) and its [additive verifier](../tools/audit_rust_native_heap_from_scratch.py) prove the actual five Python and native artifacts, six Rust and bridge source files, two real loaded native-library mappings, the complete **223,198** and **393** results, independently owned parser, compiler, and executor, zero external Cargo dependencies, and **115** malicious-input checks. One resource-contended verification was terminated by the host and correctly produced no certificate; a full serialized rerun passed every check without weakening or removing a test. No Python regex engine, external regex package, other candidate, hidden benchmark, or unopened performance case is used. Speed remains **NOT MEASURED**.

## Independent Zig correctness and stronger-test failures

The independently rebuilt Zig parser, compiler, matching engine, and native Python bridge reduce the original frozen compatibility failures from **5,281** to **339**, then **128**, and finally **zero**. The [complete corrected evidence](../candidates/evidence/rust-v8-edge-oracle-zig-corrected-v1.json.gz) passes all **223,198** unchanged cases and all **49** categories. The separately gated [Zig grammar evidence](../candidates/evidence/rust-v7-grammar-zig-v8-corrected-v1.json.gz) passes all **20,480** independent parser cases with zero errors, crashes, or timeouts. The implementation uses its own Zig matching engine, not Python `re`, an external regex library, or another candidate.

The additive [four-engine deep-contract gate](../tools/rust_v8_multi_candidate_contract.py) applies the exact frozen **393** original Python object and lifetime cases to independently verified candidate engines. It first validates each candidate's full **223,198-case** evidence and its actual source and native binaries, repeats both pinned Python references, blocks all **13** original delegation routes and additional cross-engine imports, and passes **24** poisoned-evidence controls. The [complete Zig result](../candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-CORRECTED-V1.json.gz) truthfully retains **141** genuine failures: **53** normal and seeded scanner-copy cases, **40** method cases, **21** callback cases, **12** group-conversion cases, **six** lifetime cases, **four** buffer cases, **three** object cases, and **two** warning cases. Private diagnostics are counted separately. Zig is not claimed to be a complete replacement; speed is **NOT MEASURED**, and the final test remains **NOT ACCESSED**.

## Fully compatible from-scratch Zig implementation

Four independently recorded Zig iterations reduce the complete frozen deep-test failure count from **141** to [**92**](../candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-01.json.gz), [**50**](../candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-02.json.gz), [**29**](../candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-03.json.gz), and finally [**zero**](../candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-04.json.gz). Each retained stage has its own complete **223,198-check** edge proof and independently verified current source and native-library hashes.

The fixes implement genuine Python native scanner and match objects, correctly ordered reference lifetimes, real `callable_iterator` behavior, real C method descriptors and bound-method types, exact warnings and errors, arbitrary user-defined group converters, and correctly preserved nested callback exceptions. Every match is still computed by the separately written Zig engine; Python `re`, `_sre`, third-party engines, and the other candidates are actively blocked.

The final [Zig matching result](../candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-04.json.gz) passes **223,198/223,198**. Its [independent grammar result](../candidates/evidence/rust-v7-grammar-zig-deep-stage-04.json.gz) passes **20,480/20,480**, and its [deep public-contract result](../candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-04.json.gz) passes **393/393**, with both Python references in complete agreement and **23** active anti-delegation guards. The source, both actual loaded Zig binaries, and all **76** source and runtime provenance controls were separately verified. Zig is the first correctness-qualified contender, not a declared speed winner: the enlarged final benchmark remains sealed and speed is **NOT MEASURED**.

## Independent C engine correctness and stronger-test failures

The independently implemented native C parser, compiler, bytecode engine, and Python interface reduce **52,655** original compatibility failures to **zero**, without invoking Python's regex implementation, another candidate, or an external regex package. The [complete C-engine edge result](../candidates/evidence/rust-v8-edge-oracle-vm-corrected-v1.json.gz) passes all **223,198** frozen checks and **49** categories. The separately frozen [C grammar result](../candidates/evidence/rust-v7-grammar-vm-v8-corrected-v1.json.gz) passes all **20,480** parser checks without errors, crashes, or timeouts.

The identical frozen [393-case C deep-contract result](../candidates/audits/RUST-V8-DEEP-CONTRACT-C-CORRECTED-V1.json.gz) preserves **130** genuine remaining differences: **53** ordinary and seeded scanner-copy cases, **40** method-information cases, **16** callback cases, **11** buffer cases, **seven** lifetime cases, and **three** object-information cases. Both Python reference processes agree, and all **13** original regex guards and **10** additional cross-engine guards pass. C is not yet fully qualified; performance is **NOT MEASURED**, and the sealed test is **NOT ACCESSED**.

## C matching, parser, and object compatibility

The first native-object repair reduces the independently written C engine's original **130** deeper failures to [**38**](../candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-01.json.gz). A [second stage](../candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-02.json.gz) matches Python on all **393** cases, but is rejected: its native bridge dynamically imports `copyreg`, and its Python interface aliases the pattern class instead of exposing its own independently declared class. Both complete matching and behavior results remain archived; passing behavior alone does not excuse a failed from-scratch audit.

The stage-three C implementation fixes those issues without changing or weakening the auditor. Its genuinely owned Python parser, bytecode compiler, native C matching engine, real pattern class, built-in method descriptors, scanner, and callable iterator pass the static source, independent-pipeline, and native-library checks. It passes all [**223,198 original matching tests**](../candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-03.json.gz), all [**20,480 independently frozen parser tests**](../candidates/evidence/rust-v7-grammar-vm-v8-deep-stage-03.json.gz), and all [**393 real-world behavior tests**](../candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-03.json.gz). Both isolated Python references agree; all **13** external-regex and **10** cross-candidate delegation guards pass. The C engine remains entirely independent of Python `re`, external regex packages, Zig, Rust, and the other Python candidate. Performance is **NOT MEASURED**, and the expanded final benchmark is **NOT ACCESSED**.

## Same frozen tracing and argument tests for every native engine

The [independent multi-candidate tracing gate](../tools/rust_v8_multi_candidate_observability.py) runs the exact same frozen **479** Python-visible checks for each native engine. It first verifies that each engine has genuinely passed its exact **223,198-case** matching result and **393-case** object result, fingerprints the actual owned native libraries, repeats both independent Python reference runs, verifies **34** real engine-specific native argument controls, actively blocks Python and external regex engines through **13** guards, and blocks at least **10** cross-candidate routes. All **28** dropped-result, changed-denominator, swapped-engine, false-native, stale-binary, and overwrite self-tests pass.

Both [Rust](../candidates/evidence/rust-v8-observability-rust-qualified.json.gz) and [Zig](../candidates/evidence/rust-v8-observability-zig-qualified.json.gz) match Python on **479/479** observations with zero failures. The [first C result](../candidates/evidence/rust-v8-observability-vm-qualified.json.gz) exposes **75** genuine public differences: **60** unusual public-method argument cases and **15** independently seeded variants. Its **34** native safety controls and both Python self-oracles pass; the observed differences are not waived, removed, or presented as success. C's previous **393-case** result remains valid for that separately frozen suite but does not establish compatibility with the stronger tracing suite. All hidden performance cases remain unopened and performance remains **NOT MEASURED**.

## Fully compatible native C argument handling

All **75** C failures come from genuine public-method argument binding, not regex matching. The native scanner, matching, split, and substitution methods must reject missing, repeated, excess, and unknown arguments with exactly Python's observable message and precedence. The independent C engine now implements one shared, from-scratch native argument binder for its actual built-in methods. It does not import Python `re`, call `_sre`, delegate to Zig or Rust, change a test, or replace a true native method with a Python wrapper.

The repaired implementation passes its fresh [**223,198-case matching gate**](../candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-04.json.gz), [**20,480-case independent parser gate**](../candidates/evidence/rust-v7-grammar-vm-v8-deep-stage-04.json.gz), [**393-case deep object gate**](../candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-04.json.gz), and [**479-case tracing and unusual-argument gate**](../candidates/evidence/rust-v8-observability-vm-qualified-stage-04.json.gz). All **34** actual native argument checks, **13** anti-regex guards, and **10** cross-engine guards still pass. The [complete original 75-failure archive](../candidates/evidence/rust-v8-observability-vm-qualified.json.gz) remains unchanged. The [refreshed all-engine source and actual-library audit](../candidates/audits/FROM-SCRATCH-AUDIT.json) independently passes all **76** controls for the rebuilt C binary and all other current candidates; its [immediately preceding audit](../candidates/audits/FROM-SCRATCH-AUDIT-BEFORE-C-BINDER-REPAIR.json) remains available. Speed is **NOT MEASURED**, and the expanded final benchmark remains sealed.

## Complete holdout-blind correctness campaigns

The [multi-engine campaign runner](../tools/rust_v8_multi_candidate_campaign.py) independently plans **22** actual frozen correctness, safety, and anti-delegation steps per native engine. Its plan includes both original matching suites, the official runnable Python tests, replacements and callbacks, separately isolated crash and overflow checks, all **4,494,555** full-Unicode comparisons, the complete **479-case** real tracing test, each engine's own native argument controls, and the current all-family source and loaded-library audit.

Its pinned-Python self-test passes all **46** poisoned missing-suite, changed-denominator, wrong-candidate, stale-artifact, and held-out-data controls. It explicitly excludes the same **three** older steps that could open performance cases. This result validates the runner, not the candidates: a candidate is not credited with passing until its real **22-step** run succeeds. The final speed test remains sealed and performance is **NOT MEASURED**.

## Full campaigns expose additional replacement failures

The current independent Rust engine passes its [complete, actually executed 22-stage frozen campaign](../candidates/evidence/rust-v8-rust-native-heap-final-sealed-campaign.json). Its [fresh multi-family deep proof](../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-NATIVE-HEAP-MULTIFAMILY.json.gz) separately binds the actual Rust engine and bridge to all **393** unchanged observations and all cross-engine guards. The complete campaign verifies **8,862** replacement and callback checks, **11,266** deeper replacement checks, **4,494,555** full-Unicode comparisons, the original Python suites, actual native guards, and the complete **479-case** tracing suite without opening any performance fixture.

Running that identical unchanged campaign on Zig exposes [**3,392/8,862** replacement failures](../candidates/evidence/rust-v8-replacement-zig-stage-04-original-failures.json.gz); the independently retained [deeper run](../candidates/evidence/rust-v8-replacement-zig-stage-04-original-deep-failures.json.gz) exposes **5,043/11,266**. The same standalone checks expose [**361/8,862** C failures](../candidates/evidence/rust-v8-replacement-vm-stage-04-original-failures.json.gz) and [**1,879/11,266** deeper C failures](../candidates/evidence/rust-v8-replacement-vm-stage-04-original-deep-failures.json.gz). Both pinned-Python self-oracles agree; every case, category, expected answer, actual answer, callback side effect, and error is recorded. Their earlier passing **223,198**, **20,480**, **393**, and **479** results are not used to conceal these additional failures. Zig and C are not considered full-campaign-qualified until their own genuine implementations pass both larger suites. Performance is **NOT MEASURED** and the **12,288-case** final holdout remains unopened.

## First fully qualified Rust practice baseline

Only after Rust passed its actual **22-stage** campaign was it compared with pinned standard Python on the unchanged, sealed **624-case** practice plan. Its first [complete diagnostic run](../performance/v7/evidence/rust-v7-calibration-native-heap-qualified-baseline-summary.json) produced **8,736** paired timing rows, **26,208** clean before/during/after correctness checks, **0.7683×** overall speed, and **344** slowdowns exceeding **20%**. The old architecture-integrity auditor correctly rejected that run's version-eight matching-proof filename; no timing, failed audit, or case was hidden.

The same frozen **223,198-case** matching oracle was independently rerun to produce the [exact version-seven-named proof](../candidates/evidence/rust-v7-edge-oracle-rust-native-heap-qualified.json.gz). Its deterministic compressed SHA-256 is identical to the previously certified version-eight proof. A new fully independent seven-trial [certified practice baseline](../performance/v7/evidence/RUST-NATIVE-HEAP-BASELINE.md) measures **0.7543×** with **0.7225–0.7911×** confidence, **132/624** clearly faster cases, and all **347/624** substantial slowdowns preserved. The [fresh full-result audit](../performance/v7/evidence/rust-v7-calibration-native-heap-certified-baseline-integrity.json) separately recomputes all **625** confidence intervals, verifies all **8,736** rows, all **624** cases, all **five** actual Rust artifacts and native mappings, all **175** historical slowdowns, and all **39** corruption controls.

The [five regenerated practice-only graphs](../performance/v7/evidence/rust-v7-calibration-overall.svg) include both the previous corrected Rust and the fully compatible native-heap engine; no regression, candidate, confidence interval, or old result is omitted. The two separately timed runs are never described as paired against each other. The **12,288-case** final test remains **NOT ACCESSED**.

## Native Rust attribute-name experiment

The first measured fully compatible Rust result identified repeated Python/native attribute lookup as an everyday matching cost. A single, independent [native-call experiment](../performance/v7/evidence/RUST-NATIVE-INTERNED-ATTRIBUTES.md) interns the six actual attribute names once at bridge initialization. Every call still executes the same genuine Python attribute access, reference ownership, user-visible conversions, built-in method, and from-scratch Rust matching engine; no answer is cached and no external regex implementation is invoked.

The optimized engine passes a fresh [**223,198-case matching gate**](../candidates/evidence/rust-v7-edge-oracle-rust-native-interned-attributes.json.gz), [**393-case object gate**](../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-INTERNED-ATTRIBUTES.json.gz), [**479-case tracing gate**](../candidates/evidence/rust-v8-observability-rust-qualified-interned-attributes.json.gz), both separately archived [**8,862-case**](../candidates/evidence/rust-v8-replacement-rust-interned-attributes.json.gz) and [**11,266-case**](../candidates/evidence/rust-v8-replacement-rust-interned-attributes-deep.json.gz) replacement gates, and its complete [**22-stage** correctness campaign](../candidates/evidence/rust-v8-rust-interned-attributes-sealed-campaign.json), including all **4,494,555** full-plane Unicode checks.

The [additive from-scratch audit](../candidates/audits/RUST-V8-INTERNED-ATTRIBUTES-FROM-SCRATCH.json) independently fingerprints the actual optimized Rust source, both loaded native libraries, the complete matching, object, and tracing evidence, and every historical proof. All **134** controls pass, including **125** deliberately corrupted inputs, all **115** inherited native-heap checks, and all **76** original anti-delegation checks. The first isolated control run terminated with host signal **9** while checking its nested original audit; it failed closed without accepting or publishing a report. One serialized full retry passed every control before the final audit was allowed to run.

The isolated seven-trial practice result improves from **0.7543×** to **0.9290×**, with **0.8931–0.9668×** confidence against pinned Python. Major slowdowns fall from **347** to **243** of the same **624** cases. The [independent 39-control audit](../performance/v7/evidence/rust-v7-calibration-native-heap-interned-attributes-integrity.json) verifies every timing row, confidence interval, five actual native artifacts, and all historical losses. The separate runs are not described as directly paired and the remaining **243** regressions are not hidden. The final holdout is **NOT ACCESSED** and final speed is **NOT MEASURED**.

## Independently repaired C replacements and callback buffers

The original C implementation produced [361 differences in 8,862 replacement checks](../candidates/evidence/rust-v8-replacement-vm-stage-04-original-failures.json.gz) and [1,879 differences in 11,266 deeper checks](../candidates/evidence/rust-v8-replacement-vm-stage-04-original-deep-failures.json.gz). Its actual owned C engine was repaired in three separate implementation stages; it never imports or calls a Python, Rust, Zig, third-party, or external regular-expression engine. The first retained [standard](../candidates/evidence/rust-v8-replacement-vm-stage-05.json.gz) and [deep](../candidates/evidence/rust-v8-replacement-vm-deep-stage-05.json.gz) runs leave **56** genuine deep failures. The next [standard](../candidates/evidence/rust-v8-replacement-vm-stage-06.json.gz) and [deep](../candidates/evidence/rust-v8-replacement-vm-deep-stage-06.json.gz) runs leave **44**. No failed case or intermediate result is overwritten.

The final from-scratch implementation passes [all 8,862 replacement and callback checks](../candidates/evidence/rust-v8-replacement-vm-stage-07.json.gz) and [all 11,266 deeper replacement and callback checks](../candidates/evidence/rust-v8-replacement-vm-deep-stage-07.json.gz). The same exact source and actual native binary separately pass the frozen [223,198-case matching oracle](../candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-07.json.gz), [20,480-case independent parser oracle](../candidates/evidence/rust-v7-grammar-vm-v8-deep-stage-07.json.gz), [393-case public object contract](../candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-07.json.gz), and [479-case tracing and unusual-argument oracle](../candidates/evidence/rust-v8-observability-vm-qualified-stage-07.json.gz). All **34** native-binding, **13** forbidden-regex, and **10** cross-engine guards pass.

Its [first actual full-campaign attempt](../candidates/evidence/rust-v8-vm-stage-07-sealed-campaign-failure.json) then fails closed at `frozen-correctness-v2`: **8,238/8,244** checks pass and **six** do not. The exact failing case identifiers, real captured process output, native/source hashes, unchanged **45** obligations, and absence of a generated success report are all preserved. The record is explicitly an honest failed-process observation, not a fabricated 22-stage campaign report. C is **NOT** a fully qualified replacement, its speed is **NOT MEASURED**, and no final benchmark is opened.

## A two-line C Unicode fix exposes the next official Python failure

All six earlier C failures involve the Unicode long-s character `ſ` inside a case-insensitive character range. The owned C engine already has a general Unicode `folded` operation; its range matcher simply did not apply it before testing the range. Adding that existing fold in the Unicode-only branch corrects the behavior without using another engine, adding a package, changing ASCII or bytes rules, or special-casing a test.

The genuinely repaired engine passes the complete frozen [8,244-case correctness suite](../candidates/evidence/rust-v8-vm-stage-08-frozen-correctness-v2.json), [223,198-case matching suite](../candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-08.json.gz), [20,480-case parser suite](../candidates/evidence/rust-v7-grammar-vm-v8-deep-stage-08.json.gz), [393-case public-object suite](../candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-08.json.gz), [479-case observability suite](../candidates/evidence/rust-v8-observability-vm-qualified-stage-08.json.gz), [8,862-case replacement suite](../candidates/evidence/rust-v8-replacement-vm-stage-08.json.gz), and [11,266-case deep-replacement suite](../candidates/evidence/rust-v8-replacement-vm-deep-stage-08.json.gz).

Its [next complete-campaign attempt](../candidates/evidence/rust-v8-vm-stage-08-sealed-campaign-failure.json) still correctly fails closed: Python's official `ReTests.test_ignore_case_range` exposes **one failure in 146 methods**, with **143** passes, **two** skips, no crashes, and no timeouts. The complete process output, official fixture hashes, exact native source and binary, all seven passing prerequisites, and absence of a campaign-success report are preserved. C remains **NOT** fully qualified; no final benchmark is opened.

## Symmetric C Unicode ranges and an honest public-surface failure

Python's own character-range suite requires case equivalence to work in both directions. A range containing `K` must match `K` and `k`; the same holds for the long-s, related Cyrillic characters, ligatures, and sharp-S. The owned C implementation already specifies these genuine equivalence families in its independent Python layer. Its native matcher now checks the same bounded groups in constant time, without scanning Unicode, changing ASCII or locale rules, borrowing an engine, or hardcoding a frozen case.

The repaired implementation passes the [previously failing official range test](../candidates/evidence/rust-v8-vm-stage-09-official-ignore-case-range.json), [all 146 official methods](../candidates/evidence/rust-v8-vm-stage-09-official-cpython-tests.json), [all 8,244 additional correctness checks](../candidates/evidence/rust-v8-vm-stage-09-frozen-correctness-v2.json), [all 223,198 matching checks](../candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-09.json.gz), [all 20,480 grammar checks](../candidates/evidence/rust-v7-grammar-vm-v8-deep-stage-09.json.gz), [all 393 object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-09.json.gz), [all 479 tracing checks](../candidates/evidence/rust-v8-observability-vm-qualified-stage-09.json.gz), and both [8,862-case](../candidates/evidence/rust-v8-replacement-vm-stage-09.json.gz) and [11,266-case](../candidates/evidence/rust-v8-replacement-vm-deep-stage-09.json.gz) replacement suites.

Its [unchanged full-campaign attempt](../candidates/evidence/rust-v8-vm-stage-09-sealed-campaign-failure.json) nevertheless fails the stronger frozen `upstream-public-surface` stage: **six differences in 190 checks**. The real stage output, source and actual native hashes, all previous successful checks, and absence of a completed 22-stage report are preserved. No failing case identifier is invented. C remains **NOT** fully qualified and final performance is **NOT MEASURED**.

## Native C method errors and Unicode group-name failures

A standalone, unmodified [190-case public-interface probe](../candidates/evidence/rust-v8-vm-stage-09-upstream-public-surface-failure.json) exposes exactly six remaining C differences. For both text and bytes, `Match.start`, `Match.end`, and `Match.span` must reject excess arguments with their actual method name. The C matcher used an unnamed Python argument parser, which generated a different error. Replacing it with Python's standard named `PyArg_UnpackTuple` fixes the genuine method behavior without changing the regex engine, importing a package, or inserting test answers.

The new implementation passes [all 190 upstream public checks](../candidates/evidence/rust-v8-vm-stage-10-upstream-public-surface.json), [all official Python tests](../candidates/evidence/rust-v8-vm-stage-10-official-cpython-tests.json), [all 8,244 frozen checks](../candidates/evidence/rust-v8-vm-stage-10-frozen-correctness-v2.json), [all 223,198 matching checks](../candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-10.json.gz), [all 20,480 grammar checks](../candidates/evidence/rust-v7-grammar-vm-v8-deep-stage-10.json.gz), [all 393 public-object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-10.json.gz), [all 479 tracing checks](../candidates/evidence/rust-v8-observability-vm-qualified-stage-10.json.gz), and [both](../candidates/evidence/rust-v8-replacement-vm-stage-10.json.gz) [replacement suites](../candidates/evidence/rust-v8-replacement-vm-deep-stage-10.json.gz).

The [next full-campaign attempt](../candidates/evidence/rust-v8-vm-stage-10-sealed-campaign-failure.json) nevertheless exposes **144 failures in 420** production Unicode group-name error checks. Both Python reference runs agree. The exact runner output, random seed, native source and binary, all earlier failures, and all nine passing prerequisites remain available. The temporary frozen worker did not preserve individual failing records, so no case identifiers are invented. C is **NOT** a complete replacement; final performance is **NOT MEASURED**.

## C Unicode group-name repair and the next genuine failure

A fresh unchanged [420-case standalone check](../candidates/evidence/rust-v8-vm-stage-10-unicode-group-name-failure.json) captures all **144** previous C failures and both agreeing Python references. Two minimal changes to the C family's independently owned Python front-end fix general Unicode group-name representation and line-and-column formatting; [all 420 checks now pass](../candidates/evidence/rust-v8-vm-stage-11-unicode-group-name.json). The [complete stage-11 report](../candidates/evidence/C-STAGE-11-COMPATIBILITY.md) links actual passing Python, parser, matching, public-object, tracing, native-binding, and replacement results.

Exactly one unmodified [complete campaign attempt](../candidates/evidence/rust-v8-vm-stage-11-sealed-campaign-failure.json) still fails `extended-cpython-paths`; its original reporter cannot serialize the actual expected Python pattern. The actual failing case and number of completed checks are **NOT REPORTED**. One separately authorized [diagnostic](../candidates/evidence/rust-v8-vm-stage-11-extended-path-first-mismatch-interrupted.json) was honestly interrupted before emitting a case so that the Rust practice measurement remained uncontended. C remains **NOT QUALIFIED**; no hidden benchmark was used.

## Independently repaired Zig replacements and Python buffers

The original separately written Zig engine produced [3,392 differences in 8,862 replacement checks](../candidates/evidence/rust-v8-replacement-zig-stage-04-original-failures.json.gz) and [5,043 differences in 11,266 deeper checks](../candidates/evidence/rust-v8-replacement-zig-stage-04-original-deep-failures.json.gz). Its first genuine repair passes [all standard checks](../candidates/evidence/rust-v8-replacement-zig-stage-05-from-scratch-failures.json.gz) but retains [128 deeper Python-buffer differences](../candidates/evidence/rust-v8-replacement-zig-stage-05-from-scratch-deep-failures.json.gz). These were caused by requesting a different Python buffer mode from Python's own regular-expression module; the actual owned Zig bridge was repaired without borrowing another engine, external regex library, or Python's production matcher.

The final Zig stage passes [all 8,862 standard replacement checks](../candidates/evidence/rust-v8-replacement-zig-stage-06-from-scratch-failures.json.gz) and [all 11,266 deeper replacement and callback checks](../candidates/evidence/rust-v8-replacement-zig-stage-06-from-scratch-deep-failures.json.gz). The exact same five owned source and actual-native-library fingerprints independently pass the [223,198-case matching oracle](../candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-06.json.gz), [20,480-case parser oracle](../candidates/evidence/rust-v7-grammar-zig-v8-deep-stage-06.json.gz), [393-case public object contract](../candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-06.json.gz), and [479-case tracing and unusual-argument oracle](../candidates/evidence/rust-v8-observability-zig-qualified-stage-06.json.gz). All **34** actual native-binding, **13** forbidden-regex, and **10** cross-engine controls pass.

Its [first actual full-campaign attempt](../candidates/evidence/rust-v8-zig-stage-06-sealed-campaign-failure.json) fails closed in `extended-cpython-paths`. The frozen reporting process attempts to serialize a genuine Python `Pattern` object and raises `TypeError`; the completed-step denominator therefore remains **NOT CAPTURED**. A separate [exact frozen-suite diagnostic](../candidates/evidence/rust-v8-zig-stage-06-extended-path-first-mismatch.json) retains the unchanged suite's original comparisons and reports the first genuine mismatch: Python compiles `(?:ab){4294967294}`, while the Zig engine incorrectly raises `PatternError`. The complete process traceback, original and diagnostic output, exact commands, actual source and native hashes, and unchanged matching and object proofs are preserved. No successful campaign report is invented, no frozen test is silently weakened, and Zig is **NOT** called fully qualified. Final speed remains **NOT MEASURED** and no final benchmark is opened.

## Compact independently compiled Zig repetitions

The owned Zig compiler now represents long fixed-width repeated motifs without allocating billions of instructions. Three incremental controls reveal genuine [zero-repeat](../candidates/evidence/rust-v8-zig-stage-07-repeat-motif-controls-attempt-01-failure.json), [optional-repeat and inverted-window](../candidates/evidence/rust-v8-zig-stage-07-repeat-motif-controls-attempt-02-failure.json), and [overflow](../candidates/evidence/rust-v8-zig-stage-07-repeat-motif-controls-attempt-03-failure.json) failures; none are discarded. The final [39,512-case targeted comparison](../candidates/evidence/rust-v8-zig-stage-07-repeat-motif-controls.json) and all frozen matching, grammar, object, tracing, and replacement checks pass.

The [first complete campaign](../candidates/evidence/rust-v8-zig-stage-07-sealed-campaign-failure.json) fails closed at the all-family native-code audit. After all four actual engine mappings are independently verified and frozen, the [next single complete attempt](../candidates/evidence/rust-v8-zig-stage-07-sealed-campaign-attempt-02-failure.json) exposes **308 actual differences in 72,248** unchanged extended compatibility checks. Its child does not emit individual mismatch records; none are invented. Generated evidence, including its original final newlines, is preserved byte-for-byte so that every recorded hash remains valid. [The complete Zig report](../candidates/evidence/ZIG-STAGE-07-COMPATIBILITY.md) retains every run and explicitly reports **NOT QUALIFIED** and **NOT MEASURED**.

## Recover every extended-suite failure without changing Python's tests

The [additive extended-path diagnostic](../tools/rust_v8_extended_paths_diagnostic.py) runs the exact original **72,248** frozen cases, original seed, case order, and equality rules. Its only reporting change structurally represents successfully compiled Python and candidate pattern objects the same way, allowing existing compiler-error differences to be saved without the original JSON serialization failure. [Two independent Python reference processes](../candidates/evidence/rust-v8-extended-path-diagnostic-self-test.json) both pass **72,248/72,248** and all diagnostic-poison controls.

The complete [Zig result](../candidates/evidence/rust-v8-zig-stage-07-extended-path-failures.json.gz) retains all **308** actual mismatch rows: **224** from frozen manual patterns and **84** from seeded patterns. The first actual failure is case-insensitive Unicode `İ` against `i`; every operation and failure remains inspectable. The corresponding [C diagnostic](../candidates/evidence/rust-v8-vm-stage-11-lossless-extended-path-diagnostic-interrupted.json) correctly records **INCONCLUSIVE** because its isolated worker had no timeout and was interrupted without publishing a result. No hidden test, timing, source change, invented C denominator, or passing C result is claimed.

## Independent Python engine and fail-closed provenance

The independently implemented Python parser, compiler, and matching engine reduce **52,151** original matching failures to **zero**. The first repaired implementation passes every frozen matching and parser case, but an independent source audit correctly rejects its `sys` import: that module could expose Python's module registry even though this candidate used it only for platform sizing. The [first complete edge result](../candidates/evidence/rust-v8-edge-oracle-ast-corrected-v1.json.gz), [grammar result](../candidates/evidence/rust-v7-grammar-ast-v8-corrected-v1.json.gz), and [129-failure deeper result](../candidates/audits/RUST-V8-DEEP-CONTRACT-AST-CORRECTED-V1.json.gz) remain preserved; the rejected source is not represented as provenance-qualified.

The corrected independent implementation derives platform pointer width from `struct.calcsize('n')`, removes `sys`, and passes the full guarded source, owned parser and executor, isolated-process mapping, and all **76** anti-delegation controls. Its [version-two frozen matching evidence](../candidates/evidence/rust-v8-edge-oracle-ast-corrected-v2.json.gz) passes **223,198/223,198**; its [independent grammar evidence](../candidates/evidence/rust-v7-grammar-ast-v8-corrected-v2.json.gz) passes **20,480/20,480**. The stronger [complete version-two evidence](../candidates/audits/RUST-V8-DEEP-CONTRACT-AST-CORRECTED-V2.json.gz) preserves all **129** real remaining differences: **53** scanner-copy cases, **40** method cases, **11** callback cases, **nine** buffer cases, **seven** hostile group-conversion cases, **six** lifetime cases, and **three** object cases. Python agrees with itself, all **24** regex and cross-engine import guards pass, and no fallback is allowed. Speed remains **NOT MEASURED**.

The next independent Python stage fixes callback `None` values and nested exceptions, preserves arbitrary user-defined group-converter errors, correctly releases and retains real Python buffers, uses a genuine callable iterator, and reports the correct public pattern module. Its [complete matching result](../candidates/evidence/rust-v8-edge-oracle-ast-deep-stage-01.json.gz) remains **223,198/223,198**, and its [standalone grammar](../candidates/evidence/rust-v7-grammar-ast-deep-stage-01.json.gz) remains **20,480/20,480**. The [fully preserved deeper result](../candidates/audits/RUST-V8-DEEP-CONTRACT-AST-STAGE-01.json.gz) improves from **129** to **93** genuine failures, eliminating every callback, group-converter, and buffer mismatch. The remaining differences require genuine native Python object behavior; Python functions are not misrepresented as built-in methods.

## Reproducible four-engine compatibility chart

The [headline compatibility chart](../candidates/evidence/rust-v8-correctness-progress.svg) compares each of the **four** original engines with its independently corrected version using the exact same **223,198** frozen cases. It shows every original failure—**24,462** Rust, **5,281** Zig, **52,655** C, and **52,151** Python—and all four verified zero-failure matching results. Its [deterministic generator](../tools/rust_v8_correctness_progress.py) verifies each candidate, Python baseline, all **49** categories, complete failure arrays, frozen seeds, source and native hashes, and the two embedded independent oracles. A bounded streaming parser verifies the complete large original failure reports without dropping cases or inventing answers. All **40** changed-denominator, hidden-failure, fake-zero, stale-artifact, and held-out-data poison controls pass. The graph explicitly measures matching compatibility only; it neither claims passing results on the stronger **393-case** test nor measures performance.

## Native Rust match expansion and correct replacement errors

The original 39,000-case direct replacement matrix exposes **480** genuine Rust failures: invalid `list` replacements in `sub` and `subn` produce a made-up decoding error instead of Python's actual unhashable-list error. Its [complete first run](../candidates/evidence/rust-v8-rust-native-expand-direct-replacement-controls-failures.json) also preserves **504** independent public-prototype failures; neither engine's losses are removed. The Rust bridge already contains a genuine native replacement parser and output writer. Its new match-expansion path reuses that owned implementation, safely rejects incompatible subclasses and buffers, validates mutable capture bounds, and preserves Python's real replacement-hash errors.

The [repaired direct matrix](../candidates/evidence/rust-v8-rust-native-expand-direct-replacement-controls-repaired.json) passes **13,000/13,000 Rust cases** and retains all **504** public-prototype differences. Fresh independent frozen proofs pass [all 8,862 replacements](../candidates/evidence/rust-v8-replacement-rust-native-expand-cache.json.gz), [all 11,266 deeper replacements](../candidates/evidence/rust-v8-replacement-rust-native-expand-cache-deep.json.gz), [all 223,198 matching cases](../candidates/evidence/rust-v7-edge-oracle-rust-native-expand-cache.json.gz), [all 393 object cases](../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-NATIVE-EXPAND-CACHE.json.gz), [all 479 tracing cases](../candidates/evidence/rust-v8-observability-rust-qualified-native-expand-cache.json.gz), and the [entire actual 22-stage campaign](../candidates/evidence/rust-v8-rust-native-expand-cache-sealed-campaign.json), including **4,494,555** Unicode comparisons and the official Python tests.

The isolated, fully correctness-gated [624-case practice experiment](../performance/v7/evidence/RUST-NATIVE-EXPAND-CACHE.md) measures **0.9705×** Python, with **0.9376–1.0066×** confidence, **212** individually faster cases, and all **230** substantial slowdowns retained. Match-object operations improve descriptively from **0.3451×** to **0.6192×**; the two separate practice sessions are not claimed to be directly paired. The [independent 39-control integrity audit](../performance/v7/evidence/rust-v7-calibration-native-expand-cache-integrity.json) verifies all **8,736** timing rows, **26,208** correctness checks, **625** confidence intervals, actual native mappings, and all preserved baseline regressions. Final performance remains **NOT MEASURED**.

## Checked direct access to native Rust pattern data

The Rust bridge now validates exact compiled-pattern types, version tags, member descriptors, and object offsets before directly reading pattern data; subclasses, changed object layouts, deleted attributes, and unsupported interpreter modes retain ordinary Python attribute lookup. It stores no pattern, matching answer, or native handle and continues to use the independently written Rust engine. Its [complete direct replacement comparison](../candidates/evidence/rust-v8-rust-native-slot-fastpath-direct-replacement-controls.json) passes all **13,000** Rust cases while preserving all **504** unrelated prototype failures. The exact source and native binaries separately pass [all 8,862 standard replacements](../candidates/evidence/rust-v8-replacement-rust-native-slot-fastpath.json.gz), [all 11,266 deeper replacements](../candidates/evidence/rust-v8-replacement-rust-native-slot-fastpath-deep.json.gz), [all 223,198 matching checks](../candidates/evidence/rust-v7-edge-oracle-rust-native-slot-fastpath.json.gz), [all 393 object checks](../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-NATIVE-SLOT-FASTPATH.json.gz), [all 479 tracing checks](../candidates/evidence/rust-v8-observability-rust-qualified-native-slot-fastpath.json.gz), and the [full 22-stage correctness campaign](../candidates/evidence/rust-v8-rust-native-slot-fastpath-sealed-campaign.json).

The independently correctness-gated [624-case practice experiment](../performance/v7/evidence/RUST-NATIVE-SLOT-FASTPATH.md) records **1.0171×** relative to Python, a **0.9822–1.0540×** confidence interval, **237** clearly faster cases, and all **172** substantial slowdowns. All **8,736** raw observations, **26,208** timed correctness checks, **625** recalculated confidence intervals, and **39** rejected data and native-code corruptions appear in the [independent practice audit](../performance/v7/evidence/rust-v7-calibration-native-slot-fastpath-integrity.json). The confidence interval includes **1×**; the separate design runs are not directly paired, and this is not a proved overall speedup or a final result. Graphs retain all five Rust designs and every loss. Final benchmark and performance: **NOT CREATED / NOT MEASURED**.

## Rejected Python cache-eviction hypothesis

An [additional experimental cache checker](../tools/rust_v9_cache_reentrancy_oracle.py) tests whether evicting a pattern can call a user-defined hash function and recursively disturb compilation. Its [first](../candidates/evidence/rust-v9-cache-reentrancy-self-test-failure.json) and [second](../candidates/evidence/rust-v9-cache-reentrancy-self-test-stage-two-failure.json) self-tests reject incorrect assumptions about Python's actual cache. In the [complete third and final result](../candidates/evidence/rust-v9-cache-reentrancy-self-test-stage-three-failure.json), two independently isolated Python 3.14.6 references agree that neither cache eviction hashes the evicted object. The hypothesized behavior is therefore false, not a missing Rust feature. The checker is **not** a passing correctness gate: candidate and engine-independence checks were **NOT RUN**, all three real failures remain preserved, and no implementation or final benchmark was changed.

## Direct calls into the independently written Rust matcher

The Rust bridge now sends valid positional `search`, `match`, and `fullmatch` calls directly to its owned matching engine without constructing and reparsing an intermediate Python argument list. All checked object types, attribute versions, native-handle errors, unusual windows, keyword arguments, subclasses, captures, and fallback paths remain protected. An [initial frozen-campaign audit failure](../candidates/evidence/rust-v8-rust-native-direct-dispatch-sealed-campaign-failure.json) records concurrent native-library changes honestly; after freezing the independently verified four families, the [complete unmodified campaign](../candidates/evidence/rust-v8-rust-native-direct-dispatch-sealed-campaign.json) passes **22/22** stages, including **4,494,555** full-Unicode checks. Independent matching, object, tracing, and replacement proofs are linked from the [complete direct-dispatch report](../performance/v7/evidence/RUST-NATIVE-DIRECT-DISPATCH.md).

The [first practice-command preflight](../performance/v7/evidence/rust-v7-calibration-native-direct-dispatch-preflight-failure.json) correctly rejects omission of Python as the first paired baseline before any timing occurs. The unchanged corrected practice run measures **1.0257×** against Python, **0.9916–1.0635×** confidence, **241/624** individually faster cases, and all **155/624** substantial slowdowns. Its [independent 39-control audit](../performance/v7/evidence/rust-v7-calibration-native-direct-dispatch-integrity.json) verifies all **8,736** raw rows, **26,208** correctness checks, **625** confidence intervals, and exact loaded native code. The confidence interval still includes **1×**; no overall statistical victory, final result, or direct paired comparison between architectures is claimed.

## Prove and skip impossible Rust searches

Analysis of the frozen practice results shows that **23** expensive match-related cases do not produce or inspect a match; they repeatedly run the engine on a provably impossible search. The Rust compiler now recognizes a strictly mandatory repeated single-character prefix followed by an exact character in its own bytecode. Before ruling out a search, it checks every required character with the original Unicode-aware Rust matching logic and respects input type, captures, search windows, case flags, branches, assertions, and anchors. Any potentially matching input still runs the original engine unchanged.

All [30,800 focused comparisons](../candidates/evidence/rust-v8-rust-mandatory-prefix-filter-focused-controls.json), all frozen matching, replacement, object, native-binding, and anti-delegation tests pass. The [complete frozen campaign](../candidates/evidence/rust-v8-rust-mandatory-prefix-filter-sealed-campaign.json) independently passes **22/22** stages, **72,248** extended comparisons, and **4,494,555** full-Unicode comparisons. The separate [624-case practice report](../performance/v7/evidence/RUST-MANDATORY-PREFIX-FILTER.md) records **1.1094×** relative to Python, **1.0666–1.1536×** confidence, **246** clearly faster cases, and all **142** substantial slowdowns. Match-related operations measure **2.1401×**, with **5/48** substantial slowdowns. Every confidence interval, raw row, and native-library hash passes the [independent 39-control result audit](../performance/v7/evidence/rust-v7-calibration-mandatory-prefix-filter-integrity.json). This is a statistically supported **practice-only** improvement, not a hidden-test result or a **1.5×** claim. The additional per-pattern compiled search allocation is disclosed.

## A genuinely hidden 24,576-case final speed protocol

An independent public-only review found that the preserved 12,288-case protocol allowed a secret marker to change without sufficiently changing actual matching semantics. It also included result normalization inside timed operations and did not consistently reuse genuinely precompiled patterns. The original protocol and opening remain unchanged and unused; neither is silently presented as a valid final result.

The new [prospective 24,576-case protocol](../performance/v9/HOLDOUT-PROTOCOL.md) fixes **12** public APIs, **eight** workload families, and **256** genuinely secret-dependent cases per family. The unknown opening changes the real pattern, subject, Unicode, capture, flags, replacement, and search window. Each of **31** paired rounds measures exactly **16** real public operations; setup, result conversion, and correctness comparisons occur outside the timer. The four-engine baseline and three-candidate comparison requires exactly **3,047,424** timing observations and **9,142,272** correctness checks. Its seeded confidence calculation uses **9,999** full-case bootstrap draws, preserves all losses, and requires at least **14,746** independently faster cases.

The [complete prospective public self-test](../performance/v9/evidence/HOLDOUT-PUBLIC-SYNTHETIC-SELF-TEST.json) preserves its one actual synthetic-only execution: **75** passing checks, **70** rejected adverse inputs, no imported candidate, no hidden opening, no generated final cases, and no timing. The final manifest, candidate freeze, secret opening, benchmark rows, scores, and charts are **NOT CREATED** and **NOT MEASURED**. Earlier frozen tests, sources, and results are never altered.

## All-engine from-scratch and native-code audit

The [complete source and native-code auditor](../tools/audit_from_scratch.py) and its [current, reproducible machine-readable result](../candidates/audits/FROM-SCRATCH-AUDIT.json) independently verify all **four** separately built parser, compiler, and matching-engine families after the current Rust direct-dispatch, C group-name, and Zig repetition repairs. Separate guarded processes verify the **one** C library, **two** Rust libraries, and **two** Zig libraries that are actually loaded; their complete native dependencies, exported entry points, exact current source identities, and mapped-file hashes agree. All **76** malicious controls pass, including hidden Python `re` imports, disguised external regex libraries, cross-candidate delegation, stale binaries, misleading loader paths, renamed Cargo dependencies, benchmark detection, and dropped native mappings. Rust's Cargo manifest and lockfile contain **zero** external packages.

The [audit immediately before the latest Rust engine change](../candidates/audits/FROM-SCRATCH-AUDIT-BEFORE-RUST-MANDATORY-PREFIX-FILTER.json) and the [preceding C, Zig, and Rust audit](../candidates/audits/FROM-SCRATCH-AUDIT-BEFORE-C11-ZIG07-RUST-DIRECT-DISPATCH.json) are archived byte-for-byte. An [initial in-memory diagnostic](../candidates/audits/FROM-SCRATCH-IN-MEMORY-DIRECT-DIAGNOSTIC-FAILURE.json) records a real shell-quoting failure and claims no result. The exact unchanged public self-test and normal report command subsequently pass all **76** controls against all current families. The [older pre-repair audit](../candidates/audits/FROM-SCRATCH-AUDIT-BEFORE-FINAL-REPLACEMENT-REPAIRS.json), [original audit](../candidates/audits/FROM-SCRATCH-AUDIT-HISTORICAL-BEFORE-V8-FINAL.json), and [earlier C audit](../candidates/audits/FROM-SCRATCH-AUDIT-BEFORE-C-BINDER-REPAIR.json) remain unchanged.

The audit retains the initially rejected Rust-lifetime lexer, as well as the initial interrupted full-native runs; neither failure is presented as a successful check. The complete audit and its isolated controls subsequently pass through the pinned, reproducible `python -m tools.audit_from_scratch` command. Two earlier, discarded audit attempts displayed historical file names or Git metadata outside their permitted read scope. No held-back case, benchmark content, timing, secret opening, or implementation was read or used by those attempts; both were quarantined and replaced by the independently verified, exact-path audit. No candidate speed is claimed.

## Independent final-graph verification without final data

The [new final chart generator](../tools/performance_v9_charts.py) validates all **24,576** cases for each of the **three** independent replacements and the exact Python baseline before it can render a result. It checks the complete **73,728** candidate rows, **6,144** independently authenticated memory observations, every loss and large regression, all confidence labels, the exact **31** paired rounds and **16** operations, and all **9,999** bootstrap draws and **14,746** required significant wins. Python-traced allocation, whole-process memory, and unmeasured native allocation are never mislabeled.

The [first synthetic self-test](../performance/v9/evidence/PERFORMANCE-CHARTS-PUBLIC-SYNTHETIC-SELF-TEST-FAILURE.json) correctly rejects two corruption checks sharing a name. A single one-line correction makes the controls distinct; the [one preserved retry](../performance/v9/evidence/PERFORMANCE-CHARTS-PUBLIC-SYNTHETIC-SELF-TEST.json) passes all **95** independently named poisoning checks. It starts no processes, reads or writes no files, imports no candidate, and opens no actual cases. Its synthetic charts are held in memory only. Real final graphs and measurements remain **NOT CREATED**.

## Independent final timing and confidence verification

The [final-results replay verifier](../tools/performance_v9_results_audit.py) independently checks the prospective **3,047,424** actual timing observations, all **9,142,272** correctness snapshots, **9,999** seeded confidence draws, all **24,576** results per candidate, every slowdown, the exact four-engine order, and **6,144** separately collected memory observations. Its [one actual public-only self-test](../performance/v9/evidence/PERFORMANCE-RESULTS-AUDIT-PUBLIC-SYNTHETIC-SELF-TEST.json) passes all **93** named corruption controls using only a small, clearly labeled in-memory synthetic test. No candidate, subprocess, final case, opening, previous hidden benchmark, real timing, or real memory data is accessed. The strict **20%** slowdown boundary and every omitted-case and changed-confidence attack are checked. Final results remain **NOT MEASURED**.

## Clear graphs without fabricated measurements

The [larger-test chart generator](../tools/performance_v8_charts.py) prepares **six** readable, accessible graphs for the complete unseen results: overall speed and confidence relative to Python, every faster and slower case, every public operation, every slowdown exceeding **20%**, separately identified Python and process memory, and the complete ranking. Its synthetic-only self-test validates all **96** workload groups, all **12,288** case positions, both exact confidence boundaries, and **43** omitted-case, changed-denominator, stale-binary, and misleading-memory controls. It reads no final case, timing result, candidate, native library, secret seed, or old holdout. The real larger-test graphs and rankings remain **NOT MEASURED** until all replacements pass their correctness gates.

## Independently expanded, blinded final test

The [larger final-test protocol](../performance/v8/HOLDOUT-PROTOCOL.md) freezes **12,288** genuinely distinct unseen cases: **12** public Python operations, **eight** workload families, and **128** separate cases per family. Every matching pattern has its own independently derived identity; mutable-buffer cases materialize real `bytearray` and `memoryview` objects. Python and at least **three** separately written, compatibility-qualified engines receive **four** warmups and **31** counterbalanced paired rounds. The minimum four-engine comparison therefore retains all **1,523,712** timing records and all **4,571,136** before, during, and after correctness checks. Its **768-case** memory comparison uses isolated instrumentation rather than contaminating clean timing workers.

The [canonical commitment](../performance/v8/holdout-manifest.json) preserves the existing **10,312-case** holdout unchanged and publishes only the SHA-256 commitment of a separately generated secret. The final test requires all **223,198** complete compatibility checks, the **393** deeper public-contract cases, and the complete five-library, four-family no-delegation audit before the secret can be opened. Overall confidence uses **9,999** prospectively declared stratified bootstrap samples; the passing rule requires a lower confidence bound of **1.5×**, at least **7,373/12,288** statistically faster cases, and disclosure of every slowdown exceeding **20%**. The [committed synthetic integrity evidence](../performance/v8/evidence/HOLDOUT-PROTOCOL-SELF-TEST.json) never opens the secret, generates an actual test case, imports a candidate, or measures performance. Final results remain **NOT MEASURED**.
