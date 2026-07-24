# Fresh checks for the modified Rust engine

Status: **PASS. All three current engines have fresh independence and
Python-compatibility evidence. New Rust performance is NOT MEASURED.**

The published 8,192-case performance comparison belongs only to its exact
original, archived Rust, C, and Zig engines. The newly optimized Rust
engine is a different native binary. The historical performance evidence
remains unchanged and does not measure the new version.

Three additional, independently versioned tools have produced fresh,
exclusively created evidence for the changed Rust engine and the unchanged
C and Zig engines:

1. `tools/postfinal_from_scratch_audit_v2.py` reruns all **76** original
   independence checks, adds **52** safety controls, and verifies the
   current source files and five native libraries. Its passing report is
   `candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json`.
2. `tools/postfinal_no_delegation_audit_v2.py` reruns all **32** extra
   anti-delegation checks against the fresh **76**-check report and the
   actual native libraries. Its passing report is
   `candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V2.json`.
3. `tools/python_re_universal_public_oracle_stage04.py` preserves the
   exact original **8,192** cases and **48** Python behavior checks per
   case. Its passing report is
   `candidates/evidence/python-re-universal-public-oracle-v4-all.json`:
   all three current engines pass **1,179,648** comparisons with zero
   differences and no external regex package.

The source-audit safety test passes all **76** original controls and **52**
new controls. Its real audit verifies four separate source pipelines, three
independent native engine families, and five native binaries. The strict
isolation audit inherits all **76** original controls, passes all **32**
additional production controls, and separately passes **56** in-memory
malicious-input checks. The unchanged-case Python runner passes **66**
candidate-free safety controls.

| Current source or fresh result | SHA-256 |
| --- | --- |
| Modified Rust source | `398773b8542c88cfc55fe13ceac1e84a00155217b76b8461ddf9704d2f6c82c5` |
| Modified Rust native engine | `83394c5c3b5d9e9d98c8474aac60ca5a81517dc7ec7c53b3b625e6ed0a04c165` |
| Unchanged Rust Python bridge | `81fc4c4a92005f0588dd9b811988587d4d421dd8e1102eebcab53f4deb27cd36` |
| Fresh from-scratch report | `5e299a767cbd494683100519a6ad461d1a0eb9de1564b1437c7e0229cca7a551` |
| Fresh no-delegation report | `183cd04f5e1587c181505c09867566b4bd18db270f974475c2b456ff09af1d9f` |
| Fresh all-candidate Python comparison | `facb736a3409f459cdc812e6dc740df399f98ebb84745a22b615ef130ccdb137` |

The complete [new Rust correctness report](../evidence/RUST-POSTFINAL-INLINE-STATE-V1.md)
also records its original matching, Python-object, callback, scanner, and
22-stage Unicode proofs. The modified engine has not been benchmarked or
declared faster. The **65,536**-case final test is **NOT OPENED**.

## Original evidence that must stay unchanged

| Frozen public source or result | SHA-256 |
| --- | --- |
| Original 76-check audit source | `4c47a77cf096df354e59d03096447c56bff890389869c6a75667a36c8471d024` |
| Original 76-check audit result | `c78449b1153221bd0d17854c4f6682062392d19a04cfd0a424a1c6f3fa3478cb` |
| Original 32-check audit source | `e505e17f4849242d990ee8e184794962327335d807000d1a8a0e65a0cb10c0ed` |
| Original 32-check audit result | `c4605c8af5da805c099b1efb7f15e8390781768bb3014276b465a7712b4ed06b` |
| Immutable Python comparison | `744876e5b8409b8d49982ccfb61d93a99f3e2d4fd64d0543b29b831bd26796a0` |
| Passing 8,192-case public result | `a7b6aea6e612de511990d446c8572aa4e1d3094f28ddd2b9f012b1083e73f208` |
| Frozen public benchmark | `c9950c87079ccc1909ba4470ed573b08afe1f275b85a8932cbfe83b547b24f96` |
| Original independently checked measurements | `ff86c9421747373df9f5cf640f8a081331661c7d79e8b12969cb0952c86d9246` |

## Repeat the candidate-free safety checks

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_from_scratch_audit_v2.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_no_delegation_audit_v2.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage04.py --self-test
```

These repeatable commands create no audit, compatibility result, benchmark,
or final test. The existing production evidence is exclusively created and
must not be overwritten. A new public benchmark protocol must be frozen,
committed, and pushed before the modified engine is timed.
