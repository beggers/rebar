# Current rebuilt Rust engine: verified assertion snapshot

This snapshot describes only the newly rebuilt, from-scratch Rust
engine. Historical timing results do not apply to this engine.

## Exact source and native code

| Current file | SHA-256 |
| --- | --- |
| `candidates/rust/src/lib.rs` | `94de5c9ea872bb3649a24a49e99abf5f4e4acd42cfd6d2695f7d17d101f6b888` |
| `candidates/_rust_engine.so` | `1d0851d461fcb4caf4873a4c6fb30c1fd133dfb2140b0602622b9d06e9c1f0d1` |
| `candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so` | `81fc4c4a92005f0588dd9b811988587d4d421dd8e1102eebcab53f4deb27cd36` |

The Rust engine contains its own parser, compiler, instructions, search
executor, Unicode tables, and inline working stacks. The existing
Python-to-Rust bridge is unchanged. The current Rust source passed
**33** native tests.

## Completed independent checks

The current source controller is
`tools/postfinal_from_scratch_audit_v3.py`, SHA-256
`d8230d1f0272bffc6ef2fb61136935047a4d4008afd8a66291c87c48b7a36767`.
Its completed `PASS` report is
`candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V3.json`, SHA-256
`f1a1f2402819d85d0d9135b0fc2b89aecd2212bb3259700bf7628cb881a32f05`.

The current independence controller is
`tools/postfinal_no_delegation_audit_v3.py`, SHA-256
`80d2450439893e1d6e1e2d1986cc59cc7da20e4d4c871f6670b31587da0f24f5`.
Its completed `PASS` report is
`candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V3.json`, SHA-256
`51f745b0cf4a1a91457d865b8fac26b71534f801ca6632b2fd762bd6933c6ab5`.

Together, the completed reports verify:

- **76** original synthetic malicious-input checks, passed in a fresh
  isolated pinned Python process.
- **52** inherited version-two synthetic audit checks.
- **129** current version-three synthetic audit checks.
- **32** actual independence and no-delegation checks.
- **Four** independently verified source pipelines.
- **Three** distinct native-engine families.
- **Five** native-library roles, with actual isolated-process memory
  mappings bound to the exact audited native binaries.

Synthetic audit controls test the auditing safeguards. They are not
public matching cases, benchmark observations, or memory measurements.

| Actual current-engine check | Result | Exact evidence | Evidence SHA-256 |
| --- | --- | --- | --- |
| Rust native tests | **33 passed** | Current Rust source and native binary above | Source and binary hashes above |
| Public matching edge cases | **223,198 checks; zero mismatches** | `candidates/evidence/rust-v7-edge-oracle-rust-postfinal-assertion-snapshot-v1.json.gz` | `f4bbacc480b284685e8b6fb0dfff656f323605dd5efbc3331c0b5e26ea3c03d7` |
| Deep Python-object behaviour | **393 checks; zero mismatches** | `candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-ASSERTION-SNAPSHOT-V1.json.gz` | `88dda18f6498d6cbb078fb89a8dbbfebe4ae357d4d7ca3de795bd9e6a5828e1a` |
| All-engine public comparison | **8,192 cases × 48 observations × 3 candidates; 1,179,648 comparisons; zero mismatches** | `candidates/evidence/python-re-universal-public-oracle-v5-all.json` | `d5b06b914d63f1b89cfd78c2f72c45f432755ce6895b6194e8e7d3fee9c0c2ca` |
| Callback and scanner behaviour | **479 candidate checks and 479 self-oracle checks; zero failures** | `candidates/evidence/rust-v8-observability-rust-qualified-postfinal-assertion-snapshot-v1.json.gz` | `4fb158e17dd36ed7a9ba8b7b54cdf66e87643cc82c7181ba163e961df593936a` |
| Accepted full compatibility campaign | **22 stages passed, including 4,494,555 Unicode observations and 144 official tests** | `candidates/evidence/rust-v8-rust-postfinal-assertion-snapshot-v2-sealed-campaign.json` | `9015b2a02bdf32e1f4dfdb3eb0c8fb8e67d07b78649ccb1ba3ba4da6cd4b76e8` |

## Preserved first-attempt failure

The first attempt to produce the current source audit created no report:
the original-control subprocess exited with signal **9**. Its cause,
including whether it was an out-of-memory kill, is **NOT ESTABLISHED**.
The current controller first fully verifies its immutable predecessor,
releases the predecessor's encoded and decoded report, and collects
unreachable objects before rerunning the unchanged audits. The actual
completed report then independently verifies that all **76** original
controls passed in a fresh isolated child. No candidate, original
control, predecessor, failure, or audit obligation was replaced.

The first full **22**-stage campaign also produced no report. The
historical controller,
`tools/rust_v8_multi_candidate_campaign.py`, SHA-256
`46e53abac0d2347d5fc505aa792a5ee5f55489a6e73b1f57edf37a93a0a6d45d`,
stopped with `AssertionError: complete from-scratch audit failed`
because it still called the older direct audit entry point after the
Rust engine changed. Preserve that failed attempt.

A first additive wrapper genuinely passed all **22** stages using the
actual current version-three audit. Preserve its intermediate report,
`candidates/evidence/rust-v8-rust-postfinal-assertion-snapshot-v1-sealed-campaign.json`,
SHA-256
`9e744de16c6c627715303bcf27ae9ef628b04fcdc078e3ebe9e936204b719db2`.
This first successful report is **not accepted**: its wrapper retained
a latent fallback when the current proof was missing. The actual first
run did not use that fallback, but the controller was not fail-closed.

The accepted controller is
`tools/rust_v8_multi_candidate_campaign_postfinal_v2.py`, SHA-256
`cdabec673a905b122c474a8279b84f194534fda77a0c70555fb9aa9fd299592d`.
It rejects missing or invalid current source-audit proof and passes
**43** new file-free rejection checks, **46** inherited controls, and
the **129** version-three synthetic controls. Its fresh accepted
version-two report passed all **22** actual correctness stages,
including **4,494,555** Unicode observations, **144** official tests,
**223,198** public edge checks, **393** deep checks, and **479** callback
checks. The report is the version-two campaign identified in the table
above. No performance measurements or final cases were used.

## Not yet established

- Rebuilt-engine speed: **NOT MEASURED**.
- Rebuilt-engine memory: **NOT MEASURED**.
- Final cases: **NOT OPENED**.

The historical version-six comparison measured a different Rust source
and native binary. It establishes no speed, memory result, ranking,
speedup, or winner for this rebuilt engine.
