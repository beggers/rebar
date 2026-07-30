# Additional real Python regular-expression buffer carriers

Status: **SOURCE FREEZE ONLY. The two new official Python references have not
run. No replacement has run this supplement. No expected answer is recorded.**

This supplement asks whether an independently built replacement behaves like
the pinned CPython **3.14.6** regular-expression module when users supply real
typed arrays, memory maps, and unusually shaped Python buffer views. It never
changes the original **31,237** cases, **13** suites, **73** obligations,
**34** crosswalk entries, or **13** individually named private waivers.

The existing original baseline already includes **768** memory-view cases,
**1,024** managed-buffer cases, **1,024** scanner cases, **5,120**
substitution-buffer cases, **10,240** changing-buffer cases, and **264**
Python-defined buffer-exporter cases. Those are genuine existing tests, not
missing work and not newly counted cases. The separately proven **8,244**
differential and property cases and **50** callable-signature cases remain
separate as well.

## What the new questions cover

The source defines every new case deterministically using unique
`buffer-carriers.v1/` identifiers and five disjoint cohorts:

| Additional question | Separately frozen cases |
| --- | ---: |
| Subjects and both scanner interfaces | 28,294 |
| Carriers supplied as patterns | 3,870 |
| Replacement templates and callback results | 3,184 |
| `re.escape` carrier conversion | 344 |
| Applicable owner and buffer lifetime events | 12,724 |
| **Additional total, not in the original 31,237** | **48,416** |

The complete matrix covers **86** explicitly identified carriers and has
source-ordered, canonical newline-delimited SHA-256
`4de04250c99a87d188bf1f8386ad80044ae86d136908ea7aa1bc86e8b7c32ab1`.
Every case is a frozen question, not a recorded outcome.

- A bytes-pattern subject in every published module function, compiled-pattern
  operation, native compiled-pattern scanner, and the distinct public
  `re.Scanner`; match, no-match, empty, zero-width, capture, byte-window,
  high-byte, embedded-NUL, and lookaround inputs are separately identified.
- Buffer exporters supplied as the pattern itself, including compilation,
  module operations, repeated cache keys, and mutable inputs.
- Buffer exporters supplied as replacement templates or returned by
  substitution callbacks, including literal replacements, named and numeric
  backreferences, escaped backslashes, invalid escapes, and empty templates.
- Each carrier passed to the separate `re.escape` conversion path.
- Real owner, view, iterator, match, scanner, callback, exception, mapping,
  resizing, closing, release, and garbage-collection lifetime observations.

Carrier definitions include nonempty signed and unsigned arrays with native
typecodes `b`, `B`, `h`, `H`, `i`, `I`, `l`, `L`, `q`, and `Q`; nonempty
floating-point `f` and `d`; and `u` and `w` character arrays. The pinned
upstream test already covers **empty** `bBhuwHiIlLfd` arrays; it is
authenticated as existing evidence and is never described as a new passing
reference. Native and byteswapped layouts are distinct. The native byte order
is read from the actual pinned interpreter. Element widths, warning behavior,
acceptance, and byte offsets remain **NOT RECORDED** until actual reference
workers run.

Eight declarative, mathematically verified raw layouts freeze the exact hex
representations of signed and unsigned 16-bit values and unsigned 32-bit
values in both little- and big-endian order. Their recorded source
specifications do not construct a bytes carrier or predict matching.

The view definitions cover readonly and writable views, offsets, genuine
one-dimensional stepped and reversed slices, empty and single-element stepped
views, native typed-array formats, valid single-character native casts,
C-contiguous multidimensional views, and explicitly released views. The
protocol does not claim that `memoryview.cast('<H')`, noncontiguous matching,
multi-dimensional matching, or use of a released view succeeds. Both results
and exact exceptions remain **NOT RECORDED**.

Anonymous writable mappings and file-backed readonly, writable, and
copy-on-write mappings have separately identified direct and retained-view
cases. Their closed states, view release, attempted resize and close, owner
collection, live iterators, compiled scanners, and public scanner remainders
are independent observations. This source freeze does **not** create a
mapping or backing file.

Python's public `re.Scanner.scan` and compiled `Pattern.scanner` are different
interfaces. Future evidence must retain the actual public scanner's
`(tokens, remainder)` result, callback argument types, remainder slicing and
exact carrier type; compiled scanners retain their actual `Match` or `None`
observations. Nested result types, match-subject identity, byte-offset spans,
warning category, exact exception class, module, message, arguments,
callback-raised `KeyboardInterrupt`, `SystemExit`, and `GeneratorExit`, and
every real cleanup and exporter event must be recorded. None is predicted or
silently classified as a harness error.

Case construction rejects inapplicable combinations: module functions and
public scanners do not receive compiled-pattern search windows; empty
replacement scenarios use genuinely empty exporters, including stepped
views; mutation requires a writable owner; shorter mutation does not
pretend that an exported view can resize its owner; and mapping, file,
typed-array, view, iterator, native-scanner, and callback lifetime actions
appear only for carriers and operations that can actually exercise them.

## Independent source-only safety

The source bootstraps without importing `re`, `_sre`, `array`, `mmap`, a
candidate, an external package, or `rebar`. It installs an irreversible
CPython audit hook before opening any authenticated source owner. Exact
read-only, close-on-exec, no-follow descriptors authenticate independently
pinned owner bytes, devices, inodes, permissions, and single link counts.
A duplicate-key-strict, bounded JSON codec does not import `json` or a
regular-expression engine.

Real blocked callable probes and separately labeled synthetic audit-event
probes cover captured `_io` and `posix` file aliases; imports; native and
process loading; mappings; array and view construction; threads; network;
clocks; garbage collection; compressed archives; directory access;
environment changes; and workspace writes. A blocked synthetic event is
never reported as an actual mapping, reference, timer, archive, or process.
Source-only output separately records blocked attempts and actual effects.
All actual effects must remain zero.

The source generates the complete source-ordered case matrix in memory,
hashes every individually canonicalized newline-terminated case, and freezes
the derived case total, five exact cohort totals, carrier catalog, operations,
scenarios, unique identifiers, and future observation fields. Every single
new row has expected answer **NOT RECORDED**. A source-freeze `PASS` means
only that these definitions and physical boundaries are verified; it is not
a Python self-oracle and does not qualify any candidate.

## Reproduce the frozen source

Independently determine all three SHA-256 pins:

```text
sha256sum tools/verify_owned_public_buffer_carriers_supplement_v1.py \
  oracle/phase1/P0-PUBLIC-BUFFER-CARRIERS-SUPPLEMENT-V1.md \
  oracle/phase1/p0-public-buffer-carriers-supplement-v1.json
```

Use only the official pinned stable executable
`/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14`, SHA-256
`255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016`.
Run each source-only mode both normally and in an empty environment:

```text
python3.14 -I -B -S \
  tools/verify_owned_public_buffer_carriers_supplement_v1.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

python3.14 -I -B -S \
  tools/verify_owned_public_buffer_carriers_supplement_v1.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin LC_ALL=C /absolute/path/to/python3.14 -I -B -S \
  tools/verify_owned_public_buffer_carriers_supplement_v1.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin LC_ALL=C /absolute/path/to/python3.14 -I -B -S \
  tools/verify_owned_public_buffer_carriers_supplement_v1.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

The future expanded **14,155,776-case** performance holdout remains
**NOT FROZEN / NOT GENERATED / NOT OPENED**. Speed, memory, confidence
intervals, undefined behavior, replacement compatibility, and a winner
remain **NOT MEASURED**. Recording two complete actual official Python
references requires a later, separately frozen and explicitly authorized
experiment.
