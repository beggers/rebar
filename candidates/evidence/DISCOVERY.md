# Candidate-family discovery experiment

This experiment was run only after correctness oracle v1 was frozen and pushed. It does not select a winner. It tests four materially different engine families and records raw, unadapted results so later compatibility work cannot hide the starting point.

| Family | Engine/build observed | Raw P0 result | Decision |
| --- | --- | --- | --- |
| `regex` | `regex==2026.7.10`, bundled C engine | 1,341/2,048 pass; 707 fail | retain: broad syntax and CPython wheel; needs a compatibility adapter |
| PCRE2 | `pcre2==0.7.0`, bundled PCRE2/Cython with JIT | 947/2,048 pass; 1,101 fail | retain: distinct JIT-capable backtracker; missing public helpers/metadata |
| Oniguruma | `onigurumacffi==1.5.0`, bundled Oniguruma 6.9.10 | NOT MEASURED against full oracle | retain low-level `_onigurumacffi` only; public wrapper imports and executes stdlib `re` and is rejected |
| ICU | system ICU 74.2 C API | NOT MEASURED against full oracle | reject for this round: UTF-16-only API makes exact bytes and code-point offsets a separate binding project |

The raw failure records are [discovery-regex.json](discovery-regex.json) and [discovery-pcre2.json](discovery-pcre2.json); all losses are preserved. Their chart is generated, never hand-edited.

The unadapted failures are informative. `regex` exposes extra APIs/flags, differs on `lastgroup`, Unicode `IGNORECASE` for dotless i, ambiguous-set warnings, error positions, and accepts variable-width lookbehind. PCRE2 lacks `escape`, `purge`, `scanner`, and `Match.regs`; all 384 property cases therefore fail before semantic comparison. Both need an explicit CPython-facing contract and error normalization.

Small feature probes were run for all retained engines. PCRE2 accepts Python named groups/backreferences, `\z`, atomics, possessives, fixed lookbehind, conditionals, and scoped/global flags. Oniguruma accepts the same core constructs but requires named-group/backreference translation (`(?P<n>...)`/`(?P=n)` to its syntax). Oniguruma offsets are UTF-8 bytes, so its adapter must map them back to Python code-point offsets. These are general translations, not fixture-specific answers.

## Delegation audit

Production delegation to CPython's engine is prohibited. Source and undefined-symbol scans found zero `import re`, `from re`, `_sre`, `sre_parse`, or `sre_compile` references in the `regex` and PCRE2 production packages, and zero `_sre` symbols in their native extensions. `_onigurumacffi.abi3.so` likewise has no `_sre` dependency. The **public** `onigurumacffi.py` wrapper contains `import re` and compiles a backreference expression at import time; it is explicitly rejected and will not be imported by a candidate.

Observed native SHA-256 values:

- `regex/_regex.cpython-314-x86_64-linux-gnu.so`: `4dee9c588664f08f7002c04befdc7c3922a768ac5361aacfa6bc55366f4399c7`
- `pcre2/_cy.cpython-314-x86_64-linux-gnu.so`: `a2002dbfb6b96ea6d6535931688ae318566cd450326650512ff42da919a9e18f`
- `_onigurumacffi.abi3.so`: `8d8d08c109433e504778e007c7ea9465a5f8f53284297682fe1a6cdb146762fe`

System alternatives observed were PCRE2 10.42 (`e00576d71d81d3ba0cfa4903c835a44a8723aac96f72f79ff75200b4cff9071b`), Oniguruma 6.9.9 (`373f89146c922f948c69197f80a9b321a2689666de1b70ca3cee09e6f765fa42`), and ICU 74.2 (`3550b194eb2cf2e6f798f033eb9ca279d498c21296b4a18790ce158d2023e47b`). The packaged engines are used to keep builds portable and pinned.

References: [PCRE2 native API](https://www.pcre.org/current/doc/html/pcre2api.html), [PCRE2 syntax](https://www.pcre.org/current/doc/html/pcre2pattern.html), [ICU regex guide](https://unicode-org.github.io/icu/userguide/strings/regexp.html), and the [`regex` package](https://pypi.org/project/regex/).
