# First-party C original correctness campaign, version 8

This experiment tests the independently written C regular-expression engine
against Python 3.14.6. It changes evidence transport and failure diagnostics,
not the matcher, the original test cases, the strict runtime guard, or the
reference answers. Freezing this source does not execute the candidate.

## Preserve the actual previous result

The actual version-7 public receipt is exactly
`bba4b8498a37db0bf9651c0bb040deaf96f9eef363ba6f2e2c923379d7fa5080`.
It describes 13 distinct, actually executed workers, five completed suites,
13,094 confirmed passing original cases, at least 236 real semantic
mismatches, seven candidate-execution failures, and one infrastructure
failure. The complete mismatch count is **NOT MEASURED**. The receipt says
publication passed and the candidate failed; those are different outcomes.
The previous compressed archive is authenticated through the public receipt
and is not opened during source-only verification.

| Frozen original suite | Cases | Actual version-7 result |
| --- | ---: | --- |
| `original_bounded_v5` | 151 | Candidate execution failed |
| `public_v3` | 864 | Candidate execution failed |
| `scanner_v3` | 1,024 | Candidate execution failed |
| `buffer_v3` | 768 | Candidate execution failed |
| `managed_v1` | 1,024 | 16 genuine differences |
| `scanner_verbose_v1` | 2,854 | Passed |
| `public_types_v1` | 6,912 | 216 genuine differences |
| `substitution_v2` | 5,120 | Strict result reader rejected an unpaired surrogate |
| `shape_v2` | 10,240 | Passed |
| `public_surface_v19` | 1,376 | Private normalized envelope was not transportable |
| `subinterpreter_v2` | 128 | Genuine child lifecycle failed |
| `pep688_v4` | 264 | 4 genuine differences |
| `threaded_pattern_v1` | 512 | Source and transport vector digests disagreed |
| Total | 31,237 | Candidate failed |

The separate 8,244 reference checks are not included in that denominator.
The proposed 14,155,776 benchmark cases are not generated, frozen, or opened.
Time, memory, statistical confidence, and undefined behavior remain
**NOT MEASURED**. No winner has been selected.

## Exact evidence fixes

The immutable original result reader correctly rejects unpaired JSON
surrogates. The new controller leaves that reader untouched. Only after a
real original observation and semantic comparison, it preserves genuine
Python surrogate strings as fully reversible, explicitly identified UTF-16
code units. Real bytes, tuples, and mapping-key collisions are also explicitly
preserved. Ordinary mappings are never mistaken for transport metadata.

The frozen public-surface suite creates `_NormalizedEnvelope` objects through
its own source-authenticated factory and private identity registry. The new
reporter accepts only the exact frozen source, exact class, and exact
registered instance. It preserves all fields, class provenance, and genuine
nested buffer flags. Forged instances, subclasses, and lookalike dictionaries
are rejected. This occurs after the original frozen semantic comparison.

Some frozen suite sources compute their complete-vector digest without a
trailing newline. The strictly canonical worker transport includes that
newline. Version 8 independently authenticates and publishes both exact
whole-vector digests. It does not equate, discard, or replace either digest.
Bounded record prefixes are explicitly marked as prefixes.

Every genuine original candidate and nested-child failure retains its
literal underlying error, completed-case count, available active-case
identity, nested failure chain, and 120-second worker limit. A reporting
correction never makes an incomplete suite pass and never reduces a real
semantic mismatch.

## Actual build and guard

Version 8 binds only the already built and actually published first-party
C18 source and native image. Its actual build receipt is
`4070feca7129fdcf3dc9762fae853649c68c722940af6157ecdcfa59d23e65ae`,
its actual root receipt is
`a231eec31b29ca796c75cee03b702a3e35a9195e74675c8f56209419dfeb03c8`,
and its actual engine and bridge share native SHA-256
`f3794f963819a9af3798c1d97f32edcbc2a117f9ed20c56ec554a605de82eeae`.
No future build is assumed or authorized.

The original version-2 anti-delegation guard is installed before importing
the independently written C candidate. Python `re`, `_sre`, other candidate
families, external regex packages, fallback engines, `ctypes`, hidden
answers, and benchmark detection remain forbidden. All 13 original suites
must run in 13 genuinely distinct isolated Python workers. The original
native inode must be restored exactly before actual publication.

Source-only self-test, context verification, and contract rendering may read
only authenticated frozen source and compact public receipts. They do not
activate the matcher, open a private root, inspect a native image, open a
compressed archive or holdout, start a compiler or worker, change workspace
files, collect timings, or claim candidate compatibility.

Only 13 completely observed suites, all 31,237 original cases, zero genuine
mismatches, zero worker failures, the strict no-delegation guard, and exact
native restoration can qualify the candidate. Version-8 candidate
correctness remains **NOT MEASURED** until its separately authorized actual
operation is executed and its real result is published.
