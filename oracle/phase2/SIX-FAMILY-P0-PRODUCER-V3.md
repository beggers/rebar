# Six-family original Python correctness producer V3

Status: SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED.

## Purpose

Run the exact, previously frozen Python 3.14.6 correctness tests against one
independently implemented replacement. This successor preserves all 13 original
test groups, all 31,237 original cases, their original sources, complete seeds,
expected records, and exactly 13 explicitly named private waivers. It adds no
test, waiver, guessed result, external regular-expression package, or fallback.

The implementation is an exact, auditable descendant of the already frozen V1
producer. Its subinterpreters import and authenticate the V3 producer itself,
not V1. The original CPython-suite evaluator remains independently pinned at
`8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce`.

## Independently owned native implementations

The six original families are C, Rust, Zig, C++, Go, and Fortran. Their 25
disjoint first-party source owners and original adapter, native-engine, and
Python-extension owners are unchanged. No candidate may delegate matching to
Python `re`, `_sre`, another candidate, or an external package.

For C, Rust, and Zig, V3 first uses the unchanged frozen original upstream
candidate authenticator, then requires exact agreement with its independently
authenticated source, native device, inode, byte count, and SHA-256. C must
additionally prove that `Pattern` directly derives from the exact native
bridge's `Pattern`, that `Match` is the exact native bridge's `Match`,
and that both public types have the Python-compatible module name `re`.

C++, Go, and Fortran retain their genuine adapter-owned public classes and
their exact first-party native bridge. The three-family upstream authenticator
is never incorrectly applied to those separate implementations. Go retains
its real `__new__` and `_create` construction policy.

Every required native function must be a genuine built-in bound to the exact
authenticated extension module:

- C: `build`, `match`, `collect`, `configure`, `pattern_type`,
  `escape`, and `check_recursion`. Public `compile` belongs to the Python
  adapter; the native C bridge is not required to export it.
- Rust: `compile`, `pattern_type`, `pattern_descriptors`, `run`, and
  `collect`.
- Zig: `compile`, `initialize_pattern`, `free`, and `collect`.
- C++ and Fortran: `compile`, `subject`, and `run`.
- Go: `compile` and `execute`.

## The original saved public-type references

The unchanged public-type group has 6,912 cases. Its exact frozen recorder is
`ee3e6fc00991758fee93b710a63dad9094f881f1ea57777cae2415397f752eae`.
The already published baseline archive is
`8956c0b26e074d1537a47047062fb51e11d3f0196dc97ce4a6e24d2ae45128e2`;
its publication receipt is
`6a8ce4334d0b605483e0f78a909f620a8bcdd0e5ad8cdb4fae4960fc237132fd`.
The signed uncompressed report is
`64ff0810882fd1cc0ba343de127145ae4051ab78e07a0d76f8be21cdfd7f6174`
and contains exactly 55,903,155 bytes.

The original recorder must authenticate the real receipt and stream-decode the
original archive through `authenticate_baseline_receipt` and
`stream_baseline_archive`, which itself calls
`validate_archived_baseline` and `validate_public_baseline_result`.
Both signed original reference processes, PIDs 82 and 83, must retain their
full separately authenticated output. Both 6,912-record vectors must equal
the original
`0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21`.
The recorder's supported C owner supplies only baseline authentication; it
never chooses or imports the candidate being evaluated. No reference process
is rerun.

## Preserve the real failed history

Read-only verification independently reproduces the already published V21
history renderer and verifies its exact four owner digests:

- source:
  `617a64691bf9da7730e44bfed96fe20dbd9c8e38b575e0daf8a3432dbf2625e9`;
- inputs:
  `704b2e07e32260ac741b0a914e2ae04a3deb583de317ba170432f85126af5139`;
- summary:
  `d2143b09bbf35a7a83977c08a35f6a0c87435a50e478df517099aa719e8fa28c`;
- chart:
  `ba7b82d7552603eb836a0c18e47546390c4e1398bbb74951616e309135b9ce5c`.

It retains all 103 actual evidence owners, all 108 signed reference paths, all
30 genuine repaired-C campaign owners, all 13 recorded infrastructure failures,
and the unchanged 12 ownership / 1 saved-reference failure split. Historical
matching results, compiler processes, activation recovery, native-owner
restoration, and failures are never discarded or counted as new successes.

## Verification boundary

Synthetic self-tests use only in-memory data. A physical boundary blocks file
operations, imports, native loading, processes, interpreters, threads, network,
clocks, temporary files, and candidate execution. Frozen-context verification
is read-only and independently authenticates the exact source, this protocol,
the canonical machine contract, V1, the original oracle, public-reference
recorder, signed baseline, V5 activator, V8 source build, and V21 history.

Use the pinned, isolated CPython with `-I -B`. Execute one synthetic
`--self-test` and one `--verify-frozen-context` with the exact three caller
source pins, then repeat both under
`env -i PATH=/usr/bin:/bin`. Canonical contract emission writes only to
standard output; the contract is independently added without overwriting an
existing file.

At source freeze, candidate and reference workers started: 0; candidates
qualified: 0; speed: NOT MEASURED; memory: NOT MEASURED; clocks sampled: 0;
holdout: NOT OPENED; winner: NOT SELECTED.
