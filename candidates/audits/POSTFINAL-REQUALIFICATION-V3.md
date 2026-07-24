# Fresh checks for the next from-scratch engine experiment

Status: **Prospective safety checks only. No new engine has been changed
or measured.**

The [completed current-engine comparison](../../performance/postfinal-public-v6/RESULTS.md)
binds the exact first rebuilt Rust engine, unchanged C and Zig engines,
all **12** compatibility proofs, **425,984** timing observations, and
**5,940** individually preserved slowdowns. The first Rust architecture
is rejected. Its source-bound correctness and benchmark evidence remain
immutable.

Changing the Rust source or native binary again invalidates the current
version-two audit reports and version-six benchmark for the new engine.
Never overwrite, reuse, or relabel those reports. Prepare three separate
one-use destinations before any next source change:

1. `tools/postfinal_from_scratch_audit_v3.py` must preserve all **76**
   original source, independent-family, external-engine, native-loader,
   and actual memory-mapping checks. It can exclusively create
   `candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V3.json`.
2. `tools/postfinal_no_delegation_audit_v3.py` must verify the exact new
   source audit, all **76** inherited controls, all **32** additional
   production controls, all **five** native roles, and the immutable
   source-bound process bootstrap. It can exclusively create
   `candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V3.json`.
3. `tools/python_re_universal_public_oracle_stage05.py` must preserve all
   **8,192** original public cases, all **48** observations per case,
   the exact previous correctness history, all three independent current
   engines, and all **1,179,648** Python comparisons. It can exclusively
   create `candidates/evidence/python-re-universal-public-oracle-v5-all.json`.

The three new production reports are **NOT CREATED**. No source audit,
worker, production correctness run, benchmark, final case, or entropy is
executed by a candidate-free self-test. Every actual production report
must reject symlinks, existing evidence, wrong schemas, partial reports,
missing native roles, changed source fingerprints, external regex
packages, cross-engine delegation, hidden-test access, and timing.

## Preserve the measured current version

| Unchanged source or verified result | SHA-256 |
| --- | --- |
| Current Rust source | `398773b8542c88cfc55fe13ceac1e84a00155217b76b8461ddf9704d2f6c82c5` |
| Current Rust native engine | `83394c5c3b5d9e9d98c8474aac60ca5a81517dc7ec7c53b3b625e6ed0a04c165` |
| Current from-scratch report | `5e299a767cbd494683100519a6ad461d1a0eb9de1564b1437c7e0229cca7a551` |
| Current no-delegation report | `183cd04f5e1587c181505c09867566b4bd18db270f974475c2b456ff09af1d9f` |
| Current all-engine Python comparison | `facb736a3409f459cdc812e6dc740df399f98ebb84745a22b615ef130ccdb137` |
| Current public workload manifest | `65e024a1a79d13b03e4e5ad0f3d4ae010dbb6e4f09b52a8542837a2ea4c6198a` |
| Current full public speed summary | `539fe6ba0ac492ffab121845da21033676ad7e7154ce9107f7f1778f55ceed4c` |
| Current independently verified replay | `8eb2e6bba6894a71f63e32cc35cca5317bb1beccc32c2905bbeacebedb868fd2` |
| Original native-engine archive manifest | `136a64a89fed1dce245c3774539720beb171c660291d2ca0e1e1b6303115efd6` |

## Repeat only candidate-free controls

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_from_scratch_audit_v3.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_no_delegation_audit_v3.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage05.py --self-test
```

A subsequent Rust experiment must additionally pass all **20** native
release tests, the **223,198**-case matching suite, the **393** Python
object checks, the **479** callback and scanner checks, all **22**
compatibility stages, and all **4,494,555** Unicode comparisons. Its new
public speed protocol must be separately frozen, committed, and pushed
before measuring. The **65,536**-case final test remains **NOT OPENED**.
