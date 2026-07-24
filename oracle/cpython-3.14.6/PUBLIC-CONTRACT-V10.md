# Full Python regex compatibility with isolated signature inspection

Status: **Additive design and candidate-free checks only.** Two new
independent Python reference runs and the Rust, C-VM, and Zig comparison
are **NOT RUN**. Performance is **NOT MEASURED**.

Stage ten preserves every one of the **3,584** public Python obligations,
including all **256** public-module and real-signature cases. It skips
reserved stage nine. Nothing in stage seven, stage eight, their evidence,
or the three candidates is changed.

| Unchanged requirement | Cases |
| --- | ---: |
| Public names, exact callable signatures, flags, and errors | 256 |
| Invalid expressions, warnings, and flag combinations | 256 |
| Every byte under both real locales and locale changes | 1,024 |
| Bytes, contiguous and noncontiguous buffers, and released views | 256 |
| Copying, serialization, hash behavior, groups, and weak references | 256 |
| Replacement callbacks, nested matching, and scanners | 256 |
| One pattern shared by actual groups of four and eight threads | 256 |
| Bounded positions, long inputs, Unicode, and lone surrogates | 1,024 |
| **Total for each independent implementation** | **3,584** |

The unchanged deterministic matrix is
`0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db`.
The original matrix seed and domain remain `2026072437` and
`rebar/python-re/public-contract/v7`. Stage ten independently authenticates
its own frozen source, this protocol, and observations in the
`rebar/python-re/public-contract/v10` domain.

## Preserve both actual failures

The genuine stage-seven Python-versus-Python failure remains
`765e635745a7e332a1bd22426065c43fd52036d013add0d88d840d8fde1121e0`.
All **32** process-specific pattern-hash differences and both complete
Python runs remain authenticated.

The genuine stage-eight Rust failure remains
`f509cedf5f58d1c211b63177fb843bfba3dc0b132469a392df43a9c802e323b1`.
The Rust worker completed all **3,584** obligations under the full native
and Python anti-delegation guards. Its other **3,328** records matched
standard Python. Every one of the **256** public-surface mismatches was
the same real `ImportError`: the test harness attempted to import
Python's `inspect` after blocking imports of Python's matcher. The
historical experiment is a **FAIL**; no candidate is declared passing.

The pinned complete, genuinely successful stage-eight Python self-oracle
remains
`efcf0f661363e9032ce8c0afe7ea06a4762b783eec4c4ee6ec7c7059c14994df`.

## Inspect signatures in a completely separate process

Python's genuine `inspect.signature` is retained. Signatures are not
guessed, recreated, hardcoded, mocked, or removed. Warming the inspector
inside a production worker is unsafe: Python's tokenizer keeps already
compiled matcher objects, including `cookie_re` and `blank_re`.
Replacing those objects with Python proxies or hiding them in live
frames is also insufficient. Stage ten uses **two genuinely distinct
operating-system processes for each candidate**.

The first process is an isolated public-metadata observer. It
authenticates the pinned Python interpreter, frozen stage-ten source,
complete previous correctness proofs, candidate identity, owned native
libraries, and all original engine guards. It imports the real Python
signature inspector only in this metadata-only process. The unchanged
frozen evaluator observes all **256** public names, values, classes,
list entries, and genuine callable signatures. A source-bound call
profile forbids candidate matching, direct use of cached Python
patterns, native matching calls, profiler replacement, and monitoring
disabling. The process returns only bounded, canonical, independently
authenticated public metadata.

The second process is a newly started matching worker. Neither
`inspect` nor `tokenize` is imported in this interpreter. No tokenizer
pattern, regex capability, proxy, matcher object, secret frame, or
metadata-process Python object is transferred. The parent passes only
the source- and family-bound public observation record. The matching
worker checks all **256** record identities and their digest, recompiles
the public names, flags, classes, and list entries locally, and uses the
independently measured genuine signatures solely for signature fields.
It then runs all **3,584** unchanged obligations against its own real,
independently mapped native engine. Source, family, native fingerprints,
metadata digest, and all public cases are verified again after matching
to reject candidate mutation.

Thus Python's tokenizer is confined to the non-matching metadata
process. No production candidate can reach an inspector, tokenizer,
cached Python matcher, imported `re`, `_sre`, foreign engine, or another
family through process state, a frame, or an alias.

All existing cached-alias poisoning, cross-family import blocks,
independently owned and mapped engines, and all five blocked dynamic
loader entry points remain mandatory. Both genuine private locales,
all actual threads, strict reversible Unicode, and six exclusively
created success-or-failure destinations remain unchanged in strength.

## Exclusive new evidence

```text
oracle/cpython-3.14.6/evidence/public-contract-v10-self-oracle.json
oracle/cpython-3.14.6/evidence/public-contract-v10-self-oracle-failures.json
candidates/evidence/python-re-universal-public-oracle-v10-all.json
candidates/evidence/python-re-universal-public-oracle-v10-rust-failures.json
candidates/evidence/python-re-universal-public-oracle-v10-vm-failures.json
candidates/evidence/python-re-universal-public-oracle-v10-zig-failures.json
```

First run the side-effect-free synthetic checks:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage10.py --self-test
```

Commit and push the exact stage-ten source and protocol before running
either real command. Run the two standard-Python workers first. Only a
complete, passing, source-bound Python self-oracle can authorize the
three guarded native candidate workers:

```sh
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage10.py --self-oracle

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage10.py --candidate all
```

All benchmarking, expanded holdout cases, memory measurements,
rankings, speedups, and winners remain **NOT MEASURED** until every
correctness gate has actually passed.
