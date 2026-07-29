# Freeze runtime independence without running a candidate

Status: **SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE**.
Runtime non-delegation remains **NOT ESTABLISHED**. No matching engine is
qualified, no speed is measured, and the final comparison remains unopened.

The source is `tools/verify_owned_candidate_runtime_independence_v1.py`,
SHA-256 `c511d72053957aaebeafe23d57c7d5438c72c00307bcbfed167a776666d0baa9`.
Run it using the pinned CPython 3.14.6 with `-I -B -S`. The source imports
neither `re`, `_sre`, `json`, `argparse`, `inspect`, `unittest`, `pathlib`, nor
any candidate. Its bounded, duplicate-rejecting JSON reader preserves clean
startup while authenticating the frozen original contracts.

Freeze the genuine published V73 graph and its exact four source owners,
evidence and history lower bounds **243/248**, all 13 original suite results,
all six original mismatch witnesses, and the separate original **31,237** and
supplemental **8,244** cases. Preserve the actual Rust failure **1,440/14,853**,
C failure **1,230/7,325**, and Zig failure **1,764/3,711**. The from-scratch
V19 Rust build and C build pass **28** and **14** build checks respectively;
neither fact is a passing replacement.

The guard installs both a real, irreversible `sys.addaudithook` and a
deny-first `sys.meta_path` finder before any candidate import. It denies
Python's built-in `_sre`, private standard-library regex compilers and
parsers, third-party regex packages, another candidate, unapproved native
loaders, arbitrary subprocesses, networking, and an unattested `re` alias.
Only an individually authenticated candidate may eventually be bound as the
exact object `sys.modules['re']`.

The unchanged original upstream suite legitimately needs a data-only
`re._constants.MAXGROUPS` value of **1,073,741,823**. Its one regression
case permits only its own fork; its anchor test permits separately recorded
correctness-clock events. Those are not benchmark measurements. Prepare
locale fixtures in a separate reference process. Every subinterpreter must
install its own guard before imports. Do not block or rewrite original public
tests simply to make an incomplete replacement pass.

The actual V19 root-provenance receipt is
`de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99`;
the actual build receipt is
`27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc`.
The independently captured native root is on device **2049**, not the
repository evidence device **2064**. Do not inspect a compressed archive,
discover a directory, load a native engine, start a matching worker, or
mistake a historical **928/8,965** receipt for the real **1,440/14,853**
latest Rust compatibility result.

Both `--self-test` and `--verify-frozen-context`, repeated under an empty
environment, must physically reject hostile imports, alias substitutions,
unauthorized loaders, subprocesses, cross-family candidates, network events,
and marshalled executable code. A synthetic selected module and the exact
data-only constant are the allowed positive controls. All actual candidate,
compiler, reference, native-root, archive, process, timing, and holdout
effects remain zero.

Passing this source gate proves the guard was frozen and self-tested. It does
**not** prove an actual candidate ran under the guard. A separate explicitly
authorized, correctness-gated candidate run is required before changing
runtime independence from **NOT ESTABLISHED**.
