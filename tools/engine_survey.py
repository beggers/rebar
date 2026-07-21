#!/usr/bin/env python3
"""Compare installed regex engines on representative Python-re semantics."""

import argparse
import ctypes
import hashlib
import json
import re
import runpy
import subprocess
from array import array
from pathlib import Path

CASES = [
    ("literal", "needle", "prefix needle suffix", 0),
    ("leftmost-branch", "a|ab", "ab", 0),
    ("greedy", "a+", "zaaab", 0),
    ("lazy", "a+?", "zaaab", 0),
    ("capture", "(?P<word>[a-z]+)-(?P<num>[0-9]+)", "x ab-12 y", 0),
    ("numeric-backref", r"([a-z]+)-\1", "x echo-echo y", 0),
    ("lookahead", r"[a-z]+(?=;)", "id;next", 0),
    ("lookbehind", r"(?<=id=)[0-9]+", "id=42;", 0),
    ("lookbehind-ref", r"(a)(?<=\1)b", "ab", 0),
    ("named-backref", r"(?P<x>ab)(?P=x)", "zzabab", 0),
    ("conditional", r"(<)?[a-z]+(?(1)>|!)", "<alpha>", 0),
    ("atomic", r"(?>ab|a)b", "ab", 0),
    ("possessive", r"a*+a", "aaaa", 0),
    ("dollar-newline", r"a$", "a\n", 0),
    ("empty-nonboundary", r"\B", "", 0),
    ("strict-end", r"a\z", "a", 0),
    ("unicode-word", r"\w+", "雪_2!", 0),
    ("unicode-name", r"\N{SNOWMAN}+", "x☃☃y", 0),
    ("ignorecase-kelvin", r"k", "K", re.I),
    ("ignorecase-range", r"[a-z]", "İ", re.I),
    ("ignorecase-dotless", r"[a-z]", "ı", re.I),
    ("ignorecase-cyrillic", r"\u0412", "\u1c80", re.I),
    ("ignorecase-punctuation-range", r"[9-A]", "_", re.I),
    ("octal", r"\141", "a", 0),
    ("octal-backref-ambiguity", r"(a)(b)(c)(d)(e)(f)(g)(h)(i)(j)(k)(l)\119", "abcdefghijklk9", 0),
    ("inline-unicode", r"(?u)\w+", "雪_2!", 0),
    ("scoped-ascii-unicode", r"(?a:\W(?u:\w)\W)", "-雪-", 0),
    ("forward-conditional", r"(?(1)a|b)(a)?", "ba", 0),
    ("open-group-backref-error", r"(\1)", "", 0),
    ("unknown-escape-error", r"\q", "q", 0),
    ("surrogate-literal", "\ud800", "x\ud800y", 0),
    ("class-backspace", r"[\b]", "\b", 0),
]


def byte_span(value, start, end):
    encoded = value.encode("utf-8")
    return [len(encoded[:start].decode("utf-8")), len(encoded[:end].decode("utf-8"))]


def u16_span(value, start, end):
    raw = value.encode("utf-16-le")
    return [len(raw[:start * 2].decode("utf-16-le")), len(raw[:end * 2].decode("utf-16-le"))]


def baseline(pattern, subject, flags):
    try:
        result = re.search(pattern, subject, flags)
    except Exception as error:
        return {"error": f"{type(error).__name__}: {error}"}
    return {"span": list(result.span()) if result else None, "groups": list(result.groups()) if result else None}


class PCRE2:
    def __init__(self, path, width, name, python_octal=False):
        self.name = name
        self.width = width
        self.python_octal = python_octal
        self.lib = ctypes.CDLL(path)
        suffix = f"_{width}"
        self.compile = getattr(self.lib, "pcre2_compile" + suffix)
        self.compile.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
        self.compile.restype = ctypes.c_void_p
        self.context_create = getattr(self.lib, "pcre2_compile_context_create" + suffix)
        self.context_create.argtypes = [ctypes.c_void_p]
        self.context_create.restype = ctypes.c_void_p
        self.context_free = getattr(self.lib, "pcre2_compile_context_free" + suffix)
        self.context_free.argtypes = [ctypes.c_void_p]
        self.extra_options = getattr(self.lib, "pcre2_set_compile_extra_options" + suffix, None)
        if self.extra_options is not None:
            self.extra_options.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
            self.extra_options.restype = ctypes.c_int
        self.data_create = getattr(self.lib, "pcre2_match_data_create_from_pattern" + suffix)
        self.data_create.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.data_create.restype = ctypes.c_void_p
        self.match = getattr(self.lib, "pcre2_match" + suffix)
        self.match.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
        self.match.restype = ctypes.c_int
        self.ovector = getattr(self.lib, "pcre2_get_ovector_pointer" + suffix)
        self.ovector.argtypes = [ctypes.c_void_p]
        self.ovector.restype = ctypes.POINTER(ctypes.c_size_t)
        self.data_free = getattr(self.lib, "pcre2_match_data_free" + suffix)
        self.data_free.argtypes = [ctypes.c_void_p]
        self.code_free = getattr(self.lib, "pcre2_code_free" + suffix)
        self.code_free.argtypes = [ctypes.c_void_p]

    def run(self, pattern, subject, flags):
        if self.width == 8:
            source = pattern.encode("utf-8", "surrogatepass")
            text = subject.encode("utf-8", "surrogatepass")
            source_arg = ctypes.c_char_p(source)
            text_arg = ctypes.c_char_p(text)
            options = 0x00080000 | 0x00020000
        else:
            source = array("I", map(ord, pattern))
            text = array("I", map(ord, subject))
            source_arg = ctypes.c_void_p(source.buffer_info()[0]) if source else None
            text_arg = ctypes.c_void_p(text.buffer_info()[0]) if text else None
            options = 0x00020000
        error, offset = ctypes.c_int(), ctypes.c_size_t()
        options |= 0x00000008 if flags & re.I else 0
        context = self.context_create(None)
        if self.python_octal:
            if self.extra_options is None:
                self.context_free(context)
                return {"error": "Python-octal option unavailable"}
            result = self.extra_options(context, 0x00002000)
            if result:
                self.context_free(context)
                return {"error": f"extra option {result}"}
        code = self.compile(source_arg, len(source), options, ctypes.byref(error), ctypes.byref(offset), context)
        self.context_free(context)
        if not code:
            return {"error": f"compile {error.value} at {offset.value}"}
        data = self.data_create(code, None)
        result = self.match(code, text_arg, len(text), 0, 0, data, None)
        if result < 0:
            value = {"span": None} if result == -1 else {"error": f"match {result}"}
        else:
            offsets = self.ovector(data)
            value = {"span": byte_span(subject, offsets[0], offsets[1]) if self.width == 8 else [offsets[0], offsets[1]]}
        self.data_free(data)
        self.code_free(code)
        return value


class OnigRegion(ctypes.Structure):
    _fields_ = [("allocated", ctypes.c_int), ("num_regs", ctypes.c_int), ("beg", ctypes.POINTER(ctypes.c_int)), ("end", ctypes.POINTER(ctypes.c_int)), ("history_root", ctypes.c_void_p)]


class Oniguruma:
    name = "Oniguruma 6.9.9 Python syntax / ctypes"

    def __init__(self):
        self.lib = ctypes.CDLL("/lib/x86_64-linux-gnu/libonig.so.5")
        self.encoding = ctypes.addressof(ctypes.c_byte.in_dll(self.lib, "OnigEncodingUTF8"))
        self.syntax = ctypes.addressof(ctypes.c_byte.in_dll(self.lib, "OnigSyntaxPython"))
        self.lib.onig_new.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
        self.lib.onig_new.restype = ctypes.c_int
        self.lib.onig_region_new.restype = ctypes.POINTER(OnigRegion)
        self.lib.onig_search.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(OnigRegion), ctypes.c_uint32]
        self.lib.onig_search.restype = ctypes.c_int
        self.lib.onig_region_free.argtypes = [ctypes.POINTER(OnigRegion), ctypes.c_int]
        self.lib.onig_free.argtypes = [ctypes.c_void_p]

    def run(self, pattern, subject, flags):
        source = ctypes.create_string_buffer(pattern.encode("utf-8"))
        text = ctypes.create_string_buffer(subject.encode("utf-8"))
        begin = ctypes.addressof(source)
        text_begin = ctypes.addressof(text)
        regex = ctypes.c_void_p()
        error_info = (ctypes.c_byte * 64)()
        option = 1 if flags & re.I else 0
        result = self.lib.onig_new(ctypes.byref(regex), begin, begin + len(source.value), option, self.encoding, self.syntax, ctypes.byref(error_info))
        if result != 0:
            return {"error": f"compile {result}"}
        region = self.lib.onig_region_new()
        end = text_begin + len(text.value)
        found = self.lib.onig_search(regex, text_begin, end, text_begin, end, region, 0)
        if found < 0:
            value = {"span": None} if found == -1 else {"error": f"match {found}"}
        else:
            value = {"span": byte_span(subject, region.contents.beg[0], region.contents.end[0])}
        self.lib.onig_region_free(region, 1)
        self.lib.onig_free(regex)
        return value


class ICU:
    name = "ICU 74 regex / ctypes"

    def __init__(self):
        self.lib = ctypes.CDLL("/lib/x86_64-linux-gnu/libicui18n.so.74")
        self.lib.uregex_open_74.argtypes = [ctypes.POINTER(ctypes.c_uint16), ctypes.c_int32, ctypes.c_uint32, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int32)]
        self.lib.uregex_open_74.restype = ctypes.c_void_p
        self.lib.uregex_setText_74.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint16), ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]
        self.lib.uregex_find_74.argtypes = [ctypes.c_void_p, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]
        self.lib.uregex_find_74.restype = ctypes.c_int8
        self.lib.uregex_start_74.argtypes = [ctypes.c_void_p, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]
        self.lib.uregex_start_74.restype = ctypes.c_int32
        self.lib.uregex_end_74.argtypes = [ctypes.c_void_p, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]
        self.lib.uregex_end_74.restype = ctypes.c_int32
        self.lib.uregex_close_74.argtypes = [ctypes.c_void_p]

    def run(self, pattern, subject, flags):
        pattern_raw = pattern.encode("utf-16-le")
        text_raw = subject.encode("utf-16-le")
        source = (ctypes.c_uint16 * max(len(pattern_raw) // 2, 1)).from_buffer_copy(pattern_raw or b"\0\0")
        text = (ctypes.c_uint16 * max(len(text_raw) // 2, 1)).from_buffer_copy(text_raw or b"\0\0")
        error = ctypes.c_int32()
        parse_error = (ctypes.c_byte * 160)()
        regex = self.lib.uregex_open_74(source, len(pattern_raw) // 2, 2 if flags & re.I else 0, ctypes.byref(parse_error), ctypes.byref(error))
        if not regex or error.value > 0:
            return {"error": f"compile {error.value}"}
        error.value = 0
        self.lib.uregex_setText_74(regex, text, len(text_raw) // 2, ctypes.byref(error))
        found = self.lib.uregex_find_74(regex, 0, ctypes.byref(error))
        if error.value > 0:
            value = {"error": f"match {error.value}"}
        elif not found:
            value = {"span": None}
        else:
            start = self.lib.uregex_start_74(regex, 0, ctypes.byref(error))
            end = self.lib.uregex_end_74(regex, 0, ctypes.byref(error))
            value = {"span": u16_span(subject, start, end)}
        self.lib.uregex_close_74(regex)
        return value


class ZigPOSIX:
    name = "Zig 0.16 + POSIX regex / ctypes"

    def __init__(self, path):
        self.lib = ctypes.CDLL(path)
        self.lib.rebar_zig_posix_search.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
        self.lib.rebar_zig_posix_search.restype = ctypes.c_int

    def run(self, pattern, subject, flags):
        start, end = ctypes.c_int(), ctypes.c_int()
        result = self.lib.rebar_zig_posix_search(pattern.encode("utf-8"), subject.encode("utf-8"), int(bool(flags & re.I)), ctypes.byref(start), ctypes.byref(end))
        if result < 0:
            return {"error": f"compile/match {result}"}
        if result == 0:
            return {"span": None}
        return {"span": byte_span(subject, start.value, end.value)}


def external(command, pattern, subject, flags):
    completed = subprocess.run([*command, pattern, subject, str(int(bool(flags & re.I)))], capture_output=True, text=True, check=False, timeout=3)
    value = completed.stdout.strip() or completed.stderr.strip()
    if value.startswith("MATCH "):
        _, start, end = value.split()
        return {"span": byte_span(subject, int(start), int(end))}
    if value == "MISS":
        return {"span": None}
    return {"error": value[:300]}


def compatible(expected, actual):
    if "error" in expected:
        return "error" in actual
    return "error" not in actual and actual.get("span") == expected.get("span")


def sha256(path):
    candidate = Path(path)
    if not candidate.is_file():
        return None
    return hashlib.file_digest(candidate.open("rb"), "sha256").hexdigest()


def json_ready(value):
    if isinstance(value, str):
        return value.encode("utf-8", "backslashreplace").decode("utf-8")
    if isinstance(value, list):
        return [json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--go-probe", default="/tmp/rebar-design-survey/go-regex-probe")
    parser.add_argument("--zig-probe", default="/tmp/rebar-design-survey/zig-regex-probe.so")
    parser.add_argument("--pcre2-prefix", default="/tmp/rebar-design-survey/pcre2-10.47-install")
    parser.add_argument("--upstream", default="oracle/cpython-3.14.6/re_tests.py")
    args = parser.parse_args()
    engines = [
        PCRE2("/lib/x86_64-linux-gnu/libpcre2-8.so.0", 8, "PCRE2 10.42 / ctypes"),
        PCRE2(str(Path(args.pcre2_prefix) / "lib/libpcre2-8.so.0"), 8, "PCRE2 10.47 UTF-8 + Python octal / ctypes", True),
        PCRE2(str(Path(args.pcre2_prefix) / "lib/libpcre2-32.so.0"), 32, "PCRE2 10.47 32-bit + Python octal / ctypes", True),
        Oniguruma(), ICU(), ZigPOSIX(args.zig_probe),
    ]
    node_code = 'try { const p=new RegExp(process.argv[1],process.argv[3]==="1"?"iu":"u"); const m=p.exec(process.argv[2]); console.log(m?`MATCH ${Buffer.byteLength(process.argv[2].slice(0,m.index))} ${Buffer.byteLength(process.argv[2].slice(0,m.index+m[0].length))}`:"MISS"); } catch(e) { console.log("ERROR "+e.message); }'
    perl_code = 'use utf8; use Encode qw(decode encode); my ($p,$s,$i)=@ARGV; $p=decode("UTF-8",$p); $s=decode("UTF-8",$s); my $r=eval { $i eq "1" ? qr/$p/i : qr/$p/ }; if($@){ print "ERROR $@"; exit; } if($s =~ $r){ my $a=length(encode("UTF-8",substr($s,0,$-[0]))); my $b=length(encode("UTF-8",substr($s,0,$+[0]))); print "MATCH $a $b"; } else { print "MISS"; }'
    external_engines = [("Go 1.26 regexp (RE2)", [args.go_probe]), ("Node 26 RegExp", ["node", "-e", node_code]), ("Perl 5 regex", ["perl", "-Mutf8", "-MEncode", "-e", perl_code])]
    rows = []
    for case_id, pattern, subject, flags in CASES:
        expected = baseline(pattern, subject, flags)
        for engine in engines:
            try:
                actual = engine.run(pattern, subject, flags)
            except BaseException as error:
                actual = {"error": f"{type(error).__name__}: {error}"}
            rows.append({"case": case_id, "engine": engine.name, "pattern": pattern, "subject": subject, "flags": flags, "expected": expected, "actual": actual, "compatible": compatible(expected, actual)})
        for name, command in external_engines:
            try:
                actual = external(command, pattern, subject, flags)
            except BaseException as error:
                actual = {"error": f"{type(error).__name__}: {error}"}
            rows.append({"case": case_id, "engine": name, "pattern": pattern, "subject": subject, "flags": flags, "expected": expected, "actual": actual, "compatible": compatible(expected, actual)})

    upstream = runpy.run_path(args.upstream)["tests"]
    upstream_rows = []
    for index, item in enumerate(upstream):
        pattern, subject = item[:2]
        expected = baseline(pattern, subject, 0)
        for engine in engines:
            try:
                actual = engine.run(pattern, subject, 0)
            except BaseException as error:
                actual = {"error": f"{type(error).__name__}: {error}"}
            upstream_rows.append({"case": index, "engine": engine.name, "pattern": pattern, "subject": subject, "expected": expected, "actual": actual, "compatible": compatible(expected, actual)})

    result = {"schema": "rebar-engine-survey-v2", "cases": len(CASES), "engines": len(engines) + len(external_engines), "rows": rows, "upstream_cases": len(upstream), "upstream_rows": upstream_rows, "inputs": {"upstream_sha256": sha256(args.upstream), "go_probe_sha256": sha256(args.go_probe), "zig_probe_sha256": sha256(args.zig_probe), "pcre2_1047_8_sha256": sha256(Path(args.pcre2_prefix) / "lib/libpcre2-8.so.0"), "pcre2_1047_32_sha256": sha256(Path(args.pcre2_prefix) / "lib/libpcre2-32.so.0")}}
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(json_ready(result), ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"cases": result["cases"], "engines": result["engines"], "rows": len(rows)}, sort_keys=True))
    for name in [engine.name for engine in engines] + [name for name, _ in external_engines]:
        selected = [row for row in rows if row["engine"] == name]
        print(f"{name}: {sum(row['compatible'] for row in selected)}/{len(selected)} compatible")
        for row in selected:
            if not row["compatible"]:
                print(f"  {row['case']}: {row['actual']}")
    print("Upstream historical pattern corpus (span/syntax):")
    for engine in engines:
        selected = [row for row in upstream_rows if row["engine"] == engine.name]
        print(f"{engine.name}: {sum(row['compatible'] for row in selected)}/{len(selected)} compatible")
        for row in selected:
            if not row["compatible"]:
                print(f"  {row['case']}: {row['actual']}")


if __name__ == "__main__":
    main()
