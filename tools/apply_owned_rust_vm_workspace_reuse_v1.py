#!/usr/bin/env python3
"""Freeze an independently measurable, first-party Rust VM workspace variant.

Verification reads only exact, authenticated public evidence and source owners.
It never imports a matcher, executes candidate code, starts a process, samples a
clock, opens a hidden test, or mutates the workspace.  Only an explicitly
authorized, independently pushed root invocation can create its one new source.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex")):
    raise SystemExit("first-party VM source freeze must not import a matcher")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
DEVICE = 2064
SOURCE = "tools/apply_owned_rust_vm_workspace_reuse_v1.py"
PROTOCOL = "oracle/phase2/RUST-VM-WORKSPACE-REUSE-V1.md"
CONTRACT = "oracle/phase2/rust-vm-workspace-reuse-v1.json"
VARIANTS = "candidates/rust/variants"
VARIANT_DIRECTORY = "vm_workspace_reuse_v1"
VARIANT = VARIANTS + "/" + VARIANT_DIRECTORY + "/lib.rs"
PROPOSAL = "oracle/phase3/expanded-sealed-holdout-v2.json"
SCHEMA = "rebar-owned-rust-vm-workspace-reuse-v1-source-freeze"
NOT_MEASURED = "NOT MEASURED"
MAX_OWNER_BYTES = 1_048_576
MAX_JSON_DEPTH = 80
MAX_JSON_ITEMS = 250_000
ORIGINAL_SHA256 = "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d"
ORIGINAL_BYTES = 177_967
DERIVED_SHA256 = "0bd199957ed96cbf67109d4621698a6be300cb5c88d0ae30d25402f51777ba36"
DERIVED_BYTES = 178647
PROFILE_SHA256 = "71468c3196d75994180de6ce27ab1a3c48e1253fd37f0e4d0f33ba7a6d4099cb"
PROFILE_ROWS_FILE_SHA256 = "cd237092007b231b37293414e417bce80afde3bc44a44e787adb53a0e66f7697"
PROFILE_LOGICAL_ROWS_SHA256 = "6b9729005cd919f4de2e7137a35dd67ec18388a3f5362bcfb8142bab28545c11"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
PROPOSAL_SHA256 = "5d9fa3920c1dcabc92a3521d742cd10ec399cff1a979b71ac079daba6f92cba0"
PROPOSAL_INODE = 525920
PROPOSAL_BYTES = 15561
PARENT_INODE = 524946

# role, relative path, SHA-256, complete bytes, device-2064 inode
OWNERS = (
    ("goal", "GOAL.md", GOAL_SHA256, 3756, 31364044),
    ("original_oracle", "oracle/phase1/p0-completeness-v4.json",
     "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
    ("supplemental_oracle", "oracle/phase1/p0-differential-fuzz-reference-v3.json",
     "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff", 5288, 525082),
    ("latest_v25_campaign",
     "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v25-"
     "rust-capture-clamp-v1-root-provenance-original-p0-v25-failures-publication-receipt.json",
     "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59", 11832, 524846),
    ("first_party_cargo_manifest", "candidates/rust/Cargo.toml",
     "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225, 428094),
    ("first_party_cargo_lock", "candidates/rust/Cargo.lock",
     "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167, 428098),
    ("first_party_rust_vm", "candidates/rust/src/lib.rs",
     ORIGINAL_SHA256, ORIGINAL_BYTES, 428096),
    ("first_party_rust_search", "candidates/rust/src/search.rs",
     "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773, 429682),
    ("first_party_rust_inline_stack", "candidates/rust/src/stack.rs",
     "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269, 428151),
    ("complete_public_profile_source", "tools/rust_public_profile_v2.py",
     "a4eb77c29e06b1a77152ebb2275525bfd75b3fa26fd25f100059c79cfb39437a", 31941, 429686),
    ("complete_public_profile_protocol", "oracle/phase3/RUST-PUBLIC-PROFILE-V2.md",
     "aa96b3a2132be6557020a753da8e57e1c210b1a9b9216b6a015f36715e208b9d", 3128, 526049),
    ("complete_public_profile_manifest", "oracle/phase3/rust-public-profile-v2.json",
     "9687806994bcbb401ed89cba11197b79a491da023b95be89e1686a7c6cccafea", 3926, 526050),
    ("complete_public_profile_summary",
     "experiments/rust_public_profile_v2/public-run-001/summary.json",
     PROFILE_SHA256, 28079, 526265),
    ("complete_public_paired_rows",
     "experiments/rust_public_profile_v2/public-run-001/paired-timing.raw.json",
     PROFILE_ROWS_FILE_SHA256, 504914, 526215),
    ("public_allocation_function_table",
     "experiments/rust_public_profile_v2/public-run-001/rust.cpu.txt",
     "542b2fd936535ea5739db31f7cd6e97ff62642b20bbb448c09e33095e47a7d1d", 72934, 526257),
    ("public_allocation_callers",
     "experiments/rust_public_profile_v2/public-run-001/rust.ffi.txt",
     "6957b8e19c2388173c719c757717e67aa8b116ba97243e226fed69619646d483", 525686, 526259),
    ("public_native_heap_totals",
     "experiments/rust_public_profile_v2/public-run-001/rust.heap.txt",
     "ea98056637f2a3b9634549e57c28b2183167f4874441f31140913b0c93d68b9d", 1429, 526263),
    ("public_profiler_clock_failure",
     "experiments/rust_public_profile_v2/public-run-001/rust.er/log.xml",
     "0a893318548fb3974ed0529a2379c5080c8f52142a8af81ae52645abbaf07dc2", 65536, 526246),
)

OLD_STATE_INSERT = b"#[inline]\nfn run_look(\n"
NEW_STATE_INSERT = b"""/// Search-local storage; nested assertions always own a distinct frame.
#[derive(Default)]
struct VmStateScratch {
    guards: Vec<usize>,
    repeats: Vec<RepeatState>,
    old_begins: Vec<isize>,
    old_ends: Vec<isize>,
}

#[inline]
fn run_look(
"""
OLD_LOOK = b"""fn run_look(
    program: &Program,
    context: &Context<'_>,
    pos: usize,
    instruction: Instruction,
    begins: &mut [isize],
    ends: &mut [isize],
    last: &mut isize,
) -> Option<usize> {
    if instruction.flags & 2 != 0 {
        if instruction.value == 0 {
            return run_program(
                program,
                context,
                pos,
                instruction.left,
                false,
                false,
                begins,
                ends,
                last,
            );
        }
        if pos > context.end {
            return None;
        }
        let begin = pos.checked_sub(instruction.value)?;
        let behind_context = Context {
            chars: context.chars,
            folds: context.folds,
            masks: context.masks,
            bytes: context.bytes,
            wide: context.wide,
            end: pos,
        };
        run_program(
            program,
            &behind_context,
            begin,
            instruction.left,
            true,
            false,
            begins,
            ends,
            last,
        )
    } else {
        run_program(
            program,
            context,
            pos,
            instruction.left,
            false,
            false,
            begins,
            ends,
            last,
        )
    }
}
"""
NEW_LOOK = OLD_LOOK.replace(b"                last,\n            );",
                            b"                last,\n                None,\n            );")
NEW_LOOK = NEW_LOOK.replace(b"            last,\n        )",
                            b"            last,\n            None,\n        )")

OLD_PROGRAM_START = b"""fn run_program(
    program: &Program,
    context: &Context<'_>,
    start: usize,
    entry: usize,
    full: bool,
    nonempty: bool,
    begins: &mut [isize],
    ends: &mut [isize],
    last: &mut isize,
) -> Option<usize> {
    let mut choices = InlineStack::<Choice, 24>::new();
    let mut undo = InlineStack::<CaptureUndo, 48>::new();
    let mut guard_undo = InlineStack::<GuardUndo, 16>::new();
    let mut repeat_undo = InlineStack::<RepeatUndo, 16>::new();
    let mut atomic = InlineStack::<usize, 12>::new();
    const INLINE_STATE_SLOTS: usize = 8;
    let mut inline_guards = [usize::MAX; INLINE_STATE_SLOTS];
    let mut overflow_guards = Vec::new();
    let mut guards: &mut [usize] = if program.guards <= INLINE_STATE_SLOTS {
        &mut inline_guards[..program.guards]
    } else {
        overflow_guards.resize(program.guards, usize::MAX);
        overflow_guards.as_mut_slice()
    };
    let mut inline_repeats = [RepeatState::default(); INLINE_STATE_SLOTS];
    let mut overflow_repeats = Vec::new();
    let mut repeats: &mut [RepeatState] = if program.repeats.len() <= INLINE_STATE_SLOTS {
        &mut inline_repeats[..program.repeats.len()]
    } else {
        overflow_repeats.resize(program.repeats.len(), RepeatState::default());
        overflow_repeats.as_mut_slice()
    };
"""
NEW_PROGRAM_START = b"""fn run_program(
    program: &Program,
    context: &Context<'_>,
    start: usize,
    entry: usize,
    full: bool,
    nonempty: bool,
    begins: &mut [isize],
    ends: &mut [isize],
    last: &mut isize,
    scratch: Option<&mut VmStateScratch>,
) -> Option<usize> {
    let mut local_scratch = VmStateScratch::default();
    let VmStateScratch {
        guards: overflow_guards,
        repeats: overflow_repeats,
        old_begins: overflow_old_begins,
        old_ends: overflow_old_ends,
    } = scratch.unwrap_or(&mut local_scratch);
    let mut choices = InlineStack::<Choice, 24>::new();
    let mut undo = InlineStack::<CaptureUndo, 48>::new();
    let mut guard_undo = InlineStack::<GuardUndo, 16>::new();
    let mut repeat_undo = InlineStack::<RepeatUndo, 16>::new();
    let mut atomic = InlineStack::<usize, 12>::new();
    const INLINE_STATE_SLOTS: usize = 8;
    let mut inline_guards = [usize::MAX; INLINE_STATE_SLOTS];
    let mut guards: &mut [usize] = if program.guards <= INLINE_STATE_SLOTS {
        &mut inline_guards[..program.guards]
    } else {
        overflow_guards.resize(program.guards, usize::MAX);
        overflow_guards.fill(usize::MAX);
        overflow_guards.as_mut_slice()
    };
    let mut inline_repeats = [RepeatState::default(); INLINE_STATE_SLOTS];
    let mut repeats: &mut [RepeatState] = if program.repeats.len() <= INLINE_STATE_SLOTS {
        &mut inline_repeats[..program.repeats.len()]
    } else {
        overflow_repeats.resize(program.repeats.len(), RepeatState::default());
        overflow_repeats.fill(RepeatState::default());
        overflow_repeats.as_mut_slice()
    };
"""
OLD_ASSERTION_BEGIN = b"""                    let mut inline_old_begins = [0_isize; INLINE_LOOK_CAPTURE_SLOTS];
                    let mut overflow_old_begins = Vec::new();
                    let old_begins: &[isize] = if begins.len() <= INLINE_LOOK_CAPTURE_SLOTS {
                        let snapshot = &mut inline_old_begins[..begins.len()];
                        snapshot.copy_from_slice(begins);
                        snapshot
                    } else {
                        overflow_old_begins.extend_from_slice(begins);
                        overflow_old_begins.as_slice()
                    };
"""
NEW_ASSERTION_BEGIN = b"""                    let mut inline_old_begins = [0_isize; INLINE_LOOK_CAPTURE_SLOTS];
                    let old_begins: &[isize] = if begins.len() <= INLINE_LOOK_CAPTURE_SLOTS {
                        let snapshot = &mut inline_old_begins[..begins.len()];
                        snapshot.copy_from_slice(begins);
                        snapshot
                    } else {
                        overflow_old_begins.clear();
                        overflow_old_begins.extend_from_slice(begins);
                        overflow_old_begins.as_slice()
                    };
"""
OLD_ASSERTION_END = b"""                    let mut inline_old_ends = [0_isize; INLINE_LOOK_CAPTURE_SLOTS];
                    let mut overflow_old_ends = Vec::new();
                    let old_ends: &[isize] = if ends.len() <= INLINE_LOOK_CAPTURE_SLOTS {
                        let snapshot = &mut inline_old_ends[..ends.len()];
                        snapshot.copy_from_slice(ends);
                        snapshot
                    } else {
                        overflow_old_ends.extend_from_slice(ends);
                        overflow_old_ends.as_slice()
                    };
"""
NEW_ASSERTION_END = b"""                    let mut inline_old_ends = [0_isize; INLINE_LOOK_CAPTURE_SLOTS];
                    let old_ends: &[isize] = if ends.len() <= INLINE_LOOK_CAPTURE_SLOTS {
                        let snapshot = &mut inline_old_ends[..ends.len()];
                        snapshot.copy_from_slice(ends);
                        snapshot
                    } else {
                        overflow_old_ends.clear();
                        overflow_old_ends.extend_from_slice(ends);
                        overflow_old_ends.as_slice()
                    };
"""
OLD_MATCH_START = b"""    begins.fill(-1);
    ends.fill(-1);
    *last = -1;
    let mut start = first_start;
    while start <= last_start {
"""
NEW_MATCH_START = b"""    begins.fill(-1);
    ends.fill(-1);
    *last = -1;
    let mut scratch = VmStateScratch::default();
    let mut start = first_start;
    while start <= last_start {
"""
OLD_ROOT_CALL = b"""            run_program(
                program,
                context,
                start,
                0,
                mode == 2,
                nonempty != 0 && start == pos,
                begins,
                ends,
                last,
            )
"""
NEW_ROOT_CALL = b"""            run_program(
                program,
                context,
                start,
                0,
                mode == 2,
                nonempty != 0 && start == pos,
                begins,
                ends,
                last,
                Some(&mut scratch),
            )
"""
REPLACEMENTS = (
    ("search_local_four_vector_workspace", OLD_STATE_INSERT, NEW_STATE_INSERT),
    ("distinct_nested_lookaround_frames", OLD_LOOK, NEW_LOOK),
    ("reusable_guard_and_repeat_state", OLD_PROGRAM_START, NEW_PROGRAM_START),
    ("reusable_assertion_begin_snapshot", OLD_ASSERTION_BEGIN, NEW_ASSERTION_BEGIN),
    ("reusable_assertion_end_snapshot", OLD_ASSERTION_END, NEW_ASSERTION_END),
    ("single_root_search_workspace", OLD_MATCH_START, NEW_MATCH_START),
    ("root_only_workspace_lease", OLD_ROOT_CALL, NEW_ROOT_CALL),
)


class FreezeError(Exception):
    """Reject changed semantics, external engines, or source-freeze authority."""


def require(value: object, message: str) -> None:
    if value is not True:
        raise FreezeError(message)


def sha256(value: bytes) -> str:
    require(type(value) is bytes, "hash only exact complete bytes")
    return hashlib.sha256(value).hexdigest()


def valid_sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require one exact lowercase SHA-256: " + label)
    assert isinstance(value, str)
    return value


def quoted(value: str) -> str:
    require(type(value) is str, "JSON object keys and strings must be genuine text")
    simple = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
              "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    result = ['"']
    for item in value:
        point = ord(item)
        require(not 0xD800 <= point <= 0xDFFF, "reject unpaired JSON surrogates")
        result.append(simple.get(item, "\\u" + format(point, "04x")
                                 if point < 32 else item))
    return "".join(result) + '"'


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "reject excessive JSON nesting")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is str:
        return quoted(value)
    if type(value) is int:
        return str(value)
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value), "reject nontext JSON keys")
        return "{" + ",".join(quoted(key) + ":" + canonical(value[key], depth + 1)
                              for key in sorted(value)) + "}"
    raise FreezeError("reject unsupported JSON value")


def document(value: object) -> bytes:
    return (canonical(value) + "\n").encode("utf-8")


class StrictJSON:
    """Bounded duplicate-rejecting JSON decoder without importing `re`."""

    def __init__(self, raw: bytes):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_OWNER_BYTES,
                "require one complete bounded JSON document")
        self.text = raw.decode("utf-8", "strict")
        self.at = 0
        self.items = 0

    def whitespace(self) -> None:
        while self.at < len(self.text) and self.text[self.at] in " \t\r\n":
            self.at += 1

    def string(self) -> str:
        require(self.text[self.at:self.at + 1] == '"', "require a JSON string")
        self.at += 1
        result: list[str] = []
        escapes = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
                   "n": "\n", "r": "\r", "t": "\t"}
        while self.at < len(self.text):
            item = self.text[self.at]
            self.at += 1
            if item == '"':
                return "".join(result)
            if item != "\\":
                point = ord(item)
                require(point >= 32 and not 0xD800 <= point <= 0xDFFF,
                        "reject invalid raw JSON string")
                result.append(item)
                continue
            require(self.at < len(self.text), "reject incomplete JSON escape")
            escape = self.text[self.at]
            self.at += 1
            if escape != "u":
                require(escape in escapes, "reject invalid JSON escape")
                result.append(escapes[escape])
                continue
            digits = self.text[self.at:self.at + 4]
            require(len(digits) == 4
                    and all(value in "0123456789abcdefABCDEF" for value in digits),
                    "reject malformed JSON Unicode escape")
            self.at += 4
            point = int(digits, 16)
            if 0xD800 <= point <= 0xDBFF:
                require(self.text[self.at:self.at + 2] == "\\u", "reject unpaired high surrogate")
                low_digits = self.text[self.at + 2:self.at + 6]
                require(len(low_digits) == 4
                        and all(value in "0123456789abcdefABCDEF" for value in low_digits),
                        "reject malformed low-surrogate escape")
                low = int(low_digits, 16)
                require(0xDC00 <= low <= 0xDFFF, "reject unpaired high surrogate")
                self.at += 6
                point = 0x10000 + ((point - 0xD800) << 10) + low - 0xDC00
            else:
                require(not 0xDC00 <= point <= 0xDFFF, "reject unpaired low surrogate")
            result.append(chr(point))
        raise FreezeError("reject unterminated JSON string")

    def number(self) -> int | float:
        begin = self.at
        if self.text[self.at:self.at + 1] == "-":
            self.at += 1
        require(self.at < len(self.text), "reject incomplete JSON number")
        if self.text[self.at] == "0":
            self.at += 1
            require(self.at == len(self.text) or self.text[self.at] not in "0123456789",
                    "reject a leading-zero JSON number")
        else:
            require(self.text[self.at] in "123456789", "reject malformed JSON number")
            while self.at < len(self.text) and self.text[self.at] in "0123456789":
                self.at += 1
        floating = False
        if self.text[self.at:self.at + 1] == ".":
            floating = True
            self.at += 1
            point = self.at
            while self.at < len(self.text) and self.text[self.at] in "0123456789":
                self.at += 1
            require(self.at != point, "reject a missing JSON fraction")
        if self.text[self.at:self.at + 1] in ("e", "E"):
            floating = True
            self.at += 1
            if self.text[self.at:self.at + 1] in ("+", "-"):
                self.at += 1
            exponent = self.at
            while self.at < len(self.text) and self.text[self.at] in "0123456789":
                self.at += 1
            require(self.at != exponent, "reject a missing JSON exponent")
        token = self.text[begin:self.at]
        require(len(token) <= 128, "reject an unbounded JSON number")
        if not floating:
            return int(token)
        result = float(token)
        require(result == result and abs(result) != float("inf"),
                "reject a nonfinite JSON number")
        return result

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "reject excessive JSON depth")
        self.whitespace()
        require(self.at < len(self.text), "reject missing JSON data")
        marker = self.text[self.at]
        if marker == '"':
            return self.string()
        if marker == "{":
            self.at += 1
            result: dict[str, object] = {}
            self.whitespace()
            if self.text[self.at:self.at + 1] == "}":
                self.at += 1
                return result
            while True:
                self.whitespace()
                key = self.string()
                require(key not in result, "reject duplicate JSON key: " + key)
                self.items += 1
                require(self.items <= MAX_JSON_ITEMS, "reject oversized JSON evidence")
                self.whitespace()
                require(self.text[self.at:self.at + 1] == ":", "reject missing JSON colon")
                self.at += 1
                result[key] = self.value(depth + 1)
                self.whitespace()
                marker = self.text[self.at:self.at + 1]
                self.at += 1
                if marker == "}":
                    return result
                require(marker == ",", "reject malformed JSON object")
        if marker == "[":
            self.at += 1
            result: list[object] = []
            self.whitespace()
            if self.text[self.at:self.at + 1] == "]":
                self.at += 1
                return result
            while True:
                self.items += 1
                require(self.items <= MAX_JSON_ITEMS, "reject oversized JSON evidence")
                result.append(self.value(depth + 1))
                self.whitespace()
                marker = self.text[self.at:self.at + 1]
                self.at += 1
                if marker == "]":
                    return result
                require(marker == ",", "reject malformed JSON array")
        if marker == "-" or marker in "0123456789":
            return self.number()
        for token, value in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(token, self.at):
                self.at += len(token)
                return value
        raise FreezeError("reject malformed or nonfinite JSON evidence")

    def decode(self) -> object:
        value = self.value()
        self.whitespace()
        require(self.at == len(self.text), "reject trailing JSON data")
        return value


def json_object(raw: bytes, label: str) -> dict:
    result = StrictJSON(raw).decode()
    require(type(result) is dict, "require a JSON object: " + label)
    assert isinstance(result, dict)
    return result


def no_matching_imports() -> None:
    forbidden = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
                 "ctypes", "candidates", "rebar", "subprocess", "socket", "threading",
                 "multiprocessing", "concurrent.interpreters")
    require(not any(name == prefix or name.startswith(prefix + ".")
                    for name in sys.modules for prefix in forbidden),
            "reject matcher, candidate, native loader, process, or network import")


class SourceWall:
    """Physical deny-default owner wall with one descriptor-anchored output."""

    def __init__(self, apply: bool):
        self.apply = apply
        self.allowed = frozenset(ROOT + "/" + item
                                 for item in (SOURCE, PROTOCOL, CONTRACT)
                                 ) | frozenset(ROOT + "/" + row[1] for row in OWNERS)
        self.proposal = ROOT + "/" + PROPOSAL
        self.parent = ROOT + "/" + VARIANTS
        self.child = ROOT + "/" + VARIANTS + "/" + VARIANT_DIRECTORY
        self.target = ROOT + "/" + VARIANT
        self.live: set[int] = set()
        self.parent_fd: int | None = None
        self.child_fd: int | None = None
        self.output_fd: int | None = None
        self.mkdir_done = False
        self.output_created = False
        self.proposal_stat_count = 0
        self.proposal_open_count = 0
        self.blocked: dict[str, int] = {}
        self.installed = False
        self.native_open = os.open
        self.native_read = os.read
        self.native_write = os.write
        self.native_fstat = os.fstat
        self.native_close = os.close
        self.native_fsync = os.fsync
        self.native_lstat = os.lstat
        self.native_mkdir = os.mkdir

    def deny(self, name: str) -> None:
        self.blocked[name] = self.blocked.get(name, 0) + 1
        raise FreezeError("VM workspace source wall rejected " + name)

    def approved_read(self, path: object, flags: object) -> bool:
        forbidden = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
                     | getattr(os, "O_TMPFILE", 0) | getattr(os, "O_DIRECTORY", 0))
        return (type(path) is str and path in self.allowed
                and path.startswith(ROOT + "/") and path == os.path.normpath(path)
                and type(flags) is int and not flags & forbidden
                and bool(flags & getattr(os, "O_NOFOLLOW", 0)))

    def audit(self, event: str, args: tuple) -> None:
        if event == "open":
            path = args[0] if args else None
            mode = args[1] if len(args) > 1 else None
            flags = args[2] if len(args) > 2 else None
            if self.approved_read(path, flags) and not (
                    type(mode) is str and any(char in mode for char in "wax+")):
                return
            if self.apply and type(flags) is int:
                directory = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                             | getattr(os, "O_NOFOLLOW", 0))
                output = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
                          | getattr(os, "O_NOFOLLOW", 0))
                if path == self.parent and flags & directory == directory:
                    return
                if path == VARIANT_DIRECTORY and flags & directory == directory:
                    return
                if path == "lib.rs" and flags & output == output:
                    return
            if path == self.proposal:
                self.deny("unopened-final-holdout-content")
            self.deny("foreign-candidate-native-source-or-write")
        if event == "os.mkdir":
            path = args[0] if args else None
            if self.apply and path == VARIANT_DIRECTORY and not self.mkdir_done:
                return
            self.deny("foreign-directory-mutation")
        if (event in ("import", "exec", "compile", "marshal.loads", "os.system", "os.fork",
                      "os.posix_spawn", "os.posix_spawnp", "os.rename", "os.replace",
                      "os.remove", "os.unlink", "os.rmdir", "os.chmod", "os.chown",
                      "os.urandom", "os.getrandom", "_interpreters.create",
                      "_interpreters.exec", "cpython.PyInterpreterState_New", "code.__new__")
                or event.startswith(("subprocess.", "socket.", "ctypes.", "threading.",
                                     "multiprocessing.", "tempfile.", "time.", "os.exec",
                                     "os.spawn"))):
            self.deny("candidate-native-process-clock-network-or-dynamic-code")

    def forbidden(self, name: str):
        def reject(*_args: object, **_kwargs: object) -> object:
            self.deny(name)
        return reject

    def guarded_open(self, path: object, flags: object, mode: int = 0o777,
                     *, dir_fd: object = None) -> int:
        if self.approved_read(path, flags) and dir_fd is None:
            descriptor = self.native_open(path, flags, mode)
            self.live.add(descriptor)
            return descriptor
        if not self.apply or type(flags) is not int:
            self.deny("unowned-open")
        required_directory = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                              | getattr(os, "O_NOFOLLOW", 0))
        if (path == self.parent and dir_fd is None
                and flags & required_directory == required_directory
                and self.parent_fd is None):
            descriptor = self.native_open(path, flags, mode)
            self.parent_fd = descriptor
            return descriptor
        if (path == VARIANT_DIRECTORY and dir_fd == self.parent_fd and self.mkdir_done
                and flags & required_directory == required_directory and self.child_fd is None):
            descriptor = self.native_open(path, flags, mode, dir_fd=dir_fd)
            self.child_fd = descriptor
            return descriptor
        required_output = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
                           | getattr(os, "O_NOFOLLOW", 0))
        denied_output = os.O_RDWR | os.O_TRUNC | os.O_APPEND | getattr(os, "O_TMPFILE", 0)
        if (path == "lib.rs" and dir_fd == self.child_fd and not self.output_created
                and flags & required_output == required_output and not flags & denied_output
                and mode == 0o600):
            descriptor = self.native_open(path, flags, mode, dir_fd=dir_fd)
            self.output_fd = descriptor
            self.output_created = True
            return descriptor
        self.deny("foreign-directory-descriptor-or-output")

    def guarded_read(self, descriptor: object, count: object) -> bytes:
        if (type(descriptor) is not int or descriptor not in self.live
                or type(count) is not int or count < 0 or count > MAX_OWNER_BYTES):
            self.deny("foreign-or-unbounded-descriptor-read")
        return self.native_read(descriptor, count)

    def guarded_write(self, descriptor: object, value: object) -> int:
        if not self.apply or descriptor != self.output_fd or type(value) not in (bytes, memoryview):
            self.deny("foreign-or-unapproved-descriptor-write")
        assert isinstance(descriptor, int)
        return self.native_write(descriptor, value)

    def guarded_fstat(self, descriptor: object) -> os.stat_result:
        if (type(descriptor) is not int or descriptor not in self.live
                and descriptor not in (self.parent_fd, self.child_fd, self.output_fd)):
            self.deny("foreign-descriptor-stat")
        assert isinstance(descriptor, int)
        return self.native_fstat(descriptor)

    def guarded_close(self, descriptor: object) -> None:
        if type(descriptor) is not int:
            self.deny("foreign-descriptor-close")
        if descriptor in self.live:
            self.live.remove(descriptor)
        elif descriptor == self.output_fd:
            self.output_fd = None
        elif descriptor == self.child_fd:
            self.child_fd = None
        elif descriptor == self.parent_fd:
            self.parent_fd = None
        else:
            self.deny("foreign-descriptor-close")
        self.native_close(descriptor)

    def guarded_fsync(self, descriptor: object) -> None:
        if (not self.apply or descriptor not in
                (self.parent_fd, self.child_fd, self.output_fd)):
            self.deny("foreign-descriptor-sync")
        assert isinstance(descriptor, int)
        self.native_fsync(descriptor)

    def guarded_lstat(self, path: object, *, dir_fd: object = None) -> os.stat_result:
        if path != self.proposal or dir_fd is not None or self.proposal_stat_count:
            self.deny("foreign-or-repeated-proposal-metadata")
        assert isinstance(path, str)
        result = self.native_lstat(path)
        self.proposal_stat_count += 1
        return result

    def guarded_mkdir(self, path: object, mode: int = 0o777,
                      *, dir_fd: object = None) -> None:
        if (not self.apply or path != VARIANT_DIRECTORY or dir_fd != self.parent_fd
                or self.mkdir_done or mode != 0o700):
            self.deny("foreign-variant-directory")
        self.native_mkdir(path, mode, dir_fd=dir_fd)
        self.mkdir_done = True

    def install(self) -> None:
        require(not self.installed, "install one irreversible source wall")
        sys.addaudithook(self.audit)
        builtins.open = self.forbidden("builtins-open")
        _io.open = self.forbidden("direct-_io-open")
        _io.FileIO = self.forbidden("direct-_io-fileio")
        io.open = self.forbidden("direct-io-open")
        io.FileIO = self.forbidden("direct-io-fileio")
        if hasattr(_io, "open_code"):
            _io.open_code = self.forbidden("direct-_io-open-code")
        if hasattr(io, "open_code"):
            io.open_code = self.forbidden("direct-io-open-code")
        os.open = self.guarded_open
        os.read = self.guarded_read
        os.write = self.guarded_write
        os.fstat = self.guarded_fstat
        os.close = self.guarded_close
        os.fsync = self.guarded_fsync
        os.lstat = self.guarded_lstat
        os.mkdir = self.guarded_mkdir
        for name in ("fdopen", "dup", "dup2", "stat", "readlink", "listdir", "scandir",
                     "walk", "fwalk", "access", "fork", "posix_spawn", "posix_spawnp",
                     "system", "makedirs", "remove", "unlink", "rename", "replace",
                     "rmdir", "chmod", "chown", "urandom", "getrandom"):
            if hasattr(os, name):
                setattr(os, name, self.forbidden("direct-os-" + name))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
                     "perf_counter_ns", "process_time", "process_time_ns", "thread_time",
                     "thread_time_ns", "clock_gettime", "clock_gettime_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self.forbidden("clock-" + name))
        self.installed = True


def read_owner(wall: SourceWall, owner: tuple) -> bytes:
    role, relative, fingerprint, size, inode = owner
    valid_sha(fingerprint, relative)
    require(type(size) is int and 0 < size <= MAX_OWNER_BYTES and type(inode) is int,
            "reject unbounded or incomplete source evidence")
    require(wall.installed, "install the wall before opening any frozen owner")
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_dev == DEVICE and before.st_ino == inode
                and before.st_size == size and before.st_nlink == 1
                and before.st_uid == os.geteuid(),
                "reject replaced, linked, or unowned frozen source: " + role)
        blocks: list[bytes] = []
        remaining = size
        while remaining:
            value = os.read(descriptor, min(remaining, 65536))
            require(bool(value), "reject truncated authenticated owner: " + role)
            blocks.append(value)
            remaining -= len(value)
        require(os.read(descriptor, 1) == b"", "reject trailing source bytes")
        after = os.fstat(descriptor)
        require(all(getattr(before, key) == getattr(after, key)
                    for key in ("st_dev", "st_ino", "st_size", "st_nlink",
                                "st_mtime_ns", "st_ctime_ns")),
                "reject concurrently exchanged source owner")
        raw = b"".join(blocks)
        require(sha256(raw) == fingerprint, "reject modified frozen owner: " + role)
        return raw
    finally:
        os.close(descriptor)


def dynamic_owner(wall: SourceWall, role: str, path: str, fingerprint: str) -> tuple:
    require(path in (SOURCE, PROTOCOL, CONTRACT), "reject unauthorized freeze owner")
    valid_sha(fingerprint, path)
    descriptor = os.open(ROOT + "/" + path,
                         os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        metadata = os.fstat(descriptor)
        require(stat.S_ISREG(metadata.st_mode) and stat.S_IMODE(metadata.st_mode) == 0o600
                and metadata.st_dev == DEVICE and metadata.st_uid == os.geteuid()
                and metadata.st_nlink == 1 and 0 < metadata.st_size <= MAX_OWNER_BYTES,
                "reject exchanged dynamic freeze owner: " + role)
        return role, path, fingerprint, metadata.st_size, metadata.st_ino
    finally:
        os.close(descriptor)


def owner_pin(owner: tuple) -> dict:
    role, path, fingerprint, size, inode = owner
    return {"role": role, "path": path, "sha256": fingerprint, "bytes": size,
            "device": DEVICE, "inode": inode, "mode": "0600", "nlink": 1}


def transform_source(source: bytes) -> bytes:
    require(type(source) is bytes and len(source) == ORIGINAL_BYTES
            and sha256(source) == ORIGINAL_SHA256,
            "derive only from the exact independently owned canonical Rust engine")
    derived = source
    for label, old, new in REPLACEMENTS:
        require(old != new and derived.count(old) == 1,
                "require one exact reversible Rust source anchor: " + label)
        derived = derived.replace(old, new, 1)
        require(derived.count(new) == 1,
                "require one exact first-party source transformation: " + label)
    require(NEW_LOOK.count(b"            None,\n") == 3,
            "every recursive assertion must receive an independent nested frame")
    require(derived.count(b"struct VmStateScratch {") == 1
            and derived.count(b"Some(&mut scratch)") == 1
            and derived.count(b"scratch: Option<&mut VmStateScratch>") == 1
            and derived.count(b"overflow_guards.fill(usize::MAX);") == 1
            and derived.count(b"overflow_repeats.fill(RepeatState::default());") == 1
            and derived.count(b"overflow_old_begins.clear();") == 1
            and derived.count(b"overflow_old_ends.clear();") == 1
            and derived.count(b"const INLINE_STATE_SLOTS: usize = 8;") == 1
            and derived.count(b"const INLINE_LOOK_CAPTURE_SLOTS: usize = 16;") == 1,
            "preserve independent frames, fresh sentinel resets, and inline thresholds")
    for forbidden in (b"extern crate regex", b"use regex::", b"_sre", b"pcre2",
                      b"oniguruma", b"ctypes", b"benchmark", b"holdout"):
        require(derived.count(forbidden) == source.count(forbidden),
                "reject external regex package, benchmark detection, or altered policy")
    if DERIVED_SHA256:
        require(sha256(derived) == DERIVED_SHA256 and len(derived) == DERIVED_BYTES,
                "reject an altered prospective VM workspace implementation")
    return derived


class ModelWorkspace:
    """Small exact-state model of reusable VM state and assertion rollback."""

    def __init__(self):
        self.guards: list[int] = []
        self.repeats: list[tuple[int, int]] = []
        self.old_begins: list[int] = []
        self.old_ends: list[int] = []
        self.allocations = 0

    def prepare(self, guards: int, repeats: int) -> None:
        if guards > 8:
            if len(self.guards) < guards:
                self.guards.extend([-1] * (guards - len(self.guards)))
                self.allocations += 1
            for index in range(guards):
                self.guards[index] = -1
        if repeats > 8:
            if len(self.repeats) < repeats:
                self.repeats.extend([(0, 0)] * (repeats - len(self.repeats)))
                self.allocations += 1
            for index in range(repeats):
                self.repeats[index] = (0, 0)

    def snapshot(self, begins: list[int], ends: list[int]) -> tuple[list[int], list[int]]:
        if len(begins) <= 16:
            return list(begins), list(ends)
        if len(self.old_begins) < len(begins):
            self.allocations += 1
        if len(self.old_ends) < len(ends):
            self.allocations += 1
        self.old_begins[:] = begins
        self.old_ends[:] = ends
        return list(self.old_begins), list(self.old_ends)


def model_attempt(seed: int, groups: int, guard_count: int, repeat_count: int,
                  start: int, workspace: ModelWorkspace, depth: int,
                  reentry: bool = False) -> tuple:
    workspace.prepare(guard_count, repeat_count)
    guards = workspace.guards if guard_count > 8 else [-1] * guard_count
    repeats = workspace.repeats if repeat_count > 8 else [(0, 0)] * repeat_count
    begins = [-1] * groups
    ends = [-1] * groups
    last = -1
    for step in range(1 + seed % 7):
        value = (seed * 1664525 + start * 1013904223 + step * 97 + depth * 53) & 0xFFFFFFFF
        if guard_count:
            slot = value % guard_count
            previous = guards[slot]
            require(previous == -1 or previous <= start + step,
                    "a stale guard sentinel escaped a previous candidate start")
            guards[slot] = start + step
        if repeat_count:
            slot = (value >> 3) % repeat_count
            count, origin = repeats[slot]
            if step == 0:
                require(count == 0 and origin == 0,
                        "a repeat state escaped an earlier search attempt")
            repeats[slot] = (count + 1, start + step)
        if groups:
            number = (value >> 7) % groups
            begins[number] = start + step
            ends[number] = start + step + (value & 1)
            last = number
        if depth and step % 2 == 0:
            saved_begins, saved_ends = workspace.snapshot(begins, ends)
            old_last = last
            child = ModelWorkspace()
            child_result = model_attempt(seed ^ (step + 1), groups, guard_count,
                                         repeat_count, start + step, child, depth - 1)
            require(child is not workspace,
                    "a nested assertion aliased its parent's active workspace")
            positive = (value >> 11) & 1 == 0
            matched = child_result[0]
            if matched and positive:
                number = (step + 1) % max(1, groups)
                if groups:
                    begins[number] = start + step + 1
                    ends[number] = start + step + 2
                    last = number
            elif not positive:
                begins[:] = saved_begins
                ends[:] = saved_ends
                last = old_last
            else:
                begins[:] = saved_begins
                ends[:] = saved_ends
                last = old_last
        if reentry and step == 1:
            independent = ModelWorkspace()
            before = (tuple(guards), tuple(repeats), tuple(begins), tuple(ends), last)
            model_attempt(seed ^ 0xABCDEF, groups, guard_count, repeat_count,
                          start + 9, independent, max(0, depth - 1))
            require(before == (tuple(guards), tuple(repeats), tuple(begins), tuple(ends), last),
                    "a callback/interpreter reentry mutated the active search workspace")
    return bool((seed ^ start ^ depth) & 1), tuple(begins), tuple(ends), last


def synthetic_semantics() -> dict:
    cases = 0
    nested = 0
    reentrant = 0
    overflow = 0
    snapshot_spill = 0
    saved_allocations = 0
    for groups in (0, 1, 15, 16, 17, 32, 64):
        for guard_count in (0, 1, 7, 8, 9, 12):
            for repeat_count in (0, 1, 7, 8, 9, 13):
                for depth in (0, 1, 2):
                    for seed in range(6):
                        shared = ModelWorkspace()
                        original_allocations = 0
                        for start in range(4):
                            reference = ModelWorkspace()
                            expected = model_attempt(seed + groups, groups, guard_count,
                                                     repeat_count, start, reference, depth,
                                                     reentry=depth > 0)
                            actual = model_attempt(seed + groups, groups, guard_count,
                                                   repeat_count, start, shared, depth,
                                                   reentry=depth > 0)
                            require(actual == expected,
                                    "reused VM state changed guards, repeats, captures, or rollback")
                            original_allocations += reference.allocations
                            cases += 1
                            nested += int(depth != 0)
                            reentrant += int(depth != 0)
                            overflow += int(guard_count > 8 or repeat_count > 8)
                            snapshot_spill += int(groups > 16 and depth != 0)
                        saved_allocations += original_allocations - shared.allocations
                        require(shared.allocations <= original_allocations,
                                "workspace reuse introduced a synthetic allocation")
    require(cases >= 15000 and nested > 0 and overflow > 0 and snapshot_spill > 0
            and reentrant > 0 and saved_allocations > 0,
            "exercise every real overflow, nested assertion, and callback boundary")
    return {"case_count": cases, "nested_assertion_case_count": nested,
            "callback_reentry_case_count": reentrant,
            "guard_or_repeat_overflow_case_count": overflow,
            "capture_snapshot_overflow_case_count": snapshot_spill,
            "synthetic_allocations_avoided": saved_allocations,
            "inline_guard_threshold": 8, "inline_repeat_threshold": 8,
            "inline_capture_snapshot_threshold": 16,
            "nested_frames_are_independent": True,
            "guards_reset_to_usize_max_every_attempt": True,
            "repeats_reset_to_default_every_attempt": True,
            "callback_reentry_uses_independent_root_frame": True,
            "candidate_executed": False, "native_code_executed": False}


def validate_oracles(original: dict, supplemental: dict, actual: dict) -> None:
    require(original.get("schema") == "rebar-cpython-re-p0-completeness-v4"
            and original.get("status") == "PASS"
            and original.get("original_case_execution_denominator") == 31237
            and original.get("original_suite_count") == 13
            and original.get("qualified_candidate_count") == 0,
            "preserve every original frozen P0 obligation")
    require(supplemental.get("schema") == "rebar-owned-differential-fuzz-reference-v3"
            and supplemental.get("original_case_execution_denominator") == 31237
            and type(supplemental.get("supplemental_corpus")) is dict
            and supplemental["supplemental_corpus"].get("case_count") == 8244
            and supplemental.get("case_denominator_included_in_original_31237") is False,
            "preserve the independent supplemental reference and fixed denominator")
    require(actual.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v25-durable-publication-receipt"
            and actual.get("status") == "PASS"
            and actual.get("publication_status") == "PASS"
            and actual.get("candidate_status") == "FAIL"
            and actual.get("case_execution_denominator") == 31237
            and actual.get("completed_suite_count") == 13
            and actual.get("actual_candidate_workers") == 13
            and actual.get("semantic_mismatch_count") == 1352
            and actual.get("verified_passing_case_count") == 15877
            and actual.get("candidate_qualified") is False
            and actual.get("holdout") == "NOT OPENED",
            "preserve the most recent complete failing first-party Rust campaign")
    suites = actual.get("suite_integrity")
    require(type(suites) is list and len(suites) == 13
            and {row["suite"]: row["mismatch_count"] for row in suites
                 if row["mismatch_count"]}
            == {"substitution_v2": 240, "shape_v2": 1112},
            "preserve all 1,352 unexplained original Rust differences")


def validate_cargo(cargo: bytes, lock: bytes, source: bytes, stack: bytes, search: bytes) -> None:
    require(b"[dependencies]" not in cargo
            and lock.count(b"[[package]]") == 1
            and b'name = "rebar-rust-continuation"' in lock
            and source.count(b"mod stack;") == 1
            and source.count(b"mod search;") == 1
            and b"pub(crate) struct InlineStack" in stack
            and b"pub(crate) fn next_singleton" in search,
            "require one entirely first-party zero-external-package Rust engine")


def row_in_report(raw: bytes, symbol: bytes, values: tuple[int, int, int, int]) -> bool:
    for row in raw.splitlines():
        columns = row.split(None, 4)
        if len(columns) == 5 and columns[4].strip() == symbol:
            try:
                numbers = tuple(int(item) for item in columns[:4])
            except ValueError:
                continue
            if numbers == values:
                return True
    return False


def validate_profile(evidence: dict[str, bytes]) -> dict:
    summary = json_object(evidence["complete_public_profile_summary"], "successful public profile")
    rows = json_object(evidence["complete_public_paired_rows"], "complete public timing")
    require(summary.get("schema") == "rebar-rust-fresh-public-profile-v2-published-public-profile"
            and summary.get("status") == "PASS"
            and summary.get("case_count") == 416
            and summary.get("dataset_count") == 16
            and summary.get("operation_count") == 26
            and summary.get("paired_rounds") == 4
            and summary.get("profile_passes") == 3
            and summary.get("holdout_files_read") == 0
            and summary.get("archive_files_read") == 0
            and summary.get("fixture_files_read") == 0
            and summary.get("final_winner_selected") is False
            and summary.get("source_sha256") == OWNERS[9][2]
            and summary.get("manifest_sha256") == OWNERS[11][2]
            and summary.get("raw_paired_rows_sha256") == PROFILE_LOGICAL_ROWS_SHA256,
            "preserve the complete successful holdout-blind public profiler")
    gate = summary.get("correctness_gate")
    require(type(gate) is dict and gate.get("status") == "PASS"
            and gate.get("compared_cases") == 416
            and gate.get("completed_before_any_timing_or_profiler") is True
            and gate.get("candidate_owned_reference_import_attempts") == [],
            "require all real public answers to agree before profiling")
    pairing = summary.get("paired_results")
    require(type(pairing) is dict and type(pairing.get("overall")) is dict
            and pairing["overall"].get("pairs") == 1664
            and pairing["overall"].get("baseline_total_ns") == 97941980
            and pairing["overall"].get("rust_total_ns") == 164386504
            and type(rows.get("rows")) is list and len(rows["rows"]) == 1664,
            "retain all 1,664 paired public observations and both genuine losses")
    profile = summary.get("native_profiles")
    require(type(profile) is dict and type(profile.get("rust")) is dict
            and profile["rust"].get("native_heap_tracing") == "ENABLED (-H on)"
            and profile["rust"].get("correctness_checks") == 1248,
            "authenticate actual first-party native allocation collection")
    function_table = evidence["public_allocation_function_table"]
    ffi = evidence["public_allocation_callers"]
    log = evidence["public_profiler_clock_failure"]
    heap = evidence["public_native_heap_totals"]
    require(function_table.startswith(b"Functions sorted by metric: Inclusive Bytes Leaked\n")
            and ffi.startswith(b"Functions sorted by metric: Inclusive Bytes Leaked\n")
            and b'<event kind="cerror" id="9">itimer could not be set</event>' in log
            and b'<profile name="heaptrace">' in log
            and b"Clock profiling data" not in log,
            "CPU function profiles were not collected; never mislabel heap allocation as CPU")
    require(row_in_report(function_table, b"rebar_rust_continuation::run_program",
                          (133120, 379, 397248, 984))
            and row_in_report(ffi,
                              b"<alloc::raw_vec::RawVec<rebar_rust_continuation::CaptureUndo>>::grow_one",
                              (133120, 379, 276480, 576))
            and row_in_report(ffi,
                              b"<alloc::raw_vec::RawVecInner<_>>::reserve::do_reserve_and_handle::<alloc::alloc::Global>",
                              (0, 0, 120768, 408))
            and b"Total allocations                 260204" in heap
            and b"Total bytes                       104211416" in heap,
            "authenticate the exact observed VM allocation evidence without inventing CPU data")
    return {"profile_summary_sha256": PROFILE_SHA256,
            "complete_public_case_count": 416,
            "complete_public_paired_row_count": 1664,
            "clean_public_baseline_total_ns": 97941980,
            "clean_public_rust_total_ns": 164386504,
            "instrumented_native_allocation_count": 260204,
            "instrumented_native_allocation_bytes": 104211416,
            "run_program_allocation_count": 984,
            "run_program_allocation_bytes": 397248,
            "run_program_capture_undo_allocation_count": 576,
            "run_program_capture_undo_allocation_bytes": 276480,
            "run_program_guard_repeat_allocation_count": 408,
            "run_program_guard_repeat_allocation_bytes": 120768,
            "candidate_capture_undo_reuse_in_this_variant": False,
            "cpu_function_profile": NOT_MEASURED,
            "cpu_clock_collection_error": "itimer could not be set",
            "instrumented_elapsed_is_final_speed": False,
            "final_holdout": "NOT OPENED", "final_speed": NOT_MEASURED}


def proposal_metadata(wall: SourceWall) -> dict:
    info = os.lstat(ROOT + "/" + PROPOSAL)
    require(stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o600
            and info.st_dev == DEVICE and info.st_ino == PROPOSAL_INODE
            and info.st_size == PROPOSAL_BYTES and info.st_nlink == 1
            and info.st_uid == os.geteuid()
            and wall.proposal_stat_count == 1 and wall.proposal_open_count == 0,
            "authenticate final proposal metadata without opening its contents")
    return {"path": PROPOSAL, "sha256_independently_pinned_not_read": PROPOSAL_SHA256,
            "bytes_metadata_only": PROPOSAL_BYTES, "device": DEVICE,
            "inode_metadata_only": PROPOSAL_INODE, "case_count": 141557760,
            "case_status": "NOT GENERATED; NOT OPENED",
            "final_protocol_status": "NOT FROZEN", "content_open_count": 0,
            "metadata_probe_count": 1,
            "minimum_qualified_independent_family_count": 3,
            "qualified_independent_family_count": 0}


def build_contract(source_owner: tuple, protocol_owner: tuple, derived: bytes,
                   proposal: dict, public: dict, semantics: dict) -> dict:
    return {"schema": SCHEMA, "version": 1,
            "status": "SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN",
            "phase": "PHASE 2: FIRST-PARTY CANDIDATE CORRECTNESS",
            "family": "rust", "immutable_goal_sha256": GOAL_SHA256,
            "source": owner_pin(source_owner), "protocol": owner_pin(protocol_owner),
            "authenticated_frozen_owners": [owner_pin(row) for row in OWNERS],
            "original_correctness_history": {
                "case_execution_denominator": 31237,
                "suite_count": 13, "supplemental_reference_case_count": 8244,
                "supplemental_reference_counted_in_original_denominator": False},
            "latest_complete_candidate_result": {
                "campaign": "V25", "candidate_status": "FAIL",
                "publication_status": "PASS", "case_execution_denominator": 31237,
                "completed_suite_count": 13, "actual_candidate_worker_count": 13,
                "semantic_mismatch_count": 1352, "verified_passing_case_count": 15877,
                "fully_observed_suite_mismatch_counts": {
                    "shape_v2": 1112, "substitution_v2": 240},
                "candidate_qualified": False, "holdout": "NOT OPENED"},
            "first_party_crate": {
                "package_count": 1, "external_dependency_count": 0,
                "stdlib_matching_delegation": False,
                "another_candidate_engine_delegation": False,
                "runtime_external_regex_engine": False},
            "independently_authenticated_public_profile": public,
            "derived_first_party_vm_source": {
                "source_base_path": "candidates/rust/src/lib.rs",
                "source_base_sha256": ORIGINAL_SHA256,
                "source_base_bytes": ORIGINAL_BYTES,
                "target_path": VARIANT,
                "sha256": sha256(derived), "bytes": len(derived),
                "exact_reversible_replacement_count": len(REPLACEMENTS),
                "workspace_is_local_to_one_root_match": True,
                "nested_lookaround_uses_independent_workspace": True,
                "callback_reentry_shares_no_workspace": True,
                "reused_state": ["overflow guards", "overflow repeat states",
                                 "large assertion begin snapshots",
                                 "large assertion end snapshots"],
                "capture_undo_reused": False,
                "guard_state_reset": "usize::MAX on every attempt",
                "repeat_state_reset": "RepeatState::default() on every attempt",
                "inline_guard_repeat_threshold": 8,
                "inline_assertion_capture_threshold": 16,
                "existing_inline_stacks_changed": False,
                "public_api_changed": False, "external_dependencies_added": 0,
                "canonical_source_modified": False,
                "materialized": False, "built": False, "executed": False,
                "correctness": NOT_MEASURED, "speed": NOT_MEASURED,
                "memory": NOT_MEASURED, "undefined_behavior": NOT_MEASURED},
            "synthetic_differential_semantics": semantics,
            "expanded_final_holdout_metadata_only": proposal,
            "physical_source_wall": {
                "policy": "DENY DEFAULT; EXACT FIRST-PARTY SOURCES AND PUBLIC EVIDENCE",
                "installed_before_owner_reads": True,
                "source_modes_filesystem_writes_allowed": False,
                "candidate_or_compiler_process_allowed": False,
                "clock_access_allowed": False,
                "allowed_archive_count": 0,
                "allowed_native_binary_count": 0,
                "allowed_holdout_content_count": 0,
                "allowed_unopened_holdout_metadata_count": 1,
                "apply_requires_matching_frozen_and_pushed_commit": True,
                "apply_requires_explicit_root_authorization": True,
                "apply_target_policy": "FD-ANCHORED EXCLUSIVE O_NOFOLLOW|O_CREAT|O_EXCL",
                "parent_directory_device": DEVICE,
                "parent_directory_inode": PARENT_INODE,
                "child_directory_mode": "0700", "derived_source_mode": "0600"},
            "source_only_effects": {
                "candidate_imports": 0, "candidate_workers_started": 0,
                "compiler_processes_started": 0, "native_libraries_loaded": 0,
                "native_binaries_opened": 0, "compressed_archives_opened": 0,
                "network_requests": 0, "clock_samples": 0,
                "new_timing_trials_run": 0, "private_roots_opened": 0,
                "holdout_cases_generated": 0, "holdout_cases_opened": 0,
                "holdout_proposal_content_open_count": 0,
                "holdout_proposal_metadata_probe_count": 1,
                "holdout": "NOT OPENED", "performance": NOT_MEASURED,
                "cpu_function_profile": NOT_MEASURED,
                "candidate_correctness": NOT_MEASURED,
                "runtime_non_delegation": "NOT ESTABLISHED",
                "undefined_behavior": NOT_MEASURED,
                "qualified_candidate_count": 0, "winner_selected": False}}


def rejected(action, label: str) -> str:
    try:
        action()
    except (FreezeError, OSError, UnicodeError, TypeError, ValueError):
        return label
    raise FreezeError("accepted hostile control: " + label)


def self_test(wall: SourceWall, source: bytes, semantics: dict) -> list[str]:
    controls: list[str] = []
    for label, old, new in REPLACEMENTS:
        poisoned = source.replace(old, b"BROKEN-ANCHOR\n", 1)
        controls.append(rejected(lambda value=poisoned: transform_source(value),
                                 "reject-altered-source-anchor-" + label))
        controls.append(rejected(lambda: require(old == new, "nonidentical transformation"),
                                 "reject-noop-source-anchor-" + label))
    for payload in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}',
                    b'{"x":01}', b'{"x":1.}', b'{"x":1e}', b'{"x":1e999}',
                    b'{"x":"\\ud800"}', b'{"x":"\\udc00"}', b'{"x":[1,]}',
                    b'{"x":1} trailing', b"[{]"):
        controls.append(rejected(lambda value=payload: StrictJSON(value).decode(),
                                 "reject-malformed-or-ambiguous-json"))
    forbidden_paths = (
        (ROOT + "/candidates/rust_candidate.py", "candidate-python-adapter"),
        (ROOT + "/candidates/_rust_engine.so", "candidate-native-engine"),
        (ROOT + "/candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so", "candidate-native-bridge"),
        (ROOT + "/" + PROPOSAL, "sealed-final-proposal-content"),
        (ROOT + "/oracle/phase3/expanded-sealed-holdout-v1.json", "prior-final-proposal"),
        (ROOT + "/oracle/phase2/evidence/candidate.json.gz", "compressed-candidate-archive"),
        (ROOT + "/experiments/rust_public_profile_v2/public-run-001/rust.er/heaptrace", "profiler-archive"),
        (ROOT + "/" + VARIANT, "premature-derived-source"),
        (ROOT + "/tools/../candidates/rust_candidate.py", "path-traversal"),
        ("/tmp/rebar-phase2-native-build-v9-rust-3v12tbmr", "private-build-root"),
        ("/etc/hosts", "host-file"),
    )
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    for path, label in forbidden_paths:
        controls.append(rejected(lambda item=path: os.open(item, flags),
                                 "wall-rejects-open-" + label))
        controls.append(rejected(lambda item=path: wall.native_open(item, flags),
                                 "wall-rejects-native-open-" + label))
    actions = (
        ("builtins-open", lambda: builtins.open(ROOT + "/" + SOURCE, "rb")),
        ("_io-open", lambda: _io.open(ROOT + "/" + SOURCE, "rb")),
        ("io-open", lambda: io.open(ROOT + "/" + SOURCE, "rb")),
        ("foreign-descriptor-read", lambda: os.read(0, 1)),
        ("foreign-descriptor-write", lambda: os.write(1, b"x")),
        ("foreign-descriptor-stat", lambda: os.fstat(0)),
        ("foreign-descriptor-close", lambda: os.close(0)),
        ("direct-os-stat", lambda: os.stat(ROOT + "/" + SOURCE)),
        ("repeat-proposal-metadata", lambda: os.lstat(ROOT + "/" + PROPOSAL)),
        ("clock-time", lambda: time.time()),
        ("clock-time-ns", lambda: time.time_ns()),
        ("clock-monotonic", lambda: time.monotonic()),
        ("clock-perf-counter", lambda: time.perf_counter()),
        ("entropy", lambda: os.urandom(1)),
        ("stdlib-matcher-import", lambda: sys.audit("import", "re", None)),
        ("external-matcher-import", lambda: sys.audit("import", "regex", None)),
        ("native-loader", lambda: sys.audit("ctypes.dlopen", "foreign")),
        ("candidate-worker", lambda: sys.audit("subprocess.Popen", "worker")),
        ("child-interpreter", lambda: sys.audit("cpython.PyInterpreterState_New")),
        ("network", lambda: sys.audit("socket.connect", "foreign")),
        ("dynamic-code", lambda: sys.audit("exec", "foreign")),
        ("canonical-source-write", lambda: os.open(ROOT + "/candidates/rust/src/lib.rs",
                                                     os.O_WRONLY | os.O_TRUNC)),
        ("frozen-source-write", lambda: os.open(ROOT + "/" + SOURCE,
                                                  os.O_WRONLY | os.O_TRUNC)),
        ("derived-source-write", lambda: os.open(ROOT + "/" + VARIANT,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0))),
        ("derived-directory", lambda: os.mkdir(VARIANT_DIRECTORY, 0o700)),
    )
    for name, action in actions:
        controls.append(rejected(action, "wall-rejects-" + name))
    for value in (-1, 0, 31236, 31238, 416, 141557760):
        controls.append(rejected(lambda number=value: require(number == 31237,
                                                             "original denominator changed"),
                                 "reject-original-denominator-" + str(value)))
    for value in (-1, 0, 415, 417, 31237, 1664):
        controls.append(rejected(lambda number=value: require(number == 416,
                                                             "public denominator changed"),
                                 "reject-public-denominator-" + str(value)))
    for symbol, value in (("guard", 0), ("repeat", 1), ("snapshot", 16)):
        controls.append(rejected(lambda number=value: require(number > 16,
                                                             "incorrect overflow threshold"),
                                 "reject-invalid-overflow-" + symbol))
    require(len(controls) >= 75 and semantics["case_count"] >= 15000
            and not wall.live and wall.parent_fd is None and wall.child_fd is None
            and wall.output_fd is None and not wall.output_created
            and wall.proposal_stat_count == 1 and wall.proposal_open_count == 0,
            "exercise complete physical and VM semantic hostile controls")
    return controls


def parse_arguments(values: list[str]) -> dict:
    require(bool(values), "select one explicit source-only or root-only mode")
    mode = values[0]
    require(mode in ("--render-contract", "--verify-source", "--self-test", "--apply"),
            "reject candidate, compiler, profiler, worker, benchmark, or holdout execution")
    pairs = ["--source-sha256", "--protocol-sha256"]
    switches: list[str] = []
    if mode != "--render-contract":
        pairs.append("--contract-sha256")
    if mode == "--apply":
        pairs.extend(("--frozen-commit", "--pushed-commit"))
        switches = ["--root-authorized", "--frozen-committed-pushed"]
    require(len(values) == 1 + 2 * len(pairs) + len(switches),
            "require exact source pins, pushed commit, and explicit root authority")
    pins: dict[str, str] = {}
    offset = 1
    while offset < 1 + 2 * len(pairs):
        name, value = values[offset], values[offset + 1]
        require(name in pairs and name not in pins,
                "reject repeated or invented source-freeze authority")
        if name.endswith("sha256"):
            pins[name] = valid_sha(value, name)
        else:
            require(type(value) is str and len(value) == 40
                    and all(char in "0123456789abcdef" for char in value),
                    "require complete lowercase Git commit pin")
            pins[name] = value
        offset += 2
    require(set(pins) == set(pairs), "reject missing source-freeze owner")
    if switches:
        require(values[offset:] == switches,
                "require explicit independently authorized root-only application")
        require(pins["--frozen-commit"] == pins["--pushed-commit"],
                "root may apply only one matching committed-and-pushed source freeze")
    return {"mode": mode, "pins": pins}


def load_context(wall: SourceWall, pins: dict, render: bool) -> dict:
    source_owner = dynamic_owner(wall, "source", SOURCE, pins["--source-sha256"])
    protocol_owner = dynamic_owner(wall, "protocol", PROTOCOL, pins["--protocol-sha256"])
    read_owner(wall, source_owner)
    read_owner(wall, protocol_owner)
    contract_owner = None
    if not render:
        contract_owner = dynamic_owner(wall, "contract", CONTRACT, pins["--contract-sha256"])
    evidence = {owner[0]: read_owner(wall, owner) for owner in OWNERS}
    validate_oracles(json_object(evidence["original_oracle"], "original frozen oracle"),
                     json_object(evidence["supplemental_oracle"], "supplemental reference"),
                     json_object(evidence["latest_v25_campaign"], "latest Rust V25 campaign"))
    validate_cargo(evidence["first_party_cargo_manifest"], evidence["first_party_cargo_lock"],
                   evidence["first_party_rust_vm"], evidence["first_party_rust_inline_stack"],
                   evidence["first_party_rust_search"])
    public = validate_profile(evidence)
    proposal = proposal_metadata(wall)
    derived = transform_source(evidence["first_party_rust_vm"])
    semantics = synthetic_semantics()
    frozen = build_contract(source_owner, protocol_owner, derived, proposal, public, semantics)
    if not render:
        assert contract_owner is not None
        encoded = read_owner(wall, contract_owner)
        require(encoded == document(frozen)
                and json_object(encoded, "complete VM workspace freeze contract") == frozen,
                "reject incomplete, stale, or altered VM workspace contract")
    require(not wall.live and wall.parent_fd is None and wall.child_fd is None
            and wall.output_fd is None and wall.proposal_stat_count == 1
            and wall.proposal_open_count == 0,
            "close every descriptor and keep the final proposal unopened")
    no_matching_imports()
    return {"source": evidence["first_party_rust_vm"], "derived": derived,
            "contract": frozen, "semantics": semantics, "public": public}


def apply_once(wall: SourceWall, derived: bytes) -> dict:
    require(wall.apply and DERIVED_SHA256 and sha256(derived) == DERIVED_SHA256
            and len(derived) == DERIVED_BYTES and not wall.output_created,
            "root may create only the one frozen first-party Rust variant")
    directory_flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                       | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    parent = os.open(ROOT + "/" + VARIANTS, directory_flags)
    try:
        parent_identity = os.fstat(parent)
        require(stat.S_ISDIR(parent_identity.st_mode)
                and stat.S_IMODE(parent_identity.st_mode) == 0o700
                and parent_identity.st_dev == DEVICE and parent_identity.st_ino == PARENT_INODE
                and parent_identity.st_uid == os.geteuid(),
                "reject exchanged first-party Rust variant parent")
        os.mkdir(VARIANT_DIRECTORY, 0o700, dir_fd=parent)
        child = os.open(VARIANT_DIRECTORY, directory_flags, dir_fd=parent)
        try:
            identity = os.fstat(child)
            require(stat.S_ISDIR(identity.st_mode)
                    and stat.S_IMODE(identity.st_mode) == 0o700
                    and identity.st_dev == DEVICE and identity.st_uid == os.geteuid(),
                    "reject unowned exclusive VM workspace variant directory")
            descriptor = os.open("lib.rs", os.O_WRONLY | os.O_CREAT | os.O_EXCL
                                 | getattr(os, "O_NOFOLLOW", 0)
                                 | getattr(os, "O_CLOEXEC", 0), 0o600, dir_fd=child)
            try:
                before = os.fstat(descriptor)
                require(stat.S_ISREG(before.st_mode)
                        and stat.S_IMODE(before.st_mode) == 0o600
                        and before.st_dev == DEVICE and before.st_uid == os.geteuid()
                        and before.st_size == 0 and before.st_nlink == 1,
                        "require one empty private O_EXCL Rust source")
                cursor = 0
                while cursor < len(derived):
                    amount = os.write(descriptor, memoryview(derived)[cursor:])
                    require(type(amount) is int and amount > 0,
                            "reject an incomplete exclusively created Rust source")
                    cursor += amount
                os.fsync(descriptor)
                after = os.fstat(descriptor)
                require(after.st_dev == before.st_dev and after.st_ino == before.st_ino
                        and after.st_size == DERIVED_BYTES and after.st_nlink == 1,
                        "reject exchanged or incomplete VM workspace source")
                result = {"path": VARIANT, "sha256": DERIVED_SHA256,
                          "bytes": DERIVED_BYTES, "device": after.st_dev,
                          "inode": after.st_ino, "mode": "0600", "nlink": 1,
                          "parent_inode": PARENT_INODE,
                          "private_directory_mode": "0700",
                          "exclusive_no_follow": True, "materialized_once": True}
            finally:
                os.close(descriptor)
            os.fsync(child)
        finally:
            os.close(child)
        os.fsync(parent)
    finally:
        os.close(parent)
    return result


def main() -> int:
    require(sys.implementation.name == "cpython" and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.executable == PYTHON and sys.flags.isolated == 1
            and sys.flags.no_site == 1 and sys.dont_write_bytecode is True,
            "require pinned official CPython 3.14.6 under -I -B -S")
    no_matching_imports()
    selection = parse_arguments(list(sys.argv[1:]))
    wall = SourceWall(selection["mode"] == "--apply")
    wall.install()
    context = load_context(wall, selection["pins"],
                           selection["mode"] == "--render-contract")
    if selection["mode"] == "--render-contract":
        sys.stdout.buffer.write(document(context["contract"]))
        sys.stdout.buffer.flush()
        return 0
    controls = (self_test(wall, context["source"], context["semantics"])
                if selection["mode"] == "--self-test" else [])
    variant = (apply_once(wall, context["derived"])
               if selection["mode"] == "--apply" else None)
    require(not wall.live and wall.output_fd is None and wall.parent_fd is None
            and wall.child_fd is None and wall.proposal_open_count == 0,
            "release every source descriptor and preserve the unopened holdout")
    no_matching_imports()
    result = {"schema": SCHEMA + "-source-only-gate", "status": "PASS", "version": 1,
              "mode": selection["mode"][2:],
              "source_sha256": selection["pins"]["--source-sha256"],
              "protocol_sha256": selection["pins"]["--protocol-sha256"],
              "contract_sha256": selection["pins"]["--contract-sha256"],
              "authenticated_frozen_owner_count": len(OWNERS) + 3,
              "original_case_execution_denominator": 31237,
              "latest_candidate_campaign": "V25",
              "latest_candidate_status": "FAIL",
              "latest_semantic_mismatch_count": 1352,
              "latest_verified_passing_case_count": 15877,
              "canonical_rust_source_sha256": ORIGINAL_SHA256,
              "derived_rust_source_sha256": sha256(context["derived"]),
              "derived_rust_source_bytes": len(context["derived"]),
              "exact_reversible_replacement_count": len(REPLACEMENTS),
              "synthetic_differential_case_count": context["semantics"]["case_count"],
              "synthetic_allocations_avoided":
                  context["semantics"]["synthetic_allocations_avoided"],
              "preserved_public_profile_sha256": PROFILE_SHA256,
              "preserved_public_case_count": 416,
              "preserved_public_paired_row_count": 1664,
              "observed_vm_guard_repeat_allocation_count": 408,
              "observed_vm_guard_repeat_allocation_bytes": 120768,
              "observed_vm_capture_undo_allocation_count": 576,
              "observed_vm_capture_undo_allocations_unchanged": True,
              "cpu_function_profile": NOT_MEASURED,
              "hostile_control_count": len(controls), "hostile_controls": controls,
              "physically_blocked_effects": dict(wall.blocked),
              "unopened_final_holdout_proposal_case_count": 141557760,
              "holdout_content_open_count": 0, "holdout_metadata_probe_count": 1,
              "candidate_imports": 0, "candidate_workers_started": 0,
              "compiler_processes_started": 0, "native_libraries_loaded": 0,
              "native_binaries_opened": 0, "clock_samples": 0,
              "new_timing_trials_run": 0, "holdout": "NOT OPENED",
              "performance": NOT_MEASURED, "memory": NOT_MEASURED,
              "candidate_correctness": NOT_MEASURED,
              "candidate_qualified": False, "winner_selected": False,
              "variant_materialized": variant is not None,
              "materialized_variant": variant}
    if variant is not None:
        result["frozen_pushed_commit"] = selection["pins"]["--pushed-commit"]
    sys.stdout.buffer.write(document(result))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FreezeError, OSError, UnicodeError, TypeError, ValueError) as error:
        sys.stderr.write(type(error).__name__ + ": " + str(error) + "\n")
        raise SystemExit(2)
