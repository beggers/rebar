# Freeze two independent builds of the corrected Go engine

Status: **SOURCE FROZEN. THE CORRECTED GO BUILD HAS NOT RUN.** This is a
build experiment, not a matching test. It does not make the Go candidate a
working, qualified, or faster replacement for Python `re`.

## What this preserves

The original Go candidate remains entirely first-party. Its original parser,
compiler, executor, four source owners, Python adapter, C bridge, dependency-free
Go module, and nine Go exports are preserved. No production matching may be
delegated to Go `regexp`, Python `re`, `_sre`, another candidate, or an external
regular-expression package.

The committed Unicode-name repair has three independently authenticated owners:

- `tools/apply_owned_go_unicode_name_source_repair_v1.py`:
  `a32f1062ef507903edc3a7cb5d0462853528e57582dd61e24e97fd1cc7737561`.
- `oracle/phase2/GO-UNICODE-NAME-SOURCE-REPAIR-V1.md`:
  `fa738f2365a087d07d3860b23278fb20da00300e0d3eb3df09b6d3584f3b4c95`.
- `oracle/phase2/go-unicode-name-source-repair-v1.json`:
  `b48d52c712288b037f2b2f88a69e658d8a389fd9ab469fb1999f80debc582d33`.

The original `candidates/go/engine.go` is 53,782 bytes with SHA-256
`6472c4413921f3a877455315400c532e7632a871a96d46de9583fa6170a43192`.
Its entire original 571-byte `rebar_go_copy_name` export has SHA-256
`acae2de40ef8cdb23d07d68b6226015420809df6ba8b6eaee96ffa3baa5004d5`.
The single allowed correction replaces rune-start iteration:

```go
for offset := range name {
```

with actual UTF-8 byte iteration:

```go
for offset := 0; offset < len(name); offset++ {
```

The complete corrected 592-byte export has SHA-256
`07908b618132c14c8815feaf4e860274c7bedeefeddc45185533f18a8abb49ec`.
The complete corrected 53,803-byte engine has SHA-256
`095fd5a69ab8c3667ba92dc1934bf91b650260f6e55f1ac876fd267f0d8bcf1a`.
Neither corrected bytes nor native outputs are written by either source-only gate.

## Accurate historical and latest matching results

The exact SHA-pinned V33 overview is immutable historical evidence. At that
snapshot there were 155 evidence owners, 160 authenticated references, 31,237
original cases, 13 suites, 13 named private waivers, and no qualified candidate.
The four historical Go worker failures are `scanner_verbose_v1`,
`public_types_v1`, `shape_v2`, and `threaded_pattern_v1`. The original Go
matching result remains **FAIL: 4,518 mismatches, 128 verified passing cases**.
Only `shape_v2` has a proven bounded-output harness kill. A Go native crash is
not proven, and the original crash and timeout counts are zero.

V33's 155/160 counts are historical lower bounds, not the current owner count.
Later genuine, append-only publications are explicitly permitted. In particular,
the actual newer corrected Zig matching campaign is authenticated by the small,
complete durable receipt
`repaired-zig-original-campaign-v3-zig-phase2-v12-zig-scanner-v2-original-p0-failures-publication-receipt.json`,
SHA-256 `40be94851ae23d8c4a9d2ac759d28231605247a499b0703e727c757d25b2fb96`,
4,111 bytes. Its actual matching result is **FAIL: 1,764 mismatches, 3,711
verified passing cases, 13 real workers, and zero infrastructure failures**.
That genuine publication establishes lower bounds of 157 evidence owners and
162 authenticated references. The separately authenticated V34 overview
preserves those exact counts and that actual Zig result as an immutable
historical snapshot, not a claim about the current checkout.

The older Zig result of 2,172 mismatches describes the older candidate only.
The earlier corrected Zig V12 build really ran 26 build and inspection processes,
but its build receipt by itself did not run matching. The newer Zig matching
receipt, not the earlier build receipt or V33, establishes the 1,764 result.
Historical Rust has 1,036 mismatches and historical C has 1,230. No matching or
source-build archive is opened, inspected, or decompressed in this freeze; only
the explicitly frozen small JSON receipt owners are read.

After that V34 snapshot, the actual two-process CPython 3.14.6 callable
reference was run. Its complete small durable receipt is
`oracle/phase1/evidence/callable-introspection-reference-v2-cpython-3.14.6-publication-receipt.json`,
SHA-256 `29b4a389e1b99cce15f07069ee1a0895f193e13400f944a037a4f42832619334`,
3,533 bytes. The result is **PASS: 50 out of 50 extra reference cases**, zero
reference failures, and two distinct real reference process IDs, 81 and 82.
Those references were run by the already published phase-one experiment, not
by this Go source freeze. The candidate version of the 50 extra cases has
**NOT RUN**; its matching is **NOT MEASURED**. None of the extra cases is
silently included in the original 31,237-case denominator. The actual
publication establishes lower bounds of 159 evidence owners and 164
authenticated references and explicitly permits later append-only evidence.
Its compressed evidence is authenticated by the small receipt only and is
never opened or decompressed by this experiment.

The planned 4,194,304-case performance holdout is not generated, read, or
opened. Speed, memory, uncertainty, and undefined behavior remain
**NOT MEASURED**. No winner is selected.

## Pinned first-party build

The pinned oracle is the exact isolated CPython 3.14.6 executable and its exact
Python 3.14 headers. The pinned build tools are Go 1.26.3, GCC 13, and GNU
`readelf`. Each toolchain owner is independently authenticated by its absolute
path, full bytes, SHA-256, mode, single link, descriptor identity, and required
execute permission. System-owned GCC and `readelf` are not incorrectly rejected
for having a different owner than the project checkout.

An actual build is allowed only with an explicit, caller-pinned `--build` and a
fresh `0700` root matching `/tmp/rebar-phase2-native-build-v13-go-*`. It must
create both independent `reference-a` and `reference-b` phase trees, private Go
module packages, temporary directories, Go build caches, and module caches
before building either phase. Every original source snapshot, `go.mod`, and
corrected private `engine.go` must be exclusively created without following
links, given mode `0600`, synchronized, and verified by full same-inode readback.
Canonical project sources and canonical candidate native targets are never
modified.

Each phase has exactly these 13 ordered, separately recorded roles:

1. `readelf_version`.
2. `gcc_version`.
3. `go_version`.
4. `build_go_engine`.
5. `build_go_bridge`.
6. `engine_dynamic`.
7. `engine_symbols`.
8. `engine_sections`.
9. `engine_notes`.
10. `bridge_dynamic`.
11. `bridge_symbols`.
12. `bridge_sections`.
13. `bridge_notes`.

Therefore 26 processes are a future success requirement, not processes claimed
to have run during this source freeze. The actual source-only build-process and
source-application counts are both zero.

The Go engine build runs inside its own phase-local Go module package:

```text
/home/dev-user/.openai/go/bin/go build -buildmode=c-shared -trimpath
    -buildvcs=false -ldflags=-buildid=
    -o <phase>/native/_go_engine.so .
```

Its environment fixes `PATH=/usr/bin:/bin`, `LC_ALL=C`, `LANG=C`, `TZ=UTC`,
`SOURCE_DATE_EPOCH=1`, `GOPROXY=off`, `GOSUMDB=off`, `GOWORK=off`, `GOENV=off`,
`GOTOOLCHAIN=local`, `CGO_ENABLED=1`,
`CC=/usr/bin/x86_64-linux-gnu-gcc-13`, and `GOFLAGS=-mod=readonly`. `TMPDIR`,
`GOCACHE`, and `GOMODCACHE` are distinct phase-private directories. Go may not
download modules, use a parent workspace, or replace its compiler.

The strict C bridge compilation uses `-D_GNU_SOURCE`, `-std=c11`, `-shared`,
`-fPIC`, `-O3`, `-Wall`, `-Wextra`, and `-Werror`; force-includes that phase's
actual compiler-generated `_go_engine.h`; and links the actual phase-local
`_go_engine.so` with `$ORIGIN` runpath. Both independently owned source roots
receive reproducible file-prefix mappings. Both ELF outputs are inspected with
the exact pinned `readelf --dynamic`, `--dyn-syms`, `--sections`, and `--notes`,
each with `--wide`. The complete generated header and nine real ELF exports are
checked. All three independently created phase outputs must be byte-identical:

```text
native/_go_engine.so
native/_go_engine.h
native/_go_bridge.cpython-314-x86_64-linux-gnu.so
```

A future actual build must preserve both successful and failed complete reports
in exclusively created, deterministic, synchronized evidence archives with
separate durable small receipts. A durable receipt saying `PASS` means durable
publication only; it never changes a failed build or a failing matching result
into a passing candidate.

## Four mandatory read-only gates

Use the isolated pinned Python executable with `-I -B`. Supply the full exact
SHA-256 of this controller, this protocol, and the canonical JSON contract:

```text
python3.14 -I -B tools/reproduce_owned_go_unicode_source_build_v13.py
    --self-test --source-sha256 <source> --protocol-sha256 <protocol>
    --contract-sha256 <contract>

python3.14 -I -B tools/reproduce_owned_go_unicode_source_build_v13.py
    --verify-frozen-context --source-sha256 <source>
    --protocol-sha256 <protocol> --contract-sha256 <contract>
```

Repeat both commands in the ordinary environment and with genuine
`env -i PATH=/usr/bin:/bin LC_ALL=C`. The source-only self-test physically
blocks filesystem access and writes, process creation, imports, candidate
activation, native loads, networking, threads, clocks, archive inspection,
signals, and locks while exercising positive and hostile negative controls.
The frozen-context gate independently authenticates the exact historical and
latest receipts, all four first-party Go owners, the frozen correctness matrix,
Unicode repair, passing 50-case callable references, immutable V33 and V34
historical lower bounds, V6 provenance, and all pinned compiler and Python
owners. Neither gate builds, imports, times, tests, or activates a candidate or
starts another reference process.
