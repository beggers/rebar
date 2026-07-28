# Freeze the owned Zig Scanner construction correction

This is one first-party Zig source correction frozen against the actual,
corrected Python reference and the version-39 project snapshot. It does not
modify, import, build, or run the Zig candidate. The prospective correction
exists only in verifier memory. Its compatibility result is **NOT RUN**.

Python 3.14.6 gives `re.Scanner` exactly one exposed capture slot for each
lexicon branch. If a phrase needs more numbered capture slots than there are
branches, Scanner construction raises `RuntimeError("invalid SRE code")`.
The existing Zig adapter already computes the number of captures in every
phrase, but its Scanner constructor never rejects a count above the number of
branches. The first archived mismatch is
`scanner-differential.v1.0160`.

The original frozen Scanner matrix has **1,024** cases, **32** families,
and **32** variants per family. Independently reconstituting the entire
original matrix from its authenticated, first-party syntax tree identifies
exactly **64** capture-slot overflows:

- 32 nested-capture cases.
- 16 numbered-capture cases.
- 16 named-capture cases.

The matrix retains its original SHA-256,
`83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c`.
The other **960** Scanner stimuli are preserved. Constructing this matrix
does not import its oracle module, start a reference process, run an engine,
or load a candidate.

The prospective correction adds a capture-slot check to the existing
`Scanner.__init__` block in `candidates/zig_candidate.py`. It preserves the
existing empty-lexicon error and every adapter byte outside that block. The
original Zig engine, bridge, and adapter are unchanged. Corrected adapter
bytes exist only in verifier memory; they have not been installed or tested.

The full previous Zig result remains **FAIL**: **1,764** recorded
differences, **3,711** verified passing cases, **13** actual workers, all
**13** original groups completed, and no infrastructure failures. Its
**620** verbose-scanner differences are **NOT REPAIRED**. The other original
losses remain preserved. In particular, the public subtype-equality cohort
must not be removed or waived merely because evaluator-module provenance
also requires separate investigation.

The corrected phase-one Python reference has actually passed. Two genuinely
separate, isolated Python 3.14.6 workers, process IDs **81** and **82**, each
observed all **6,912** original public-type cases and agreed on complete
record SHA-256:

    6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2

They retained every one of the **96** original candidate-context cases. Their
shared candidate-context record SHA-256 is:

    587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad

The durable receipt is authenticated separately from its publication status;
the actual reference status is PASS. The version-37 false-reference evidence
remains preserved, and its **96** historical failures are not represented as
current Python failures.

The original denominator remains **31,237**, across **13** original suites,
with exactly **13** separately named private waivers. The additional **50**
callable checks remain separate; their two isolated reference workers passed,
and no candidate has run them. Current version-39 evidence proves lower
bounds of at least **164** evidence owners and **169** history references.
These are authenticated lower bounds, not a whole-repository census.

The corrected, six-family version-4 case producer is actually frozen. It is
not a matching result. Its exact first-party source, protocol, and contract
are authenticated alongside all four version-39 graph owners. The older
version-3 producer and version-38 graph remain preserved as history.
Candidate workers and the Rust campaign still require the corrected
version-6, version-8, and version-10 runner chain. Until those runner owners
are separately frozen, committed, and pushed, source installation, native
building, and candidate matching remain **BLOCKED**. Never invent future
runner hashes or describe the genuinely frozen version-4 producer as
unfrozen.

No matching archive is opened, decompressed, or rewritten by the verifier.
Its source-only boundary rejects candidate and reference workers, native
loading, `re` imports, external matchers, network, files, archives, clocks,
and hidden benchmarks. Runtime non-delegation is **NOT ESTABLISHED**.
The source-only gate additionally physically blocks direct low-level process
execution and forks, native Python extension creation, dynamic-library
loading, low-level source imports, original native file interfaces, network
and thread creation, decompression, signals, locks, writes, and clocks.
It verifies the exact unaffected **960** Scanner stimuli, independently
rejects forged version-39 and corrected version-4 evidence, and exercises
inverse controls for every prohibited source-apply, native-build, candidate,
reference, benchmark, and holdout action.

Its historical graph snapshot truthfully records one actual reference-archive
inflation in each version-38 and version-39 renderer. The Zig source verifier
itself opens and inflates **zero** reference or matching archives.

Speed, memory, confidence, undefined behavior, and the final result are
**NOT MEASURED**. The expanded holdout is **NOT OPENED**.

Run each mode in both ordinary and sterile environments, supplying three
independently computed SHA-256 pins:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/apply_owned_zig_scanner_phrase_source_repair_v3.py \
  --self-test \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/apply_owned_zig_scanner_phrase_source_repair_v3.py \
  --verify-frozen-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

Repeat both commands with `env -i PATH=/usr/bin:/bin LC_ALL=C` immediately
before the absolute Python path. These are source-only gates, not matching
tests or candidate qualification.
