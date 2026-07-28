# Freeze the real Go Unicode group-name correction

This freezes one observed, first-party Go source correction. It does not apply
the correction, build Go, import a candidate, run Python's tests, measure
performance, or qualify an engine.

## The actual Python failure

The original independently built Go candidate genuinely failed the frozen
CPython 3.14.6 correctness campaign. All 13 original groups ran. One group
passed its 128 cases; eight groups recorded 4,518 matching differences. Four
further groups failed to return valid complete test results. The
changing-buffer group exceeded the frozen 64 MiB output limit and was
intentionally stopped by the test harness. This is not an independently
demonstrated Go crash, timeout, or matching difference.

The original Go failure archive has SHA-256
`af971b3387382862ebf084b1d48ff0a21f37084cb234fd9e776d721b3ca5aae0`
and is 9,139,062 compressed bytes. A single, already completed bounded
investigation read 77,824 compressed bytes and at most 1,048,576 original
report bytes; the decompressed prefix has SHA-256
`226fe9ccf85def9cd41457c0320f1a0670871df946a013d3f44ba6c1c652bede`.
Neither source-only verification mode opens or decompresses this archive.

The first original mismatch is `ReTests.test_keep_buffer`; this separate buffer
lifetime failure is not repaired or hidden by the present Unicode correction.
The actual original named-group mismatch is
`ReTests.test_symbolic_groups`. At line 288, CPython 3.14.6 requires:

```python
re.compile("(?P<µ>x)(?P=µ)(?(µ)y)")
```

The Go candidate instead raises `UnicodeDecodeError` for UTF-8 leading byte
`0xc2` at position zero. The next upstream case likewise requires a valid
astral-plane group name. Both the committed and independently located upstream
test files have SHA-256
`879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2`.
The actual method spans lines 282–293. Its exact source and AST are
independently authenticated; the test is not executed by the source freeze.

## One byte-accurate first-party correction

The original, repository-owned Go engine is
`candidates/go/engine.go`, SHA-256
`6472c4413921f3a877455315400c532e7632a871a96d46de9583fa6170a43192`,
53,782 bytes. Its `rebar_go_copy_name` export reports the length of a group
name in UTF-8 bytes. However, the following original loop visits only the
starting byte of each Unicode character:

```go
for offset := range name {
    target[offset] = C.uint8_t(name[offset])
}
```

Leave the complete parser, compiler, matching engine, native ABI, C bridge,
Python adapter, dependency-free Go module, and every other source byte intact.
Change only that loop to iterate every UTF-8 byte:

```go
for offset := 0; offset < len(name); offset++ {
    target[offset] = C.uint8_t(name[offset])
}
```

Authenticate the entire original 571-byte native export, not merely the loop.
Its SHA-256 is
`acae2de40ef8cdb23d07d68b6226015420809df6ba8b6eaee96ffa3baa5004d5`.
The complete corrected 592-byte export has SHA-256
`07908b618132c14c8815feaf4e860274c7bedeefeddc45185533f18a8abb49ec`.
The uniquely derived complete Go source has SHA-256
`095fd5a69ab8c3667ba92dc1934bf91b650260f6e55f1ac876fd267f0d8bcf1a`
and is exactly 53,803 bytes. Derive it only in memory during the source-only
gates. Verify ten genuine Python identifiers, including the observed micro
sign, an astral-plane group, combining marks, and multilingual names. Prove
that the historical rune-offset copy breaks eight and that the corrected loop
copies every UTF-8 byte. These are source controls, not candidate tests.

No production source imports Go `regexp`, Python `re`, `_sre`, a third-party
regular-expression package, or another candidate. A historical standalone Go
probe is not part of the four frozen first-party Go source owners and must
never be promoted or used as a candidate.

## Preserve the newest actual results

The already published version-31 graph remains unchanged: 151 evidence owners
and 156 authenticated history references. Its older Rust matching result is
1,087 differences and 7,438 verified passing cases; do not describe it as the
latest corrected Rust result.

The separately completed, genuinely corrected Rust V4 campaign adds exactly
two real evidence owners. Its small 4,674-byte receipt has SHA-256
`201b7edc94d54f9ea2054f2eab98a68c83850def841ceade6a14c8db7d05cdd3`.
It proves the real current total of 153 owners and 158 authenticated
references, 1,036 Rust differences, 8,965 verified passing cases, 13 original
workers, and no worker failures. Its actual 3,663,299-byte compressed matching
archive has SHA-256
`2ab266d193728e1297382ed233a813c7ef62c0aa407355cf44fef6aaeffa134f`.
Authenticate that archive only through the exact small receipt. Never open,
read, decompress, or run the Rust matching archive in this Go source freeze.

Preserve C's actual 1,230 differences, Zig's actual 2,172 differences, and
Go's actual 4,518 differences, 128 verified passes, and four genuine worker
failures. Preserve all 31,237 original checks, all 13 original groups, and all
13 named private exclusions. The 50 separately frozen callable-signature
checks have not run against either the Python reference or a candidate and
are not added to the original denominator.

No candidate is qualified. Corrected Go matching, undefined behavior, memory,
speed, confidence intervals, regressions, and rankings remain **NOT
MEASURED**. The proposed 4,194,304-case final comparison is **NOT GENERATED**
and **NOT OPENED**. There is no winner.

## Future private source application only

Only a separately authorized, caller-pinned `--apply` can create the derived
source. Its destination must be a fresh owner-only
`/tmp/rebar-phase2-native-build-…-go-…/reference-a/go-engine-package/engine.go`
or the corresponding `reference-b` phase. Both independent phase and package
directories must already exist, be distinct, have mode `0700`, and belong to
the current user. Verify the original, dependency-free private `go.mod`.
Create `engine.go` only with `O_CREAT | O_EXCL | O_NOFOLLOW`, mode `0600`.
Read back the identical inode, authenticate all 53,803 bytes, synchronize the
file and package directory, and independently reverify the unchanged
canonical repository engine. Never overwrite an existing file or promote a
native target. A source application is not a source build or a matching run.

Run caller-pinned `--self-test` and `--verify-frozen-context` in both the
ordinary environment and genuine `env -i PATH=/usr/bin:/bin LC_ALL=C`, using
the exact CPython 3.14.6 executable with `-I -B`. The synthetic tests
physically block filesystem access and writes, imports, candidate and
reference processes, networking, threads, clocks, native loads, locks,
signals, and archive decompression. The read-only context authenticates the
exact V31 history, actual Rust V4 source and receipt, the original Go build
and failure receipts, the original upstream method, the unchanged C and Zig
failure receipts, and all 50 unrun signature obligations. It never opens a
matching archive, reads a native target, changes a worktree file, runs a
candidate, samples a clock, or opens the holdout.
