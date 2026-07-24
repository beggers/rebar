# Fair public speed comparison for the updated Rust engine

Status: **FROZEN. Performance NOT MEASURED.**

This comparison will run the unchanged Python **3.14.6** baseline against
three independently written engines: the newly optimized Rust engine and
the previously qualified C and Zig engines. It is a public development
comparison, not the **65,536**-case hidden final test. The final test
remains **NOT OPENED**.

The new comparison was frozen without importing an engine, starting a
worker, taking a timing, or opening the hidden test. Its exact source,
[manifest](manifest.json), and this protocol must be committed and pushed
to `main` before the runner will permit timing. The previous results remain
[historical](../postfinal-public-v5/RESULTS.md); their exact original
native binaries remain [independently archived](../postfinal-public-v5/NATIVE-ARCHIVE-V1.md).
No earlier speed observation may select, weight, or exclude a case.

## Exactly the same balanced public cases

Use all **8,192** previously frozen, equally weighted public cases across
all **260** workload categories. Preserve every original Python operation,
case, pattern, input, lifecycle, quota, and answer. Do not substitute or
remove a case:

| Python operation | Cases |
| --- | ---: |
| `compile` | 210 |
| `escape` | 161 |
| `findall` | 2,040 |
| `finditer` | 2,041 |
| `fullmatch` | 358 |
| `match` | 229 |
| Match-object access | 241 |
| `scanner` | 427 |
| `search` | 1,057 |
| `split` | 451 |
| `sub` | 447 |
| `subn` | 530 |
| Total | 8,192 |

Preserve selection seed `2026072404`, paired-trial order seed
`2026072405`, and confidence-interval seed `2026072406`. Every baseline
and candidate case receives **four** warmups, **13** counterbalanced
paired trials, and **2,000** predeclared confidence resamples.

The selected cases include **355** cold-start calls, **7,210** previously
compiled calls, and **627** module-level calls. They cover four input
representations and all four frozen result densities: **331** empty,
**2,682** single-result, **2,869** few-result, and **2,310** many-result
cases.

A complete run must record all **425,984** raw timing observations,
**1,277,952** checks of exact answers, **24,579** reproducible 95%
confidence intervals, and **65,544** process and native-library integrity
checks. Report every case, all **12** operations, all **260** categories,
and every regression greater than **20%**. No hidden cases are read.

## Requalify the actual current engines before timing

All three engines first pass the
[new Python compatibility comparison](../../candidates/evidence/python-re-universal-public-oracle-v4-all.json):
**1,179,648** comparisons, zero mismatches, and no external regex package.
The fresh
[from-scratch audit](../../candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json)
passes all **76** inherited controls and **52** extra safety checks. The
fresh
[no-delegation audit](../../candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V2.json)
binds all **76** inherited controls, all **32** additional production
controls, all five native binaries, and all three independent engines.

Preserve all **eight** original, still-valid C and Zig compatibility
proofs. Bind the modified Rust engine to its four newly passing reports:

- [223,198-check matching and grammar suite](../../candidates/evidence/rust-v7-edge-oracle-rust-postfinal-inline-state-v1.json.gz).
- [393-check Python-object contract](../../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-INLINE-STATE-V1.json.gz).
- [479-check callback, buffer, and scanner suite](../../candidates/evidence/rust-v8-observability-rust-qualified-postfinal-inline-state-v1.json.gz).
- [22-stage compatibility campaign](../../candidates/evidence/rust-v8-rust-postfinal-inline-state-v1-sealed-campaign.json), including **4,494,555** Unicode checks.

The controller never imports a candidate. Each engine runs in its own
continuously guarded process. Source-bind both the fresh version-two
independence proof and the exact, immutable version-one process bootstrap
it authenticates. Preserve the previous surrogate-safe worker protocol.
Reject any call to Python's regex engine, another candidate, or a
third-party regex package outside the isolated Python baseline.

## Report everything

The headline result is the equally weighted geometric mean compared with
Python. **1×** means Python's speed; larger numbers are faster. Show
individual confidence intervals and report whether each candidate reaches
**1.5×** overall and is statistically faster on at least **60%** of cases.
Publish every slower case without changing the denominator.

Report Python-visible temporary allocations and worker memory separately.
Neither identifies all allocations inside a native engine: exact native
memory remains **NOT MEASURED**. Report process startup, Python/native
boundary, pattern compilation, cached and uncached calls, and other
lifecycle costs according to the original frozen public cases. Never add
controller communication or answer verification to the timed operation.

## Inputs already verified

| Existing input | SHA-256 |
| --- | --- |
| Frozen version-six public manifest | `65e024a1a79d13b03e4e5ad0f3d4ae010dbb6e4f09b52a8542837a2ea4c6198a` |
| Frozen version-six benchmark source | `16a56d1573526894733b6284204ff3712b4d4e2a9c63027d51b8de1869df3fc3` |
| Original public workload manifest | `c9950c87079ccc1909ba4470ed573b08afe1f275b85a8932cbfe83b547b24f96` |
| Original Unicode-safe benchmark source | `f4294a3b5434f43a92970635a958cf3b39db0eb926adef50e242ac0f6b9a1d22` |
| Fresh from-scratch report | `5e299a767cbd494683100519a6ad461d1a0eb9de1564b1437c7e0229cca7a551` |
| Fresh isolation report | `183cd04f5e1587c181505c09867566b4bd18db270f974475c2b456ff09af1d9f` |
| Fresh Python compatibility comparison | `facb736a3409f459cdc812e6dc740df399f98ebb84745a22b615ef130ccdb137` |
| Changed Rust source | `398773b8542c88cfc55fe13ceac1e84a00155217b76b8461ddf9704d2f6c82c5` |
| Changed Rust native engine | `83394c5c3b5d9e9d98c8474aac60ca5a81517dc7ec7c53b3b625e6ed0a04c165` |
| Unchanged Rust Python bridge | `81fc4c4a92005f0588dd9b811988587d4d421dd8e1102eebcab53f4deb27cd36` |
| Immutable guarded-worker bootstrap | `e505e17f4849242d990ee8e184794962327335d807000d1a8a0e65a0cb10c0ed` |

The one-time public freeze must not be repeated. The new speed, memory,
confidence intervals, regressions, and a winner remain **NOT MEASURED**.

Repeat only the candidate-free safety test and the frozen fingerprints:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -I -B -c \
  'import sys;sys.path.insert(0,".");from tools.postfinal_public_practice_v6 import main;main(["--self-test"])'

sha256sum \
  performance/postfinal-public-v6/manifest.json \
  tools/postfinal_public_practice_v6.py
```
