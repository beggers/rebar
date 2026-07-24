# Fresh checks for future engine changes

Status: **Candidate-free safety checks only. No engine has been changed.**

The published 8,192-case comparison proves correctness and performance only
for the exact Rust, C, and Zig source files and native libraries it records.
Rebuilding even one library invalidates that proof for the new version. The
original evidence must remain unchanged.

Three additional, independently versioned tools make it possible to earn
fresh evidence after a real engine change:

1. `tools/postfinal_from_scratch_audit_v2.py` reruns all **76** original
   independence checks and verifies the current source files and native
   libraries. It can exclusively create
   `candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json`.
2. `tools/postfinal_no_delegation_audit_v2.py` reruns all **32** extra
   anti-delegation checks against the new **76**-check report and the actual
   native libraries. It can exclusively create
   `candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V2.json`.
3. `tools/python_re_universal_public_oracle_stage04.py` preserves the
   exact original **8,192** cases and **48** Python behavior checks per
   case. It can exclusively create
   `candidates/evidence/python-re-universal-public-oracle-v4-all.json`
   after all three current engines pass **1,179,648** comparisons.

The source-audit safety test passes all **76** original controls and **52**
new controls. The isolation audit passes **56** malicious-input checks;
the unchanged-case Python runner passes **66**. All three safety runs use
only in-memory test data, start no candidate worker, and write no report.

None of those three real new evidence files has been created. No current
engine has been modified, recompiled, rebenchmarked, or declared faster.
The **65,536**-case final test is **NOT OPENED**. Future performance is
**NOT MEASURED**.

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

## Run only candidate-free safety checks

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_from_scratch_audit_v2.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_no_delegation_audit_v2.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage04.py --self-test
```

These commands create no audit, compatibility result, benchmark, or final
test. A future actual engine experiment must separately pass the complete
matching, object, callback, buffer, scanner, and Unicode suites before a
new benchmark protocol is frozen, committed, and pushed.
