# Rust: preserve the real Zig build before building twice

This is a source freeze. It does not run Rust, test a candidate, time a
regular expression, or open the final holdout.

The previous Rust build plan was correct for its version-23 snapshot but can
still return 135 evidence files and 140 references after two new, genuine Zig
evidence files appear. This successor authenticates those two actual files and
states the current complete totals: 137 evidence owners and 142 signed
references.

## The evidence that remains unchanged

CPython 3.14.6 remains the reference. All 13 original groups, 31,237 counted
checks, and 13 explicitly named private exclusions remain frozen.

The signed version-23 graph and all its original evidence remain unchanged.
Its 30 real C evidence files show 13 actual workers, 7,325 passing checks,
1,262 mismatches, and zero infrastructure failures. The original C library was
restored. Rust's original 2,042 failures and 7,461 passing checks also remain
visible. Neither implementation qualifies.

The two new Zig files contain a genuinely successful source build, not a
passing correctness test. Their complete, bounded 300,582-byte report and
durable receipt record 26 real build and inspection processes. They show two
separate private phases, two first-party source repairs, and byte-identical
engine and bridge files with different real file identities. There is no
external, Python, or borrowed regular-expression engine. Zig matching,
speed, and memory are NOT MEASURED.

The independently published version-24 renderer, inputs, summary, and chart
are also separately pinned. Their exact current snapshot is validated and
their complete chart is reproduced. The current graph, all three original
Zig build-source owners, and both real Zig result owners must agree on the
same genuine build. No draft or future graph is inspected.

Evidence totals are exact: 135 prior owners plus two actual Zig files equals
137. The 140 prior signed references plus those same two files equals 142.
Equivalently, 138 prior signed evidence paths, the two Zig paths, and two
independently authenticated graph owners produce 142 verified references.
The two counting categories are always identified; neither denominator is
silently changed.

## Preserve the independently reviewed Rust build

Reuse the immutable, separately published Rust V10 implementation. Do not
rewrite its two reviewed source repairs, native checks, Cargo policy, or
28-process real build.

The future private root still begins with:

    /tmp/rebar-phase2-native-build-v9-rust-

The spelling is required because the independently frozen bridge repair
accepts only that exact safe prefix. Both reference-a and reference-b must
be genuine distinct owner-only 0700 phase directories before either repair.

In each phase, copy exactly seven original Rust sources while leaving both
repair destinations absent. Apply the already frozen bridge repair and Python
public-interface repair exactly once using exclusive, no-follow, 0600
creation. Independently verify both complete outputs:

    bridge 4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257
    public 81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c

Cargo contains one local first-party package and zero outside dependencies.
A later explicit build must remain locked, frozen, offline, and separately
pinned. Its 28 real compiler and native-inspection processes must happen only
after explicit build authorization. A successful source build is not proof
that the replacement passes the original Python test suite.

Both normal and minimal-environment source-only self-tests and read-only
context tests are required. They do not start a compiler, apply a source
repair, run a candidate, use the network, access an unreleased graph, measure
time, inspect the holdout, or choose a winner.
