# Test the actual public `import rebar as re`

Status: **The source-only verifier passes. The existing public entrypoint
fails. No candidate is qualified; no winner is selected.** This chunk freezes
the observation. It does not fix, import, install, or publish `rebar`.

The original correctness baseline remains exactly **31,237 cases in 13
suites with 13 named private waivers**. The existing **50** independently
referenced callable-signature cases remain separately counted. The **32**
source-only entrypoint observations in this document are a further separate
matrix. None is added to either older denominator.

The independently canonical 32-observation matrix has SHA-256
`f67f8d4d62f9939c94250ad2e4df55b14df013df7212aa66930ecc3a772d2a58`.

## What the real entrypoint does

The existing, tracked `rebar.py` has SHA-256
`289769bd637ea525ae7e71d263377e15c0f394ba20619c11b98e266f57fcc34f`.
Its actual source describes the unmeasured module as a “Measured” replacement
and immediately re-exports `candidates.zig_candidate` before any qualification
check.

The Zig source has SHA-256
`2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862`.
The original Python source and Zig agree on the exact ordered public
`__all__`. `DEBUG` and `Scanner` are intentionally direct module attributes,
not wildcard exports, and the existing shim correctly restores them. Do not
report those correctly preserved observations as failures.

The public module-version failure is genuine. Python publishes
`re.__version__ == "2.2.1"`. The Zig source also defines `"2.2.1"`, but
its wildcard list correctly does not include `__version__`. The shim never
explicitly imports the version. Therefore `rebar.__version__` is **MISSING**
by Python's source-defined wildcard semantics. This contradicts an original,
already-required module-version obligation.

Source analysis also proves that importing the Zig candidate would first
import its `_zig_bridge` extension and then run `_Native()`, whose
constructor calls `ctypes.CDLL` on the owned `_zig_probe.so`. Those are
**two potential native effects of an actual future import**. This source
freeze imports neither module and loads **zero** native libraries. Potential
effects are never counted as actual effects.

The existing `pyproject.toml`, SHA-256
`7d50e8c6c2bc76a0e3ddcac6b5f157b013bcfd76944fdeb2c1c81e0181ae7825`,
sets `[tool.uv] package = false`. A correctly built and installed public
artifact has **NOT BEEN MEASURED**. A project distribution name is not
assumed to equal its Python import name.

The preserved historical Zig result has **1,764** differences and is
**FAIL**. It is an independently written source design, not a qualified
replacement. There are **zero** qualified families. The observed entrypoint
is **FAIL / UNQUALIFIED_ZIG_PROTOTYPE**, even though this source-only verifier
correctly returns **PASS** for detecting and preserving the failure.

## Source-only isolation

The pinned interpreter is exclusively:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016
```

The verifier deliberately does not import `json`, `tomllib`, `argparse`,
`pathlib`, or `dataclasses`: on the pinned interpreter those modules can
indirectly load Python `re` and `_sre`. It uses `ast`, `hashlib`, `os`,
`stat`, `sys`, and a small, bounded, duplicate-key-strict JSON decoder. Its
strict project reader supports only the exact needed TOML subset. The
regular-expression modules and every candidate must remain absent from
`sys.modules` before, during, and after both source-only modes.

A real, fail-closed Python audit hook is installed after the clean bootstrap
and before reading any frozen source owner. It allows only the exactly
pinned owner paths as read-only files and bounded source-only AST parsing.
It physically blocks all later module imports, unlisted or writable files,
execution, native loading, process creation, networking, and explicit clock
events. The self-test actually attempts forbidden matcher, candidate,
archive, native, execution, process, network, and write operations and
proves the hook rejects each before its underlying effect can occur.
Blocked hostile attempts are reported separately from actual effects.

Read-only context authenticates every exact owner, including all four files
of the pushed **version-44** overview, all three exact owners of the pushed,
repaired Rust V7 source freeze, the current independent source inventory,
the separately durable 50-signature Python reference receipt, and the pinned
standard-library source. The Rust source freeze is not a candidate matching
result. Read-only verification authenticates **20** exact owners and preserves
the actual failed Rust
controller, its one historical build-archive effect, the omitted effect
ledger, zero started Rust matching workers, and the authenticated lower
bounds of **166** evidence owners and **171** history references. It does not
open the historical archive or claim those lower bounds are a full
repository census.

Both modes perform zero candidate imports, native loads, reference or
candidate processes, archive reads or inflation, writes, network requests,
clock samples, hidden-case reads, or holdout reads. The final **4,194,304**
examples remain **NOT FROZEN, NOT GENERATED, and NOT OPENED**.

## A future winner must fail closed

This source-freeze chunk must not alter the existing shim. A later,
individually committed feature may make a no-winner public entrypoint fail
closed without importing the standard library matcher, another regex
package, or an unqualified candidate. It must leave the separate
`candidates.*` research modules independently runnable.

Actual activation of a public winner is allowed only after at least three
genuinely different first-party families independently pass the exact
original **31,237** cases and their own separate **50** signature cases.
The chosen family must also pass actual public and installed imports,
ordered wildcard exports, `__version__`, `DEBUG`, `Scanner`, runtime
no-delegation, native provenance and safety, and the frozen fair performance
and statistical winner gates. No fallback, premature winner, or changed
denominator is permitted. Nothing in this source freeze runs those gates.

## Reproduce the two source-only modes

Independently hash the exact three owners:

```text
sha256sum tools/verify_public_entrypoint_import_v1.py \
  oracle/phase1/P0-PUBLIC-ENTRYPOINT-IMPORT-V1.md \
  oracle/phase1/p0-public-entrypoint-import-v1.json
```

Substitute those three actual full hashes for `SOURCE_SHA256`,
`PROTOCOL_SHA256`, and `CONTRACT_SHA256`:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/verify_public_entrypoint_import_v1.py --self-test \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin LC_ALL=C \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/verify_public_entrypoint_import_v1.py --self-test \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/verify_public_entrypoint_import_v1.py --verify-frozen-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin LC_ALL=C \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/verify_public_entrypoint_import_v1.py --verify-frozen-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

**Source-freeze gate: PASS. Actual public entrypoint: FAIL. Candidate
qualification: zero. Speed, memory, undefined behavior, and runtime
non-delegation: NOT MEASURED or NOT ESTABLISHED. Holdout: NOT OPENED.
Winner: NOT SELECTED.**
