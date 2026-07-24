# Native ownership and Python-compatible match objects

Status: **NOT RUN.** The version-eight source and no-delegation audits,
the repaired candidate builds, refreshed correctness proofs, and full
correctness campaigns have not passed. Speed, memory, holdout
performance, candidate rankings, and a winner are **NOT MEASURED**.

## The actual failure

The complete, unchanged Python 3.14.6 edge oracle ran all 223,198
observations in all 49 frozen categories against each genuinely owned
Rust, C, and Zig implementation. All three genuine failures remain
complete and separately preserved:

```text
candidates/evidence/rust-v7-edge-oracle-rust-postfinal-locale-v7-first-failure.json.gz
3ffdb21d10f40deabd70fa1f408fa38ff2b027a2d269c4b75e607a05cefde3b8
16 actual failures; 223,198 observations; 49 categories

candidates/evidence/rust-v7-edge-oracle-vm-postfinal-locale-v7-first-failure.json.gz
2cce7c26d2487c8e400d2fd6b8cfbc81d4b734b08f7a8f356def910a9cbb385c
33 actual failures; 223,198 observations; 49 categories

candidates/evidence/rust-v7-edge-oracle-zig-postfinal-locale-v7-first-failure.json.gz
5fa7283942994139d531593cc1bdf25f5da48f6de424d7604ce2ce569100788a
16 actual failures; 223,198 observations; 49 categories
```

Each implementation has the same 16 actual public match-identity
failures. Its genuine native match advertises its implementation
module instead of the Python-required `re.Match`. This changes the
visible module, representation, signature error, weak-reference
error, and read-only match errors.

The C implementation also has 17 additional `groupindex` errors: its
native pattern descriptor reports `candidates._vm_native.Pattern`
where Python requires `re.Pattern`. This is an actual 33-failure C
result, not another Rust or Zig result. Every failure is real;
none indicates an oracle defect or a passing candidate. Preserve all
65 original rows, the original seed `2026072329`, all three full
denominators, and all three immutable archive digests.

The distinct, unchanged first campaign failure is also preserved:

```text
candidates/evidence/rust-v8-rust-postfinal-locale-v7-sealed-campaign-first-failure.json
62aba93fa8bdd6df7be93199aea6f58be7b24c095750c520179e96b98084b75a
```

The unchanged original edge script is:

```text
tools/rust_v7_edge_oracle.py
fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca
```

Do not change, skip, waive, replay as a pass, or reduce this oracle.

## Correct ownership rule

A public type's display name is not evidence that another engine
performed its work. For each independently implemented Rust, C, and
Zig family, prove all three properties in an actually guarded,
isolated native matching process:

```text
public.Match is owned_native_bridge.Match
type(actual_native_match) is public.Match is owned_native_bridge.Match
type(actual_native_match).__module__ == "re"
type(public.compile(text_pattern)) is public.Pattern
type(public.compile(bytes_pattern)) is public.Pattern
public.Pattern.__module__ == "re"
public.Pattern.__name__ == public.Pattern.__qualname__ == "Pattern"
```

Rehash the actual five native ELF files, verify their real in-process
mappings before and after matching, verify all 12 owned source files,
and preserve three separate parser, compiler, and matching pipelines.
The standard-library matcher, `_sre`, another candidate, an external
matcher, and every unauthorized dynamic-library loader remain blocked.
A public name of `re.Pattern` or `re.Match` must never be used to
import Python's `re` module or to infer native ownership. Match
ownership is proved by the actual bridge-exported object. Pattern
ownership is proved independently by the actual public candidate
export, actual compiled-object identity, its own guarded native
matching pipeline, and the rehashed mapped native binary. Do not
replace these actual identity checks with a hardcoded descriptor
owner or an importable display string.

For both string and bytes subjects, actually compare:

- The match span, matched text, and exact Python `re.Match` display.
- Class and bound-method signature errors.
- Weak-reference and read-only `lastindex`, `lastgroup`, and `regs`
  errors.
- The native pattern descriptor's exact read-only `groupindex` error,
  including Python's public `re.Pattern` owner.
- All original 16 per-family standard pickle and generic-alias cases,
  for both public types, both argument types, and all four original
  pickle protocols.

Changing the public module to `re` can expose a genuine pickle global
identity collision: ordinary pickle may resolve Python's actual
`re.Match` instead of the owned native match class. Record every real
round-trip result. Never drop the 48-case denominator, install a
standard-library matcher, forge an importable owner, or claim a failed
pickle check passed. If reconstruction cannot satisfy both the
unchanged Python behavior and native ownership, preserve and report the
actual failure.

## Immutable historical results

The following version-seven results genuinely described the earlier
build. They are historical, not evidence that the repaired native
public types pass the unchanged oracle:

```text
tools/postfinal_from_scratch_audit_v7.py
defa306e47a0d325af7d4c7fabb54324f6cb6d4653a494c46846838f5e2cf487

candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json
efae1f94fb06a1eabbab352794410c4d8e20a78202dcbf769b08ff9c7cee130a

tools/postfinal_no_delegation_audit_v7.py
9283457064f32658747b449c4ee6ebd20ca7cc7dc442ce03ece6b02896cff4e4

candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json
1f71caac01bffdffbf7ffdc2e21a9aa8d6936c452051cbdaa4c90ac67010fd34
```

They incorrectly treated the implementation's display module as its
proof of native ownership. Neither historical report may be edited,
rerun as a repaired-build audit, or relabeled as a version-eight pass.

## Source-first audit sequence

Freeze, commit, and push these independently authored controllers and
this protocol before executing any actual candidate:

```text
tools/postfinal_from_scratch_audit_v8.py
tools/postfinal_no_delegation_audit_v8.py
candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V8.md
```

Run the source-only, candidate-free malicious controls first:

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_from_scratch_audit_v8.py --self-test

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_no_delegation_audit_v8.py --self-test
```

These checks must not run a candidate, create a report, read a
benchmark, materialize a holdout, start a process, or sample a clock.
Synthetic passes never qualify a production engine.

Only after the real native implementations have been repaired and
rebuilt, run and separately record each actual audit:

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_from_scratch_audit_v8.py --gate

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_no_delegation_audit_v8.py --gate
```

The only authorized new report paths are:

```text
candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V8.json
candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V8.json
```

Open each destination exclusively with no symbolic-link following.
Write and synchronize the complete genuine `PASS` or genuine `FAIL`
report once. Never overwrite or retry a report. A failed actual audit
blocks renewed correctness proofs and full campaigns; it is not a
benchmark and cannot qualify a winner.
