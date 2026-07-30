# Retest the rebuilt, first-party Rust engine against the complete original oracle

Status: **V35 BUILD PASS; CURRENT ORIGINAL CORRECTNESS NOT RUN.**

This experiment retests a newly rebuilt Rust regular-expression implementation
against the same frozen **31,237 original cases in 13 suites** used for earlier
candidates. The current engine, bridge, parser, compiler, and executor are
first-party implementations; wrapping another regular-expression package or
delegating matching to Python's regular-expression engine is forbidden.

## Freeze the exact current first-party build

Build label: `phase2-v35-rust-optimized-safe-source-root-provenance`.

| Owner or artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| Public build receipt | `442fba9a323d527977b3b19b9cb733d81a63d93adf6f4e9f25510f01ae5b4a2e` | 9,669 |
| Public root-provenance receipt | `4cb72c8ae0de6b52b25a38926a4e6c15e047a99b31d5c2a3e7b51d5f4c43fbcf` | 83,616 |
| First-party Rust engine source | `7ec7dc9815bec10c3149123ddc5045f575c3cd45731531bd81e0b888362a9136` | 194,276 |
| Safe first-party native bridge source | `c9b22c4443c36cc6e653af18fcd829561b7987df312368b30dfcbade254538f8` | 182,459 |
| First-party Python adapter | `f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227` | 34,039 |
| Reproduced Rust engine | `06eb2922a11681a70a687ba7b0c5b252e28700689c9fefd347752e1e7c836000` | 674,080 |
| Reproduced safe native bridge | `d8a8b689089d48f4dfe7b27eed7a78dfae92cac8acbd28d32678c1f5466304f6` | 153,152 |

Two fresh build phases observed 28 real offline compiler/ELF-inspector processes
and produced byte-identical binaries. Their four distinct phase-native inodes
are 11680883, 11680886, 11680914, and 11680878. The root receipt records private
root device 2049, inode 11680812, and path
`/tmp/rebar-phase2-native-build-v9-rust-34cndurg`. Source-only modes authenticate
that public receipt but never open, inspect, or stat the private root or native
artifacts.

## Preserve earlier evidence without attributing it to the new engine

Earlier V25 matching failed 1,352 cases: 240 substitution failures, 1,024
capture-ordering failures, 56 trailing-probe failures, and 32 malformed-expansion
failures. An older V30 architecture separately passed 31,237 original cases.

The distinct V33 architecture passed all 31,237 original cases under receipt
`5204823a291ec01890913218582ff978cbe923dd5c787c8d6ae68a9790c43064` and all
10,434 wider public cases spanning 111 API operations under receipt
`8e2343809a8d9226973b1b70ca9d7348f750573caa2729123afb007f02a03bd9`.
Those results authenticate the **historical V33 engine and bridge only**:
`e692633896b61141734d4bb6ddce4a66b2c93bbeaa29b940fcf85904cf6a42e8` and
`ecb19eb814430aeb571f60dd50ba4de4b3f54e7f57f056d2436c41714a257000`.
They do not establish correctness, performance, safety, or independence for V35.

The V33 public speed result, 1.2424347186648022× over Python on 416 public
cases, is historical only. The V35 speed, wider-public correctness, static
source/ELF independence, live non-delegation, and undefined behavior remain
**NOT MEASURED** or **NOT ESTABLISHED**.

## Preserve callback and iterator ownership evidence separately

The safe bridge owns each native engine through one private Python capsule.
Strong leases protect active matching, substitution callbacks, iterators, and
scanners when a callback invokes `match.re.__del__()`. Its independently frozen
source proof covered 32,768 callback-operation sequences, 103,184 callback
finalizations, and 20,656 scanner/iterator lifetime cases without executing the
candidate. Authenticate the applied bridge receipt
`8f3ad6bffcbbb2129a4a95bc12a0b9865b39f08d2c953ba5ce303a4a77743764`.

Synthetic lifetime proof is not actual crash-freedom. Actual adverse callback,
repeated-finalizer, exception, iterator-after-finalization, and
scanner-after-finalization checks must remain separately counted and must never
change the 31,237-case denominator. Candidate crash-freedom and undefined
behavior remain **NOT MEASURED** until real root-authorized candidate execution.

## Original suites, guard, and authority

Keep every immutable original case, all 13 named private waivers, every suite
row, and the 13 independently started candidate workers. The separate 8,244
supplemental and 6,912 corrected-reference cases are never added to the original
denominator. Install the independently pinned strict V4 guard before candidate
import. Historical strict V4 audit failure remains historical; static and live
independence for the exact V35 artifacts are **NOT ESTABLISHED**.

All public modes install a deny-default source wall before reading a predecessor.
The wall rejects candidate sources, native libraries, private roots, compressed
archives, processes, clocks, filesystem mutation, benchmark files, current or
retired proposals, hidden holdout content, and standard-library regex imports.

Run ordinary and sterile `--self-test` and `--verify-frozen-context` gates
under the pinned CPython 3.14.6 interpreter, supplying independently pinned V29
source/protocol/contract, V35 build source/protocol/contract, V35 publication
and root receipt, and strict V4 guard hashes. Only root may run, recover, or
start actual workers, after this exact triple is committed and pushed and root
supplies explicit authorization plus matching full frozen/pushed commit hashes.

The compromised former holdout is **INVALIDATED; REKEYED SUCCESSOR REQUIRED**.
No hidden proposal may be opened, probed, generated, benchmarked, or counted.
No candidate is fully qualified, no winner is selected, and current candidate
correctness, speed, memory, confidence intervals, safety, and crash-freedom
remain **NOT MEASURED** before actual execution.
