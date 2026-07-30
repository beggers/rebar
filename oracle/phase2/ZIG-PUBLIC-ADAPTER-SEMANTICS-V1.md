# First-party Zig public-adapter semantics, version 1

Status: SOURCE FREEZE ONLY. The independently written Zig engine is not built,
imported, activated, matched, benchmarked, or qualified by this experiment.

## Preserve the exact observed failure

The frozen original Python reference contains 31,237 checks in 13 groups. The
last complete Zig attempt verified 4,607 checks in seven passing groups. Five
completed groups exposed exactly 1,700 genuine differences:

| Original group | Actual differences |
| --- | ---: |
| Scanner comments and captures | 620 |
| Public types, equality, serialization, and flags | 248 |
| Replacement-buffer lifetimes | 64 |
| Shape-changing buffers and replacement errors | 672 |
| Additional public flags | 96 |

Its remaining 128-check child-interpreter group failed before completion, so
the complete candidate mismatch count is **NOT MEASURED**. The compressed
historical archive, all 13 actual processes, and the previous failure receipt
remain unchanged. Publication success never means candidate success.

The observed public-type differences further partition into 96 error-module
cases, 96 subclass-pattern equality cases, 12 unknown-flag representations,
12 pattern flag-order representations, and 32 native match-pickling cases.
The separate 96 public-surface differences divide evenly into unknown-flag
representation, indexed compile arguments, and mixed or inverted flags.

## Exactly scoped first-party fixes

Start with the authenticated owned lifetime-safe Zig Python adapter,
SHA-256 `e9e052fdd50bcec54145b828b1353cf082c6bc13869176486bcfa41d1624ab50`.
First independently reproduce the already frozen object-setter-safe finalizer
in memory; its complete intermediate source must have SHA-256
`c16a6e4c9745eff3a55dcf85eb14c26ec84092d70ddbc40d5e841ab0140d3032`.

Apply only these additional owned Python-adapter corrections:

1. Identify the public `PatternError` class as belonging to `re`.
2. Compare and hash compiled patterns by pattern value and flags while keeping
   base strings and their subclasses in separately keyed compilation caches.
3. Display known flags in Python's numeric order; retain unknown bits and use
   the exact Python class or hexadecimal spelling for unknown values.
4. Preserve ordinary integer and flag arguments but reject index-only objects
   through Python's genuine bitwise operation before native compilation.
5. Retain the independently frozen safe finalizer, including early-bound
   attribute access, ownership clearing, native release, and error propagation.

These changes are modeled to correct 312 observed cases. This is a source-level
prediction, not a candidate result. At least 1,388 existing measured failures
remain: all 620 scanner differences, 32 native match-pickling differences,
64 replacement-lifetime differences, and 672 shape-changing-buffer differences.
The unfinished interpreter group remains **NOT MEASURED**.

No matching parser, compiler, scanner, executor, native engine, native bridge,
other candidate, external regex package, Python `re`, or `_sre` is changed,
imported, or used. Cache separation is preserved. No existing test, record,
denominator, waiver, failure, or guard is changed.

## Source-only gates and exclusive publication

Use the exact official pinned CPython 3.14.6 with `-I -B -S`. Independently pin
the source, this protocol, the complete canonical JSON contract, the original
adapter, frozen finalizer, complete previous Zig failure receipt, frozen V15
campaign and its three owners, frozen finalizer source and its three owners,
and the exact independent public-type oracle source.

Run `--verify-frozen-context` and `--self-test` in both the ordinary isolated
environment and the empty environment
`env -i PATH=/usr/bin:/bin LC_ALL=C PYTHONDONTWRITEBYTECODE=1`. Every source
mode uses a deny-default, read-only physical owner wall; candidate imports,
matching, native loads, archive access, private roots, hidden cases, timers,
processes, interpreter creation, and all writes remain zero. Synthetic checks
exercise the genuine isolated flag, error, pattern-equality, indexed-argument,
and finalizer code without activating a matching engine.

The prospective target
`candidates/zig/variants/public_adapter_semantics_v1/zig_candidate.py` must
remain absent throughout all source-only checks. Only a separately authorized,
fully pinned root-only `--apply` may exclusively create that exact new source.
It never overwrites an existing file or changes a canonical candidate.

Correctness: **NOT RUN**. Runtime non-delegation: **NOT ESTABLISHED**.
Performance: **NOT MEASURED**. Hidden final test: **NOT OPENED**.
Qualified Zig replacements: zero. Winner: none.
