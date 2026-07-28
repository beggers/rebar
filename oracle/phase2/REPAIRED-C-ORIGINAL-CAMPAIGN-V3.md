# Freeze a crash-safe, complete rerun of the original C tests

We are building a faster replacement for Python's `re` from scratch. This
document freezes the infrastructure for testing the independently built C
candidate against the original CPython 3.14.6 correctness oracle. It does not
run a candidate, claim compatibility, time matching, or open the holdout.

The frozen oracle contains all 13 original suites, 31,237 counted executions,
and 13 separately named private waivers. The current V22 history has 105 actual
evidence-file owners and 110 authenticated references. This includes the two
genuine failure owners from the previous C attempt: its aggregate process
failed before matching, started zero suite workers, and restored the original
native file. Keep that failed attempt visible. Its matching result is **NOT
MEASURED**.

## What the later run must actually do

The original immutable V9 aggregate and V7 worker retain their historically
correct V21 counts of 103 owners and 108 references. The separately committed
V9 live-context adapter additionally authenticates the current V22 counts of
105 and 110. It fixes the aggregate-to-worker option namespace without changing
the original V9 code, V7 worker, matching implementation, test cases, or
publication formats.

Only a later separately authorized `--run` may activate the existing,
independently authenticated repaired C binary. Its label is exactly
`phase2-v10-live-original-p0`. First authenticate the caller-pinned V3 source,
protocol and contract; the complete released adapter source, protocol and
contract; V22 and the preserved V2 failure; all immutable V9 and V7 pins; the
existing V8 source-build receipt; and the original C target.

The real original target is SHA-256
`075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd`,
device 2064, inode 430300, 149,976 bytes, mode 0755, and one hard link. Begin
the outer recovery `try/finally` before the first possible native mutation.
Authenticate the fresh V5 activation journal and pass every original V9
worker, producer, build, activation, journal and native hash, plus all three
adapter pins and all three outer-controller pins, to the pinned adapter child.

The unchanged V9 aggregate must run all 13 genuinely original V7 suite workers.
Authenticate the full aggregate report and its receipt; then authenticate every
original suite's actual case count, process, matching result, compressed report
and independent receipt. Preserve every mismatch. A real complete semantic
failure is **FAIL**, not a successful candidate and not an infrastructure
failure. An interrupted or incomplete run remains **FAIL** with every observed
record preserved.

If V9 has already restored the native target, authenticate and reuse its exact
existing V5 restoration receipt. Do not attempt to publish a duplicate receipt.
Otherwise recover the same authenticated journal in the outer `finally`.
Before publishing any new campaign archive, verify the original target's exact
bytes, inode and 0755 mode again. Publish only fresh, exclusive, owner-only
archives and durable receipts. Never overwrite the earlier failed campaign.

No source-only verification performs candidate execution, native activation or
recovery, source builds, reference work, network access, performance timing, or
holdout access. Correctness, speed, memory and undefined behavior remain
**NOT MEASURED** until an actual independently recorded campaign.

## Safe source-only gates

Run the synthetic and read-only context gates under exact stable CPython 3.14.6
in ordinary and sterile environments:

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/run_owned_repaired_c_original_campaign_v3.py --self-test

env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/run_owned_repaired_c_original_campaign_v3.py --self-test

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/run_owned_repaired_c_original_campaign_v3.py \
  --verify-frozen-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/run_owned_repaired_c_original_campaign_v3.py \
  --verify-frozen-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

Substitute the independently published complete SHA-256 values. These commands
do not authorize `--run`.
