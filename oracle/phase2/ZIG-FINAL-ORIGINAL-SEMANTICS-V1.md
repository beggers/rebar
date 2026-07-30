# Final first-party Zig corrections for the frozen original suite

This source-only experiment preserves the complete failed Zig run with
31,237 frozen original Python checks. Thirteen independent workers completed;
18,056 checks are verified, and 1,156 mismatches remain. The authenticated
public receipt is
`a7019c02b2906eb15f622e9bd9e61eb7476c528019fac537ed7072b3f82efe7a`.
The archived observation remains untouched and unopened by this controller.

Every observed mismatch belongs to one of two independently diagnosed
first-party corrections:

| Frozen original category | Scanner capture ending | Flag display | Total |
| --- | ---: | ---: | ---: |
| Upstream bounded Python tests | 0 | 2 | 2 |
| Public practice | 34 | 0 | 34 |
| Scanner differential | 64 | 0 | 64 |
| Scanner comments and verbose patterns | 930 | 0 | 930 |
| Public Python types | 0 | 48 | 48 |
| Public Python surface | 0 | 78 | 78 |
| Total | 1,028 | 128 | 1,156 |

Independent, read-only replay transformed all 1,154 structured actual
observations into their complete expected observations. The other two are
upstream assertions requiring the same flag corrections. No candidate was
executed during that forensic analysis.

## Scanner capture ending

The native Zig bridge projects each scanner branch into its Python-visible
capture group. When the branch contains another capture in the same slot,
Python preserves the inner capture's beginning but closes that slot when the
whole branch finishes. The current bridge preserves the beginning and the
incorrect earlier ending.

Change only the active branch projection so its ending is always the complete
match ending. Preserve an already-recorded nested beginning. If the slot was
empty, preserve the existing full-match-beginning fallback. Do not change
branch selection, bounds checks, other groups, or `lastindex`.

For example, a nested capture of `a` inside a match of `abc` becomes `abc`;
a nested capture of `a` after a leading `#` inside `#ab` becomes `ab`, not
`#ab`. Strings, bytes, bytearrays, and memoryviews are independently modeled.

The immutable bridge source is
`candidates/zig/variants/replacement_event_semantics_v1/py_bridge.c`, SHA-256
`07337863f6b4a0e749a8d60b2e5704bb961e43dc09bfa85c238f0efa40d3583c`.

## Public flags and compiled-pattern display

Python flag objects expose their flags in class-declaration order. Compiled
patterns independently display their flags in increasing numeric-bit order.
These orders differ: a flag object displays
`re.ASCII|re.IGNORECASE`, while a compiled pattern displays
`re.IGNORECASE|re.ASCII`.

Unknown-only flag objects use a decimal representation such as
`re.RegexFlag(512)`. Unknown-only compiled patterns use hexadecimal, such as
`re.compile('a', 0x200)`. Mixed unknown bits remain hexadecimal in both.

Give the first-party adapter the complete Python flag member and alias
surface, declaration-ordered object representations and names, and separately
numeric-ordered compiled-pattern representations. Preserve its engine,
matching semantics, existing pattern truncation, and Unicode flag masking.

The immutable adapter source is
`candidates/zig/variants/public_adapter_semantics_v1/zig_candidate.py`,
SHA-256
`7129c63bdfd3c265a44541500238c26a8a5511f8932140de7d06bb49c13f588d`.

## Strict source-only gates

Run the controller only with pinned CPython 3.14.6 and `-I -B -S`. Two
ordinary source gates and the same two gates in a sterile environment must
pass. Self-tests read no files. Verification authenticates only its own
source, this protocol, its exact frozen contract, and the historical public
receipt. It never opens either candidate input, the compressed archive, a
private directory, a benchmark, or a holdout.

The permanent wall blocks standard-library regular-expression imports,
external packages, dynamic code, processes, native libraries, unauthenticated
paths, inherited descriptors, destructive filesystem operations, clocks,
compressed archives, private data, and hidden holdout contents or metadata.
Both `os` and its underlying native `posix` aliases are guarded.

The synthetic gate independently checks exhaustive flag values, compiled
pattern displays, inverted flags, every public flag alias, and scanner branch
projections across all four supported subject representations. It preserves
every currently passing category; no timing, matching, compilation, or
candidate qualification is claimed.

Only after this source freeze is committed and pushed may root authorize
application. Root then reads both exact immutable candidate inputs, validates
both expected outputs before any mutation, and exclusively creates one private
variant directory containing:

- `candidates/zig/variants/final_original_semantics_v1/zig_candidate.py`;
- `candidates/zig/variants/final_original_semantics_v1/py_bridge.c`.

The directory is mode `0700`; each source is mode `0600`, created with
`O_EXCL` and `O_NOFOLLOW`, verified by exact hash and size, and synchronized.
No existing candidate source is changed. A later independently frozen build
and complete correctness run are still required.

Correctness: NOT MEASURED. Runtime independence: NOT ESTABLISHED.
Performance, memory, and undefined behavior: NOT MEASURED.
Qualified candidates: zero. No winner is selected.
