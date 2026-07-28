# Six independent engines, built from first-party source

This gate answers one question: are six genuinely different regular-expression
engines implemented in this repository, rather than wrappers around Python's
`re`, another regex package, or one another?

It is a static, source-only answer. It does not build, import, load, execute,
benchmark, or qualify a candidate.

| Family | First-party parser, compiler, and matching engine | Source files |
| --- | --- | ---: |
| C virtual machine | Python bytecode parser and compiler; separate owned C executor | 2 |
| Rust | Owned Rust parser, compiler, executor, support modules, native bridge, and dependency lock | 9 |
| Zig | Owned Zig parser, compiler, executor, Python bridge, and one precisely anchored native loader | 3 |
| C++ | Owned C++ parser, compiler, executor, private header, and Python bridge | 4 |
| Go | Owned Go parser, compiler, executor, dependency-free module, and Python bridge | 4 |
| Fortran | Owned Fortran parser, compiler, executor, and Python bridge | 3 |

The total is exactly **six distinct families and 25 distinct source owners**.
Python's `re` is the baseline, not a seventh replacement. The exact owner paths,
roles, and SHA-256 values are frozen in
`oracle/phase2/candidate-independence-v2.json`. Every owner must agree with the
already published version-seven overview input. Here **version seven refers
only to that published overview, not to a candidate correctness protocol**.
The published candidate correctness protocol remains version five.

The two separately pinned Python project support files, `pyproject.toml` and
`uv.lock`, are not candidate source owners. The verifier parses both complete
files and requires exactly the local first-party package, no production or
optional dependencies, no external package, and no extra workspace or source.
Neither support file changes the **six-family, 25-source-owner** denominator.

The verifier parses Python adapters as syntax; independently tokenizes C,
C++, Rust, Zig, Go, and Fortran; verifies each family's real parser, compiler,
and executor; rejects a missing owner, a shared semantic owner, a foreign
header, a cross-family bridge, a dynamic loader, a process or environment
escape, Python `re` or `_sre`, and third-party regex dependencies. It checks
the entire Rust manifest and lock and the complete Go module. The only allowed
Zig dynamic load is its one owned, `__file__`-anchored `_zig_probe.so`.

Go's C bridge receives extra scrutiny because executable cgo directives live
inside comments. Its complete C preamble must contain exactly three ordinary
C headers, with no foreign source, linker option, hidden import, `go:linkname`,
or embedded binary. Fortran may not include another source file, and all 12 of
its native binding names must belong to its own engine. Versioned PCRE,
Oniguruma, Hyperscan, RE2, Rust regex, and C++ standard or Boost regex calls
are rejected even when an external header is hidden.

Python Unicode operations and the normal Python C interface are not regex
engines. A literal `unicodedata` support import is permitted only in the owned
C++ and Go bridges. The Rust bridge's literal `copyreg`, `functools`, and
`inspect` support imports are recorded. Since `inspect` can indirectly import
Python `re`, source analysis alone cannot establish runtime non-delegation;
the later isolated correctness runner must check it separately. Public
compatibility strings such as `_sre.SRE_Scanner` are display names, not engine
imports. C++ and Fortran may use only `sys.maxsize`, not Python's module table
or import machinery.

There is **no committed or generated Go engine header**. A future, separately
authorized clean build would generate its header beside its own phase-local
shared object. This gate reports the header as **NOT GENERATED; NOT BUILT**;
it neither invents a repository path nor claims a Go build exists. Fortran,
C++, and Go are not claimed to have passed a native source-build gate.

The immutable Python baseline remains **13 suites, 31,237 checks, and 13
explicitly named private waivers**. The verifier independently reads and
checks the exact SHA-256 of **all 34 current C and Rust version-five evidence
owners: 16 compressed failure reports and 18 publication or restoration
receipts**. Compressed reports are checked as raw bytes; they are never
decompressed, interpreted, or executed. It also authenticates the distinct
set of **24 historical receipts** across all published families. A receipt
means that evidence was published, not that its candidate passed. The failed
Zig build, later successful Zig source build, and C and Rust correctness and
worker failures all remain visible as their actual historical outcomes.

The source-only test uses positive synthetic fixtures and hostile imports,
aliased native loaders, computed imports, cross-family bridges, unsafe paths,
foreign Python, Rust, and Go dependencies, altered graph provenance,
concealed historical failure reports, C string concatenation, Go raw strings,
C++ raw strings, and Fortran comments. It intercepts file access, candidate
imports, process creation, native loading, networking, and all ordinary and
high-resolution clocks. All external-effect counters must be zero in both an
ordinary and an empty environment.

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B tools/audit_candidate_independence_v2.py --self-test

    env -i \
      /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B tools/audit_candidate_independence_v2.py --self-test

After the three V2 files are frozen, verify the actual read-only context using
the published hashes:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B tools/audit_candidate_independence_v2.py --verify \
      --source-sha256 PUBLISHED_V2_SOURCE_SHA256 \
      --protocol-sha256 PUBLISHED_V2_MARKDOWN_SHA256 \
      --inventory-sha256 PUBLISHED_V2_JSON_SHA256

Current correctness: **NOT MEASURED**. Runtime non-delegation:
**NOT ESTABLISHED**. Undefined behavior: **NOT MEASURED**. Relative speed and
memory: **NOT MEASURED**. Holdout: **NOT ACCESSED**. Winner: **NOT SELECTED**.
