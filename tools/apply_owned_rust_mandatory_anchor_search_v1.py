#!/usr/bin/env python3
"""Freeze one bounded, independently authored Rust candidate-start filter.

Source verification reads only named first-party Rust source, public practice
evidence, and this experiment's three documents.  It imports no regular-
expression engine, loads no native library, starts no process, reads no hidden
case, samples no clock, and never changes a file.  Only explicit root-owned
``--apply`` may exclusively create the two predicted Rust-source variants.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex")):
    raise SystemExit("source verification must begin without a regex engine")

import builtins
import hashlib
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/apply_owned_rust_mandatory_anchor_search_v1.py"
PROTOCOL = "oracle/phase2/RUST-MANDATORY-ANCHOR-SEARCH-V1.md"
CONTRACT = "oracle/phase2/rust-mandatory-anchor-search-v1.json"
VARIANT_DIRECTORY = "candidates/rust/variants/mandatory_anchor_search_v1"
LIB_VARIANT = VARIANT_DIRECTORY + "/lib.rs"
SEARCH_VARIANT = VARIANT_DIRECTORY + "/search.rs"
SCHEMA = "rebar-owned-rust-mandatory-anchor-search-v1"
MATRIX_SHA256 = "b13ff74122041ea792774fd5ee2d1f6d38033e94a1a6703c6e48522e461552a7"
PRACTICE_RECORDS_SHA256 = "41f83dc761a93ea8e3203f46cedbba1e10918cf053194c20b37b8c209e992242"
MAX_OWNER_BYTES = 2 * 1024 * 1024
MAX_JSON_DEPTH = 48
ANCHOR_CAPACITY = 16
SET_CAPACITY = 8

# These fixed owner identities were measured before this source was authored.
# Only public, already-open development-practice records are included; no
# archive, candidate library, private build root, or final holdout is named.
OWNERS = (
    ("goal", "GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 2064, 31364044),
    ("rust_manifest", "candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225, 2064, 428094),
    ("rust_lock", "candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167, 2064, 428098),
    ("rust_engine_source", "candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967, 2064, 428096),
    ("rust_search_source", "candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773, 2064, 429682),
    ("public_profile_source", "tools/rust_public_profile_v1.py", "ada1e9cfc8684ecb4fcf9294057347018b6058fc1619ae9de6a8b31097aa1562", 79693, 2064, 429476),
    ("public_profile_protocol", "oracle/phase3/RUST-PUBLIC-PROFILE-V1.md", "6664f17ddd65c1953782f43b7fe1fa01427f1f510adfbad86fe8efdb135829ba", 5281, 2064, 525927),
    ("public_profile_manifest", "oracle/phase3/rust-public-profile-v1.json", "b791b141eabbf6eb8a67484f5deb82bb41e324aedbdfe5b53a98ebc1553372c5", 1797, 2064, 525928),
    ("rust_practice_correctness", "experiments/rust_public_profile_v1/public-run-001/rust.correctness.raw.json", "8774ad035e17126252803e75494a80d376386a85e13c46cb3e0380b82dae89b0", 445394, 2064, 526006),
    ("python_practice_correctness", "experiments/rust_public_profile_v1/public-run-001/stdlib.correctness.raw.json", "efe0a3cc37194290b9577d5bd4f502a5c482016bc2b8ae90acec6254545b5381", 445036, 2064, 526005),
    ("public_paired_timings", "experiments/rust_public_profile_v1/public-run-001/paired-timing.raw.json", "3da06bdb04ace9897d359aaa962ca412f3e9260a5c1a337703e0aa35567b6b85", 504907, 2064, 526015),
    ("owned_simd_search_research", "tools/rust_search_lab.rs", "45726e1ba3e4864ef64b441eb63c67d68729a43be3bd2f02682453fe113c35c7", 20573, 2064, 429633),
    ("owned_simd_search_results", "candidates/evidence/RUST-V6-SEARCH-LAB.md", "dfa25003ab643cbd1012943771a1364d34f7d9b3c170d4022e6a26f18b17b8b0", 4725, 2064, 429638),
)

ALLOWED_SOURCE_PATHS = frozenset(
    ROOT + "/" + relative
    for relative in (SOURCE, PROTOCOL, CONTRACT)
    + tuple(owner[1] for owner in OWNERS)
)
FORBIDDEN_SOURCE_TOKENS = (
    "archive", "holdout", "sealed", "hidden", "fixture", ".so", ".dll", ".dylib",
)
WALL_ACTIVE = False
WALL_INSTALLED = False
BLOCKED = {
    "candidate_execution": 0,
    "native": 0,
    "process": 0,
    "clock": 0,
    "workspace_write": 0,
    "restricted_case": 0,
    "foreign_read": 0,
}


class FreezeError(Exception):
    """The frozen source, conservative proof, or one-shot creation failed."""


def require(value: object, message: str) -> None:
    if value is not True:
        raise FreezeError(message)


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete immutable bytes")
    return hashlib.sha256(raw).hexdigest()


def blocked(kind: str, description: str) -> None:
    BLOCKED[kind] += 1
    raise FreezeError("the physical source-only wall rejected " + description)


def source_wall(event: str, arguments: tuple[object, ...]) -> None:
    if not WALL_ACTIVE:
        return
    if event == "open":
        path = arguments[0] if arguments else None
        mode = arguments[1] if len(arguments) > 1 else None
        flags = arguments[2] if len(arguments) > 2 else 0
        if (type(mode) is str and any(letter in mode for letter in "wax+")) or (
            type(flags) is int and (
                flags & os.O_ACCMODE != os.O_RDONLY
                or flags & (os.O_CREAT | os.O_TRUNC | os.O_APPEND | os.O_EXCL)
            )
        ):
            blocked("workspace_write", "a source-mode filesystem write")
        if type(path) is not str or path not in ALLOWED_SOURCE_PATHS:
            spelling = path.lower() if type(path) is str else "descriptor"
            if any(token in spelling for token in FORBIDDEN_SOURCE_TOKENS):
                blocked("restricted_case", "a hidden case, archive, or native owner")
            if "candidate" in spelling:
                blocked("candidate_execution", "an unapproved candidate owner")
            blocked("foreign_read", "an unapproved source owner")
    elif event == "import":
        blocked("native", "a late module or native-library import")
    elif event.startswith(("subprocess.", "os.posix_spawn", "os.spawn", "os.exec", "os.fork", "os.system")):
        blocked("process", "a candidate, compiler, oracle, or profiler process")
    elif event.startswith(("ctypes.", "socket.", "os.dlopen")):
        blocked("native", "native activation or external communication")
    elif event.startswith(("os.mkdir", "os.rmdir", "os.remove", "os.unlink", "os.rename", "os.replace", "os.chmod", "os.chown", "os.link", "os.symlink", "os.truncate", "shutil.")):
        blocked("workspace_write", "a source-mode workspace mutation")
    elif event in ("os.listdir", "os.scandir", "glob.glob"):
        blocked("foreign_read", "source-mode directory or case enumeration")


def no_clock(*_arguments: object, **_keywords: object) -> object:
    blocked("clock", "a clock, sleep, timing trial, or profiler sample")


def install_wall() -> None:
    global WALL_ACTIVE, WALL_INSTALLED
    require(WALL_INSTALLED is False, "the one-way source wall was installed twice")
    sys.addaudithook(source_wall)
    WALL_INSTALLED = True
    WALL_ACTIVE = True
    for name in (
        "time", "time_ns", "monotonic", "monotonic_ns", "perf_counter", "perf_counter_ns",
        "process_time", "process_time_ns", "thread_time", "thread_time_ns", "sleep",
    ):
        if hasattr(time, name):
            setattr(time, name, no_clock)


def owner_bytes(relative: str, digest: str, size: int, device: int, inode: int) -> bytes:
    absolute = ROOT + "/" + relative
    descriptor = os.open(absolute, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode), "owner must remain a regular file: " + relative)
        require((identity.st_dev, identity.st_ino, identity.st_size) == (device, inode, size),
                "frozen owner identity changed: " + relative)
        raw = b""
        while len(raw) < size:
            part = os.read(descriptor, min(65536, size - len(raw)))
            require(len(part) != 0, "owner ended before its frozen byte count: " + relative)
            raw += part
        require(os.read(descriptor, 1) == b"", "owner extends beyond its frozen byte count")
    finally:
        os.close(descriptor)
    require(sha256(raw) == digest, "frozen owner SHA-256 changed: " + relative)
    return raw


def bounded_file(relative: str) -> bytes:
    descriptor = os.open(ROOT + "/" + relative, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode) and 0 < identity.st_size <= MAX_OWNER_BYTES,
                "source-freeze document is not a bounded regular file: " + relative)
        raw = b""
        while len(raw) < identity.st_size:
            part = os.read(descriptor, min(65536, identity.st_size - len(raw)))
            require(len(part) != 0, "source-freeze document ended early: " + relative)
            raw += part
        require(os.read(descriptor, 1) == b"", "source-freeze document gained trailing data")
    finally:
        os.close(descriptor)
    return raw


class StrictJSON:
    """Decode complete bounded JSON without importing Python's regex package."""

    def __init__(self, raw: bytes):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_OWNER_BYTES,
                "one complete bounded JSON document is mandatory")
        try:
            self.text = raw.decode("utf-8", "strict")
        except UnicodeError as error:
            raise FreezeError("public JSON must be valid UTF-8") from error
        self.index = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def string(self) -> str:
        require(self.text[self.index:self.index + 1] == '"', "a JSON string is required")
        self.index += 1
        result: list[str] = []
        escapes = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            char = self.text[self.index]
            self.index += 1
            if char == '"':
                return "".join(result)
            if char != "\\":
                require(ord(char) >= 32 and not 0xD800 <= ord(char) <= 0xDFFF,
                        "a JSON string contains an invalid character")
                result.append(char)
                continue
            require(self.index < len(self.text), "an incomplete JSON escape")
            char = self.text[self.index]
            self.index += 1
            if char != "u":
                require(char in escapes, "an unknown JSON escape")
                result.append(escapes[char])
                continue
            digits = self.text[self.index:self.index + 4]
            require(len(digits) == 4 and all(item in "0123456789abcdefABCDEF" for item in digits),
                    "an invalid JSON Unicode escape")
            self.index += 4
            value = int(digits, 16)
            if 0xD800 <= value <= 0xDBFF:
                require(self.text[self.index:self.index + 2] == "\\u", "an unpaired high surrogate")
                lower = self.text[self.index + 2:self.index + 6]
                require(len(lower) == 4 and all(item in "0123456789abcdefABCDEF" for item in lower),
                        "an invalid JSON low surrogate")
                low = int(lower, 16)
                require(0xDC00 <= low <= 0xDFFF, "an unpaired JSON high surrogate")
                self.index += 6
                value = 0x10000 + ((value - 0xD800) << 10) + low - 0xDC00
            else:
                require(not 0xDC00 <= value <= 0xDFFF, "an unpaired JSON low surrogate")
            result.append(chr(value))
        raise FreezeError("an unterminated JSON string")

    def number(self) -> int:
        first = self.index
        if self.text[self.index:self.index + 1] == "-":
            self.index += 1
        require(self.index < len(self.text), "an incomplete JSON integer")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text) or self.text[self.index] not in "0123456789",
                    "a JSON integer has a leading zero")
        else:
            require(self.text[self.index] in "123456789", "an invalid JSON integer")
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        require(self.text[self.index:self.index + 1] not in (".", "e", "E"),
                "public timing and correctness records must contain exact integers")
        return int(self.text[first:self.index])

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "public JSON exceeded its bounded depth")
        self.whitespace()
        token = self.text[self.index:self.index + 1]
        if token == '"':
            return self.string()
        if token == "{":
            self.index += 1
            actual: dict[str, object] = {}
            self.whitespace()
            if self.text[self.index:self.index + 1] == "}":
                self.index += 1
                return actual
            while True:
                self.whitespace()
                key = self.string()
                require(key not in actual, "duplicate JSON keys conceal evidence")
                self.whitespace()
                require(self.text[self.index:self.index + 1] == ":", "missing JSON object separator")
                self.index += 1
                actual[key] = self.value(depth + 1)
                self.whitespace()
                token = self.text[self.index:self.index + 1]
                self.index += 1
                if token == "}":
                    return actual
                require(token == ",", "missing JSON object comma")
        if token == "[":
            self.index += 1
            actual: list[object] = []
            self.whitespace()
            if self.text[self.index:self.index + 1] == "]":
                self.index += 1
                return actual
            while True:
                actual.append(self.value(depth + 1))
                self.whitespace()
                token = self.text[self.index:self.index + 1]
                self.index += 1
                if token == "]":
                    return actual
                require(token == ",", "missing JSON array comma")
        for spelling, actual in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(spelling, self.index):
                self.index += len(spelling)
                return actual
        return self.number()

    def document(self) -> object:
        actual = self.value()
        self.whitespace()
        require(self.index == len(self.text), "concatenated or truncated JSON evidence")
        return actual


def quote(value: str) -> str:
    require(type(value) is str, "JSON object keys must remain strings")
    escapes = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f", "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    result = ['"']
    for item in value:
        code = ord(item)
        require(not 0xD800 <= code <= 0xDFFF, "unpaired JSON surrogate")
        result.append(escapes.get(item, "\\u" + format(code, "04x") if code < 32 else item))
    result.append('"')
    return "".join(result)


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "canonical JSON exceeded its depth bound")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is int:
        return str(value)
    if type(value) is str:
        return quote(value)
    if type(value) in (tuple, list):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value), "canonical object keys changed type")
        return "{" + ",".join(quote(key) + ":" + canonical(value[key], depth + 1)
                              for key in sorted(value)) + "}"
    raise FreezeError("unsupported canonical JSON value")


ANCHOR_TYPES = b'''
const MANDATORY_ANCHOR_CAPACITY: usize = 16;
const MANDATORY_ANCHOR_VALUES: usize = 8;
const MANDATORY_ANCHOR_DEPTH: usize = 64;

/// An exact necessary byte set; zero members conservatively means unknown.
#[derive(Clone, Copy)]
struct MandatoryAnchorPredicate {
    bytes: [u8; MANDATORY_ANCHOR_VALUES],
    count: u8,
}

impl MandatoryAnchorPredicate {
    #[inline]
    const fn unknown() -> Self {
        Self { bytes: [0; MANDATORY_ANCHOR_VALUES], count: 0 }
    }

    #[inline]
    fn literal(value: u8) -> Self {
        let mut result = Self::unknown();
        result.bytes[0] = value;
        result.count = 1;
        result
    }

    /// Union preserves every alternative; overflow disables the predicate.
    #[inline]
    fn union(&mut self, other: &Self) {
        if self.count == 0 || other.count == 0 {
            *self = Self::unknown();
            return;
        }
        for &value in &other.bytes[..usize::from(other.count)] {
            if self.bytes[..usize::from(self.count)].contains(&value) {
                continue;
            }
            if usize::from(self.count) == MANDATORY_ANCHOR_VALUES {
                *self = Self::unknown();
                return;
            }
            self.bytes[usize::from(self.count)] = value;
            self.count += 1;
        }
    }

    #[inline]
    fn same_set(&self, other: &Self) -> bool {
        self.count == other.count
            && self.bytes[..usize::from(self.count)]
                .iter()
                .all(|value| other.bytes[..usize::from(other.count)].contains(value))
    }
}

#[derive(Clone, Copy)]
struct MandatoryAnchorShape {
    columns: [MandatoryAnchorPredicate; MANDATORY_ANCHOR_CAPACITY],
    length: u8,
    exact: bool,
}

impl MandatoryAnchorShape {
    #[inline]
    const fn empty(exact: bool) -> Self {
        Self {
            columns: [MandatoryAnchorPredicate::unknown(); MANDATORY_ANCHOR_CAPACITY],
            length: 0,
            exact,
        }
    }

    #[inline]
    fn one(predicate: MandatoryAnchorPredicate) -> Self {
        let mut result = Self::empty(true);
        result.columns[0] = predicate;
        result.length = 1;
        result
    }

    /// Continue only through an expression with a fully proven fixed width.
    #[inline]
    fn append(&mut self, other: &Self) -> bool {
        let initial = usize::from(self.length);
        let available = MANDATORY_ANCHOR_CAPACITY - initial;
        let copied = available.min(usize::from(other.length));
        self.columns[initial..initial + copied]
            .copy_from_slice(&other.columns[..copied]);
        self.length = (initial + copied) as u8;
        if copied != usize::from(other.length) || !other.exact {
            self.exact = false;
            return false;
        }
        true
    }

    #[inline]
    fn union_alternative(&mut self, other: &Self) {
        let old_length = usize::from(self.length);
        let other_length = usize::from(other.length);
        let shared = old_length.min(other_length);
        for index in 0..shared {
            self.columns[index].union(&other.columns[index]);
        }
        self.length = shared as u8;
        self.exact = self.exact && other.exact && old_length == other_length;
    }
}
'''


ANCHOR_DERIVATION = b'''
/// Derive only byte predicates required on every original ordered AST path.
///
/// Fixed-width unknown atoms preserve offsets.  Alternative byte sets are
/// unioned; uncertain folding, unbounded width, backreferences, deep nesting,
/// and large sets disable only the uncertain predicate.  The original,
/// capture-aware ordered program still validates every selected start.
fn mandatory_anchor_shape(node: &Expr, depth: usize) -> MandatoryAnchorShape {
    if depth >= MANDATORY_ANCHOR_DEPTH {
        return MandatoryAnchorShape::empty(false);
    }
    match node {
        Expr::Lit(value, flags) if flags & (I | L) == 0 => {
            let predicate = u8::try_from(*value)
                .ok()
                .map_or(MandatoryAnchorPredicate::unknown(), MandatoryAnchorPredicate::literal);
            MandatoryAnchorShape::one(predicate)
        }
        Expr::Lit(_, _)
        | Expr::Dot(_)
        | Expr::Cat(_, _)
        | Expr::Class(_, _, _) => {
            MandatoryAnchorShape::one(MandatoryAnchorPredicate::unknown())
        }
        Expr::Anchor(_, _) | Expr::Boundary(_, _) | Expr::Look(_, _, _, _) => {
            MandatoryAnchorShape::empty(true)
        }
        Expr::Group(_, child) | Expr::Atomic(child) => {
            mandatory_anchor_shape(child, depth + 1)
        }
        Expr::Seq(children) => {
            let mut result = MandatoryAnchorShape::empty(true);
            for child in children {
                let next = mandatory_anchor_shape(child, depth + 1);
                if !result.append(&next) {
                    break;
                }
            }
            result
        }
        Expr::Alt(children) => {
            let mut branches = children.iter();
            let Some(first) = branches.next() else {
                return MandatoryAnchorShape::empty(true);
            };
            let mut result = mandatory_anchor_shape(first, depth + 1);
            for child in branches {
                let next = mandatory_anchor_shape(child, depth + 1);
                result.union_alternative(&next);
            }
            result
        }
        Expr::Cond(_, yes, no) => {
            let mut result = mandatory_anchor_shape(yes, depth + 1);
            let next = mandatory_anchor_shape(no, depth + 1);
            result.union_alternative(&next);
            result
        }
        Expr::Repeat(child, minimum, maximum, _) => {
            let child = mandatory_anchor_shape(child, depth + 1);
            if child.length == 0 {
                return MandatoryAnchorShape::empty(child.exact);
            }
            if *minimum == 0 {
                return MandatoryAnchorShape::empty(false);
            }
            if !child.exact {
                let mut result = child;
                result.exact = false;
                return result;
            }
            let bounded = (*minimum)
                .min(MANDATORY_ANCHOR_CAPACITY / usize::from(child.length) + 1);
            let mut result = MandatoryAnchorShape::empty(true);
            for _ in 0..bounded {
                if !result.append(&child) {
                    return result;
                }
            }
            if bounded != *minimum || maximum != &Some(*minimum) {
                result.exact = false;
            }
            result
        }
        Expr::Backref(_, _) => MandatoryAnchorShape::empty(false),
    }
}

fn mandatory_anchor_search(root: &Expr) -> Option<search::AnchorPlan> {
    let shape = mandatory_anchor_shape(root, 0);
    let first_offset = (0..usize::from(shape.length))
        .find(|&index| shape.columns[index].count != 0)?;
    let first_column = &shape.columns[first_offset];
    let first = search::AnchorSet::new(
        first_offset,
        &first_column.bytes[..usize::from(first_column.count)],
    )?;
    let second_offset = (0..usize::from(shape.length))
        .filter(|&index| index != first_offset && shape.columns[index].count != 0)
        .max_by_key(|&index| {
            let candidate = &shape.columns[index];
            let repetitions = (0..usize::from(shape.length))
                .filter(|&other| shape.columns[other].same_set(candidate))
                .count();
            (
                !candidate.same_set(first_column),
                MANDATORY_ANCHOR_VALUES - usize::from(candidate.count),
                MANDATORY_ANCHOR_CAPACITY - repetitions,
                index,
            )
        });
    let second = second_offset.and_then(|index| {
        let column = &shape.columns[index];
        search::AnchorSet::new(index, &column.bytes[..usize::from(column.count)])
    });
    search::AnchorPlan::new(first, second, usize::from(shape.length))
}

'''


ANCHOR_RUNTIME = b'''        if mode == 0
            && engine.start_anchor == SearchAnchor::Unrestricted
            && engine.leading_lookbehind.is_none()
            && let Some(plan) = engine.mandatory_anchor_search.as_ref()
            && let Some(values) = context.bytes.or_else(|| {
                context
                    .wide
                    .filter(|subject| subject.kind == 1)
                    .map(|subject| subject.data)
            })
        {
            let Some(next) = plan.next(values, start, context.end) else {
                return 0;
            };
            start = next;
        }
'''


ANCHOR_ENGINE_TESTS = b'''

#[cfg(test)]
mod mandatory_anchor_search_tests {
    use super::{mandatory_anchor_search, Expr, BYTE, I, L};

    fn literal(value: u8) -> Expr {
        Expr::Lit(u32::from(value), 0)
    }

    fn sequence(values: &[u8]) -> Expr {
        Expr::Seq(values.iter().copied().map(literal).collect())
    }

    #[test]
    fn alternative_suffix_union_rejects_every_impossible_dense_start() {
        let root = Expr::Group(
            1,
            Box::new(Expr::Alt(vec![sequence(b"AAAAAAB"), sequence(b"AAAAAAC")])),
        );
        let plan = mandatory_anchor_search(&root).expect("the common suffix is mandatory");
        assert_eq!(plan.next(b"AAAAAAAAAAAAAAAAAAD", 0, 19), None);
        assert_eq!(plan.next(b"AAAAAAAAAAAAAAAAB", 0, 17), Some(10));
        assert_eq!(plan.next(b"AAAAAAAAAAAAAAAAC", 0, 17), Some(10));
    }

    #[test]
    fn opposite_sparse_anchors_preserve_the_first_overlapping_position() {
        let dense = mandatory_anchor_search(&sequence(b"aaaaab")).unwrap();
        let sparse = mandatory_anchor_search(&sequence(b"bcaaaa")).unwrap();
        assert_eq!(dense.next(b"aaaaaaaaab7", 0, 11), Some(4));
        assert_eq!(sparse.next(b"bdaaaaaaaaaaaaa", 0, 15), None);
        assert_eq!(sparse.next(b"bbcaaaa", 0, 7), Some(1));
        assert_eq!(dense.next(b"aaaaab", 0, 5), None);
    }

    #[test]
    fn uncertain_semantics_do_not_erase_original_candidate_starts() {
        assert!(mandatory_anchor_search(&Expr::Lit(u32::from(b'A'), I)).is_none());
        assert!(mandatory_anchor_search(&Expr::Lit(u32::from(b'A'), BYTE | L)).is_none());
        assert!(mandatory_anchor_search(&Expr::Lit(0x212a, 0)).is_none());
        let variable = Expr::Seq(vec![
            Expr::Repeat(Box::new(literal(b'a')), 0, None, 0),
            literal(b'b'),
        ]);
        assert!(mandatory_anchor_search(&variable).is_none());
        let reference = Expr::Seq(vec![Expr::Backref(1, 0), literal(b'b')]);
        assert!(mandatory_anchor_search(&reference).is_none());
    }

    #[test]
    fn known_width_keeps_a_safe_later_literal_offset() {
        let root = Expr::Seq(vec![
            Expr::Repeat(Box::new(Expr::Dot(0)), 3, Some(3), 0),
            sequence(b"END"),
        ]);
        let plan = mandatory_anchor_search(&root).expect("fixed-width suffix");
        assert_eq!(plan.next(b"xxxEND", 0, 6), Some(0));
        assert_eq!(plan.next(b"xxEND", 0, 5), None);
        assert_eq!(plan.next(b"xxxENX", 0, 6), None);
    }
}
'''


ANCHOR_SEARCH = b'''
const ANCHOR_SET_CAPACITY: usize = 8;
const ANCHOR_SAMPLE: usize = 64;

/// At one proven fixed offset, admit every byte in a complete necessary set.
#[derive(Clone, Copy)]
pub(crate) struct AnchorSet {
    offset: usize,
    bytes: [u8; ANCHOR_SET_CAPACITY],
    count: u8,
}

impl AnchorSet {
    #[inline]
    pub(crate) fn new(offset: usize, values: &[u8]) -> Option<Self> {
        if values.is_empty() || values.len() > ANCHOR_SET_CAPACITY {
            return None;
        }
        let mut result = Self { offset, bytes: [0; ANCHOR_SET_CAPACITY], count: 0 };
        for &value in values {
            if result.bytes[..usize::from(result.count)].contains(&value) {
                continue;
            }
            result.bytes[usize::from(result.count)] = value;
            result.count += 1;
        }
        Some(result)
    }

    #[inline(always)]
    fn admits(&self, value: u8) -> bool {
        self.bytes[..usize::from(self.count)].contains(&value)
    }
}

/// Candidate positions are only filtered; the ordered regex VM remains final.
#[derive(Clone)]
pub(crate) struct AnchorPlan {
    first: AnchorSet,
    second: Option<AnchorSet>,
    width: usize,
}

impl AnchorPlan {
    #[inline]
    pub(crate) fn new(first: AnchorSet, second: Option<AnchorSet>, width: usize) -> Option<Self> {
        if width == 0 || first.offset >= width
            || second.is_some_and(|value| value.offset >= width || value.offset == first.offset)
        {
            return None;
        }
        Some(Self { first, second, width })
    }

    /// Return the earliest necessary candidate within the exact Python window.
    #[inline]
    pub(crate) fn next(&self, haystack: &[u8], from: usize, end: usize) -> Option<usize> {
        let end = end.min(haystack.len());
        if from > end || self.width > end.saturating_sub(from) {
            return None;
        }
        let last = end - self.width;
        if self.first.admits(haystack[from + self.first.offset])
            && self.second.is_none_or(|other| other.admits(haystack[from + other.offset]))
        {
            return Some(from);
        }

        let mut primary = self.first;
        let mut secondary = self.second;
        let available = last - from + 1;
        if available >= ANCHOR_SAMPLE * 2
            && let Some(other) = secondary
        {
            let samples = ANCHOR_SAMPLE.min(available);
            let first_count = (0..samples)
                .filter(|&index| primary.admits(haystack[from + index + primary.offset]))
                .count();
            let other_count = (0..samples)
                .filter(|&index| other.admits(haystack[from + index + other.offset]))
                .count();
            if other_count < first_count {
                primary = other;
                secondary = Some(self.first);
            }
        }

        #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
        if available >= 32 && is_x86_feature_detected!("avx2") {
            // SAFETY: feature detection precedes the call, and every 32-lane
            // load fits entirely inside the bounded Python subject window.
            return unsafe { avx2_anchor_search(haystack, from, last, &primary, secondary) };
        }

        scalar_anchor_search(haystack, from, last, &primary, secondary)
    }
}

#[inline]
fn scalar_anchor_search(
    haystack: &[u8],
    from: usize,
    last: usize,
    primary: &AnchorSet,
    secondary: Option<AnchorSet>,
) -> Option<usize> {
    let mut cursor = from;
    while cursor <= last {
        let candidate = if primary.count == 1 {
            let stop = last + primary.offset + 1;
            next_singleton(haystack, primary.bytes[0], cursor + primary.offset, stop)?
                - primary.offset
        } else {
            let mut found = cursor;
            while found <= last && !primary.admits(haystack[found + primary.offset]) {
                found += 1;
            }
            if found > last {
                return None;
            }
            found
        };
        if secondary.is_none_or(|other| other.admits(haystack[candidate + other.offset])) {
            return Some(candidate);
        }
        cursor = candidate + 1;
    }
    None
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "avx2")]
unsafe fn avx2_anchor_membership(values: __m256i, allowed: &AnchorSet) -> __m256i {
    let mut accepted = _mm256_setzero_si256();
    for &value in &allowed.bytes[..usize::from(allowed.count)] {
        accepted = _mm256_or_si256(
            accepted,
            _mm256_cmpeq_epi8(values, _mm256_set1_epi8(value as i8)),
        );
    }
    accepted
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "avx2")]
unsafe fn avx2_anchor_search(
    haystack: &[u8],
    from: usize,
    last: usize,
    primary: &AnchorSet,
    secondary: Option<AnchorSet>,
) -> Option<usize> {
    let mut cursor = from;
    while last - cursor >= 31 {
        // SAFETY: cursor + 31 <= last and every anchor offset is below the
        // proven required width, so both unaligned loads stay in the window.
        let initial = unsafe {
            _mm256_loadu_si256(haystack.as_ptr().add(cursor + primary.offset).cast::<__m256i>())
        };
        // SAFETY: this function is called only after AVX2 feature detection.
        let mut accepted = unsafe { avx2_anchor_membership(initial, primary) };
        if _mm256_movemask_epi8(accepted) != 0
            && let Some(other) = secondary
        {
            // SAFETY: the second fixed offset has the same checked bounds.
            let following = unsafe {
                _mm256_loadu_si256(haystack.as_ptr().add(cursor + other.offset).cast::<__m256i>())
            };
            // SAFETY: AVX2 was authenticated before this function was entered.
            accepted = _mm256_and_si256(
                accepted,
                unsafe { avx2_anchor_membership(following, &other) },
            );
        }
        let matches = _mm256_movemask_epi8(accepted) as u32;
        if matches != 0 {
            return Some(cursor + matches.trailing_zeros() as usize);
        }
        cursor += 32;
        if cursor > last {
            return None;
        }
    }
    scalar_anchor_search(haystack, cursor, last, primary, secondary)
}

'''


ANCHOR_SEARCH_TESTS = b'''

#[cfg(test)]
mod anchor_position_tests {
    use super::{AnchorPlan, AnchorSet};

    fn expected(haystack: &[u8], from: usize, end: usize, width: usize,
                first: (usize, &[u8]), second: Option<(usize, &[u8])>) -> Option<usize> {
        let end = end.min(haystack.len());
        if from > end || width > end.saturating_sub(from) {
            return None;
        }
        (from..=end - width).find(|&position| {
            first.1.contains(&haystack[position + first.0])
                && second.is_none_or(|other| other.1.contains(&haystack[position + other.0]))
        })
    }

    fn random(seed: &mut u64) -> u64 {
        *seed ^= *seed << 13;
        *seed ^= *seed >> 7;
        *seed ^= *seed << 17;
        *seed
    }

    #[test]
    fn exact_bounds_high_bytes_and_vector_edges() {
        let mut seed = 0x5245_4241_525f_4131_u64;
        for _case in 0..768 {
            let length = (random(&mut seed) % 193) as usize;
            let mut arena = vec![0_u8; length + 1];
            for byte in &mut arena {
                *byte = random(&mut seed) as u8;
            }
            let haystack = &arena[1..];
            let width = (random(&mut seed) % 16 + 1) as usize;
            let first_offset = (random(&mut seed) as usize) % width;
            let second_offset = (random(&mut seed) as usize) % width;
            let first_bytes = [0, 0x80, 0xff, random(&mut seed) as u8];
            let second_bytes = [b'A', b'B', random(&mut seed) as u8];
            let first = AnchorSet::new(first_offset, &first_bytes).unwrap();
            let second = (second_offset != first_offset)
                .then(|| AnchorSet::new(second_offset, &second_bytes).unwrap());
            let plan = AnchorPlan::new(first, second, width).unwrap();
            for from in [0, 1, 15, 16, 31, 32, 63, 64, length,
                         length.saturating_add(1), usize::MAX] {
                for end in [0, 1, 15, 16, 31, 32, 63, 64, length, usize::MAX] {
                    let want = expected(
                        haystack, from, end, width, (first_offset, &first_bytes),
                        (second_offset != first_offset)
                            .then_some((second_offset, &second_bytes)),
                    );
                    assert_eq!(plan.next(haystack, from, end), want);
                }
            }
        }
    }

    #[test]
    fn opposite_anchor_density_and_overlaps_preserve_leftmost_order() {
        let first = AnchorSet::new(0, b"a").unwrap();
        let last = AnchorSet::new(5, b"b").unwrap();
        let plan = AnchorPlan::new(first, Some(last), 6).unwrap();
        let mut dense = vec![b'a'; 2048];
        dense.push(b'b');
        assert_eq!(plan.next(&dense, 0, dense.len()), Some(2043));

        let first = AnchorSet::new(0, b"b").unwrap();
        let last = AnchorSet::new(5, b"a").unwrap();
        let plan = AnchorPlan::new(first, Some(last), 6).unwrap();
        let mut sparse = vec![b'b', b'd'];
        sparse.extend(std::iter::repeat_n(b'a', 2048));
        assert_eq!(plan.next(&sparse, 0, sparse.len()), None);
        assert_eq!(plan.next(b"bbcaaaa", 0, 7), Some(1));
    }
}
'''


def replace_once(source: bytes, old: bytes, new: bytes, label: str) -> bytes:
    require(source.count(old) == 1, "exactly one first-party source anchor changed: " + label)
    return source.replace(old, new, 1)


def transform_engine(original: bytes) -> bytes:
    result = replace_once(
        original,
        b"const MANDATORY_LITERAL_PREFIX_CAPACITY: usize = 16;\n",
        ANCHOR_TYPES + b"\nconst MANDATORY_LITERAL_PREFIX_CAPACITY: usize = 16;\n",
        "owned anchor predicate and shape definitions",
    )
    result = replace_once(
        result,
        b"    mandatory_literal_prefix: Option<MandatoryLiteralPrefix>,\n",
        b"    mandatory_literal_prefix: Option<MandatoryLiteralPrefix>,\n"
        b"    mandatory_anchor_search: Option<search::AnchorPlan>,\n",
        "owned engine anchor plan field",
    )
    result = replace_once(
        result,
        b"/// Derive only byte prefixes that every original, ordered AST path requires.\n",
        ANCHOR_DERIVATION
        + b"/// Derive only byte prefixes that every original, ordered AST path requires.\n",
        "owned conservative ordered-AST derivation",
    )
    source = (
        b"            let prefix = mandatory_literal_prefix(&root, 0);\n"
        b"            let mandatory_literal_prefix = (prefix.length >= 2).then_some(prefix);\n"
    )
    result = replace_once(
        result,
        source,
        source + b"            let mandatory_anchor_search = mandatory_anchor_search(&root);\n",
        "ordinary owned compiler plan construction",
    )
    source = (
        b"    let prefix = mandatory_literal_prefix(&root, 0);\n"
        b"    let mandatory_literal_prefix = (prefix.length >= 2).then_some(prefix);\n"
    )
    result = replace_once(
        result,
        source,
        source + b"    let mandatory_anchor_search = mandatory_anchor_search(&root);\n",
        "owned scanner compiler plan construction",
    )
    engine_members = b"                mandatory_literal_prefix,\n                mandatory_run_delimiter,\n"
    result = replace_once(
        result,
        engine_members,
        b"                mandatory_literal_prefix,\n"
        b"                mandatory_anchor_search,\n"
        b"                mandatory_run_delimiter,\n",
        "ordinary owned engine plan ownership",
    )
    engine_members = b"        mandatory_literal_prefix,\n        mandatory_run_delimiter,\n"
    result = replace_once(
        result,
        engine_members,
        b"        mandatory_literal_prefix,\n"
        b"        mandatory_anchor_search,\n"
        b"        mandatory_run_delimiter,\n",
        "owned scanner engine plan ownership",
    )
    old_test_members = b"            mandatory_literal_prefix: None,\n            mandatory_run_delimiter: None,\n"
    require(result.count(old_test_members) == 2,
            "both original Rust test-only Engine constructors are mandatory")
    result = result.replace(
        old_test_members,
        b"            mandatory_literal_prefix: None,\n"
        b"            mandatory_anchor_search: None,\n"
        b"            mandatory_run_delimiter: None,\n",
    )
    runtime_marker = (
        b"        if mode == 0\n"
        b"            && start < context.end\n"
        b"            && let Some(starts) = &engine.starts\n"
    )
    result = replace_once(result, runtime_marker, ANCHOR_RUNTIME + runtime_marker,
                          "owned ordered-VM candidate-start filtering")
    return result + ANCHOR_ENGINE_TESTS


def transform_search(original: bytes) -> bytes:
    marker = b"/// A compiled, exact representation of any subset of the 256 possible bytes.\n"
    result = replace_once(original, marker, ANCHOR_SEARCH + marker,
                          "owned adaptive scalar and runtime-checked AVX2 anchor filter")
    return result + ANCHOR_SEARCH_TESTS


def parse_document(raw: bytes, label: str) -> dict[str, object]:
    actual = StrictJSON(raw).document()
    require(type(actual) is dict, "a JSON object is mandatory: " + label)
    return actual


def positive_integer(value: object, label: str) -> int:
    require(type(value) is int and value > 0, "a positive exact integer is mandatory: " + label)
    return value


def check_practice_evidence(owners: dict[str, bytes]) -> dict[str, object]:
    rust = parse_document(owners["rust_practice_correctness"], "Rust public correctness")
    python = parse_document(owners["python_practice_correctness"], "Python public correctness")
    for name, document, candidate_count in (("rust", rust, 3), ("stdlib", python, 0)):
        require(document.get("engine") == name and document.get("case_count") == 416
                and document.get("status") == "PASS"
                and document.get("matrix_sha256") == MATRIX_SHA256
                and document.get("records_sha256") == PRACTICE_RECORDS_SHA256
                and document.get("candidate_import_count") == candidate_count
                and document.get("clock_samples") == 0
                and document.get("holdout_files_read") == 0
                and document.get("archive_files_read") == 0
                and document.get("timing_trials_run") == 0
                and type(document.get("records")) is list
                and len(document["records"]) == 416,
                "the frozen actual 416-case correctness result changed: " + name)
    require(rust["records"] == python["records"],
            "the actual Rust and official Python public results are no longer identical")

    paired = parse_document(owners["public_paired_timings"], "actual public paired timings")
    require(paired.get("schema") == "rebar-rust-fresh-public-profile-v1-paired-timing-rows"
            and paired.get("matrix_sha256") == MATRIX_SHA256
            and paired.get("rows_sha256")
            == "ce5ddb143be0d58588d2b18540c0db1b716eebb138cfe32a04690a0efe62c378"
            and type(paired.get("rows")) is list and len(paired["rows"]) == 1664,
            "the full four-round, 416-case paired public evidence changed")
    dense: list[dict[str, object]] = []
    for item in paired["rows"]:
        require(type(item) is dict, "an actual paired practice timing row changed type")
        positive_integer(item.get("baseline_elapsed_ns"), "Python nanoseconds")
        positive_integer(item.get("rust_elapsed_ns"), "Rust nanoseconds")
        require(item.get("correctness_checks_per_engine") == 5
                and item.get("iterations") == 3
                and item.get("round") in (0, 1, 2, 3)
                and item.get("pair_order") in (["stdlib", "rust"], ["rust", "stdlib"]),
                "the original correctness-gated paired timing protocol changed")
        if item.get("cohort") == "mandatory_literal_dense_same_first_byte":
            dense.append(item)
    require(len(dense) == 416, "the independently measured dense-anchor cohort changed")
    baseline = sum(positive_integer(row.get("baseline_elapsed_ns"), "dense Python time")
                   for row in dense)
    candidate = sum(positive_integer(row.get("rust_elapsed_ns"), "dense Rust time")
                    for row in dense)
    require(baseline == 21797729 and candidate == 102371349,
            "the actual preserved dense-prefix slowdown changed")

    worst = [row for row in dense if row.get("case") == "rust-public-profile.v1.0036"
             and row.get("operation") == "pattern.search"]
    require(len(worst) == 4
            and sum(positive_integer(row.get("baseline_elapsed_ns"), "worst Python time")
                    for row in worst) == 254724
            and sum(positive_integer(row.get("rust_elapsed_ns"), "worst Rust time")
                    for row in worst) == 2554459,
            "the observed tenfold fixed-offset alternation regression disappeared")

    manifest = parse_document(owners["public_profile_manifest"], "public profile manifest")
    require(manifest.get("case_count") == 416 and manifest.get("dataset_count") == 16
            and manifest.get("operation_count") == 26
            and manifest.get("matrix_sha256") == MATRIX_SHA256
            and manifest.get("pinned_cpython") == "3.14.6"
            and manifest.get("pinned_python") == PYTHON,
            "the public-only profiler source freeze changed")

    cargo = owners["rust_manifest"]
    lock = owners["rust_lock"]
    require(b"[dependencies]" not in cargo and b"[[package]]" in lock
            and lock.count(b"[[package]]") == 1
            and b'name = "rebar-rust-continuation"' in lock,
            "the Rust replacement no longer has exactly one first-party package")
    require(b"Runtime-selected AVX2 first-and-last filter" in owners["owned_simd_search_results"]
            and b"55.89" in owners["owned_simd_search_results"]
            and b"50.02" in owners["owned_simd_search_results"]
            and b"unsafe fn avx2_first_last_inner" in owners["owned_simd_search_research"],
            "the previously measured first-party SIMD research was altered")
    return {
        "public_case_count": 416,
        "paired_row_count": 1664,
        "dense_paired_row_count": len(dense),
        "dense_python_elapsed_ns": baseline,
        "dense_rust_elapsed_ns": candidate,
        "worst_alternation_python_elapsed_ns": 254724,
        "worst_alternation_rust_elapsed_ns": 2554459,
        "records_sha256": PRACTICE_RECORDS_SHA256,
    }


def model_union(left: tuple[int, ...] | None,
                right: tuple[int, ...] | None) -> tuple[int, ...] | None:
    if left is None or right is None:
        return None
    result = list(left)
    for value in right:
        if value not in result:
            if len(result) == SET_CAPACITY:
                return None
            result.append(value)
    return tuple(result)


def model_shape(node: tuple[object, ...], depth: int = 0) -> tuple[list[tuple[int, ...] | None], bool]:
    if depth >= 64:
        return [], False
    kind = node[0]
    if kind == "lit":
        value, flags = node[1], node[2]
        return [((value,) if type(value) is int and 0 <= value <= 255
                 and type(flags) is int and flags & 6 == 0 else None)], True
    if kind in ("dot", "class"):
        return [None], True
    if kind in ("look", "anchor", "boundary", "empty"):
        return [], True
    if kind == "backref":
        return [], False
    if kind in ("group", "atomic"):
        return model_shape(node[1], depth + 1)
    if kind in ("alt", "cond"):
        branches = node[1]
        if not branches:
            return [], True
        actual, exact = model_shape(branches[0], depth + 1)
        for branch in branches[1:]:
            other, other_exact = model_shape(branch, depth + 1)
            previous = len(actual)
            count = min(previous, len(other))
            actual = [model_union(actual[index], other[index]) for index in range(count)]
            exact = exact and other_exact and previous == len(other)
        return actual, exact
    if kind == "seq":
        actual: list[tuple[int, ...] | None] = []
        for child in node[1]:
            following, exact = model_shape(child, depth + 1)
            count = min(ANCHOR_CAPACITY - len(actual), len(following))
            actual.extend(following[:count])
            if count != len(following) or not exact:
                return actual, False
        return actual, True
    if kind == "repeat":
        child, minimum, maximum = node[1], node[2], node[3]
        shape, exact = model_shape(child, depth + 1)
        if len(shape) == 0:
            return [], exact
        if minimum == 0:
            return [], False
        if not exact:
            return shape, False
        actual: list[tuple[int, ...] | None] = []
        for _ in range(min(minimum, ANCHOR_CAPACITY // len(shape) + 1)):
            count = min(ANCHOR_CAPACITY - len(actual), len(shape))
            actual.extend(shape[:count])
            if count != len(shape):
                return actual, False
        return actual, maximum == minimum and len(actual) == len(shape) * minimum
    raise FreezeError("unknown native-equivalent synthetic AST")


def model_plan(node: tuple[object, ...]) -> tuple[int, tuple[int, ...], int | None, tuple[int, ...] | None, int] | None:
    columns, _ = model_shape(node)
    first = next((index for index, value in enumerate(columns) if value is not None), None)
    if first is None:
        return None
    initial = columns[first]
    require(initial is not None, "the first modeled byte predicate disappeared")
    candidates = [index for index, value in enumerate(columns)
                  if index != first and value is not None]
    second = max(candidates,
                 key=lambda index: (set(columns[index]) != set(initial),
                                    SET_CAPACITY - len(columns[index]),
                                    ANCHOR_CAPACITY - sum(
                                        item is not None and set(item) == set(columns[index])
                                        for item in columns
                                    ), index),
                 default=None)
    return first, initial, second, columns[second] if second is not None else None, len(columns)


def model_next(subject: bytes, start: int, end: int,
               plan: tuple[int, tuple[int, ...], int | None, tuple[int, ...] | None, int]) -> int | None:
    first_offset, first, second_offset, second, width = plan
    end = min(end, len(subject))
    if start > end or width > end - start:
        return None
    for index in range(start, end - width + 1):
        if subject[index + first_offset] not in first:
            continue
        if second is not None and second_offset is not None and subject[index + second_offset] not in second:
            continue
        return index
    return None


def model_language(node: tuple[object, ...], alphabet: tuple[int, ...], depth: int = 0) -> list[tuple[int, ...]]:
    require(depth < 16, "a synthetic semantic expression escaped its depth bound")
    kind = node[0]
    if kind == "lit":
        value, flags = node[1], node[2]
        if flags & 2 and value in (ord("A"), ord("a")):
            return [(ord("A"),), (ord("a"),)]
        return [(value,)]
    if kind in ("dot", "class"):
        return [(item,) for item in alphabet]
    if kind in ("look", "anchor", "boundary", "empty"):
        return [()]
    if kind == "backref":
        return [(item,) for item in alphabet]
    if kind in ("group", "atomic"):
        return model_language(node[1], alphabet, depth + 1)
    if kind in ("alt", "cond"):
        result: list[tuple[int, ...]] = []
        for child in node[1]:
            result.extend(model_language(child, alphabet, depth + 1))
        return result
    if kind == "seq":
        actual: list[tuple[int, ...]] = [()]
        for child in node[1]:
            additions = model_language(child, alphabet, depth + 1)
            actual = [prefix + suffix for prefix in actual for suffix in additions][:128]
        return actual
    if kind == "repeat":
        options = model_language(node[1], alphabet, depth + 1)
        minimum = node[2]
        maximum = min(node[3] if node[3] is not None else minimum + 2, minimum + 2)
        result: list[tuple[int, ...]] = []
        for count in range(minimum, maximum + 1):
            actual: list[tuple[int, ...]] = [()]
            for _ in range(count):
                actual = [prefix + suffix for prefix in actual for suffix in options][:128]
            result.extend(actual)
        return result[:128]
    raise FreezeError("unknown native-equivalent synthetic language")


def model_original(words: list[tuple[int, ...]], subject: bytes, start: int, end: int) -> tuple[int, int] | None:
    end = min(end, len(subject))
    if start > end:
        return None
    for position in range(start, end + 1):
        for branch, value in enumerate(words):
            if len(value) <= end - position and all(
                unit <= 255 and subject[position + offset] == unit
                for offset, unit in enumerate(value)
            ):
                return position, branch
    return None


def model_filtered(words: list[tuple[int, ...]], subject: bytes, start: int, end: int,
                   plan: tuple[int, tuple[int, ...], int | None, tuple[int, ...] | None, int] | None) -> tuple[int, int] | None:
    if plan is None:
        return model_original(words, subject, start, end)
    end = min(end, len(subject))
    while start <= end:
        position = model_next(subject, start, end, plan)
        if position is None:
            return None
        for branch, value in enumerate(words):
            if len(value) <= end - position and all(
                unit <= 255 and subject[position + offset] == unit
                for offset, unit in enumerate(value)
            ):
                return position, branch
        start = position + 1
    return None


def next_random(seed: int) -> int:
    mask = (1 << 64) - 1
    seed ^= (seed << 13) & mask
    seed ^= seed >> 7
    seed ^= (seed << 17) & mask
    return seed & mask


def check_model() -> dict[str, int]:
    literal = lambda value, flags=0: ("lit", value, flags)
    sequence = lambda values: ("seq", tuple(literal(value) for value in values))
    patterns: list[tuple[object, ...]] = [
        sequence(b"aaaaab"),
        sequence(b"bcaaaa"),
        ("group", ("alt", (sequence(b"AAAAAAB"), sequence(b"AAAAAAC")))),
        ("seq", (("repeat", ("dot",), 3, 3), sequence(b"END"))),
        ("seq", (("look",), literal(ord("A")), literal(ord("B")))),
        ("seq", (("boundary",), ("group", sequence(b"ab")))),
        ("atomic", ("alt", (sequence(b"ab"), sequence(b"abc")))),
        ("cond", (sequence(b"AB"), sequence(b"AC"))),
        ("seq", (("repeat", literal(ord("a")), 0, None), literal(ord("b")))),
        ("seq", (("repeat", literal(ord("a")), 1, None), literal(ord("b")))),
        ("seq", (("backref",), literal(ord("b")))),
        ("seq", (literal(ord("A"), 2), literal(ord("b")))),
        ("seq", (literal(ord("A"), 4), literal(ord("b")))),
        ("seq", (literal(0x212A), literal(ord("b")))),
        sequence(bytes((0x80, 0xff))),
        ("alt", (sequence(b"ab"), ("empty",))),
        ("repeat", ("look",), 0, None),
        ("repeat", sequence(b"ab"), 2, 2),
    ]
    alphabet = (ord("a"), ord("A"), ord("b"), ord("B"), ord("C"), ord("d"), ord("E"), ord("N"), ord("D"), 0x80, 0xff)
    seed = 0x52454241525F4131
    checks = 0
    for expression in patterns:
        plan = model_plan(expression)
        words = model_language(expression, alphabet)
        for size in (0, 1, 2, 3, 5, 7, 15, 16, 17, 31, 32, 33, 63, 64, 65, 129):
            subject = bytearray()
            for _ in range(size):
                seed = next_random(seed)
                subject.append(alphabet[seed % len(alphabet)])
            original = bytes(subject)
            for first in (0, 1, size // 2, size, size + 1):
                for last in (0, 1, size // 2, size, size + 1, (1 << 64) - 1):
                    expected = model_original(words, original, first, last)
                    actual = model_filtered(words, original, first, last, plan)
                    require(actual == expected,
                            "fixed-offset filtering changed a match, branch, overlap, or window")
                    checks += 1
            for word in words[:8]:
                if any(value > 255 for value in word):
                    continue
                for beginning in (b"", b"a", b"aaa", bytes((0x80,))):
                    witness = beginning + bytes(word) + b"ab"
                    expected = model_original(words, witness, 0, len(witness))
                    actual = model_filtered(words, witness, 0, len(witness), plan)
                    require(actual == expected,
                            "fixed-offset filtering changed an ordered positive witness")
                    checks += 1

    alternative = model_plan(patterns[2])
    require(alternative is not None and alternative[2] == 6
            and set(alternative[3]) == {ord("B"), ord("C")},
            "the actual dense alternative must derive its required {B,C} suffix")
    require(model_next(b"A" * 2048 + b"D", 0, 2049, alternative) is None,
            "the preserved tenfold dense regression was not filtered")
    dense = model_plan(patterns[0])
    sparse = model_plan(patterns[1])
    require(dense is not None and sparse is not None
            and model_next(b"a" * 2048 + b"b7", 0, 2050, dense) == 2043
            and model_next(b"b" + b"d" + b"a" * 2048, 0, 2050, sparse) is None,
            "the opposite public anchor-density cohorts changed their exact answers")
    return {"differential_checks": checks, "seed": 0x52454241525F4131,
            "semantic_pattern_count": len(patterns)}


def check_transformed_sources(original_lib: bytes, original_search: bytes,
                              transformed_lib: bytes, transformed_search: bytes) -> None:
    require(transformed_lib != original_lib and transformed_search != original_search,
            "both independent first-party source transformations are mandatory")
    for marker in (
        b"fn mandatory_anchor_shape(node: &Expr, depth: usize)",
        b"Expr::Alt(children) =>",
        b"result.union_alternative(&next);",
        b"Expr::Backref(_, _) => MandatoryAnchorShape::empty(false)",
        b"flags & (I | L) == 0",
        b"engine.leading_lookbehind.is_none()",
        b"subject.kind == 1",
        b"let Some(next) = plan.next(values, start, context.end)",
    ):
        require(marker in transformed_lib, "a required conservative Rust proof disappeared")
    for marker in (
        b"pub(crate) struct AnchorPlan",
        b"pub(crate) fn next(&self, haystack: &[u8], from: usize, end: usize)",
        b"is_x86_feature_detected!(\"avx2\")",
        b"unsafe fn avx2_anchor_search",
        b"_mm256_loadu_si256",
        b"_mm256_movemask_epi8",
        b"scalar_anchor_search",
        b"next_singleton(haystack, primary.bytes[0]",
        b"other_count < first_count",
    ):
        require(marker in transformed_search, "a required first-party search safeguard disappeared")
    inserted = b"\n".join((ANCHOR_TYPES, ANCHOR_DERIVATION, ANCHOR_RUNTIME,
                            ANCHOR_ENGINE_TESTS, ANCHOR_SEARCH, ANCHOR_SEARCH_TESTS))
    reject_delegation(inserted)
    require(transformed_lib.count(ANCHOR_TYPES) == 1
            and transformed_lib.count(ANCHOR_DERIVATION) == 1
            and transformed_lib.count(ANCHOR_RUNTIME) == 1
            and transformed_lib.count(ANCHOR_ENGINE_TESTS) == 1
            and transformed_search.count(ANCHOR_SEARCH) == 1
            and transformed_search.count(ANCHOR_SEARCH_TESTS) == 1,
            "every complete inserted block must occur exactly once")
    require(transformed_lib.count(b"mandatory_anchor_search: Option<search::AnchorPlan>") == 1
            and transformed_lib.count(b"let mandatory_anchor_search = mandatory_anchor_search(&root);") == 2
            and transformed_lib.count(b"mandatory_anchor_search: None,") == 2
            and transformed_lib.count(b"mod mandatory_anchor_search_tests") == 1
            and transformed_search.count(b"mod anchor_position_tests") == 1,
            "the two compile paths, test constructors, or owned tests changed cardinality")


def reject_delegation(inserted: bytes) -> None:
    require(type(inserted) is bytes and len(inserted) > 0,
            "complete inserted first-party source bytes are mandatory")
    for forbidden in (
        b"extern crate regex", b"use regex::", b"regex::Regex", b"_sre", b"pcre2",
        b"oniguruma", b"rebar_match(", b"dlopen(", b"ctypes", b"std::process::",
    ):
        require(forbidden not in inserted,
                "a complete inserted first-party block delegates matching")


def validate_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PYTHON
            and os.path.realpath(sys.executable) == PYTHON
            and os.path.abspath(__file__) == ROOT + "/" + SOURCE
            and os.path.realpath(__file__) == ROOT + "/" + SOURCE
            and os.path.realpath(ROOT) == ROOT,
            "use only the exact owned source under isolated pinned CPython 3.14.6")
    require(not any(name in sys.modules for name in ("re", "_sre", "regex")),
            "a regex engine escaped into candidate-free source verification")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a candidate escaped into candidate-free source verification")


def validate_contract(contract: dict[str, object], source_digest: str,
                      protocol_digest: str, actual: dict[str, object],
                      derived: dict[str, object]) -> None:
    require(contract.get("schema") == SCHEMA
            and contract.get("version") == 1
            and contract.get("source") == SOURCE
            and contract.get("protocol") == PROTOCOL
            and contract.get("contract") == CONTRACT
            and contract.get("goal_sha256") == OWNERS[0][2]
            and contract.get("phase") == "CANDIDATES"
            and contract.get("holdout") == "NOT OPENED"
            and contract.get("final_performance") == "NOT MEASURED"
            and contract.get("external_rust_dependency_count") == 0
            and contract.get("matching_engine") == "FIRST-PARTY ORDERED RUST VM"
            and contract.get("candidate_native_execution") == "NOT RUN"
            and contract.get("public_practice") == actual
            and contract.get("derived") == derived,
            "the immutable optimization source contract changed")
    require(contract.get("source_sha256") == source_digest
            and contract.get("protocol_sha256") == protocol_digest,
            "the source and protocol are not frozen by the experiment contract")


def verify_sources() -> dict[str, object]:
    source = bounded_file(SOURCE)
    protocol = bounded_file(PROTOCOL)
    contract_raw = bounded_file(CONTRACT)
    owners: dict[str, bytes] = {}
    for role, path, digest, size, device, inode in OWNERS:
        owners[role] = owner_bytes(path, digest, size, device, inode)
    actual = check_practice_evidence(owners)
    transformed_lib = transform_engine(owners["rust_engine_source"])
    transformed_search = transform_search(owners["rust_search_source"])
    check_transformed_sources(owners["rust_engine_source"], owners["rust_search_source"],
                              transformed_lib, transformed_search)
    model = check_model()
    derived = {
        "engine": {"path": LIB_VARIANT, "sha256": sha256(transformed_lib),
                   "bytes": len(transformed_lib)},
        "search": {"path": SEARCH_VARIANT, "sha256": sha256(transformed_search),
                   "bytes": len(transformed_search)},
    }
    contract = parse_document(contract_raw, "frozen mandatory-anchor contract")
    validate_contract(contract, sha256(source), sha256(protocol), actual, derived)
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "source_sha256": sha256(source),
        "protocol_sha256": sha256(protocol),
        "contract_sha256": sha256(contract_raw),
        "derived": derived,
        "public_practice": actual,
        "synthetic": model,
        "source_owner_count": len(OWNERS) + 3,
        "candidate_processes": 0,
        "native_libraries_loaded": 0,
        "clocks_sampled": 0,
        "workspace_mutations": 0,
        "archives_opened": 0,
        "holdout_opened": 0,
        "performance_change": "NOT MEASURED",
    }


def expect_block(kind: str, callback: object) -> None:
    before = BLOCKED[kind]
    try:
        callback()
    except FreezeError:
        pass
    else:
        raise FreezeError("a hostile source-mode operation escaped the physical wall")
    require(BLOCKED[kind] == before + 1,
            "a hostile source operation was blocked under the wrong category")


def hostile_self_test() -> dict[str, int]:
    expect_block("workspace_write", lambda: builtins.open(ROOT + "/" + SOURCE, "wb"))
    expect_block("workspace_write", lambda: os.open(ROOT + "/" + SOURCE, os.O_WRONLY))
    expect_block("restricted_case", lambda: builtins.open(ROOT + "/oracle/phase3/sealed-holdout.json"))
    expect_block("restricted_case", lambda: builtins.open(ROOT + "/oracle/phase2/failure-archive.gz"))
    expect_block("restricted_case", lambda: builtins.open(ROOT + "/candidates/_rust_engine.so"))
    expect_block("candidate_execution", lambda: builtins.open(ROOT + "/candidates/rust_candidate.py"))
    expect_block("candidate_execution", lambda: builtins.open(ROOT + "/candidates/rust/src/../lib.rs"))
    expect_block("foreign_read", lambda: builtins.open("/etc/passwd"))
    expect_block("foreign_read", lambda: os.listdir(ROOT))
    expect_block("native", lambda: __import__("subprocess"))
    expect_block("process", lambda: os.system("true"))
    expect_block("clock", lambda: time.time())
    expect_block("clock", lambda: time.perf_counter_ns())
    expect_block("workspace_write", lambda: os.mkdir(ROOT + "/forbidden-mandatory-anchor"))

    malformed = (
        b'{"same":1,"same":2}', b'{"trailing":1}{}', b'{"zero":01}',
        b'{"fraction":1.5}', b'{"nan":NaN}', b'{"bad":"\\q"}',
        b'{"surrogate":"\\ud800"}', b'{"object":[1,}', b'[] trailing',
    )
    rejected = 0
    for raw in malformed:
        try:
            StrictJSON(raw).document()
        except (FreezeError, IndexError, ValueError):
            rejected += 1
        else:
            raise FreezeError("a malformed public JSON document was accepted")
    require(rejected == len(malformed), "a malformed JSON control escaped")

    for malformed_set in ((), tuple(range(9))):
        if malformed_set:
            require(model_union(tuple(malformed_set[:8]), tuple(malformed_set[8:])) is None,
                    "an overflowing alternative byte set was not disabled")
        else:
            require(model_union(None, ()) is None,
                    "an unknown alternative byte set was treated as exact")
    forbidden_controls = (
        b"extern crate regex", b"use regex::Regex", b"regex::Regex::new",
        b"_sre", b"pcre2", b"oniguruma", b"rebar_match(", b"dlopen(",
        b"ctypes", b"std::process::Command",
    )
    for control in forbidden_controls:
        try:
            reject_delegation(ANCHOR_TYPES + b"\n" + control + ANCHOR_DERIVATION)
        except FreezeError:
            pass
        else:
            raise FreezeError("a complete inserted-block delegation control escaped")
    return {"physically_blocked_controls": sum(BLOCKED.values()),
            "malformed_json_controls": rejected,
            "rejected_delegation_controls": len(forbidden_controls),
            "blocked_clock_controls": BLOCKED["clock"],
            "blocked_native_controls": BLOCKED["native"],
            "blocked_candidate_controls": BLOCKED["candidate_execution"]}


def checked_digest(value: str, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value)
            and len(set(value)) > 1,
            "a real lowercase SHA-256 is required: " + label)
    return value


def parse_arguments(arguments: list[str]) -> tuple[str, dict[str, str], frozenset[str]]:
    require(type(arguments) is list and len(arguments) > 0,
            "one explicit source-verification, self-test, or root-only action is mandatory")
    mode = arguments[0]
    require(mode in ("--verify-source", "--self-test", "--apply"),
            "unknown or missing mandatory-anchor action")
    options: dict[str, str] = {}
    flags: set[str] = set()
    index = 1
    while index < len(arguments):
        item = arguments[index]
        if item in ("--root-authorized", "--frozen-committed-pushed"):
            require(item not in flags, "duplicate root authorization")
            flags.add(item)
            index += 1
            continue
        require(item in ("--source-sha256", "--protocol-sha256", "--contract-sha256")
                and item not in options and index + 1 < len(arguments),
                "unknown, duplicate, or incomplete mandatory-anchor option")
        options[item] = checked_digest(arguments[index + 1], item)
        index += 2
    if mode == "--apply":
        require(set(options) == {"--source-sha256", "--protocol-sha256", "--contract-sha256"}
                and flags == {"--root-authorized", "--frozen-committed-pushed"},
                "variant creation requires all three frozen hashes and both root authorizations")
    else:
        require(not options and not flags,
                "source-only modes reject candidate activation and root-only arguments")
    return mode, options, frozenset(flags)


def write_exclusive(directory: int, name: str, raw: bytes) -> dict[str, object]:
    descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600,
                         dir_fd=directory)
    try:
        written = 0
        while written < len(raw):
            count = os.write(descriptor, raw[written:])
            require(count > 0, "exclusive Rust variant write made no progress")
            written += count
        os.fsync(descriptor)
        owner = os.fstat(descriptor)
        require(stat.S_ISREG(owner.st_mode) and owner.st_size == len(raw)
                and stat.S_IMODE(owner.st_mode) == 0o600,
                "exclusive Rust variant ownership changed during publication")
    finally:
        os.close(descriptor)
    return {"bytes": len(raw), "device": owner.st_dev, "inode": owner.st_ino,
            "mode": "0600", "sha256": sha256(raw)}


def apply_root_only(result: dict[str, object], options: dict[str, str]) -> dict[str, object]:
    global WALL_ACTIVE
    require(options["--source-sha256"] == result["source_sha256"]
            and options["--protocol-sha256"] == result["protocol_sha256"]
            and options["--contract-sha256"] == result["contract_sha256"],
            "root did not authenticate the exact committed source-freeze triple")
    owners: dict[str, bytes] = {}
    for role, path, digest, size, device, inode in OWNERS:
        if role in ("rust_engine_source", "rust_search_source"):
            owners[role] = owner_bytes(path, digest, size, device, inode)
    engine = transform_engine(owners["rust_engine_source"])
    search = transform_search(owners["rust_search_source"])
    require(result["derived"] == {
        "engine": {"path": LIB_VARIANT, "sha256": sha256(engine), "bytes": len(engine)},
        "search": {"path": SEARCH_VARIANT, "sha256": sha256(search), "bytes": len(search)},
    }, "the exact predicted Rust variants changed before exclusive creation")

    # Only this fully authenticated, explicitly root-authorized action lowers
    # the source-only wall.  Both outputs are fresh O_EXCL descendants of one
    # fresh O_EXCL mode-0700 directory; existing candidates remain untouched.
    WALL_ACTIVE = False
    parent = os.open(ROOT + "/candidates/rust/variants",
                     os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        os.mkdir("mandatory_anchor_search_v1", 0o700, dir_fd=parent)
        directory = os.open("mandatory_anchor_search_v1",
                            os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW,
                            dir_fd=parent)
        try:
            identity = os.fstat(directory)
            require(stat.S_ISDIR(identity.st_mode)
                    and stat.S_IMODE(identity.st_mode) == 0o700,
                    "the owned exclusive Rust variant directory is unsafe")
            engine_owner = write_exclusive(directory, "lib.rs", engine)
            search_owner = write_exclusive(directory, "search.rs", search)
            os.fsync(directory)
        finally:
            os.close(directory)
        os.fsync(parent)
    finally:
        os.close(parent)
    result = dict(result)
    result["status"] = "APPLIED"
    result["workspace_mutations"] = 3
    result["created"] = {
        "directory": {"path": VARIANT_DIRECTORY, "device": identity.st_dev,
                      "inode": identity.st_ino, "mode": "0700"},
        "engine": {"path": LIB_VARIANT, **engine_owner},
        "search": {"path": SEARCH_VARIANT, **search_owner},
    }
    return result


def main(arguments: list[str] | None = None) -> int:
    validate_runtime()
    mode, options, _flags = parse_arguments(sys.argv[1:] if arguments is None else arguments)
    install_wall()
    result = verify_sources()
    if mode == "--self-test":
        result["hostile"] = hostile_self_test()
    elif mode == "--apply":
        result = apply_root_only(result, options)
    sys.stdout.write(canonical(result) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FreezeError, OSError, UnicodeError, ValueError, IndexError) as error:
        sys.stderr.write("mandatory-anchor source freeze rejected: " + str(error) + "\n")
        raise SystemExit(2)
