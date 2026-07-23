#!/usr/bin/env python3
"""Prove that the generated Rust tables exactly reproduce pinned Python data.

The production module is compiled into an isolated, temporary Rust executable.
Its full-plane binary stream is compared with CPython 3.14.6 scalar character
data without importing a regular-expression implementation or external package.
"""

from __future__ import annotations

import argparse
import collections
import ctypes
import hashlib
import json
import pathlib
import struct
import subprocess
import sys
import tempfile
import unicodedata


CODEPOINTS = 0x11_0000
SOURCE_SHA256 = (
    "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af"
)
SUITE_SHA256 = (
    "091d7be04f7251781e2b8568f6cb19acbe603cb1d945926a69ba32adaf9b6b0f"
)
EXPECTED_SHA256 = (
    "c8e32e879cc7a134748f8f3f29fed49678895745fdecebe63ceec46b6a3b5335"
)
MANIFEST_SHA256 = (
    "06c3b09a203d036e3129d90b6c412e716a3835e4c4e2827df73c189dec4956f1"
)
FIELDS = (
    "decimal",
    "whitespace",
    "word",
    "digit",
    "numeric",
    "alpha",
    "xid_start",
    "xid_continue",
    "simple_lower",
    "simple_upper",
    "literal_fold",
    "multi_upper",
)
FORBIDDEN_PRODUCTION_MARKERS = (
    "import re",
    "from re",
    "_sre",
    "regex::",
    "use regex",
    "pcre",
    "oniguruma",
    "hyperscan",
    'extern "C"',
    "PyObject",
    "_PyUnicode",
)


RUST_SOURCE = r'''
use std::env;
use std::io::{self, BufWriter, Write};

#[path = "__REBAR_UNICODE_MODULE__"]
mod unicode_tables;

const ALL_PROPERTY_BITS: u8 = unicode_tables::CATEGORY_DECIMAL
    | unicode_tables::CATEGORY_WHITESPACE
    | unicode_tables::CATEGORY_WORD
    | unicode_tables::CATEGORY_DIGIT
    | unicode_tables::CATEGORY_NUMERIC
    | unicode_tables::CATEGORY_ALPHA
    | unicode_tables::CATEGORY_XID_START
    | unicode_tables::CATEGORY_XID_CONTINUE;

fn stream() -> io::Result<()> {
    let stdout = io::stdout();
    let mut output = BufWriter::with_capacity(256 * 1024, stdout.lock());
    for value in 0..=0x10_ffff_u32 {
        let mask = unicode_tables::category_mask(value);
        if mask & !ALL_PROPERTY_BITS != 0
            || unicode_tables::xid_start(value)
                != (mask & unicode_tables::CATEGORY_XID_START != 0)
            || unicode_tables::xid_continue(value)
                != (mask & unicode_tables::CATEGORY_XID_CONTINUE != 0)
        {
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                format!("inconsistent Unicode identifier at U+{value:04X}"),
            ));
        }
        output.write_all(&[mask])?;
        output.write_all(&unicode_tables::simple_lower(value).to_le_bytes())?;
        output.write_all(&unicode_tables::simple_upper(value).to_le_bytes())?;
        output.write_all(&unicode_tables::literal_fold(value).to_le_bytes())?;
        output.write_all(&[u8::from(unicode_tables::multi_upper(value))])?;
    }
    output.flush()
}

fn out_of_range() -> io::Result<()> {
    for value in [0x11_0000_u32, 0x20_0000, u32::MAX] {
        let mask = unicode_tables::category_mask(value);
        let lower = unicode_tables::simple_lower(value);
        let upper = unicode_tables::simple_upper(value);
        let literal = unicode_tables::literal_fold(value);
        let start = unicode_tables::xid_start(value);
        let continuation = unicode_tables::xid_continue(value);
        let multi = unicode_tables::multi_upper(value);
        println!(
            "{value} {mask} {lower} {upper} {literal} {} {} {}",
            u8::from(start),
            u8::from(continuation),
            u8::from(multi),
        );
        if mask != 0
            || lower != value
            || upper != value
            || literal != value
            || start
            || continuation
            || multi
        {
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                format!("invalid out-of-range behavior at U+{value:08X}"),
            ));
        }
    }
    Ok(())
}

fn main() -> io::Result<()> {
    match env::args().nth(1).as_deref() {
        Some("--full-plane") => stream(),
        Some("--out-of-range") => out_of_range(),
        _ => Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "expected --full-plane or --out-of-range",
        )),
    }
}
'''


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frozen_fixture(workspace: pathlib.Path) -> dict[str, object]:
    manifest_path = workspace / "performance" / "v6" / "manifest.json"
    suite_path = workspace / "performance" / "v6" / "suite.py"
    expected_path = workspace / "performance" / "v6" / "expected.jsonl"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    observed = {
        "suite_sha256": sha256(suite_path),
        "expected_sha256": sha256(expected_path),
        "manifest_sha256": sha256(manifest_path),
        "order_seed": manifest.get("order_seed"),
        "bootstrap_seed": manifest.get("bootstrap_seed"),
    }
    if observed != {
        "suite_sha256": SUITE_SHA256,
        "expected_sha256": EXPECTED_SHA256,
        "manifest_sha256": MANIFEST_SHA256,
        "order_seed": 1985072201,
        "bootstrap_seed": 1985072202,
    }:
        raise RuntimeError(f"the frozen v6 performance fixture changed: {observed}")
    if manifest.get("python") != "3.14.6":
        raise RuntimeError("the frozen reference is not CPython 3.14.6")
    return observed


def source_headers(source: bytes) -> dict[str, str]:
    headers: dict[str, str] = {}
    for line in source.decode("utf-8").splitlines()[:12]:
        if not line.startswith("// "):
            continue
        name, separator, digest = line[3:].partition(" source SHA-256: ")
        if not separator:
            continue
        if len(digest) != 64 or any(value not in "0123456789abcdef" for value in digest):
            raise RuntimeError(f"invalid pinned Unicode source digest: {line}")
        headers[name.lower().replace(" ", "_").replace("-", "_")] = digest
    if set(headers) != {"property", "simple_lower", "simple_upper", "literal_fold"}:
        raise RuntimeError(f"missing pinned Unicode source headers: {headers}")
    return headers


def scalar_helpers() -> tuple[object, object]:
    lower = ctypes.pythonapi._PyUnicode_ToLowercase
    upper = ctypes.pythonapi._PyUnicode_ToUppercase
    lower.argtypes = upper.argtypes = (ctypes.c_uint32,)
    lower.restype = upper.restype = ctypes.c_uint32
    return lower, upper


def literal_representatives(lower: object, upper: object) -> dict[int, int]:
    cased_lowers: set[int] = set()
    for value in range(CODEPOINTS):
        lowered = lower(value)
        if lowered != value or upper(value) != value:
            cased_lowers.add(lowered)
    groups: dict[str, list[int]] = collections.defaultdict(list)
    for value in cased_lowers:
        groups[chr(value).upper()].append(value)
    representatives: dict[int, int] = {}
    for members in groups.values():
        if len(members) < 2:
            continue
        representative = (
            0xA64B if 0x1C88 in members and 0xA64B in members else min(members)
        )
        representatives.update({member: representative for member in members})
    if len(representatives) != 50 or len(set(representatives.values())) != 24:
        raise RuntimeError("the pinned 24 Python case-equivalence groups changed")
    return representatives


def build_verifier(source: pathlib.Path, directory: pathlib.Path) -> pathlib.Path:
    escaped = str(source).replace("\\", "\\\\").replace('"', '\\"')
    rendered = RUST_SOURCE.replace("__REBAR_UNICODE_MODULE__", escaped)
    harness = directory / "rebar_unicode_production_verify.rs"
    binary = directory / "rebar_unicode_production_verify"
    harness.write_text(rendered, encoding="utf-8")
    result = subprocess.run(
        [
            "rustc",
            "--edition=2024",
            "-D",
            "warnings",
            "-C",
            "opt-level=3",
            str(harness),
            "-o",
            str(binary),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            "isolated production Unicode verifier failed strict compilation: "
            f"{result.stderr}"
        )
    return binary


def check_out_of_range(binary: pathlib.Path) -> list[dict[str, object]]:
    result = subprocess.run(
        [str(binary), "--out-of-range"],
        check=True,
        text=True,
        capture_output=True,
    )
    rows = []
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) != 8:
            raise RuntimeError(f"malformed out-of-range verifier result: {line}")
        value, mask, lower, upper, literal, start, continuation, multi = map(
            int, fields
        )
        if (mask, lower, upper, literal, start, continuation, multi) != (
            0,
            value,
            value,
            value,
            0,
            0,
            0,
        ):
            raise RuntimeError(f"incorrect out-of-range behavior: {line}")
        rows.append(
            {
                "value": value,
                "mask": mask,
                "simple_lower": lower,
                "simple_upper": upper,
                "literal_fold": literal,
                "xid_start": bool(start),
                "xid_continue": bool(continuation),
                "multi_upper": bool(multi),
            }
        )
    if [row["value"] for row in rows] != [0x11_0000, 0x20_0000, 0xFFFF_FFFF]:
        raise RuntimeError("incomplete out-of-range production verification")
    return rows


def verify_stream(
    binary: pathlib.Path,
    lower: object,
    upper: object,
    representatives: dict[int, int],
) -> dict[str, object]:
    hashes = {
        "property": hashlib.sha256(),
        "simple_lower": hashlib.sha256(),
        "simple_upper": hashlib.sha256(),
        "literal_fold": hashlib.sha256(),
    }
    runtime_properties = hashlib.sha256()
    counts = {field: 0 for field in FIELDS}
    examples: dict[str, list[dict[str, object]]] = {
        field: [] for field in FIELDS
    }
    property_counts = {field: 0 for field in FIELDS[:8]}
    multi_count = 0
    surrogate_count = 0
    process = subprocess.Popen(
        [str(binary), "--full-plane"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.stdout is None or process.stderr is None:
        raise RuntimeError("cannot read the isolated production Unicode stream")
    position = 0
    carry = b""
    while True:
        chunk = process.stdout.read(14 * 8192)
        if not chunk:
            break
        data = carry + chunk
        complete = len(data) - len(data) % 14
        carry = data[complete:]
        for mask, actual_lower, actual_upper, actual_fold, actual_multi in (
            struct.iter_unpack("<BIIIB", memoryview(data)[:complete])
        ):
            if position >= CODEPOINTS:
                raise RuntimeError("the production module returned an extra scalar")
            character = chr(position)
            expected_properties = (
                character.isdecimal(),
                character.isspace(),
                character == "_" or character.isalnum(),
                character.isdigit(),
                character.isnumeric(),
                character.isalpha(),
                character.isidentifier(),
                ("a" + character).isidentifier(),
            )
            production_mask = sum(
                int(value) << bit
                for bit, value in enumerate(expected_properties)
            )
            original_order = (
                expected_properties[2],
                expected_properties[0],
                expected_properties[3],
                expected_properties[4],
                expected_properties[5],
                expected_properties[1],
                expected_properties[6],
                expected_properties[7],
            )
            original_mask = sum(
                int(value) << bit for bit, value in enumerate(original_order)
            )
            hashes["property"].update(bytes((original_mask,)))
            runtime_properties.update(bytes((production_mask,)))

            for bit, expected in enumerate(expected_properties):
                actual = bool(mask & (1 << bit))
                property_counts[FIELDS[bit]] += int(actual)
                if actual != expected:
                    field = FIELDS[bit]
                    counts[field] += 1
                    if len(examples[field]) < 12:
                        examples[field].append(
                            {
                                "codepoint": position,
                                "actual": actual,
                                "expected": expected,
                            }
                        )

            expected_lower = lower(position)
            expected_upper = upper(position)
            expected_fold = representatives.get(expected_lower, expected_lower)
            expected_multi = len(character.upper()) > 1
            hashes["simple_lower"].update(struct.pack("<I", expected_lower))
            hashes["simple_upper"].update(struct.pack("<I", expected_upper))
            hashes["literal_fold"].update(struct.pack("<I", expected_fold))
            multi_count += int(expected_multi)
            surrogate_count += int(0xD800 <= position <= 0xDFFF)
            for field, actual, expected in (
                ("simple_lower", actual_lower, expected_lower),
                ("simple_upper", actual_upper, expected_upper),
                ("literal_fold", actual_fold, expected_fold),
                ("multi_upper", bool(actual_multi), expected_multi),
            ):
                if actual != expected:
                    counts[field] += 1
                    if len(examples[field]) < 12:
                        examples[field].append(
                            {
                                "codepoint": position,
                                "actual": actual,
                                "expected": expected,
                            }
                        )
            position += 1

    stderr = process.stderr.read().decode("utf-8", errors="replace")
    return_code = process.wait()
    if position != CODEPOINTS or carry or return_code:
        raise RuntimeError(
            "invalid production Unicode stream: "
            f"codepoints={position}, remainder={len(carry)}, "
            f"returncode={return_code}, stderr={stderr!r}"
        )
    if multi_count != 102 or surrogate_count != 2048:
        raise RuntimeError("pinned uppercase expansion or surrogate counts changed")
    return {
        "codepoints": position,
        "comparisons_per_codepoint": len(FIELDS),
        "full_plane_comparisons": position * len(FIELDS),
        "category_counts": property_counts,
        "case_equivalence_groups": len(set(representatives.values())),
        "case_equivalence_keys": len(representatives),
        "multi_upper_count": multi_count,
        "unpaired_surrogates": surrogate_count,
        "source_data_hashes": {
            field: digest.hexdigest() for field, digest in hashes.items()
        },
        "production_property_data_sha256": runtime_properties.hexdigest(),
        "mismatch_counts": counts,
        "mismatch_examples": {
            field: values for field, values in examples.items() if values
        },
        "total_mismatches": sum(counts.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    workspace = pathlib.Path(__file__).resolve().parents[1]
    parser.add_argument(
        "--source",
        type=pathlib.Path,
        default=workspace / "candidates" / "rust" / "src" / "unicode_tables.rs",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=(
            workspace
            / "candidates"
            / "evidence"
            / "rust-v6-unicode-production-fullplane.json"
        ),
    )
    args = parser.parse_args()
    if sys.version_info[:3] != (3, 14, 6):
        raise RuntimeError("production verification requires pinned CPython 3.14.6")
    if unicodedata.unidata_version != "16.0.0":
        raise RuntimeError("production verification requires pinned Unicode 16.0.0")
    fixture = frozen_fixture(workspace)
    source_path = args.source.resolve()
    source = source_path.read_bytes()
    source_sha = hashlib.sha256(source).hexdigest()
    if source_sha != SOURCE_SHA256:
        raise RuntimeError(
            "production Unicode module does not match its frozen source: "
            f"expected {SOURCE_SHA256}, observed {source_sha}"
        )
    source_text = source.decode("utf-8")
    forbidden_imports = [
        marker for marker in FORBIDDEN_PRODUCTION_MARKERS if marker in source_text
    ]
    headers = source_headers(source)
    lower, upper = scalar_helpers()
    representatives = literal_representatives(lower, upper)
    with tempfile.TemporaryDirectory(prefix="rebar-unicode-production-") as name:
        binary = build_verifier(source_path, pathlib.Path(name))
        checked = verify_stream(binary, lower, upper, representatives)
        outside = check_out_of_range(binary)

    expected_headers = checked["source_data_hashes"]
    digest_failures = [
        {
            "field": field,
            "header": headers.get(field),
            "calculated": expected,
        }
        for field, expected in expected_headers.items()
        if headers.get(field) != expected
    ]
    try:
        source_name = str(source_path.relative_to(workspace))
    except ValueError:
        source_name = str(source_path)
    report = {
        "schema": "rebar-rust-production-unicode-full-plane-v1",
        "python": sys.version.split()[0],
        "unicode": unicodedata.unidata_version,
        "frozen_fixture": fixture,
        "source": source_name,
        "source_sha256": source_sha,
        "source_sha256_expected": SOURCE_SHA256,
        "source_hash_match": source_sha == SOURCE_SHA256,
        "source_header_hashes": headers,
        "source_digest_failures": digest_failures,
        **checked,
        "out_of_range": outside,
        "out_of_range_failures": 0,
        "forbidden_regex_imports": forbidden_imports,
        "failures": (
            [field for field, count in checked["mismatch_counts"].items() if count]
            + (["source-data-digests"] if digest_failures else [])
            + (["production-regex-delegation"] if forbidden_imports else [])
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "source_sha256": source_sha,
                "codepoints": checked["codepoints"],
                "full_plane_comparisons": checked["full_plane_comparisons"],
                "total_mismatches": checked["total_mismatches"],
                "source_digest_failures": digest_failures,
                "multi_upper_count": checked["multi_upper_count"],
                "surrogates": checked["unpaired_surrogates"],
                "out_of_range_checks": len(outside),
            },
            sort_keys=True,
        )
    )
    return int(bool(report["failures"]))


if __name__ == "__main__":
    raise SystemExit(main())
