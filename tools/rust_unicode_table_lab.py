#!/usr/bin/env python3
"""Reproduce and compare from-scratch, exact CPython 3.14 Unicode tables.

The fourteen native scalar variants use only pinned Unicode-16 character data.
All timing rows are checked, paired and retained; this is an internal
architecture experiment, not the end-to-end regex performance holdout.
"""

from __future__ import annotations

import argparse
import array
import collections
import ctypes
import gzip
import hashlib
import json
import math
import pathlib
import random
import resource
import statistics
import subprocess
import sys
import time
import unicodedata


POINTS = 0x110000
PAGE_SIZE = 256
FOLD_PAGE_SIZE = 128
TRIALS = 13
WARMUPS = 4
BOOTSTRAPS = 2000
ORDER_SEED = 1985072201
BOOTSTRAP_SEED = 1985072202
TARGET_CHARACTERS = 100_000
SUBJECTS = (
    ("unicode-word-lines", 0),
    ("unicode-word-lines", 3),
    ("unicode-word-lines", 7),
    ("unicode-casefold", 0),
    ("unicode-casefold", 3),
    ("unicode-casefold", 7),
    ("combining-wide", 0),
    ("combining-wide", 7),
)
WORKLOADS = ("word", "decimal", "whitespace", "simple-lower", "canonical-fold")


RUST_TEMPLATE = r'''
use std::hint::black_box;
use std::slice;

unsafe extern "C" {
    fn _PyUnicode_IsAlpha(value: u32) -> i32;
    fn _PyUnicode_IsDecimalDigit(value: u32) -> i32;
    fn _PyUnicode_IsDigit(value: u32) -> i32;
    fn _PyUnicode_IsNumeric(value: u32) -> i32;
    fn _PyUnicode_IsWhitespace(value: u32) -> i32;
    fn _PyUnicode_ToLowercase(value: u32) -> u32;
}

__GENERATED_TABLES__

#[inline(always)]
fn ascii_word(value: u32) -> bool {
    value == 0x5f
        || value.wrapping_sub(0x30) <= 9
        || (value | 0x20).wrapping_sub(0x61) <= 25
}

#[inline(always)]
fn ascii_space(value: u32) -> bool {
    matches!(value, 9..=13 | 0x1c..=0x20)
}

#[inline(always)]
fn direct_word(value: u32) -> u32 {
    if value < 128 {
        return u32::from(ascii_word(value));
    }
    unsafe {
        u32::from(
            _PyUnicode_IsAlpha(value) != 0
                || _PyUnicode_IsDecimalDigit(value) != 0
                || _PyUnicode_IsDigit(value) != 0
                || _PyUnicode_IsNumeric(value) != 0,
        )
    }
}

#[inline(always)]
fn direct_decimal(value: u32) -> u32 {
    if value < 128 {
        return u32::from(value.wrapping_sub(0x30) <= 9);
    }
    unsafe { u32::from(_PyUnicode_IsDecimalDigit(value) != 0) }
}

#[inline(always)]
fn direct_space(value: u32) -> u32 {
    if value < 128 {
        return u32::from(ascii_space(value));
    }
    unsafe { u32::from(_PyUnicode_IsWhitespace(value) != 0) }
}

#[inline(always)]
fn direct_lower(value: u32) -> u32 {
    if value < 128 {
        if value.wrapping_sub(0x41) <= 25 {
            value + 32
        } else {
            value
        }
    } else {
        unsafe { _PyUnicode_ToLowercase(value) }
    }
}

#[inline(always)]
fn canonical_component(value: u32) -> u32 {
    match value {
        __CANONICAL_MATCH_ARMS__
        other => other,
    }
}

#[inline(always)]
fn direct_canonical(value: u32) -> u32 {
    canonical_component(direct_lower(value))
}

#[cfg(rebar_unicode_tables)]
#[inline(always)]
fn table_property(value: u32) -> u8 {
    #[cfg(rebar_unicode_latin1)]
    if value < 256 {
        return PROPERTY_PAGES[value as usize];
    }
    #[cfg(rebar_unicode_property4k)]
    if value < 4096 {
        return PROPERTY_PREFIX_4K[value as usize];
    }
    #[cfg(rebar_unicode_property16k)]
    if value < 16384 {
        return PROPERTY_PREFIX_16K[value as usize];
    }
    #[cfg(rebar_unicode_propertybmp)]
    if value < 65536 {
        return PROPERTY_PREFIX_BMP[value as usize];
    }
    #[cfg(rebar_unicode_u8index)]
    let page = PROPERTY_PAGE_INDEX_U8[(value >> 8) as usize] as usize;
    #[cfg(not(rebar_unicode_u8index))]
    let page = PROPERTY_PAGE_INDEX_U16[(value >> 8) as usize] as usize;
    PROPERTY_PAGES[page * 256 + (value as usize & 255)]
}

#[cfg(rebar_unicode_tables)]
#[inline(always)]
fn table_word(value: u32) -> u32 {
    if value < 128 {
        u32::from(ascii_word(value))
    } else {
        u32::from(table_property(value) & 1 != 0)
    }
}

#[cfg(rebar_unicode_tables)]
#[inline(always)]
fn table_decimal(value: u32) -> u32 {
    if value < 128 {
        u32::from(value.wrapping_sub(0x30) <= 9)
    } else {
        u32::from(table_property(value) & 2 != 0)
    }
}

#[cfg(rebar_unicode_tables)]
#[inline(always)]
fn table_space(value: u32) -> u32 {
    if value < 128 {
        u32::from(ascii_space(value))
    } else {
        u32::from(table_property(value) & 32 != 0)
    }
}

#[cfg(all(
    rebar_unicode_tables,
    not(rebar_unicode_i16),
    not(rebar_unicode_fold128)
))]
#[inline(always)]
fn table_lower(value: u32) -> u32 {
    if value < 128 {
        direct_lower(value)
    } else {
        #[cfg(rebar_unicode_u8index)]
        let page = LOWER_PAGE_INDEX_U8[(value >> 8) as usize] as usize;
        #[cfg(not(rebar_unicode_u8index))]
        let page = LOWER_PAGE_INDEX_U16[(value >> 8) as usize] as usize;
        value.wrapping_add_signed(LOWER_PAGES[page * 256 + (value as usize & 255)])
    }
}

#[cfg(all(
    rebar_unicode_tables,
    not(rebar_unicode_i16),
    rebar_unicode_fold128
))]
#[inline(always)]
fn table_lower(value: u32) -> u32 {
    if value < 128 {
        return direct_lower(value);
    }
    #[cfg(rebar_unicode_foldprefix4k)]
    if value < 4096 {
        return value.wrapping_add_signed(LOWER_PREFIX_4K[value as usize]);
    }
    let page = LOWER128_PAGE_INDEX_U8[(value >> 7) as usize] as usize;
    value.wrapping_add_signed(LOWER128_PAGES[page * 128 + (value as usize & 127)])
}

#[cfg(all(rebar_unicode_tables, rebar_unicode_i16))]
#[inline(always)]
fn table_lower(value: u32) -> u32 {
    if value < 128 {
        return direct_lower(value);
    }
    let page = LOWER16_PAGE_INDEX_U8[(value >> 8) as usize] as usize;
    let delta = LOWER16_PAGES[page * 256 + (value as usize & 255)];
    if delta == i16::MIN {
        match value {
            __LOWER16_OUTLIER_ARMS__
            other => other,
        }
    } else {
        value.wrapping_add_signed(i32::from(delta))
    }
}

#[cfg(all(
    rebar_unicode_tables,
    not(rebar_unicode_i16),
    not(rebar_unicode_fold128)
))]
#[inline(always)]
fn table_canonical(value: u32) -> u32 {
    if value < 128 {
        direct_lower(value)
    } else {
        #[cfg(rebar_unicode_u8index)]
        let page = CANONICAL_PAGE_INDEX_U8[(value >> 8) as usize] as usize;
        #[cfg(not(rebar_unicode_u8index))]
        let page = CANONICAL_PAGE_INDEX_U16[(value >> 8) as usize] as usize;
        value.wrapping_add_signed(CANONICAL_PAGES[page * 256 + (value as usize & 255)])
    }
}

#[cfg(all(
    rebar_unicode_tables,
    not(rebar_unicode_i16),
    rebar_unicode_fold128
))]
#[inline(always)]
fn table_canonical(value: u32) -> u32 {
    if value < 128 {
        return direct_lower(value);
    }
    #[cfg(rebar_unicode_foldprefix4k)]
    if value < 4096 {
        return value.wrapping_add_signed(CANONICAL_PREFIX_4K[value as usize]);
    }
    let page = CANONICAL128_PAGE_INDEX_U8[(value >> 7) as usize] as usize;
    value.wrapping_add_signed(CANONICAL128_PAGES[page * 128 + (value as usize & 127)])
}

#[cfg(all(rebar_unicode_tables, rebar_unicode_i16))]
#[inline(always)]
fn table_canonical(value: u32) -> u32 {
    if value < 128 {
        return direct_lower(value);
    }
    let page = CANONICAL16_PAGE_INDEX_U8[(value >> 8) as usize] as usize;
    let delta = CANONICAL16_PAGES[page * 256 + (value as usize & 255)];
    if delta == i16::MIN {
        match value {
            __CANONICAL16_OUTLIER_ARMS__
            other => other,
        }
    } else {
        value.wrapping_add_signed(i32::from(delta))
    }
}

#[inline(always)]
fn scan<F: Fn(u32) -> u32>(data: &[u32], repetitions: usize, operation: F) -> u64 {
    let mut checksum = black_box(0xcbf29ce484222325_u64);
    for _ in 0..repetitions {
        for &character in black_box(data) {
            checksum = checksum.rotate_left(5)
                ^ u64::from(operation(character)).wrapping_add(0x9e3779b97f4a7c15);
        }
    }
    black_box(checksum)
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn rebar_unicode_bench_direct(
    data: *const u32,
    length: usize,
    repetitions: usize,
    mode: u32,
) -> u64 {
    if data.is_null() {
        return 0;
    }
    let subject = unsafe { slice::from_raw_parts(data, length) };
    match mode {
        0 => scan(subject, repetitions, direct_word),
        1 => scan(subject, repetitions, direct_decimal),
        2 => scan(subject, repetitions, direct_space),
        3 => scan(subject, repetitions, direct_lower),
        4 => scan(subject, repetitions, direct_canonical),
        _ => 0,
    }
}

#[cfg(rebar_unicode_tables)]
#[unsafe(no_mangle)]
pub unsafe extern "C" fn rebar_unicode_bench_table(
    data: *const u32,
    length: usize,
    repetitions: usize,
    mode: u32,
) -> u64 {
    if data.is_null() {
        return 0;
    }
    let subject = unsafe { slice::from_raw_parts(data, length) };
    match mode {
        0 => scan(subject, repetitions, table_word),
        1 => scan(subject, repetitions, table_decimal),
        2 => scan(subject, repetitions, table_space),
        3 => scan(subject, repetitions, table_lower),
        4 => scan(subject, repetitions, table_canonical),
        _ => 0,
    }
}
'''


def deduplicate(
    values: list[int] | bytearray,
    page_size: int = PAGE_SIZE,
) -> tuple[list[int], list[int]]:
    lookup: dict[tuple[int, ...], int] = {}
    indexes: list[int] = []
    pages: list[int] = []
    for start in range(0, len(values), page_size):
        page = tuple(values[start : start + page_size])
        number = lookup.get(page)
        if number is None:
            number = len(lookup)
            lookup[page] = number
            pages.extend(page)
        indexes.append(number)
    if len(indexes) != POINTS // page_size or len(lookup) > 0xFFFF:
        raise AssertionError("invalid generated Unicode page index")
    return indexes, pages


def render_array(
    name: str,
    kind: str,
    values: list[int],
    condition: str = "rebar_unicode_tables",
) -> str:
    rows = []
    for start in range(0, len(values), 24):
        rows.append("    " + ", ".join(map(str, values[start : start + 24])) + ",")
    return (
        f"#[cfg({condition})]\n"
        + f"static {name}: [{kind}; {len(values)}] = [\n"
        + "\n".join(rows)
        + "\n];\n"
    )


def source_digest(values: list[int] | bytearray, typecode: str) -> str:
    """Hash explicitly little-endian, full-plane CPython character data."""

    encoded = array.array(typecode, values)
    if sys.byteorder != "little" and encoded.itemsize != 1:
        encoded.byteswap()
    return hashlib.sha256(encoded.tobytes()).hexdigest()


def production_array(name: str, kind: str, values: list[int]) -> str:
    rows = [
        "    " + ", ".join(map(str, values[start : start + 24])) + ","
        for start in range(0, len(values), 24)
    ]
    return (
        "#[rustfmt::skip]\n"
        + f"static {name}: [{kind}; {len(values)}] = [\n"
        + "\n".join(rows)
        + "\n];\n"
    )


def contiguous_ranges(values: list[int]) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for value in values:
        if ranges and value == ranges[-1][1] + 1:
            ranges[-1] = (ranges[-1][0], value)
        else:
            ranges.append((value, value))
    return ranges


def production_source(
    *,
    property_index: list[int],
    property_pages: list[int],
    lower_index: list[int],
    lower_pages: list[int],
    upper_index: list[int],
    upper_pages: list[int],
    canonical_index: list[int],
    canonical_pages: list[int],
    multi_upper: list[int],
    digests: dict[str, str],
) -> str:
    """Render the measured, dependency-free production architecture.

    The lab orders property bits for convenient experiments. Production keeps
    the existing matcher contract: decimal=1, whitespace=2, word=4.
    """

    def production_mask(value: int) -> int:
        return (
            ((value & 0x02) >> 1)
            | ((value & 0x20) >> 4)
            | ((value & 0x01) << 2)
            | ((value & 0x04) << 1)
            | ((value & 0x08) << 1)
            | ((value & 0x10) << 1)
            | (value & 0xC0)
        )

    masks = [production_mask(value) for value in property_pages]
    property_prefix = [
        masks[(property_index[value >> 8] << 8) + (value & 0xff)]
        for value in range(16_384)
    ]
    lower_prefix = [
        lower_pages[(lower_index[value >> 7] << 7) + (value & 0x7f)]
        for value in range(4_096)
    ]
    literal_prefix = [
        canonical_pages[(canonical_index[value >> 7] << 7) + (value & 0x7f)]
        for value in range(4_096)
    ]
    arms = []
    for first, last in contiguous_ranges(multi_upper):
        if first == last:
            arms.append(f"0x{first:x}")
        else:
            arms.append(f"0x{first:x}..=0x{last:x}")
    multi_upper_expression = " |\n        ".join(arms)
    blocks = "\n".join(
        (
            production_array("PROPERTY_PAGE_INDEX", "u8", property_index),
            production_array("PROPERTY_PAGES", "u8", masks),
            production_array("PROPERTY_PREFIX_16K", "u8", property_prefix),
            production_array("LOWER_PAGE_INDEX", "u8", lower_index),
            production_array("LOWER_PAGES", "i32", lower_pages),
            production_array("LOWER_PREFIX_4K", "i32", lower_prefix),
            production_array("UPPER_PAGE_INDEX", "u8", upper_index),
            production_array("UPPER_PAGES", "i32", upper_pages),
            production_array("LITERAL_PAGE_INDEX", "u8", canonical_index),
            production_array("LITERAL_PAGES", "i32", canonical_pages),
            production_array("LITERAL_PREFIX_4K", "i32", literal_prefix),
        )
    )
    return (
        "// Generated by tools/rust_unicode_table_lab.py; do not hand-edit.\n"
        "// Pinned oracle: CPython 3.14.6, Unicode 16.0.0.\n"
        f"// Property source SHA-256: {digests['properties']}\n"
        f"// Simple-lower source SHA-256: {digests['simple_lower']}\n"
        f"// Simple-upper source SHA-256: {digests['simple_upper']}\n"
        f"// Literal-fold source SHA-256: {digests['literal_fold']}\n"
        "// No regular-expression engine, Python callback, or external package.\n\n"
        "pub(crate) const CATEGORY_DECIMAL: u8 = 1;\n"
        "pub(crate) const CATEGORY_WHITESPACE: u8 = 2;\n"
        "pub(crate) const CATEGORY_WORD: u8 = 4;\n"
        "pub(crate) const CATEGORY_DIGIT: u8 = 8;\n"
        "pub(crate) const CATEGORY_NUMERIC: u8 = 16;\n"
        "pub(crate) const CATEGORY_ALPHA: u8 = 32;\n"
        "pub(crate) const CATEGORY_XID_START: u8 = 64;\n"
        "pub(crate) const CATEGORY_XID_CONTINUE: u8 = 128;\n\n"
        + blocks
        + "\n"
        + """#[inline(always)]
pub(crate) fn category_mask(value: u32) -> u8 {
    if value >= 0x11_0000 {
        return 0;
    }
    if value < 0x4000 {
        return PROPERTY_PREFIX_16K[value as usize];
    }
    let page = usize::from(PROPERTY_PAGE_INDEX[(value >> 8) as usize]);
    PROPERTY_PAGES[(page << 8) + (value as usize & 0xff)]
}

#[inline(always)]
pub(crate) fn simple_lower(value: u32) -> u32 {
    if value < 128 {
        return if value.wrapping_sub(0x41) < 26 {
            value + 32
        } else {
            value
        };
    }
    if value >= 0x11_0000 {
        return value;
    }
    if value < 0x1000 {
        return value.wrapping_add_signed(LOWER_PREFIX_4K[value as usize]);
    }
    let page = usize::from(LOWER_PAGE_INDEX[(value >> 7) as usize]);
    value.wrapping_add_signed(LOWER_PAGES[(page << 7) + (value as usize & 0x7f)])
}

#[inline(always)]
pub(crate) fn simple_upper(value: u32) -> u32 {
    if value < 128 {
        return if value.wrapping_sub(0x61) < 26 {
            value - 32
        } else {
            value
        };
    }
    if value >= 0x11_0000 {
        return value;
    }
    let page = usize::from(UPPER_PAGE_INDEX[(value >> 7) as usize]);
    value.wrapping_add_signed(UPPER_PAGES[(page << 7) + (value as usize & 0x7f)])
}

#[inline(always)]
pub(crate) fn literal_fold(value: u32) -> u32 {
    if value < 128 {
        return simple_lower(value);
    }
    if value >= 0x11_0000 {
        return value;
    }
    if value < 0x1000 {
        return value.wrapping_add_signed(LITERAL_PREFIX_4K[value as usize]);
    }
    let page = usize::from(LITERAL_PAGE_INDEX[(value >> 7) as usize]);
    value.wrapping_add_signed(LITERAL_PAGES[(page << 7) + (value as usize & 0x7f)])
}

#[inline(always)]
pub(crate) fn xid_start(value: u32) -> bool {
    category_mask(value) & CATEGORY_XID_START != 0
}

#[inline(always)]
pub(crate) fn xid_continue(value: u32) -> bool {
    category_mask(value) & CATEGORY_XID_CONTINUE != 0
}

#[inline(always)]
pub(crate) fn multi_upper(value: u32) -> bool {
    matches!(
        value,
        __MULTI_UPPER_ARMS__
    )
}
"""
    ).replace("__MULTI_UPPER_ARMS__", multi_upper_expression)


def validate_frozen_fixture(workspace: pathlib.Path) -> dict[str, object]:
    manifest_path = workspace / "performance" / "v6" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    suite_path = workspace / "performance" / "v6" / "suite.py"
    expected_path = workspace / "performance" / "v6" / "expected.jsonl"
    suite_hash = hashlib.sha256(suite_path.read_bytes()).hexdigest()
    expected_hash = hashlib.sha256(expected_path.read_bytes()).hexdigest()
    if manifest.get("python") != "3.14.6":
        raise RuntimeError("the v6 holdout does not use pinned CPython 3.14.6")
    if manifest.get("suite_sha256") != suite_hash:
        raise RuntimeError("the frozen v6 suite source has changed")
    if manifest.get("expected_sha256") != expected_hash:
        raise RuntimeError("the frozen v6 expected results have changed")
    if manifest.get("order_seed") != ORDER_SEED:
        raise RuntimeError("the Unicode lab order seed is not the frozen v6 seed")
    if manifest.get("bootstrap_seed") != BOOTSTRAP_SEED:
        raise RuntimeError("the Unicode lab bootstrap seed is not the frozen v6 seed")
    if manifest.get("trials") != TRIALS or manifest.get("warmups") != WARMUPS:
        raise RuntimeError("the Unicode lab trial protocol is not the frozen v6 protocol")
    return {
        "suite_sha256": suite_hash,
        "expected_sha256": expected_hash,
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "order_seed": ORDER_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
    }


def generate(
    source_path: pathlib.Path,
    production_path: pathlib.Path | None = None,
) -> dict[str, object]:
    if sys.version_info[:3] != (3, 14, 6):
        raise RuntimeError("the table generator requires pinned CPython 3.14.6")
    if unicodedata.unidata_version != "16.0.0":
        raise RuntimeError("the table generator requires pinned Unicode 16.0.0")
    lower = ctypes.pythonapi._PyUnicode_ToLowercase
    upper = ctypes.pythonapi._PyUnicode_ToUppercase
    lower.argtypes = upper.argtypes = (ctypes.c_uint32,)
    lower.restype = upper.restype = ctypes.c_uint32
    masks = bytearray()
    lowers: list[int] = []
    uppers: list[int] = []
    multi_upper: list[int] = []
    cased_lowers = set()
    property_counts = [0] * 8
    for codepoint in range(POINTS):
        character = chr(codepoint)
        properties = (
            character == "_" or character.isalnum(),
            character.isdecimal(),
            character.isdigit(),
            character.isnumeric(),
            character.isalpha(),
            character.isspace(),
            character.isidentifier(),
            ("a" + character).isidentifier(),
        )
        mask = 0
        for bit, present in enumerate(properties):
            mask |= int(present) << bit
            property_counts[bit] += int(present)
        masks.append(mask)
        lowered = lower(codepoint)
        uppered = upper(codepoint)
        lowers.append(lowered)
        uppers.append(uppered)
        if len(character.upper()) > 1:
            multi_upper.append(codepoint)
        if lowered != codepoint or uppered != codepoint:
            cased_lowers.add(lowered)

    groups: dict[str, list[int]] = collections.defaultdict(list)
    for value in cased_lowers:
        groups[chr(value).upper()].append(value)
    canonical = {}
    for members in groups.values():
        if len(members) < 2:
            continue
        representative = (
            0xA64B
            if 0x1C88 in members and 0xA64B in members
            else min(members)
        )
        canonical.update({member: representative for member in members})
    if len(canonical) != 50 or len({canonical[x] for x in canonical}) != 24:
        raise AssertionError("Unicode-16 full-uppercase case closure drift")

    lower_deltas = [value - index for index, value in enumerate(lowers)]
    canonical_deltas = [
        canonical.get(value, value) - index
        for index, value in enumerate(lowers)
    ]
    property_index, property_pages = deduplicate(masks)
    lower_index, lower_pages = deduplicate(lower_deltas)
    canonical_index, canonical_pages = deduplicate(canonical_deltas)
    lower128_index, lower128_pages = deduplicate(lower_deltas, 128)
    canonical128_index, canonical128_pages = deduplicate(canonical_deltas, 128)
    upper_deltas = [value - index for index, value in enumerate(uppers)]
    upper128_index, upper128_pages = deduplicate(upper_deltas, FOLD_PAGE_SIZE)
    lower16_deltas = [
        value if -32767 <= value <= 32767 else -32768
        for value in lower_deltas
    ]
    canonical16_deltas = [
        value if -32767 <= value <= 32767 else -32768
        for value in canonical_deltas
    ]
    lower16_index, lower16_pages = deduplicate(lower16_deltas)
    canonical16_index, canonical16_pages = deduplicate(canonical16_deltas)
    lower_outliers = {
        index: lowers[index]
        for index, delta in enumerate(lower_deltas)
        if not -32767 <= delta <= 32767
    }
    canonical_outliers = {
        index: canonical.get(lowers[index], lowers[index])
        for index, delta in enumerate(canonical_deltas)
        if not -32767 <= delta <= 32767
    }
    if len(property_pages) != 175 * PAGE_SIZE:
        raise AssertionError("expected 175 exact eight-property Unicode pages")
    if len(lower_outliers) != 94 or len(canonical_outliers) != 95:
        raise AssertionError("pinned 16-bit case-fold outlier count drift")
    if max(
        property_index
        + lower_index
        + canonical_index
        + lower128_index
        + canonical128_index
        + upper128_index
    ) > 255:
        raise AssertionError("Unicode-16 page indexes unexpectedly exceed u8")
    if len(multi_upper) != 102:
        raise AssertionError("pinned Unicode-16 multi-uppercase count drift")

    canonical_values = [canonical.get(value, value) for value in lowers]
    source_hashes = {
        "properties": hashlib.sha256(masks).hexdigest(),
        "simple_lower": source_digest(lowers, "I"),
        "simple_upper": source_digest(uppers, "I"),
        "literal_fold": source_digest(canonical_values, "I"),
    }

    blocks = [
        render_array(
            "PROPERTY_PAGE_INDEX_U16",
            "u16",
            property_index,
            "all(rebar_unicode_tables, not(rebar_unicode_u8index))",
        ),
        render_array(
            "PROPERTY_PAGE_INDEX_U8",
            "u8",
            property_index,
            "all(rebar_unicode_tables, rebar_unicode_u8index)",
        ),
        render_array("PROPERTY_PAGES", "u8", property_pages),
        render_array(
            "PROPERTY_PREFIX_4K",
            "u8",
            list(masks[:4096]),
            "all(rebar_unicode_tables, rebar_unicode_property4k)",
        ),
        render_array(
            "PROPERTY_PREFIX_16K",
            "u8",
            list(masks[:16384]),
            "all(rebar_unicode_tables, rebar_unicode_property16k)",
        ),
        render_array(
            "PROPERTY_PREFIX_BMP",
            "u8",
            list(masks[:65536]),
            "all(rebar_unicode_tables, rebar_unicode_propertybmp)",
        ),
        render_array(
            "LOWER_PAGE_INDEX_U16",
            "u16",
            lower_index,
            "all(rebar_unicode_tables, not(rebar_unicode_u8index), not(rebar_unicode_i16))",
        ),
        render_array(
            "LOWER_PAGE_INDEX_U8",
            "u8",
            lower_index,
            "all(rebar_unicode_tables, rebar_unicode_u8index, not(rebar_unicode_i16))",
        ),
        render_array(
            "LOWER_PAGES",
            "i32",
            lower_pages,
            "all(rebar_unicode_tables, not(rebar_unicode_i16), not(rebar_unicode_fold128))",
        ),
        render_array(
            "CANONICAL_PAGE_INDEX_U16",
            "u16",
            canonical_index,
            "all(rebar_unicode_tables, not(rebar_unicode_u8index), not(rebar_unicode_i16))",
        ),
        render_array(
            "CANONICAL_PAGE_INDEX_U8",
            "u8",
            canonical_index,
            "all(rebar_unicode_tables, rebar_unicode_u8index, not(rebar_unicode_i16))",
        ),
        render_array(
            "CANONICAL_PAGES",
            "i32",
            canonical_pages,
            "all(rebar_unicode_tables, not(rebar_unicode_i16), not(rebar_unicode_fold128))",
        ),
        render_array(
            "LOWER128_PAGE_INDEX_U8",
            "u8",
            lower128_index,
            "all(rebar_unicode_tables, rebar_unicode_fold128, not(rebar_unicode_i16))",
        ),
        render_array(
            "LOWER128_PAGES",
            "i32",
            lower128_pages,
            "all(rebar_unicode_tables, rebar_unicode_fold128, not(rebar_unicode_i16))",
        ),
        render_array(
            "LOWER_PREFIX_4K",
            "i32",
            lower_deltas[:4096],
            "all(rebar_unicode_tables, rebar_unicode_fold128, rebar_unicode_foldprefix4k)",
        ),
        render_array(
            "CANONICAL128_PAGE_INDEX_U8",
            "u8",
            canonical128_index,
            "all(rebar_unicode_tables, rebar_unicode_fold128, not(rebar_unicode_i16))",
        ),
        render_array(
            "CANONICAL128_PAGES",
            "i32",
            canonical128_pages,
            "all(rebar_unicode_tables, rebar_unicode_fold128, not(rebar_unicode_i16))",
        ),
        render_array(
            "CANONICAL_PREFIX_4K",
            "i32",
            canonical_deltas[:4096],
            "all(rebar_unicode_tables, rebar_unicode_fold128, rebar_unicode_foldprefix4k)",
        ),
        render_array(
            "LOWER16_PAGE_INDEX_U8",
            "u8",
            lower16_index,
            "all(rebar_unicode_tables, rebar_unicode_i16)",
        ),
        render_array(
            "LOWER16_PAGES",
            "i16",
            lower16_pages,
            "all(rebar_unicode_tables, rebar_unicode_i16)",
        ),
        render_array(
            "CANONICAL16_PAGE_INDEX_U8",
            "u8",
            canonical16_index,
            "all(rebar_unicode_tables, rebar_unicode_i16)",
        ),
        render_array(
            "CANONICAL16_PAGES",
            "i16",
            canonical16_pages,
            "all(rebar_unicode_tables, rebar_unicode_i16)",
        ),
    ]
    grouped: dict[int, list[int]] = collections.defaultdict(list)
    for value, representative in canonical.items():
        grouped[representative].append(value)
    match_arms = "\n        ".join(
        " | ".join(f"0x{member:x}" for member in sorted(members))
        + f" => 0x{representative:x},"
        for representative, members in sorted(grouped.items())
    )
    rendered = RUST_TEMPLATE.replace("__GENERATED_TABLES__", "\n".join(blocks))
    rendered = rendered.replace("__CANONICAL_MATCH_ARMS__", match_arms)
    def outlier_arms(outliers: dict[int, int]) -> str:
        if any(
            outliers.get(value) != value + 38864
            for value in range(0x13A0, 0x13F0)
        ):
            raise AssertionError("Cherokee outlier compression changed")
        arms = ["0x13a0..=0x13ef => value + 38864,"]
        arms.extend(
            f"0x{codepoint:x} => 0x{mapped:x},"
            for codepoint, mapped in sorted(outliers.items())
            if not 0x13A0 <= codepoint <= 0x13EF
        )
        return "\n            ".join(arms)

    rendered = rendered.replace(
        "__LOWER16_OUTLIER_ARMS__", outlier_arms(lower_outliers)
    )
    rendered = rendered.replace(
        "__CANONICAL16_OUTLIER_ARMS__", outlier_arms(canonical_outliers)
    )
    if "__GENERATED_" in rendered or "__CANONICAL_" in rendered:
        raise AssertionError("unresolved generated Rust source token")
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(rendered, encoding="utf-8")
    production_info: dict[str, object] | None = None
    if production_path is not None:
        production = production_source(
            property_index=property_index,
            property_pages=property_pages,
            lower_index=lower128_index,
            lower_pages=lower128_pages,
            upper_index=upper128_index,
            upper_pages=upper128_pages,
            canonical_index=canonical128_index,
            canonical_pages=canonical128_pages,
            multi_upper=multi_upper,
            digests=source_hashes,
        )
        production_path.parent.mkdir(parents=True, exist_ok=True)
        production_path.write_text(production, encoding="utf-8")
        production_info = {
            "path": str(production_path),
            "source_sha256": hashlib.sha256(production.encode("utf-8")).hexdigest(),
            "source_bytes": len(production.encode("utf-8")),
            "property_bytes": len(property_index) + len(property_pages),
            "property_prefix_bytes": 16_384,
            "simple_lower_bytes": len(lower128_index) + len(lower128_pages) * 4,
            "simple_lower_prefix_bytes": 4_096 * 4,
            "simple_upper_bytes": len(upper128_index) + len(upper128_pages) * 4,
            "literal_fold_bytes": len(canonical128_index) + len(canonical128_pages) * 4,
            "literal_fold_prefix_bytes": 4_096 * 4,
            "multi_upper_codepoints": len(multi_upper),
            "multi_upper_ranges": len(contiguous_ranges(multi_upper)),
        }
    return {
        "unicode": unicodedata.unidata_version,
        "source": str(source_path),
        "source_sha256": hashlib.sha256(rendered.encode()).hexdigest(),
        "property_names": [
            "word",
            "decimal",
            "digit",
            "numeric",
            "alpha",
            "whitespace",
            "xid_start",
            "xid_continue",
        ],
        "property_counts": property_counts,
        "property_unique_pages": len(property_pages) // PAGE_SIZE,
        "property_index_bytes": len(property_index) * 2,
        "property_data_bytes": len(property_pages),
        "property_total_bytes": len(property_index) * 2 + len(property_pages),
        "property_u8_index_bytes": len(property_index),
        "property_u8_total_bytes": len(property_index) + len(property_pages),
        "property_prefix_4k_added_bytes": 4_096,
        "property_prefix_16k_added_bytes": 16_384,
        "property_prefix_bmp_added_bytes": 65_536,
        "lower_unique_pages": len(lower_pages) // PAGE_SIZE,
        "lower_total_bytes": len(lower_index) * 2 + len(lower_pages) * 4,
        "canonical_unique_pages": len(canonical_pages) // PAGE_SIZE,
        "canonical_total_bytes": len(canonical_index) * 2
        + len(canonical_pages) * 4,
        "lower_u8_i32_total_bytes": len(lower_index) + len(lower_pages) * 4,
        "canonical_u8_i32_total_bytes": len(canonical_index)
        + len(canonical_pages) * 4,
        "lower128_unique_pages": len(lower128_pages) // 128,
        "lower128_u8_i32_total_bytes": len(lower128_index)
        + len(lower128_pages) * 4,
        "lower_prefix_4k_added_bytes": 4_096 * 4,
        "canonical128_unique_pages": len(canonical128_pages) // 128,
        "canonical128_u8_i32_total_bytes": len(canonical128_index)
        + len(canonical128_pages) * 4,
        "canonical_prefix_4k_added_bytes": 4_096 * 4,
        "lower_i16_unique_pages": len(lower16_pages) // PAGE_SIZE,
        "lower_u8_i16_total_bytes": len(lower16_index) + len(lower16_pages) * 2,
        "lower_i16_outlier_count": len(lower_outliers),
        "canonical_i16_unique_pages": len(canonical16_pages) // PAGE_SIZE,
        "canonical_u8_i16_total_bytes": len(canonical16_index)
        + len(canonical16_pages) * 2,
        "canonical_i16_outlier_count": len(canonical_outliers),
        "casefix_keys": len(canonical),
        "casefix_components": len(grouped),
        "source_hashes": source_hashes,
        "upper128_unique_pages": len(upper128_pages) // FOLD_PAGE_SIZE,
        "upper128_u8_i32_total_bytes": len(upper128_index) + len(upper128_pages) * 4,
        "multi_upper_codepoints": len(multi_upper),
        "multi_upper_ranges": len(contiguous_ranges(multi_upper)),
        "production": production_info,
    }


def build(
    source: pathlib.Path,
    destination: pathlib.Path,
    tables: bool,
    u8index: bool = False,
    i16: bool = False,
    fold128: bool = False,
    latin1: bool = False,
    property_prefix: int = 0,
    foldprefix4k: bool = False,
) -> None:
    command = [
        "rustc",
        "--edition=2024",
        "--crate-type=cdylib",
        "-C",
        "opt-level=3",
        "-C",
        "lto=fat",
        "-C",
        "codegen-units=1",
        "-C",
        "panic=abort",
    ]
    if tables:
        command.extend(("--cfg", "rebar_unicode_tables"))
    if u8index:
        command.extend(("--cfg", "rebar_unicode_u8index"))
    if i16:
        command.extend(("--cfg", "rebar_unicode_i16"))
    if fold128:
        command.extend(("--cfg", "rebar_unicode_fold128"))
    if latin1:
        command.extend(("--cfg", "rebar_unicode_latin1"))
    if property_prefix == 4_096:
        command.extend(("--cfg", "rebar_unicode_property4k"))
    elif property_prefix == 16_384:
        command.extend(("--cfg", "rebar_unicode_property16k"))
    elif property_prefix == 65_536:
        command.extend(("--cfg", "rebar_unicode_propertybmp"))
    elif property_prefix:
        raise ValueError(f"unsupported Unicode property prefix {property_prefix}")
    if foldprefix4k:
        command.extend(("--cfg", "rebar_unicode_foldprefix4k"))
    command.extend((str(source), "-o", str(destination)))
    subprocess.run(command, check=True, capture_output=True, text=True)


def load_function(library_path: pathlib.Path, symbol: str):
    library = ctypes.CDLL(str(library_path))
    function = getattr(library, symbol)
    function.argtypes = (
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.c_uint32,
    )
    function.restype = ctypes.c_uint64
    return library, function


def bootstrap_interval(ratios: list[float], seed: int) -> tuple[float, float, float]:
    logarithms = [math.log(value) for value in ratios]
    center = math.exp(statistics.fmean(logarithms))
    randomizer = random.Random(seed)
    draws = []
    for _ in range(BOOTSTRAPS):
        draws.append(
            math.exp(
                statistics.fmean(
                    logarithms[randomizer.randrange(len(logarithms))]
                    for _ in logarithms
                )
            )
        )
    draws.sort()
    return center, draws[int(BOOTSTRAPS * 0.025)], draws[int(BOOTSTRAPS * 0.975)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=pathlib.Path,
        default=pathlib.Path("/tmp/rebar-rust-unicode-project-lab-v1.rs"),
    )
    parser.add_argument(
        "--direct-library",
        type=pathlib.Path,
        default=pathlib.Path("/tmp/rebar-rust-unicode-project-lab-direct-v1.so"),
    )
    parser.add_argument(
        "--table-library",
        type=pathlib.Path,
        default=pathlib.Path("/tmp/rebar-rust-unicode-project-lab-u16-i32-v1.so"),
    )
    parser.add_argument(
        "--u8-library",
        type=pathlib.Path,
        default=pathlib.Path("/tmp/rebar-rust-unicode-project-lab-u8-i32-v1.so"),
    )
    parser.add_argument(
        "--i16-library",
        type=pathlib.Path,
        default=pathlib.Path("/tmp/rebar-rust-unicode-project-lab-u8-i16-v1.so"),
    )
    parser.add_argument(
        "--fold128-library",
        type=pathlib.Path,
        default=pathlib.Path("/tmp/rebar-rust-unicode-project-lab-fold128-v1.so"),
    )
    parser.add_argument(
        "--latin1-library",
        type=pathlib.Path,
        default=pathlib.Path("/tmp/rebar-rust-unicode-project-lab-latin1-v1.so"),
    )
    parser.add_argument(
        "--combined-library",
        type=pathlib.Path,
        default=pathlib.Path("/tmp/rebar-rust-unicode-project-lab-combined-v1.so"),
    )
    parser.add_argument(
        "--property4k-library",
        type=pathlib.Path,
        default=pathlib.Path("/tmp/rebar-rust-unicode-project-lab-property4k-v1.so"),
    )
    parser.add_argument(
        "--property16k-library",
        type=pathlib.Path,
        default=pathlib.Path("/tmp/rebar-rust-unicode-project-lab-property16k-v1.so"),
    )
    parser.add_argument(
        "--propertybmp-library",
        type=pathlib.Path,
        default=pathlib.Path("/tmp/rebar-rust-unicode-project-lab-propertybmp-v1.so"),
    )
    parser.add_argument(
        "--foldprefix-library",
        type=pathlib.Path,
        default=pathlib.Path("/tmp/rebar-rust-unicode-project-lab-foldprefix-v1.so"),
    )
    parser.add_argument(
        "--prefixcombined-library",
        type=pathlib.Path,
        default=pathlib.Path("/tmp/rebar-rust-unicode-project-lab-prefix4k-fold4k-v1.so"),
    )
    parser.add_argument(
        "--prefix16combined-library",
        type=pathlib.Path,
        default=pathlib.Path("/tmp/rebar-rust-unicode-project-lab-prefix16k-fold4k-v1.so"),
    )
    parser.add_argument(
        "--prefixbmpcombined-library",
        type=pathlib.Path,
        default=pathlib.Path("/tmp/rebar-rust-unicode-project-lab-prefixbmp-fold4k-v1.so"),
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=(
            pathlib.Path(__file__).resolve().parents[1]
            / "candidates"
            / "evidence"
            / "rust-v6-unicode-table-lab.json.gz"
        ),
    )
    parser.add_argument(
        "--workspace",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--emit-production-module",
        type=pathlib.Path,
        default=None,
        help="write the deterministic, exact pinned-Unicode production module",
    )
    parser.add_argument(
        "--generate-only",
        action="store_true",
        help="generate and validate Unicode tables without running timing trials",
    )
    args = parser.parse_args()
    started = time.monotonic()
    frozen_fixture = validate_frozen_fixture(args.workspace)
    table_info = generate(args.source, args.emit_production_module)
    if args.generate_only:
        print(
            json.dumps(
                {
                    "schema": "rebar-rust-unicode-table-generation-v1",
                    "python": sys.version.split()[0],
                    "unicode": unicodedata.unidata_version,
                    "frozen_fixture": frozen_fixture,
                    "tables": table_info,
                },
                sort_keys=True,
            )
        )
        return 0
    build(args.source, args.direct_library, False)
    build(args.source, args.table_library, True)
    build(args.source, args.u8_library, True, u8index=True)
    build(args.source, args.i16_library, True, u8index=True, i16=True)
    build(args.source, args.fold128_library, True, u8index=True, fold128=True)
    build(args.source, args.latin1_library, True, u8index=True, latin1=True)
    build(
        args.source,
        args.combined_library,
        True,
        u8index=True,
        fold128=True,
        latin1=True,
    )
    build(
        args.source,
        args.property4k_library,
        True,
        u8index=True,
        fold128=True,
        latin1=True,
        property_prefix=4_096,
    )
    build(
        args.source,
        args.property16k_library,
        True,
        u8index=True,
        fold128=True,
        latin1=True,
        property_prefix=16_384,
    )
    build(
        args.source,
        args.propertybmp_library,
        True,
        u8index=True,
        fold128=True,
        latin1=True,
        property_prefix=65_536,
    )
    build(
        args.source,
        args.foldprefix_library,
        True,
        u8index=True,
        fold128=True,
        latin1=True,
        foldprefix4k=True,
    )
    build(
        args.source,
        args.prefixcombined_library,
        True,
        u8index=True,
        fold128=True,
        latin1=True,
        property_prefix=4_096,
        foldprefix4k=True,
    )
    build(
        args.source,
        args.prefix16combined_library,
        True,
        u8index=True,
        fold128=True,
        latin1=True,
        property_prefix=16_384,
        foldprefix4k=True,
    )
    build(
        args.source,
        args.prefixbmpcombined_library,
        True,
        u8index=True,
        fold128=True,
        latin1=True,
        property_prefix=65_536,
        foldprefix4k=True,
    )
    direct_library, direct = load_function(
        args.direct_library, "rebar_unicode_bench_direct"
    )
    table_library, table = load_function(
        args.table_library, "rebar_unicode_bench_table"
    )
    u8_library, u8_table = load_function(
        args.u8_library, "rebar_unicode_bench_table"
    )
    i16_library, i16_table = load_function(
        args.i16_library, "rebar_unicode_bench_table"
    )
    fold128_library, fold128_table = load_function(
        args.fold128_library, "rebar_unicode_bench_table"
    )
    latin1_library, latin1_table = load_function(
        args.latin1_library, "rebar_unicode_bench_table"
    )
    combined_library, combined_table = load_function(
        args.combined_library, "rebar_unicode_bench_table"
    )
    property4k_library, property4k_table = load_function(
        args.property4k_library, "rebar_unicode_bench_table"
    )
    property16k_library, property16k_table = load_function(
        args.property16k_library, "rebar_unicode_bench_table"
    )
    propertybmp_library, propertybmp_table = load_function(
        args.propertybmp_library, "rebar_unicode_bench_table"
    )
    foldprefix_library, foldprefix_table = load_function(
        args.foldprefix_library, "rebar_unicode_bench_table"
    )
    prefixcombined_library, prefixcombined_table = load_function(
        args.prefixcombined_library, "rebar_unicode_bench_table"
    )
    prefix16combined_library, prefix16combined_table = load_function(
        args.prefix16combined_library, "rebar_unicode_bench_table"
    )
    prefixbmpcombined_library, prefixbmpcombined_table = load_function(
        args.prefixbmpcombined_library, "rebar_unicode_bench_table"
    )
    _keep_libraries_alive = (
        direct_library,
        table_library,
        u8_library,
        i16_library,
        fold128_library,
        latin1_library,
        combined_library,
        property4k_library,
        property16k_library,
        propertybmp_library,
        foldprefix_library,
        prefixcombined_library,
        prefix16combined_library,
        prefixbmpcombined_library,
    )
    functions = {
        "direct": direct,
        "u16-index-i32-delta": table,
        "u8-index-i32-delta": u8_table,
        "u8-index-i16-delta": i16_table,
        "u8-index-i32-delta-fold128": fold128_table,
        "u8-index-i32-delta-latin1": latin1_table,
        "u8-index-i32-delta-fold128-latin1": combined_table,
        "mixed-prefix-property4k": property4k_table,
        "mixed-prefix-property16k": property16k_table,
        "mixed-prefix-propertybmp": propertybmp_table,
        "mixed-prefix-fold4k": foldprefix_table,
        "mixed-prefix-property4k-fold4k": prefixcombined_table,
        "mixed-prefix-property16k-fold4k": prefix16combined_table,
        "mixed-prefix-propertybmp-fold4k": prefixbmpcombined_table,
    }
    variant_names = tuple(name for name in functions if name != "direct")

    plane = array.array("I", range(POINTS))
    plane_data = (ctypes.c_uint32 * len(plane)).from_buffer(plane)
    full_plane = []
    for mode, workload in enumerate(WORKLOADS):
        first = direct(plane_data, len(plane), 1, mode)
        for variant in variant_names:
            second = functions[variant](plane_data, len(plane), 1, mode)
            if first != second:
                raise AssertionError(
                    f"full-plane {workload}/{variant} mismatch: "
                    f"{first:#x} != {second:#x}"
                )
            full_plane.append(
                {
                    "workload": workload,
                    "variant": variant,
                    "codepoints": len(plane),
                    "checksum": f"{first:016x}",
                    "passed": True,
                }
            )

    sys.path.insert(0, str(args.workspace))
    from performance.v6.suite import generated_case

    randomizer = random.Random(ORDER_SEED)
    raw_rows = []
    result_rows = []
    all_ratios = {name: [] for name in variant_names}
    for family, variant in SUBJECTS:
        fixture = generated_case("holdout", family, variant)
        if not isinstance(fixture["string"], str):
            raise AssertionError("expected frozen Unicode text holdout subject")
        values = array.array("I", map(ord, fixture["string"]))
        pointer = (ctypes.c_uint32 * len(values)).from_buffer(values)
        repetitions = max(1, math.ceil(TARGET_CHARACTERS / len(values)))
        for mode, workload in enumerate(WORKLOADS):
            expected = direct(pointer, len(values), repetitions, mode)
            for name in variant_names:
                if functions[name](pointer, len(values), repetitions, mode) != expected:
                    raise AssertionError(
                        f"holdout checksum mismatch: {fixture['id']} {workload} {name}"
                    )
            for warmup in range(WARMUPS):
                warmup_order = list(functions.items())
                if warmup % 2:
                    warmup_order.reverse()
                for _name, function in warmup_order:
                    if function(pointer, len(values), repetitions, mode) != expected:
                        raise AssertionError("Unicode warmup checksum mismatch")
            ratios = {name: [] for name in variant_names}
            elapsed_rows = {name: [] for name in functions}
            for trial in range(TRIALS):
                sequence = list(functions.items())
                randomizer.shuffle(sequence)
                times = {}
                for position, (name, function) in enumerate(sequence):
                    begun = time.perf_counter_ns()
                    checksum = function(pointer, len(values), repetitions, mode)
                    elapsed = time.perf_counter_ns() - begun
                    if checksum != expected:
                        raise AssertionError("timed Unicode checksum mismatch")
                    times[name] = elapsed
                    elapsed_rows[name].append(elapsed)
                    raw_rows.append(
                        {
                            "id": fixture["id"],
                            "family": family,
                            "workload": workload,
                            "trial": trial,
                            "position": position,
                            "implementation": name,
                            "characters": len(values),
                            "repetitions": repetitions,
                            "processed_characters": len(values) * repetitions,
                            "nanoseconds": elapsed,
                            "checksum": f"{checksum:016x}",
                        }
                    )
                for name in variant_names:
                    ratios[name].append(times["direct"] / times[name])
            for name in variant_names:
                center, low, high = bootstrap_interval(
                    ratios[name], BOOTSTRAP_SEED + len(result_rows) * 1009
                )
                all_ratios[name].extend(ratios[name])
                result_rows.append(
                    {
                        "id": fixture["id"],
                        "family": family,
                        "workload": workload,
                        "implementation": name,
                        "characters": len(values),
                        "non_ascii": sum(item >= 128 for item in values),
                        "repetitions": repetitions,
                        "paired_trials": TRIALS,
                        "speedup_geomean": center,
                        "confidence_low": low,
                        "confidence_high": high,
                        "direct_median_ns": int(statistics.median(elapsed_rows["direct"])),
                        "variant_median_ns": int(statistics.median(elapsed_rows[name])),
                        "checksum": f"{expected:016x}",
                    }
                )

    overall_rows = []
    for number, name in enumerate(variant_names):
        center, low, high = bootstrap_interval(
            all_ratios[name], BOOTSTRAP_SEED + 65537 + number * 1009
        )
        overall_rows.append(
            {
                "implementation": name,
                "speedup_geomean": center,
                "confidence_low": low,
                "confidence_high": high,
                "paired_samples": len(all_ratios[name]),
            }
        )
    per_workload = []
    for workload in WORKLOADS:
        for name in variant_names:
            values = [
                row["speedup_geomean"]
                for row in result_rows
                if row["workload"] == workload and row["implementation"] == name
            ]
            per_workload.append(
                {
                    "workload": workload,
                    "implementation": name,
                    "subjects": len(values),
                    "geomean": math.exp(statistics.fmean(map(math.log, values))),
                    "faster_subjects": sum(value > 1 for value in values),
                }
            )
    library_paths = {
        "direct": args.direct_library,
        "u16-index-i32-delta": args.table_library,
        "u8-index-i32-delta": args.u8_library,
        "u8-index-i16-delta": args.i16_library,
        "u8-index-i32-delta-fold128": args.fold128_library,
        "u8-index-i32-delta-latin1": args.latin1_library,
        "u8-index-i32-delta-fold128-latin1": args.combined_library,
        "mixed-prefix-property4k": args.property4k_library,
        "mixed-prefix-property16k": args.property16k_library,
        "mixed-prefix-propertybmp": args.propertybmp_library,
        "mixed-prefix-fold4k": args.foldprefix_library,
        "mixed-prefix-property4k-fold4k": args.prefixcombined_library,
        "mixed-prefix-property16k-fold4k": args.prefix16combined_library,
        "mixed-prefix-propertybmp-fold4k": args.prefixbmpcombined_library,
    }
    if tuple(library_paths) != tuple(functions):
        raise AssertionError("Unicode variants and measured libraries differ")
    direct_bytes = args.direct_library.stat().st_size
    binaries = {
        name: {
            "path": str(path),
            "bytes": path.stat().st_size,
            **({} if name == "direct" else {
                "added_bytes": path.stat().st_size - direct_bytes
            }),
        }
        for name, path in library_paths.items()
    }
    output = {
        "schema": "rebar-rust-unicode-table-lab-v1",
        "python": sys.version.split()[0],
        "unicode": unicodedata.unidata_version,
        "fixture": "performance/v6/suite.py frozen holdout generated_case",
        "holdout_subjects": len(SUBJECTS),
        "implementations": list(functions),
        "workloads": list(WORKLOADS),
        "paired_trials": TRIALS,
        "warmups": WARMUPS,
        "bootstrap_draws": BOOTSTRAPS,
        "order_seed": ORDER_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "frozen_fixture": frozen_fixture,
        "generator_sha256": hashlib.sha256(
            pathlib.Path(__file__).read_bytes()
        ).hexdigest(),
        "minimum_characters_per_sample": TARGET_CHARACTERS,
        "tables": table_info,
        "full_plane_correctness": full_plane,
        "full_plane_comparisons": POINTS * len(WORKLOADS) * len(variant_names),
        "binary": binaries,
        "maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "overall": overall_rows,
        "by_workload": per_workload,
        "results": result_rows,
        "raw": raw_rows,
        "failures": [],
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }
    production_path = (
        args.workspace / "candidates" / "rust" / "src" / "unicode_tables.rs"
    )
    if production_path.is_file():
        production = production_path.read_bytes()
        output["production_module"] = {
            "path": "candidates/rust/src/unicode_tables.rs",
            "sha256": hashlib.sha256(production).hexdigest(),
            "bytes": len(production),
        }
    payload = (
        json.dumps(output, ensure_ascii=True, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.suffix == ".gz":
        with args.output.open("wb") as destination:
            with gzip.GzipFile(
                filename="", mode="wb", fileobj=destination, mtime=0
            ) as compressed:
                compressed.write(payload)
    else:
        args.output.write_bytes(payload)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "holdout_subjects": len(SUBJECTS),
                "workloads": len(WORKLOADS),
                "paired_trials": TRIALS,
                "raw_rows": len(raw_rows),
                "full_plane_comparisons": output["full_plane_comparisons"],
                "full_plane_failures": 0,
                "implementations": list(functions),
                "overall": overall_rows,
                "by_workload": per_workload,
                "property_u16_table_bytes": table_info["property_total_bytes"],
                "property_u8_table_bytes": table_info["property_u8_total_bytes"],
                "simple_u16_i32_table_bytes": table_info["lower_total_bytes"],
                "simple_u8_i32_table_bytes": table_info["lower_u8_i32_total_bytes"],
                "simple_u8_i32_fold128_table_bytes": table_info[
                    "lower128_u8_i32_total_bytes"
                ],
                "simple_u8_i16_table_bytes": table_info["lower_u8_i16_total_bytes"],
                "canonical_u16_i32_table_bytes": table_info["canonical_total_bytes"],
                "canonical_u8_i32_table_bytes": table_info["canonical_u8_i32_total_bytes"],
                "canonical_u8_i32_fold128_table_bytes": table_info[
                    "canonical128_u8_i32_total_bytes"
                ],
                "canonical_u8_i16_table_bytes": table_info[
                    "canonical_u8_i16_total_bytes"
                ],
                "binary": binaries,
                "elapsed_seconds": output["elapsed_seconds"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
