# Additional Python `re` compatibility checks

Status: **Frozen design and candidate-free safety checks only.** The
two-Python self-comparison and the independent-engine comparison are
**NOT RUN**. This expansion does not measure performance.

Python 3.14.6 remains the sole behavioral oracle. This stage retains the
original **8,192** public cases, all **48** observations per case, and
all **1,179,648** completed comparisons against the independently
written Rust, C, and Zig implementations. It also retains all **146**
selected, genuinely executed upstream Python tests and their complete,
unskipped Rust, C, and Zig results.

The additional contract has exactly eight disjoint, deterministic public
cohorts. Each case has an explicit cohort, operation, index, and
domain-separated seed. Its expected value is an actual observation of
unmodified Python, not a hardcoded answer.

| Public obligation | Deterministic cases | What is checked |
| --- | ---: | --- |
| Public module and function behavior | 256 | Public exports, call signatures, module-level operations, `RegexFlag`, constants, error attributes, and unchanged positional and keyword behavior. |
| Invalid patterns, warnings, and flags | 256 | Syntax errors, error locations, warning classes and messages, bytes and text flag combinations, inline and scoped flags, and incompatible flags. |
| Real byte-locale behavior | 1,024 | All 256 byte values in genuine ISO-8859-1 and UTF-8 locales, both direct and compiled-before-switch execution, character classes, complements, word boundaries, and case-insensitive matching. |
| Bytes, buffers, and lifetimes | 256 | `bytes`, `bytearray`, contiguous and noncontiguous memory views, released buffers, type errors, match ownership, and deterministic buffer lifetime. |
| Pattern and match object contract | 256 | Group names and indices, spans, mapping views, copies, pickle round trips, equality, deterministic hashes, and weak references. Pickle bytes and private reducer names are not treated as a public promise. |
| Callbacks, replacement, and scanning | 256 | Replacement templates, callable invocation order, nested matching, callback exceptions, empty-match advancement, scanner actions, and scanner remainders. |
| One compiled pattern across threads | 256 | Real groups of four and eight threads share one immutable compiled pattern, synchronize with a barrier, and compare results in deterministic submission order. Locale is never changed in a threaded cohort. |
| Bounded indices, sizes, and Unicode | 1,024 | Out-of-range and index-protocol values, zero-width matches, bounded large inputs, Unicode boundaries and casing, supplementary characters, lone surrogates, and exact exceptions. |
| **Total per isolated engine** | **3,584** | Every case, warning, observable exception, result, and failure remains individually recorded. |

The fixed seed domain is `rebar/python-re/public-contract/v7`; the root
seed is `2026072437`. The eight cohort seeds are separately derived
using SHA-256. The complete canonical matrix SHA-256 is
`0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db`.
Case counts, case identifiers, case ordering, this exact matrix
fingerprint, and all source and native-library fingerprints must be
verified before any production worker is started.

| Cohort | Independent deterministic SHA-256 seed |
| --- | --- |
| Public module and function behavior | `4a2c210dd648de80b11894cfda56b17da2e28af5f811833e1af6ce2573a696df` |
| Invalid patterns, warnings, and flags | `01802b507481a0b1c8930044fb01142aa24ad4f05db75c4cc865eb5dc8c6f67d` |
| Real byte-locale behavior | `d294b817374d7f7ab20c49e2de1e92fd54030d50521e1586e22ad957b4a8ac4d` |
| Bytes, buffers, and lifetimes | `6d0202087a781450aa1c9ff72022daa226df89231833b629db860b94eba60156` |
| Pattern and match object contract | `874be68fefe1c5e58d41043b851ee35f05635ac1c7734fd97a23cd50409fbfec` |
| Callbacks, replacement, and scanning | `794a01eeb09b8ccdd9db84df5fae56e2b156054de47e6186a7239bc3a096c812` |
| One compiled pattern across threads | `e58d42ee61ccdda8718ed1a7387d239bbb3e823b8780c4adbea296e4ed722312` |
| Bounded indices, sizes, and Unicode | `94aa7e389ee247f0e5ddbbd82cd327a3711b956ede51e465fde27a47f3b7a131` |

## Real Python must agree with itself first

`--self-oracle` uses two independently started, isolated instances of
the exact pinned CPython 3.14.6 interpreter. Both independently execute
all **3,584** deterministic cases. Their results must agree in full,
including exception type and arguments, `PatternError` fields, warning
class and message, callback event order, group values, byte values,
buffer errors, and sorted threaded results. A single discrepancy,
crash, skip, timeout, missing case, or changed case identifier prevents
creation of a passing evidence file.

The Python self-comparison creates only the new, exclusive public proof
`oracle/cpython-3.14.6/evidence/public-contract-v7-self-oracle.json`.
It does not run, import, or prepare a candidate.

If the two genuine Python references disagree, no passing proof is
created. Every expected and actual case, warning, exception, cohort,
source fingerprint, and seed is first durably preserved in the distinct,
exclusive failure file
`oracle/cpython-3.14.6/evidence/public-contract-v7-self-oracle-failures.json`.

`--candidate all` is blocked until that exact passing self-comparison
exists. It also requires the current, independently authenticated
version-five source and no-delegation proofs; the real **146 × 4**
official-locale result; and the original current-engine **1,179,648**
comparison. Each candidate then runs in its own isolated, guarded
process. No implementation may load Python's matching engine, an
external matching package, or another candidate.

Only all three independently passing candidate processes can create
`candidates/evidence/python-re-universal-public-oracle-v7-all.json`.
No historical evidence is overwritten. All mismatch values, seeds,
cohort denominators, exception records, and guarded source and native
fingerprints are retained.

A failed Rust, C, or Zig worker never creates the all-candidate passing
report. Its complete baseline and actual results are first durably
preserved in exactly one independently named, exclusive failure file:

```text
candidates/evidence/python-re-universal-public-oracle-v7-rust-failures.json
candidates/evidence/python-re-universal-public-oracle-v7-vm-failures.json
candidates/evidence/python-re-universal-public-oracle-v7-zig-failures.json
```

Failure artifacts retain every mismatching case rather than reporting
only a count. They can never overwrite a passing result or a different
candidate's failures.

An initial direct invocation of the preliminary stage-seven self-test
exited with signal status **137** before producing JSON. No
self-oracle, candidate worker, or evidence file was created. Its cause
is **NOT ESTABLISHED**. The controller now starts the same authenticated
canonical Python module in the original process; it does not start a
subprocess or production worker. The exact direct, unpiped command must
return zero with valid passing JSON before this protocol can be frozen.

## Unchanged upstream exclusions

The only upstream exclusions are the same original six named methods
and two private implementation classes. They cover private constants,
multi-gigabyte resources, a timing assertion, unavailable
multiprocessing infrastructure, a CPython debug-only memory hook,
private debug text, and private compiler internals. Neither genuine
locale test is excluded. No thread, buffer, callback, Unicode, public
object, or public error obligation is waived.

## Reproduce candidate-free checks

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage07.py --self-test
```

Running `--self-test` never starts a production worker, reads or writes
project evidence, imports a candidate, samples a clock, draws entropy,
or measures performance.

After the protocol, source, original current correctness proofs, and
both version-five independence reports are frozen, the **root process
only** may run the two production steps in this exact order:

```sh
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage07.py --self-oracle

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage07.py --candidate all
```

The runner builds its own genuine, private ISO-8859-1 and UTF-8
locales using the pinned original-locale controller. It supplies the
actual private `LOCPATH` only to the isolated worker. Users do not set
or simulate a locale. `PYTHONHASHSEED=0` is independently set for
both Python references and every candidate worker.

These commands are documented but **NOT RUN**. Candidate production is
impossible until the exact, source-bound Python self-oracle has passed.
