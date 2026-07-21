# Engine and language survey

This is discovery evidence, not a set of production candidates. The goal was to learn which execution models and foreign-function boundaries might be useful while checking where existing engines disagree with Python. **No external regex package or system engine may be wrapped and presented as a candidate.** Any production implementation must be written from scratch in this repository.

The probe compares 32 focused semantic cases and all 403 historical patterns vendored from CPython 3.14.6. Focused cases cover matching order, captures and references, lookarounds, conditionals, atomic and possessive behavior, end rules, Unicode classes and case folding, octal ambiguity, inline/scoped flags, invalid syntax, and lone surrogates. The larger corpus checks match span and syntax acceptance. Full rows, including every loss, are in [engine-survey.json](engine-survey.json), SHA-256 `42d9057ef14d3a89b7f80387c3f2a73b9371a8eb6c2515cccc8f95dfa88b8227`.

| Discovery probe | Focused cases | Historical patterns | What the losses show |
| --- | ---: | ---: | --- |
| PCRE2 10.47, 32-bit strings | 24/32 | **399/403** | Close pattern behavior, but Python's Unicode case folding, named escapes, inline `u`, open-group errors, and one octal/backreference case differ. |
| PCRE2 10.47, UTF-8 | 23/32 | **399/403** | Same gaps plus lone-surrogate handling; converting Python strings to UTF-8 also adds boundary work. |
| PCRE2 10.42, UTF-8 | 23/32 | 397/403 | Older octal behavior adds historical misses. |
| Oniguruma 6.9.9, Python syntax | 21/32 | 385/403 | Possessive, strict end, flags, escapes, and several historical cases differ. |
| ICU 74 | 18/32 | 382/403 | Python group syntax, references, conditionals, escapes, and empty cases differ. |
| Perl 5 | 24/32 | NOT MEASURED | Several Unicode, reference, and error cases differ; process-per-call is unsuitable for a Python API. |
| Node 26 | 14/32 | NOT MEASURED | JavaScript lacks several Python constructs and uses different Unicode and end behavior. |
| Go 1.26 `regexp` | 12/32 | NOT MEASURED | RE2 intentionally omits backreferences, lookarounds, conditionals, atomic groups, and possessive repeats. |
| Zig 0.16 calling POSIX regex | 8/32 | 212/403 | POSIX has different matching order and lacks most modern Python syntax; this boundary is rejected. |

The separately tested `regex` Python package is also rejected as a drop-in wrapper: it passes 6,297/8,244 seeded cases and 87/144 runnable official test methods, with 57 failed methods and one timeout. Missing `PatternError`, different flags/object behavior, warnings, Unicode and error rules account for many failures. This reinforces the from-scratch requirement.

## Useful architectural findings

- A 32-bit native representation can operate directly on Python's code points, avoids repeated UTF-8 offset conversion, and can represent lone surrogates. This is useful for a from-scratch executor or Zig/C FFI design.
- Python's case-insensitive ranges are unusually specific: `[a-z]` includes `İ`, `ı`, `ſ`, and `K`, and other Unicode closures matter. Folding range endpoints or relying on a general Unicode engine is insufficient.
- Python syntax validation is observable behavior. Open-group references, octal/backreference disambiguation, scoped flags, and unknown escapes must be handled by the candidate parser, not delegated to an engine.
- The Zig/POSIX probe demonstrates that language choice and engine semantics are separate decisions: Zig remains viable for a purpose-built executor, but POSIX regex is not.

## Reproduction

The survey used CPython 3.14.6, Go 1.26.3, Zig 0.16.0, Rust 1.97.1, GCC 13.3, Node 26.5, Perl 5.38.2, system PCRE2 10.42/Oniguruma 6.9.9/ICU 74, and a locally built PCRE2 10.47 with 8-, 16-, and 32-bit libraries and JIT enabled. Source archive hashes were:

- CPython `143b1dddefaec3bd2e21e3b839b34a2b7fb9842272883c576420d605e9f30c63`
- PCRE2 10.47 `c08ae2388ef333e8403e670ad70c0a11f1eed021fd88308d7e02f596fcd9dc16`
- `regex` wheel `7322ec6cc9fba9d49ab888bb82d67ac5625627aa168f0165139b17018df3fb8a`

With the toolchains and PCRE2 installed under `/tmp/rebar-design-survey`, reproduce the probes with:

```sh
survey_root=/tmp/rebar-design-survey
GOCACHE="$survey_root/go-cache" go build -trimpath -o "$survey_root/go-regex-probe" tools/go_regex_probe.go
ZIG_GLOBAL_CACHE_DIR="$survey_root/zig-global-cache" ZIG_LOCAL_CACHE_DIR="$survey_root/zig-local-cache" \
  "$survey_root/zig-0.16.0/zig" build-lib tools/zig_regex_probe.zig -dynamic -lc -O ReleaseFast \
  -femit-bin="$survey_root/zig-regex-probe.so"
PYTHONPATH=. /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  tools/engine_survey.py --output /tmp/engine-survey.json
```
