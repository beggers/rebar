# First from-scratch Rust matching-state optimization

Status: **Correctness PASS. Performance NOT MEASURED.**

The Rust engine owns its parser, compiler, matching executor, and Python
bridge. This experiment changes only the owned executor in
[`candidates/rust/src/lib.rs`](../rust/src/lib.rs). It does not wrap or
call Python's regex engine, C, Zig, another regex package, or another
candidate.

Each match now keeps up to **eight** recursion guards and repeat states in
local stack arrays. Patterns needing more than eight retain the original
heap-backed behavior. Every nested matching call receives separate local
state. The Rust compiler, public Python contract, C interface, Python
bridge, third-party dependencies, and C and Zig engines are unchanged.

Avoiding small heap allocations is a hypothesis, not a measured result.
The modified Rust engine's speed and memory remain **NOT MEASURED**. The
65,536-case final test is **NOT OPENED**. There is no winner.

## Build the owned engine

The engine compiles without fetching a dependency:

```sh
cargo build \
  --manifest-path candidates/rust/Cargo.toml \
  --release --locked --offline \
  --target-dir /tmp/rebar-rust-inline-guard-repeat-v1

cargo test \
  --manifest-path candidates/rust/Cargo.toml \
  --release --locked --offline \
  --target-dir /tmp/rebar-rust-inline-guard-repeat-v1
```

The release build passes without warnings. All **20** owned Rust release
tests pass; no test is ignored or measured.

| Current source or native role | SHA-256 |
| --- | --- |
| Modified Rust source | `398773b8542c88cfc55fe13ceac1e84a00155217b76b8461ddf9704d2f6c82c5` |
| Modified Rust engine | `83394c5c3b5d9e9d98c8474aac60ca5a81517dc7ec7c53b3b625e6ed0a04c165` |
| Unchanged Rust Python bridge | `81fc4c4a92005f0588dd9b811988587d4d421dd8e1102eebcab53f4deb27cd36` |
| Original archived Rust engine | `c6c09ae96e3a840dc7a62870b3f8c54f6ebc4d82537b319f77520175e84a3255` |

The [independently verified original native archive](../../performance/postfinal-public-v5/NATIVE-ARCHIVE-V1.md)
preserves the complete original Rust engine and four other benchmarked
native roles. The [original 8,192-case speed comparison](../../performance/postfinal-public-v5/RESULTS.md)
measures that archived original Rust engine, not the modified engine.

## Recheck every current candidate

The fresh [from-scratch audit](../audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json)
passes all **76** inherited independence controls and **52** new safety
controls. It verifies four independently owned source pipelines, three
native engine families, and all five native binaries.

The fresh [no-delegation audit](../audits/POSTFINAL-NO-DELEGATION-AUDIT-V2.json)
binds the exact source audit, inherits all **76** original controls, and
passes all **32** additional no-delegation controls. The actual loaded
native libraries do not delegate matching to Python's regex engine,
another candidate, or a third-party regex package.

The frozen [all-candidate Python comparison](python-re-universal-public-oracle-v4-all.json)
tests **8,192** public patterns, **48** observations per pattern, and all
three current engines. All **1,179,648** comparisons pass with zero
mismatches, without running a benchmark or accessing the final test.

## Recheck the exact modified Rust binary

| Frozen compatibility check | Result | Evidence |
| --- | ---: | --- |
| Matching, errors, and pattern grammar | 223,198 passed | [edge oracle](rust-v7-edge-oracle-rust-postfinal-inline-state-v1.json.gz) |
| Observable Python-object behavior | 393 passed | [object contract](../audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-INLINE-STATE-V1.json.gz) |
| Callbacks, buffers, and scanners | 479 passed | [observability suite](rust-v8-observability-rust-qualified-postfinal-inline-state-v1.json.gz) |
| Complete source-bound campaign | 22/22 stages passed | [22-stage campaign](rust-v8-rust-postfinal-inline-state-v1-sealed-campaign.json) |
| Full Unicode stage | 4,494,555 passed | [Unicode stage within the campaign](rust-v8-rust-postfinal-inline-state-v1-sealed-campaign.json) |

Every report authenticates the same modified Rust source, the same new
engine, and the original unchanged Python bridge. No unexplained
correctness failure, crash, delegated match, external regex package, or
holdout access occurred.

## Preserve failed checks

The first `cargo fmt -- --check` found pre-existing formatting differences
in unrelated original Rust lines. No formatting change was applied. The
offline release build itself passed without warnings.

The first observability invocation correctly rejected an output filename
without its required `rust-v8-observability-rust-qualified` prefix before
creating a report. Rerunning the unchanged test with the required prefix
produced the passing **479**-check evidence linked above.

Neither incident changes a frozen test or justifies a compatibility
waiver. New performance is **NOT MEASURED**.
