# Go engine: source-only compatibility review

Status: **NOT BUILT. NOT RUN. NOT QUALIFIED.** Speed, memory,
holdout, crash, sanitizer, and cross-interpreter behavior are
**NOT MEASURED**.

## Frozen implementation

| Owned file | SHA-256 |
| --- | --- |
| `go.mod` | `99763f86f7aa4e396487c2c72734030bdad903354885d12aabb12c0f2fc0e33b` |
| `engine.go` | `cd4b878c895f4c39472baebb54770b6b63d2692c1fad5f29bf046b0e12efc119` |
| `exports.go` | `4e3b6a5f7dc21ae6b37d21827de4cb2570cfb138d1026962f9a2b95116c29a7f` |
| `python_bridge.c` | `5c9372e924fd5d0797086369b9db71a0f5120c56821d74cad8324491bec6f65a` |

`go.mod` declares **zero external dependencies**. `engine.go:103`
begins the owned lexer, `:253` defines the separate parser, `:1059`
compiles the owned expression tree, and `:1236`–`:1506` implements
the independent continuation-based matching executor.
`exports.go:197` exposes an owned, explicitly versioned native ABI;
`python_bridge.c` is a separate direct CPython binding.

The bridge's `copyreg` import is ordinary object reconstruction,
not regular-expression matching. Its `_sre.SRE_Scanner` string is
the display name of an independently declared native type; it does
not import Python's `_sre` engine. Static inspection is not an
executed binary or no-delegation audit.

## Reproducible Python-compatibility gaps

Use the unchanged original
[`test_re.py`](../../oracle/cpython-3.14.6/test_re.py) and
[`complete upstream protocol`](../../oracle/cpython-3.14.6/POSTFINAL-LOCALE-V4.md).

- Supply the complete real public surface: `RegexFlag`, ordered
  public exports, an independently owned lexical `Scanner`, the
  package-only `_constants.MAXGROUPS`, full caching, public
  reconstruction, and native-owned Python-compatible type names.
  The original scanner and constant tests begin at
  `test_re.py:1622` and `:702`.
- Accept legal unknown integer flag bits and implement Python's
  exact pattern representations, equality, and hashing. Preserve
  the original tests at `test_re.py:2847`, `:2309`, and `:2338`.
- Independently implement named Unicode character escapes;
  `engine.go:167` currently explicitly rejects them. Preserve the
  original Unicode escape test beginning at `test_re.py:851`.
- Implement genuine locale-dependent matching and Python-visible
  debug output. `engine.go:665`, `:1059`, and `:1071` explicitly
  reject the required matching or debug behavior.
- Implement replacement-template grammar and `Match.expand`.
  `python_bridge.c:1016`, `:1316`, and `:1329` explicitly return
  `NotImplementedError`. The unchanged original replacement tests
  begin at `test_re.py:119`, `:192`, and `:331`.
- Add a real interpreter-local bounded pattern cache.
  `python_bridge.c:2050` currently implements `purge` without
  clearing an actual compilation cache.
- Implement the original ambiguous-set and positional-argument
  warnings, including true caller information, and independently
  resolve forward conditional group references.
- Preserve the bridge's genuine retained `Py_buffer` ownership and
  pattern reconstruction while adding weak-reference and structural
  native type behavior. Do not discard existing lifecycle checks.
- Remove full-subject rune copying before attempting the actual
  two-gibibyte original tests. Prove the real anchored CPU test,
  multiprocessing behavior, and fork safety; do not substitute a
  reduced subject or claim cross-interpreter support.

## Qualification rule

Build the owned Go engine as its own versioned shared library and
build the direct CPython extension separately against the pinned
Python 3.14.6 headers. Keep Go handles and pointer ownership within
their documented native boundaries. Execute the same genuine
native-ownership, complete upstream, independent edge, public API,
and final holdout gates required of every other engine. Do not
benchmark or rank Go before it actually passes those gates.
