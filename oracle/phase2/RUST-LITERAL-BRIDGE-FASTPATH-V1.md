# First-party Rust literal bridge acceleration V1

Status: **SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN.**

The exact current Rust engine already passes all **31,237** original Python
checks and all **10,434** wider checks. Its measured, fully correct public
build runs at **1.2424347186648022× Python** across **416** public cases;
**252** cases are faster, **164** slower, and all **14** slowdowns exceeding
20% remain preserved. Runtime independence and hidden-test speed remain
**NOT MEASURED**. This experiment does not change those historical results.

Ten of those 14 severe slowdowns share one real implementation problem: the
Python-facing native bridge handles plain literal searches and collections
itself using generic substring search. Consequently, the independently frozen
Rust final-byte acceleration never runs on those calls. The exact affected
public observations are:

```text
rust-public-profile.v1.0001  rust-public-profile.v1.0010
rust-public-profile.v1.0023  rust-public-profile.v1.0024
rust-public-profile.v1.0209  rust-public-profile.v1.0212
rust-public-profile.v1.0218  rust-public-profile.v1.0221
rust-public-profile.v1.0231  rust-public-profile.v1.0232
```

The remaining four substantial losses remain visible and uncorrected by this
focused experiment: `.0110`, `.0119`, `.0156`, and `.0342`. No performance
improvement is claimed before an independently gated real measurement.

The experiment derives exactly one new first-party C bridge from the frozen
complete, compatibility-tested bridge:

```text
bridge parent   f6253fbecc76b64750a22dc9393180d3ea6e3f2e29aace006c0479543e94342e
Rust engine     7ec7dc9815bec10c3149123ddc5045f575c3cd45731531bd81e0b888362a9136
speed receipt   db9288ea7c0a00e0c702acb7520e74482f8fb3c90cccee8f6e247f592811f2b3
speed summary   7366a81a3fa1352cb6e8a165d5c45871f0081bda7e5c392e07d7bbf3f3a4cfef
target          candidates/rust/variants/literal_bridge_fastpath_v1/py_bridge.c
```

The replacement is an independently implemented exact substring finder, not
a regular-expression library or wrapper. It searches a necessary literal
byte with the ordinary C `memchr` primitive, verifies the complete bounded
candidate with `memcmp`, and returns the first genuine match. On sufficiently
large windows, a small bounded sample chooses whichever of the first and last
literal bytes occurs less frequently; this keeps repeated final-byte patterns
safe. No additional Python/Rust crossing occurs.

Only nonempty, capture-free, case-sensitive literals with at least two bytes
use the shortcut. Byte strings, byte-oriented buffer exporters, and compact
one-byte Python Unicode strings are supported. Two-byte and four-byte Unicode,
empty or single-character literals, Unicode conversions, matching/fullmatching,
all position bounds, and every exceptional path retain their original code.
Search and find-all preserve leftmost and non-overlapping order. Buffer
acquisition and release, callbacks, result ownership, and exact Python public
objects remain unchanged.

An independent exhaustive bounded model covers all windows, starts, ends,
matching modes, repeated collection, empty and one-byte exclusions, all byte
values including zero and 255, Unicode-width rejection, case flags, groups,
and both adaptive anchor choices. It imports no matching engine, runs no
candidate, starts no subprocess, and reads no hidden test. Immutable public
receipts preserve all 14 previous regressions and the exact ten targeted IDs.

A permanent deny-default source wall authenticates every permitted owner by
exact device, inode, owner, mode, link count, size, and SHA-256. Source gates
cannot open native libraries, private roots, raw paired trials, archives,
proposal metadata, hidden cases, or any writable descriptor. Only root may
materialize one fresh `0700` variant directory containing one exclusive,
no-follow `0600` C source file after the complete freeze has been committed
and pushed.

Ordinary and sterile gates:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_literal_bridge_fastpath_v1.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_literal_bridge_fastpath_v1.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Repeat both commands under `env -i PATH=/usr/bin:/bin LC_ALL=C`.

Root-only source materialization after committing and pushing all three files:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_literal_bridge_fastpath_v1.py \
  --apply --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256 \
  --frozen-commit PUSHED_COMMIT --pushed-commit PUSHED_COMMIT \
  --root-authorized --frozen-committed-pushed
```

Actual corrected compatibility, speed, memory, confidence, undefined
behavior, live non-delegation, candidate qualification, and the final
comparison all remain **NOT MEASURED** until separate authorized runs.
