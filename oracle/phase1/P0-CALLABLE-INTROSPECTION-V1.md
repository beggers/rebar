# Python regular-expression callable signatures

Status: **SOURCE FREEZE ONLY. The two-reference introspection baseline and
all candidate introspection results are NOT RUN.** Performance, memory,
undefined behavior, and the final holdout are **NOT MEASURED** or **NOT OPENED**.

This is one separately counted addition to the immutable Python 3.14.6
correctness test. It does not replace, edit, expand, or reinterpret the
original **31,237** cases, **13** suites, **13** named private waivers, or
published results. Passing the old test does not mean that a candidate has
passed these new questions. Passing the new questions does not mean that a
candidate has passed the old test.

## The independently verified missing behavior

The original pinned standard library explicitly publishes the user-visible
signatures of `re.sub`, `re.subn`, and `re.split` at lines **209**, **239**,
and **268** of its authenticated `re/__init__.py`. Python's `inspect.signature`
also exposes parameter names, positional-only parameters, default values,
bound methods, and unbound methods throughout the regular-expression API.

None of the source owners of the original 13 suites, their delegated
public-surface evaluator, or the original upstream `test_re.py` checks
`inspect.signature`, `__signature__`, or `__text_signature__`. Existing
coverage of `__all__`, wildcard imports, deprecated positional warnings,
flag representations, copying, pickling, and ordinary callable behavior is
real. It is not a substitute for an introspection observation, and none of
those existing tests is removed or counted again.

The independently pinned reference is only:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/__init__.py
741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35

oracle/cpython-3.14.6/test_re.py
879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2
```

## Exactly 50 additional public observations

| Category | Separate cases | What is checked |
| --- | ---: | --- |
| Public module functions | 11 | `match`, `fullmatch`, `search`, `sub`, `subn`, `split`, `findall`, `finditer`, `compile`, `purge`, and `escape`. |
| Compiled patterns | 18 | The bound and unbound signatures of nine public methods. |
| Match objects | 14 | The bound and unbound signatures of seven public methods. |
| Both kinds of scanner | 7 | `re.Scanner` initialization and scanning, plus bound and unbound compiled-scanner methods. |
| **Separately counted total** | **50** | **Never included in the original 31,237.** |

Every case has one deterministic, source-ordered identifier. The machine
contract pins the complete 50-case matrix and its canonical SHA-256. Records
retain exact parameter names, parameter kind, positional-only behavior,
default values, return annotations, whether a text signature exists, and its
complete original value. The architecture-specific integer for Python's
maximum index is represented by the semantic marker `sys.maxsize`.

Python's ordinary `Match.group` is genuinely not inspectable and raises
`ValueError`. Record the actual public exception class. Do not compare
implementation-specific error text, private module paths, memory addresses,
the name of a module imported as `re`, or a guessed regular-expression
answer.

The three CPython source-defined public text signatures are:

```text
sub:   (pattern, repl, string, count=0, flags=0)
subn:  (pattern, repl, string, count=0, flags=0)
split: (pattern, string, maxsplit=0, flags=0)
```

This source freeze is **not** an executed two-process reference and does not
claim that Rust, C, Zig, C++, Go, or Fortran passes a single new case.

## Preserve historical and current evidence separately

The original phase-one ledger remains:

```text
oracle/phase1/p0-completeness-v1.json
cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f

oracle/phase1/P0-COMPLETENESS-V1.md
1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798
```

The preserved version-30 overview actually recorded **149** repository
evidence owners and **154** digest-addressed history references. It remains
valid historical evidence; those are not the current owner counts.

A subsequently published Rust source build added exactly two independently
authenticated evidence owners:

```text
oracle/phase2/evidence/native-source-build-v12-rust-phase2-v12-rust-flag-original-p0.json.gz
840a6403699fec44d4f725f737fc9538c997b818a48d167398ad1b95cbb9828d

oracle/phase2/evidence/native-source-build-v12-rust-phase2-v12-rust-flag-original-p0-publication-receipt.json
1cd7e538098711ddac017ee3375d302d4b1ba4e6da52d10d2a524103db500a2f
```

Its actual released totals are **151** evidence owners and **156** history
references. Its receipt proves a source build, not a correctness run. The
frozen-context verifier authenticates the exact compressed source-build bytes
without decompressing the archive.

The actually measured matching results remain **1,087 Rust differences**,
**1,230 C differences**, and **2,172 Zig differences**. There are **zero**
qualified replacements. No candidate or independent reference has run the
50 additional observations.

The original large-input candidate harness uses a **5,147-item dry run**.
Separate Python-only evidence of an actual **2,147,483,648**-item input and
a **42,949,672,960-byte** resource allowance does not establish that a native
candidate passed either `test_large_search` or `test_large_subn`. The genuine
full-resource candidate tests remain **NOT RUN**; this 50-case amendment
does not waive, replace, or claim to execute them.

The separately planned **4,194,304** final examples remain **NOT GENERATED**
and **NOT OPENED**. Speed, memory, undefined behavior, confidence intervals,
and a winner remain **NOT MEASURED** or **NOT SELECTED**.

## Reproduce only the frozen-source gates

First calculate and independently supply the exact three owner hashes:

```text
sha256sum tools/verify_python_re_callable_introspection_v1.py \
  oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md \
  oracle/phase1/p0-callable-introspection-v1.json
```

Use the stable, isolated interpreter and all three caller-supplied pins:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/verify_python_re_callable_introspection_v1.py \
  --self-test \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin LC_ALL=C \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/verify_python_re_callable_introspection_v1.py \
  --self-test \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/verify_python_re_callable_introspection_v1.py \
  --verify-frozen-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin LC_ALL=C \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/verify_python_re_callable_introspection_v1.py \
  --verify-frozen-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

The source-only self-test first authenticates only its three independently
pinned owners. Its synthetic controls then physically block candidate and
Python-reference imports, matcher calls, native libraries, file operations,
processes, threads, clocks, network access, archive decompression, locale
changes, and hidden or final examples. Read-only context verification
authenticates the original ledger, installed CPython source, historical V30
overview, both actual Rust V12 build evidence owners, and original six-family
producer; it runs no reference or candidate and never decompresses a source
build or candidate-matching archive.

Only after this source, protocol, and canonical machine contract have been
separately committed and pushed may a future explicitly authorized
`--run-reference` start its two distinct, pinned standard-library worker
processes. Keep their complete 50-case vectors, actual different process IDs,
complete output streams, and first failure. Commit and push their result
before considering any candidate.

Only a separately authorized `--run-candidate` may later run one of the six
original independent families. It must first authenticate the committed
two-reference baseline, a genuinely passing original **31,237-case** report,
and an independently passing no-delegation proof. An external package,
standard-library matching fallback, another candidate, unqualified native
build, unpublished baseline, or partial report fails closed. Neither mode is
executed or implied by this source freeze.
