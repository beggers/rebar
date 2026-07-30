# First-party non-delegation audit V2

This is a frozen, fail-closed policy for six independently owned candidate
families. It does not import, load, compile, execute, qualify, or benchmark a
candidate. The actual candidates have not been run under this policy. Runtime
non-delegation is **NOT ESTABLISHED**.

The preceding source audit admitted two genuine ownership-policy violations:

1. Rust's native bridge exposes a legacy private `bind` capability whose custom
   `__signature__` getter calls `PyImport_ImportModule("inspect")`. Pinned
   CPython 3.14.6 `inspect` imports `re` and `tokenize`; `tokenize` imports `re`
   and executes exactly two import-time `re.compile` calls. The normal public
   Rust `Pattern` methods instead use `PyDescr_NewMethod`, and the adapter's
   `_NATIVE_BIND` alias has no callsites. This is therefore a **forbidden latent
   private native escape hatch**, not proof that ordinary public matching
   delegates to CPython.
2. The Zig adapter imports `ctypes` and invokes `ctypes.CDLL`. The public
   `rebar.py` surface re-exports that adapter. Even when the present file name is
   first-party, a candidate-owned general-purpose dynamic loader and the
   transitive public wrapper violate the stricter production ownership policy.

Conversely, caller-controlled warning formatting can reach
`warnings -> _py_warnings -> linecache -> tokenize -> re.compile`; caller-owned
`enum.EnumType.__signature__` can reach `inspect -> tokenize -> re.compile`.
Those are ordinary host warning/introspection plumbing. They are not attributed
to candidate-owned matching and are not, by themselves, policy failures.

The standalone auditor parses Python sources with `ast`; lexes first-party C,
C++, Rust, Zig, Go, and Fortran without compiling them; proves that the Rust
Cargo manifest and lock contain exactly one package and zero dependencies;
rejects external headers, Zig packages, foreign candidate symbols, computed
native imports, and candidate-owned loaders; and reads ELF dynamic sections,
`DT_NEEDED`, search paths, and dynamic symbols directly without invoking an
external tool or loading a shared library. C/Zig/Rust link ownership accepts
only the enumerated first-party engine and ordinary system C-runtime libraries.

The **only** frozen source owners are:

- `tools/audit_candidate_runtime_non_delegation_v2.py`
- `oracle/phase2/RUNTIME-NON-DELEGATION-V2.md`
- `oracle/phase2/runtime-non-delegation-v2.json`

`--self-test` installs a physical effect wall and uses only synthetic,
in-memory Python/native source, dependency manifests, ELF binaries, private
getter reachability controls, and adversarial path fixtures. It opens no file.
`--verify-source` opens exactly those three explicitly pinned owners through
descriptor-relative, no-follow reads. Neither mode reads candidate sources,
candidate binaries, pinned stdlib files, archives, evidence, private data,
holdout cases, Git metadata, or benchmark files. Both prevent imports after
their effect wall is installed, subprocesses, candidate execution, native
loading, network, clocks, threads, audit-hook installation, and workspace
mutation.

Use the pinned CPython, both normally and under an empty environment:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/audit_candidate_runtime_non_delegation_v2.py --self-test

env -i /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/audit_candidate_runtime_non_delegation_v2.py --self-test

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/audit_candidate_runtime_non_delegation_v2.py --verify-source \
  --source-sha256 PUBLISHED_SOURCE_SHA256 \
  --protocol-sha256 PUBLISHED_PROTOCOL_SHA256 \
  --contract-sha256 PUBLISHED_CONTRACT_SHA256
```

The same exact verification command must also pass under `env -i`.

`--audit` is **root-agent-only**, and can run only after the root agent has
independently verified that the exact source was committed and pushed. It
requires `--root-authorized --pushed-source-sha256 SHA256`. It performs a
read-only first-party source, pinned-stdlib, and ELF inspection. It does not
execute a candidate or compiler. The current truthful expected result is
**FAIL** for Rust's private bridge escape hatch, Zig's candidate-owned
`ctypes` loader, and the transitive public `rebar.py` facade.

`--run-runtime-audit` is deliberately unimplemented, always fails closed, and
starts no candidate. Any genuine future runtime instrumentation or campaign
requires separate root-agent authorization and a separately reviewed freeze.

Runtime non-delegation: **NOT ESTABLISHED**. Public Rust matching delegation:
**NOT PROVEN**. Candidate execution: **NOT RUN**. Candidate qualification:
**NOT ESTABLISHED**. Holdout: **NOT OPENED**. Performance: **NOT MEASURED**.
Winner: **NOT SELECTED**.
