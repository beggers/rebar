# Frozen Python `re` candidate protocol V7

This protocol answers one question: does a genuinely independent, built-from-source Python regular-expression implementation behave exactly like pinned CPython 3.14.6 on every frozen original case? A partially passing implementation is not a compatible replacement. Publishing a failure successfully does not make that implementation pass.

This is a correctness protocol. Speed, memory, benchmark results, and the final holdout are **NOT MEASURED**. No winner is selected.

## Frozen original standard

The exact reference is the completed, independently frozen phase-one inventory `oracle/phase1/p0-completeness-v1.json`, SHA-256 `cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f`. The pinned isolated CPython 3.14.6 executable is `/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14`, SHA-256 `255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016`.

All 13 original groups, totaling exactly 31,237 runnable cases, are required:

| Original correctness group | Required cases |
| --- | ---: |
| Original bounded CPython public tests | 151 |
| Public behavior | 864 |
| Scanner behavior | 1,024 |
| Buffer behavior | 768 |
| Managed buffer lifetime | 1,024 |
| Verbose patterns and comments | 2,854 |
| Public types, identity, and serialization | 6,912 |
| Substitution and buffers | 5,120 |
| Shape-changing buffers | 10,240 |
| Complete public API, including real locales | 1,376 |
| Independent Python subinterpreters | 128 |
| Python buffer exporters | 264 |
| Shared patterns across actual threads | 512 |
| **Total** | **31,237** |

The 151 runnable original public cases remain separate from their 152 published records: one genuine upstream debug-only skip remains a skip. All 13 original named private waivers remain unchanged. The machine-readable V7 inventory freezes each original producer, its source hash, exact matrix hash, complete reference-record hash, full-width published seed where applicable, and original candidate recorder. No case, seed, exception, warning, or resource obligation may be silently added, removed, replaced, or counted twice.

## Genuinely independent implementations

The separately frozen six-family independence audit is `tools/audit_candidate_independence_v2.py`, SHA-256 `57168db3df64414a7dc27f1793d9c22b7c493a8b37c025dc57243796e892d93c`; its protocol is SHA-256 `80a1de729c067da36648dcfb9751f7bd3833ff561956df9ad82fc6106a19a16b` and its machine inventory is SHA-256 `89662570a643d94ae1581393ed48015c6fa78d5dbe5ad0419e9a2032e4609659`.

The audit checks six separately owned source families and all 25 exact source owners. It rejects an external regular-expression package, use of Python's `re` or `_sre` as a production engine, shared semantic parsing or execution across candidates, undeclared dependencies, and fallback. A static source audit establishes independence; it does not establish successful source builds, activated matching, complete compatibility, or performance.

V7 freezes **six independently owned source families** and **three genuinely runnable frozen-P0 families**. The complete unchanged original correctness producers presently support only the independently source-built and genuinely activated C, Rust, and Zig candidates. C and Rust require their real version-two builds; Zig requires its real version-three build. Every currently runnable candidate requires the original byte-pinned version-two activator, complete source-build provenance, real promotion intentions, an unchanged independently owned engine and bridge, and durable restoration. No candidate is fully qualified.

The six-family version-four build source and its contract are separately frozen. The independently frozen version-three activation source is `tools/activate_verified_native_candidate_v3.py`, SHA-256 `39a170d5981e3484366eca223c0533366d92927975271fdb004fbce784b7a21e`; its protocol is SHA-256 `17656cd0ea3aa879cc5c69078460118f1e5e977f3e5c8d977c784954ea9f65bf` and its machine inventory is SHA-256 `87d2d34a142f620894b87b35f3216ede4a0374921a3dfacb9d8e209e3d3133fc`.

A V3 activation could qualify as a genuine activation only after proving an actual **passing**, independently reproducible two-phase V4 source build, a passing durable build receipt, the exact V3 report and receipt, every recovery-journal owner and promotion intention, and all live canonical native targets. Freezing the activation source does not perform an activation. The current original CPython, specialist, and subinterpreter producers are independently frozen for C, Rust, and Zig. A future C++, Go, or Fortran correctness request must fail closed until all the unchanged 13-group producer obligations are genuinely implemented for that family. A reproducible source build is **not** a correctness result.

## Preserve the real historical results

V7 freezes and independently verifies **57 actual evidence owners**: 51 historical C, Rust, and Zig candidate archives, publication receipts, and restoration receipts; the two actual C++ version-four source-build owners; the two actual Go version-four source-build-failure owners; and the two actual Fortran version-four reproducibility-failure owners. The V7 machine inventory lists every exact path and SHA-256. A successfully written receipt means only that evidence was preserved.

| Actual historical implementation | Passing groups | Verified passing original cases | Actual behavior mismatches | Fully compatible? |
| --- | ---: | ---: | ---: | --- |
| C | 7 / 13 | 7,197 / 31,237 | 2,094 | No |
| Rust | 8 / 13 | 7,461 / 31,237 | 2,042 | No |
| Zig | 6 / 13 | 3,583 / 31,237 | 1,764 | No |

“Verified passing cases” are cases belonging to a completely passing original group. They are not qualified replacement candidates. The original producers named this quantity `qualified_candidate_case_executions`; V7 preserves that exact historical producer field as `legacy_qualified_candidate_case_executions` and separately reports `verified_passing_case_count`. All three historical candidates failed. **The number of fully qualified candidates is zero.**

The independently verified C++ V4 source-build archive is SHA-256 `48910a6328e8aaacdac993b2c029995d878960a456359a14db5c83b9fc518df9`; its durable receipt is SHA-256 `7742eda3ce777b1378d0c7fb87fc064f222850ca8bcf15cd23ff8a4d87d8bebf`. Its 10 actual compiler and inspection processes produced byte-identical native outputs in two independent fresh phases. **C++ matching cases executed: 0. C++ correctness, activation, and performance: NOT MEASURED.**

The independently verified Go V4 failure archive is SHA-256 `fcf643b7b8e9fbe80bd3b40c7ed884695a844f46e1117f5ebdb130135e5db4bb`; its durable receipt is SHA-256 `215e9680bbe0f8d2250fcca8bae0335017606288e13e7636224b7c76336b5e41`. Four actual compiler and inspection processes ran. The final `build_go_engine` process failed because the Go package's C compilation could not find `Python.h`. No independent Go build phase completed; no generated Go header or candidate activation exists. The Go receipt has `status: PASS` because the failure was durably recorded, but `build_status: FAIL`: the build **failed**.

The independently verified Fortran V4 failure archive is SHA-256 `ba35ea4f0d28814f716a36d2ccb384ef034a88a4029ca3f3cbf4f91eae268103`; its durable receipt is SHA-256 `86b4b2648adf651481eea8d8b427a432f121c59322f508b522eca18af0749a08`. All 18 actual compiler and inspection processes passed, and both independent build phases finished. Both phases produced the same 37,424-byte bridge. However, their 74,624-byte engines had different SHA-256 hashes, `37557a44033a80aa11a81fa145ca76c2bbd44ee544b31974dcf6e59ba0f2949c` and `696126d3f3e7239cac55975f53beb3b5e5cffc6948f08258817b6b2d86422199`. Thus the source-build reproducibility gate **failed**. Its receipt reports `status: PASS` but `build_status: FAIL`; Fortran has not been activated or tested for regular-expression compatibility.

Process totals have explicit boundaries. The three historical V2 builds recorded 39 actual compiler and inspection processes. The V4 C++, Go, and Fortran builds recorded 10, 4, and 18, respectively: **71 V2-plus-V4 processes**. The separately preserved successful V3 Zig source build recorded another 15 processes. Thus the total across V2, V3, and V4 is **86**, not 71. Process identities are required to be unique within each actual run; no claim is made that process IDs are unique across independent runs.

Zig's 1,764 preserved actual mismatches are: 64 scanner cases, 620 verbose-pattern cases, 248 public-type cases, 64 substitution cases, 672 shape-changing-buffer cases, and 96 public-API cases. The original independently run subinterpreter producer additionally made 385 genuine interpreter-case calls, created and destroyed three interpreters, initialized three interpreters, attempted cleanup four times, and recorded three cleanup failures. It did **not** complete the required passing 128-case, 394-call, 11-interpreter lifecycle. Therefore its number of verified passing original subinterpreter cases is **zero**.

The historical Zig subinterpreter archive is `oracle/phase2/evidence/owned-candidate-subinterpreters-v3-zig-phase2-v6-subinterpreters-failures.json.gz`, SHA-256 `ded1049f0d1979b6a71c80fcd86fe411e400603b02bbe28ed8b3634f513612f4`. Its complete failed child stdout contains exactly 1,126,801 bytes, SHA-256 `2da4af1e62facbe6565bb127a0920f647ec04c3f0005d02f58b233229277721d`. V7 decodes and validates the full original child, real process, cleanup ledger, archive, and receipt; it does not manufacture substitute outcomes.

## Correct the original publication check

The original nested version-three producer publishes an exact **nine-field** archive owner:

```text
relative, sha256, bytes, device, inode,
exclusive_creation, nofollow, file_fsync,
same_inode_readback_verified
```

The unchanged version-six whole-candidate checker incorrectly required `file_fsync_completed` for this original nested owner. This is a separate checker error, not proof that the genuine interpreter cleanup passed. V7 accepts exactly the real nested `file_fsync` field, authenticates the original same inode, requires the original no-follow and exclusive-creation flags, and preserves the actual failed child and all 385 calls.

Original specialist recorders retain their separate exact twelve-field `file_fsync_completed` publication schema. V7's own whole-worker and aggregate publications retain their separate exact eight-field `file_fsync_completed` schema. These three schemas are never interchangeable. A nested receipt reporting `status: PASS` and `result_status: FAIL` remains a **failed candidate**.

The original full shape-changing specialist report is larger than 32 MiB. Specialist report inputs are bounded at 64 MiB, genuine nested inputs at 48 MiB, and new V7 worker and aggregate reports at 32 MiB. Original frozen reference archives remain independently bounded at 256 MiB. No large genuine failure is truncated or discarded to satisfy a smaller bound.

## Frozen execution and verification

The complete V7 candidate worker is `tools/run_frozen_p0_candidate_worker_v5.py`. The independent whole-candidate runner is `tools/run_frozen_p0_candidate_v7.py`. The exact machine inventory is `oracle/phase2/p0-candidate-protocol-v7.json`. Every real run must pin all four committed V7 owner bytes explicitly; hashes are supplied as exact caller pins rather than embedded circularly in the files they authenticate.

The two `--self-test` commands are synthetic and forbid all actual file reads and writes, candidate imports, processes, native loading and promotion, interpreter creation, threads, clocks, network access, benchmark access, and holdout access:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/run_frozen_p0_candidate_worker_v5.py --self-test
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/run_frozen_p0_candidate_v7.py --self-test
```

The worker's `--verify-frozen-context` requires `--source-sha256`, `--protocol-sha256`, and `--document-sha256`. The whole-candidate runner additionally requires `--worker-source-sha256`. Read-only verification authenticates the full frozen original standard, all 57 historical evidence owners, complete historical mismatch ledgers, real failed nested child, exact six-family V3 activation source freeze, six-family source-independence audit, and independently decoded C++-pass, Go-fail, and Fortran-nonreproducibility source builds. It creates no candidate, reference process, build, activation, native promotion, timing measurement, or holdout access.

An actual candidate passes only if all 13 groups and all 31,237 original cases pass, with zero mismatches, crashes, timeouts, unexplained failures, or incomplete cleanup. All attempted groups and every observed mismatch remain durably published even when the candidate fails. Success never authorizes or opens the performance holdout; performance is **NOT MEASURED** until the separate later phase.
