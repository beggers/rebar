# From-scratch Rust automata experiments

This is a research experiment, not a replacement candidate or a final
performance result. It asks whether two general-purpose shortcuts can do less
work while returning exactly the same answer as Python's regular-expression
engine.

Overall speed compared with Python: **NOT MEASURED**. Performance on the unseen
test set: **NOT MEASURED**. No unseen test case is constructed, selected, or
timed by this experiment.

## Independent implementations

[`tools/rust_automata_lab.rs`](../../tools/rust_automata_lab.rs) implements its
own regular-expression parser, ordered bytecode compiler, capture-aware
backtracking machine, and four execution strategies. It does not import or call
a regular-expression package, Python's regular-expression implementation, or
another candidate.

The only shared generated input is the frozen Python 3.14.6 Unicode 16 lookup
table. It contains character classifications and simple case mappings, not a
parser or an executable regular-expression engine. The experiment explicitly
covers the 28 unusual case-equivalence components required to reproduce
Python's case-insensitive ranges.

The strategies are:

1. `ordered`: execute every alternative using a conventional ordered
   backtracking instruction. This is the reference architecture for the
   experiment, not the Python performance baseline.
2. `dispatch`: inspect the next character and enter an alternative directly
   only when exactly one alternative could consume that character. If multiple
   alternatives are possible, execute the original ordered instructions
   unchanged. The optimization is disabled for nullable alternatives. A
   256-entry lookup covers bytes and compact one-byte text; full-width Unicode
   uses the exact character classification and scoped flags.
3. `needle`: retain the safe alternative dispatcher and locate a mandatory,
   case-sensitive literal at a proven fixed offset using a from-scratch,
   overlapping Knuth–Morris–Pratt search. A match is attempted at every
   possible resulting start position; overlapping occurrences are never
   discarded.
4. `pike`: use an ordered set of instruction threads only to locate the exact
   first possible match. Threads with the same instruction and input position
   are merged in their original priority order. The real capture-aware ordered
   machine is then executed at the predicted position to recover all groups.
   This strategy excludes backreferences, conditional groups, lookarounds, and
   every other capture-reading or position-dependent assertion.

The reproduction driver also verifies that all four designs reject 12 explicit
non-regular or position-dependent negative controls rather than accidentally
claiming support. They include `(?>a|ab)c` against `abc ac`, `a*+a`, numeric
backreferences, capture-dependent conditions, positive and negative
lookarounds, anchors, empty non-word boundaries, and nullable unbounded loops.
Their exact CPython results and rejection reasons are retained in the raw
evidence.

The `needle` strategy is not enabled for case-insensitive literals, unknown or
variable-width prefixes, alternatives that do not share the mandatory literal,
or assertions and references whose behavior the experiment does not model.

## Why direct dispatch preserves match order

At any one attempted start position, a successful nonempty alternative must
consume that position's first character. If exactly one alternative accepts
that character, every other alternative necessarily fails before consuming a
character. Entering the sole possible alternative therefore gives the same
first match, captures, group-closing order, and subsequent backtracking as
trying all alternatives in their Python-specified order.

When two alternatives accept the same character, when an alternative can match
the empty string, or when a condition cannot be established exactly, the
original ordered backtracking instructions remain in use. Therefore overlapping
prefixes such as `a|ab`, nullable branches such as `|ab`, and nested captures
are not approximated or silently reordered.

Case-insensitive matching uses the same frozen Unicode tables and
case-equivalence exceptions as the candidate. Flag changes inside `(?i:...)`,
`(?-i:...)`, `(?a:...)`, and `(?s:...)` are attached to the individual parsed
expressions. An ASCII dispatch entry is accepted only if the complete exact
first-character predicate identifies a unique possible branch.

## Rejected or deliberately excluded approaches

- A conventional unordered deterministic or Thompson automaton can change
  Python's leftmost alternative, greedy or lazy preference, capture contents,
  and last participating group. It cannot replace the general executor.
- Backreferences and conditional groups are not ordinary regular languages;
  converting them to a plain deterministic automaton is not exact.
- Atomic or possessive alternatives can reject an early start that an ordinary
  automaton would accept. For example, `(?>a|ab)c` rejects `abc` but can still
  match the later `ac` in `abc ac`. Returning after the first filtered start
  would silently miss that valid result.
- Counted repeats, zero-width progress guards, and atomic-cut stacks cannot
  be merged by instruction and text position alone; their distinct internal
  state can produce different future matches. The isolated ordered-thread
  compiler uses ordinary ordered splits and excludes those stateful opcodes.
- Lookarounds and zero-width assertions cannot be discarded simply because
  they do not consume a character. They can reject a start or introduce
  captures.
- Prefix trees are unsafe when an earlier shorter branch can match before a
  later longer branch. A tree would require an ordered acceptance and
  backtracking proof before inclusion.
- Case-folding a literal with Rust's current Unicode tables is unsafe because
  pinned Python 3.14.6 uses Unicode 16 and special equivalence components.
- A literal appearing in only one branch is not a mandatory prefilter for the
  entire expression.
- Finding a literal with an unbounded or uncertain offset does not establish a
  safe candidate start position.
- Component-level timing is not an end-to-end comparison with Python. It
  excludes pattern compilation, Python object creation, calls across the Python
  boundary, iteration, substitution, and memory costs unless those are measured
  separately in the frozen project benchmark.

## Reproduction

Use the pinned CPython interpreter and run these commands only when the other
benchmark and correctness captures are idle:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONPATH=. "$PY" tools/rust_automata_lab.py build
PYTHONPATH=. "$PY" tools/rust_automata_lab.py self-test
PYTHONPATH=. "$PY" tools/rust_automata_lab.py verify \
  --patterns 1024 --seed 2708488230 \
  --output candidates/evidence/rust-v6-automata-lab.json.gz
PYTHONPATH=. "$PY" tools/rust_automata_lab.py measure \
  --limit 128 --trials 9 --operations 12 --warmups 3 --bootstraps 1000
```

The driver runs CPython `re` only in a separate oracle-only process. Every
architecture is compared against that oracle before its timing; the Rust
executable also checks that each timed operation returns the same answer before
and after timing. Samples for all four approaches are interleaved in a
deterministic shuffled order.

A candidate is counted as more than 20% slower only when its running time is
strictly greater than 120% of the comparison time. Equivalently, its speedup
must be strictly below `5/6`, not below `0.8`. The `self-test` verifies the
exact boundary, the immediately adjacent floating-point values, and invalid
inputs before any future timing can run.

The timed cases are drawn exclusively from frozen version-6 practice cases by
calling `generated_case("calibration", family, variant)`. The complete suite
constructor is deliberately not called because it would also construct unseen
cases. Unsupported APIs, input types, patterns, and subject sizes are counted
and recorded, not treated as successful measurements.

The compressed evidence contains the full result and internal operation counts
for all 87,408 individual architecture comparisons, the Unicode, Rust source,
and driver hashes, the exact seed, all 12 negative controls with their CPython
answers, and every observed mismatch. Raw paired timings, all slower timed
cases, and confidence intervals remain
**NOT MEASURED** until a separately authorized practice-only timing run.

## Results

Pinned Python version: **CPython 3.14.6**.

Seeded cases: **21,852**.

Independent architecture comparisons: **87,408**.

Unexpected differences: **0**.

Explicit unsupported-semantics controls: **12 correctly rejected out of 12**.

Unseen performance cases accessed: **0**.

The following counts describe deterministic internal work on the correctness
cases. They are not elapsed-time measurements or claims about speed:

| Rust research approach | Bytecode steps | Saved alternative paths | Actual match-start attempts |
| --- | ---: | ---: | ---: |
| Ordinary ordered machine | 849,978 | 311,722 | 109,502 |
| Safe alternative dispatch | 273,010 | 29,778 | 109,502 |
| Mandatory-literal filter | 260,805 | 29,778 | 98,969 |
| Ordered-thread filter | 1,482,135 | 20,461 | 5,412 |

The ordered-thread approach attempts fewer match starts but performs more
internal work. It remains a recorded alternative, not a claimed improvement.

Practice-case architecture speed: **NOT MEASURED**.

Performance relative to Python: **NOT MEASURED**.

Performance on the expanded unseen test: **NOT MEASURED**.
