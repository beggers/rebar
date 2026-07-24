# Python regular-expression compatibility

Status: **SOURCE-ONLY DRAFT. REFERENCE NOT RUN. CANDIDATES NOT RUN.** Speed,
memory, benchmarks, an expanded performance holdout, and a winner are
**NOT MEASURED**. Source-only controls cannot qualify an implementation.

The goal is to establish whether an application using Python's public
`re` module can safely use an independently implemented replacement.
This is an additive correctness contract, not a performance experiment.
It imports no preceding public-surface oracle and treats no draft,
historical campaign, synthetic record, or absent report as a pass.

## Start from the actual Python baseline

Pin the actual CPython 3.14.6 upstream source:

```text
oracle/cpython-3.14.6/test_re.py
879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2
```

Independently reconstruct its real source-ordered method matrix using
the exact Python AST of every original test. Require the frozen matrix
`5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a`.
There are exactly 165 original methods: 152 public methods and 13
methods in the two explicitly named Python-private classes. Each
actual release-build reference has 151 passes and the one unchanged
`ReTests.test_memory_leaks` private debug-condition skip. No public
method is waived; private debug-build coverage is **NOT RUN**.

Authenticate the complete, actually published, candidate-free Python
versus Python reference:

```text
oracle/cpython-3.14.6/evidence/postfinal-locale-v5-self-oracle.json
3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916
```

Revalidate both individually retained original reference roles, every
source-ordered original method identity and AST hash, all 403 upstream
corpus entries, all 11 external fixtures, the genuine 26-file support
tree, both actual two-gibibyte inputs, the 36-gibibyte requirement, the
unchanged CPU and fork tests, and both genuine original private
locales. Do not read a candidate audit or candidate proof, import an
engine, or require an old campaign to validate this baseline.

The frozen original version-five source and protocol are:

```text
tools/postfinal_cpython_locale_oracle_v5.py
9a4f2ac53617fb91e498ae2935bde622417921415af255e390668f69ba908730

oracle/cpython-3.14.6/POSTFINAL-LOCALE-V5.md
1329cf9c8e36391af134b2fb2b212e71067ace736b282dacd2a6c90233384840
```

## Independently freeze the real public calls

The full generator and evaluator are self-contained in
`tools/python_re_public_surface_oracle_stage17.py`. No earlier
public-surface source, protocol, evidence, or campaign is opened or
imported. Its exact case and actual behavioral-input fingerprints,
independently derived by the genuinely file-free pinned source-only
control, are:

```text
Seeded case matrix
7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa

Actual semantic stimuli
8c1a4fd434af5fb1ea0dcd1aa3faaa06b07e7d186ca52c1593575eff93b4d7da
```

A frozen matrix is a test specification, not a reference result.

The standalone source-only control actually reconstructs **43
cohorts**, **32 real behavioral inputs per cohort**, **640**
source-local base cases, **736** independently seeded additional
cases, and **1,376 distinct complete case inputs**. It independently
checks every case identity, expression, subject, variant, cohort, and
semantic fingerprint. The base case matrix is
`748ef9556f3202678d42ff47a4d55ce2cf965ed16026b5b62ed1c1d75937aeb7`;
its actual base stimuli are
`82856f5f3782ddd80caab6b420749565c1c225405bccad5850400bc00d327cbe`.
Both are generated from this source alone. An old source or old
protocol is never read or required. Changing only a case label never
creates a new matching test.

The original public surface contains 31 ordered exports, 13 public
compiled-pattern members, and 14 public match members. `Scanner` and
`DEBUG` are genuine public attributes but do not occur in `re.__all__`.
Test every export and member, every public alias, string and bytes
scanners, public debug output without relying on private opcode text,
matching windows, genuine warnings, Unicode, callbacks, buffers,
caching, and replacements.

The independently generated additional checks require actual calls,
not merely the existence of a property:

1. Really compile and match with unknown, high, mixed, inverted, and
   indexable flag values. Preserve the actual result or actual public
   exception.
2. Round-trip actual compiled string and bytes patterns under every
   supported pickle protocol. Check cache identity, structural
   equality, hash, purge, pattern weak references, and actual pattern
   and match copying.
3. Hold a real mutable buffer inside a live iterator, scanner, or
   match; record the true resize error while the export is live and
   the genuine outcome after release. Include empty, typed, strided,
   contiguous, and already released buffers.
4. Exercise valid named Unicode character escapes, non-ASCII and
   astral capture names, named replacements, byte-pattern errors,
   unusual Unicode case folding, ASCII flags, and word boundaries.
5. Compile one genuine locale-sensitive bytes pattern and switch its
   actual `LC_CTYPE` between freshly available ISO-8859-1 and UTF-8.
   Validate each real encoding, re-use the same compiled object,
   check cache and invalid flag combinations, and always restore the
   original locale. The temporary private locales from the completed
   version-five workers have already been destroyed: independently
   provision actual new locales or stop. `C.UTF-8` is not ISO-8859-1.
6. Preserve every scanner or replacement callback invocation, span,
   token, nested result, and preceding side effect when a real
   callback raises. Never retain just the final exception.
7. Record exact public deprecation and character-set warning
   categories, messages, filenames, source lines, and caller origin;
   check actual positional `sub`, `subn`, and `split` calls.
8. Check mapping identity and immutability, cached match
   registrations, every genuine public pattern-error attribute and
   pickle behavior, and the actual `typing` origin, arguments,
   parameters, rejection behavior, and all genuine generic-alias
   pickle protocols.
9. Report a separate-interpreter run as **NOT RUN** until an
   independently authenticated engine guard can actually be
   installed inside the new interpreter. Never import an unguarded
   engine or pass an unavailable interpreter as tested.

Each real row retains its original case identity, actual full
behavioral-stimulus SHA-256, and complete returned value or actual
exception. Two independently started genuine standard-library
workers must produce and preserve all individual records. A mismatch,
crash, missing fresh locale, timeout, missing buffer lifetime, or
uncaught exception is a failure, not an approximation or a waiver.
All **736** independently added rows must return from their outer
probe. Their intentionally tested public exceptions are individually
recorded inside that successful observation; an infrastructure
exception cannot be accepted merely because two Python workers agree.
Each worker must genuinely pass all **64** locale cases and their
**192** actual encoding transitions. Recheck each transition and
restored state independently when validating the full records.

## Candidate checks are separate and fail closed

Only after the frozen V17 source and protocol are committed and
pushed, both genuine public references agree, and their complete
records are independently published can candidate validation begin.
Require the independently published actual V17 reference hash as
`--reference-sha256`, and validate every complete record from both
real workers before opening a candidate ownership audit.

Require both actual, successful, independently authenticated V10
native-owner audit reports and their genuinely frozen source and
protocol hashes. Also require each family's own actually qualified
current-build edge and deep archives:

```text
tools/postfinal_from_scratch_audit_v10.py
0c4d3f07bb51b0ce5ddc148810cb157d21067ddb07b578d3a793aaac5c671505

tools/postfinal_no_delegation_audit_v10.py
885168bd6df92ac9cabc8fc78a8389ee487f0be8d3c7fe67a393e984011b8d95

candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V10.md
902bc095d08331089dcc1d1d11233747438a0cacb0cf1057ae41a2474bde2fa6

tools/postfinal_current_build_proofs_v10.py
74209ed4e59351802c7dae3af3d21a03a23c0e464e340c3bf29eeddf8337d5b9

oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V10.md
2eb5b5c0828059b1d02d306e9cf6f05e90d30575e3a386c20f83582456de1ae0
```

These are real source and protocol hashes, not execution or report
hashes. They are neither read nor required in Python-reference or
source-only mode. The exact independently owned archive paths are:

```text
candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v10-qualified-pass.json.gz
candidates/evidence/rust-v7-edge-oracle-vm-postfinal-current-build-v10-qualified-pass.json.gz
candidates/evidence/rust-v7-edge-oracle-zig-postfinal-current-build-v10-qualified-pass.json.gz

candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-CURRENT-BUILD-V10-PASS.json.gz
candidates/audits/RUST-V8-DEEP-CONTRACT-C-POSTFINAL-CURRENT-BUILD-V10-PASS.json.gz
candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-CURRENT-BUILD-V10-PASS.json.gz
```

The real archive hashes must be supplied externally after the actual
reports exist. Use the actual unchanged V10
`audit_v10_reports` and strict base-report validator to check all
three workers, all 12 owned source files, all five actual native
binaries, all genuine matcher guards, all original pickle checks,
and the exact real V10 source/report identity. Validate the complete
edge and deep archives using their actual original complete-suite
validators, exact candidate family, current native/source snapshot,
seed, denominator, and all actual failure records. A report saying
`PASS`, a gzip signature, a guessed hash, or a different family's
archive is never sufficient.

Even an actual full V10 audit and real original edge/deep archive do
not retain durable, independently authenticated matching-owner
observations before and after the production of each archive. They do
not prove a public V17 worker is independently guarded. There is no
invented all-family V10 owner-proof report. Actual candidate
matching remains **BLOCKED** before candidate import until a genuine
durable per-family V11 owner proof and an independently reviewed,
current-build public-worker guard actually exist. This draft never
treats an unexecuted candidate as compatible.

## Source-only reproduction

Run only after the two additive draft files are ready:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/python_re_public_surface_oracle_stage17.py --self-test
env -i PATH=/usr/bin:/bin /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/python_re_public_surface_oracle_stage17.py --self-test
```

The control must perform at least 150 separately named, actual
in-memory source and poison checks with zero candidate imports, regex
matches, worker starts, source or evidence reads, writes, clock
samples, entropy draws, global locale changes, benchmark accesses,
and holdout reads. It must preserve actual **NOT RUN** and **NOT
MEASURED** status.

No reference worker, candidate worker, performance experiment,
benchmark, holdout, fixture, report, release, deployment, commit, or
push is authorized by this draft.
