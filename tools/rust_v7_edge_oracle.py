#!/usr/bin/env python3
"""Frozen, from-scratch, all-candidate CPython 3.14.6 edge-case oracle.

The standard library is used only as the correctness oracle.  No performance
fixture, benchmark, timing result, external regex package, or holdout is read.
Reports are canonical JSON or deterministic gzip (level 9, timestamp zero).
"""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import importlib
import inspect
import itertools
import json
import locale
import platform
import random
import re
import sys
import types
import unicodedata
import warnings
from pathlib import Path


SCHEMA = "rebar-v7-independent-edge-oracle-v1"
PINNED_PYTHON = (3, 14, 6)
PINNED_UNICODE = "16.0.0"
DEFAULT_SEED = 2026072329
ROOT = Path(__file__).resolve().parents[1]
FULL_PLANE = 0x110000
MEMORY_SAFETY_SEED = 0x52454241525F4D37
REPEAT_SEED = 0x52455045415417
MODULE_API_SEED = 0x72656261725F6170695F3134

OBJECT_CONTRACT_SEED = 0x52454241525F4F42
PARSER_GRAMMAR_SEED = 0x52454241525F4752414D4D4152
PARSER_GRAMMAR_CASES_PER_FAMILY = 1280
PARSER_GRAMMAR_FIXTURE_SHA256 = (
    "f2b0e9bfaa7dedacdf201e66499019f30860050b75dd722310f27bb1c79e35dd"
)

# Exact, independently generated pre-fix oracle sources are embedded so the
# frozen suite never relies on mutable private /tmp files or candidate code.
FROZEN_OBJECT_CONTRACT_SOURCE = (
    "#!/usr/bin/env python3\n\"\"\"Bounded, independent CPython 3.14.6 regex object-contract differential.\n\nOnly standard-library modules and the four from-scratch candidate modules are\nimported.  No benchmarks, holdout cases, performance results, or repository\nfiles are read or written.  The complete observations are written exclusively\nunder the caller-supplied private /tmp directory.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\n"
    "import array\nimport collections\nimport copy\nimport gc\nimport importlib\nimport inspect\nimport json\nimport operator\nimport pickle\nimport random\nimport re\nimport sys\n"
    "import types\nimport warnings\nimport weakref\nfrom dataclasses import dataclass\nfrom pathlib import Path\n\n\nSEED = 0x52454241525F4F42\nSCHEMA = \"rebar-independent-object-contract-v1\"\nPINNED = (3, 14, 6)\nMODULES = (\n    (\"ast\", \"candidates.ast_candidate\"),\n"
    "    (\"vm\", \"candidates.vm_candidate\"),\n    (\"rust\", \"candidates.rust_candidate\"),\n    (\"zig\", \"candidates.zig_candidate\"),\n)\n\n\nclass Text(str):\n    pass\n\n\nclass Blob(bytes):\n    pass\n"
    "\n\nclass Index:\n    def __init__(self, value, trace=None, label=\"index\", behavior=\"normal\"):\n        self.value = value\n        self.trace = trace\n        self.label = label\n        self.behavior = behavior\n\n    def __index__(self):\n        if self.trace is not None:\n            self.trace.append((\"index\", self.label, self.behavior))\n"
    "        if self.behavior == \"raise\":\n            raise RuntimeError(\"independent object-contract index sentinel\")\n        if self.behavior == \"noninteger\":\n            return \"not-an-integer\"\n        return self.value\n\n\nclass HashText(str):\n    def __new__(cls, value, trace, behavior=\"normal\"):\n        item = str.__new__(cls, value)\n        item.trace = trace\n        item.behavior = behavior\n"
    "        return item\n\n    def __hash__(self):\n        self.trace.append((\"pattern-hash\", \"text\", self.behavior))\n        if self.behavior == \"raise\":\n            raise RuntimeError(\"independent object-contract text hash sentinel\")\n        return str.__hash__(self)\n\n\nclass HashBlob(bytes):\n    def __new__(cls, value, trace, behavior=\"normal\"):\n        item = bytes.__new__(cls, value)\n"
    "        item.trace = trace\n        item.behavior = behavior\n        return item\n\n    def __hash__(self):\n        self.trace.append((\"pattern-hash\", \"bytes\", self.behavior))\n        if self.behavior == \"raise\":\n            raise RuntimeError(\"independent object-contract bytes hash sentinel\")\n        return bytes.__hash__(self)\n\n\ndef normal(value):\n"
    "    if value is None or isinstance(value, bool):\n        return value\n    if isinstance(value, int):\n        return int(value)\n    if isinstance(value, str):\n        return {\"kind\": type(value).__name__, \"text\": str(value)}\n    if isinstance(value, (bytes, bytearray)):\n        return {\"kind\": type(value).__name__, \"hex\": bytes(value).hex()}\n    if isinstance(value, memoryview):\n        return {\n            \"kind\": \"memoryview\",\n            \"hex\": value.tobytes().hex(),\n"
    "            \"format\": value.format,\n            \"shape\": list(value.shape),\n            \"contiguous\": value.c_contiguous,\n        }\n    if isinstance(value, tuple):\n        return {\"tuple\": [normal(item) for item in value]}\n    if isinstance(value, list):\n        return [normal(item) for item in value]\n    if isinstance(value, dict):\n        return {\n            str(key): normal(item)\n            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))\n"
    "        }\n    if isinstance(value, types.MappingProxyType):\n        return {\"kind\": \"mappingproxy\", \"value\": normal(dict(value))}\n    if isinstance(value, type):\n        return {\"kind\": \"type\", \"name\": value.__name__}\n    return {\"kind\": type(value).__name__, \"repr\": repr(value)}\n\n\ndef attempted(action):\n    try:\n        return {\"status\": \"ok\", \"value\": normal(action())}\n    except Exception as exc:\n"
    "        result = {\n            \"status\": \"error\",\n            \"type\": type(exc).__name__,\n            \"args\": normal(exc.args),\n        }\n        if hasattr(exc, \"msg\") and hasattr(exc, \"pos\"):\n            result[\"pattern_error\"] = {\n                key: normal(getattr(exc, key, None))\n                for key in (\"msg\", \"pattern\", \"pos\", \"lineno\", \"colno\")\n            }\n        return result\n\n"
    "\ndef match_snapshot(match, subject=None):\n    if match is None:\n        return None\n    groups = match.groups()\n    named = match.groupdict()\n    return {\n        \"span\": normal(match.span()),\n        \"regs\": normal(match.regs),\n        \"regs_cached\": match.regs is match.regs,\n        \"group0\": normal(match.group(0)),\n        \"group0_same_subject\": match.group(0) is subject,\n"
    "        \"getitem0_same_subject\": match[0] is subject,\n        \"groups\": normal(groups),\n        \"group_same_subject\": [value is subject for value in groups],\n        \"groupdict\": normal(named),\n        \"named_same_subject\": {\n            name: value is subject for name, value in sorted(named.items())\n        },\n        \"pos\": match.pos,\n        \"endpos\": match.endpos,\n        \"lastindex\": match.lastindex,\n        \"lastgroup\": match.lastgroup,\n        \"subject_same\": match.string is subject,\n"
    "        \"subject_kind\": type(match.string).__name__,\n        \"pattern_kind\": type(match.re.pattern).__name__,\n    }\n\n\n@dataclass(frozen=True, slots=True)\nclass Case:\n    family: str\n    label: str\n    action: object\n\n\n"
    "def byte_subject(kind, payload):\n    if kind == \"bytes\":\n        return payload\n    if kind == \"bytes-subclass\":\n        return Blob(payload)\n    if kind == \"bytearray\":\n        return bytearray(payload)\n    if kind == \"memoryview\":\n        return memoryview(payload)\n    if kind == \"mutable-memoryview\":\n        return memoryview(bytearray(payload))\n    if kind == \"array\":\n"
    "        return array.array(\"B\", payload)\n    raise ValueError(kind)\n\n\ndef collect_rows(rows, subject):\n    output = []\n    for row in rows:\n        if isinstance(row, tuple):\n            output.append({\n                \"value\": normal(row),\n                \"same_subject\": [part is subject for part in row],\n            })\n"
    "        else:\n            output.append({\n                \"value\": normal(row),\n                \"same_subject\": row is subject,\n            })\n    return {\n        \"rows\": output,\n        \"adjacent_same\": [left is right for left, right in zip(rows, rows[1:])],\n    }\n\n\ndef bytes_action(module, expression, payload, kind, operation, pos, endpos):\n"
    "    subject = byte_subject(kind, payload)\n    pattern = module.compile(expression)\n    if operation == \"findall\":\n        return collect_rows(pattern.findall(subject, pos, endpos), subject)\n    if operation == \"finditer\":\n        return [\n            match_snapshot(match, subject)\n            for match in pattern.finditer(subject, pos, endpos)\n        ]\n    if operation == \"scanner-search\":\n        scanner = pattern.scanner(subject, pos, endpos)\n        result = []\n"
    "        for _ in range(len(payload) + 3):\n            match = scanner.search()\n            result.append(match_snapshot(match, subject))\n            if match is None:\n                break\n        else:\n            raise AssertionError(\"scanner did not terminate\")\n        return result\n    if operation == \"scanner-match\":\n        scanner = pattern.scanner(subject, pos, endpos)\n        result = []\n        for _ in range(len(payload) + 3):\n"
    "            match = scanner.match()\n            result.append(match_snapshot(match, subject))\n            if match is None:\n                break\n        else:\n            raise AssertionError(\"scanner did not terminate\")\n        return result\n    return match_snapshot(getattr(pattern, operation)(subject, pos, endpos), subject)\n\n\ndef text_action(module, expression, payload, subclass, operation, pos, endpos):\n    subject = Text(payload) if subclass else payload\n"
    "    pattern = module.compile(expression)\n    if operation == \"findall\":\n        return collect_rows(pattern.findall(subject, pos, endpos), subject)\n    if operation == \"finditer\":\n        return [\n            match_snapshot(match, subject)\n            for match in pattern.finditer(subject, pos, endpos)\n        ]\n    return match_snapshot(getattr(pattern, operation)(subject, pos, endpos), subject)\n\n\ndef pattern_contract(module, expression, flags, operation):\n"
    "    module.purge()\n    source = expression\n    pattern = module.compile(source, flags)\n    subject = b\"abc abc\" if isinstance(source, bytes) else \"abc abc\"\n    if operation == \"repr\":\n        return repr(pattern)\n    if operation == \"source-kind\":\n        return {\"kind\": type(pattern.pattern).__name__, \"same\": pattern.pattern is source}\n    if operation == \"flags\":\n        return pattern.flags\n    if operation == \"groups\":\n        return pattern.groups\n"
    "    if operation == \"groupindex\":\n        return {\"kind\": type(pattern.groupindex).__name__, \"value\": dict(pattern.groupindex)}\n    if operation == \"groupindex-identity\":\n        return pattern.groupindex is pattern.groupindex\n    if operation == \"cache-identity\":\n        return module.compile(source, flags) is pattern\n    if operation == \"copy\":\n        return copy.copy(pattern) is pattern\n    if operation == \"deepcopy\":\n        return copy.deepcopy(pattern) is pattern\n    if operation == \"weakref\":\n        return weakref.ref(pattern)() is pattern\n"
    "    if operation == \"pickle\":\n        restored = pickle.loads(pickle.dumps(pattern))\n        return {\n            \"pattern\": normal(restored.pattern),\n            \"flags\": restored.flags,\n            \"groups\": restored.groups,\n            \"groupindex\": dict(restored.groupindex),\n            \"search\": match_snapshot(restored.search(subject), subject),\n        }\n    if operation == \"equal-compiled\":\n        module.purge()\n        other = module.compile(source, flags)\n"
    "        return {\"equal\": pattern == other, \"same_hash\": hash(pattern) == hash(other)}\n    if operation.startswith(\"readonly-\"):\n        name = operation.removeprefix(\"readonly-\")\n        return setattr(pattern, name, None)\n    if operation == \"generic\":\n        alias = module.Pattern[str]\n        return {\n            \"origin_name\": alias.__origin__.__name__,\n            \"args\": [item.__name__ for item in alias.__args__],\n        }\n    raise ValueError(operation)\n\n"
    "\ndef match_contract(module, expression, subject, operation, key_kind):\n    match = module.compile(expression).search(subject)\n    if match is None:\n        raise AssertionError(\"independent object-contract expected a match\")\n    trace = []\n    keys = {\n        \"zero\": 0,\n        \"one\": 1,\n        \"minus-one\": -1,\n        \"true\": True,\n        \"false\": False,\n"
    "        \"float\": 1.0,\n        \"string\": \"name\",\n        \"bytes\": b\"name\",\n        \"index\": Index(1, trace, \"group\"),\n        \"negative-index\": Index(-1, trace, \"group\"),\n        \"raising-index\": Index(1, trace, \"group\", \"raise\"),\n        \"noninteger-index\": Index(1, trace, \"group\", \"noninteger\"),\n        \"huge-index\": Index(1 << 100, trace, \"group\"),\n        \"none\": None,\n        \"object\": object(),\n    }\n    key = keys[key_kind]\n"
    "\n    def action():\n        if operation == \"group\":\n            return match.group(key)\n        if operation == \"getitem\":\n            return match[key]\n        if operation == \"start\":\n            return match.start(key)\n        if operation == \"end\":\n            return match.end(key)\n        if operation == \"span\":\n            return match.span(key)\n"
    "        raise ValueError(operation)\n\n    result = attempted(action)\n    result[\"trace\"] = normal(trace)\n    return result\n\n\ndef window_contract(module, expression, subject, operation, start_kind, end_kind):\n    trace = []\n\n    def make(kind, label):\n        options = {\n"
    "            \"zero\": 0,\n            \"one\": 1,\n            \"negative\": -5,\n            \"huge\": 1 << 100,\n            \"true\": True,\n            \"false\": False,\n            \"float\": 1.0,\n            \"none\": None,\n            \"normal-index\": Index(1, trace, label),\n            \"raising-index\": Index(1, trace, label, \"raise\"),\n            \"bad-index\": Index(1, trace, label, \"noninteger\"),\n        }\n"
    "        return options[kind]\n\n    start = make(start_kind, \"pos\")\n    end = make(end_kind, \"endpos\")\n    pattern = module.compile(expression)\n\n    def action():\n        if operation == \"finditer\":\n            return [match_snapshot(item, subject) for item in pattern.finditer(subject, start, end)]\n        if operation == \"scanner\":\n            scanner = pattern.scanner(subject, start, end)\n            return [match_snapshot(scanner.search(), subject) for _ in range(3)]\n"
    "        result = getattr(pattern, operation)(subject, start, end)\n        if operation == \"findall\":\n            return collect_rows(result, subject)\n        return match_snapshot(result, subject)\n\n    result = attempted(action)\n    result[\"trace\"] = normal(trace)\n    return result\n\n\ndef signature_contract(module, owner, name):\n    if owner == \"module\":\n"
    "        value = getattr(module, name)\n    elif owner == \"pattern-class\":\n        value = getattr(module.Pattern, name)\n    elif owner == \"pattern-bound\":\n        value = getattr(module.compile(\"(?P<name>a)\"), name)\n    elif owner == \"match-class\":\n        value = getattr(module.Match, name)\n    elif owner == \"match-bound\":\n        value = getattr(module.search(\"(?P<name>a)\", \"a\"), name)\n    else:\n        raise ValueError(owner)\n    return str(inspect.signature(value))\n"
    "\n\ndef warning_contract(module, action, text, byte_mode):\n    expression = text.encode(\"ascii\") if byte_mode else text\n    subject = b\"aaa\" if byte_mode else \"aaa\"\n    replacement = b\"x\" if byte_mode else \"x\"\n    module.purge()\n    with warnings.catch_warnings(record=True) as captured:\n        warnings.simplefilter(\"always\")\n        if action == \"compile\":\n            result = attempted(lambda: module.compile(expression))\n        elif action == \"split-positional\":\n"
    "            result = attempted(lambda: module.split(expression, subject, 1))\n        elif action == \"split-flags-positional\":\n            result = attempted(lambda: module.split(expression, subject, 1, 0))\n        elif action == \"sub-positional\":\n            result = attempted(lambda: module.sub(expression, replacement, subject, 1))\n        elif action == \"sub-flags-positional\":\n            result = attempted(lambda: module.sub(expression, replacement, subject, 1, 0))\n        elif action == \"subn-positional\":\n            result = attempted(lambda: module.subn(expression, replacement, subject, 1))\n        elif action == \"subn-flags-positional\":\n            result = attempted(lambda: module.subn(expression, replacement, subject, 1, 0))\n        else:\n"
    "            raise ValueError(action)\n    return {\n        \"result\": result,\n        \"warnings\": [\n            {\n                \"category\": item.category.__name__,\n                \"message\": str(item.message),\n                \"at_probe\": Path(item.filename).name == \"object_contract_probe.py\",\n            }\n            for item in captured\n        ],\n    }\n"
    "\n\ndef mutable_contract(module, operation, kind, expression):\n    backing = bytearray(b\"a1 b2 c3\")\n    subject = backing if kind == \"bytearray\" else memoryview(backing)\n    pattern = module.compile(expression)\n    if operation == \"match-mutation\":\n        found = pattern.search(subject)\n        before = match_snapshot(found, subject)\n        backing[0] = ord(\"z\")\n        after = match_snapshot(found, subject)\n        resize = attempted(lambda: backing.append(ord(\"!\")))\n"
    "        return {\n            \"before\": before,\n            \"after\": after,\n            \"resize\": resize,\n            \"final\": normal(backing),\n        }\n    if operation == \"iterator-mutation\":\n        iterator = pattern.finditer(subject)\n        first = next(iterator, None)\n        backing[3] = ord(\"y\")\n        remaining = [match_snapshot(value, subject) for value in iterator]\n        return {\n"
    "            \"first\": match_snapshot(first, subject),\n            \"remaining\": remaining,\n            \"final\": normal(backing),\n        }\n    if operation == \"scanner-mutation\":\n        scanner = pattern.scanner(subject)\n        first = scanner.search()\n        backing[3] = ord(\"y\")\n        values = []\n        for _ in range(5):\n            value = scanner.search()\n            values.append(match_snapshot(value, subject))\n"
    "            if value is None:\n                break\n        return {\n            \"first\": match_snapshot(first, subject),\n            \"remaining\": values,\n            \"final\": normal(backing),\n        }\n    raise ValueError(operation)\n\n\ndef hash_contract(module, byte_mode, behavior, operation):\n    trace = []\n"
    "    module.purge()\n    pattern = (\n        HashBlob(b\"a\", trace, behavior)\n        if byte_mode else HashText(\"a\", trace, behavior)\n    )\n    subject = b\"aba\" if byte_mode else \"aba\"\n\n    def invoke():\n        if operation == \"compile\":\n            return {\"source_kind\": type(module.compile(pattern).pattern).__name__}\n        result = getattr(module, operation)(pattern, subject)\n        if operation == \"finditer\":\n"
    "            return [match_snapshot(item, subject) for item in result]\n        if operation == \"findall\":\n            return collect_rows(result, subject)\n        return match_snapshot(result, subject)\n\n    result = attempted(invoke)\n    result[\"trace\"] = normal(trace)\n    return result\n\n\ndef group_capture_contract(module, expression, subject, operation):\n    match = module.compile(expression).search(subject)\n"
    "    if match is None:\n        return None\n    if operation == \"copy\":\n        return copy.copy(match) is match\n    if operation == \"deepcopy\":\n        return copy.deepcopy(match) is match\n    if operation == \"pickle\":\n        return pickle.dumps(match)\n    if operation == \"weakref\":\n        return weakref.ref(match)() is match\n    if operation == \"repr\":\n        return repr(match)\n"
    "    if operation == \"regs-cache\":\n        return match.regs is match.regs\n    if operation == \"re-same\":\n        return match.re is module.compile(expression)\n    if operation == \"string-same\":\n        return match.string is subject\n    if operation.startswith(\"readonly-\"):\n        return setattr(match, operation.removeprefix(\"readonly-\"), None)\n    if operation == \"generic\":\n        alias = module.Match[str]\n        return {\n            \"origin_name\": alias.__origin__.__name__,\n"
    "            \"args\": [item.__name__ for item in alias.__args__],\n        }\n    if operation == \"tracked\":\n        return gc.is_tracked(match)\n    raise ValueError(operation)\n\n\ndef build_cases():\n    cases = []\n\n    def add(family, label, action):\n        cases.append(Case(family, label, action))\n"
    "\n    byte_patterns = (\n        rb\"a*\", rb\"(a*)\", rb\"(?P<all>a*)\", rb\".*\",\n        rb\"(?P<all>.*)\", rb\"(a*)(a?)\", rb\"(?:a|)*\",\n        rb\"(?P<x>a)(?P<y>a)?\", rb\"a|\", rb\"[a-z]+\",\n    )\n    lengths = (0, 1, 2, 3, 7, 31, 63, 64, 65, 127, 128, 129)\n    for pattern_index, expression in enumerate(byte_patterns):\n        for length in lengths:\n            payload = b\"a\" * length\n            windows = dict.fromkeys(((0, length), (0, max(length - 1, 0)), (min(1, length), length)))\n            for kind in (\"bytes\", \"bytes-subclass\", \"bytearray\", \"memoryview\", \"mutable-memoryview\", \"array\"):\n"
    "                for pos, endpos in windows:\n                    for operation in (\"search\", \"match\", \"fullmatch\", \"findall\", \"finditer\"):\n                        label = f\"p{pattern_index}:{kind}:len{length}:{operation}:{pos}:{endpos}\"\n                        add(\n                            \"whole-bytes-and-capture-identity\", label,\n                            lambda module, e=expression, p=payload, k=kind, op=operation, a=pos, b=endpos:\n                                bytes_action(module, e, p, k, op, a, b),\n                        )\n\n    text_patterns = (r\"a*\", r\"(a*)\", r\"(?P<all>a*)\", r\".*\", r\"(?P<all>.*)\", r\"(a*)(a?)\", r\"a|\")\n    text_values = (\"\", \"a\", \"aa\", \"aaa\", \"é\", \"éé\", \"😀\", \"a😀a\", \"a\\x00a\", \"a\" * 63, \"a\" * 64, \"a\" * 65, \"\\ud800\")\n    for pattern_index, expression in enumerate(text_patterns):\n"
    "        for value_index, payload in enumerate(text_values):\n            windows = dict.fromkeys(((0, len(payload)), (0, max(len(payload) - 1, 0)), (min(1, len(payload)), len(payload))))\n            for subclass in (False, True):\n                for pos, endpos in windows:\n                    for operation in (\"search\", \"match\", \"fullmatch\", \"findall\", \"finditer\"):\n                        label = f\"p{pattern_index}:v{value_index}:subclass{int(subclass)}:{operation}:{pos}:{endpos}\"\n                        add(\n                            \"whole-text-and-capture-identity\", label,\n                            lambda module, e=expression, p=payload, s=subclass, op=operation, a=pos, b=endpos:\n                                text_action(module, e, p, s, op, a, b),\n                        )\n\n"
    "    expressions = (\n        (\"plain-text\", \"abc\", 0),\n        (\"named-text\", r\"(?P<name>abc)\", 0),\n        (\"subclass-text\", Text(\"abc\"), 0),\n        (\"plain-bytes\", b\"abc\", 0),\n        (\"named-bytes\", rb\"(?P<name>abc)\", 0),\n        (\"subclass-bytes\", Blob(b\"abc\"), 0),\n        (\"ignorecase\", \"abc\", int(re.IGNORECASE)),\n        (\"ascii\", \"abc\", int(re.ASCII)),\n        (\"multiline\", \"abc\", int(re.MULTILINE)),\n        (\"dotall\", \"abc\", int(re.DOTALL)),\n        (\"combined\", \"abc\", int(re.IGNORECASE | re.MULTILINE)),\n"
    "        (\"repr-199\", \"a\" * 199, 0),\n        (\"repr-200\", \"a\" * 200, 0),\n        (\"repr-201\", \"a\" * 201, 0),\n        (\"repr-wide\", \"é\" * 100, 0),\n    )\n    pattern_ops = (\n        \"repr\", \"source-kind\", \"flags\", \"groups\", \"groupindex\",\n        \"groupindex-identity\", \"cache-identity\", \"copy\", \"deepcopy\",\n        \"weakref\", \"pickle\", \"equal-compiled\", \"generic\",\n        \"readonly-pattern\", \"readonly-flags\", \"readonly-groups\", \"readonly-groupindex\",\n        \"readonly-search\", \"readonly-match\", \"readonly-fullmatch\", \"readonly-findall\",\n        \"readonly-finditer\", \"readonly-scanner\", \"readonly-split\", \"readonly-sub\", \"readonly-subn\",\n"
    "    )\n    for tag, expression, flags in expressions:\n        for operation in pattern_ops:\n            add(\n                \"compiled-pattern-contract\", f\"{tag}:{operation}\",\n                lambda module, e=expression, f=flags, op=operation: pattern_contract(module, e, f, op),\n            )\n\n    keys = (\n        \"zero\", \"one\", \"minus-one\", \"true\", \"false\", \"float\", \"string\",\n        \"bytes\", \"index\", \"negative-index\", \"raising-index\", \"noninteger-index\",\n        \"huge-index\", \"none\", \"object\",\n"
    "    )\n    for byte_mode in (False, True):\n        expression = rb\"(?P<name>a)(b)?\" if byte_mode else r\"(?P<name>a)(b)?\"\n        subject = b\"a\" if byte_mode else \"a\"\n        for operation in (\"group\", \"getitem\", \"start\", \"end\", \"span\"):\n            for key in keys:\n                add(\n                    \"match-group-index-errors-and-side-effects\",\n                    f\"{'bytes' if byte_mode else 'text'}:{operation}:{key}\",\n                    lambda module, e=expression, s=subject, op=operation, k=key:\n                        match_contract(module, e, s, op, k),\n                )\n"
    "\n    window_pairs = (\n        (\"zero\", \"zero\"), (\"zero\", \"one\"), (\"one\", \"one\"),\n        (\"negative\", \"one\"), (\"true\", \"false\"), (\"normal-index\", \"normal-index\"),\n        (\"normal-index\", \"raising-index\"), (\"raising-index\", \"normal-index\"),\n        (\"normal-index\", \"bad-index\"), (\"bad-index\", \"normal-index\"),\n        (\"huge\", \"normal-index\"), (\"normal-index\", \"huge\"),\n        (\"none\", \"one\"), (\"zero\", \"none\"), (\"float\", \"one\"), (\"zero\", \"float\"),\n    )\n    for byte_mode in (False, True):\n        expression = rb\"(?P<name>a)\" if byte_mode else r\"(?P<name>a)\"\n        subject = b\"a a\" if byte_mode else \"a a\"\n"
    "        for operation in (\"search\", \"match\", \"fullmatch\", \"findall\", \"finditer\", \"scanner\"):\n            for start, end in window_pairs:\n                add(\n                    \"window-index-order-and-exact-errors\",\n                    f\"{'bytes' if byte_mode else 'text'}:{operation}:{start}:{end}\",\n                    lambda module, e=expression, s=subject, op=operation, a=start, b=end:\n                        window_contract(module, e, s, op, a, b),\n                )\n\n    module_names = (\n        \"compile\", \"search\", \"match\", \"fullmatch\", \"findall\", \"finditer\",\n        \"split\", \"sub\", \"subn\", \"escape\", \"purge\",\n"
    "    )\n    pattern_names = (\n        \"search\", \"match\", \"fullmatch\", \"findall\", \"finditer\", \"scanner\",\n        \"split\", \"sub\", \"subn\",\n    )\n    match_names = (\"group\", \"groups\", \"groupdict\", \"start\", \"end\", \"span\", \"expand\")\n    for owner, names in (\n        (\"module\", module_names),\n        (\"pattern-class\", pattern_names),\n        (\"pattern-bound\", pattern_names),\n        (\"match-class\", match_names),\n        (\"match-bound\", match_names),\n"
    "    ):\n        for name in names:\n            add(\n                \"inspectable-public-signatures\", f\"{owner}:{name}\",\n                lambda module, o=owner, n=name: signature_contract(module, o, n),\n            )\n\n    warning_patterns = (\"[[a]\", \"[a&&b]\", \"[a~~b]\", \"[a||b]\", \"[a--b]\")\n    for byte_mode in (False, True):\n        for expression in warning_patterns:\n            add(\n                \"warning-messages-and-call-site\", f\"{'bytes' if byte_mode else 'text'}:compile:{expression}\",\n"
    "                lambda module, e=expression, b=byte_mode: warning_contract(module, \"compile\", e, b),\n            )\n        for operation in (\n            \"split-positional\", \"split-flags-positional\", \"sub-positional\",\n            \"sub-flags-positional\", \"subn-positional\", \"subn-flags-positional\",\n        ):\n            add(\n                \"warning-messages-and-call-site\", f\"{'bytes' if byte_mode else 'text'}:{operation}\",\n                lambda module, op=operation, b=byte_mode: warning_contract(module, op, \"a\", b),\n            )\n\n    for kind in (\"bytearray\", \"memoryview\"):\n"
    "        for expression in (rb\"(?P<letter>[a-z])(?P<digit>\\d)\", rb\"[a-z]\\d\", rb\"(?:[a-z]\\d)*\"):\n            for operation in (\"match-mutation\", \"iterator-mutation\", \"scanner-mutation\"):\n                add(\n                    \"mutable-buffer-and-scanner-lifetime\",\n                    f\"{kind}:{expression!r}:{operation}\",\n                    lambda module, k=kind, e=expression, op=operation:\n                        mutable_contract(module, op, k, e),\n                )\n\n    for byte_mode in (False, True):\n        for behavior in (\"normal\", \"raise\"):\n            for operation in (\"compile\", \"search\", \"match\", \"fullmatch\", \"findall\", \"finditer\"):\n"
    "                add(\n                    \"pattern-hash-call-count-and-exact-errors\",\n                    f\"{'bytes' if byte_mode else 'text'}:{behavior}:{operation}\",\n                    lambda module, b=byte_mode, h=behavior, op=operation:\n                        hash_contract(module, b, h, op),\n                )\n\n    for byte_mode in (False, True):\n        expression = rb\"(?P<name>a)(b)?\" if byte_mode else r\"(?P<name>a)(b)?\"\n        subject = b\"a\" if byte_mode else \"a\"\n        for operation in (\n            \"copy\", \"deepcopy\", \"pickle\", \"weakref\", \"repr\", \"regs-cache\",\n"
    "            \"re-same\", \"string-same\", \"generic\", \"tracked\", \"readonly-re\",\n            \"readonly-string\", \"readonly-pos\", \"readonly-endpos\",\n            \"readonly-lastindex\", \"readonly-lastgroup\", \"readonly-regs\",\n        ):\n            add(\n                \"match-copy-pickle-gc-and-readonly\", f\"{'bytes' if byte_mode else 'text'}:{operation}\",\n                lambda module, e=expression, s=subject, op=operation:\n                    group_capture_contract(module, e, s, op),\n            )\n\n    randomizer = random.Random(SEED)\n    seeded_patterns = (\n"
    "        rb\"a*\", rb\"(a*)\", rb\"(?P<x>a*)\", rb\"[ab]+\",\n        rb\"(a?)(b?)\", rb\"(?:ab|a|)\", rb\"(?P<x>a)(?P<y>b)?\",\n        rb\"(?:a|b)*\", rb\"a{0,3}\", rb\"(?=a)a\",\n    )\n    for index in range(160):\n        length = randomizer.randrange(0, 48)\n        payload = bytes(randomizer.choice(b\"abxy\\x00\\n\") for _ in range(length))\n        expression = randomizer.choice(seeded_patterns)\n        kind = randomizer.choice((\"bytes\", \"bytes-subclass\", \"bytearray\", \"memoryview\", \"array\"))\n        start = randomizer.randrange(0, length + 1)\n        end = randomizer.randrange(start, length + 1)\n        for operation in (\"search\", \"match\", \"fullmatch\", \"findall\", \"finditer\", \"scanner-search\", \"scanner-match\"):\n"
    "            add(\n                \"independent-seeded-object-fuzz\",\n                f\"seed{SEED:x}:case{index}:{kind}:{operation}:{start}:{end}\",\n                lambda module, e=expression, p=payload, k=kind, op=operation, a=start, b=end:\n                    bytes_action(module, e, p, k, op, a, b),\n            )\n\n    return tuple(cases)\n\n\ndef evaluate(cases, module):\n    records = []\n"
    "    for case in cases:\n        records.append({\n            \"family\": case.family,\n            \"case\": case.label,\n            \"observation\": attempted(lambda c=case: c.action(module)),\n        })\n    return records\n\n\ndef summarize(records, expected):\n    counts = collections.Counter()\n    failed_counts = collections.Counter()\n"
    "    failures = []\n    for actual, oracle in zip(records, expected, strict=True):\n        if actual[\"family\"] != oracle[\"family\"] or actual[\"case\"] != oracle[\"case\"]:\n            raise AssertionError(\"independent oracle case identity drift\")\n        counts[actual[\"family\"]] += 1\n        if actual[\"observation\"] != oracle[\"observation\"]:\n            failed_counts[actual[\"family\"]] += 1\n            failures.append({\n                \"family\": actual[\"family\"],\n                \"case\": actual[\"case\"],\n                \"expected\": oracle[\"observation\"],\n                \"actual\": actual[\"observation\"],\n"
    "            })\n    return {\n        \"checks\": len(records),\n        \"failed\": len(failures),\n        \"families\": [\n            {\"family\": family, \"checks\": checks, \"failed\": failed_counts[family]}\n            for family, checks in sorted(counts.items())\n        ],\n        \"failures\": failures,\n    }\n\n\n"
    "def main():\n    parser = argparse.ArgumentParser(description=__doc__)\n    parser.add_argument(\"--output-dir\", type=Path, required=True)\n    args = parser.parse_args()\n    if tuple(sys.version_info[:3]) != PINNED:\n        raise SystemExit(f\"requires exact pinned CPython {PINNED!r}\")\n    output = args.output_dir.resolve()\n    if not str(output).startswith(\"/tmp/rebar-object-contract-\"):\n        raise SystemExit(\"independent evidence must remain in its private /tmp directory\")\n    if not output.is_dir():\n        raise SystemExit(\"private output directory must already exist\")\n\n"
    "    cases = build_cases()\n    reference_a = evaluate(cases, re)\n    reference_b = evaluate(cases, re)\n    self_summary = summarize(reference_b, reference_a)\n    reports = {\n        \"schema\": SCHEMA,\n        \"python\": sys.version.split()[0],\n        \"seed\": SEED,\n        \"case_count\": len(cases),\n        \"self_oracle\": self_summary,\n        \"candidates\": {},\n    }\n"
    "    (output / \"independent-stdlib-self.json\").write_text(\n        json.dumps({\"schema\": SCHEMA, \"seed\": SEED, **self_summary}, sort_keys=True, ensure_ascii=True, indent=2) + \"\\n\",\n        encoding=\"utf-8\",\n    )\n    if self_summary[\"failed\"]:\n        (output / \"independent-summary.json\").write_text(\n            json.dumps(reports, sort_keys=True, ensure_ascii=True, indent=2) + \"\\n\", encoding=\"utf-8\",\n        )\n        raise SystemExit(\"independent stdlib-vs-stdlib self oracle is not deterministic\")\n\n    for label, module_name in MODULES:\n        module = importlib.import_module(module_name)\n"
    "        records = evaluate(cases, module)\n        summary = summarize(records, reference_a)\n        report = {\"schema\": SCHEMA, \"seed\": SEED, \"module\": module_name, **summary}\n        (output / f\"independent-{label}.json\").write_text(\n            json.dumps(report, sort_keys=True, ensure_ascii=True, indent=2) + \"\\n\", encoding=\"utf-8\",\n        )\n        reports[\"candidates\"][label] = {\n            key: value for key, value in summary.items() if key != \"failures\"\n        }\n        print(json.dumps({\"module\": label, \"checks\": summary[\"checks\"], \"failed\": summary[\"failed\"]}, sort_keys=True), flush=True)\n\n    (output / \"independent-summary.json\").write_text(\n"
    "        json.dumps(reports, sort_keys=True, ensure_ascii=True, indent=2) + \"\\n\", encoding=\"utf-8\",\n    )\n    print(json.dumps({\"schema\": SCHEMA, \"seed\": SEED, \"self_failed\": self_summary[\"failed\"], \"cases\": len(cases)}, sort_keys=True), flush=True)\n\n\nif __name__ == \"__main__\":\n    main()\n"
)

FROZEN_PARSER_GRAMMAR_SOURCE = (
    "#!/usr/bin/env python3\n\"\"\"Private, crash-isolated CPython 3.14.6 regex-grammar differential.\n\nThis tool never reads a performance fixture, benchmark, or holdout.  The\nstandard-library regex engine runs only in dedicated ``worker --module re``\noracle processes.  Candidate workers import one from-scratch candidate each.\nEvery case, valid result, invalid-pattern error, offset, warning, mismatch,\ntimeout, and crashed worker is retained.\n\"\"\"\n\nfrom __future__ import annotations\n\n"
    "import argparse\nimport collections\nimport hashlib\nimport importlib\nimport itertools\nimport json\nimport os\nimport pathlib\nimport platform\nimport random\nimport subprocess\nimport sys\n"
    "import time\nimport warnings\n\n\nROOT = pathlib.Path(\"/home/dev-user/src/rebar\")\nSCHEMA = \"rebar-independent-parser-grammar-fuzz-v1\"\nSEED = 0x52454241525F4752414D4D4152\nPINNED_VERSION = (3, 14, 6)\nI, M, S, X, A = 2, 8, 16, 64, 256\nCANDIDATES = (\n    \"candidates.ast_candidate\",\n    \"candidates.vm_candidate\",\n"
    "    \"candidates.rust_candidate\",\n    \"candidates.zig_candidate\",\n)\nTRACKED_SOURCES = (\n    \"candidates/ast_candidate.py\",\n    \"candidates/vm_candidate.py\",\n    \"candidates/_vm_native.c\",\n    \"candidates/_vm_native.cpython-314-x86_64-linux-gnu.so\",\n    \"candidates/rust_candidate.py\",\n    \"candidates/rust/src/lib.rs\",\n    \"candidates/rust/src/search.rs\",\n    \"candidates/rust/src/newline.rs\",\n"
    "    \"candidates/rust/src/stack.rs\",\n    \"candidates/rust/src/unicode_tables.rs\",\n    \"candidates/rust/py_bridge.c\",\n    \"candidates/_rust_engine.so\",\n    \"candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so\",\n    \"candidates/zig_candidate.py\",\n    \"candidates/zig/mini_regex.zig\",\n    \"candidates/zig/py_bridge.c\",\n    \"candidates/_zig_probe.so\",\n    \"candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so\",\n)\nFAMILIES = (\n"
    "    \"quantified-positive-lookahead\",\n    \"quantified-negative-lookahead\",\n    \"quantified-positive-lookbehind\",\n    \"quantified-negative-lookbehind\",\n    \"nested-capture-conditionals\",\n    \"conditional-error-offsets\",\n    \"scoped-inline-flags\",\n    \"invalid-inline-flags\",\n    \"verbose-comments-and-escapes\",\n    \"bytes-named-backreferences\",\n    \"bytes-error-offsets\",\n    \"atomic-ordered-alternation\",\n"
    "    \"possessive-repeat-captures\",\n    \"lookbehind-backreference-width\",\n    \"nullable-branch-captures\",\n    \"escape-and-character-class-errors\",\n)\n\n\ndef canonical(value):\n    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(\",\", \":\"))\n\n\ndef digest_path(path):\n"
    "    digest = hashlib.sha256()\n    with path.open(\"rb\") as handle:\n        for block in iter(lambda: handle.read(1024 * 1024), b\"\"):\n            digest.update(block)\n    return digest.hexdigest()\n\n\ndef source_hashes():\n    result = {}\n    for name in TRACKED_SOURCES:\n        path = ROOT / name\n        if path.is_file():\n"
    "            result[name] = digest_path(path)\n    return result\n\n\ndef assert_pinned():\n    if tuple(sys.version_info[:3]) != PINNED_VERSION:\n        raise RuntimeError(f\"requires pinned CPython {PINNED_VERSION}, found {sys.version}\")\n\n\ndef normalise(value):\n    if value is None or isinstance(value, (bool, int, float, str)):\n        return value\n"
    "    if isinstance(value, (bytes, bytearray, memoryview)):\n        return {\"kind\": type(value).__name__, \"hex\": bytes(value).hex()}\n    if isinstance(value, tuple):\n        return {\"tuple\": [normalise(item) for item in value]}\n    if isinstance(value, list):\n        return [normalise(item) for item in value]\n    if isinstance(value, dict):\n        return {\n            str(key): normalise(item)\n            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))\n        }\n    return {\"kind\": type(value).__name__, \"repr\": repr(value)}\n"
    "\n\ndef encode_domain(value):\n    if isinstance(value, bytes):\n        return {\"kind\": \"bytes\", \"hex\": value.hex()}\n    return {\"kind\": \"str\", \"value\": value}\n\n\ndef decode_domain(item):\n    if item[\"kind\"] == \"bytes\":\n        return bytes.fromhex(item[\"hex\"])\n    if item[\"kind\"] == \"str\":\n"
    "        return item[\"value\"]\n    raise ValueError(f\"unknown case domain: {item['kind']!r}\")\n\n\ndef match_snapshot(match):\n    if match is None:\n        return None\n    default = b\"!\" if isinstance(match.re.pattern, bytes) else \"!\"\n    return {\n        \"span\": normalise(match.span()),\n        \"regs\": normalise(match.regs),\n        \"group0\": normalise(match.group(0)),\n"
    "        \"groups\": normalise(match.groups()),\n        \"groups_default\": normalise(match.groups(default)),\n        \"groupdict\": normalise(match.groupdict()),\n        \"lastindex\": match.lastindex,\n        \"lastgroup\": match.lastgroup,\n        \"pos\": match.pos,\n        \"endpos\": match.endpos,\n    }\n\n\ndef capture_error(error):\n    observed = {\n"
    "        \"status\": \"error\",\n        \"type\": type(error).__name__,\n        \"str\": str(error),\n        \"args\": normalise(error.args),\n    }\n    if all(hasattr(error, key) for key in (\"msg\", \"pattern\", \"pos\", \"lineno\", \"colno\")):\n        observed[\"pattern_error\"] = {\n            key: normalise(getattr(error, key))\n            for key in (\"msg\", \"pattern\", \"pos\", \"lineno\", \"colno\")\n        }\n    return observed\n\n"
    "\ndef attempt(action):\n    try:\n        return {\"status\": \"ok\", \"value\": normalise(action())}\n    except Exception as error:\n        return capture_error(error)\n\n\ndef short_word(rng):\n    return \"\".join(rng.choice(\"abcxyz\") for _ in range(rng.randrange(1, 6)))\n\n\n"
    "def text_subject(rng, token=\"a\"):\n    atoms = (\"\", \"a\", \"b\", \"ab\", \"ba\", \"x\", \"\\n\", \"1\", \"_\", \"é\", \"İ\", \"ß\")\n    return rng.choice(atoms) + token + rng.choice(atoms) + rng.choice(atoms)\n\n\ndef byte_subject(rng, token=b\"a\"):\n    atoms = (b\"\", b\"a\", b\"b\", b\"ab\", b\"ba\", b\"x\", b\"\\n\", b\"1\", b\"_\", b\"\\x80\", b\"\\xff\")\n    return rng.choice(atoms) + token + rng.choice(atoms) + rng.choice(atoms)\n\n\ndef quantified_case(family, rng, name):\n    behind = \"lookbehind\" in family\n"
    "    negative = \"negative\" in family\n    prefix = \"?<!\" if behind and negative else \"?<=\" if behind else \"?!\" if negative else \"?=\"\n    if behind:\n        inner = rng.choice((\"a\", \"b\", \"[ab]\", \".\", \"(?i:a)\", \"(?:a|b)\", f\"(?P<{name}>a)\"))\n    else:\n        inner = rng.choice((\n            \"a\", \"b\", \"[ab]\", \".\", r\"\\d\", \"(?:a|ab)\",\n            f\"(?P<{name}>a)\", \"(?i:a)\", \"(?=a)\", \"(?!z)\",\n        ))\n    quant = rng.choice((\"*\", \"+\", \"?\", \"{0}\", \"{1}\", \"{2}\", \"{0,1}\", \"{1,3}\", \"{2,4}\"))\n    quant += rng.choice((\"\", \"?\", \"+\"))\n    assertion = \"(\" + prefix + inner + \")\" + quant\n"
    "    shape = rng.randrange(6)\n    if shape == 0:\n        pattern = assertion\n    elif shape == 1:\n        pattern = assertion + rng.choice((\"a\", \"b\", \"\", \"(?:a|)\", r\"\\b\"))\n    elif shape == 2:\n        pattern = \"(?:\" + assertion + \")\" + rng.choice((\"\", \"a\", \"b\"))\n    elif shape == 3:\n        pattern = rng.choice((\"a\", \"\", r\"\\b\")) + assertion + rng.choice((\"\", \"a\"))\n    elif shape == 4:\n        pattern = \"(\" + assertion + \")\" + rng.choice((\"\", \"a\"))\n    else:\n"
    "        pattern = \"(?:\" + assertion + \"|\" + rng.choice((\"a\", \"b\", \"\")) + \")\"\n    flags = rng.choice((0, I, M, S, I | M, A, A | I))\n    return pattern, text_subject(rng, rng.choice((\"a\", \"b\", \"ab\", \"1\"))), flags\n\n\ndef make_case(family, rng, index):\n    name = \"g\" + short_word(rng) + str(rng.randrange(0, 4096))\n    word = short_word(rng)\n    if family.startswith(\"quantified-\"):\n        pattern, subject, flags = quantified_case(family, rng, name)\n    elif family == \"nested-capture-conditionals\":\n        patterns = (\n"
    "            f\"(?P<{name}>a)?(?(\" + name + \")b|c)\",\n            f\"((?P<{name}>a)?b)(?({name})c|d)\",\n            f\"(?:(?P<{name}>a)|b)(?({name})c|d)\",\n            f\"(?P<{name}>a(b)?)?(?({name})(c|d)|e)\",\n            f\"(?=(?P<{name}>a))(?({name})a|b)\",\n            f\"(?P<{name}>(a|ab))(?({name})b|c)\",\n            f\"(?:(?P<{name}>a)?)*?(?({name})b|c)\",\n            f\"(?P<{name}>a)?(?({name})(?=b)b|(?!b)c)\",\n        )\n        pattern, subject, flags = rng.choice(patterns), text_subject(rng, rng.choice((\"ab\", \"c\", \"abd\", \"ac\"))), rng.choice((0, I, M))\n    elif family == \"conditional-error-offsets\":\n        bad = rng.choice((\n"
    "            \"(?(missing)a|b)\", \"(?(0)a|b)\", \"(?(999)a|b)\", \"(?(1)a|b)\",\n            \"(?(name)a|b|c)\", \"(?(<x>)a|b)\", \"(?(=a)b|c)\", \"(?(?=a)b|c)\",\n            \"(?(a)\", \"(?(a)a|\", \"(?(a)a|b\", \"(?(a)a|b|c)\",\n        ))\n        pattern = rng.choice((\"\", word, \"(?:\", \"(?i:\")) + bad + rng.choice((\"\", \"x\", \")\"))\n        subject, flags = text_subject(rng, word), rng.choice((0, I, M, X))\n    elif family == \"scoped-inline-flags\":\n        local = rng.choice((\"i\", \"m\", \"s\", \"x\", \"a\", \"im\", \"is\", \"ms\", \"ix\", \"a-i\", \"i-m\", \"im-s\"))\n        core = rng.choice((\"a\", \"A\", \".\", \"[a-z]\", r\"\\w\", \"a b\", \"(?:a|A)\", \"(?-i:a)\"))\n        pattern = rng.choice((\"\", \"a?\", \"(?:b|)\")) + f\"(?{local}:{core})\" + rng.choice((\"\", \"A\", \"(?i:a)\", \"(?-i:A)\"))\n        subject, flags = text_subject(rng, rng.choice((\"a\", \"A\", \"ab\", \"a b\"))), rng.choice((0, I, M, S, X, A))\n    elif family == \"invalid-inline-flags\":\n"
    "        bad = rng.choice((\n            \"(?i)\", \"(?m)\", \"(?s)\", \"(?x)\", \"(?a)\", \"(?u)\", \"(?L)\", \"(?z)\",\n            \"(?i-)\", \"(?-i)\", \"(?i-a:a)\", \"(?a-u:a)\", \"(?au:a)\", \"(?i::a)\",\n            \"(?i\", \"(?i:\", \"(?-:a)\", \"(?i--m:a)\", \"(?u-a:a)\", \"(?L:a)\",\n        ))\n        pattern = rng.choice((\"a\", \"(?:a)\", word, \"a|\", \"\")) + bad + rng.choice((\"\", \"a\", word, \")\"))\n        subject, flags = text_subject(rng, word), rng.choice((0, I, M, X, A))\n    elif family == \"verbose-comments-and-escapes\":\n        token = rng.choice((\"a\", \"b\", word))\n        patterns = (\n            f\"(?x) {token} [ ] b\",\n            f\"(?x:{token} \\\\# b)\",\n"
    "            f\"(?x:{token} # comment {word}\\n b)\",\n            f\"(?x) (?P<{name}> {token} ) \\\\s* (?P={name})\",\n            f\"(?x) [a # b] + \\\\# ?\",\n            f\"(?x:{token} (?-x: ) b)\",\n            f\"(?x) (?: {token} | b ) {{ 1,2 }}\",\n            f\"(?x) {token} \\\\ \\\\# comment {word}\\n b\",\n        )\n        pattern, subject, flags = rng.choice(patterns), text_subject(rng, rng.choice((token, token + \" b\", token + token, \"a#b\"))), rng.choice((0, M, I))\n    elif family == \"bytes-named-backreferences\":\n        bn = name.encode(\"ascii\")\n        patterns = (\n            b\"(?P<\" + bn + b\">a)(?P=\" + bn + b\")\",\n"
    "            b\"(?P<\" + bn + b\">[a-z]+)(?P=\" + bn + b\")\",\n            b\"(?:(?P<\" + bn + b\">a)|b)(?(\" + bn + b\")a|b)\",\n            b\"(?=(?P<\" + bn + b\">a)){2}a\",\n            b\"(?P<\" + bn + b\">a)?(?(\" + bn + b\")b|c)\",\n            b\"(?i:(?P<\" + bn + b\">a))(?P=\" + bn + b\")\",\n            b\"(?P<\" + bn + b\">[\\\\x80-\\\\xff]+)(?P=\" + bn + b\")\",\n            b\"(a)(b)\\\\2\\\\1\",\n        )\n        pattern, subject, flags = rng.choice(patterns), byte_subject(rng, rng.choice((b\"a\", b\"aa\", b\"abba\", b\"\\x80\\x80\"))), rng.choice((0, I, M, S, A))\n    elif family == \"bytes-error-offsets\":\n        bad = rng.choice((\n            b\"(?P<\\xff>a)\", b\"(?P<\\x80>a)\", b\"(?P<>a)\", b\"(?P<1x>a)\",\n"
    "            b\"(?P<x>a)(?P<x>b)\", b\"(?P=x)\", b\"\\\\u1234\", b\"\\\\U00000041\",\n            b\"\\\\N{LATIN SMALL LETTER A}\", b\"\\\\x\", b\"\\\\x1\", b\"\\\\xGG\",\n            b\"[\\\\u1234]\", b\"(?u:a)\", b\"(?au:a)\", b\"(?P<ab\",\n        ))\n        pattern = rng.choice((b\"\", word.encode(\"ascii\"), b\"(?:\")) + bad + rng.choice((b\"\", b\"x\", b\")\"))\n        subject, flags = byte_subject(rng), rng.choice((0, I, M, S, A))\n    elif family == \"atomic-ordered-alternation\":\n        patterns = (\n            \"(?>a|ab)b\", \"(?>ab|a)b\", \"(?>a*)a\", \"(?>a+?)a\",\n            \"(?>(a)|(ab))b\", \"(?>(a|ab))b\", \"(?>a|)a\",\n            \"(?>(?=a)a|ab)b\", f\"(?>(?P<{name}>a)|ab)b\",\n            \"((?>a|ab)b|ab)\", \"(?>a(?>b|bc))c\", \"(?>(?:a|aa){1,3})a\",\n"
    "        )\n        pattern, subject, flags = rng.choice(patterns), text_subject(rng, rng.choice((\"a\", \"ab\", \"aab\", \"abb\", \"abc\"))), rng.choice((0, I, M, S))\n    elif family == \"possessive-repeat-captures\":\n        atom = rng.choice((\"a\", \"(?:a|aa)\", \"(a)\", \"(?:a?)\", \"[ab]\", \".\", r\"\\w\"))\n        quant = rng.choice((\"*+\", \"++\", \"?+\", \"{0,2}+\", \"{1,3}+\", \"{2}+\", \"{0}+\"))\n        pattern = rng.choice((\"\", \"(?:\", \"(\")) + atom + quant + rng.choice((\"a\", \"b\", \"\", r\"\\b\"))\n        if pattern.startswith(\"(?:\") or pattern.startswith(\"(\") and not pattern.startswith(\"(a)\"):\n            pattern += \")\"\n        subject, flags = text_subject(rng, rng.choice((\"a\", \"aa\", \"aaa\", \"ab\"))), rng.choice((0, I, M, S))\n    elif family == \"lookbehind-backreference-width\":\n        patterns = (\n            r\"(a)(?<=\\1)b\", r\"(ab)(?<=\\1)c\", r\"(a|b)(?<=\\1)c\",\n"
    "            r\"(a?)(?<=\\1)b\", r\"(a+)(?<=\\1)b\", r\"(?<=(a))\\1\",\n            f\"(?P<{name}>a)(?<=(?P={name}))b\",\n            f\"(?P<{name}>a+)(?<=(?P={name}))b\",\n            r\"(?<=(?:a|b))c\", r\"(?<=(?:a|bc))d\",\n            r\"(?<=a{2})b\", r\"(?<=a{1,2})b\",\n            r\"(?<!a{2})b\", r\"(?<!a{1,2})b\",\n        )\n        pattern, subject, flags = rng.choice(patterns), text_subject(rng, rng.choice((\"ab\", \"abc\", \"aac\", \"aab\", \"b\"))), rng.choice((0, I, M))\n    elif family == \"nullable-branch-captures\":\n        patterns = (\n            \"(|a)*\", \"(a?)*\", \"((a)?)*\", \"((a)|)*\", \"(?:|a)+?\",\n            \"((?=a)|a)*\", \"((?!z)|a)+\", \"(?:(a)?|b)*?\",\n"
    "            \"((a)?){0,3}\", \"((?:a|){1,2})*\", \"(?:(a)|(b)|)*\",\n            f\"(?:(?P<{name}>a)?)*?(?({name})b|c)\",\n            \"(?:a?)*+a\", \"(?:(a)|)*+\", \"(|(?:a|))*?\",\n        )\n        pattern, subject, flags = rng.choice(patterns), text_subject(rng, rng.choice((\"\", \"a\", \"aa\", \"ab\", \"c\"))), rng.choice((0, I, M))\n    elif family == \"escape-and-character-class-errors\":\n        bad = rng.choice((\n            \"\\\\\", r\"\\x\", r\"\\x1\", r\"\\xGG\", r\"\\u\", r\"\\u12\", r\"\\uGGGG\",\n            r\"\\U00110000\", r\"\\N{}\", r\"\\N{\", r\"\\N{NOT A CHARACTER}\",\n            r\"\\8\", r\"\\9\", r\"\\11\", r\"\\400\", r\"\\777\",\n            \"[\", \"[]\", \"[z-a]\", r\"[\\x]\", r\"[\\8]\", \"[a-\", \"[a--b]\",\n            \"*\", \"+\", \"?\", \"{1,2}*\", \"a**\", \"a++?\", \"a{2,1}\",\n"
    "            \"(?\", \"(?P<\", \"(?P=\", \"(?z)\", \"(?<=a+)\", \"(?<!a*)\",\n        ))\n        pattern = rng.choice((\"\", word, \"(?:\")) + bad + rng.choice((\"\", \"x\", \")\"))\n        subject, flags = text_subject(rng, word), rng.choice((0, I, M, S, X, A))\n    else:\n        raise AssertionError(family)\n    return {\n        \"id\": f\"{family}:{index:05d}\",\n        \"family\": family,\n        \"pattern\": encode_domain(pattern),\n        \"subject\": encode_domain(subject),\n        \"flags\": int(flags),\n"
    "    }\n\n\ndef observe(module, case):\n    pattern = decode_domain(case[\"pattern\"])\n    subject = decode_domain(case[\"subject\"])\n    flags = case[\"flags\"]\n    with warnings.catch_warnings(record=True) as caught:\n        warnings.simplefilter(\"always\")\n        try:\n            compiled = module.compile(pattern, flags)\n        except Exception as error:\n"
    "            return {\n                \"compile\": capture_error(error),\n                \"warnings\": [\n                    {\"category\": item.category.__name__, \"message\": str(item.message)}\n                    for item in caught\n                ],\n            }\n    metadata = {\n        \"pattern\": normalise(compiled.pattern),\n        \"flags\": int(compiled.flags),\n        \"groups\": compiled.groups,\n        \"groupindex\": normalise(dict(compiled.groupindex)),\n"
    "    }\n    observations = {\n        \"compile\": {\"status\": \"ok\", \"value\": metadata},\n        \"warnings\": [\n            {\"category\": item.category.__name__, \"message\": str(item.message)}\n            for item in caught\n        ],\n        \"operations\": {},\n    }\n    length = len(subject)\n    windows = tuple(dict.fromkeys(((0, length), (min(1, length), length), (0, max(0, length - 1)), (length, length))))\n    for pos, endpos in windows:\n"
    "        for operation in (\"search\", \"match\", \"fullmatch\"):\n            label = f\"{operation}:{pos}:{endpos}\"\n            observations[\"operations\"][label] = attempt(\n                lambda operation=operation, pos=pos, endpos=endpos: match_snapshot(\n                    getattr(compiled, operation)(subject, pos, endpos)\n                )\n            )\n    replacement = rb\"<\\g<0>>\" if isinstance(pattern, bytes) else r\"<\\g<0>>\"\n    collection_ops = (\n        (\"findall\", lambda: compiled.findall(subject)),\n        (\"finditer\", lambda: [match_snapshot(item) for item in itertools.islice(compiled.finditer(subject), 129)]),\n        (\"split:2\", lambda: compiled.split(subject, 2)),\n"
    "        (\"sub:2\", lambda: compiled.sub(replacement, subject, 2)),\n        (\"subn:2\", lambda: compiled.subn(replacement, subject, 2)),\n    )\n    for label, action in collection_ops:\n        observations[\"operations\"][label] = attempt(action)\n    return observations\n\n\ndef directory_arg(value):\n    path = pathlib.Path(value).resolve()\n    if path.parent != pathlib.Path(\"/tmp\") or not path.name.startswith(\"rebar-rust-parser-grammar-\"):\n        raise argparse.ArgumentTypeError(\"evidence directory must be a specifically named immediate /tmp child\")\n"
    "    return path\n\n\ndef read_cases(path, limit=None):\n    cases = []\n    with path.open(\"r\", encoding=\"utf-8\") as handle:\n        for line in handle:\n            if line.strip():\n                cases.append(json.loads(line))\n                if limit is not None and len(cases) >= limit:\n                    break\n    return cases\n"
    "\n\ndef write_json(path, payload):\n    with path.open(\"w\", encoding=\"utf-8\", newline=\"\\n\") as handle:\n        handle.write(canonical(payload))\n        handle.write(\"\\n\")\n\n\ndef command_generate(args):\n    assert_pinned()\n    output = args.directory\n    output.mkdir(mode=0o700, parents=False, exist_ok=False)\n"
    "    rng = random.Random(SEED)\n    cases = []\n    seen = set()\n    for family in FAMILIES:\n        index = 0\n        attempts = 0\n        while index < args.per_family:\n            attempts += 1\n            if attempts > args.per_family * 100:\n                raise RuntimeError(f\"could not generate distinct cases for {family}\")\n            case = make_case(family, rng, index)\n            semantic_key = canonical((family, case[\"pattern\"], case[\"subject\"], case[\"flags\"]))\n"
    "            if semantic_key in seen:\n                continue\n            seen.add(semantic_key)\n            cases.append(case)\n            index += 1\n    fixture_path = output / \"cases.jsonl\"\n    with fixture_path.open(\"w\", encoding=\"utf-8\", newline=\"\\n\") as handle:\n        for case in cases:\n            handle.write(canonical(case))\n            handle.write(\"\\n\")\n    manifest = {\n        \"schema\": SCHEMA,\n"
    "        \"seed\": SEED,\n        \"python\": platform.python_version(),\n        \"python_executable\": sys.executable,\n        \"cases\": len(cases),\n        \"cases_per_family\": args.per_family,\n        \"families\": list(FAMILIES),\n        \"fixture_sha256\": digest_path(fixture_path),\n        \"source_hashes\": source_hashes(),\n        \"candidates\": list(CANDIDATES),\n        \"performance_fixtures_read\": 0,\n        \"holdout_cases_read\": 0,\n        \"external_regex_packages\": 0,\n"
    "    }\n    write_json(output / \"manifest.json\", manifest)\n    print(canonical({\"phase\": \"generated\", \"directory\": str(output), **manifest}), flush=True)\n\n\ndef checked_manifest(directory):\n    with (directory / \"manifest.json\").open(\"r\", encoding=\"utf-8\") as handle:\n        manifest = json.load(handle)\n    if manifest.get(\"schema\") != SCHEMA:\n        raise RuntimeError(\"incorrect evidence schema\")\n    if digest_path(directory / \"cases.jsonl\") != manifest.get(\"fixture_sha256\"):\n        raise RuntimeError(\"frozen grammar fixture changed\")\n"
    "    return manifest\n\n\ndef assert_unchanged(manifest):\n    actual = source_hashes()\n    if actual != manifest[\"source_hashes\"]:\n        names = sorted(set(actual) | set(manifest[\"source_hashes\"]))\n        changes = {\n            name: {\"frozen\": manifest[\"source_hashes\"].get(name), \"actual\": actual.get(name)}\n            for name in names\n            if manifest[\"source_hashes\"].get(name) != actual.get(name)\n        }\n"
    "        raise RuntimeError(\"frozen candidate baseline changed: \" + canonical(changes))\n\n\ndef command_worker(args):\n    assert_pinned()\n    manifest = checked_manifest(args.directory)\n    if args.module != \"re\":\n        assert_unchanged(manifest)\n        if args.module not in CANDIDATES:\n            raise RuntimeError(f\"unapproved candidate: {args.module}\")\n    if str(ROOT) not in sys.path:\n        sys.path.insert(0, str(ROOT))\n"
    "    module = importlib.import_module(args.module)\n    for line in sys.stdin:\n        if not line.strip():\n            continue\n        case = json.loads(line)\n        result = {\"id\": case[\"id\"], \"family\": case[\"family\"], \"observation\": observe(module, case)}\n        print(canonical(result), flush=True)\n\n\ndef run_one_batch(directory, module, cases, timeout):\n    payload = \"\".join(canonical(case) + \"\\n\" for case in cases)\n    command = [sys.executable, str(pathlib.Path(__file__).resolve()), \"worker\", \"--directory\", str(directory), \"--module\", module]\n"
    "    try:\n        result = subprocess.run(\n            command,\n            input=payload,\n            text=True,\n            capture_output=True,\n            cwd=str(ROOT),\n            timeout=timeout,\n            check=False,\n        )\n    except subprocess.TimeoutExpired as error:\n        return {\"status\": \"timeout\", \"cases\": cases, \"timeout_seconds\": timeout, \"stderr\": normalise(error.stderr)}\n"
    "    if result.returncode != 0:\n        return {\"status\": \"crash\", \"cases\": cases, \"returncode\": result.returncode, \"stderr\": result.stderr[-12000:], \"stdout\": result.stdout[-12000:]}\n    try:\n        rows = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]\n    except (ValueError, TypeError) as error:\n        return {\"status\": \"malformed-output\", \"cases\": cases, \"error\": str(error), \"stdout\": result.stdout[-12000:], \"stderr\": result.stderr[-12000:]}\n    if len(rows) != len(cases) or any(row[\"id\"] != case[\"id\"] for row, case in zip(rows, cases, strict=True)):\n        return {\"status\": \"incomplete-output\", \"cases\": cases, \"observed_rows\": len(rows), \"stdout\": result.stdout[-12000:], \"stderr\": result.stderr[-12000:]}\n    return {\"status\": \"ok\", \"rows\": rows}\n\n\ndef isolated_rows(directory, module, cases, timeout):\n"
    "    batch = run_one_batch(directory, module, cases, timeout)\n    if batch[\"status\"] == \"ok\":\n        return batch[\"rows\"]\n    if len(cases) > 1:\n        middle = len(cases) // 2\n        return (\n            isolated_rows(directory, module, cases[:middle], timeout)\n            + isolated_rows(directory, module, cases[middle:], timeout)\n        )\n    case = cases[0]\n    failure = {key: value for key, value in batch.items() if key != \"cases\"}\n    return [{\"id\": case[\"id\"], \"family\": case[\"family\"], \"observation\": {\"worker_failure\": failure}}]\n"
    "\n\ndef write_run(directory, module, cases, path, batch_size, timeout):\n    counts = collections.Counter()\n    digest = hashlib.sha256()\n    with path.open(\"w\", encoding=\"utf-8\", newline=\"\\n\") as handle:\n        for start in range(0, len(cases), batch_size):\n            chunk = cases[start:start + batch_size]\n            rows = isolated_rows(directory, module, chunk, timeout)\n            for row in rows:\n                encoded = canonical(row) + \"\\n\"\n                handle.write(encoded)\n"
    "                digest.update(encoded.encode(\"ascii\"))\n                counts[row[\"family\"]] += 1\n            if start == 0 or (start + len(chunk)) % max(batch_size, 2048) == 0 or start + len(chunk) == len(cases):\n                print(canonical({\"phase\": \"progress\", \"module\": module, \"completed\": start + len(chunk), \"total\": len(cases)}), flush=True)\n    return {\"rows\": len(cases), \"sha256\": digest.hexdigest(), \"family_counts\": dict(sorted(counts.items()))}\n\n\ndef command_self(args):\n    assert_pinned()\n    manifest = checked_manifest(args.directory)\n    assert_unchanged(manifest)\n    cases = read_cases(args.directory / \"cases.jsonl\", args.limit)\n"
    "    first = write_run(args.directory, \"re\", cases, args.directory / \"oracle-a.jsonl\", args.batch_size, args.timeout)\n    second = write_run(args.directory, \"re\", cases, args.directory / \"oracle-b.jsonl\", args.batch_size, args.timeout)\n    errors = []\n    valid = 0\n    invalid = 0\n    with (args.directory / \"oracle-a.jsonl\").open(\"r\", encoding=\"utf-8\") as lhs, (args.directory / \"oracle-b.jsonl\").open(\"r\", encoding=\"utf-8\") as rhs:\n        for number, (left, right) in enumerate(itertools.zip_longest(lhs, rhs), 1):\n            if left != right:\n                errors.append({\"line\": number, \"first\": None if left is None else json.loads(left), \"second\": None if right is None else json.loads(right)})\n            if left is not None:\n                row = json.loads(left)\n                if \"worker_failure\" in row[\"observation\"]:\n"
    "                    errors.append({\"line\": number, \"oracle_worker_failure\": row})\n                elif row[\"observation\"][\"compile\"][\"status\"] == \"ok\":\n                    valid += 1\n                else:\n                    invalid += 1\n    report = {\n        \"schema\": SCHEMA + \"-self-oracle\",\n        \"python\": platform.python_version(),\n        \"seed\": SEED,\n        \"fixture_sha256\": manifest[\"fixture_sha256\"],\n        \"cases\": len(cases),\n        \"valid_grammars\": valid,\n"
    "        \"invalid_grammars_retained\": invalid,\n        \"pass_a\": first,\n        \"pass_b\": second,\n        \"self_oracle_failures\": len(errors),\n        \"failures\": errors,\n    }\n    write_json(args.directory / \"self-oracle.json\", report)\n    assert_unchanged(manifest)\n    print(canonical({key: value for key, value in report.items() if key != \"failures\"}), flush=True)\n    if errors:\n        raise SystemExit(2)\n\n"
    "\ndef command_check(args):\n    assert_pinned()\n    manifest = checked_manifest(args.directory)\n    assert_unchanged(manifest)\n    if args.module not in CANDIDATES:\n        raise RuntimeError(f\"unapproved candidate: {args.module}\")\n    self_report_path = args.directory / \"self-oracle.json\"\n    if not self_report_path.is_file():\n        raise RuntimeError(\"stdlib-vs-stdlib self-oracle must pass before a candidate runs\")\n    with self_report_path.open(\"r\", encoding=\"utf-8\") as handle:\n        self_report = json.load(handle)\n"
    "    if self_report.get(\"self_oracle_failures\") != 0 or self_report.get(\"fixture_sha256\") != manifest[\"fixture_sha256\"]:\n        raise RuntimeError(\"stdlib-vs-stdlib self-oracle failed or fixture changed\")\n    cases = read_cases(args.directory / \"cases.jsonl\", args.limit)\n    if len(cases) > self_report[\"cases\"]:\n        raise RuntimeError(\"candidate coverage exceeds frozen self-oracle coverage\")\n    slug = args.module.rsplit(\".\", 1)[1]\n    actual_path = args.directory / (slug + \"-actual.jsonl\")\n    actual_summary = write_run(args.directory, args.module, cases, actual_path, args.batch_size, args.timeout)\n    mismatch_path = args.directory / (slug + \"-mismatches.jsonl\")\n    differences = collections.Counter()\n    mismatches = 0\n    crashes = 0\n"
    "    timeouts = 0\n    compile_valid_rejected = 0\n    compile_invalid_accepted = 0\n    error_detail_mismatches = 0\n    with (args.directory / \"oracle-a.jsonl\").open(\"r\", encoding=\"utf-8\") as expected_file, actual_path.open(\"r\", encoding=\"utf-8\") as actual_file, mismatch_path.open(\"w\", encoding=\"utf-8\", newline=\"\\n\") as evidence:\n        for index, (expected_line, actual_line) in enumerate(itertools.zip_longest(expected_file, actual_file)):\n            if index == len(cases):\n                break\n            if expected_line is None or actual_line is None:\n                raise RuntimeError(\"candidate or oracle denominator changed\")\n            expected = json.loads(expected_line)\n            actual = json.loads(actual_line)\n"
    "            case = cases[index]\n            if expected[\"id\"] != case[\"id\"] or actual[\"id\"] != case[\"id\"]:\n                raise RuntimeError(\"candidate or oracle case order changed\")\n            if expected[\"observation\"] == actual[\"observation\"]:\n                continue\n            mismatches += 1\n            differences[case[\"family\"]] += 1\n            candidate_observation = actual[\"observation\"]\n            if \"worker_failure\" in candidate_observation:\n                status = candidate_observation[\"worker_failure\"][\"status\"]\n                if status == \"timeout\":\n                    timeouts += 1\n"
    "                else:\n                    crashes += 1\n                mismatch_kind = \"worker-\" + status\n            else:\n                expected_compile = expected[\"observation\"][\"compile\"]\n                actual_compile = candidate_observation[\"compile\"]\n                if expected_compile[\"status\"] == \"ok\" and actual_compile[\"status\"] == \"error\":\n                    compile_valid_rejected += 1\n                    mismatch_kind = \"valid-grammar-rejected\"\n                elif expected_compile[\"status\"] == \"error\" and actual_compile[\"status\"] == \"ok\":\n                    compile_invalid_accepted += 1\n                    mismatch_kind = \"invalid-grammar-accepted\"\n"
    "                elif expected_compile[\"status\"] == \"error\" and actual_compile[\"status\"] == \"error\":\n                    error_detail_mismatches += 1\n                    mismatch_kind = \"error-message-or-offset\"\n                elif expected[\"observation\"].get(\"warnings\") != actual[\"observation\"].get(\"warnings\"):\n                    mismatch_kind = \"compile-warning\"\n                elif expected_compile != actual_compile:\n                    mismatch_kind = \"compiled-pattern-metadata\"\n                else:\n                    mismatch_kind = \"matching-or-collection-result\"\n            evidence.write(canonical({\n                \"case\": case,\n                \"candidate\": args.module,\n"
    "                \"mismatch_kind\": mismatch_kind,\n                \"expected\": expected[\"observation\"],\n                \"actual\": actual[\"observation\"],\n            }))\n            evidence.write(\"\\n\")\n    assert_unchanged(manifest)\n    report = {\n        \"schema\": SCHEMA + \"-candidate-report\",\n        \"module\": args.module,\n        \"python\": platform.python_version(),\n        \"seed\": SEED,\n        \"fixture_sha256\": manifest[\"fixture_sha256\"],\n"
    "        \"source_hashes\": manifest[\"source_hashes\"],\n        \"cases\": len(cases),\n        \"matches\": len(cases) - mismatches,\n        \"mismatches\": mismatches,\n        \"valid_grammars_rejected\": compile_valid_rejected,\n        \"invalid_grammars_accepted\": compile_invalid_accepted,\n        \"error_message_or_offset_mismatches\": error_detail_mismatches,\n        \"crashes\": crashes,\n        \"timeouts\": timeouts,\n        \"mismatches_by_family\": dict(sorted(differences.items())),\n        \"actual\": actual_summary,\n        \"mismatch_evidence\": str(mismatch_path),\n"
    "        \"mismatch_evidence_sha256\": digest_path(mismatch_path),\n        \"performance_fixtures_read\": 0,\n        \"holdout_cases_read\": 0,\n        \"external_regex_packages\": 0,\n    }\n    write_json(args.directory / (slug + \"-report.json\"), report)\n    print(canonical(report), flush=True)\n\n\ndef command_summarize(args):\n    manifest = checked_manifest(args.directory)\n    with (args.directory / \"self-oracle.json\").open(\"r\", encoding=\"utf-8\") as handle:\n"
    "        self_oracle = json.load(handle)\n    reports = []\n    for module in CANDIDATES:\n        path = args.directory / (module.rsplit(\".\", 1)[1] + \"-report.json\")\n        if path.is_file():\n            with path.open(\"r\", encoding=\"utf-8\") as handle:\n                reports.append(json.load(handle))\n    summary = {\n        \"schema\": SCHEMA + \"-summary\",\n        \"directory\": str(args.directory),\n        \"python\": platform.python_version(),\n        \"seed\": SEED,\n"
    "        \"fixture_sha256\": manifest[\"fixture_sha256\"],\n        \"cases\": manifest[\"cases\"],\n        \"families\": manifest[\"families\"],\n        \"self_oracle_cases\": self_oracle[\"cases\"],\n        \"self_oracle_failures\": self_oracle[\"self_oracle_failures\"],\n        \"valid_grammars\": self_oracle[\"valid_grammars\"],\n        \"invalid_grammars_retained\": self_oracle[\"invalid_grammars_retained\"],\n        \"candidates_measured\": len(reports),\n        \"candidate_reports\": reports,\n        \"performance_fixtures_read\": 0,\n        \"holdout_cases_read\": 0,\n        \"external_regex_packages\": 0,\n"
    "    }\n    write_json(args.directory / \"summary.json\", summary)\n    print(canonical(summary), flush=True)\n\n\ndef build_parser():\n    parser = argparse.ArgumentParser(description=__doc__)\n    commands = parser.add_subparsers(dest=\"command\", required=True)\n    generate = commands.add_parser(\"generate\")\n    generate.add_argument(\"--directory\", required=True, type=directory_arg)\n    generate.add_argument(\"--per-family\", type=int, default=1280)\n    generate.set_defaults(handler=command_generate)\n"
    "    for name, handler in ((\"self\", command_self), (\"check\", command_check)):\n        command = commands.add_parser(name)\n        command.add_argument(\"--directory\", required=True, type=directory_arg)\n        command.add_argument(\"--batch-size\", type=int, default=128)\n        command.add_argument(\"--timeout\", type=float, default=15.0)\n        command.add_argument(\"--limit\", type=int)\n        if name == \"check\":\n            command.add_argument(\"--module\", required=True, choices=CANDIDATES)\n        command.set_defaults(handler=handler)\n    worker = commands.add_parser(\"worker\")\n    worker.add_argument(\"--directory\", required=True, type=directory_arg)\n    worker.add_argument(\"--module\", required=True, choices=(\"re\",) + CANDIDATES)\n"
    "    worker.set_defaults(handler=command_worker)\n    summarize = commands.add_parser(\"summarize\")\n    summarize.add_argument(\"--directory\", required=True, type=directory_arg)\n    summarize.set_defaults(handler=command_summarize)\n    return parser\n\n\ndef main():\n    parser = build_parser()\n    args = parser.parse_args()\n    if getattr(args, \"per_family\", 1) <= 0:\n        parser.error(\"--per-family must be positive\")\n"
    "    if getattr(args, \"batch_size\", 1) <= 0:\n        parser.error(\"--batch-size must be positive\")\n    limit = getattr(args, \"limit\", None)\n    if limit is not None and limit <= 0:\n        parser.error(\"--limit must be positive\")\n    args.handler(args)\n\n\nif __name__ == \"__main__\":\n    main()\n"
)

FULL_PLANE_DIGESTS = {
    "unicode-categories":
        "c6bb3b50278d370bd288a040d07976730f92fe4475c947a7ac8e4158cdda6ec5",
    "ascii-categories":
        "9888738c9f6e04a0b5e86300a648cf042531945a2761e7a666c2a407b5d6a339",
    "unicode-ignorecase-ranges":
        "b9394ae400bc6c32867be06a02363c740cc670bbcfd89668949a422ad93d8f1a",
    "ascii-ignorecase-ranges":
        "5084555e7d9ccfbbc9db1ea1e85b1d28820120a085739322159fe3bf79a7a554",
}

CATEGORY_PARTITION = (
    r"(?P<digit>\d)|(?P<space>\s)|(?P<word>\w)|(?P<other>[\s\S])"
)
CASE_PARTITION = (
    r"(?P<latin>[A-Za-z])"
    r"|(?P<latin1>[\xc0-\xde])"
    r"|(?P<greek>[\u0391-\u03a9])"
    r"|(?P<cyrillic>[\u0400-\u042f])"
    r"|(?P<deseret>[\U00010400-\U00010427])"
    r"|(?P<other>[\s\S])"
)

UNICODE_BOUNDARIES = (
    0x0000, 0x0001, 0x0008, 0x0009, 0x000A, 0x000B, 0x000C,
    0x000D, 0x001B, 0x001C, 0x001D, 0x001E, 0x001F, 0x0020,
    0x007E, 0x007F, 0x0080, 0x0084, 0x0085, 0x009F, 0x00A0,
    0x00AA, 0x00B5, 0x00BA, 0x00DF, 0x00FF, 0x0100, 0x0130,
    0x0131, 0x017F, 0x0345, 0x0378, 0x0390, 0x03A3, 0x03B0,
    0x03C2, 0x03C3, 0x03D0, 0x03F4, 0x061C, 0x1680, 0x180E,
    0x1C80, 0x1C88, 0x1E9B, 0x1E9E, 0x1FBE, 0x1FD3, 0x1FE3,
    0x2000, 0x200B, 0x200C, 0x200D, 0x2028, 0x2029, 0x202F,
    0x205F, 0x2060, 0x2126, 0x212A, 0x212B, 0x3000, 0xD7FF,
    0xD800, 0xDBFF, 0xDC00, 0xDFFF, 0xE000, 0xFDD0, 0xFB05,
    0xFB06, 0xFFFE, 0xFFFF, 0x10000, 0x10400, 0x10427,
    0x10428, 0x1044F, 0x1F600, 0x1F64F, 0x10FFFE, 0x10FFFF,
)

CASE_EQUIVALENCES = (
    (0x0049, 0x0069, 0x0130, 0x0131),
    (0x004B, 0x006B, 0x212A),
    (0x0053, 0x0073, 0x017F),
    (0x00B5, 0x039C, 0x03BC),
    (0x00DF, 0x1E9E),
    (0x0345, 0x0399, 0x03B9, 0x1FBE),
    (0x0390, 0x1FD3),
    (0x03B0, 0x1FE3),
    (0x0392, 0x03B2, 0x03D0),
    (0x0395, 0x03B5, 0x03F5),
    (0x0398, 0x03B8, 0x03D1, 0x03F4),
    (0x039A, 0x03BA, 0x03F0),
    (0x03A0, 0x03C0, 0x03D6),
    (0x03A1, 0x03C1, 0x03F1),
    (0x03A3, 0x03C2, 0x03C3),
    (0x03A6, 0x03C6, 0x03D5),
    (0x0412, 0x0432, 0x1C80),
    (0x0414, 0x0434, 0x1C81),
    (0x041E, 0x043E, 0x1C82),
    (0x0421, 0x0441, 0x1C83),
    (0x0422, 0x0442, 0x1C84, 0x1C85),
    (0x042A, 0x044A, 0x1C86),
    (0x0462, 0x0463, 0x1C87),
    (0xA64A, 0xA64B, 0x1C88),
    (0x1E60, 0x1E61, 0x1E9B),
    (0xFB05, 0xFB06),
)


class TextSubclass(str):
    pass


class BytesSubclass(bytes):
    pass


def portable_json_report(value):
    """Losslessly encode lone surrogates without changing oracle observations."""
    if isinstance(value, str):
        if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
            return {
                "kind": "str",
                "surrogatepass_utf8_hex": value.encode(
                    "utf-8", "surrogatepass"
                ).hex(),
            }
        return value
    if isinstance(value, (list, tuple)):
        return [portable_json_report(item) for item in value]
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if isinstance(key, str) and any(
                0xD800 <= ord(character) <= 0xDFFF for character in key
            ):
                raise ValueError(
                    "frozen edge reports cannot encode surrogate mapping keys"
                )
            result[key] = portable_json_report(item)
        return result
    return value


def normalise(value):
    if value is None or isinstance(value, (bool, str)):
        return value
    if isinstance(value, int):
        return int(value)
    if isinstance(value, bytes):
        return {"kind": type(value).__name__, "hex": bytes(value).hex()}
    if isinstance(value, bytearray):
        return {"kind": type(value).__name__, "hex": bytes(value).hex()}
    if isinstance(value, memoryview):
        return {
            "kind": "memoryview",
            "hex": value.tobytes().hex(),
            "format": value.format,
            "contiguous": value.contiguous,
        }
    if isinstance(value, tuple):
        return {"tuple": [normalise(item) for item in value]}
    if isinstance(value, list):
        return [normalise(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): normalise(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    return {"kind": type(value).__name__, "repr": repr(value)}


def match_snapshot(match):
    if match is None:
        return None
    return {
        "span": normalise(match.span()),
        "regs": normalise(match.regs),
        "group0": normalise(match.group(0)),
        "groups": normalise(match.groups()),
        "groups_default": normalise(match.groups("!" if isinstance(match.string, str) else b"!")),
        "groupdict": normalise(match.groupdict()),
        "lastindex": match.lastindex,
        "lastgroup": match.lastgroup,
        "pos": match.pos,
        "endpos": match.endpos,
    }


def attempted(action):
    try:
        return {"status": "ok", "value": normalise(action())}
    except Exception as error:
        result = {
            "status": "error",
            "type": type(error).__name__,
            "args": normalise(error.args),
        }
        if hasattr(error, "msg") and hasattr(error, "pos"):
            result["pattern_error"] = {
                key: normalise(getattr(error, key, None))
                for key in ("msg", "pattern", "pos", "lineno", "colno")
            }
        return result


def pattern_snapshot(pattern):
    return {
        "pattern": normalise(pattern.pattern),
        "flags": int(pattern.flags),
        "groups": pattern.groups,
        "groupindex": normalise(dict(pattern.groupindex)),
    }


class DifferentialGate:
    def __init__(self, candidate, seed):
        self.candidate = candidate
        self.seed = seed
        self.failures = []
        self.counts = collections.Counter()
        self.expected_digest = hashlib.sha256()
        self.actual_digest = hashlib.sha256()
        self.membership = []
        self.embedded_oracles = []

    def record(self, category, label, expected, actual, **details):
        self.counts[category] += 1
        for digest, value in (
            (self.expected_digest, expected),
            (self.actual_digest, actual),
        ):
            digest.update(
                json.dumps(
                    (category, label, value),
                    ensure_ascii=True,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("ascii")
            )
            digest.update(b"\n")
        if expected != actual:
            self.failures.append(
                {
                    "category": category,
                    "label": label,
                    "details": normalise(details),
                    "expected": expected,
                    "actual": actual,
                }
            )

    def compare(self, category, label, expected_action, actual_action, **details):
        self.record(
            category,
            label,
            attempted(expected_action),
            attempted(actual_action),
            **details,
        )

    def compile_pair(self, category, label, pattern, flags=0):
        compiled = []
        observed = []
        for module in (re, self.candidate):
            try:
                item = module.compile(pattern, flags)
                compiled.append(item)
                observed.append({"status": "ok", "value": pattern_snapshot(item)})
            except Exception as error:
                compiled.append(None)
                observed.append(attempted(lambda error=error: raise_error(error)))
        self.record(
            category,
            label + ":compile",
            observed[0],
            observed[1],
            pattern=pattern,
            flags=int(flags),
        )
        if compiled[0] is None or compiled[1] is None:
            return None
        return compiled[0], compiled[1]


def raise_error(error):
    raise error


def scanner_values(pattern, subject, pos, endpos, mode):
    scanner = pattern.scanner(subject, pos, endpos)
    if mode == "search":
        values = []
        for _ in range(2 * len(subject) + 12):
            match = scanner.search()
            values.append(match_snapshot(match))
            if match is None:
                values.append(match_snapshot(scanner.search()))
                values.append(match_snapshot(scanner.search()))
                return values
        raise RuntimeError("search scanner did not terminate")
    if mode == "match":
        values = []
        for _ in range(2 * len(subject) + 12):
            match = scanner.match()
            values.append(match_snapshot(match))
            if match is None:
                values.append(match_snapshot(scanner.match()))
                values.append(match_snapshot(scanner.match()))
                return values
        raise RuntimeError("match scanner did not terminate")
    methods = (
        "search", "match", "search", "search", "match", "search",
        "match", "match", "search", "search", "match", "search",
    )
    return [match_snapshot(getattr(scanner, method)()) for method in methods]


def callback_result(pattern, subject, operation, count):
    trace = []

    def replacement(match):
        nested = pattern.search(match.group(0))
        trace.append({"outer": match_snapshot(match), "nested": match_snapshot(nested)})
        return b"#" if not isinstance(match.string, str) else "#"

    result = getattr(pattern, operation)(replacement, subject, count=count)
    return {"result": normalise(result), "trace": trace}


def windows(length):
    options = (
        (0, length),
        (0, 0),
        (min(1, length), length),
        (-2, length + 2),
        (length, length),
        (length + 1, length + 3),
        (min(3, length), min(1, length)),
    )
    return tuple(dict.fromkeys(options))


def exercise_pattern(gate, category, label, pattern, subject, flags=0, *, collections_enabled=True):
    pair = gate.compile_pair(category, label, pattern, flags)
    if pair is None:
        return
    expected_pattern, actual_pattern = pair
    subject_details = {"pattern": pattern, "subject": subject, "flags": int(flags)}

    for pos, endpos in windows(len(subject)):
        window = {**subject_details, "pos": pos, "endpos": endpos}
        for operation in ("search", "match", "fullmatch"):
            gate.compare(
                category,
                f"{label}:{operation}:{pos}:{endpos}",
                lambda item=expected_pattern, name=operation: match_snapshot(
                    getattr(item, name)(subject, pos, endpos)
                ),
                lambda item=actual_pattern, name=operation: match_snapshot(
                    getattr(item, name)(subject, pos, endpos)
                ),
                **window,
            )
        gate.compare(
            category,
            f"{label}:findall:{pos}:{endpos}",
            lambda: expected_pattern.findall(subject, pos, endpos),
            lambda: actual_pattern.findall(subject, pos, endpos),
            **window,
        )
        gate.compare(
            category,
            f"{label}:finditer:{pos}:{endpos}",
            lambda: [match_snapshot(match) for match in expected_pattern.finditer(subject, pos, endpos)],
            lambda: [match_snapshot(match) for match in actual_pattern.finditer(subject, pos, endpos)],
            **window,
        )
        for mode in ("search", "match", "mixed"):
            gate.compare(
                category,
                f"{label}:scanner-{mode}:{pos}:{endpos}",
                lambda mode=mode: scanner_values(expected_pattern, subject, pos, endpos, mode),
                lambda mode=mode: scanner_values(actual_pattern, subject, pos, endpos, mode),
                **window,
            )

    if not collections_enabled:
        return

    template = rb"<\g<0>>" if not isinstance(pattern, str) else r"<\g<0>>"
    for count in (0, 1, 2, -1):
        gate.compare(
            category,
            f"{label}:split:{count}",
            lambda count=count: expected_pattern.split(subject, maxsplit=count),
            lambda count=count: actual_pattern.split(subject, maxsplit=count),
            **subject_details,
            count=count,
        )
        for operation in ("sub", "subn"):
            gate.compare(
                category,
                f"{label}:{operation}:{count}",
                lambda operation=operation, count=count: getattr(expected_pattern, operation)(
                    template, subject, count=count
                ),
                lambda operation=operation, count=count: getattr(actual_pattern, operation)(
                    template, subject, count=count
                ),
                **subject_details,
                count=count,
            )

    for operation in ("sub", "subn"):
        for count in (0, 2):
            gate.compare(
                category,
                f"{label}:{operation}:reentrant:{count}",
                lambda operation=operation, count=count: callback_result(
                    expected_pattern, subject, operation, count
                ),
                lambda operation=operation, count=count: callback_result(
                    actual_pattern, subject, operation, count
                ),
                **subject_details,
                count=count,
            )


def unicode_membership(gate, stride):
    codepoints = sorted(set(range(0, FULL_PLANE, stride)) | set(UNICODE_BOUNDARIES))
    partitions = (
        ("unicode-categories", CATEGORY_PARTITION, 0),
        ("ascii-categories", CATEGORY_PARTITION, re.ASCII),
        ("unicode-ignorecase-ranges", CASE_PARTITION, re.IGNORECASE),
        ("ascii-ignorecase-ranges", CASE_PARTITION, re.ASCII | re.IGNORECASE),
    )
    for label, pattern, flags in partitions:
        pair = gate.compile_pair("unicode-membership", label, pattern, flags)
        if pair is None:
            continue
        expected_pattern, actual_pattern = pair
        expected_digest = hashlib.sha256()
        actual_digest = hashlib.sha256()
        for codepoint in codepoints:
            subject = chr(codepoint)
            try:
                expected_match = expected_pattern.fullmatch(subject)
                expected = expected_match.lastindex if expected_match is not None else 0
                actual_match = actual_pattern.fullmatch(subject)
                actual = actual_match.lastindex if actual_match is not None else 0
            except Exception:
                gate.compare(
                    "unicode-membership",
                    f"{label}:U+{codepoint:06X}",
                    lambda subject=subject: match_snapshot(expected_pattern.fullmatch(subject)),
                    lambda subject=subject: match_snapshot(actual_pattern.fullmatch(subject)),
                    codepoint=codepoint,
                    pattern=pattern,
                    flags=int(flags),
                )
                actual_digest.update(b"\xff")
                expected_digest.update(b"\xff")
                continue
            expected_digest.update(bytes((expected,)))
            actual_digest.update(bytes((actual,)))
            gate.counts["unicode-membership"] += 1
            if expected != actual:
                gate.failures.append(
                    {
                        "category": "unicode-membership",
                        "label": f"{label}:U+{codepoint:06X}",
                        "details": {
                            "codepoint": codepoint,
                            "unicode": f"U+{codepoint:04X}",
                            "pattern": pattern,
                            "flags": int(flags),
                        },
                        "expected": expected,
                        "actual": actual,
                    }
                )
        expected_hex = expected_digest.hexdigest()
        actual_hex = actual_digest.hexdigest()
        gate.expected_digest.update(label.encode("ascii") + b":" + expected_digest.digest())
        gate.actual_digest.update(label.encode("ascii") + b":" + actual_digest.digest())
        member = {
            "partition": label,
            "stride": stride,
            "codepoints": len(codepoints),
            "expected_sha256": expected_hex,
            "actual_sha256": actual_hex,
            "matches_pinned_full_plane": (
                expected_hex == FULL_PLANE_DIGESTS[label] if stride == 1 else None
            ),
        }
        gate.membership.append(member)
        if stride == 1 and expected_hex != FULL_PLANE_DIGESTS[label]:
            gate.failures.append(
                {
                    "category": "unicode-oracle-self-check",
                    "label": label,
                    "details": {"codepoints": len(codepoints)},
                    "expected": FULL_PLANE_DIGESTS[label],
                    "actual": expected_hex,
                }
            )
        print(json.dumps(member, sort_keys=True), flush=True)


def exhaustive_bytes(gate):
    patterns = (
        rb"\d", rb"\D", rb"\s", rb"\S", rb"\w", rb"\W", rb".",
        rb"[a-z]", rb"[^a-z]", rb"[\x00-\x1f]", rb"[\x80-\xff]",
        rb"(?a:\w)", rb"(?:\d|\s|\w)",
    )
    flags = (0, re.IGNORECASE, re.ASCII, re.ASCII | re.IGNORECASE, re.LOCALE, re.LOCALE | re.IGNORECASE)
    for pattern_index, pattern in enumerate(patterns):
        for flag in flags:
            label = f"bytes:{pattern_index}:flags={int(flag)}"
            pair = gate.compile_pair("byte-membership", label, pattern, flag)
            if pair is None:
                continue
            expected_pattern, actual_pattern = pair
            constructors = (
                ("bytes", bytes),
                ("bytearray", bytearray),
                ("memoryview", memoryview),
                ("bytes-subclass", BytesSubclass),
            ) if pattern_index < 4 else (("bytes", bytes),)
            for codepoint in range(256):
                raw = bytes((codepoint,))
                for kind, constructor in constructors:
                    subject = constructor(raw)
                    gate.compare(
                        "byte-membership",
                        f"{label}:{kind}:{codepoint:02x}",
                        lambda subject=subject: match_snapshot(expected_pattern.fullmatch(subject)),
                        lambda subject=subject: match_snapshot(actual_pattern.fullmatch(subject)),
                        pattern=pattern,
                        flags=int(flag),
                        byte=codepoint,
                        subject_kind=kind,
                    )


def zero_width_and_lookaround(gate):
    text_patterns = (
        ("empty", r"", 0),
        ("empty-first", r"|.", 0),
        ("nonempty-first", r".|", 0),
        ("lazy-star", r".*?", 0),
        ("lazy-captured", r"(.*?)", 0),
        ("optional-capture", r"(a)?", 0),
        ("empty-lookahead", r"(?=a)|a", 0),
        ("any-lookahead", r"(?=.)|.", 0),
        ("boundary", r"\b|\B", 0),
        ("boundary-reversed", r"\B|\b", 0),
        ("anchors", r"^|$", 0),
        ("multiline-anchors", r"^|$", re.MULTILINE),
        ("positive-lookahead-capture", r"(?=(a))a", 0),
        ("named-lookahead-backref", r"(?=(?P<x>a))(?P=x)", 0),
        ("negative-lookahead-capture", r"(?!(a))b", 0),
        ("positive-lookbehind-capture", r"(?<=(a))b", 0),
        ("negative-lookbehind-capture", r"(?<!(a))b", 0),
        ("lookahead-alternative-rollback", r"(?:(?=(a))ab|a(c))", 0),
        ("lookahead-condition", r"(?=(a)?)(?(1)a|b)", 0),
        ("alternative-condition-rollback", r"(?:(a)b|a)(?(1)c|d)", 0),
        ("nested-capture-order", r"(?=(?P<outer>a(?P<inner>b)?))(?P=outer)", 0),
        ("repeat-capture-order", r"(a(b)?)+", 0),
        ("nullable-repeat", r"(?:a?)*", 0),
        ("nullable-repeat-lazy", r"(?:a?)*?", 0),
        ("scoped-unicode", r"(?a:\w+)|(?u:\w+)", 0),
        ("scoped-case", r"(?i:[a-z]+)(?-i:[A-Z]+)", 0),
        ("scoped-boundary", r"(?a:\b\w+\b)|(?u:\b\w+\b)", 0),
        ("c0-unicode-whitespace", r"\s+|\S+", 0),
        ("c0-ascii-whitespace", r"\s+|\S+", re.ASCII),
        ("wide-negative-class", r"[^\x00-\xff]+|[\x00-\xff]+", 0),
        ("case-range", r"[A-Z]+", re.IGNORECASE),
        ("atomic-alternative", r"(?>a|ab)b", 0),
        ("possessive-repeat", r"a*+a|a++", 0),
    )
    text_subjects = (
        "", "a", "aba", "ab\nac\n", "aaabbb", "a\x1c\x1d\x1e\x1f b",
        "caf\xe9 Stra\xdfe \u0130\u0131\u017f\u212a",
        "\u96ea\U0001f600\ud800a", "a\u0301_\u0663\uff19",
    )
    for pattern_index, (name, pattern, flags) in enumerate(text_patterns):
        for subject_index, subject in enumerate(text_subjects):
            if subject_index > 3 and pattern_index < 12 and subject_index not in (5, 7):
                continue
            exercise_pattern(
                gate,
                "zero-width-lookaround-flags",
                f"{name}:subject={subject_index}",
                pattern,
                subject,
                flags,
            )

    byte_patterns = (
        ("byte-empty", rb"", 0),
        ("byte-empty-first", rb"|.", 0),
        ("byte-nonempty-first", rb".|", 0),
        ("byte-lazy", rb".*?", 0),
        ("byte-boundary", rb"\b|\B", 0),
        ("byte-lookahead", rb"(?=(a))a|.", 0),
        ("byte-lookbehind", rb"(?<=(a))b|.", 0),
        ("byte-condition", rb"(?:(a)b|a)(?(1)c|d)", 0),
        ("byte-case", rb"(?i:[a-z]+)(?-i:[A-Z]+)", 0),
        ("byte-locale", rb"(?L:\w+)|\W+", 0),
        ("byte-multiline", rb"^|$", re.MULTILINE),
    )
    payloads = (b"", b"a", b"aba", b"a\x1c\xff\nAB", bytes(range(16)))
    for name, pattern, flags in byte_patterns:
        for index, payload in enumerate(payloads):
            variants = (("bytes", payload),)
            if index in (1, 3):
                variants += (
                    ("bytearray", bytearray(payload)),
                    ("memoryview", memoryview(payload)),
                    ("bytes-subclass", BytesSubclass(payload)),
                )
            for kind, subject in variants:
                exercise_pattern(
                    gate,
                    "bytes-zero-width-lookaround",
                    f"{name}:{kind}:subject={index}",
                    pattern,
                    subject,
                    flags,
                )


def backreferences(gate):
    for group_index, equivalences in enumerate(CASE_EQUIVALENCES):
        for left in equivalences:
            escaped = re.escape(chr(left))
            patterns = (
                ("global-numeric", f"({escaped})-\\1", re.IGNORECASE),
                ("global-named", f"(?P<x>{escaped})-(?P=x)", re.IGNORECASE),
                ("local-both", f"(?i:(?P<x>{escaped})-(?P=x))", 0),
                ("local-capture-only", f"(?i:(?P<x>{escaped}))-(?P=x)", 0),
                ("case-disabled-reference", f"(?i)(?P<x>{escaped})-(?-i:(?P=x))", 0),
                ("class-reference", f"([{escaped}])-\\1", re.IGNORECASE),
            )
            for name, pattern, flags in patterns:
                label = f"{name}:group={group_index}:left=U+{left:04X}"
                pair = gate.compile_pair("unicode-backreferences", label, pattern, flags)
                if pair is None:
                    continue
                expected_pattern, actual_pattern = pair
                for right in equivalences:
                    for first in equivalences:
                        subject = chr(first) + "-" + chr(right)
                        gate.compare(
                            "unicode-backreferences",
                            f"{label}:first=U+{first:04X}:right=U+{right:04X}",
                            lambda subject=subject: match_snapshot(expected_pattern.fullmatch(subject)),
                            lambda subject=subject: match_snapshot(actual_pattern.fullmatch(subject)),
                            pattern=pattern,
                            flags=int(flags),
                            first=first,
                            right=right,
                        )

    byte_patterns = (
        ("byte-global-numeric", rb"([a-z])-\1", re.IGNORECASE),
        ("byte-global-named", rb"(?P<x>[a-z])-(?P=x)", re.IGNORECASE),
        ("byte-local", rb"(?i:(?P<x>[a-z])-(?P=x))", 0),
        ("byte-scoped-reference", rb"(?i:(?P<x>[a-z]))-(?P=x)", 0),
        ("byte-locale-reference", rb"(?P<x>\w)-(?P=x)", re.LOCALE | re.IGNORECASE),
    )
    for name, pattern, flags in byte_patterns:
        pair = gate.compile_pair("byte-backreferences", name, pattern, flags)
        if pair is None:
            continue
        expected_pattern, actual_pattern = pair
        for first in range(256):
            rights = (first, first ^ 0x20, (first + 1) & 0xFF)
            for right in dict.fromkeys(rights):
                subject = bytes((first, 0x2D, right))
                gate.compare(
                    "byte-backreferences",
                    f"{name}:{first:02x}:{right:02x}",
                    lambda subject=subject: match_snapshot(expected_pattern.fullmatch(subject)),
                    lambda subject=subject: match_snapshot(actual_pattern.fullmatch(subject)),
                    pattern=pattern,
                    flags=int(flags),
                    first=first,
                    right=right,
                )


def parser_escapes(gate):
    valid_text = (
        r"\x00", r"\x7f", r"\x80", r"\xff", r"\u0000", r"\u00ff",
        r"\u0100", r"\ud800", r"\udfff", r"\uffff", r"\U00010000",
        r"\U0010ffff", r"\000", r"\001", r"\037", r"\177", r"\377",
        r"[\x00-\xff]", r"[\u0080-\u0100]", r"[\U00010000-\U0010ffff]",
        r"\N{SNOWMAN}", r"\N{KELVIN SIGN}", r"\N{LATIN SMALL LETTER SHARP S}",
        r"(?x: \x41 [\x42-\x43] )", r"(?i:\u212a)",
    )
    valid_bytes = (
        rb"\x00", rb"\x7f", rb"\x80", rb"\xff", rb"\000", rb"\001",
        rb"\037", rb"\177", rb"\377", rb"[\x00-\xff]", rb"[\x80-\xff]",
        rb"(?x: \x41 [\x42-\x43] )", rb"(?i:\x6b)",
    )
    invalid_text = (
        "\\", r"\x", r"\x0", r"\xgg", r"\u", r"\u0", r"\u000",
        r"\uXXXX", r"\U", r"\U0000000", r"\U00110000", r"\Uffffffff",
        r"\400", r"\777", r"\8", r"\9", r"\q", r"[\q]", r"[z-a]",
        r"[\x01-\x00]", r"\N", r"\N{}", r"\N{NOT A VALID NAME}",
        r"(?P<1>a)", r"(?P<>a)", r"(?P<x>a)(?P<x>b)", r"(?P=missing)",
        r"(?i", r"(?-i)", r"(?a-u:a)", r"(?<=a+)b", r"a{2,1}",
    )
    invalid_bytes = (
        b"\\", rb"\x", rb"\x0", rb"\xgg", rb"\u0041",
        rb"\U00000041", rb"\N{SNOWMAN}", rb"\400", rb"\777", rb"\q",
        rb"[\q]", rb"[z-a]", rb"(?P<1>a)", b"(?P<\xff>a)",
        rb"(?P=missing)", rb"(?u:a)", rb"(?<=a+)b",
    )
    for kind, patterns in (("valid-text", valid_text), ("valid-bytes", valid_bytes)):
        for index, pattern in enumerate(patterns):
            gate.compile_pair("parser-escapes", f"{kind}:{index}", pattern, 0)
    for kind, patterns in (("invalid-text", invalid_text), ("invalid-bytes", invalid_bytes)):
        for index, pattern in enumerate(patterns):
            gate.compare(
                "parser-errors",
                f"{kind}:{index}",
                lambda pattern=pattern: pattern_snapshot(re.compile(pattern)),
                lambda pattern=pattern: pattern_snapshot(gate.candidate.compile(pattern)),
                pattern=pattern,
            )

    invalid_flag_cases = (
        ("text-locale", r"a", re.LOCALE),
        ("text-ascii-unicode", r"a", re.ASCII | re.UNICODE),
        ("byte-unicode", rb"a", re.UNICODE),
        ("byte-locale-ascii", rb"a", re.LOCALE | re.ASCII),
    )
    for name, pattern, flags in invalid_flag_cases:
        gate.compare(
            "flag-errors",
            name,
            lambda pattern=pattern, flags=flags: pattern_snapshot(re.compile(pattern, flags)),
            lambda pattern=pattern, flags=flags: pattern_snapshot(gate.candidate.compile(pattern, flags)),
            pattern=pattern,
            flags=int(flags),
        )


def mutable_scanners(gate):
    patterns = (
        ("mutable-literal", rb"a"),
        ("mutable-nullable", rb"|a"),
        ("mutable-lookahead", rb"(?=a)|a"),
        ("mutable-class", rb"[a-z]+|\d+"),
    )

    def action(module, pattern, kind):
        payload = bytearray(b"aXa1a")
        subject = payload if kind == "bytearray" else memoryview(payload)
        scanner = module.compile(pattern).scanner(subject)
        events = [match_snapshot(scanner.search())]
        payload[1] = ord("a")
        events.append(match_snapshot(scanner.search()))
        payload[3] = ord("b")
        events.append(match_snapshot(scanner.search()))
        events.append(match_snapshot(scanner.search()))
        events.append(match_snapshot(scanner.search()))
        return {"events": events, "final_bytes": bytes(payload)}

    for name, pattern in patterns:
        for kind in ("bytearray", "memoryview"):
            gate.compare(
                "mutable-scanners",
                f"{name}:{kind}",
                lambda pattern=pattern, kind=kind: action(re, pattern, kind),
                lambda pattern=pattern, kind=kind: action(gate.candidate, pattern, kind),
                pattern=pattern,
                subject_kind=kind,
            )


def signature_snapshot(function):
    signature = inspect.signature(function)
    parameters = []
    for parameter in signature.parameters.values():
        if parameter.default is inspect.Parameter.empty:
            default = {"kind": "missing"}
        elif parameter.default is None or isinstance(parameter.default, (bool, int, str)):
            default = {"kind": "literal", "value": normalise(parameter.default)}
        else:
            default = {"kind": type(parameter.default).__name__}
        parameters.append(
            {
                "name": parameter.name,
                "kind": parameter.kind.name,
                "default": default,
            }
        )
    return {
        "parameters": parameters,
        "return_annotation": (
            "missing"
            if signature.return_annotation is inspect.Signature.empty
            else normalise(signature.return_annotation)
        ),
    }


MODULE_OPERATIONS = (
    "search", "match", "fullmatch", "findall", "finditer",
    "split", "sub", "subn",
)


def invoke_module(module, operation, pattern, subject, flags=0):
    function = getattr(module, operation)
    if operation in ("sub", "subn"):
        replacement = b"#" if not isinstance(subject, str) else "#"
        return function(pattern, replacement, subject, count=1, flags=flags)
    if operation == "split":
        return function(pattern, subject, maxsplit=1, flags=flags)
    result = function(pattern, subject, flags=flags)
    if operation in ("search", "match", "fullmatch"):
        return match_snapshot(result)
    if operation == "finditer":
        return [match_snapshot(item) for item in result]
    return result


class RecordingTextHash(str):
    def __new__(cls, value, trace, module, behavior):
        item = str.__new__(cls, value)
        item.trace = trace
        item.module = module
        item.behavior = behavior
        item.active = False
        return item

    def __hash__(self):
        self.trace.append(("pattern-hash", "text", self.behavior))
        if self.behavior == "raises":
            raise RuntimeError("independent text pattern hash sentinel")
        if self.behavior == "raises-keyerror":
            raise KeyError("independent text pattern hash sentinel")
        if self.behavior == "reentrant" and not self.active:
            self.active = True
            try:
                match = self.module.search("z", "z")
                self.trace.append(("nested-search", match.span()))
            finally:
                self.active = False
        elif self.behavior == "purge":
            self.module.purge()
            self.trace.append(("nested-purge", True))
        return str.__hash__(self)


class RecordingBytesHash(bytes):
    def __new__(cls, value, trace, module, behavior):
        item = bytes.__new__(cls, value)
        item.trace = trace
        item.module = module
        item.behavior = behavior
        item.active = False
        return item

    def __hash__(self):
        self.trace.append(("pattern-hash", "bytes", self.behavior))
        if self.behavior == "raises":
            raise RuntimeError("independent bytes pattern hash sentinel")
        if self.behavior == "raises-keyerror":
            raise KeyError("independent bytes pattern hash sentinel")
        if self.behavior == "reentrant" and not self.active:
            self.active = True
            try:
                match = self.module.search(b"z", b"z")
                self.trace.append(("nested-search", match.span()))
            finally:
                self.active = False
        elif self.behavior == "purge":
            self.module.purge()
            self.trace.append(("nested-purge", True))
        return bytes.__hash__(self)


class RecordingFlagHash(int):
    def __new__(cls, value, trace, behavior):
        item = int.__new__(cls, value)
        item.trace = trace
        item.behavior = behavior
        return item

    def __hash__(self):
        self.trace.append(("flag-hash", int(self), self.behavior))
        if self.behavior == "raises":
            raise RuntimeError("independent flag hash sentinel")
        if self.behavior == "raises-keyerror":
            raise KeyError("independent flag hash sentinel")
        return int.__hash__(self)


def hash_observation(module, operation, byte_mode, kind, behavior):
    trace = []
    module.purge()
    value = b"a" if byte_mode else "a"
    subject = b"aba" if byte_mode else "aba"
    pattern = value
    flags = 0
    if kind == "pattern":
        cls = RecordingBytesHash if byte_mode else RecordingTextHash
        pattern = cls(value, trace, module, behavior)
    elif kind == "flag":
        flags = RecordingFlagHash(0, trace, behavior)
    elif kind == "unhashable-pattern":
        pattern = {
            "list": [value],
            "dict": {"pattern": value},
            "set": {value},
        }[behavior]
    elif kind == "unhashable-flag":
        flags = {
            "list": [0],
            "dict": {"flag": 0},
            "set": {0},
        }[behavior]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        answer = attempted(
            lambda: invoke_module(module, operation, pattern, subject, flags)
        )
    answer["trace"] = normalise(trace)
    return answer


def module_signatures_and_hashes(gate):
    for operation in ("split", "sub", "subn"):
        gate.compare(
            "module-signature-metadata",
            operation,
            lambda operation=operation: signature_snapshot(getattr(re, operation)),
            lambda operation=operation: signature_snapshot(
                getattr(gate.candidate, operation)
            ),
            operation=operation,
        )

    variants = (
        ("pattern", ("normal", "raises", "raises-keyerror", "reentrant", "purge")),
        ("flag", ("normal", "raises", "raises-keyerror")),
        ("unhashable-flag", ("list", "dict", "set")),
        ("unhashable-pattern", ("list", "dict", "set")),
    )
    for operation in MODULE_OPERATIONS:
        for byte_mode in (False, True):
            for kind, behaviors in variants:
                for behavior in behaviors:
                    label = (
                        f"{operation}:"
                        f"{'bytes' if byte_mode else 'text'}:"
                        f"{kind}:{behavior}"
                    )
                    gate.record(
                        "module-hash-and-cache-order",
                        label,
                        hash_observation(re, operation, byte_mode, kind, behavior),
                        hash_observation(
                            gate.candidate, operation, byte_mode, kind, behavior
                        ),
                        operation=operation,
                        byte_mode=byte_mode,
                        hash_kind=kind,
                        behavior=behavior,
                        source_seed=MODULE_API_SEED,
                    )


def bytes_identity_snapshot(module, expression, payload, kind, operation, window):
    subject = (
        payload
        if kind == "bytes"
        else BytesSubclass(payload)
        if kind == "bytes-subclass"
        else bytearray(payload)
        if kind == "bytearray"
        else memoryview(payload)
    )
    pattern = module.compile(expression)
    pos, endpos = window
    if operation == "findall":
        rows = pattern.findall(subject, pos, endpos)

        def row_identity(row):
            if isinstance(row, tuple):
                return {
                    "value": normalise(row),
                    "same_subject": [item is subject for item in row],
                    "same_pattern": [item is pattern.pattern for item in row],
                }
            return {
                "value": normalise(row),
                "same_subject": row is subject,
                "same_pattern": row is pattern.pattern,
            }

        return {
            "rows": [row_identity(row) for row in rows],
            "adjacent_identity": [left is right for left, right in zip(rows, rows[1:])],
        }

    match = pattern.search(subject, pos, endpos)
    if match is None:
        return None
    if operation == "group0":
        item = match.group(0)
        return {"value": normalise(item), "same_subject": item is subject}
    if operation == "getitem0":
        item = match[0]
        return {"value": normalise(item), "same_subject": item is subject}
    if operation == "groups":
        items = match.groups()
        return {
            "value": normalise(items),
            "same_subject": [item is subject for item in items],
        }
    if operation == "groupdict":
        items = match.groupdict()
        return {
            "value": normalise(items),
            "same_subject": {
                name: item is subject for name, item in sorted(items.items())
            },
        }
    if operation == "group1":
        if not pattern.groups:
            return {"not_applicable": True}
        item = match.group(1)
        return {"value": normalise(item), "same_subject": item is subject}
    raise ValueError(f"unknown identity operation: {operation}")


def exact_bytes_identity(gate):
    patterns = (
        rb"a*", rb"(a*)", rb".*", rb"(?P<all>.*)",
        rb"(?P<all>a*)", rb"(a*)(a?)", rb"(?:a|)*",
    )
    lengths = (0, 1, 2, 3, 63, 64, 65, 127, 128, 129, 255, 256, 257)
    operations = ("findall", "group0", "getitem0", "group1", "groups", "groupdict")
    for pattern_index, pattern in enumerate(patterns):
        for length in lengths:
            payload = b"a" * length
            for kind in ("bytes", "bytes-subclass", "bytearray", "memoryview"):
                available = (
                    (0, length),
                    (0, max(length - 1, 0)),
                    (min(1, length), length),
                )
                for pos, endpos in dict.fromkeys(available):
                    for operation in operations:
                        label = (
                            f"p{pattern_index}:{kind}:len={length}:"
                            f"{operation}:{pos}:{endpos}"
                        )
                        gate.compare(
                            "whole-bytes-object-identity",
                            label,
                            lambda pattern=pattern, kind=kind, operation=operation,
                                   payload=payload, window=(pos, endpos):
                                bytes_identity_snapshot(
                                    re, pattern, payload, kind, operation, window
                                ),
                            lambda pattern=pattern, kind=kind, operation=operation,
                                   payload=payload, window=(pos, endpos):
                                bytes_identity_snapshot(
                                    gate.candidate, pattern, payload, kind,
                                    operation, window
                                ),
                            pattern=pattern,
                            subject_kind=kind,
                            length=length,
                            operation=operation,
                            pos=pos,
                            endpos=endpos,
                        )


def scoped_c0_whitespace(gate):
    patterns = (
        r"\s", r"\S", r"[\s]", r"[\S]", r"(\s)", r"(\S)",
        r"(?P<space>\s)", r"(?P<other>\S)", r"\s+", r"\S+",
        r"(?a:\s)", r"(?a:\S)", r"(?u:\s)", r"(?u:\S)",
        r"(?a:(\s))", r"(?a:(\S))", r"(?u:(\s))", r"(?u:(\S))",
        r"(?a:\S)|a", r"(?u:\s)|a", r"(?:\s|\S)", r"(?:\S|\s)",
        r"(?=\s)\s", r"(?=\S)\S",
    )
    flags_options = (0, int(re.ASCII), int(re.IGNORECASE),
                     int(re.ASCII | re.IGNORECASE), int(re.MULTILINE))
    window_operations = ("search", "match", "fullmatch", "findall", "finditer", "scanner")
    full_operations = ("split", "sub", "subn", "module-findall", "module-search", "module-sub")

    def source_rows(character):
        raw = character.encode("ascii")
        return (
            ("text-single", character, False),
            ("text-prefix", "a" + character, False),
            ("text-double", character * 2, False),
            ("text-subclass", TextSubclass("a" + character + "a"), False),
            ("bytes-single", raw, True),
            ("bytes-prefix", b"a" + raw, True),
            ("bytes-subclass", BytesSubclass(b"a" + raw + b"a"), True),
            ("bytearray", bytearray(b"a" + raw + b"a"), True),
            ("memoryview", memoryview(b"a" + raw + b"a"), True),
        )

    def operation_result(module, compiled, expression, subject, flags, operation, pos, endpos):
        binary = not isinstance(subject, str)
        replacement = b"X" if binary else "X"
        if operation in ("search", "match", "fullmatch"):
            return match_snapshot(getattr(compiled, operation)(subject, pos, endpos))
        if operation == "findall":
            return compiled.findall(subject, pos, endpos)
        if operation == "finditer":
            return [match_snapshot(item) for item in compiled.finditer(subject, pos, endpos)]
        if operation == "scanner":
            scanner = compiled.scanner(subject, pos, endpos)
            result = []
            for _ in range(64):
                match = scanner.search()
                if match is None:
                    return result
                result.append(match_snapshot(match))
            raise RuntimeError("C0 scanner failed to terminate")
        if operation == "split":
            return compiled.split(subject)
        if operation == "sub":
            return compiled.sub(replacement, subject)
        if operation == "subn":
            return compiled.subn(replacement, subject)
        if operation == "module-findall":
            return module.findall(expression, subject, flags)
        if operation == "module-search":
            return match_snapshot(module.search(expression, subject, flags))
        if operation == "module-sub":
            return module.sub(expression, replacement, subject, flags=flags)
        raise ValueError(f"unknown frozen C0 operation: {operation}")

    for codepoint in range(0x1C, 0x20):
        character = chr(codepoint)
        for source_name, subject, byte_mode in source_rows(character):
            for pattern_index, text_pattern in enumerate(patterns):
                pattern = text_pattern.encode("ascii") if byte_mode else text_pattern
                for flags in flags_options:
                    prefix = (
                        f"U+{codepoint:04X}:{source_name}:"
                        f"p{pattern_index:02d}:flags={flags}"
                    )
                    standard = attempted(lambda: pattern_snapshot(re.compile(pattern, flags)))
                    actual = attempted(
                        lambda: pattern_snapshot(gate.candidate.compile(pattern, flags))
                    )
                    details = {
                        "pattern": pattern,
                        "subject": subject,
                        "source": source_name,
                        "flags": flags,
                        "codepoint": codepoint,
                    }
                    if standard["status"] == "error" or actual["status"] == "error":
                        gate.record(
                            "c0-unicode-scoped-whitespace",
                            prefix + ":compile",
                            standard,
                            actual,
                            **details,
                        )
                        continue
                    expected_pattern = re.compile(pattern, flags)
                    actual_pattern = gate.candidate.compile(pattern, flags)
                    ranges = tuple(dict.fromkeys(((0, len(subject)), (1, len(subject)))))
                    plans = [
                        (operation, pos, endpos)
                        for operation in window_operations
                        for pos, endpos in ranges
                    ] + [
                        (operation, 0, len(subject))
                        for operation in full_operations
                    ]
                    for operation, pos, endpos in plans:
                        gate.compare(
                            "c0-unicode-scoped-whitespace",
                            f"{prefix}:{operation}:{pos}:{endpos}",
                            lambda operation=operation, pos=pos, endpos=endpos:
                                operation_result(
                                    re, expected_pattern, pattern, subject,
                                    flags, operation, pos, endpos
                                ),
                            lambda operation=operation, pos=pos, endpos=endpos:
                                operation_result(
                                    gate.candidate, actual_pattern, pattern,
                                    subject, flags, operation, pos, endpos
                                ),
                            **details,
                            operation=operation,
                            pos=pos,
                            endpos=endpos,
                        )


def quantified_pair(gate, category, label, pattern, flags):
    expected_pattern = re.compile(pattern, flags)
    try:
        actual_pattern = gate.candidate.compile(pattern, flags)
    except Exception as error:
        actual_pattern = None
        actual_error = error
    else:
        actual_error = None
    gate.record(
        category,
        f"{label}:compile",
        {"status": "ok", "value": pattern_snapshot(expected_pattern)},
        (
            {"status": "ok", "value": pattern_snapshot(actual_pattern)}
            if actual_pattern is not None
            else attempted(lambda: raise_error(actual_error))
        ),
        pattern=pattern,
        flags=int(flags),
    )
    return expected_pattern, actual_pattern, actual_error


def quantified_semantics(gate, category, label, pattern, subject, flags, ranges):
    expected, actual, compile_error = quantified_pair(
        gate, category, label, pattern, flags
    )

    def apply(compiled, operation, pos, endpos):
        if compiled is None:
            return raise_error(compile_error)
        if operation in ("search", "match", "fullmatch"):
            return match_snapshot(
                getattr(compiled, operation)(subject, pos, endpos)
            )
        if operation == "findall":
            return compiled.findall(subject, pos, endpos)
        if operation == "finditer":
            matches = [
                match_snapshot(item)
                for item in itertools.islice(
                    compiled.finditer(subject, pos, endpos),
                    2 * len(subject) + 17,
                )
            ]
            if len(matches) > 2 * len(subject) + 16:
                raise RuntimeError("quantified-assertion finditer did not terminate")
            return matches
        if operation == "scanner-search":
            return scanner_values(compiled, subject, pos, endpos, "search")
        if operation == "scanner-match":
            return scanner_values(compiled, subject, pos, endpos, "match")
        raise ValueError(f"unknown quantified semantic operation: {operation}")

    for pos, endpos in ranges:
        for operation in (
            "search", "match", "fullmatch", "findall", "finditer",
            "scanner-search", "scanner-match",
        ):
            gate.compare(
                category,
                f"{label}:{operation}:{pos}:{endpos}",
                lambda operation=operation, pos=pos, endpos=endpos:
                    apply(expected, operation, pos, endpos),
                lambda operation=operation, pos=pos, endpos=endpos:
                    apply(actual, operation, pos, endpos),
                pattern=pattern,
                flags=int(flags),
                subject=subject,
                pos=pos,
                endpos=endpos,
            )


def quantified_assertions(gate):
    atoms = ("(?=a)", "(?!a)", "(?<=a)", "(?<!a)")
    quantifiers = ("?", "??", "*", "*?", "+", "+?", "{0,2}", "{1,3}", "*+")
    for atom_index, atom in enumerate(atoms):
        for quantifier_index, quantifier in enumerate(quantifiers):
            piece = atom + quantifier
            contexts = (
                piece, "x" + piece, piece + "x", "(?:" + piece + ")", piece + "|b"
            )
            for context_index, text_pattern in enumerate(contexts):
                for byte_mode in (False, True):
                    pattern = (
                        text_pattern.encode("ascii") if byte_mode else text_pattern
                    )
                    subject = b"aab" if byte_mode else "aab"
                    for flags in (0, re.IGNORECASE, re.MULTILINE, re.ASCII):
                        label = (
                            f"atom={atom_index}:quantifier={quantifier_index}:"
                            f"context={context_index}:"
                            f"{'bytes' if byte_mode else 'text'}:"
                            f"flags={int(flags)}"
                        )
                        quantified_semantics(
                            gate,
                            "quantified-zero-width-assertions",
                            label,
                            pattern,
                            subject,
                            flags,
                            ((0, len(subject)),),
                        )

    repeat_assertions = (
        ("positive-ahead", r"(?=a)"),
        ("negative-ahead", r"(?!b)"),
        ("positive-behind", r"(?<=a)"),
        ("negative-behind", r"(?<!b)"),
        ("positive-boundary", r"(?=\b)"),
        ("negative-nonboundary", r"(?!\B)"),
    )
    repeat_quantifiers = (
        ("zero-or-more", "*"),
        ("zero-or-more-lazy", "*?"),
        ("zero-or-more-possessive", "*+"),
        ("one-or-more", "+"),
        ("one-or-more-lazy", "+?"),
        ("one-or-more-possessive", "++"),
    )
    subjects = ("", "a", "ba", "a a", "!!  xſ", "雪a😀")
    for assertion_index, (assertion_name, atom) in enumerate(repeat_assertions):
        for quantifier_index, (quantifier_name, quantifier) in enumerate(repeat_quantifiers):
            subject = subjects[(assertion_index + quantifier_index) % len(subjects)]
            flags = (
                re.IGNORECASE | re.MULTILINE
                if (assertion_index + quantifier_index) % 3 == 0
                else 0
            )
            pattern = atom + quantifier + r"(?P<value>[a-z]?)\b"
            length = len(subject)
            ranges = tuple(
                dict.fromkeys(
                    ((0, length), (0, 0), (length, length),
                     (min(1, length), length), (length, 0))
                )
            )
            quantified_semantics(
                gate,
                "repeat-quantified-lookaround",
                f"{assertion_name}:{quantifier_name}:seed={REPEAT_SEED}",
                pattern,
                subject,
                flags,
                ranges,
            )


def memory_seeded_assertions(gate):
    randomizer = random.Random(MEMORY_SAFETY_SEED)
    atoms = (
        "a", "b", ".", r"\d", r"\w", "[ab]", "[^x]", "(?:a|b)",
        "(?=a)", "(?<!b)", "()", "(a)",
    )
    quantifiers = ("", "?", "??", "*", "*?", "+", "+?", "{0,2}")
    patterns = []
    while len(patterns) < 128:
        pieces = []
        for _ in range(randomizer.randrange(1, 5)):
            pieces.append(randomizer.choice(atoms) + randomizer.choice(quantifiers))
        pattern = "".join(pieces)
        if randomizer.randrange(3) == 0:
            pattern += "|" + randomizer.choice(("", "a", "b", "(?=a)"))
        try:
            re.compile(pattern)
        except re.error:
            continue
        patterns.append(pattern)

    subjects = ("", "a", "ab", "ba", "aab", "0b9", "a\nb", "xy")
    flags_options = (0, int(re.IGNORECASE), int(re.MULTILINE),
                     int(re.DOTALL), int(re.ASCII))

    def original_windows(length):
        return (
            (0, length), (0, 0), (length, length), (1, length),
            (0, max(0, length - 1)), (-5, length + 5),
            (length + 3, length + 9), (length, 0),
        )

    for pattern_index, pattern in enumerate(patterns):
        for variant in range(3):
            subject = randomizer.choice(subjects)
            pos, endpos = randomizer.choice(original_windows(len(subject)))
            flags = randomizer.choice(flags_options)
            quantified_semantics(
                gate,
                "memory-safety-seeded-valid-grammar",
                f"seed={MEMORY_SAFETY_SEED}:p{pattern_index}:v{variant}",
                pattern,
                subject,
                flags,
                ((pos, endpos),),
            )


def grammar_assertion_controls(gate):
    patterns = (
        r"(?=a){2}",
        r"(?=a){2,4}",
        r"(?=a)*",
        r"(?=a)+",
        r"(?=a)?",
        r"(?!b){2}",
        r"(?<=a){2}",
        r"(?<!b){2}",
        r"(?=(a)){2}",
        r"(?=(a))+",
        r"(?=a){2}+",
        r"(?=a){2,4}?",
        r"(?<=a){2}a",
        r"(?<!b){2}a",
        r"[ab]+?[ab]+?\d(?<!b)*",
    )
    for pattern_index, expression in enumerate(patterns):
        for byte_mode in (False, True):
            pattern = expression.encode("ascii") if byte_mode else expression
            subject = b"aab1a" if byte_mode else "aab1a"
            for flags in (0, re.IGNORECASE, re.MULTILINE, re.ASCII):
                quantified_semantics(
                    gate,
                    "grammar-quantified-lookaround",
                    f"p{pattern_index}:"
                    f"{'bytes' if byte_mode else 'text'}:flags={int(flags)}",
                    pattern,
                    subject,
                    flags,
                    ((0, len(subject)),),
                )


def public_object_contract(gate):
    surface = importlib.import_module("tools.rust_surface_probe")
    records = []
    runners = (
        surface.index_protocol,
        surface.bound_calls,
        surface.count_protocol,
        surface.subclass_surface,
        surface.buffer_surface,
        surface.match_surface,
        surface.malicious_hash,
        surface.pattern_surface,
    )
    for run in runners:
        run(records, re, gate.candidate)
    for index, item in enumerate(records):
        gate.record(
            "public-object-and-buffer-contract",
            f"{index:04d}:{item['family']}:{item['operation']}",
            item["expected"],
            item["actual"],
            family=item["family"],
            operation=item["operation"],
            original_details=item["details"],
            original_equivalent=item["passed"],
        )


def frozen_source_module(name, filename, source):
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / "tools" / filename)
    sys.modules[name] = module
    exec(compile(source, filename, "exec"), module.__dict__)
    return module


_EPHEMERAL_ADDRESS = re.compile(r"0x[0-9a-fA-F]+")


def canonical_object_observation(value):
    """Keep exact semantics while removing nondeterministic repr addresses."""

    if isinstance(value, str):
        return _EPHEMERAL_ADDRESS.sub("0xADDRESS", value)
    if isinstance(value, list):
        return [canonical_object_observation(item) for item in value]
    if isinstance(value, dict):
        return {
            key: canonical_object_observation(item)
            for key, item in value.items()
        }
    return value


def independent_object_contract(gate):
    oracle = frozen_source_module(
        "_rebar_frozen_independent_object_contract",
        "object_contract_probe.py",
        FROZEN_OBJECT_CONTRACT_SOURCE,
    )
    cases = oracle.build_cases()
    if len(cases) != 14_783:
        raise RuntimeError(
            f"independent frozen object case count changed: {len(cases)}"
        )
    for case in cases:
        expected = canonical_object_observation(
            oracle.attempted(lambda case=case: case.action(re))
        )
        actual = canonical_object_observation(
            oracle.attempted(lambda case=case: case.action(gate.candidate))
        )
        gate.record(
            "independent-object-contract/" + case.family,
            case.label,
            expected,
            actual,
            independent_family=case.family,
            independent_seed=OBJECT_CONTRACT_SEED,
            ephemeral_address_normalisation="0xADDRESS",
        )
    gate.embedded_oracles.append(
        {
            "name": "independent-object-contract",
            "schema": oracle.SCHEMA,
            "seed": oracle.SEED,
            "source_sha256": hashlib.sha256(
                FROZEN_OBJECT_CONTRACT_SOURCE.encode("utf-8")
            ).hexdigest(),
            "cases": len(cases),
            "ephemeral_address_normalisation": "0xADDRESS",
        }
    )


def independent_parser_grammar(gate):
    oracle = frozen_source_module(
        "_rebar_frozen_independent_parser_grammar",
        "parser_grammar_fuzz.py",
        FROZEN_PARSER_GRAMMAR_SOURCE,
    )
    randomizer = random.Random(oracle.SEED)
    digest = hashlib.sha256()
    seen = set()
    cases = []
    for family in oracle.FAMILIES:
        index = 0
        attempts = 0
        while index < PARSER_GRAMMAR_CASES_PER_FAMILY:
            attempts += 1
            if attempts > PARSER_GRAMMAR_CASES_PER_FAMILY * 100:
                raise RuntimeError(
                    f"could not regenerate unique frozen grammar cases: {family}"
                )
            case = oracle.make_case(family, randomizer, index)
            identity = oracle.canonical(
                (family, case["pattern"], case["subject"], case["flags"])
            )
            if identity in seen:
                continue
            seen.add(identity)
            digest.update((oracle.canonical(case) + "\n").encode("utf-8"))
            cases.append(case)
            index += 1
    actual_fixture_digest = digest.hexdigest()
    if actual_fixture_digest != PARSER_GRAMMAR_FIXTURE_SHA256:
        raise RuntimeError(
            "independent frozen grammar fixture changed: "
            f"expected={PARSER_GRAMMAR_FIXTURE_SHA256}; "
            f"actual={actual_fixture_digest}"
        )
    if len(cases) != 20_480:
        raise RuntimeError(
            f"independent frozen grammar case count changed: {len(cases)}"
        )
    for case in cases:
        expected = oracle.observe(re, case)
        actual = oracle.observe(gate.candidate, case)
        gate.record(
            "independent-parser-grammar/" + case["family"],
            case["id"],
            expected,
            actual,
            independent_family=case["family"],
            independent_seed=PARSER_GRAMMAR_SEED,
            fixture_sha256=actual_fixture_digest,
            pattern=case["pattern"],
            subject=case["subject"],
            flags=case["flags"],
        )
    gate.embedded_oracles.append(
        {
            "name": "independent-parser-grammar",
            "schema": oracle.SCHEMA,
            "seed": oracle.SEED,
            "source_sha256": hashlib.sha256(
                FROZEN_PARSER_GRAMMAR_SOURCE.encode("utf-8")
            ).hexdigest(),
            "families": list(oracle.FAMILIES),
            "cases_per_family": PARSER_GRAMMAR_CASES_PER_FAMILY,
            "cases": len(cases),
            "fixture_sha256": actual_fixture_digest,
        }
    )


def complete_identity_trace(match, subject):
    if match is None:
        return None
    groups = []
    for index in range(match.re.groups + 1):
        value = match.group(index)
        indexed = match[index]
        groups.append(
            {
                "group": index,
                "value": normalise(value),
                "same_subject": value is subject,
                "indexed_value": normalise(indexed),
                "indexed_same_subject": indexed is subject,
                "indexed_same_value": indexed is value,
            }
        )
    values = match.groups()
    named = match.groupdict()
    return {
        "span": normalise(match.span()),
        "groups": groups,
        "all_groups": normalise(values),
        "all_group_subject_identity": [item is subject for item in values],
        "named": normalise(named),
        "named_subject_identity": {
            key: item is subject for key, item in sorted(named.items())
        },
        "subject_identity": match.string is subject,
        "registers_identity": match.regs is match.regs,
        "expanded_zero": attempted(lambda: match.expand(rb"\g<0>")),
    }


def expanded_bytes_identity(gate):
    patterns = (
        rb".*", rb".+", rb"a*", rb"a+", rb"(a*)", rb"(.*)",
        rb"(?P<whole>.*)", rb"(a+)(b*)", rb"((?:a|b)*)",
        rb"(?:(a)|b)*", rb".?", rb".*?", rb"([\s\S]*)",
        rb"(?P<left>[a-z]*)(?P<right>[0-9]*)", rb"(?:ab)*", rb"(?=a)|a",
    )
    lengths = (0, 1, 2, 3, 7, 31, 63, 64, 65, 127, 128, 129)
    operations = (
        "search", "match", "fullmatch", "finditer",
        "scanner-search", "scanner-match", "findall",
    )

    def source_rows(length):
        payload = (b"ab17" * (length // 4 + 1))[:length]
        return (
            ("exact-bytes", payload),
            ("bytes-subclass", BytesSubclass(payload)),
            ("bytearray", bytearray(payload)),
            ("readonly-view", memoryview(payload)),
            ("mutable-view", memoryview(bytearray(payload))),
        )

    def action(module, pattern, subject, operation, pos, endpos):
        compiled = module.compile(pattern)
        if operation in ("search", "match", "fullmatch"):
            return complete_identity_trace(
                getattr(compiled, operation)(subject, pos, endpos), subject
            )
        if operation == "finditer":
            iterator = compiled.finditer(subject, pos, endpos)
            values = [
                complete_identity_trace(item, subject)
                for item in itertools.islice(iterator, 2 * len(subject) + 4)
            ]
            if len(values) >= 2 * len(subject) + 4:
                raise RuntimeError("bytes identity finditer did not terminate")
            return values
        if operation == "scanner-search":
            scanner = compiled.scanner(subject, pos, endpos)
            values = []
            for _ in range(2 * len(subject) + 4):
                item = scanner.search()
                if item is None:
                    return values
                values.append(complete_identity_trace(item, subject))
            raise RuntimeError("bytes identity scanner failed to terminate")
        if operation == "scanner-match":
            return complete_identity_trace(
                compiled.scanner(subject, pos, endpos).match(), subject
            )
        if operation == "findall":
            values = compiled.findall(subject, pos, endpos)
            return {
                "values": normalise(values),
                "whole_subject_identity": [item is subject for item in values],
                "adjacent_identity": [
                    values[index] is values[index + 1]
                    for index in range(max(0, len(values) - 1))
                ],
            }
        raise ValueError(f"unknown expanded bytes identity action: {operation}")

    before = gate.counts["expanded-whole-bytes-identity"]
    for pattern_index, expression in enumerate(patterns):
        for length in lengths:
            for source_name, subject in source_rows(length):
                ranges = tuple(
                    dict.fromkeys(
                        ((0, length), (1, length), (0, max(0, length - 1)))
                    )
                )
                for pos, endpos in ranges:
                    for operation in operations:
                        gate.compare(
                            "expanded-whole-bytes-identity",
                            f"p{pattern_index:02d}:{source_name}:"
                            f"len={length}:{operation}:{pos}:{endpos}",
                            lambda expression=expression, subject=subject,
                                   operation=operation, pos=pos, endpos=endpos:
                                action(re, expression, subject, operation, pos, endpos),
                            lambda expression=expression, subject=subject,
                                   operation=operation, pos=pos, endpos=endpos:
                                action(
                                    gate.candidate, expression, subject,
                                    operation, pos, endpos
                                ),
                            pattern=expression,
                            source=source_name,
                            length=length,
                            operation=operation,
                            pos=pos,
                            endpos=endpos,
                        )
    observed = gate.counts["expanded-whole-bytes-identity"] - before
    if observed != 19_600:
        raise RuntimeError(f"frozen expanded bytes identity count changed: {observed}")


def inverted_windows(gate):
    cases = (
        (
            "repeat-unicode-lookbehind",
            r"(?<!x)(?P<value>[\x00-\x7f])?\b",
            "!!  xſ",
            int(re.IGNORECASE | re.MULTILINE),
            5,
            4,
        ),
        (
            "bytes-multiline-newline",
            rb"^|$",
            b"a\x1c\xff\nAB",
            int(re.MULTILINE),
            3,
            1,
        ),
        ("text-multiline-newline", r"^|$", "a\x1c\xff\nAB", int(re.MULTILINE), 3, 1),
        ("text-boundary", r"\b", "!a!", 0, 2, 1),
        ("text-nonboundary", r"\B", "aa", 0, 1, 0),
        ("text-end-anchor", r"$", "a\n", int(re.MULTILINE), 1, 0),
        ("bytes-end-anchor", rb"$", b"a\n", int(re.MULTILINE), 1, 0),
    )
    for name, pattern, raw, flags, pos, endpos in cases:
        variants = (
            (("text", raw), ("text-subclass", TextSubclass(raw)))
            if isinstance(raw, str)
            else (
                ("bytes", raw),
                ("bytes-subclass", BytesSubclass(raw)),
                ("bytearray", bytearray(raw)),
                ("memoryview", memoryview(raw)),
            )
        )
        for kind, subject in variants:
            quantified_semantics(
                gate,
                "inverted-window-zero-width",
                f"{name}:{kind}:seed={REPEAT_SEED}",
                pattern,
                subject,
                flags,
                ((pos, endpos),),
            )


def generated_cases(gate, cases):
    rng = random.Random(gate.seed)
    text_patterns = (
        r"", r"|.", r".|", r".*?", r"(a)?", r"\s*", r"\w+", r"\W+",
        r"\b|\B", r"(?=\w)|.", r"(?=(a))a", r"(?!(a))b",
        r"(?<=(a))b", r"(?:(a)b|a)(?(1)c|d)", r"(a(b)?)+",
        r"(?a:\w+)|(?u:\w+)", r"[A-Z]+", r"[^\x00-\xff]+",
        r"(?P<x>[a-z])-(?P=x)", r"(?:a?)*?", r"^|$",
    )
    byte_patterns = (
        rb"", rb"|.", rb".|", rb".*?", rb"(a)?", rb"\s*", rb"\w+",
        rb"\b|\B", rb"(?=\w)|.", rb"(?=(a))a", rb"(?<=(a))b",
        rb"(?:(a)b|a)(?(1)c|d)", rb"(?P<x>[a-z])-(?P=x)", rb"^|$",
    )
    alphabet = (
        "aAbBzZ09_- \t\n\x1c\x1f\x85\xe9\xdf\u0130\u0131"
        "\u017f\u212a\u03a3\u03c2\u0663\u96ea\U0001f600\ud800"
    )
    for index in range(cases):
        binary = index % 4 == 3
        if binary:
            pattern = rng.choice(byte_patterns)
            raw = bytes(rng.randrange(256) for _ in range(rng.randrange(17)))
            variant = rng.randrange(4)
            subject = (
                raw if variant == 0 else bytearray(raw) if variant == 1
                else memoryview(raw) if variant == 2 else BytesSubclass(raw)
            )
            flags = rng.choice((0, re.IGNORECASE, re.ASCII, re.MULTILINE, re.DOTALL))
        else:
            pattern = rng.choice(text_patterns)
            subject = "".join(rng.choice(alphabet) for _ in range(rng.randrange(17)))
            if index % 11 == 0:
                subject = TextSubclass(subject)
            flags = rng.choice(
                (0, re.IGNORECASE, re.ASCII, re.ASCII | re.IGNORECASE,
                 re.MULTILINE, re.DOTALL)
            )
        exercise_pattern(
            gate,
            "seeded-edges",
            f"seed={gate.seed}:case={index}",
            pattern,
            subject,
            flags,
            collections_enabled=index % 4 == 0,
        )


def candidate_artifacts(module, module_name):
    paths = [("public-python", Path(module.__file__).resolve())]
    native_modules = {
        "candidates.rust_candidate": ("candidates._rust_bridge", "_rust_engine.so"),
        "candidates.zig_candidate": ("candidates._zig_bridge", "_zig_probe.so"),
        "candidates.vm_candidate": ("candidates._vm_native", None),
    }
    if module_name in native_modules:
        native_name, engine_name = native_modules[module_name]
        native = importlib.import_module(native_name)
        paths.append(("native-bridge", Path(native.__file__).resolve()))
        if engine_name is not None:
            paths.append(("native-engine", (ROOT / "candidates" / engine_name).resolve()))
    if module_name == "candidates.rust_candidate":
        paths.extend(
            (
                ("native-source", ROOT / "candidates" / "rust" / "src" / "lib.rs"),
                ("bridge-source", ROOT / "candidates" / "rust" / "py_bridge.c"),
            )
        )
    result = []
    for role, path in paths:
        relative = (
            str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
        )
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        result.append({"role": role, "path": relative, "sha256": digest})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", default="candidates.rust_candidate")
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--seeded-cases", type=int, default=8)
    parser.add_argument("--unicode-stride", type=int, default=4099)
    args = parser.parse_args()
    if args.seeded_cases < 0:
        parser.error("--seeded-cases must be nonnegative")
    if not 1 <= args.unicode_stride < FULL_PLANE:
        parser.error("--unicode-stride must be in [1, 0x110000)")
    output = Path(args.output).resolve()
    allowed_output = (
        Path("/tmp").resolve(),
        (ROOT / "candidates" / "evidence").resolve(),
    )
    if not any(output.is_relative_to(parent) for parent in allowed_output):
        parser.error("--output must resolve under /tmp or candidates/evidence")
    if platform.python_implementation() != "CPython" or tuple(sys.version_info[:3]) != PINNED_PYTHON:
        parser.error("this gate requires pinned CPython 3.14.6")
    if unicodedata.unidata_version != PINNED_UNICODE:
        parser.error("this gate requires Unicode 16.0.0")
    locale.setlocale(locale.LC_CTYPE, "C")
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))
    candidate = importlib.import_module(args.module)
    artifacts = candidate_artifacts(candidate, args.module)
    gate = DifferentialGate(candidate, args.seed)

    print(
        json.dumps(
            {
                "schema": SCHEMA,
                "phase": "start",
                "python": platform.python_version(),
                "unicode": unicodedata.unidata_version,
                "module": args.module,
                "seed": args.seed,
                "seeded_cases": args.seeded_cases,
                "unicode_stride": args.unicode_stride,
            },
            sort_keys=True,
        ),
        flush=True,
    )

    stages = (
        ("unicode-membership", lambda: unicode_membership(gate, args.unicode_stride)),
        ("byte-membership", lambda: exhaustive_bytes(gate)),
        ("zero-width-and-lookaround", lambda: zero_width_and_lookaround(gate)),
        ("backreferences", lambda: backreferences(gate)),
        ("parser-escapes", lambda: parser_escapes(gate)),
        ("mutable-scanners", lambda: mutable_scanners(gate)),
        ("seeded-edges", lambda: generated_cases(gate, args.seeded_cases)),
        ("c0-unicode-scoped-whitespace", lambda: scoped_c0_whitespace(gate)),
        ("whole-bytes-object-identity", lambda: exact_bytes_identity(gate)),
        ("expanded-whole-bytes-identity", lambda: expanded_bytes_identity(gate)),
        ("module-signatures-and-hash", lambda: module_signatures_and_hashes(gate)),
        ("quantified-zero-width-assertions", lambda: quantified_assertions(gate)),
        ("memory-safety-seeded-valid-grammar", lambda: memory_seeded_assertions(gate)),
        ("grammar-quantified-lookaround", lambda: grammar_assertion_controls(gate)),
        ("inverted-window-zero-width", lambda: inverted_windows(gate)),
        ("public-object-and-buffer-contract", lambda: public_object_contract(gate)),
        ("independent-object-contract", lambda: independent_object_contract(gate)),
        ("independent-parser-grammar", lambda: independent_parser_grammar(gate)),
    )
    for name, run in stages:
        before_count = sum(gate.counts.values())
        before_failures = len(gate.failures)
        run()
        print(
            json.dumps(
                {
                    "phase": name,
                    "checks": sum(gate.counts.values()) - before_count,
                    "failures": len(gate.failures) - before_failures,
                    "total_checks": sum(gate.counts.values()),
                    "total_failures": len(gate.failures),
                },
                sort_keys=True,
            ),
            flush=True,
        )

    report = {
        "schema": SCHEMA,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "oracle": "CPython standard-library re",
        "python": platform.python_version(),
        "unicode": unicodedata.unidata_version,
        "locale": locale.setlocale(locale.LC_CTYPE),
        "module": args.module,
        "seed": args.seed,
        "independent_source_seeds": {
            "edge_generation": args.seed,
            "memory_safety": MEMORY_SAFETY_SEED,
            "repeat_stream": REPEAT_SEED,
            "module_api": MODULE_API_SEED,
            "object_contract": OBJECT_CONTRACT_SEED,
            "parser_grammar": PARSER_GRAMMAR_SEED,
        },
        "seeded_cases": args.seeded_cases,
        "unicode_stride": args.unicode_stride,
        "json_normalization": {
            "lone_surrogates": "surrogatepass_utf8_hex",
        },
        "candidate_artifacts": artifacts,
        "embedded_frozen_oracles": gate.embedded_oracles,
        "correctness_checks": sum(gate.counts.values()),
        "categories": dict(sorted(gate.counts.items())),
        "membership_partitions": gate.membership,
        "expected_sha256": gate.expected_digest.hexdigest(),
        "actual_sha256": gate.actual_digest.hexdigest(),
        "failed": len(gate.failures),
        "failures": gate.failures,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (
        json.dumps(
            portable_json_report(report),
            ensure_ascii=True,
            sort_keys=True,
            indent=2,
        )
        + "\n"
    ).encode("utf-8")
    if output.suffix == ".gz":
        output.write_bytes(gzip.compress(encoded, compresslevel=9, mtime=0))
    else:
        output.write_bytes(encoded)
    print(
        json.dumps(
            {key: value for key, value in report.items() if key not in {"failures", "membership_partitions"}},
            sort_keys=True,
        ),
        flush=True,
    )
    for failure in gate.failures[:5]:
        print(
            json.dumps(
                portable_json_report(failure),
                ensure_ascii=True,
                sort_keys=True,
            ),
            flush=True,
        )
    raise SystemExit(bool(gate.failures))


if __name__ == "__main__":
    main()
