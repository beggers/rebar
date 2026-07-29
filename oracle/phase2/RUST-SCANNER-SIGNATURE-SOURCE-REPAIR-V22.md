# First-party Rust scanner signature repair

Status: **SOURCE FROZEN; VARIANT NOT BUILT; NOT RUN; NOT BENCHMARKED.**

This is a small, source-only improvement to the project's independently
written Rust regular-expression engine. It does not run a candidate, build
native code, import a regular-expression implementation, or expose the
final performance comparison.

## Start from an actual first-party build

The immediate predecessor is the complete, cumulative Rust bridge:

```text
candidates/rust/variants/buffer_shape_pickle_findall_captures_v1/py_bridge.c
SHA-256  a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a
bytes    179520
```

This predecessor has an actual independently reproduced native build. Its
small public build and root-provenance receipts are, respectively:

```text
bc3ebdc835ef6a89d351c4541863274d410e2685d35eacdc9668f4bf3a474102
73cee9c0a4f44d113da96b505eb0e9224577584b75c347e6fd351995d1d09a4e
```

They record two offline source-build phases and 28 real compiler or binary
inspection processes. They establish a first-party **BUILD PASS** for the
predecessor, not a matching, compatibility, runtime-independence, or speed
result. The verifier reads only the two small, explicitly authenticated
receipts. It never reads the compressed build report or a private native
build directory.

## Change exactly two metadata entries

The existing Rust scanner already executes the project's own Rust engine.
Its displayed native type, `_sre.SRE_Scanner`, is Python-compatible type
metadata; it is not an import of `_sre` or a delegation to Python's matcher.

Change only the `METH_NOARGS` entries in `rust_scanner_methods[]`:

```c
{"search", (PyCFunction)rust_scanner_search, METH_NOARGS,
 "search($self, /)\n--\n\n"},
{"match", (PyCFunction)rust_scanner_match, METH_NOARGS,
 "match($self, /)\n--\n\n"},
```

The empty body following `--` is essential. Frozen CPython 3.14.6 reports
`__text_signature__ == "($self, /)"` and `__doc__ is None`; the unbound
signature is `(self, /)` and the bound signature is `()`. Adding an
ordinary descriptive docstring would create a new compatibility difference.

The different fastcall scanner entry must remain unchanged. So must the
parser, matcher, capture construction, literal-search improvement, public
scanner type name, and existing bound-method signature implementation. In
particular, this two-entry source repair does not prove that the existing
bound-method implementation is runtime-independent.

The exact in-memory successor is:

```text
SHA-256  6639104f618b5a905d0883b02e5183b9a3b6ac6db0587b1dfa7b074990f3bb75
bytes    179482
```

The successor is represented as a deterministic in-memory transformation of
the authenticated predecessor. The verifier does not materialize, build,
load, or run it. Forward and reverse byte comparisons prove that all other
predecessor bytes remain unchanged.

## Keep reference observations distinct from candidate observations

The separately frozen 50-case callable-introspection reference contains
these four compiled-scanner observations:

```text
callable-introspection.v1.scanner.03.unbound.compiled-scanner.match
callable-introspection.v1.scanner.04.bound.compiled-scanner.match
callable-introspection.v1.scanner.05.unbound.compiled-scanner.search
callable-introspection.v1.scanner.06.bound.compiled-scanner.search
```

The authenticated CPython reference passes. The four candidate corrections
are source-based predictions, **not observed candidate results**. Candidate
introspection is **NOT MEASURED**. These 50 additional cases are separate
from the frozen 31,237 original cases across 13 groups and the separate
8,244 additional differential cases. Denominators are never combined.

## Reproduce without writes

Use only the frozen isolated CPython 3.14.6 executable:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
```

Hash the three new owners:

```text
tools/verify_owned_rust_scanner_signature_source_v22.py
oracle/phase2/RUST-SCANNER-SIGNATURE-SOURCE-REPAIR-V22.md
oracle/phase2/rust-scanner-signature-source-repair-v22.json
```

Run both verification modes using those exact hashes:

```text
python3.14 -I -B -S tools/verify_owned_rust_scanner_signature_source_v22.py \
  --self-test \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

python3.14 -I -B -S tools/verify_owned_rust_scanner_signature_source_v22.py \
  --verify-frozen-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

Repeat both commands under `env -i PATH=/usr/bin:/bin LC_ALL=C`. All four
commands are read-only. The verifier authenticates every permitted public
owner, rejects unauthenticated sources and writable modes, and prohibits
regular-expression imports, subprocesses, compilers, dynamic libraries,
archives, private build roots, clock samples, network access, and hidden
benchmark cases. Its canonical `--render-contract` mode also writes only
to standard output and accepts exactly the source and protocol hashes.

The source repair still needs an independently authenticated native build,
all 31,237 original cases, all 8,244 additional cases, the public API and
callable-introspection checks, and the runtime no-delegation audit. None
has been run for this successor.

The proposed 14,155,776-case final comparison remains **NOT FROZEN**,
**NOT GENERATED**, and **NOT OPENED**. The previous 4,194,304-case proposal
remains preserved. Performance, memory, confidence intervals, undefined
behavior, and complete candidate compatibility are **NOT MEASURED**.
Qualified independent replacements: **0**. No winner is selected.
