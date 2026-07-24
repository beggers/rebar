# C++ engine: source-only compatibility review

Status: **NOT BUILT. NOT RUN. NOT QUALIFIED.** No performance,
memory, held-out test, crash, or sanitizer result has been measured.

## Frozen implementation

| Owned file | SHA-256 |
| --- | --- |
| `engine.hpp` | `ac7fd6038d8e88c492844339acdcb0af8689a4317f28dd4057c5c2a60782936b` |
| `engine.cpp` | `c3d75a79841d15e65a7b3618e466a9844de75877a5384b340dff472e45184f31` |
| `py_bridge.cpp` | `96d4ea5a723a452c71655275563777327522c11e3bd1476b458dbdf1ce3d5036` |

This is a genuinely separate implementation. `engine.cpp:241` begins
its own parser, `engine.hpp:113` defines its own instruction set,
`engine.cpp:1533` invokes its own compiler, and
`engine.cpp:1551`–`1561` invokes its own backtracking machine.
`py_bridge.cpp` is a direct Python C API binding. The reviewed source
does not include C++ `std::regex`, Python's matching engine, or an
external regex library. Static inspection is not an executed
no-delegation audit.

## Reproducible Python-compatibility gaps

Compare against the unchanged original
[`test_re.py`](../../oracle/cpython-3.14.6/test_re.py) and
[`complete upstream protocol`](../../oracle/cpython-3.14.6/POSTFINAL-LOCALE-V4.md).

- The public package needs Python's complete `RegexFlag` enumeration,
  all ordered public exports, a lexical `Scanner`, an owned
  `_constants.MAXGROUPS`, and an independently owned compilation and
  pickle surface. The original scanner and group-limit tests are at
  `test_re.py:1622` and `test_re.py:702`.
- Exact Python pattern representations must support legal unknown
  integer flag bits; pattern equality and hashing must remain correct
  after the cache is cleared. The original tests are at
  `test_re.py:2847`, `test_re.py:2309`, and `test_re.py:2338`.
- The native pattern and iterator must keep borrowed mutable buffers
  exported for their entire actual lifetime.
  `py_bridge.cpp:171`, `:184`, and `:187` currently release the
  acquired buffer during conversion. The original mutable-buffer and
  weak-reference tests begin at `test_re.py:69` and `:80`.
- Pattern pickling, identity copying, weak references, and exception
  `.pattern` details require complete actual native type slots and
  independently owned reconstruction. Their original tests include
  `test_re.py:1415`, `:1425`, and `:2254`.
- Independently implement Unicode group-name validation, Unicode
  replacements, correct three-digit octal replacement parsing, and
  forward conditional group resolution. Preserve the real originals
  at `test_re.py:192`, `:282`, `:331`, and `:1061`.
- Emit the genuine Python-visible deprecation and ambiguous-set
  warnings with the correct caller location; do not silence them.
- Replace process-global native types and cache state with genuinely
  interpreter-local module state. The existing cache is real, but
  `py_bridge.cpp:91`–`:96` and `:1626` use global module state.
- Run the original two-gibibyte tests, anchored CPU-resource test,
  and actual multiprocessing test without converting the whole
  subject into an avoidable four-byte character copy. Preserve the
  original memory requirements rather than substituting small input.

## Qualification rule

Compile this source directly against the pinned CPython 3.14.6 C API.
Require the frozen authentic 152-method upstream oracle, genuine
native-ownership and anti-delegation checks, full archived failures,
and the same independently frozen public and final comparisons as all
other engines. Do not benchmark, rank, or select this experiment
until all applicable correctness gates actually pass.
