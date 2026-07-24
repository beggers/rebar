# Read the complete regex results without weakening their safety checks

Status: **Source-only.** This reader never runs a Python reference, native
candidate, audit, benchmark, or final test. It never rewrites a result.

The genuinely complete stage-seventeen candidate result is **20,220,593
bytes**, larger than the original reader's 16 MiB safety limit. Its size
comes from retaining all **10,752** actual candidate observations, both
complete Python reference streams, and both actual Python worker reports.
Do not remove observations, change the existing reader, increase the limit
for other files, or infer compatibility from a truncated report.

Use a new, fixed maximum of **33,554,432 bytes (32 MiB)** for exactly these
two already-published evidence files, and no others:

```text
oracle/cpython-3.14.6/evidence/public-contract-v17-self-oracle.json
11,556,111 bytes
de1272f7c3681402b8787ea2a53de8228ef0341760505dc052c52b023e3d3c3d

candidates/evidence/python-re-universal-public-oracle-v17-all.json
20,220,593 bytes
255644709afe8fa8ce41cefcfd029b7f865bbcd0314d528902bb5a56d52aa288
```

The actual producer and protocol are independently frozen:

```text
tools/python_re_universal_public_oracle_stage17.py
9e5ca448ecc6a6de8745b0c84cf5b4ae5d92cd098914731a4047d45e6ce1b6d4

oracle/cpython-3.14.6/PUBLIC-CONTRACT-V17.md
8773d4fd2d0b9f04808b2a22358a233b44abfd892862aaaf224cd0d607081520
```

Retain the real preceding failure report
`cb71e1a44549c7c76c3bf08900e6107d2b49e789e5002afc725d1e9df0c92880`.
Its durable plain-JSON hash is `0d6a74b1f923436c14569bfdd84431e4251f3bb8dd3129fbbcaf82a47f906b94`.
The original double-encoding validator instead produced
`7a3bed83093800085fe1bd084820108142929f60e37632b3c24a02c6a4584d72`.
Never treat that first failed run as successful.

Open only an exact allowed relative path through its separately checked
repository-root directory descriptor. Deny traversal, absolute paths,
symlinks, nonregular files, changed files, and an unpinned hash. Open both
the directory and file with `O_NOFOLLOW` and `O_CLOEXEC`; check the regular
file descriptor and its actual size before reading. Stream at most 32 MiB
in bounded chunks, hash the bytes actually read, and compare the original
and final file metadata.

Reject malformed UTF-8, duplicate JSON keys, nonfinite JSON numbers,
trailing bytes, missing or extra newlines, and any JSON whose exact plain
canonical bytes do not equal the original file. Authenticate the actual
V17 provenance and call both genuine, context-free reference and
three-candidate validators on the parsed results.

Expose exactly these interoperable entry points:

```python
read_exact_evidence(relative, *, expected_sha256) -> (document, sha256)
read_stage17_self_and_all(
    *, expected_self_sha256, expected_all_sha256
) -> (reference_document, all_candidates_document)
validate_v17_evidence() -> validated_evidence_bundle
```

The validated bundle exposes the actual V17 current provenance, both
complete documents, both hashes, both byte sizes, the fixed bound, and
explicit zero-worker and zero-performance flags.

First run only the candidate-free, file-free malicious-input self-test:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage17_evidence.py --self-test
```

Commit and push this exact reader and protocol before any downstream
controller consumes the large result. Rankings, speed, memory, the hidden
holdout, and a winner remain **NOT MEASURED**.
