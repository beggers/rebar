# Shared regular-expression patterns in real Python threads

Status: **FROZEN PROSPECTIVE PROTOCOL. TWO-REFERENCE ORACLE NOT RUN.**
Candidate thread compatibility is **NOT RUN**. Candidate module-version
compatibility is **NOT RUN**. Performance and memory are **NOT MEASURED**.
The holdout is **NOT ACCESSED**. A source-only self-test is never evidence
of an executed thread, regular-expression operation, or candidate.

This is one additive public-behavior category for an exact replacement used as
`import rebar as re`. It closes two independently identified public obligations:
`API-THREAD-SHARED-PATTERN-REENTRANCY` and
`API-MODULE-VERSION-METADATA`. Do not require the imported module to be named
`re`: the public import alias and exact Python behavior are the contract.

Preserve the untouched original **165** CPython methods: **152** public
methods, consisting of **151** actual applicable passes and the one original
debug-only skip, and exactly **13** explicitly named private implementation
methods. Never turn either private waiver into a public waiver.

Preserve the previously frozen genuine original CPython double reference:

    oracle/cpython-3.14.6/evidence/postfinal-locale-v6-self-oracle.json
    1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf

Preserve and reauthenticate all **1,376** genuine public cases, all **43**
public cohorts, all **64** real locale cases, and all **192** transitions
through the already frozen V27 source and the actual producer-owned V19
duplicate-key-strict canonical decoder. Do not parse lone-surrogate original
public-reference evidence with jq or a guessed JSON codec.

    tools/python_re_public_surface_oracle_stage27.py
    fd0ef1babdb5943d74ef443486805ef6586e46b06eb9d46e4f5b7b650045032b
    oracle/cpython-3.14.6/PUBLIC-SURFACE-V27.md
    c8cc917b52affbce8d61ae1ad217835c7c890fe1e1369d211475a7aaf443cd3f
    oracle/cpython-3.14.6/evidence/public-surface-v19-self-oracle.json
    a2ac2853a6551b9eb95564ee74731c9e7d44998f5ec32ad5aac2259b5b313ad8
    complete producer-owned 1,376-record SHA-256
    c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef

Pin the actual stable CPython executable, original public regex source, and
genuine public threading source by their complete content, not only paths:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
    255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016
    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/__init__.py
    741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35
    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/threading.py
    5323909624ec2165e70b6d31333e4191b63d383d2dc5a7d7d516a3475ea2b7e3

Freeze exactly **512** distinct cases: **16** equally weighted public
categories, with **32** deterministic variants in every category. The complete
base seed is **2026072701**. The exact canonical case-matrix SHA-256 is:

    a7d467e3e529204946fe00ddb819e734421e7087ea909af9ec24b757e42afa0b

The categories, in their immutable original order, are:

1. Shared immutable text-pattern search and capture spans.
2. Shared immutable text-pattern `match` and `fullmatch`.
3. Shared immutable bytes-pattern search and capture spans.
4. Shared immutable bytes-pattern `match` and `fullmatch`.
5. Independent text `finditer` states on the same compiled pattern.
6. Independent bytes `finditer` states on the same compiled pattern.
7. Independent text scanner states, progress, and exhaustion.
8. Independent bytes scanner states, progress, and exhaustion.
9. Shared text zero-width and empty-match iteration.
10. Shared bytes zero-width and empty-match iteration.
11. Named captures, actual backreferences, and replacement templates.
12. Text replacement callbacks recursively matching the same pattern.
13. Bytes replacement callbacks recursively matching the same pattern.
14. Actual public cache hits, safe nonconcurrent `purge`, and ASCII flags.
15. Preserved mixed-type errors and the original deterministic warning.
16. Exact public module version and flags during real shared text matches.

Every one of the **512** cases, including all **32** module-metadata cases,
must execute actual pattern operations in **two genuinely different live
`threading.Thread` roles inside one pinned reference process. Cases 481–512
are a named **subset** of all 512 thread cases; never count 544 cases.
Synchronize both live worker threads and their controlling thread through
genuine `threading.Barrier` generations. Prove concurrency by the barrier and
the distinct live Python and native thread identities, never by timing or an
assumed scheduling order. Use one original immutable compiled pattern object
for the two roles; record exact `id()` identity for every actually used
pattern. Iterators, scanners, and replacement callback lists are genuinely
independent per thread. Never assume that mutation of a shared scanner,
iterator, match, or warning filter is safe. `purge()` occurs before the two
cohort threads start; both later threads still use the original pattern.

Each process starts and joins exactly **32** real persistent threads: two
roles for each of the 16 cohorts. It retains **1,024** actual thread-side
case executions and **2,176** actual thread-side matcher, iterator, scanner,
and replacement API calls. Count `Pattern.scanner()`, every
`Scanner.search()`, `Match.expand()`, pattern matching, iteration, replacement,
recursive callback operations, and the exact expected `TypeError` calls.
Preparation-time module compilation and `purge()`, diagnostics, ordinary
match-result accessors, and performance are separate and **NOT MEASURED**.
The exact warning is one original `FutureWarning` per isolated reference:

    Possible set intersection at position 2

Capture that warning while preparing the compiled pattern before threads
start. Preserve every warning, observed exception, broken barrier, complete
traceback, actual start, full join, teardown, signal, timeout, candidate
import, and worker stdout and stderr. No placeholder, capability check,
synthetic event, failed join, main-thread operation, or `NOT RUN` is a case.

In the final category, observe the actual value and type of
`re.__version__`: exactly the Python string **2.2.1**. Observe zero-valued
`re.NOFLAG`, its genuine `RegexFlag` type, the real public flag values, and
a successful shared-pattern match in **both** live threads. Explicitly do
not check that the public module's `__name__` equals `re`.

Run exactly two genuinely distinct, externally PID-bound pinned CPython
reference processes. Fully preserve the original canonical process streams.
Compare all 512 stable semantic records and all exact warning records; do
not compare process-local thread or pattern addresses between processes.
Combined actual denominators are **64** started and joined threads,
**2,048** actual thread-side case executions, and **4,352** actual thread-side
matcher, iterator, scanner, and replacement API calls. Require no orphan,
failed barrier, hidden exception, warning,
candidate, timing, holdout, or altered private/public denominator.

Only root may run `--self-oracle` after this exact controller and protocol
have passed independent review and have been committed and successfully
pushed. Independently supply the exact reviewed controller and protocol
SHA-256 values. Candidate evidence remains **NOT RUN** until a separately
frozen prospective candidate protocol and independently audited native-owner
process actually evaluate all cases.

Retain the previously reviewed complete descriptor-relative publication
ledger. Successful and failed complete reports use bounded deterministic
gzip, compression level **9**, modification timestamp **0**, exact original
canonical bytes, strict single-member decompression, and complete SHA-256
readback. Publish only the four specifically declared new report and receipt
paths. Walk all parent directories using `O_DIRECTORY | O_NOFOLLOW`. Create
every output using `O_EXCL | O_NOFOLLOW`; record pending and completed
descriptor roles, actual device/inode, all original short writes and reads,
file `fsync`, parent-directory `fsync`, EOF, and complete owned-only
rollback. Never replace, truncate, or unlink an already existing basename.

`--self-test` is strictly source-only: it reads exactly its own frozen
controller and this protocol before entering a reversible no-effects guard.
It uses over 200 independently named deterministic positive and hostile
synthetic controls, including all 512 source-only matrix identities, false
thread roles and identities, incomplete barriers, hidden metadata, wrong
module version or type, wrong public flags, omitted joins, forged vectors,
invented PIDs, duplicate-key or noncanonical JSON, all 25 exclusive
publication attacks, and all 11 gzip attacks. Block filesystem operations,
real `threading.Thread.start`, regex matching, reference subprocesses,
native candidates, subinterpreters, clock sampling, benchmarks, and holdout
access. Run source-only controls with both the normal isolated pinned
environment and `env -i`. A source-only result never changes actual thread,
regex, candidate, holdout, or performance status.
