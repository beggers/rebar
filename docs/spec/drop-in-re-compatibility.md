# Drop-In `re` Compatibility Target

## Purpose

`rebar` targets a Rust implementation of Python's `re` stack that can be loaded from CPython and used as a drop-in replacement for the standard-library `re` module. "Drop-in replacement" means user code written against `re` should continue to work without source changes, while the implementation underneath moves from CPython's current parser/compiler stack to Rust.

This document defines the public compatibility contract for that goal. It does not define the full syntax corpus or the internal Rust architecture in detail.

## Reference Boundary

- The compatibility boundary is the behavior that Python code observes when importing and using `re`.
- The target is bug-for-bug compatibility where behavior is visible at the module API, object API, parse acceptance/rejection boundary, result values, warnings, and exceptions.
- Internal implementation structure is not part of the contract unless it leaks through public behavior.
- The initial reference implementation is CPython's standard-library `re` behavior on the pinned project support version once that version is recorded in the syntax-scope work.
- If CPython behavior differs across supported versions, `rebar` will pin one version first and treat cross-version drift as follow-up work rather than silently averaging behaviors together.

## Near-Term Compatibility Requirements

The first implementation target must preserve these properties:

- Import shape compatible with `re`, including the expected module-level entry points, flags, exported helper types, and public constants that normal user code imports directly.
- Pattern compilation behavior compatible with CPython for accepted patterns, rejected patterns, warnings, and user-visible error messages where tests can pin them.
- Module-level functions compatible with CPython for argument handling, return types, and observable behavior, including `compile`, `search`, `match`, `fullmatch`, `split`, `findall`, `finditer`, `sub`, `subn`, `escape`, and cache-management surfaces that are part of normal `re` usage.
- Pattern object behavior compatible with CPython, including methods, attributes, flags, group metadata, and result production.
- Match object behavior compatible with CPython, including truthiness, indexing/group access, span/position data, expansion behavior, and string-vs-bytes result conventions.
- Flag semantics compatible with CPython, including combinations of inline flags and API-level flags, to the extent those semantics are observable from Python.
- Both `str` and `bytes` pattern/input paths treated as in-scope. A fast parser that only matches one text model is not sufficient for the drop-in target.
- Compatibility for parser diagnostics and exceptions treated as part of correctness, not a best-effort extra.

## Explicit Near-Term Non-Goals

These items are out of scope for the first compatibility milestone unless later tasking pulls them in explicitly:

- Supporting non-CPython runtimes as first-class targets.
- Providing a broader syntax than CPython `re` accepts.
- Inventing a new public API that users must opt into instead of importing `re`-compatible symbols.
- Optimization work justified only by intuition rather than the benchmark plan.
- Promising binary-compatibility details for embedding scenarios beyond normal CPython extension loading.

## Deferred or Open Behavior

The following areas remain in scope for the project overall, but this document leaves them intentionally open until dedicated follow-up tasks pin them down:

- Exact CPython version pin for the first bug-for-bug target.
- The final packaging/import strategy: dedicated extension module, Python shim over an extension, or both. The user-visible requirement is that CPython code can import the replacement through a `re`-compatible surface.
- The precise handling contract for private or semi-private implementation details in `re` and `sre_*` modules. The default assumption is "private is not promised" unless public `re` behavior depends on it.
- The exact naming/alias requirements for `re` exceptions across CPython versions where docs and implementation have drifted.
- The exact cache-size, eviction, and introspection behavior if CPython treats some of that behavior as implementation detail rather than stable API. User-visible effects still need differential testing before any deviation is accepted.

## Rust and CPython Integration Shape

The high-level implementation shape is:

- A Rust core owns parsing, pattern compilation, and the internal structures needed to drive `re`-compatible behavior.
- CPython integration exposes that Rust implementation through a Python extension boundary so Python code sees `re`-compatible module functions, pattern objects, match objects, flags, and exceptions.
- Any thin Python shim that exists for bootstrap or packaging must preserve the same public behavior and must not become the long-term home of parser logic.
- The Rust core is allowed to diverge internally from CPython's structure as long as the public Python contract remains compatible.
- FFI boundaries must be designed around preserving Python-visible semantics first; moving work into Rust is not sufficient if it changes argument parsing, exception timing, object identity expectations, or repr/attribute behavior.

## What Correctness Must Prove

Correctness testing, preferably by differential comparison against CPython, must prove:

- Which patterns compile successfully and which fail.
- Which warnings and exceptions are emitted, and at what API boundary they appear.
- Return values, match spans, group extraction, substitutions, splits, iterators, and pattern metadata.
- Behavior differences between `str` and `bytes` inputs.
- Observable flag behavior, including inline-flag interactions.
- Public object behavior for module objects, pattern objects, and match objects.
- User-visible cache and purge behavior if those surfaces remain part of the module contract.

If a behavior matters to user code, it is a correctness question before it is a performance question.

## What Benchmarks Must Measure

Benchmarks exist to measure speed once correctness is held constant. The benchmark plan must cover at least:

- Parser/compile throughput for representative valid patterns.
- End-to-end module call overhead for common entry points such as `compile`, `search`, and `match`.
- First-use and repeated-use paths where cache behavior materially changes cost.
- Workloads that distinguish parser speed from matching speed so the project does not claim parser wins that disappear at the module boundary.

Benchmarks do not establish compatibility. They only measure cost on already-correct behavior.

## Acceptance Rule for Future Work

Future implementation tasks should assume this rule:

- A change is acceptable if it preserves the Python-visible `re` contract defined here and can be validated by correctness tests.
- A change is desirable if it also improves benchmarked cost on targeted workloads.
- A change is not acceptable if it is faster but observably less compatible.
