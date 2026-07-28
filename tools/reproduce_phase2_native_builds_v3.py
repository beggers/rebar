#!/usr/bin/env python3
"""Independently reproduce the three owned, offline version-three native builds.

``--self-test`` is synthetic and has no filesystem, compiler, subprocess,
clock, candidate, network, or holdout effects.  ``--build`` is a separately
authorized, explicitly hash-pinned operation.  It never imports a candidate,
loads a native library, runs a matcher, or measures performance.
"""

from __future__ import annotations

import ast
import base64
import builtins
import copy
import gzip
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import tomllib
import zlib
from typing import Any


ROOT = Path(os.path.abspath(__file__)).parent.parent
SOURCE_RELATIVE = "tools/reproduce_phase2_native_builds_v3.py"
PROTOCOL_RELATIVE = "oracle/phase2/NATIVE-SOURCE-BUILDS-V3.md"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
SCHEMA = "rebar-phase2-independent-native-source-build-v3"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
WORK_PREFIX = "rebar-phase2-native-build-v3-"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PYTHON_INCLUDE = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14"
)
RUST_TOOLCHAIN = (
    "/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu"
)
PINNED_RUSTC = RUST_TOOLCHAIN + "/bin/rustc"
PINNED_CARGO = RUST_TOOLCHAIN + "/bin/cargo"
PINNED_RUST_DRIVER = (
    RUST_TOOLCHAIN + "/lib/librustc_driver-6108105cd7e839cf.so"
)
PINNED_GCC = "/usr/bin/x86_64-linux-gnu-gcc-13"
PINNED_READELF = "/usr/bin/x86_64-linux-gnu-readelf"
ZIG_COMPILER = "/tmp/zig-x86_64-linux-0.16.0/zig"
ZIG_ARCHIVE = "/tmp/rebar-zig-0.16.0-x86_64-linux.tar.xz"

# This first C build is authentic historical evidence, not a V2 proof.  The
# complete two GNU readelf streams are identical.  Embedding that actual stream
# lets synthetic controls expose the old parser without touching the archive.
HISTORICAL_V1_SOURCE = (
    "tools/reproduce_phase2_native_builds_v1.py",
    "e4cee196fcd6ff0908f46c26ef66363aa059e3003f2e89b302df10f35f9a3afd",
)
HISTORICAL_V1_PROTOCOL = (
    "oracle/phase2/NATIVE-SOURCE-BUILDS-V1.md",
    "33c495f6852155130c92af73422b7a6c6aae26b1c7012e65e2ddddab028064a2",
)
HISTORICAL_V1_C_ARCHIVE = (
    "oracle/phase2/evidence/native-source-build-v1-c-phase2-v1.json.gz",
    "b7844048cde986cae25ec4dafadfbb6dc560f4ea86108b908fe074176423f2e2",
    8_942,
)
HISTORICAL_V1_C_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v1-c-phase2-v1-publication-receipt.json",
    "7736349d1e8dce83e47fdf741a4e34fb313d4d370a11a2d5563dba4468e55002",
    1_636,
)
HISTORICAL_V1_C_UNCOMPRESSED_SHA256 = (
    "70779c2751a805774a0b570e12f7d7f843dca45e06edf862136d184f27d297d3"
)
HISTORICAL_V1_C_UNCOMPRESSED_BYTES = 55_943
HISTORICAL_V1_C_SYMBOL_STDOUT_SHA256 = (
    "6a3188f92c0dfa2d3e11e0984cd0066187654067ca4f3db348d058628f08e885"
)
HISTORICAL_V1_C_SYMBOL_STDOUT_BYTES = 10_402
HISTORICAL_V1_C_SYMBOL_STDOUT_BASE64 = (
    b"ClN5bWJvbCB0YWJsZSAnLmR5bnN5bScgY29udGFpbnMgMTMyIGVudHJpZXM6CiAgIE51bTogICAgVmFsdWUgICAgICAg"
    b"ICAgU2l6ZSBUeXBlICAgIEJpbmQgICBWaXMgICAgICBOZHggTmFtZQogICAgIDA6IDAwMDAwMDAwMDAwMDAwMDAgICAg"
    b"IDAgTk9UWVBFICBMT0NBTCAgREVGQVVMVCAgVU5EIAogICAgIDE6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBF"
    b"ICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5RXhjX1JlY3Vyc2lvbkVycm9yCiAgICAgMjogMDAwMDAwMDAwMDAwMDAwMCAg"
    b"ICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBVTkQgUHlVbmljb2RlX0Zyb21Gb3JtYXQKICAgICAzOiAwMDAwMDAw"
    b"MDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeUZ1bmN0aW9uX0dldEdsb2JhbHMKICAg"
    b"ICA0OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeUxpc3RfTmV3CiAg"
    b"ICAgNTogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBVTkQgUHlEaWN0X1NpemUK"
    b"ICAgICA2OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeVRocmVhZFN0"
    b"YXRlX0dldEZyYW1lCiAgICAgNzogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBV"
    b"TkQgUHlNb2R1bGVfVHlwZQogICAgIDg6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVM"
    b"VCAgVU5EIFB5QXJnX1BhcnNlVHVwbGVBbmRLZXl3b3JkcwogICAgIDk6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9U"
    b"WVBFICBXRUFLICAgREVGQVVMVCAgVU5EIF9JVE1fZGVyZWdpc3RlclRNQ2xvbmVUYWJsZQogICAgMTA6IDAwMDAwMDAw"
    b"MDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5RGljdFByb3h5X05ldwogICAgMTE6IDAw"
    b"MDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5VHVwbGVfVHlwZQogICAgMTI6"
    b"IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5T2JqZWN0X0NsZWFyV2Vh"
    b"a1JlZnMKICAgIDEzOiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeU1v"
    b"ZHVsZURlZl9Jbml0CiAgICAxNDogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBV"
    b"TkQgX1B5X2FzY2lpX3doaXRlc3BhY2UKICAgIDE1OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFM"
    b"IERFRkFVTFQgIFVORCBQeU9iamVjdF9DYWxsTWV0aG9kCiAgICAxNjogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZ"
    b"UEUgIEdMT0JBTCBERUZBVUxUICBVTkQgUHlNZW1fRnJlZQogICAgMTc6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9U"
    b"WVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5QnVmZmVyX1JlbGVhc2UKICAgIDE4OiAwMDAwMDAwMDAwMDAwMDAwICAg"
    b"ICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeVVuaWNvZGVXcml0ZXJfRmluaXNoCiAgICAxOTogMDAwMDAw"
    b"MDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBVTkQgUHlPYmplY3RfR2V0QXR0clN0cmluZwog"
    b"ICAgMjA6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5VW5pY29kZV9K"
    b"b2luCiAgICAyMTogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBVTkQgUHlFeGNf"
    b"QnVmZmVyRXJyb3IKICAgIDIyOiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVO"
    b"RCBQeU9iamVjdF9DYWxsT25lQXJnCiAgICAyMzogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBE"
    b"RUZBVUxUICBVTkQgUHlCdWZmZXJfSXNDb250aWd1b3VzCiAgICAyNDogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZ"
    b"UEUgIEdMT0JBTCBERUZBVUxUICBVTkQgUHlCeXRlc19Gcm9tU3RyaW5nQW5kU2l6ZQogICAgMjU6IDAwMDAwMDAwMDAw"
    b"MDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5Qnl0ZXNfVHlwZQogICAgMjY6IDAwMDAwMDAw"
    b"MDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIF9QeV9EZWFsbG9jCiAgICAyNzogMDAwMDAw"
    b"MDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBVTkQgUHlFcnJfTm9NZW1vcnkKICAgIDI4OiAw"
    b"MDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBfUHlfTm90SW1wbGVtZW50ZWRT"
    b"dHJ1Y3QKICAgIDI5OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeVVu"
    b"aWNvZGVXcml0ZXJfV3JpdGVTdWJzdHJpbmcKICAgIDMwOiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xP"
    b"QkFMIERFRkFVTFQgIFVORCBQeU9iamVjdF9SaWNoQ29tcGFyZQogICAgMzE6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAg"
    b"Tk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5T2JqZWN0X0dDX1RyYWNrCiAgICAzMjogMDAwMDAwMDAwMDAwMDAw"
    b"MCAgICAgMCBGVU5DICAgIEdMT0JBTCBERUZBVUxUICBVTkQgX19zdGFja19jaGtfZmFpbEBHTElCQ18yLjQgKDIpCiAg"
    b"ICAzMzogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBVTkQgUHlFeGNfUnVudGlt"
    b"ZUVycm9yCiAgICAzNDogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBVTkQgUHlD"
    b"TWV0aG9kX05ldwogICAgMzU6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5E"
    b"IFB5RXJyX1NldFN0cmluZwogICAgMzY6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVM"
    b"VCAgVU5EIF9QeU9iamVjdF9HQ19OZXcKICAgIDM3OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFM"
    b"IERFRkFVTFQgIFVORCBQeUV4Y19WYWx1ZUVycm9yCiAgICAzODogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUg"
    b"IEdMT0JBTCBERUZBVUxUICBVTkQgUHlNb2R1bGVfR2V0U3RhdGUKICAgIDM5OiAwMDAwMDAwMDAwMDAwMDAwICAgICAw"
    b"IE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeUV4Y19UeXBlRXJyb3IKICAgIDQwOiAwMDAwMDAwMDAwMDAwMDAw"
    b"ICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeVR5cGVfR2VuZXJpY05ldwogICAgNDE6IDAwMDAwMDAw"
    b"MDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5SW5kZXhfQ2hlY2sKICAgIDQyOiAwMDAw"
    b"MDAwMDAwMDAwMDAwICAgICAwIEZVTkMgICAgR0xPQkFMIERFRkFVTFQgIFVORCBfX2Fzc2VydF9mYWlsQEdMSUJDXzIu"
    b"Mi41ICgzKQogICAgNDM6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5"
    b"X0dlbmVyaWNBbGlhc1R5cGUKICAgIDQ0OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFV"
    b"TFQgIFVORCBQeU1lbV9SZWFsbG9jCiAgICA0NTogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBE"
    b"RUZBVUxUICBVTkQgUHlNZW1vcnlWaWV3X1R5cGUKICAgIDQ2OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAg"
    b"R0xPQkFMIERFRkFVTFQgIFVORCBQeUVycl9FeGNlcHRpb25NYXRjaGVzCiAgICA0NzogMDAwMDAwMDAwMDAwMDAwMCAg"
    b"ICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBVTkQgUHlfR2V0UmVjdXJzaW9uTGltaXQKICAgIDQ4OiAwMDAwMDAw"
    b"MDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeUxvbmdfRnJvbVNzaXplX3QKICAgIDQ5"
    b"OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIEZVTkMgICAgR0xPQkFMIERFRkFVTFQgIFVORCBtZW1jaHJAR0xJQkNfMi4y"
    b"LjUgKDMpCiAgICA1MDogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBGVU5DICAgIEdMT0JBTCBERUZBVUxUICBVTkQgbWVt"
    b"Y21wQEdMSUJDXzIuMi41ICgzKQogICAgNTE6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVG"
    b"QVVMVCAgVU5EIFB5TG9uZ19Bc1NzaXplX3QKICAgIDUyOiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xP"
    b"QkFMIERFRkFVTFQgIFVORCBQeU9iamVjdF9SaWNoQ29tcGFyZUJvb2wKICAgIDUzOiAwMDAwMDAwMDAwMDAwMDAwICAg"
    b"ICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeU9iamVjdF9DaGVja0J1ZmZlcgogICAgNTQ6IDAwMDAwMDAw"
    b"MDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5TW9kdWxlX0dldERlZgogICAgNTU6IDAw"
    b"MDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5RXJyX0NsZWFyCiAgICA1Njog"
    b"MDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBVTkQgUHlMaXN0X0FwcGVuZAogICAg"
    b"NTc6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgRlVOQyAgICBHTE9CQUwgREVGQVVMVCAgVU5EIF9fbWVtY3B5X2Noa0BH"
    b"TElCQ18yLjMuNCAoNCkKICAgIDU4OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQg"
    b"IFVORCBfUHlfRmFsc2VTdHJ1Y3QKICAgIDU5OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgV0VBSyAgIERF"
    b"RkFVTFQgIFVORCBfX2dtb25fc3RhcnRfXwogICAgNjA6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9C"
    b"QUwgREVGQVVMVCAgVU5EIFB5TW9kdWxlX0FkZE9iamVjdFJlZgogICAgNjE6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAg"
    b"Tk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5VHlwZV9HZXRNb2R1bGUKICAgIDYyOiAwMDAwMDAwMDAwMDAwMDAw"
    b"ICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeVR1cGxlX05ldwogICAgNjM6IDAwMDAwMDAwMDAwMDAw"
    b"MDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5T2JqZWN0X0dlbmVyaWNHZXRBdHRyCiAgICA2NDog"
    b"MDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBVTkQgUHlUaHJlYWRTdGF0ZV9HZXQK"
    b"ICAgIDY1OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIEZVTkMgICAgR0xPQkFMIERFRkFVTFQgIFVORCBtZW1jcHlAR0xJ"
    b"QkNfMi4xNCAoNSkKICAgIDY2OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVO"
    b"RCBQeUFyZ19VbnBhY2tUdXBsZQogICAgNjc6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVG"
    b"QVVMVCAgVU5EIFB5X0J1aWxkVmFsdWUKICAgIDY4OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFM"
    b"IERFRkFVTFQgIFVORCBQeVVuaWNvZGVfRnJvbU9iamVjdAogICAgNjk6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9U"
    b"WVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIF9QeVVuaWNvZGVfSXNEZWNpbWFsRGlnaXQKICAgIDcwOiAwMDAwMDAwMDAw"
    b"MDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeUVycl9PY2N1cnJlZAogICAgNzE6IDAwMDAw"
    b"MDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIF9QeVVuaWNvZGVfSXNXaGl0ZXNwYWNl"
    b"CiAgICA3MjogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBVTkQgUHlVbmljb2Rl"
    b"X1JlcGxhY2UKICAgIDczOiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQ"
    b"eU9iamVjdF9DYWxsRnVuY3Rpb25PYmpBcmdzCiAgICA3NDogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdM"
    b"T0JBTCBERUZBVUxUICBVTkQgUHlEaWN0X0dldEl0ZW1TdHJpbmcKICAgIDc1OiAwMDAwMDAwMDAwMDAwMDAwICAgICAw"
    b"IE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeVVuaWNvZGVfQ29tcGFyZVdpdGhBU0NJSVN0cmluZwogICAgNzY6"
    b"IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5VW5pY29kZV9GaW5kCiAg"
    b"ICA3NzogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBVTkQgX1B5X05vbmVTdHJ1"
    b"Y3QKICAgIDc4OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeUFyZ19Q"
    b"YXJzZVR1cGxlCiAgICA3OTogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBVTkQg"
    b"UHlUeXBlX0dlbmVyaWNBbGxvYwogICAgODA6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVG"
    b"QVVMVCAgVU5EIF9QeVVuaWNvZGVfSXNBbHBoYQogICAgODE6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBH"
    b"TE9CQUwgREVGQVVMVCAgVU5EIFB5T2JqZWN0X0hhc2gKICAgIDgyOiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQ"
    b"RSAgR0xPQkFMIERFRkFVTFQgIFVORCBfUHlfVHJ1ZVN0cnVjdAogICAgODM6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAg"
    b"Tk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5VHlwZV9HZXRNb2R1bGVTdGF0ZQogICAgODQ6IDAwMDAwMDAwMDAw"
    b"MDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5Qnl0ZXNfSm9pbgogICAgODU6IDAwMDAwMDAw"
    b"MDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5Q2FsbEl0ZXJfTmV3CiAgICA4NjogMDAw"
    b"MDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBVTkQgUHlGdW5jdGlvbl9UeXBlCiAgICA4"
    b"NzogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBVTkQgUHlVbmljb2RlV3JpdGVy"
    b"X0NyZWF0ZQogICAgODg6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5"
    b"RGljdF9OZXcKICAgIDg5OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQ"
    b"eUV4Y19JbmRleEVycm9yCiAgICA5MDogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxU"
    b"ICBVTkQgUHlCb29sX1R5cGUKICAgIDkxOiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFV"
    b"TFQgIFVORCBQeUNhbGxhYmxlX0NoZWNrCiAgICA5MjogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JB"
    b"TCBERUZBVUxUICBVTkQgUHlPYmplY3RfR2V0QnVmZmVyCiAgICA5MzogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZ"
    b"UEUgIEdMT0JBTCBERUZBVUxUICBVTkQgUHlEaWN0X1R5cGUKICAgIDk0OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5P"
    b"VFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeURpY3RfTmV4dAogICAgOTU6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAg"
    b"Tk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIF9QeVVuaWNvZGVfSXNEaWdpdAogICAgOTY6IDAwMDAwMDAwMDAwMDAw"
    b"MDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5QmFzZU9iamVjdF9UeXBlCiAgICA5NzogMDAwMDAw"
    b"MDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZBVUxUICBVTkQgUHlMb25nX0Zyb21VbnNpZ25lZExvbmcK"
    b"ICAgIDk4OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeUxvbmdfVHlw"
    b"ZQogICAgOTk6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5VW5pY29k"
    b"ZVdyaXRlcl9Xcml0ZVN0cgogICAxMDA6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVM"
    b"VCAgVU5EIFB5RGljdF9TZXRJdGVtCiAgIDEwMTogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBE"
    b"RUZBVUxUICBVTkQgUHlPYmplY3RfR2VuZXJpY1NldEF0dHIKICAgMTAyOiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5P"
    b"VFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeUZyYW1lX0dldEJhY2sKICAgMTAzOiAwMDAwMDAwMDAwMDAwMDAwICAg"
    b"ICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeUV4Y19BdHRyaWJ1dGVFcnJvcgogICAxMDQ6IDAwMDAwMDAw"
    b"MDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5T2JqZWN0X1JlcHIKICAgMTA1OiAwMDAw"
    b"MDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeVR5cGVfRnJvbU1vZHVsZUFuZFNw"
    b"ZWMKICAgMTA2OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeVVuaWNv"
    b"ZGVfVHlwZQogICAxMDc6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5"
    b"Q2Fwc3VsZV9OZXcKICAgMTA4OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVO"
    b"RCBQeVR5cGVfSXNTdWJ0eXBlCiAgIDEwOTogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdMT0JBTCBERUZB"
    b"VUxUICBVTkQgUHlVbmljb2RlV3JpdGVyX0Rpc2NhcmQKICAgMTEwOiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQ"
    b"RSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeUVycl9Gb3JtYXQKICAgMTExOiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5P"
    b"VFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeUJ5dGVzX0Zyb21PYmplY3QKICAgMTEyOiAwMDAwMDAwMDAwMDAwMDAw"
    b"ICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeUNhcHN1bGVfR2V0UG9pbnRlcgogICAxMTM6IDAwMDAw"
    b"MDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIF9QeVVuaWNvZGVfVG9VcHBlcmNhc2UK"
    b"ICAgMTE0OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBfUHlVbmljb2Rl"
    b"X0lzTnVtZXJpYwogICAxMTU6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBXRUFLICAgREVGQVVMVCAgVU5E"
    b"IF9JVE1fcmVnaXN0ZXJUTUNsb25lVGFibGUKICAgMTE2OiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xP"
    b"QkFMIERFRkFVTFQgIFVORCBQeVVuaWNvZGVfRnJvbU9yZGluYWwKICAgMTE3OiAwMDAwMDAwMDAwMDAwMDAwICAgICAw"
    b"IE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeU51bWJlcl9JbmRleAogICAxMTg6IDAwMDAwMDAwMDAwMDAwMDAg"
    b"ICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5TWVtX0NhbGxvYwogICAxMTk6IDAwMDAwMDAwMDAwMDAw"
    b"MDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIF9QeVVuaWNvZGVfVG9Mb3dlcmNhc2UKICAgMTIwOiAw"
    b"MDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeVVuaWNvZGVfRmluZENoYXIK"
    b"ICAgMTIxOiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFMIERFRkFVTFQgIFVORCBQeU1lbV9NYWxs"
    b"b2MKICAgMTIyOiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIEZVTkMgICAgV0VBSyAgIERFRkFVTFQgIFVORCBfX2N4YV9m"
    b"aW5hbGl6ZUBHTElCQ18yLjIuNSAoMykKICAgMTIzOiAwMDAwMDAwMDAwMDAwMDAwICAgICAwIE5PVFlQRSAgR0xPQkFM"
    b"IERFRkFVTFQgIFVORCBQeVVuaWNvZGVfTmV3CiAgIDEyNDogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdM"
    b"T0JBTCBERUZBVUxUICBVTkQgUHlUdXBsZV9QYWNrCiAgIDEyNTogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUg"
    b"IEdMT0JBTCBERUZBVUxUICBVTkQgUHlPYmplY3RfR0NfVW5UcmFjawogICAxMjY6IDAwMDAwMDAwMDAwMDAwMDAgICAg"
    b"IDAgRlVOQyAgICBHTE9CQUwgREVGQVVMVCAgVU5EIF9fY3R5cGVfdG9sb3dlcl9sb2NAR0xJQkNfMi4zICg2KQogICAx"
    b"Mjc6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgRlVOQyAgICBHTE9CQUwgREVGQVVMVCAgVU5EIF9fY3R5cGVfYl9sb2NA"
    b"R0xJQkNfMi4zICg2KQogICAxMjg6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAgTk9UWVBFICBHTE9CQUwgREVGQVVMVCAg"
    b"VU5EIFB5RGljdF9HZXRJdGVtV2l0aEVycm9yCiAgIDEyOTogMDAwMDAwMDAwMDAwMDAwMCAgICAgMCBOT1RZUEUgIEdM"
    b"T0JBTCBERUZBVUxUICBVTkQgUHlVbmljb2RlX1N1YnN0cmluZwogICAxMzA6IDAwMDAwMDAwMDAwMDAwMDAgICAgIDAg"
    b"Tk9UWVBFICBHTE9CQUwgREVGQVVMVCAgVU5EIFB5U2VxdWVuY2VfRmFzdAogICAxMzE6IDAwMDAwMDAwMDAwMWQ3NTAg"
    b"ICAgMTYgRlVOQyAgICBHTE9CQUwgREVGQVVMVCAgIDE0IFB5SW5pdF9fdm1fbmF0aXZlCg=="
)
HISTORICAL_V1_C_TRUE_VERSIONED_SYMBOLS = frozenset({
    "__stack_chk_fail", "__assert_fail", "memchr", "memcmp",
    "__memcpy_chk", "memcpy", "__cxa_finalize",
    "__ctype_tolower_loc", "__ctype_b_loc",
})

MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_PROCESS_BYTES = 32 * 1024 * 1024
MAX_REPORT_BYTES = 48 * 1024 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_LABEL_BYTES = 48


PRESERVED_V2_SOURCE = (
    "tools/reproduce_phase2_native_builds_v2.py",
    "e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796",
    136_677,
)
PRESERVED_V2_PROTOCOL = (
    "oracle/phase2/NATIVE-SOURCE-BUILDS-V2.md",
    "f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603",
    13_032,
)
PRESERVED_V2_SCHEMA = "rebar-phase2-independent-native-source-build-v2"
PRESERVED_V2_OWNERS: dict[str, dict[str, str]] = {
    "c": {
        "candidates/_vm_native.c":
            "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55",
        "candidates/vm_candidate.py":
            "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096",
    },
    "rust": {
        "candidates/rust_candidate.py":
            "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
        "candidates/rust/py_bridge.c":
            "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
        "candidates/rust/Cargo.toml":
            "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966",
        "candidates/rust/Cargo.lock":
            "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63",
        "candidates/rust/src/lib.rs":
            "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d",
        "candidates/rust/src/newline.rs":
            "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b",
        "candidates/rust/src/search.rs":
            "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe",
        "candidates/rust/src/stack.rs":
            "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e",
        "candidates/rust/src/unicode_tables.rs":
            "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af",
    },
    "zig": {
        "candidates/zig_candidate.py":
            "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862",
        "candidates/zig/mini_regex.zig":
            "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28",
        "candidates/zig/py_bridge.c":
            "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b",
    },
}
PRESERVED_V2_RECORDS: tuple[dict[str, Any], ...] = (
    {
        "family": "c",
        "build_status": "PASS",
        "archive_path":
            "oracle/phase2/evidence/native-source-build-v2-c-phase2-v2.json.gz",
        "archive_sha256":
            "4d954992312a039daa46a2810e51fc29cfdd2bd49d159dc834f5bf003e456878",
        "archive_bytes": 16_016,
        "uncompressed_sha256":
            "0d0a67a3c8ebba83806ba3b9beaee39e154f9d0483f0e39aac6bb04ecbfc598a",
        "uncompressed_bytes": 169_716,
        "receipt_path":
            "oracle/phase2/evidence/"
            "native-source-build-v2-c-phase2-v2-publication-receipt.json",
        "receipt_sha256":
            "e90b4c12a087c0e8864c1627e242be18bd779f9d9693ec711f7dd575288eda24",
        "receipt_bytes": 1_639,
        "process_count": 8,
        "phase_outputs": (
            {"extension": (
                "ed57383dad99ce311664d165635fa300f3894df6b4816b5f54801d0e68263697",
                163_136,
            )},
            {"extension": (
                "ed57383dad99ce311664d165635fa300f3894df6b4816b5f54801d0e68263697",
                163_136,
            )},
        ),
    },
    {
        "family": "rust",
        "build_status": "PASS",
        "archive_path":
            "oracle/phase2/evidence/native-source-build-v2-rust-phase2-v2.json.gz",
        "archive_sha256":
            "69b645c14ca3e566256f5a5b393a6d18554ad347b97b542383db3d86681bb35d",
        "archive_bytes": 33_741,
        "uncompressed_sha256":
            "389a833d6a3ce6c7aed3216759278d97d8d02dd901f758815e002f7a0031d4ec",
        "uncompressed_bytes": 279_925,
        "receipt_path":
            "oracle/phase2/evidence/"
            "native-source-build-v2-rust-phase2-v2-publication-receipt.json",
        "receipt_sha256":
            "15580e4441ce651c21800df187fcfaa88ec9336322348a07d84544094d5b050e",
        "receipt_bytes": 2_346,
        "process_count": 16,
        "phase_outputs": (
            {
                "engine": (
                    "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f",
                    658_344,
                ),
                "bridge": (
                    "9e13396f93872222f77577ac7658609f5e2d3e77c0655a27c83572f0a1a06b4c",
                    148_536,
                ),
            },
            {
                "engine": (
                    "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f",
                    658_344,
                ),
                "bridge": (
                    "9e13396f93872222f77577ac7658609f5e2d3e77c0655a27c83572f0a1a06b4c",
                    148_536,
                ),
            },
        ),
    },
    {
        "family": "zig",
        "build_status": "FAIL",
        "archive_path":
            "oracle/phase2/evidence/"
            "native-source-build-v2-zig-phase2-v2-failures.json.gz",
        "archive_sha256":
            "dc5128aaaf8a4d915c57ea8770696db3dc7ca51c89d5a3570cab9d259d070a0e",
        "archive_bytes": 19_556,
        "uncompressed_sha256":
            "f6ea1eb57d9ceb23c6dc5d4f291c4eb300768460a658d97828b7ce0095c53652",
        "uncompressed_bytes": 188_479,
        "receipt_path":
            "oracle/phase2/evidence/"
            "native-source-build-v2-zig-phase2-v2-failures-publication-receipt.json",
        "receipt_sha256":
            "97e3150e9b68d3031c96ea6e973097687c80163a371f99a67f8b3de08bc0707a",
        "receipt_bytes": 1_766,
        "process_count": 15,
        "phase_outputs": (
            {
                "engine": (
                    "b73d43dc4bab42abc1de92e7aaf4a0b145e242ef8407714dc1bef48fc28a7d12",
                    480_040,
                ),
                "bridge": (
                    "c579cf52b767b84ecc3d0a60f837d526978ace4e7739fe4cf51c2d2c8cfd90d9",
                    133_656,
                ),
            },
            {
                "engine": (
                    "69a3f024c079b8994c4ffdbf37cbecf59d5afd67c8bcf5200a7331cae66d1f53",
                    480_040,
                ),
                "bridge": (
                    "c579cf52b767b84ecc3d0a60f837d526978ace4e7739fe4cf51c2d2c8cfd90d9",
                    133_656,
                ),
            },
        ),
    },
)

FAMILIES: dict[str, dict[str, Any]] = {
    "c": {
        "owners": (
            "candidates/vm_candidate.py",
            "candidates/_vm_native.c",
        ),
        "adapter_import": "_vm_native",
        "binaries": {"extension": "_vm_native" + EXTENSION_SUFFIX},
    },
    "rust": {
        "owners": (
            "candidates/rust_candidate.py",
            "candidates/rust/py_bridge.c",
            "candidates/rust/Cargo.toml",
            "candidates/rust/Cargo.lock",
            "candidates/rust/src/lib.rs",
            "candidates/rust/src/newline.rs",
            "candidates/rust/src/search.rs",
            "candidates/rust/src/stack.rs",
            "candidates/rust/src/unicode_tables.rs",
        ),
        "adapter_import": "_rust_bridge",
        "binaries": {
            "engine": "_rust_engine.so",
            "bridge": "_rust_bridge" + EXTENSION_SUFFIX,
        },
    },
    "zig": {
        "owners": (
            "candidates/zig_candidate.py",
            "candidates/zig/mini_regex.zig",
            "candidates/zig/py_bridge.c",
        ),
        "adapter_import": "_zig_bridge",
        "binaries": {
            "engine": "_zig_probe.so",
            "bridge": "_zig_bridge" + EXTENSION_SUFFIX,
        },
    },
}

FROZEN_INPUTS: tuple[tuple[str, str, str, int, int | None], ...] = (
    (
        "immutable_objective",
        "GOAL.md",
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
        MAX_SOURCE_BYTES,
        None,
    ),
    (
        "complete_correctness_manifest",
        "oracle/phase1/p0-completeness-v1.json",
        "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
        MAX_SOURCE_BYTES,
        45_632,
    ),
    (
        "complete_correctness_protocol",
        "oracle/phase1/P0-COMPLETENESS-V1.md",
        "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798",
        MAX_SOURCE_BYTES,
        10_392,
    ),
    (
        "complete_correctness_verifier",
        "tools/verify_p0_completeness_v1.py",
        "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c",
        MAX_SOURCE_BYTES,
        None,
    ),
    (
        "pinned_cpython_executable",
        PINNED_PYTHON,
        "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
        MAX_BINARY_BYTES,
        32_387_816,
    ),
    (
        "pinned_cpython_header",
        PYTHON_INCLUDE + "/Python.h",
        "e39aad93d70c3ea1a63b77ec5795ff59a5c177745aedace6f83bbf4275a20d9f",
        MAX_SOURCE_BYTES,
        None,
    ),
    (
        "pinned_cpython_patchlevel",
        PYTHON_INCLUDE + "/patchlevel.h",
        "1c61b149e1ce72a7f6328c58057970d37fcafb02bec805be071dc0ed4cf39a95",
        MAX_SOURCE_BYTES,
        None,
    ),
    (
        "pinned_host_gcc_13",
        PINNED_GCC,
        "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26",
        MAX_BINARY_BYTES,
        1_023_032,
    ),
    (
        "pinned_host_readelf",
        PINNED_READELF,
        "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0",
        MAX_BINARY_BYTES,
        789_280,
    ),

    (
        "preserved_v2_build_source",
        PRESERVED_V2_SOURCE[0],
        PRESERVED_V2_SOURCE[1],
        MAX_SOURCE_BYTES,
        PRESERVED_V2_SOURCE[2],
    ),
    (
        "preserved_v2_build_protocol",
        PRESERVED_V2_PROTOCOL[0],
        PRESERVED_V2_PROTOCOL[1],
        MAX_SOURCE_BYTES,
        PRESERVED_V2_PROTOCOL[2],
    ),
    (
        "preserved_v2_c_archive",
        PRESERVED_V2_RECORDS[0]["archive_path"],
        PRESERVED_V2_RECORDS[0]["archive_sha256"],
        MAX_ARCHIVE_BYTES,
        PRESERVED_V2_RECORDS[0]["archive_bytes"],
    ),
    (
        "preserved_v2_c_receipt",
        PRESERVED_V2_RECORDS[0]["receipt_path"],
        PRESERVED_V2_RECORDS[0]["receipt_sha256"],
        MAX_SOURCE_BYTES,
        PRESERVED_V2_RECORDS[0]["receipt_bytes"],
    ),
    (
        "preserved_v2_rust_archive",
        PRESERVED_V2_RECORDS[1]["archive_path"],
        PRESERVED_V2_RECORDS[1]["archive_sha256"],
        MAX_ARCHIVE_BYTES,
        PRESERVED_V2_RECORDS[1]["archive_bytes"],
    ),
    (
        "preserved_v2_rust_receipt",
        PRESERVED_V2_RECORDS[1]["receipt_path"],
        PRESERVED_V2_RECORDS[1]["receipt_sha256"],
        MAX_SOURCE_BYTES,
        PRESERVED_V2_RECORDS[1]["receipt_bytes"],
    ),
    (
        "preserved_v2_zig_archive",
        PRESERVED_V2_RECORDS[2]["archive_path"],
        PRESERVED_V2_RECORDS[2]["archive_sha256"],
        MAX_ARCHIVE_BYTES,
        PRESERVED_V2_RECORDS[2]["archive_bytes"],
    ),
    (
        "preserved_v2_zig_receipt",
        PRESERVED_V2_RECORDS[2]["receipt_path"],
        PRESERVED_V2_RECORDS[2]["receipt_sha256"],
        MAX_SOURCE_BYTES,
        PRESERVED_V2_RECORDS[2]["receipt_bytes"],
    ),
)

RUST_INPUTS: tuple[tuple[str, str, str, int, int | None], ...] = (
    (
        "pinned_rust_1_95_0_rustc",
        PINNED_RUSTC,
        "bff349e72704ff70bc08a234a3847338e797065bbedde5e556808bc87b7bf7c6",
        MAX_BINARY_BYTES,
        644_784,
    ),
    (
        "pinned_rust_1_95_0_cargo",
        PINNED_CARGO,
        "841072d1d92f9e841d9ba5b0814182a0adf064acf4527cd120967b7bc49dcb66",
        MAX_BINARY_BYTES,
        42_185_192,
    ),
    (
        "pinned_rust_1_95_0_compiler_driver",
        PINNED_RUST_DRIVER,
        "ae69468875215df490fde685ec1f1b969743482ba7e0251f4074a222606a5484",
        MAX_BINARY_BYTES,
        153_621_360,
    ),
)

ZIG_INPUTS: tuple[tuple[str, str, str, int, int | None], ...] = (
    (
        "pinned_official_zig_0_16_0_lock",
        "toolchains/zig-0.16.0.lock.json",
        "a0f105b47dd60bab9c3136a7b7a44ab417bc034e680bf2d30693cc954422b3cd",
        MAX_SOURCE_BYTES,
        628,
    ),
    (
        "pinned_official_zig_0_16_0_archive",
        ZIG_ARCHIVE,
        "70e49664a74374b48b51e6f3fdfbf437f6395d42509050588bd49abe52ba3d00",
        MAX_BINARY_BYTES,
        55_478_392,
    ),
    (
        "pinned_official_zig_0_16_0_compiler",
        ZIG_COMPILER,
        "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c",
        MAX_BINARY_BYTES,
        172_641_672,
    ),
)

RUST_ENGINE_EXPORTS = frozenset({
    "rebar_collect_ascii", "rebar_collect_wide", "rebar_compile",
    "rebar_compile_scanner", "rebar_error_copy", "rebar_error_include",
    "rebar_error_len", "rebar_error_pos", "rebar_flags", "rebar_free",
    "rebar_groups", "rebar_match", "rebar_match_ascii", "rebar_match_wide",
    "rebar_name_copy", "rebar_name_count", "rebar_name_group",
    "rebar_name_len",
})
ZIG_ENGINE_EXPORTS = frozenset({
    "rebar_zig_batch", "rebar_zig_collect_captures",
    "rebar_zig_collect_records", "rebar_zig_collect_records_wide",
    "rebar_zig_compile", "rebar_zig_compile_guarded", "rebar_zig_flags",
    "rebar_zig_free", "rebar_zig_groups", "rebar_zig_match",
    "rebar_zig_match_captures", "rebar_zig_match_captures_wide",
    "rebar_zig_match_inverted_wide", "rebar_zig_match_nonempty_wide",
    "rebar_zig_match_tree", "rebar_zig_match_wide", "rebar_zig_name_copy",
    "rebar_zig_name_count", "rebar_zig_name_group", "rebar_zig_name_length",
    "rebar_zig_program_memory", "rebar_zig_program_size",
})
FORBIDDEN_NATIVE_NAMES = frozenset({
    "dlmopen", "dlopen", "dlsym", "dlvsym", "execv", "execve", "fork",
    "popen", "posix_spawn", "regcomp", "regexec", "regfree", "system",
    "PyRun_AnyFile", "PyRun_SimpleString", "PyRun_String",
    "Py_CompileString", "PyEval_EvalCode",
})
FORBIDDEN_NATIVE_PREFIXES = (
    "hs_", "onig_", "pcre2_", "pcre_", "re2_", "regex_", "sre_", "_sre",
    "PyInit__sre", "PyRun_", "PyEval_Eval", "Py_CompileString",
)
FORBIDDEN_MODULES = frozenset({
    "re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
    "hyperscan", "sre_compile", "sre_constants", "sre_parse",
})
ALLOWED_SYSTEM_LIBRARIES = frozenset({
    "libc.so.6", "libm.so.6", "libgcc_s.so.1", "ld-linux-x86-64.so.2",
})
ALLOWED_BRIDGE_IMPORTS = frozenset({"copyreg", "functools", "inspect"})


class BuildError(Exception):
    """A frozen input, independent build, or native output failed closed."""


class SourceOnlyError(BuildError):
    """A synthetic-only control attempted a real external effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise BuildError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False,
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise BuildError("a complete finite canonical JSON record is required") from error


def valid_digest(value: Any) -> bool:
    return (
        type(value) is str and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def checked_digest(value: Any, description: str) -> str:
    require(valid_digest(value), "an exact lowercase SHA-256 is required: " + description)
    return value


def checked_family(value: Any) -> str:
    require(type(value) is str and value in FAMILIES,
            "select exactly one independent C, Rust, or Zig family")
    return value


def checked_relative(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 512,
            "a bounded, repository-relative source path is mandatory")
    require("\\" not in value and "\x00" not in value and not value.startswith("/"),
            "reject absolute paths, NULs, and alternate path separators")
    components = value.split("/")
    require(all(part not in ("", ".", "..") for part in components),
            "reject source-path traversal and empty components")
    return value


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= MAX_LABEL_BYTES,
            "supply one short, unique, non-overwriting build label")
    require(value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(ch in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in value)
            and "--" not in value and not value.endswith("-"),
            "a build label must contain only lowercase letters, digits, and single hyphens")
    return value


def checked_source_pins(family: Any, values: Any) -> dict[str, str]:
    name = checked_family(family)
    expected = FAMILIES[name]["owners"]
    require(type(values) is list and len(values) == len(expected),
            "pin every independently owned source exactly once: " + name)
    result: dict[str, str] = {}
    for value in values:
        require(type(value) is str and value.count("=") == 1,
                "an owned source pin must be exactly RELATIVE/PATH=SHA256")
        path, digest = value.split("=", 1)
        checked_relative(path)
        require(path in expected and path not in result,
                "reject missing, duplicated, cross-family, or foreign source owners")
        result[path] = checked_digest(digest, path)
    require(set(result) == set(expected),
            "the complete independent native source closure was not pinned")
    return dict(sorted(result.items()))


def unique_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result,
                "reject duplicate and non-string JSON keys")
        result[key] = value
    return result


def reject_json_constant(value: str) -> Any:
    raise BuildError("reject non-finite JSON values: " + value)


def decode_json(raw: Any, *, canonical_required: bool) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_REPORT_BYTES,
            "a complete bounded JSON source is required")
    try:
        document = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique_json_pairs,
            parse_constant=reject_json_constant,
        )
    except (ValueError, UnicodeError, RecursionError) as error:
        raise BuildError("a complete, duplicate-key-free JSON source is required") from error
    require(type(document) is dict, "a top-level JSON object is mandatory")
    if canonical_required:
        require(canonical(document) == raw,
                "a signed document changed its exact canonical encoding")
    return document


def authenticate_file(
    path: Path, *, expected: str | None, maximum: int,
    exact_size: int | None = None, capture: bool = False,
) -> tuple[dict[str, Any], bytes | None]:
    require(isinstance(path, Path) and path.is_absolute(),
            "authenticate only one absolute, bounded regular file")
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "reject an invalid authenticated byte limit")
    require(type(capture) is bool, "reject a forged source capture request")
    if exact_size is not None:
        require(type(exact_size) is int and 0 < exact_size <= maximum,
                "reject an invalid exact source or compiler byte count")
    descriptor = os.open(
        str(path), os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and 0 < before.st_size <= maximum,
                "an authenticated owner is not a bounded regular file")
        require(exact_size is None or before.st_size == exact_size,
                "an authenticated owner has a different exact byte count")
        digest = hashlib.sha256()
        kept = bytearray() if capture else None
        actual = 0
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            actual += len(block)
            require(actual <= maximum,
                    "an authenticated owner grew during its complete read")
            digest.update(block)
            if kept is not None:
                kept.extend(block)
        after = os.fstat(descriptor)
        require(
            actual == before.st_size == after.st_size
            and (before.st_dev, before.st_ino, before.st_mtime_ns,
                 before.st_ctime_ns)
            == (after.st_dev, after.st_ino, after.st_mtime_ns,
                after.st_ctime_ns),
            "an authenticated owner changed during its complete no-follow read",
        )
        visible = os.lstat(str(path))
        require(stat.S_ISREG(visible.st_mode)
                and (visible.st_dev, visible.st_ino, visible.st_size)
                == (after.st_dev, after.st_ino, after.st_size),
                "an authenticated owner path was replaced or redirected")
        observed = digest.hexdigest()
        if expected is not None:
            require(observed == checked_digest(expected, str(path)),
                    "an exact frozen owner or toolchain changed: " + str(path))
        return {
            "path": str(path), "sha256": observed,
            "size_bytes": actual, "device": after.st_dev, "inode": after.st_ino,
        }, bytes(kept) if kept is not None else None
    finally:
        os.close(descriptor)


def authenticate_specification(
    specification: tuple[str, str, str, int, int | None],
    *, capture: bool = False,
) -> tuple[str, dict[str, Any], bytes | None]:
    name, location, digest, maximum, exact_size = specification
    require(type(name) is str and bool(name), "an authenticated input name is missing")
    checked_digest(digest, name)
    path = Path(location) if location.startswith("/") else ROOT / checked_relative(location)
    result, raw = authenticate_file(
        path, expected=digest, maximum=maximum,
        exact_size=exact_size, capture=capture,
    )
    return name, result, raw


def validate_cargo_closure(manifest_bytes: Any, lock_bytes: Any) -> dict[str, Any]:
    require(type(manifest_bytes) is bytes and 0 < len(manifest_bytes) <= MAX_SOURCE_BYTES
            and type(lock_bytes) is bytes and 0 < len(lock_bytes) <= MAX_SOURCE_BYTES,
            "both complete owned Cargo inputs are mandatory")
    try:
        manifest = tomllib.loads(manifest_bytes.decode("utf-8"))
        lock = tomllib.loads(lock_bytes.decode("utf-8"))
    except (UnicodeError, tomllib.TOMLDecodeError) as error:
        raise BuildError("an exact dependency-free Rust Cargo closure is required") from error
    require(set(manifest) == {"package", "lib", "profile"},
            "reject external packages, registries, workspaces, build scripts, and patches")
    require(manifest["package"] == {
        "name": "rebar-rust-continuation", "version": "0.1.0",
        "edition": "2024", "rust-version": "1.85", "publish": False,
    }, "the exact unpublished independently owned Rust package changed")
    require(manifest["lib"] == {"crate-type": ["cdylib"]},
            "the Rust engine must be one independently owned native cdylib")
    require(manifest["profile"] == {"release": {
        "opt-level": 3, "lto": True, "codegen-units": 1, "panic": "abort",
    }}, "the exact independently reproducible Rust release profile changed")
    require(lock == {"version": 4, "package": [
        {"name": "rebar-rust-continuation", "version": "0.1.0"},
    ]}, "the Rust lockfile contains a foreign package, registry, or build hook")
    return {
        "package": "rebar-rust-continuation", "package_count": 1,
        "external_package_count": 0, "registry_count": 0,
        "build_script_count": 0, "locked": True, "offline": True,
    }


def native_tokens(raw: Any) -> list[tuple[str, str]]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES,
            "a complete bounded native source is required")
    try:
        text = raw.decode("utf-8")
    except UnicodeError as error:
        raise BuildError("native owner source must be valid UTF-8") from error
    tokens: list[tuple[str, str]] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if text.startswith("//", index):
            end = text.find("\n", index + 2)
            index = len(text) if end < 0 else end + 1
            continue
        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            require(end >= 0, "reject an unterminated native source comment")
            index = end + 2
            continue
        if (char == "'" and index + 1 < len(text)
                and (text[index + 1] == "_" or text[index + 1].isalpha())):
            lifetime_end = index + 2
            while lifetime_end < len(text) and (
                text[lifetime_end] == "_" or text[lifetime_end].isalnum()
            ):
                lifetime_end += 1
            if lifetime_end >= len(text) or text[lifetime_end] != "'":
                tokens.append(("punctuation", char))
                index += 1
                continue
        if char in "\"'":
            quote, start = char, index
            index += 1
            while index < len(text) and text[index] != quote:
                if text[index] == "\\":
                    index += 1
                index += 1
            require(index < len(text), "reject an unterminated native source string")
            tokens.append(("string", text[start + 1:index]))
            index += 1
            continue
        if char == "_" or char.isalpha():
            start = index
            index += 1
            while index < len(text) and (
                text[index] == "_" or text[index].isalnum()
            ):
                index += 1
            tokens.append(("identifier", text[start:index]))
            continue
        tokens.append(("punctuation", char))
        index += 1
    return tokens


def audit_native_source(raw: bytes, *, family: str, location: str) -> dict[str, Any]:
    checked_family(family)
    checked_relative(location)
    tokens = native_tokens(raw)
    identifiers = {value for kind, value in tokens if kind == "identifier"}
    for name in identifiers:
        require(name not in FORBIDDEN_NATIVE_NAMES
                and not any(name.startswith(prefix)
                            for prefix in FORBIDDEN_NATIVE_PREFIXES),
                "a native source delegates to an external matcher or process: " + name)
    import_calls: list[str] = []
    for index, (kind, value) in enumerate(tokens):
        if (kind == "identifier" and value == "import"
                and index > 0 and tokens[index - 1] == ("punctuation", "@")):
            require(index + 2 < len(tokens)
                    and tokens[index + 1] == ("punctuation", "(")
                    and tokens[index + 2][0] == "string",
                    "reject a computed Zig compiler import")
            imported = tokens[index + 2][1]
            require(imported not in FORBIDDEN_MODULES,
                    "a native source imports a forbidden regex engine: " + imported)
        if kind == "identifier" and value == "PyImport_ImportModule":
            require(index + 3 < len(tokens)
                    and tokens[index + 1] == ("punctuation", "(")
                    and tokens[index + 2][0] == "string",
                    "reject a computed or nonliteral native Python import")
            imported = tokens[index + 2][1]
            require(family == "rust" and location == "candidates/rust/py_bridge.c"
                    and imported in ALLOWED_BRIDGE_IMPORTS,
                    "reject a native cross-family or standard-regex import")
            import_calls.append(imported)
    required = {
        "candidates/_vm_native.c": "PyInit__vm_native",
        "candidates/rust/py_bridge.c": "PyInit__rust_bridge",
        "candidates/rust/src/lib.rs": "rebar_compile",
        "candidates/zig/mini_regex.zig": "rebar_zig_compile",
        "candidates/zig/py_bridge.c": "PyInit__zig_bridge",
    }.get(location)
    if required is not None:
        require(required in identifiers,
                "an independently owned native entry point is missing: " + required)
    return {
        "path": location, "native_identifier_count": len(identifiers),
        "native_literal_imports": sorted(import_calls),
        "external_regex_dependency_count": 0,
    }


def audit_python_source(raw: Any, *, family: str, location: str) -> dict[str, Any]:
    checked_family(family)
    checked_relative(location)
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES,
            "a complete independently owned Python adapter is required")
    try:
        source = raw.decode("utf-8")
        document = ast.parse(source, filename=location, mode="exec")
    except (UnicodeError, SyntaxError, ValueError, RecursionError) as error:
        raise BuildError("an independently owned candidate adapter cannot be parsed") from error
    imports: set[str] = set()
    own_native = FAMILIES[family]["adapter_import"]
    saw_native = False
    for node in ast.walk(document):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                require(root not in FORBIDDEN_MODULES,
                        "a candidate adapter imports a standard or external regex engine")
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            root = module.split(".", 1)[0]
            require(root not in FORBIDDEN_MODULES,
                    "a candidate adapter imports a standard or external regex engine")
            imports.add(module)
            if module == "candidates":
                for alias in node.names:
                    require(alias.name == own_native,
                            "a candidate delegates to another family's native engine")
                    saw_native = True
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                require(func.id not in {"__import__", "eval", "exec"},
                        "a candidate adapter contains an uninspectable dynamic import")
            elif isinstance(func, ast.Attribute):
                if isinstance(func.value, ast.Name):
                    require((func.value.id, func.attr) not in {
                        ("importlib", "import_module"),
                        ("importlib", "__import__"),
                        ("os", "system"), ("os", "popen"),
                        ("subprocess", "run"), ("subprocess", "Popen"),
                    }, "a candidate adapter dynamically imports or runs another engine")
                if func.attr == "find_library":
                    raise BuildError("a candidate resolves an unpinned native matcher")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            require(node.value != "__import__",
                    "a candidate adapter conceals the dynamic Python importer")
    require(saw_native,
            "an independently owned adapter does not import its exact own native bridge")
    if family == "zig":
        require("_zig_probe.so" in source,
                "the Zig adapter does not identify its exact owned native engine")
    return {
        "path": location, "imports": sorted(imports),
        "own_native_bridge": own_native,
        "external_regex_dependency_count": 0,
        "cross_family_dependency_count": 0,
    }


def checked_workdir(value: Any) -> str:
    require(type(value) is str and value.startswith("/tmp/" + WORK_PREFIX),
            "use only a fresh, family-specific private temporary build root")
    require("\x00" not in value and "\\" not in value
            and value == value.rstrip("/"),
            "reject an unsafe private build directory")
    parts = value.split("/")
    require(all(part not in (".", "..", "") for part in parts[1:])
            and len(parts) == 3,
            "reject broad, nested, redirected, or traversing build directories")
    return value


def phase_paths(workdir: str, family: str, phase: str) -> dict[str, Path]:
    checked_workdir(workdir)
    family = checked_family(family)
    require(phase in ("reference-a", "reference-b"),
            "exactly two fresh, independent source-build phases are mandatory")
    base = Path(workdir) / phase
    source = base / "source"
    native = base / "native"
    return {
        "base": base, "source": source, "native": native,
        "target": base / "target", "cargo_home": base / "cargo-home",
        "temporary": base / "temporary",
        "local_cache": base / "zig-local-cache",
        "global_cache": base / "zig-global-cache",
        "rust_manifest": source / "candidates/rust/Cargo.toml",
        "cargo_engine": base / "target/release/librebar_rust_continuation.so",
        **{
            "binary_" + kind: native / name
            for kind, name in FAMILIES[family]["binaries"].items()
        },
    }


def reproducible_prefix_flags(workdir: str, family: str) -> tuple[list[str], str]:
    cflags: list[str] = []
    rustflags: list[str] = []
    for phase in ("reference-a", "reference-b"):
        source = str(phase_paths(workdir, family, phase)["source"])
        cflags.append("-ffile-prefix-map=" + source + "=/rebar-phase2-owned-source")
        rustflags.append(
            "--remap-path-prefix=" + source + "=/rebar-phase2-owned-source"
        )
    if family == "rust":
        rustflags.append("-Clink-arg=-Wl,-soname,_rust_engine.so")
    return cflags, " ".join(rustflags)


def build_environment(workdir: str, family: str, phase: str) -> dict[str, str]:
    paths = phase_paths(workdir, family, phase)
    _, rustflags = reproducible_prefix_flags(workdir, family)
    env = {
        "PATH": "/usr/bin:/bin",
        "LC_ALL": "C", "LANG": "C", "TZ": "UTC",
        "SOURCE_DATE_EPOCH": "1",
        "TMPDIR": str(paths["temporary"]),
    }
    if family == "rust":
        env.update({
            "PATH": RUST_TOOLCHAIN + "/bin:/usr/bin:/bin",
            "CARGO_HOME": str(paths["cargo_home"]),
            "CARGO_NET_OFFLINE": "true",
            "CARGO_INCREMENTAL": "0",
            "CARGO_BUILD_JOBS": "1",
            "RUSTC": PINNED_RUSTC,
            "RUSTFLAGS": rustflags,
        })
    if family == "zig":
        env.update({
            "ZIG_GLOBAL_CACHE_DIR": str(paths["global_cache"]),
            "ZIG_LOCAL_CACHE_DIR": str(paths["local_cache"]),
        })
    return env


def planned_commands(workdir: str, family: str, phase: str) -> dict[str, list[str]]:
    paths = phase_paths(workdir, family, phase)
    prefix, _ = reproducible_prefix_flags(workdir, family)
    commands: dict[str, list[str]] = {
        "gcc_version": [PINNED_GCC, "--version"],
        "readelf_version": [PINNED_READELF, "--version"],
    }
    if family == "c":
        commands["build_c_extension"] = [
            PINNED_GCC, "-std=c11", "-O3", "-Wall", "-Wextra", "-Werror",
            "-fPIC", "-shared", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE,
            str(paths["source"] / "candidates/_vm_native.c"),
            "-o", str(paths["binary_extension"]),
        ]
    elif family == "rust":
        commands["rustc_version"] = [PINNED_RUSTC, "--version", "--verbose"]
        commands["cargo_version"] = [PINNED_CARGO, "--version"]
        commands["build_rust_engine"] = [
            PINNED_CARGO, "build", "--manifest-path",
            str(paths["rust_manifest"]), "--release", "--locked",
            "--offline", "--frozen", "--target-dir", str(paths["target"]),
        ]
        commands["build_rust_bridge"] = [
            PINNED_GCC, "-pthread", "-std=c11", "-shared", "-fPIC", "-O3",
            "-Wall", "-Wextra", "-Werror", "-Wl,-z,noexecstack",
            "-Wl,--exclude-libs,ALL", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE,
            str(paths["source"] / "candidates/rust/py_bridge.c"),
            "-L" + str(paths["native"]), "-l:_rust_engine.so",
            "-Wl,-rpath,$ORIGIN", "-o", str(paths["binary_bridge"]),
        ]
    else:
        commands["zig_version"] = [ZIG_COMPILER, "version"]
        commands["build_zig_engine"] = [
            ZIG_COMPILER, "build-lib",
            str(paths["source"] / "candidates/zig/mini_regex.zig"),
            "-dynamic", "-lc", "-O", "ReleaseFast", "-fstrip",
            "-fallow-shlib-undefined", "-fsoname=_zig_probe.so",
            "--cache-dir", str(paths["local_cache"]),
            "--global-cache-dir", str(paths["global_cache"]),
            "-femit-bin=" + str(paths["binary_engine"]),
        ]
        commands["build_zig_bridge"] = [
            PINNED_GCC, "-std=c11", "-shared", "-fPIC", "-O3",
            "-Wall", "-Wextra", "-Werror", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE,
            str(paths["source"] / "candidates/zig/py_bridge.c"),
            "-L" + str(paths["native"]), "-l:_zig_probe.so",
            "-Wl,-rpath,$ORIGIN", "-o", str(paths["binary_bridge"]),
        ]
    for kind, binary in FAMILIES[family]["binaries"].items():
        path = paths["binary_" + kind]
        commands[kind + "_dynamic"] = [
            PINNED_READELF, "--dynamic", "--wide", str(path),
        ]
        commands[kind + "_symbols"] = [
            PINNED_READELF, "--dyn-syms", "--wide", str(path),
        ]
    return commands


def checked_command(
    name: Any, argv: Any, workdir: str, family: str, phase: str,
) -> list[str]:
    commands = planned_commands(workdir, family, phase)
    require(type(name) is str and name in commands
            and type(argv) is list
            and all(type(item) is str and "\x00" not in item for item in argv)
            and argv == commands[name],
            "reject an unpinned, shell-based, networked, or modified build command")
    require(argv[0] in {PINNED_GCC, PINNED_READELF, PINNED_RUSTC,
                         PINNED_CARGO, ZIG_COMPILER},
            "only an exactly authenticated compiler or ELF inspector may execute")
    return list(argv)


def sanitized(value: str, workdir: str) -> str:
    return value.replace(checked_workdir(workdir), "<FRESH_PRIVATE_TMP>")


def parse_elf_dynamic(raw: Any) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "complete bounded readelf dynamic output is mandatory")
    try:
        text = raw.decode("utf-8")
    except UnicodeError as error:
        raise BuildError("readelf dynamic output is not valid UTF-8") from error
    found: dict[str, list[str]] = {
        "needed": [], "runpath": [], "rpath": [], "soname": [],
    }
    markers = {
        "(NEEDED)": "needed", "(RUNPATH)": "runpath",
        "(RPATH)": "rpath", "(SONAME)": "soname",
    }
    for line in text.splitlines():
        for marker, key in markers.items():
            if marker in line:
                left = line.find("[")
                right = line.find("]", left + 1)
                require(left >= 0 and right > left,
                        "a native dynamic dependency has no exact bounded value")
                value = line[left + 1:right]
                require(value and "\x00" not in value,
                        "reject an empty or malformed native dependency")
                found[key].append(value)
    for key, values in found.items():
        require(len(values) == len(set(values)),
                "reject duplicated or disguised native dynamic dependencies: " + key)
    return found


def checked_symbol_name(value: Any) -> tuple[str, str | None, bool]:
    require(type(value) is str and 0 < len(value) <= 1024,
            "a complete bounded GNU dynamic-symbol name is mandatory")
    parts = value.split("@")
    require(1 <= len(parts) <= 3,
            "reject an invalid or multiply decorated ELF symbol version")
    name = parts[0]
    require(bool(name) and name[0] in
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$"
            and all(ch.isascii() and (ch.isalnum() or ch in "_.$")
                    for ch in name),
            "reject an empty, non-ASCII, malformed, or disguised ELF symbol")
    version: str | None = None
    default = False
    if len(parts) == 2:
        version = parts[1]
    elif len(parts) == 3:
        require(parts[1] == "",
                "a GNU default symbol version must use exactly two at-signs")
        default = True
        version = parts[2]
    if version is not None:
        require(bool(version) and len(version) <= 256
                and all(ch.isascii() and (ch.isalnum() or ch in "_.+-")
                        for ch in version),
                "reject a missing or malformed GNU ELF symbol version")
    return name, version, default


def parse_elf_symbols(raw: Any) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES
            and raw.endswith(b"\n") and b"\x00" not in raw,
            "complete bounded readelf dynamic-symbol output is mandatory")
    try:
        text = raw.decode("utf-8")
    except UnicodeError as error:
        raise BuildError("readelf symbol output is not valid UTF-8") from error
    prefix = "Symbol table '.dynsym' contains "
    suffix = " entries:"
    declared: int | None = None
    entries: dict[int, dict[str, Any]] = {}
    allowed_types = {
        "NOTYPE", "OBJECT", "FUNC", "SECTION", "FILE", "COMMON", "TLS",
        "GNU_IFUNC", "IFUNC",
    }
    allowed_bindings = {"LOCAL", "GLOBAL", "WEAK", "UNIQUE", "GNU_UNIQUE"}
    allowed_visibility = {"DEFAULT", "INTERNAL", "HIDDEN", "PROTECTED"}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(prefix):
            require(declared is None and stripped.endswith(suffix),
                    "reject duplicated or malformed GNU dynamic-symbol table headers")
            count = stripped[len(prefix):-len(suffix)]
            require(count.isascii() and count.isdecimal()
                    and 1 <= int(count) <= 131_072,
                    "reject an invalid bounded GNU dynamic-symbol table count")
            declared = int(count)
            continue
        if stripped.startswith("Num:"):
            require(declared is not None,
                    "the dynamic symbol header precedes its authenticated table")
            continue
        fields = stripped.split()
        if not fields:
            continue
        first = fields[0]
        if not (first.endswith(":") and first[:-1].isascii()
                and first[:-1].isdecimal()):
            raise BuildError("reject an unrecognized GNU dynamic-symbol record")
        require(declared is not None,
                "reject a dynamic-symbol row outside its authenticated table")
        index = int(first[:-1])
        require(index not in entries and 0 <= index < declared,
                "reject a duplicate or out-of-range dynamic-symbol row")
        require(7 <= len(fields) <= 9,
                "reject omitted, shifted, hidden, or trailing ELF symbol columns")
        value, size, kind, binding, visibility, section = fields[1:7]
        require(value.isascii() and 1 <= len(value) <= 32
                and all(ch in "0123456789abcdefABCDEF" for ch in value),
                "reject a malformed GNU dynamic-symbol address")
        require(size.isascii() and size.isdecimal()
                and 0 <= int(size) <= MAX_BINARY_BYTES,
                "reject a malformed GNU dynamic-symbol size")
        require(kind in allowed_types and binding in allowed_bindings
                and visibility in allowed_visibility,
                "reject a shifted GNU dynamic-symbol type, binding, or visibility")
        require(section in {"UND", "ABS", "COM"}
                or section.isascii() and section.isdecimal(),
                "reject a shifted or malformed GNU dynamic-symbol section index")
        if len(fields) == 7:
            require(index == 0 and section == "UND" and binding == "LOCAL",
                    "only the original null dynamic-symbol record may omit its name")
            entries[index] = {
                "index": index, "type": kind, "binding": binding,
                "visibility": visibility, "section": section,
                "name": None, "raw_name": None,
                "version": None, "default_version": False,
                "version_index": None,
            }
            continue
        raw_name = fields[7]
        name, version, default = checked_symbol_name(raw_name)
        version_index = None
        if len(fields) == 9:
            trailer = fields[8]
            require(version is not None and trailer.startswith("(")
                    and trailer.endswith(")")
                    and trailer[1:-1].isascii()
                    and trailer[1:-1].isdecimal()
                    and int(trailer[1:-1]) > 0,
                    "reject a disguised or malformed GNU symbol-version index")
            version_index = int(trailer[1:-1])
        require(name not in FORBIDDEN_NATIVE_NAMES
                and not any(name.startswith(p) for p in FORBIDDEN_NATIVE_PREFIXES),
                "the native binary delegates to a foreign matcher or process: " + name)
        entries[index] = {
            "index": index, "type": kind, "binding": binding,
            "visibility": visibility, "section": section,
            "name": name, "raw_name": raw_name,
            "version": version, "default_version": default,
            "version_index": version_index,
        }
    require(declared is not None and len(entries) == declared
            and set(entries) == set(range(declared)),
            "the actual complete GNU dynamic-symbol table was omitted or altered")
    records = [entries[index] for index in range(declared)]
    exports = {
        row["name"] for row in records
        if row["name"] is not None and row["section"] != "UND"
        and row["binding"] in {"GLOBAL", "WEAK", "UNIQUE", "GNU_UNIQUE"}
    }
    undefined = {
        row["name"] for row in records
        if row["name"] is not None and row["section"] == "UND"
    }
    require(bool(exports),
            "a native binary exposes no genuine dynamic matching or bridge entry point")
    return {
        "exports": sorted(exports), "undefined": sorted(undefined),
        "symbol_count": declared,
        "versioned_symbol_count": sum(row["version"] is not None for row in records),
        "symbol_records": records,
    }


def validate_elf(
    family: str, kind: str, dynamic: dict[str, Any], symbols: dict[str, Any],
) -> dict[str, Any]:
    family = checked_family(family)
    require(kind in FAMILIES[family]["binaries"],
            "reject a substituted native binary role")
    needed = set(dynamic["needed"])
    require(not dynamic["rpath"], "a native binary contains an unsafe RPATH")
    exports = set(symbols["exports"])
    undefined = set(symbols["undefined"])
    all_symbols = exports | undefined
    if family == "c":
        require(not any(name.startswith(("rebar_", "rebar_zig_"))
                        or name in {"PyInit__rust_bridge", "PyInit__zig_bridge"}
                        for name in all_symbols),
                "the C extension references a Rust or Zig matching engine")
    elif family == "rust":
        require(not any(name.startswith("rebar_zig_")
                        or name in {"PyInit__vm_native", "PyInit__zig_bridge"}
                        for name in all_symbols),
                "the Rust native family references the C or Zig engine")
    else:
        require(not any((name.startswith("rebar_")
                         and not name.startswith("rebar_zig_"))
                        or name in {"PyInit__vm_native", "PyInit__rust_bridge"}
                        for name in all_symbols),
                "the Zig native family references the C or Rust engine")
    if family == "c":
        require(kind == "extension" and "PyInit__vm_native" in exports,
                "the C extension lacks its genuine CPython entry point")
        require(needed.issubset(ALLOWED_SYSTEM_LIBRARIES)
                and not dynamic["runpath"],
                "the C extension delegates to another native matcher")
        required = {"PyInit__vm_native"}
    elif kind == "engine":
        expected_name = FAMILIES[family]["binaries"]["engine"]
        required = RUST_ENGINE_EXPORTS if family == "rust" else ZIG_ENGINE_EXPORTS
        require(dynamic["soname"] == [expected_name],
                "the owned native engine SONAME is missing or substituted")
        require(not dynamic["runpath"] and needed.issubset(ALLOWED_SYSTEM_LIBRARIES),
                "the native engine loads an external or sibling matching engine")
        require(set(required).issubset(exports),
                "a genuinely owned native matching entry point is missing")
    else:
        expected_name = FAMILIES[family]["binaries"]["engine"]
        expected_init = "PyInit__" + family + "_bridge"
        require(expected_init in exports,
                "the owned bridge lacks its exact CPython 3.14 entry point")
        require(expected_name in needed
                and needed.issubset(ALLOWED_SYSTEM_LIBRARIES | {expected_name}),
                "the bridge does not exclusively link to its own native engine")
        require(dynamic["runpath"] == ["$ORIGIN"],
                "the bridge must resolve only its adjacent owned engine")
        engine_prefix = "rebar_" if family == "rust" else "rebar_zig_"
        require(any(name.startswith(engine_prefix) for name in undefined),
                "the bridge does not call its actual own matching engine")
        forbidden_sibling = "rebar_zig_" if family == "rust" else "rebar_compile"
        require(not any(name.startswith(forbidden_sibling) for name in undefined),
                "the bridge calls another candidate's matching engine")
        required = {expected_init}
    return {
        "role": kind, "needed": sorted(needed),
        "runpath": list(dynamic["runpath"]),
        "soname": list(dynamic["soname"]),
        "required_exports": sorted(required),
        "exports": list(symbols["exports"]),
        "undefined": list(symbols["undefined"]),
        "symbol_count": symbols["symbol_count"],
        "versioned_symbol_count": symbols["versioned_symbol_count"],
        "symbol_records": list(symbols["symbol_records"]),
        "external_regex_dependency_count": 0,
        "cross_family_dependency_count": 0,
    }


def validate_phase1_manifest(raw: bytes) -> dict[str, Any]:
    value = decode_json(raw, canonical_required=True)
    require(value.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and value.get("version") == 1,
            "the independently completed Python correctness oracle was substituted")
    suites = value.get("suites")
    phase = value.get("phase_gate")
    guards = value.get("audit_boundaries")
    require(type(suites) is list and len(suites) == 13
            and sum(item.get("case_execution_count", 0) for item in suites) == 31_237
            and all(item.get("baseline", {}).get("status") == "PASS" for item in suites),
            "all 31,237 independently recorded Python cases must pass first")
    require(type(phase) is dict and phase.get("status") == "PASS"
            and phase.get("all_obligations_mapped") is True
            and phase.get("blockers") == []
            and phase.get("final_holdout_authorized") is False,
            "reject incomplete correctness or unauthorized holdout evidence")
    require(type(guards) is dict and guards.get("hidden_cases_read") == 0
            and guards.get("final_cases_read") == 0
            and guards.get("timing_trials_run") == 0,
            "the build may not read a holdout or inherit performance measurements")
    return {
        "status": "PASS", "suite_count": 13,
        "case_execution_count": 31_237,
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "final_holdout_authorized": False,
    }


def validate_zig_lock(raw: bytes) -> dict[str, Any]:
    lock = decode_json(raw, canonical_required=False)
    expected = {
        "schema": "rebar-official-language-toolchain-v1",
        "language": "Zig", "version": "0.16.0",
        "release_channel": "stable", "platform": "x86_64-linux",
        "official_release_index": "https://ziglang.org/download/index.json",
        "archive_url": (
            "https://ziglang.org/download/0.16.0/zig-x86_64-linux-0.16.0.tar.xz"
        ),
        "archive_sha256": (
            "70e49664a74374b48b51e6f3fdfbf437f6395d42509050588bd49abe52ba3d00"
        ),
        "archive_bytes": 55_478_392,
        "archive_root": "zig-x86_64-linux-0.16.0",
        "compiler_relative_path": "zig-x86_64-linux-0.16.0/zig",
        "compiler_sha256": (
            "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c"
        ),
    }
    require(lock == expected,
            "the exact offline, official Zig 0.16.0 release lock changed")
    return {
        "language": "Zig", "version": "0.16.0",
        "archive_sha256": lock["archive_sha256"],
        "compiler_sha256": lock["compiler_sha256"],
        "network_requests": 0,
    }


def run_process(
    name: str, workdir: str, family: str, phase: str,
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    require(type(steps) is list, "retain every actual compiler and inspector process")
    command = planned_commands(workdir, family, phase)
    require(name in command, "an independently frozen compiler command is missing")
    argv = checked_command(name, command[name], workdir, family, phase)
    environment = build_environment(workdir, family, phase)
    empty = hashlib.sha256(b"").hexdigest()
    item: dict[str, Any] = {
        "name": name,
        "argv": [sanitized(value, workdir) for value in argv],
        "environment": {
            key: sanitized(value, workdir)
            for key, value in sorted(environment.items())
        },
        "shell": False, "pid": None, "exit_status": None,
        "stdout_base64": "", "stderr_base64": "",
        "stdout_sha256": empty, "stderr_sha256": empty,
        "stdout_bytes": 0, "stderr_bytes": 0,
    }
    steps.append(item)
    try:
        process = subprocess.Popen(
            argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=environment,
            cwd=str(phase_paths(workdir, family, phase)["base"]),
            shell=False,
        )
        item["pid"] = process.pid
        try:
            stdout, stderr = process.communicate(timeout=900)
        except subprocess.TimeoutExpired as error:
            process.kill()
            stdout, stderr = process.communicate()
            item["exit_status"] = process.returncode
            raise BuildError("a bounded owned compiler process exceeded its limit") from error
        item["exit_status"] = process.returncode
        require(type(stdout) is bytes and type(stderr) is bytes
                and len(stdout) <= MAX_PROCESS_BYTES
                and len(stderr) <= MAX_PROCESS_BYTES,
                "retain complete bounded compiler output and errors")
        item["stdout_base64"] = base64.b64encode(stdout).decode("ascii")
        item["stderr_base64"] = base64.b64encode(stderr).decode("ascii")
        item["stdout_sha256"] = hashlib.sha256(stdout).hexdigest()
        item["stderr_sha256"] = hashlib.sha256(stderr).hexdigest()
        item["stdout_bytes"] = len(stdout)
        item["stderr_bytes"] = len(stderr)
        require(process.returncode == 0,
                "an exact owned compiler or ELF inspector failed: " + name)
        return {"record": item, "stdout": stdout, "stderr": stderr}
    except (OSError, subprocess.SubprocessError) as error:
        item["error_type"] = type(error).__name__
        item["error_message"] = str(error)
        raise BuildError("an authenticated compiler process could not complete") from error


def validate_version(name: str, raw: bytes) -> None:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "record the complete pinned compiler version")
    if name == "zig_version":
        require(raw == b"0.16.0\n",
                "the exact official stable Zig 0.16.0 compiler was substituted")
    elif name == "cargo_version":
        require(raw.startswith(b"cargo 1.95.0 (f2d3ce0bd"),
                "PATH cargo or a non-1.95.0 Rust toolchain was substituted")
    elif name == "rustc_version":
        require(raw.startswith(b"rustc 1.95.0 (59807616e")
                and b"release: 1.95.0\n" in raw
                and b"commit-hash: 59807616e1fa2540724bfbac14d7976d7e4a3860\n" in raw
                and b"host: x86_64-unknown-linux-gnu\n" in raw,
                "the exact official Rust 1.95.0 compiler identity changed")
    elif name == "gcc_version":
        require(b"13." in raw.split(b"\n", 1)[0],
                "the pinned host GCC 13 version changed")
    elif name == "readelf_version":
        require(b"readelf" in raw.split(b"\n", 1)[0].lower(),
                "the pinned ELF inspector version changed")
    else:
        raise BuildError("an unapproved compiler-version command was run")


def mkdir_private(path: Path) -> None:
    require(isinstance(path, Path) and path.is_absolute(),
            "create only an absolute fresh private build directory")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    result = os.lstat(str(path))
    require(stat.S_ISDIR(result.st_mode) and not stat.S_ISLNK(result.st_mode),
            "a private build directory was redirected")


def write_fresh(path: Path, content: bytes, *, synchronize: bool) -> dict[str, Any]:
    require(isinstance(path, Path) and path.is_absolute()
            and type(content) is bytes and 0 < len(content) <= MAX_ARCHIVE_BYTES,
            "write only a complete, bounded, specifically approved fresh file")
    descriptor = os.open(
        str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
        0o600,
    )
    calls = 0
    written = 0
    try:
        while written < len(content):
            result = os.write(descriptor, content[written:])
            require(type(result) is int and result > 0,
                    "a fresh evidence or source write stopped prematurely")
            written += result
            calls += 1
        require(written == len(content), "a fresh source or report was truncated")
        if synchronize:
            os.fsync(descriptor)
    finally:
        os.close(descriptor)
    observed, _ = authenticate_file(
        path, expected=hashlib.sha256(content).hexdigest(),
        maximum=MAX_ARCHIVE_BYTES, exact_size=len(content),
    )
    return {
        "path": str(path), "sha256": observed["sha256"],
        "bytes": len(content), "write_calls": calls,
        "exclusive_creation": True,
        "same_inode_readback_verified": True,
        "file_fsync_completed": synchronize,
    }


def snapshot_owned_sources(
    family: str, pins: dict[str, str],
) -> tuple[dict[str, dict[str, Any]], dict[str, bytes]]:
    checked_family(family)
    require(set(pins) == set(FAMILIES[family]["owners"]),
            "reject an incomplete or cross-family actual source snapshot")
    observed: dict[str, dict[str, Any]] = {}
    source: dict[str, bytes] = {}
    for relative, digest in sorted(pins.items()):
        owner, raw = authenticate_file(
            ROOT / checked_relative(relative), expected=digest,
            maximum=MAX_SOURCE_BYTES, capture=True,
        )
        require(raw is not None, "an actual owned source snapshot is missing")
        observed[relative] = owner
        source[relative] = raw
    return observed, source


def audit_owned_sources(family: str, sources: dict[str, bytes]) -> dict[str, Any]:
    require(set(sources) == set(FAMILIES[family]["owners"]),
            "the complete independent family source graph is mandatory")
    audits: list[dict[str, Any]] = []
    for relative, raw in sorted(sources.items()):
        if relative.endswith(".py"):
            audits.append(audit_python_source(raw, family=family, location=relative))
        elif relative.endswith((".c", ".rs", ".zig")):
            audits.append(audit_native_source(raw, family=family, location=relative))
    cargo = None
    if family == "rust":
        cargo = validate_cargo_closure(
            sources["candidates/rust/Cargo.toml"],
            sources["candidates/rust/Cargo.lock"],
        )
    return {
        "source_audits": audits,
        "source_owner_count": len(sources),
        "external_regex_package_count": 0,
        "cross_family_dependency_count": 0,
        "cargo_dependency_closure": cargo,
    }


def copy_snapshot(
    workdir: str, family: str, phase: str,
    sources: dict[str, bytes],
) -> dict[str, dict[str, Any]]:
    paths = phase_paths(workdir, family, phase)
    for name in ("base", "source", "native", "temporary"):
        mkdir_private(paths[name])
    if family == "rust":
        mkdir_private(paths["cargo_home"])
    if family == "zig":
        mkdir_private(paths["local_cache"])
        mkdir_private(paths["global_cache"])
    copied: dict[str, dict[str, Any]] = {}
    for relative, content in sorted(sources.items()):
        destination = paths["source"] / checked_relative(relative)
        mkdir_private(destination.parent)
        result = write_fresh(destination, content, synchronize=False)
        result["path"] = sanitized(result["path"], workdir)
        copied[relative] = result
    return copied


def verify_fresh_binary(
    workdir: str, family: str, phase: str, kind: str,
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    paths = phase_paths(workdir, family, phase)
    binary, _ = authenticate_file(
        paths["binary_" + kind], expected=None,
        maximum=MAX_BINARY_BYTES,
    )
    dynamic_result = run_process(kind + "_dynamic", workdir, family, phase, steps)
    symbol_result = run_process(kind + "_symbols", workdir, family, phase, steps)
    dynamic = parse_elf_dynamic(dynamic_result["stdout"])
    symbols = parse_elf_symbols(symbol_result["stdout"])
    audit = validate_elf(family, kind, dynamic, symbols)
    after, _ = authenticate_file(
        paths["binary_" + kind], expected=binary["sha256"],
        maximum=MAX_BINARY_BYTES, exact_size=binary["size_bytes"],
    )
    require((binary["device"], binary["inode"])
            == (after["device"], after["inode"]),
            "a fresh native binary changed during ELF inspection")
    return {
        "family": family, "role": kind,
        "file_name": FAMILIES[family]["binaries"][kind],
        "path": sanitized(binary["path"], workdir),
        "sha256": binary["sha256"], "size_bytes": binary["size_bytes"],
        "elf": audit,
        "prebuilt_binary_read": False,
        "candidate_imported": False,
    }


def exact_build_phase(
    workdir: str, family: str, phase: str,
    sources: dict[str, bytes], steps: list[dict[str, Any]],
) -> dict[str, Any]:
    copied = copy_snapshot(workdir, family, phase, sources)
    paths = phase_paths(workdir, family, phase)
    if family == "c":
        run_process("build_c_extension", workdir, family, phase, steps)
    elif family == "rust":
        run_process("build_rust_engine", workdir, family, phase, steps)
        engine, raw = authenticate_file(
            paths["cargo_engine"], expected=None,
            maximum=MAX_BINARY_BYTES, capture=True,
        )
        require(raw is not None and engine["size_bytes"] == len(raw),
                "Cargo did not produce a complete fresh owned Rust engine")
        write_fresh(paths["binary_engine"], raw, synchronize=False)
        run_process("build_rust_bridge", workdir, family, phase, steps)
    else:
        run_process("build_zig_engine", workdir, family, phase, steps)
        run_process("build_zig_bridge", workdir, family, phase, steps)
    binaries = {
        kind: verify_fresh_binary(workdir, family, phase, kind, steps)
        for kind in FAMILIES[family]["binaries"]
    }
    return {
        "name": phase,
        "fresh_source_directory": sanitized(str(paths["source"]), workdir),
        "fresh_native_directory": sanitized(str(paths["native"]), workdir),
        "copied_source_owners": copied,
        "native_outputs": binaries,
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "timing_trials_run": 0,
        "hidden_cases_read": 0,
    }


def verify_reproducible_phases(
    family: str, phases: list[dict[str, Any]],
) -> dict[str, Any]:
    checked_family(family)
    require(type(phases) is list and len(phases) == 2
            and [item.get("name") for item in phases]
            == ["reference-a", "reference-b"],
            "two genuinely independent complete source-build phases are mandatory")
    first, second = phases
    require(first["fresh_source_directory"] != second["fresh_source_directory"]
            and first["fresh_native_directory"] != second["fresh_native_directory"],
            "an existing build directory or compiled candidate was reused")
    owners = set(FAMILIES[family]["owners"])
    require(set(first["copied_source_owners"])
            == set(second["copied_source_owners"]) == owners,
            "the two fresh build phases used different source closures")
    outputs: dict[str, dict[str, Any]] = {}
    for kind, name in FAMILIES[family]["binaries"].items():
        left = first["native_outputs"][kind]
        right = second["native_outputs"][kind]
        require(left["file_name"] == right["file_name"] == name
                and left["sha256"] == right["sha256"]
                and left["size_bytes"] == right["size_bytes"]
                and left["path"] != right["path"]
                and left["elf"] == right["elf"],
                "two independent native builds are not byte-for-byte reproducible")
        outputs[kind] = {
            "file_name": name, "sha256": left["sha256"],
            "size_bytes": left["size_bytes"],
            "reproduced_in_two_fresh_directories": True,
            "elf": left["elf"],
        }
    return {
        "independent_fresh_phase_count": 2,
        "byte_identical": True,
        "native_outputs": outputs,
        "prebuilt_binary_count": 0,
        "native_libraries_loaded": 0,
    }


def evidence_names(family: str, label: str, *, failure: bool) -> tuple[str, str]:
    family = checked_family(family)
    label = checked_label(label)
    base = "native-source-build-v3-" + family + "-" + label
    if failure:
        base += "-failures"
    return base + ".json.gz", base + "-publication-receipt.json"


def check_fresh_evidence(family: str, label: str) -> None:
    parent = ROOT / EVIDENCE_RELATIVE
    if parent.exists():
        observed = os.lstat(str(parent))
        require(stat.S_ISDIR(observed.st_mode) and not stat.S_ISLNK(observed.st_mode),
                "the native build evidence directory is unsafe")
    for failure in (False, True):
        for name in evidence_names(family, label, failure=failure):
            target = parent / name
            try:
                os.lstat(str(target))
            except FileNotFoundError:
                continue
            raise BuildError("refusing to overwrite a preserved native build: " + str(target))


def fsync_directory(path: Path) -> dict[str, Any]:
    descriptor = os.open(
        str(path), os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISDIR(before.st_mode), "synchronize only the owned report directory")
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino) == (after.st_dev, after.st_ino),
                "the published evidence directory was redirected")
        return {"completed": True, "device": after.st_dev, "inode": after.st_ino}
    finally:
        os.close(descriptor)


def publish_report(report: dict[str, Any], family: str, label: str) -> dict[str, Any]:
    failure = report.get("status") != "PASS"
    archive_name, receipt_name = evidence_names(family, label, failure=failure)
    directory = ROOT / EVIDENCE_RELATIVE
    mkdir_private(directory)
    plain = canonical(report)
    require(len(plain) <= MAX_REPORT_BYTES,
            "a full reproducible-build report exceeded its signed byte bound")
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(archive) <= MAX_ARCHIVE_BYTES,
            "a reproducible-build report archive exceeded its signed byte bound")
    archive_path = directory / archive_name
    receipt_path = directory / receipt_name
    archive_record = write_fresh(archive_path, archive, synchronize=True)
    archive_sync = fsync_directory(directory)
    receipt: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "status": "PASS",
        "build_status": report["status"],
        "family": family, "label": label,
        "source_sha256": report["source_sha256"],
        "protocol_sha256": report["protocol_sha256"],
        "phase1_manifest_sha256": FROZEN_INPUTS[1][2],
        "archive_relative": EVIDENCE_RELATIVE + "/" + archive_name,
        "archive_sha256": archive_record["sha256"],
        "archive_bytes": archive_record["bytes"],
        "uncompressed_sha256": hashlib.sha256(plain).hexdigest(),
        "uncompressed_bytes": len(plain),
        "archive_publication": archive_record,
        "archive_directory_fsync": archive_sync,
        "owned_source_sha256": report["owned_source_sha256"],
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "candidate_correctness": "NOT MEASURED",
        "winner_selected": False,
        "receipt_self_publication": "NOT CLAIMED",
    }
    receipt_bytes = canonical(receipt)
    require(len(receipt_bytes) <= MAX_SOURCE_BYTES,
            "a complete native-build receipt exceeded its signed byte bound")
    receipt_record = write_fresh(receipt_path, receipt_bytes, synchronize=True)
    receipt_sync = fsync_directory(directory)
    return {
        "status": report["status"], "family": family, "label": label,
        "archive_relative": EVIDENCE_RELATIVE + "/" + archive_name,
        "archive_sha256": archive_record["sha256"],
        "receipt_relative": EVIDENCE_RELATIVE + "/" + receipt_name,
        "receipt_sha256": receipt_record["sha256"],
        "receipt_directory_fsync": receipt_sync,
        "failure_preserved": failure,
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def authenticate_build_inputs(
    family: str, *, source_digest: str, protocol_digest: str,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any], dict[str, Any]]:
    family = checked_family(family)
    require(sys.executable == PINNED_PYTHON
            and sys.version_info[:3] == (3, 14, 6)
            and sys.implementation.name == "cpython"
            and sys.implementation.cache_tag == "cpython-314",
            "invoke the exact frozen CPython 3.14.6 executable and ABI")
    support: dict[str, dict[str, Any]] = {}
    preserved_raw: dict[str, bytes] = {}
    phase1: dict[str, Any] | None = None
    for specification in FROZEN_INPUTS:
        capture = specification[0] in {
            "complete_correctness_manifest", "pinned_cpython_patchlevel",
        } or specification[0].startswith("preserved_v2_")
        name, evidence, raw = authenticate_specification(specification, capture=capture)
        support[name] = evidence
        if name.startswith("preserved_v2_"):
            require(raw is not None,
                    "capture every immutable, complete version-two owner")
            preserved_raw[name] = raw
        if name == "complete_correctness_manifest":
            require(raw is not None, "the complete Phase-1 manifest is missing")
            phase1 = validate_phase1_manifest(raw)
        if name == "pinned_cpython_patchlevel":
            require(raw is not None, "the pinned Python patch-level header is missing")
            actual_versions = [
                line.split()
                for line in raw.splitlines()
                if line.split()[:2] == [b"#define", b"PY_VERSION"]
            ]
            require(actual_versions == [[b"#define", b"PY_VERSION", b'"3.14.6"']],
                    "the exact stable CPython 3.14.6 header changed")
    source, _ = authenticate_file(
        ROOT / SOURCE_RELATIVE, expected=checked_digest(source_digest, "build recorder"),
        maximum=MAX_SOURCE_BYTES,
    )
    protocol, _ = authenticate_file(
        ROOT / PROTOCOL_RELATIVE,
        expected=checked_digest(protocol_digest, "build protocol"),
        maximum=MAX_SOURCE_BYTES,
    )
    support["native_build_recorder"] = source
    support["native_build_protocol"] = protocol
    if family == "rust":
        for specification in RUST_INPUTS:
            name, evidence, _ = authenticate_specification(specification)
            support[name] = evidence
    if family == "zig":
        for specification in ZIG_INPUTS:
            name, evidence, raw = authenticate_specification(
                specification, capture=specification[0].endswith("_lock"),
            )
            support[name] = evidence
            if name == "pinned_official_zig_0_16_0_lock":
                require(raw is not None, "the exact official Zig lock was not captured")
                validate_zig_lock(raw)
    require(phase1 is not None,
            "the previously published Python correctness phase is mandatory")
    preserved_history = authenticate_preserved_v2_history(preserved_raw)
    return support, phase1, preserved_history


def historical_process_output(step: Any, expected_name: str) -> bytes:
    require(type(step) is dict and step.get("name") == expected_name
            and type(step.get("pid")) is int and step["pid"] > 0
            and step.get("exit_status") == 0,
            "an authentic independently observed V1 compiler process was omitted")
    encoded = step.get("stdout_base64")
    require(type(encoded) is str,
            "the complete observed historical compiler output is missing")
    try:
        raw = base64.b64decode(encoded.encode("ascii"), validate=True)
    except (ValueError, UnicodeError) as error:
        raise BuildError("a complete historical compiler stream is malformed") from error
    require(len(raw) == step.get("stdout_bytes")
            and hashlib.sha256(raw).hexdigest() == step.get("stdout_sha256"),
            "an actual historical compiler process output was substituted")
    return raw


def decompress_historical_v1(raw: Any) -> bytes:
    require(type(raw) is bytes and len(raw) == HISTORICAL_V1_C_ARCHIVE[2]
            and raw[:4] == bytes.fromhex("1f8b0800")
            and raw[4:8] == bytes(4),
            "the actual deterministic historical V1 C archive was substituted")
    decoder = zlib.decompressobj(wbits=16 + zlib.MAX_WBITS)
    try:
        plain = decoder.decompress(raw, HISTORICAL_V1_C_UNCOMPRESSED_BYTES + 1)
        plain += decoder.flush()
    except zlib.error as error:
        raise BuildError("the historical source-build archive is malformed") from error
    require(decoder.eof and not decoder.unused_data
            and not decoder.unconsumed_tail
            and len(plain) == HISTORICAL_V1_C_UNCOMPRESSED_BYTES
            and hashlib.sha256(plain).hexdigest()
            == HISTORICAL_V1_C_UNCOMPRESSED_SHA256,
            "the complete single historical gzip member changed or was concatenated")
    return plain



def validate_preserved_v2_specification(record: Any) -> dict[str, Any]:
    """Fail closed on a renamed, rewritten, or incorrectly classified V2 result."""
    require(type(record) is dict and record.get("family") in FAMILIES,
            "one exact independently published version-two family is mandatory")
    expected = next(
        (entry for entry in PRESERVED_V2_RECORDS
         if entry["family"] == record["family"]),
        None,
    )
    require(expected is not None and record == expected,
            "a genuine frozen version-two record or failure was changed")
    family = record["family"]
    require(record["build_status"] == ("FAIL" if family == "zig" else "PASS"),
            "never turn the authentic Zig reproducibility failure into a pass")
    require(record["archive_path"].startswith(
        "oracle/phase2/evidence/native-source-build-v2-" + family + "-",
    ) and record["receipt_path"].startswith(
        "oracle/phase2/evidence/native-source-build-v2-" + family + "-",
    ), "preserve each actual version-two evidence owner and namespace")
    if family == "zig":
        require("-failures." in record["archive_path"]
                and "-failures-" in record["receipt_path"],
                "the authentic Zig failure must retain its failure filenames")
    else:
        require("-failures" not in record["archive_path"]
                and "-failures" not in record["receipt_path"],
                "a genuine C or Rust success cannot be relabelled as a failure")
    for key in ("archive_sha256", "uncompressed_sha256", "receipt_sha256"):
        checked_digest(record[key], "preserved V2 " + family + " " + key)
    for key in ("archive_bytes", "uncompressed_bytes", "receipt_bytes"):
        require(type(record[key]) is int and 0 < record[key] <= MAX_REPORT_BYTES,
                "bound every genuine preserved version-two evidence owner")
    require(type(record["phase_outputs"]) is tuple
            and len(record["phase_outputs"]) == 2,
            "preserve both original genuine version-two source-build phases")
    return copy.deepcopy(record)


def decompress_preserved_v2(
    raw: Any, *, archive_sha256: str, archive_bytes: int,
    uncompressed_sha256: str, uncompressed_bytes: int,
) -> bytes:
    """Decode one exact, bounded, canonical, deterministic gzip member."""
    checked_digest(archive_sha256, "preserved version-two compressed archive")
    checked_digest(uncompressed_sha256, "preserved version-two complete report")
    require(type(archive_bytes) is int and 0 < archive_bytes <= MAX_ARCHIVE_BYTES
            and type(uncompressed_bytes) is int
            and 0 < uncompressed_bytes <= MAX_REPORT_BYTES,
            "require bounded exact historical compressed and complete byte counts")
    require(type(raw) is bytes and len(raw) == archive_bytes
            and hashlib.sha256(raw).hexdigest() == archive_sha256
            and raw[:4] == bytes.fromhex("1f8b0800")
            and raw[4:8] == bytes(4),
            "the exact deterministic single-member version-two archive changed")
    decoder = zlib.decompressobj(wbits=16 + zlib.MAX_WBITS)
    try:
        plain = decoder.decompress(raw, uncompressed_bytes + 1)
        require(len(plain) <= uncompressed_bytes
                and not decoder.unconsumed_tail,
                "reject a historical gzip report exceeding its signed limit")
        remaining = decoder.flush()
    except zlib.error as error:
        raise BuildError("the preserved version-two gzip member is malformed") from error
    require(len(remaining) <= uncompressed_bytes - len(plain),
            "reject unbounded historical gzip output")
    plain += remaining
    require(decoder.eof and not decoder.unused_data
            and not decoder.unconsumed_tail
            and len(plain) == uncompressed_bytes
            and hashlib.sha256(plain).hexdigest() == uncompressed_sha256,
            "the complete single-member version-two archive changed")
    return plain


def validate_preserved_v2_process(
    record: Any, *, family: str, phase: str, name: str,
) -> dict[str, bytes]:
    """Recheck a real V2 process against its actual complete historical plan."""
    require(type(record) is dict and record.get("name") == name
            and type(record.get("pid")) is int and record["pid"] > 0
            and record.get("exit_status") == 0
            and record.get("shell") is False,
            "an independently observed version-two compiler process changed")
    synthetic_root = "/tmp/" + WORK_PREFIX + family + "-preserved-history"
    commands = planned_commands(synthetic_root, family, phase)
    require(name in commands,
            "an actual historical compiler or ELF-inspection step is missing")
    original = list(commands[name])
    if family == "zig" and name == "build_zig_engine":
        require(original.count("-fstrip") == 1,
                "the version-three Zig correction must remain compiler-native")
        original.remove("-fstrip")
    expected_argv = [sanitized(item, synthetic_root) for item in original]
    require(record.get("argv") == expected_argv,
            "the exact independently pinned version-two process was substituted")
    environment = build_environment(synthetic_root, family, phase)
    expected_environment = {
        key: sanitized(value, synthetic_root)
        for key, value in sorted(environment.items())
    }
    require(record.get("environment") == expected_environment,
            "the authentic private, offline version-two environment changed")
    streams: dict[str, bytes] = {}
    for stream in ("stdout", "stderr"):
        encoded = record.get(stream + "_base64")
        require(type(encoded) is str,
                "retain each complete genuine historical compiler stream")
        try:
            raw = base64.b64decode(encoded.encode("ascii"), validate=True)
        except (ValueError, UnicodeError) as error:
            raise BuildError("a genuine historical process stream is malformed") from error
        require(len(raw) <= MAX_PROCESS_BYTES
                and len(raw) == record.get(stream + "_bytes")
                and hashlib.sha256(raw).hexdigest()
                == record.get(stream + "_sha256"),
                "a complete historical process output changed")
        streams[stream] = raw
    if name.endswith("_version"):
        validate_version(name, streams["stdout"])
    return streams


def authenticate_preserved_v2_history(captured: Any) -> dict[str, Any]:
    """Authenticate both real V2 successes and the real V2 Zig failure."""
    require(type(captured) is dict and set(captured) == {
        "preserved_v2_build_source", "preserved_v2_build_protocol",
        "preserved_v2_c_archive", "preserved_v2_c_receipt",
        "preserved_v2_rust_archive", "preserved_v2_rust_receipt",
        "preserved_v2_zig_archive", "preserved_v2_zig_receipt",
    }, "the complete immutable version-two source, protocol, and evidence are required")
    require(
        type(captured["preserved_v2_build_source"]) is bytes
        and len(captured["preserved_v2_build_source"]) == PRESERVED_V2_SOURCE[2]
        and hashlib.sha256(captured["preserved_v2_build_source"]).hexdigest()
        == PRESERVED_V2_SOURCE[1]
        and type(captured["preserved_v2_build_protocol"]) is bytes
        and len(captured["preserved_v2_build_protocol"]) == PRESERVED_V2_PROTOCOL[2]
        and hashlib.sha256(captured["preserved_v2_build_protocol"]).hexdigest()
        == PRESERVED_V2_PROTOCOL[1],
        "the authentic frozen version-two source or protocol was substituted",
    )
    summaries: list[dict[str, Any]] = []
    effect_names = (
        "candidate_processes_started", "candidate_imports",
        "native_libraries_loaded", "hidden_cases_read",
        "benchmark_files_read", "clock_samples", "timing_trials_run",
    )
    for original in PRESERVED_V2_RECORDS:
        spec = validate_preserved_v2_specification(original)
        family = spec["family"]
        archive = captured["preserved_v2_" + family + "_archive"]
        receipt_raw = captured["preserved_v2_" + family + "_receipt"]
        plain = decompress_preserved_v2(
            archive,
            archive_sha256=spec["archive_sha256"],
            archive_bytes=spec["archive_bytes"],
            uncompressed_sha256=spec["uncompressed_sha256"],
            uncompressed_bytes=spec["uncompressed_bytes"],
        )
        require(type(receipt_raw) is bytes
                and len(receipt_raw) == spec["receipt_bytes"]
                and hashlib.sha256(receipt_raw).hexdigest()
                == spec["receipt_sha256"],
                "a genuine complete version-two durable receipt changed")
        report = decode_json(plain, canonical_required=True)
        receipt = decode_json(receipt_raw, canonical_required=True)
        owners = dict(sorted(PRESERVED_V2_OWNERS[family].items()))
        require(
            report.get("schema") == PRESERVED_V2_SCHEMA
            and report.get("status") == spec["build_status"]
            and report.get("family") == family
            and report.get("label") == "phase2-v2"
            and report.get("source_sha256") == PRESERVED_V2_SOURCE[1]
            and report.get("protocol_sha256") == PRESERVED_V2_PROTOCOL[1]
            and report.get("owned_source_sha256") == owners,
            "an actual authentic version-two source-build result was substituted",
        )
        require(
            receipt.get("schema")
            == PRESERVED_V2_SCHEMA + "-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == spec["build_status"]
            and receipt.get("family") == family
            and receipt.get("label") == "phase2-v2"
            and receipt.get("source_sha256") == PRESERVED_V2_SOURCE[1]
            and receipt.get("protocol_sha256") == PRESERVED_V2_PROTOCOL[1]
            and receipt.get("phase1_manifest_sha256") == FROZEN_INPUTS[1][2]
            and receipt.get("archive_relative") == spec["archive_path"]
            and receipt.get("archive_sha256") == spec["archive_sha256"]
            and receipt.get("archive_bytes") == spec["archive_bytes"]
            and receipt.get("uncompressed_sha256") == spec["uncompressed_sha256"]
            and receipt.get("uncompressed_bytes") == spec["uncompressed_bytes"]
            and receipt.get("owned_source_sha256") == owners
            and receipt.get("receipt_self_publication") == "NOT CLAIMED",
            "a genuine version-two durable publication receipt was substituted",
        )
        published = receipt.get("archive_publication")
        synchronized = receipt.get("archive_directory_fsync")
        require(type(published) is dict
                and published.get("sha256") == spec["archive_sha256"]
                and published.get("bytes") == spec["archive_bytes"]
                and published.get("exclusive_creation") is True
                and published.get("same_inode_readback_verified") is True
                and published.get("file_fsync_completed") is True
                and type(synchronized) is dict
                and synchronized.get("completed") is True,
                "the authentic exclusive, synchronized V2 archive was weakened")
        for observed in (report, receipt):
            for name in effect_names:
                require(observed.get(name) == 0,
                        "historical evidence cannot run a candidate, hidden case, or clock")
            require(observed.get("candidate_correctness") == "NOT MEASURED"
                    and observed.get("performance") == "NOT MEASURED"
                    and observed.get("winner_selected") is False,
                    "a historical source build cannot establish correctness or speed")
        require(report.get("reference_processes_started") == 0
                and report.get("network_requests") == 0,
                "a genuine V2 build cannot run an oracle worker or network request")
        phase1 = report.get("phase1")
        require(type(phase1) is dict and phase1.get("status") == "PASS"
                and phase1.get("suite_count") == 13
                and phase1.get("case_execution_count") == 31_237
                and phase1.get("final_holdout_authorized") is False,
                "preserve the exact previously qualified reference-only correctness matrix")
        audit = report.get("source_independence_audit")
        require(type(audit) is dict
                and audit.get("source_owner_count") == len(owners)
                and audit.get("external_regex_package_count") == 0
                and audit.get("cross_family_dependency_count") == 0,
                "the genuine historical family imported a foreign regular-expression engine")
        phases = report.get("build_phases")
        require(type(phases) is list and len(phases) == 2
                and [phase.get("name") for phase in phases]
                == ["reference-a", "reference-b"],
                "retain both genuinely distinct original V2 build phases")
        for index, phase in enumerate(phases):
            expected_name = "reference-a" if index == 0 else "reference-b"
            require(
                phase.get("fresh_source_directory")
                == "<FRESH_PRIVATE_TMP>/" + expected_name + "/source"
                and phase.get("fresh_native_directory")
                == "<FRESH_PRIVATE_TMP>/" + expected_name + "/native",
                "never reuse a historical source, cache, or native output directory",
            )
            copied = phase.get("copied_source_owners")
            require(type(copied) is dict and set(copied) == set(owners),
                    "retain every actual historical per-phase source owner")
            for relative, digest in owners.items():
                owner = copied[relative]
                require(type(owner) is dict and owner.get("sha256") == digest
                        and owner.get("exclusive_creation") is True
                        and owner.get("same_inode_readback_verified") is True,
                        "a complete historical phase source was replaced")
            outputs = phase.get("native_outputs")
            require(type(outputs) is dict
                    and set(outputs) == set(spec["phase_outputs"][index]),
                    "the historical fresh native output closure is incomplete")
            for role, (digest, size) in spec["phase_outputs"][index].items():
                observed = outputs[role]
                require(type(observed) is dict
                        and observed.get("sha256") == digest
                        and observed.get("size_bytes") == size
                        and observed.get("file_name") == FAMILIES[family]["binaries"][role]
                        and observed.get("path")
                        == "<FRESH_PRIVATE_TMP>/" + expected_name
                        + "/native/" + FAMILIES[family]["binaries"][role]
                        and observed.get("prebuilt_binary_read") is False
                        and observed.get("candidate_imported") is False,
                        "an independently source-built historical native file changed")
        version_names = ["gcc_version", "readelf_version"]
        if family == "rust":
            version_names += ["rustc_version", "cargo_version"]
        elif family == "zig":
            version_names += ["zig_version"]
        schedule = [(name, "reference-a") for name in version_names]
        for phase_name in ("reference-a", "reference-b"):
            if family == "c":
                schedule.append(("build_c_extension", phase_name))
            elif family == "rust":
                schedule.extend([
                    ("build_rust_engine", phase_name),
                    ("build_rust_bridge", phase_name),
                ])
            else:
                schedule.extend([
                    ("build_zig_engine", phase_name),
                    ("build_zig_bridge", phase_name),
                ])
            for role in FAMILIES[family]["binaries"]:
                schedule.extend([
                    (role + "_dynamic", phase_name),
                    (role + "_symbols", phase_name),
                ])
        processes = report.get("processes")
        require(type(processes) is list
                and len(processes) == spec["process_count"] == len(schedule)
                and len({
                    step.get("pid") for step in processes
                    if type(step) is dict and type(step.get("pid")) is int
                    and step["pid"] > 0
                }) == len(schedule),
                "retain every distinct actual compiler and ELF-inspector process")
        streams: dict[tuple[str, str], dict[str, bytes]] = {}
        for step, (name, phase_name) in zip(processes, schedule, strict=True):
            streams[(phase_name, name)] = validate_preserved_v2_process(
                step, family=family, phase=phase_name, name=name,
            )
        for phase in phases:
            phase_name = phase["name"]
            for role in FAMILIES[family]["binaries"]:
                dynamic = parse_elf_dynamic(
                    streams[(phase_name, role + "_dynamic")]["stdout"],
                )
                symbols = parse_elf_symbols(
                    streams[(phase_name, role + "_symbols")]["stdout"],
                )
                require(
                    validate_elf(family, role, dynamic, symbols)
                    == phase["native_outputs"][role]["elf"],
                    "the complete actual historical dynamic or versioned-symbol stream changed",
                )
        if spec["build_status"] == "PASS":
            require(report.get("error") is None
                    and verify_reproducible_phases(family, phases)
                    == report.get("reproducibility"),
                    "a genuine matching two-phase C or Rust build was weakened")
        else:
            require(family == "zig"
                    and report.get("reproducibility") is None
                    and report.get("error") == {
                        "message":
                            "two independent native builds are not byte-for-byte reproducible",
                        "type": "BuildError",
                    }
                    and spec["phase_outputs"][0]["engine"][0]
                    != spec["phase_outputs"][1]["engine"][0]
                    and spec["phase_outputs"][0]["engine"][1]
                    == spec["phase_outputs"][1]["engine"][1]
                    and spec["phase_outputs"][0]["bridge"]
                    == spec["phase_outputs"][1]["bridge"],
                    "never hide or reclassify the actual V2 Zig deterministic-build loss")
        summaries.append({
            "family": family,
            "status": spec["build_status"],
            "archive_sha256": spec["archive_sha256"],
            "archive_bytes": spec["archive_bytes"],
            "receipt_sha256": spec["receipt_sha256"],
            "receipt_bytes": spec["receipt_bytes"],
            "uncompressed_sha256": spec["uncompressed_sha256"],
            "uncompressed_bytes": spec["uncompressed_bytes"],
            "independent_phase_count": 2,
            "genuine_process_count": len(processes),
            "phase_outputs": [
                {
                    role: {"sha256": digest, "size_bytes": size}
                    for role, (digest, size) in phase.items()
                }
                for phase in spec["phase_outputs"]
            ],
            "external_regex_package_count": 0,
            "cross_family_dependency_count": 0,
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED",
        })
    return {
        "source_path": PRESERVED_V2_SOURCE[0],
        "source_sha256": PRESERVED_V2_SOURCE[1],
        "protocol_path": PRESERVED_V2_PROTOCOL[0],
        "protocol_sha256": PRESERVED_V2_PROTOCOL[1],
        "records": summaries,
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "winner_selected": False,
    }


def authenticate_historical_v1_c() -> dict[str, Any]:
    source, _ = authenticate_file(
        ROOT / HISTORICAL_V1_SOURCE[0],
        expected=HISTORICAL_V1_SOURCE[1], maximum=MAX_SOURCE_BYTES,
    )
    protocol, _ = authenticate_file(
        ROOT / HISTORICAL_V1_PROTOCOL[0],
        expected=HISTORICAL_V1_PROTOCOL[1], maximum=MAX_SOURCE_BYTES,
    )
    archive, compressed = authenticate_file(
        ROOT / HISTORICAL_V1_C_ARCHIVE[0],
        expected=HISTORICAL_V1_C_ARCHIVE[1],
        maximum=MAX_ARCHIVE_BYTES, exact_size=HISTORICAL_V1_C_ARCHIVE[2],
        capture=True,
    )
    receipt_owner, receipt_raw = authenticate_file(
        ROOT / HISTORICAL_V1_C_RECEIPT[0],
        expected=HISTORICAL_V1_C_RECEIPT[1],
        maximum=MAX_SOURCE_BYTES, exact_size=HISTORICAL_V1_C_RECEIPT[2],
        capture=True,
    )
    require(compressed is not None and receipt_raw is not None,
            "the exact historical V1 report and receipt were not captured")
    plain = decompress_historical_v1(compressed)
    report = decode_json(plain, canonical_required=True)
    receipt = decode_json(receipt_raw, canonical_required=True)
    require(report.get("schema") == "rebar-phase2-independent-native-source-build-v1"
            and report.get("status") == "PASS" and report.get("family") == "c"
            and report.get("source_sha256") == HISTORICAL_V1_SOURCE[1]
            and report.get("protocol_sha256") == HISTORICAL_V1_PROTOCOL[1]
            and report.get("label") == "phase2-v1",
            "the actual separately published V1 C build was substituted")
    expected_owners = {
        "candidates/_vm_native.c":
            "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55",
        "candidates/vm_candidate.py":
            "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096",
    }
    require(report.get("owned_source_sha256") == expected_owners,
            "an actual historical C owner was silently substituted")
    require(receipt.get("schema")
            == "rebar-phase2-independent-native-source-build-v1-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("family") == "c"
            and receipt.get("label") == "phase2-v1"
            and receipt.get("source_sha256") == HISTORICAL_V1_SOURCE[1]
            and receipt.get("protocol_sha256") == HISTORICAL_V1_PROTOCOL[1]
            and receipt.get("archive_relative") == HISTORICAL_V1_C_ARCHIVE[0]
            and receipt.get("archive_sha256") == HISTORICAL_V1_C_ARCHIVE[1]
            and receipt.get("archive_bytes") == HISTORICAL_V1_C_ARCHIVE[2]
            and receipt.get("uncompressed_sha256")
            == HISTORICAL_V1_C_UNCOMPRESSED_SHA256
            and receipt.get("uncompressed_bytes")
            == HISTORICAL_V1_C_UNCOMPRESSED_BYTES
            and receipt.get("owned_source_sha256") == expected_owners,
            "the authentic original V1 C publication receipt was substituted")
    for record in (report, receipt):
        for key in ("candidate_processes_started", "candidate_imports",
                    "native_libraries_loaded", "hidden_cases_read",
                    "benchmark_files_read", "clock_samples", "timing_trials_run"):
            require(record.get(key) == 0,
                    "the historical C build ran candidate, holdout, or timing work")
        require(record.get("performance") == "NOT MEASURED",
                "historical native build evidence cannot establish speed")
    processes = report.get("processes")
    phases = report.get("build_phases")
    require(type(processes) is list and len(processes) == 8
            and [step.get("name") for step in processes]
            == ["gcc_version", "readelf_version", "build_c_extension",
                "extension_dynamic", "extension_symbols",
                "build_c_extension", "extension_dynamic", "extension_symbols"]
            and type(phases) is list and len(phases) == 2
            and [phase.get("name") for phase in phases]
            == ["reference-a", "reference-b"],
            "the two authentic independent V1 C build processes were omitted")
    require(len({step.get("pid") for step in processes}) == len(processes),
            "a genuine separately recorded historical compiler PID was reused")
    observed_symbols: list[dict[str, Any]] = []
    for offset, phase in ((3, phases[0]), (6, phases[1])):
        dynamic_raw = historical_process_output(
            processes[offset], "extension_dynamic",
        )
        symbol_raw = historical_process_output(
            processes[offset + 1], "extension_symbols",
        )
        require(len(symbol_raw) == HISTORICAL_V1_C_SYMBOL_STDOUT_BYTES
                and hashlib.sha256(symbol_raw).hexdigest()
                == HISTORICAL_V1_C_SYMBOL_STDOUT_SHA256
                and symbol_raw == base64.b64decode(
                    HISTORICAL_V1_C_SYMBOL_STDOUT_BASE64, validate=True,
                ), "a complete original versioned V1 C symbol stream changed")
        symbols = parse_elf_symbols(symbol_raw)
        require(symbols["symbol_count"] == 132
                and symbols["versioned_symbol_count"] == 9
                and HISTORICAL_V1_C_TRUE_VERSIONED_SYMBOLS
                .issubset(set(symbols["undefined"])),
                "the nine actual versioned C library imports were not recovered")
        corrected = validate_elf(
            "c", "extension", parse_elf_dynamic(dynamic_raw), symbols,
        )
        recorded = phase.get("native_outputs", {}).get("extension", {})
        stale = recorded.get("elf", {}).get("undefined", [])
        require(recorded.get("sha256")
                == "ed57383dad99ce311664d165635fa300f3894df6b4816b5f54801d0e68263697"
                and recorded.get("size_bytes") == 163_136
                and set(("(2)", "(3)", "(4)", "(5)", "(6)"))
                .issubset(set(stale)),
                "the genuine historical versioned-symbol parser failure was hidden")
        observed_symbols.append(corrected)
    require(observed_symbols[0] == observed_symbols[1],
            "the two historical genuine source-built symbol streams differ")
    return {
        "status": "AUTHENTIC HISTORICAL BUILD; V1 SYMBOL AUDIT FALSIFIED",
        "candidate_qualified": False,
        "source": source,
        "protocol": protocol,
        "archive": archive,
        "receipt": receipt_owner,
        "uncompressed_sha256": HISTORICAL_V1_C_UNCOMPRESSED_SHA256,
        "uncompressed_bytes": HISTORICAL_V1_C_UNCOMPRESSED_BYTES,
        "complete_reference_phase_count": 2,
        "complete_symbol_table_entries_per_phase": 132,
        "real_versioned_symbol_count_per_phase": 9,
        "true_versioned_symbols": sorted(HISTORICAL_V1_C_TRUE_VERSIONED_SYMBOLS),
        "observed_v1_parser_false_symbols": ["(2)", "(3)", "(4)", "(5)", "(6)"],
        "corrected_actual_symbol_audit": observed_symbols[0],
        "candidate_processes_started": 0,
        "hidden_cases_read": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
    }


def run_build(arguments: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    family = checked_family(arguments["family"])
    label = checked_label(arguments["label"])
    pins = checked_source_pins(family, arguments["owned_source_sha256"])
    support, phase1, preserved_v2 = authenticate_build_inputs(
        family, source_digest=arguments["source_sha256"],
        protocol_digest=arguments["protocol_sha256"],
    )
    history = authenticate_historical_v1_c()
    before, sources = snapshot_owned_sources(family, pins)
    source_audit = audit_owned_sources(family, sources)
    check_fresh_evidence(family, label)
    workdir = tempfile.mkdtemp(prefix=WORK_PREFIX + family + "-", dir="/tmp")
    checked_workdir(workdir)
    report: dict[str, Any] = {
        "schema": SCHEMA, "status": "FAIL", "family": family,
        "label": label, "source_sha256": arguments["source_sha256"],
        "protocol_sha256": arguments["protocol_sha256"],
        "phase1": phase1, "historical_v1_c": history,
        "preserved_version_two": preserved_v2,
        "frozen_support_inputs": support,
        "frozen_support_inputs_after": None,
        "owned_source_sha256": pins,
        "owned_source_before": before,
        "owned_source_after": None,
        "source_independence_audit": source_audit,
        "fresh_private_root": sanitized(workdir, workdir),
        "build_phases": [], "processes": [],
        "reproducibility": None,
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "reference_processes_started": 0,
        "network_requests": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "winner_selected": False,
        "error": None,
    }
    try:
        phase = "reference-a"
        version_commands = ["gcc_version", "readelf_version"]
        if family == "rust":
            version_commands += ["rustc_version", "cargo_version"]
        elif family == "zig":
            version_commands += ["zig_version"]
        initial = phase_paths(workdir, family, phase)
        mkdir_private(initial["base"])
        mkdir_private(initial["temporary"])
        for name in version_commands:
            result = run_process(name, workdir, family, phase, report["processes"])
            validate_version(name, result["stdout"])
        for phase in ("reference-a", "reference-b"):
            report["build_phases"].append(
                exact_build_phase(workdir, family, phase, sources, report["processes"])
            )
        after, _ = snapshot_owned_sources(family, pins)
        report["owned_source_after"] = after
        for path in pins:
            require(before[path]["sha256"] == after[path]["sha256"]
                    and before[path]["size_bytes"] == after[path]["size_bytes"]
                    and before[path]["device"] == after[path]["device"]
                    and before[path]["inode"] == after[path]["inode"],
                    "a candidate owner changed during its isolated source build")
        support_after, phase1_after, preserved_v2_after = authenticate_build_inputs(
            family, source_digest=arguments["source_sha256"],
            protocol_digest=arguments["protocol_sha256"],
        )
        require(phase1_after == phase1
                and preserved_v2_after == preserved_v2
                and set(support_after) == set(support),
                "the frozen correctness, immutable V2 evidence, or compiler closure changed")
        for name, original in support.items():
            current = support_after[name]
            require(
                (original["sha256"], original["size_bytes"],
                 original["device"], original["inode"])
                == (current["sha256"], current["size_bytes"],
                    current["device"], current["inode"]),
                "a frozen compiler, header, protocol, or correctness owner changed: "
                + name,
            )
        report["frozen_support_inputs_after"] = support_after
        report["reproducibility"] = verify_reproducible_phases(
            family, report["build_phases"],
        )
        report["status"] = "PASS"
    except Exception as error:
        report["status"] = "FAIL"
        report["error"] = {
            "type": type(error).__name__, "message": str(error),
        }
    result = publish_report(report, family, label)
    return (0 if report["status"] == "PASS" else 1), result


class SyntheticSandbox:
    """Deny and count every real effect during synthetic-only controls."""

    def __init__(self) -> None:
        self.original: list[tuple[Any, str, Any]] = []
        self.counts = {
            "actual_file_reads": 0, "actual_file_writes": 0,
            "actual_processes": 0, "actual_threads": 0,
            "actual_clocks": 0, "actual_network": 0,
            "actual_candidate_imports": 0,
            "actual_native_library_loads": 0,
            "actual_holdout_reads": 0,
            "blocked_file_operations": 0,
            "blocked_process_operations": 0,
            "blocked_thread_operations": 0,
            "blocked_clock_operations": 0,
            "blocked_network_operations": 0,
            "blocked_import_operations": 0,
            "blocked_temporary_operations": 0,
        }

    def install(self, owner: Any, name: str, replacement: Any) -> None:
        self.original.append((owner, name, getattr(owner, name)))
        setattr(owner, name, replacement)

    def deny(self, counter: str, description: str) -> Any:
        def blocked(*arguments: Any, **keywords: Any) -> Any:
            self.counts[counter] += 1
            raise SourceOnlyError(description)
        return blocked

    def __enter__(self) -> SyntheticSandbox:
        file_block = self.deny(
            "blocked_file_operations", "source-only controls cannot access files",
        )
        for owner, name in (
            (builtins, "open"), (io, "open"),
            (os, "open"), (os, "read"), (os, "write"),
            (os, "stat"), (os, "lstat"), (os, "fstat"),
            (os, "listdir"), (os, "scandir"),
            (os, "mkdir"), (os, "makedirs"),
            (os, "unlink"), (os, "remove"), (os, "replace"),
            (os, "rename"), (os, "link"), (os, "fsync"),
            (Path, "open"), (Path, "read_bytes"), (Path, "read_text"),
            (Path, "write_bytes"), (Path, "write_text"),
            (Path, "stat"), (Path, "lstat"), (Path, "exists"),
            (Path, "is_file"), (Path, "is_dir"), (Path, "mkdir"),
            (Path, "iterdir"),
        ):
            if hasattr(owner, name):
                self.install(owner, name, file_block)
        process_block = self.deny(
            "blocked_process_operations",
            "source-only controls cannot run a compiler or subprocess",
        )
        for owner, name in (
            (subprocess, "Popen"), (subprocess, "run"),
            (subprocess, "check_call"), (subprocess, "check_output"),
            (os, "system"), (os, "popen"),
        ):
            if hasattr(owner, name):
                self.install(owner, name, process_block)
        for name in ("mkdtemp", "mkstemp", "TemporaryDirectory"):
            if hasattr(tempfile, name):
                self.install(tempfile, name, self.deny(
                    "blocked_temporary_operations",
                    "source-only controls cannot create a build directory",
                ))
        self.install(threading.Thread, "start", self.deny(
            "blocked_thread_operations", "source-only controls cannot start a thread",
        ))
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns",
            "perf_counter", "perf_counter_ns", "process_time", "thread_time",
        ):
            if hasattr(time, name):
                self.install(time, name, self.deny(
                    "blocked_clock_operations",
                    "source-only controls cannot measure time or performance",
                ))
        self.install(socket, "socket", self.deny(
            "blocked_network_operations",
            "source-only controls cannot open a network connection",
        ))
        self.install(importlib, "import_module", self.deny(
            "blocked_import_operations",
            "source-only controls cannot import a candidate or native engine",
        ))
        return self

    def __exit__(self, kind: Any, value: Any, trace: Any) -> bool:
        for owner, name, previous in reversed(self.original):
            setattr(owner, name, previous)
        return False


def synthetic_digest(name: str) -> str:
    return hashlib.sha256(name.encode("ascii")).hexdigest()


def synthetic_pins(family: str) -> list[str]:
    checked_family(family)
    return [path + "=" + synthetic_digest(path)
            for path in FAMILIES[family]["owners"]]


def synthetic_dynamic(
    *, needed: tuple[str, ...] = (), soname: str | None = None,
    runpath: str | None = None, rpath: str | None = None,
) -> bytes:
    lines = ["Dynamic section at offset 0x1 contains 1 entry:"]
    for value in needed:
        lines.append(" 0x1 (NEEDED) Shared library: [" + value + "]")
    if soname is not None:
        lines.append(" 0xe (SONAME) Library soname: [" + soname + "]")
    if runpath is not None:
        lines.append(" 0x1d (RUNPATH) Library runpath: [" + runpath + "]")
    if rpath is not None:
        lines.append(" 0xf (RPATH) Library rpath: [" + rpath + "]")
    return ("\n".join(lines) + "\n").encode("ascii")


def synthetic_symbols(exports: tuple[str, ...], undefined: tuple[str, ...]) -> bytes:
    require(type(exports) is tuple and type(undefined) is tuple,
            "individually identified synthetic ELF symbols are mandatory")
    count = 1 + len(exports) + len(undefined)
    lines = [
        "Symbol table '.dynsym' contains " + str(count) + " entries:",
        "   Num:    Value          Size Type    Bind   Vis      Ndx Name",
        "     0: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT  UND",
    ]
    index = 1
    for name in exports:
        require(type(name) is str and bool(name), "a synthetic ELF export is missing")
        trailer = " (2)" if "@" in name else ""
        lines.append(
            str(index) + ": 0000000000000000 1 FUNC GLOBAL DEFAULT 12 "
            + name + trailer
        )
        index += 1
    for name in undefined:
        require(type(name) is str and bool(name), "a synthetic ELF reference is missing")
        trailer = " (2)" if "@" in name else ""
        lines.append(
            str(index) + ": 0000000000000000 0 FUNC GLOBAL DEFAULT UND "
            + name + trailer
        )
        index += 1
    return ("\n".join(lines) + "\n").encode("ascii")


def parse_arguments(arguments: list[str]) -> dict[str, Any]:
    require(type(arguments) is list and all(type(item) is str for item in arguments),
            "supply exact native source-build command arguments")
    if arguments == ["--self-test"]:
        return {"mode": "self-test"}
    require(bool(arguments) and arguments[0] == "--build",
            "select the synthetic --self-test or explicitly authorized --build")
    result: dict[str, Any] = {"mode": "build", "owned_source_sha256": []}
    mapping = {
        "--family": "family", "--label": "label",
        "--source-sha256": "source_sha256",
        "--protocol-sha256": "protocol_sha256",
    }
    position = 1
    while position < len(arguments):
        option = arguments[position]
        require(position + 1 < len(arguments),
                "an exact native source-build option is missing its value")
        value = arguments[position + 1]
        if option == "--owned-source-sha256":
            result["owned_source_sha256"].append(value)
        else:
            require(option in mapping,
                    "reject an abbreviated, repeated, hidden, or performance option")
            key = mapping[option]
            require(key not in result, "reject a repeated native build authorization")
            result[key] = value
        position += 2
    require(set(result) == {
        "mode", "family", "label", "source_sha256", "protocol_sha256",
        "owned_source_sha256",
    }, "pin the recorder, protocol, label, family, and complete source closure")
    checked_family(result["family"])
    checked_label(result["label"])
    checked_digest(result["source_sha256"], "native build recorder")
    checked_digest(result["protocol_sha256"], "native build protocol")
    checked_source_pins(result["family"], result["owned_source_sha256"])
    return result


def self_test() -> dict[str, Any]:
    accepted: list[str] = []
    rejected: list[str] = []
    pending_rejections: list[tuple[str, Any]] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in accepted and name not in rejected,
                "synthetic control names must be individually distinct")
        require(condition, "a required positive native-build control failed: " + name)
        accepted.append(name)

    def reject(name: str, operation: Any) -> None:
        require(type(name) is str and name not in accepted and name not in rejected,
                "synthetic attack names must be individually distinct")
        try:
            operation()
        except (BuildError, TypeError, ValueError, UnicodeError,
                RecursionError, OverflowError, OSError):
            rejected.append(name)
            return
        raise BuildError("an unsafe native-build attack was accepted: " + name)

    with SyntheticSandbox() as guard:
        accept("exact-frozen-python-version", PINNED_PYTHON.endswith("/bin/python3.14"))
        accept("exact-native-cpython-314-extension", EXTENSION_SUFFIX
               == ".cpython-314-x86_64-linux-gnu.so")
        accept("direct-official-rust-1-95-compiler", PINNED_RUSTC.startswith(
            "/home/dev-user/.rustup/toolchains/1.95.0-"
        ) and PINNED_RUSTC.endswith("/bin/rustc"))
        accept("direct-official-rust-1-95-cargo", PINNED_CARGO.startswith(
            "/home/dev-user/.rustup/toolchains/1.95.0-"
        ) and PINNED_CARGO.endswith("/bin/cargo"))
        accept("direct-official-rust-1-95-effective-compiler-driver",
               PINNED_RUST_DRIVER.startswith(
                   "/home/dev-user/.rustup/toolchains/1.95.0-"
               ) and PINNED_RUST_DRIVER.endswith(
                   "/lib/librustc_driver-6108105cd7e839cf.so"
               ) and RUST_INPUTS[2][2]
               == "ae69468875215df490fde685ec1f1b969743482ba7e0251f4074a222606a5484"
               and RUST_INPUTS[2][4] == 153_621_360
               and MAX_BINARY_BYTES >= 153_621_360)
        accept("official-zig-0-16-binary", ZIG_COMPILER
               == "/tmp/zig-x86_64-linux-0.16.0/zig")
        accept("canonical-json-has-one-newline", canonical({"z": 1, "a": 2})
               == b'{"a":2,"z":1}\n')
        accept("strict-three-independent-families", set(FAMILIES)
               == {"c", "rust", "zig"})
        accept("exact-frozen-phase-one-matrix", FROZEN_INPUTS[1][2]
               == "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f")
        accept("synthetic-only-cli", parse_arguments(["--self-test"])
               == {"mode": "self-test"})

        for family in FAMILIES:
            pins = synthetic_pins(family)
            parsed = checked_source_pins(family, pins)
            accept(family + "-complete-distinct-source-closure",
                   set(parsed) == set(FAMILIES[family]["owners"]))
            accept(family + "-order-independent-source-pins",
                   checked_source_pins(family, list(reversed(pins))) == parsed)
            workdir = "/tmp/" + WORK_PREFIX + family + "-synthetic"
            left = phase_paths(workdir, family, "reference-a")
            right = phase_paths(workdir, family, "reference-b")
            accept(family + "-two-independent-fresh-source-roots",
                   left["source"] != right["source"]
                   and left["native"] != right["native"])
            env = build_environment(workdir, family, "reference-a")
            accept(family + "-sanitized-no-parent-environment",
                   env["LC_ALL"] == "C" and env["SOURCE_DATE_EPOCH"] == "1"
                   and env["TMPDIR"].startswith(workdir + "/reference-a/"))
            commands = planned_commands(workdir, family, "reference-a")
            for name, argv in commands.items():
                accept(family + "-exact-command-" + name,
                       checked_command(name, argv, workdir, family, "reference-a")
                       == argv and os.path.isabs(argv[0]))
                changed = list(argv)
                changed[0] = "/usr/bin/" + Path(argv[0]).name
                if changed != argv:
                    reject(family + "-reject-unpinned-command-" + name,
                           lambda name=name, changed=changed,
                           workdir=workdir, family=family:
                           checked_command(name, changed, workdir, family, "reference-a"))
                changed_arg = list(argv)
                changed_arg.append("--network")
                reject(family + "-reject-extra-command-" + name,
                       lambda name=name, changed_arg=changed_arg,
                       workdir=workdir, family=family:
                       checked_command(name, changed_arg, workdir, family, "reference-a"))
            if family == "rust":
                cargo = commands["build_rust_engine"]
                accept("rust-cargo-frozen-locked-and-offline",
                       {"--locked", "--offline", "--frozen"}.issubset(cargo)
                       and cargo[0] == PINNED_CARGO
                       and env["RUSTC"] == PINNED_RUSTC
                       and env["CARGO_NET_OFFLINE"] == "true")
                accept("rust-never-uses-path-1-97", "1.97.1" not in canonical(
                    {"commands": commands, "environment": env}
                ).decode("ascii"))
            if family == "zig":

                zig_command = commands["build_zig_engine"]
                accept("zig-exactly-one-official-native-strip-flag",
                       zig_command.count("-fstrip") == 1
                       and "-fno-strip" not in zig_command
                       and zig_command.index("-fstrip")
                       == zig_command.index("ReleaseFast") + 1)
                accept("zig-independently-private-phase-cache-paths",
                       "--cache-dir" in zig_command
                       and "--global-cache-dir" in zig_command
                       and str(left["local_cache"]) in zig_command
                       and str(left["global_cache"]) in zig_command
                       and left["local_cache"] != right["local_cache"]
                       and left["global_cache"] != right["global_cache"])
                attacks: dict[str, list[str]] = {
                    "missing-native-strip": [
                        item for item in zig_command if item != "-fstrip"
                    ],
                    "explicit-unstripped-debug": [
                        "-fno-strip" if item == "-fstrip" else item
                        for item in zig_command
                    ],
                    "duplicate-native-strip": zig_command + ["-fstrip"],
                    "foreign-post-hoc-stripper": (
                        ["/usr/bin/strip"] + zig_command[1:]
                    ),
                    "shared-other-phase-local-cache": [
                        str(right["local_cache"])
                        if item == str(left["local_cache"]) else item
                        for item in zig_command
                    ],
                    "shared-other-phase-global-cache": [
                        str(right["global_cache"])
                        if item == str(left["global_cache"]) else item
                        for item in zig_command
                    ],
                    "shared-other-phase-source": [
                        str(right["source"] / "candidates/zig/mini_regex.zig")
                        if item == str(
                            left["source"] / "candidates/zig/mini_regex.zig"
                        ) else item
                        for item in zig_command
                    ],
                    "shared-other-phase-output": [
                        "-femit-bin=" + str(right["binary_engine"])
                        if item == "-femit-bin=" + str(left["binary_engine"])
                        else item
                        for item in zig_command
                    ],
                    "unapproved-random-build-id": (
                        zig_command + ["--build-id=uuid"]
                    ),
                }
                for attack_name, hostile_argv in attacks.items():
                    pending_rejections.append((
                        "zig-v3-reject-" + attack_name,
                        lambda hostile_argv=hostile_argv,
                        workdir=workdir:
                        checked_command(
                            "build_zig_engine", hostile_argv,
                            workdir, "zig", "reference-a",
                        ),
                    ))
                accept("zig-cache-is-private-to-fresh-phase",
                       "--cache-dir" in commands["build_zig_engine"]
                       and "--global-cache-dir" in commands["build_zig_engine"]
                       and env["ZIG_GLOBAL_CACHE_DIR"].startswith(workdir))

            for failure in (False, True):
                archive_name, receipt_name = evidence_names(
                    family, "phase2-v3", failure=failure,
                )
                accept(family + "-v3-" + ("failure" if failure else "success")
                       + "-never-reuses-v2-evidence",
                       archive_name.startswith("native-source-build-v3-" + family + "-")
                       and receipt_name.startswith(
                           "native-source-build-v3-" + family + "-"
                       )
                       and "native-source-build-v2-" not in archive_name
                       and "native-source-build-v2-" not in receipt_name
                       and (("-failures" in archive_name) == failure))
            all_args = ["--build", "--family", family, "--label", "source-v1",
                        "--source-sha256", synthetic_digest("source"),
                        "--protocol-sha256", synthetic_digest("protocol")]
            for item in pins:
                all_args += ["--owned-source-sha256", item]
            accept(family + "-complete-explicit-build-cli",
                   parse_arguments(all_args)["family"] == family)
            for index in range(len(pins)):
                missing = pins[:index] + pins[index + 1:]
                reject(family + "-reject-missing-owner-" + str(index),
                       lambda family=family, missing=missing:
                       checked_source_pins(family, missing))
                duplicate = list(pins)
                duplicate[index] = pins[(index + 1) % len(pins)]
                reject(family + "-reject-duplicated-owner-" + str(index),
                       lambda family=family, duplicate=duplicate:
                       checked_source_pins(family, duplicate))
                invalid = list(pins)
                path, _ = invalid[index].split("=", 1)
                invalid[index] = path + "=" + "A" * 64
                reject(family + "-reject-invalid-owner-digest-" + str(index),
                       lambda family=family, invalid=invalid:
                       checked_source_pins(family, invalid))
            for other in FAMILIES:
                if family != other:
                    poisoned = list(pins)
                    poisoned[0] = synthetic_pins(other)[0]
                    reject(family + "-reject-" + other + "-cross-family-owner",
                           lambda family=family, poisoned=poisoned:
                           checked_source_pins(family, poisoned))

        valid_manifest = (
            b'[package]\nname = "rebar-rust-continuation"\n'
            b'version = "0.1.0"\nedition = "2024"\n'
            b'rust-version = "1.85"\npublish = false\n\n'
            b'[lib]\ncrate-type = ["cdylib"]\n\n'
            b'[profile.release]\nopt-level = 3\nlto = true\n'
            b'codegen-units = 1\npanic = "abort"\n'
        )
        valid_lock = (
            b'version = 4\n\n[[package]]\n'
            b'name = "rebar-rust-continuation"\nversion = "0.1.0"\n'
        )
        accept("dependency-free-offline-single-package-rust",
               validate_cargo_closure(valid_manifest, valid_lock)["external_package_count"]
               == 0)
        cargo_attacks = {
            "external-regex-package": valid_manifest + b'\n[dependencies]\nregex = "1"\n',
            "external-git-dependency": valid_manifest + (
                b'\n[dependencies.bad]\ngit = "https://example.invalid/bad"\n'
            ),
            "external-build-dependency": valid_manifest + b'\n[build-dependencies]\ncc = "1"\n',
            "external-workspace": valid_manifest + b'\n[workspace]\nmembers = []\n',
            "cargo-registry-patch": valid_manifest + b'\n[patch.crates-io]\n',
            "unexpected-cargo-features": valid_manifest + b'\n[features]\ndefault = []\n',
            "weakened-cargo-release": valid_manifest.replace(b"opt-level = 3", b"opt-level = 0"),
            "foreign-cargo-package": valid_manifest.replace(
                b"rebar-rust-continuation", b"foreign-rust-matcher"
            ),
            "non-cdylib-rust-engine": valid_manifest.replace(b'"cdylib"', b'"rlib"'),
        }
        for name, value in cargo_attacks.items():
            reject("reject-" + name,
                   lambda value=value: validate_cargo_closure(value, valid_lock))
        for name, poisoned in {
            "foreign-locked-crate": valid_lock + (
                b'\n[[package]]\nname = "regex"\nversion = "1.0.0"\n'
            ),
            "foreign-locked-registry": valid_lock.replace(
                b'version = "0.1.0"',
                b'version = "0.1.0"\nsource = "registry+https://example.invalid"',
            ),
            "changed-lock-version": valid_lock.replace(b"version = 4", b"version = 3"),
        }.items():
            reject("reject-" + name,
                   lambda poisoned=poisoned:
                   validate_cargo_closure(valid_manifest, poisoned))

        for family in FAMILIES:
            own = FAMILIES[family]["adapter_import"]
            source = ("from candidates import " + own + "\n").encode("ascii")
            if family == "zig":
                source += b'engine = "_zig_probe.so"\n'
            source += b'public_match_attribute = "re"\n'
            accept(family + "-owned-python-native-bridge",
                   audit_python_source(source, family=family,
                                       location="candidates/synthetic.py")
                   ["own_native_bridge"] == own)
            for module in sorted(FORBIDDEN_MODULES):
                reject(family + "-forbid-python-module-" + module,
                       lambda family=family, own=own, module=module:
                       audit_python_source(
                           ("from candidates import " + own + "\nimport "
                            + module + "\n").encode("ascii"),
                           family=family, location="candidates/synthetic.py",
                       ))
            for other in FAMILIES:
                if other != family:
                    reject(family + "-forbid-python-bridge-" + other,
                           lambda family=family, other=other:
                           audit_python_source(
                               ("from candidates import "
                                + FAMILIES[other]["adapter_import"] + "\n")
                               .encode("ascii"),
                               family=family, location="candidates/synthetic.py",
                           ))
            for name, attack in (
                ("computed-python-import", b'__import__("re")\n'),
                ("dynamic-module-import", b'importlib.import_module("regex")\n'),
                ("subprocess-delegation", b'subprocess.run(["other"])\n'),
                ("unbounded-native-loader", b'ctypes.util.find_library("pcre")\n'),
                ("dynamic-evaluation", b'eval("import re")\n'),
            ):
                reject(family + "-forbid-" + name,
                       lambda family=family, source=source, attack=attack:
                       audit_python_source(
                           source + attack, family=family,
                           location="candidates/synthetic.py",
                       ))

        synthetic_c = (
            b"#include <Python.h>\n"
            b'const char *public_match_attribute = "re";\n'
            b"void PyInit__vm_native(void) {}\n"
        )
        accept("independent-c-source-entry", audit_native_source(
            synthetic_c, family="c", location="candidates/_vm_native.c"
        )["external_regex_dependency_count"] == 0)
        accept("rust-lifetimes-do-not-swallow-real-engine-exports",
               audit_native_source(
                   b"struct Context<'a> { value: &'a [u8] }\n"
                   b"impl Context<'_> { fn own(&self) {} }\n"
                   b"pub extern fn rebar_compile() {}\n",
                   family="rust", location="candidates/rust/src/lib.rs",
               )["external_regex_dependency_count"] == 0)
        accept("rust-byte-and-character-literals-remain-tokenized",
               ("identifier", "rebar_compile") in native_tokens(
                   b"const X: u8 = b'a'; const Y: char = '\\\\';\n"
                   b"pub extern fn rebar_compile() {}\n"
               ))
        for module in sorted(FORBIDDEN_MODULES):
            reject("reject-computed-native-import-" + module,
                   lambda module=module: audit_native_source(
                       synthetic_c + (
                           'PyImport_ImportModule("' + module + '");\n'
                       ).encode("ascii"),
                       family="c", location="candidates/_vm_native.c",
                   ))
            reject("reject-zig-foreign-compiler-import-" + module,
                   lambda module=module: audit_native_source(
                       ('const foreign = @import("' + module + '");\n'
                        'export fn rebar_zig_compile() void {}\n').encode("ascii"),
                       family="zig", location="candidates/zig/mini_regex.zig",
                   ))
        for name in sorted(FORBIDDEN_NATIVE_NAMES):
            reject("forbid-native-symbol-" + name,
                   lambda name=name: audit_native_source(
                       synthetic_c + ("void " + name + "(void);\n").encode("ascii"),
                       family="c", location="candidates/_vm_native.c",
                   ))
        for prefix in FORBIDDEN_NATIVE_PREFIXES:
            reject("forbid-native-prefix-" + prefix.rstrip("_"),
                   lambda prefix=prefix: audit_native_source(
                       synthetic_c + ("void " + prefix + "foreign(void);\n").encode("ascii"),
                       family="c", location="candidates/_vm_native.c",
                   ))
        accept("ignore-native-comments-without-masking-code",
               audit_native_source(
                   synthetic_c + b"// dlopen regex pcre\n/* dlsym re2 */\n",
                   family="c", location="candidates/_vm_native.c",
               )["external_regex_dependency_count"] == 0)

        c_dynamic = parse_elf_dynamic(synthetic_dynamic(needed=("libc.so.6",)))
        c_symbols = parse_elf_symbols(synthetic_symbols(("PyInit__vm_native",), ()))
        accept("authentic-c-native-abi",
               validate_elf("c", "extension", c_dynamic, c_symbols)
               ["required_exports"] == ["PyInit__vm_native"])
        for family in ("rust", "zig"):
            exports = tuple(sorted(
                RUST_ENGINE_EXPORTS if family == "rust" else ZIG_ENGINE_EXPORTS
            ))
            name = FAMILIES[family]["binaries"]["engine"]
            engine_dynamic = parse_elf_dynamic(synthetic_dynamic(
                needed=("libc.so.6",), soname=name,
            ))
            engine_symbols = parse_elf_symbols(synthetic_symbols(exports, ()))
            accept(family + "-authentic-native-engine-abi",
                   validate_elf(family, "engine", engine_dynamic, engine_symbols)
                   ["soname"] == [name])
            initial = "PyInit__" + family + "_bridge"
            own_reference = "rebar_compile" if family == "rust" else "rebar_zig_compile"
            bridge_dynamic = parse_elf_dynamic(synthetic_dynamic(
                needed=(name, "libc.so.6"), runpath="$ORIGIN",
            ))
            bridge_symbols = parse_elf_symbols(synthetic_symbols(
                (initial,), (own_reference,),
            ))
            accept(family + "-authentic-native-bridge-abi",
                   validate_elf(family, "bridge", bridge_dynamic, bridge_symbols)
                   ["runpath"] == ["$ORIGIN"])
            attacks = {
                "foreign-engine-needed": parse_elf_dynamic(synthetic_dynamic(
                    needed=(name, "libpcre2-8.so.0"), runpath="$ORIGIN",
                )),
                "foreign-absolute-runpath": parse_elf_dynamic(synthetic_dynamic(
                    needed=(name,), runpath="/tmp/foreign",
                )),
                "legacy-rpath-delegation": parse_elf_dynamic(synthetic_dynamic(
                    needed=(name,), runpath="$ORIGIN", rpath="/tmp/foreign",
                )),
                "missing-own-engine-dependency": parse_elf_dynamic(synthetic_dynamic(
                    needed=("libc.so.6",), runpath="$ORIGIN",
                )),
            }
            for attack_name, poisoned in attacks.items():
                reject(family + "-reject-" + attack_name,
                       lambda family=family, poisoned=poisoned,
                       bridge_symbols=bridge_symbols:
                       validate_elf(family, "bridge", poisoned, bridge_symbols))
            reject(family + "-reject-substituted-engine-soname",
                   lambda family=family, name=name, engine_symbols=engine_symbols:
                   validate_elf(family, "engine", parse_elf_dynamic(
                       synthetic_dynamic(needed=("libc.so.6",),
                                         soname="foreign-" + name)
                   ), engine_symbols))
            reject(family + "-reject-omitted-engine-export",
                   lambda family=family, name=name, exports=exports:
                   validate_elf(family, "engine", parse_elf_dynamic(
                       synthetic_dynamic(needed=("libc.so.6",), soname=name)
                   ), parse_elf_symbols(synthetic_symbols(exports[:-1], ()))))

        actual_historical_stream = base64.b64decode(
            HISTORICAL_V1_C_SYMBOL_STDOUT_BASE64, validate=True,
        )
        historical_symbols = parse_elf_symbols(actual_historical_stream)
        accept("actual-v1-complete-132-entry-c-gnu-symbol-stream",
               len(actual_historical_stream) == HISTORICAL_V1_C_SYMBOL_STDOUT_BYTES
               and hashlib.sha256(actual_historical_stream).hexdigest()
               == HISTORICAL_V1_C_SYMBOL_STDOUT_SHA256
               and historical_symbols["symbol_count"] == 132
               and len(historical_symbols["symbol_records"]) == 132)
        accept("actual-v1-nine-versioned-c-libc-symbols-recovered",
               historical_symbols["versioned_symbol_count"] == 9
               and HISTORICAL_V1_C_TRUE_VERSIONED_SYMBOLS
               .issubset(set(historical_symbols["undefined"])))
        accept("actual-v1-bogus-parenthetical-undefined-symbols-removed",
               not set(("(2)", "(3)", "(4)", "(5)", "(6)"))
               .intersection(historical_symbols["undefined"]))
        accept("actual-v1-complete-real-c-elf-revalidated",
               validate_elf(
                   "c", "extension",
                   parse_elf_dynamic(synthetic_dynamic(needed=("libc.so.6",))),
                   historical_symbols,
               )["required_exports"] == ["PyInit__vm_native"])
        accept("gnu-default-symbol-version-normalized",
               checked_symbol_name("memcpy@@GLIBC_2.14")
               == ("memcpy", "GLIBC_2.14", True))
        accept("gnu-imported-symbol-version-normalized",
               checked_symbol_name("memcpy@GLIBC_2.14")
               == ("memcpy", "GLIBC_2.14", False))

        for symbol in sorted(FORBIDDEN_NATIVE_NAMES):
            for state, value in (
                ("plain", symbol),
                ("versioned", symbol + "@GLIBC_2.2.5"),
                ("default-versioned", symbol + "@@GLIBC_2.2.5"),
            ):
                reject("reject-" + state + "-elf-reference-" + symbol,
                       lambda value=value: parse_elf_symbols(
                           synthetic_symbols(("PyInit__vm_native",), (value,))
                       ))
                reject("reject-" + state + "-elf-export-" + symbol,
                       lambda value=value: parse_elf_symbols(
                           synthetic_symbols(("PyInit__vm_native", value), ())
                       ))
        for prefix in FORBIDDEN_NATIVE_PREFIXES:
            actual = prefix + "foreign"
            for state, value in (
                ("plain", actual),
                ("versioned", actual + "@GLIBC_2.2.5"),
                ("default-versioned", actual + "@@GLIBC_2.2.5"),
            ):
                reject("reject-" + state + "-elf-prefix-" + prefix.rstrip("_"),
                       lambda value=value: parse_elf_symbols(
                           synthetic_symbols(("PyInit__vm_native",), (value,))
                       ))

        for family in FAMILIES:
            current = FAMILIES[family]
            for other in FAMILIES:
                if family == other:
                    continue
                if family == "c":
                    own_exports = ("PyInit__vm_native",)
                    dynamic = parse_elf_dynamic(
                        synthetic_dynamic(needed=("libc.so.6",))
                    )
                    role = "extension"
                else:
                    own_exports = ("PyInit__" + family + "_bridge",)
                    own_engine = current["binaries"]["engine"]
                    dynamic = parse_elf_dynamic(synthetic_dynamic(
                        needed=(own_engine, "libc.so.6"), runpath="$ORIGIN",
                    ))
                    role = "bridge"
                foreign = (
                    "rebar_zig_compile" if other == "zig"
                    else "rebar_compile" if other == "rust"
                    else "PyInit__vm_native"
                )
                own_reference = (
                    () if family == "c"
                    else ("rebar_compile",) if family == "rust"
                    else ("rebar_zig_compile",)
                )
                for state, adversarial in (
                    ("plain", foreign),
                    ("versioned", foreign + "@FOREIGN_1.0"),
                    ("default-versioned", foreign + "@@FOREIGN_1.0"),
                ):
                    reject(
                        family + "-reject-" + state + "-" + other
                        + "-cross-engine-undefined",
                        lambda family=family, role=role, dynamic=dynamic,
                        own_exports=own_exports, own_reference=own_reference,
                        adversarial=adversarial: validate_elf(
                            family, role, dynamic,
                            parse_elf_symbols(synthetic_symbols(
                                own_exports, own_reference + (adversarial,),
                            )),
                        ),
                    )
                    reject(
                        family + "-reject-" + state + "-" + other
                        + "-cross-engine-export",
                        lambda family=family, role=role, dynamic=dynamic,
                        own_exports=own_exports, own_reference=own_reference,
                        adversarial=adversarial: validate_elf(
                            family, role, dynamic,
                            parse_elf_symbols(synthetic_symbols(
                                own_exports + (adversarial,), own_reference,
                            )),
                        ),
                    )
        valid_versioned = synthetic_symbols(
            ("PyInit__vm_native",), ("memcpy@GLIBC_2.14",),
        )
        for title, poisoned in (
            ("hidden-trailing-symbol", valid_versioned.replace(
                b"memcpy@GLIBC_2.14 (2)",
                b"memcpy@GLIBC_2.14 (2) regexec@GLIBC_2.2.5",
            )),
            ("trailing-marker-without-version", valid_versioned.replace(
                b"memcpy@GLIBC_2.14 (2)", b"memcpy (2)",
            )),
            ("nondecimal-version-marker", valid_versioned.replace(
                b"memcpy@GLIBC_2.14 (2)", b"memcpy@GLIBC_2.14 (x)",
            )),
            ("zero-version-marker", valid_versioned.replace(
                b"memcpy@GLIBC_2.14 (2)", b"memcpy@GLIBC_2.14 (0)",
            )),
            ("missing-symbol-version", valid_versioned.replace(
                b"memcpy@GLIBC_2.14 (2)", b"memcpy@ (2)",
            )),
            ("misplaced-double-symbol-version", valid_versioned.replace(
                b"memcpy@GLIBC_2.14 (2)", b"memcpy@BAD@GLIBC_2.14 (2)",
            )),
            ("hidden-third-symbol-version", valid_versioned.replace(
                b"memcpy@GLIBC_2.14 (2)", b"memcpy@@@GLIBC_2.14 (2)",
            )),
            ("omitted-gnu-symbol-row", valid_versioned.replace(
                b"memcpy@GLIBC_2.14 (2)", b"",
            )),
            ("inflated-gnu-symbol-count", valid_versioned.replace(
                b"contains 3 entries:", b"contains 4 entries:",
            )),
            ("truncated-real-versioned-gnu-table", actual_historical_stream[:-1]),
            ("noncanonical-real-versioned-symbol-encoding",
             actual_historical_stream + b"hidden foreign record\\n"),
        ):
            reject("reject-" + title,
                   lambda poisoned=poisoned: parse_elf_symbols(poisoned))

        for value in (None, "", "A" * 64, "a" * 63, "a" * 65,
                      "g" * 64, 7, True, b"a" * 64):
            reject("invalid-sha256-" + str(len(rejected)),
                   lambda value=value: checked_digest(value, "synthetic"))
        for value in ("", "/tmp/other", "../owner", "a/../b", "a//b",
                      "./owner", "a/./b", "a\\b", "a\x00b"):
            reject("reject-unsafe-relative-path-" + str(len(rejected)),
                   lambda value=value: checked_relative(value))
        for value in ("", "A", "../x", "a_b", "a--b", "a-", "/tmp/x",
                      "x" * 49):
            reject("reject-unsafe-label-" + str(len(rejected)),
                   lambda value=value: checked_label(value))
        for value in ("/", "/tmp", "/tmp/other", "/tmp/" + WORK_PREFIX + "x/../x",
                      "/tmp/" + WORK_PREFIX + "x/child",
                      "/tmp/" + WORK_PREFIX + "x/"):
            reject("reject-broad-build-root-" + str(len(rejected)),
                   lambda value=value: checked_workdir(value))
        for raw in (b'{"x":1,"x":2}\n', b'{"x":NaN}\n',
                    b'{"x":Infinity}\n', b'{"x":-Infinity}\n',
                    b"[]\n", b"", b"{", b"\xff"):
            reject("reject-unsafe-json-" + str(len(rejected)),
                   lambda raw=raw: decode_json(raw, canonical_required=False))
        for name, operation in (
            ("actual-filesystem-open", lambda: builtins.open("/tmp/forbidden")),
            ("actual-filesystem-os-open", lambda: os.open("/tmp/forbidden", os.O_RDONLY)),
            ("actual-source-read", lambda: Path("/tmp/forbidden").read_bytes()),
            ("actual-source-write", lambda: Path("/tmp/forbidden").write_bytes(b"x")),
            ("actual-directory-scan", lambda: os.listdir("/tmp")),
            ("actual-compiler-subprocess", lambda: subprocess.run([PINNED_RUSTC])),
            ("actual-compiler-popen", lambda: subprocess.Popen([ZIG_COMPILER])),
            ("actual-private-temp-root", lambda: tempfile.mkdtemp()),
            ("actual-thread-start", lambda: threading.Thread(target=lambda: None).start()),
            ("actual-clock", lambda: time.time()),
            ("actual-performance-clock", lambda: time.perf_counter_ns()),
            ("actual-network", lambda: socket.socket()),
            ("actual-candidate-import", lambda: importlib.import_module(
                "candidates.rust_candidate"
            )),
        ):
            reject("source-only-blocks-" + name, operation)

        for name, operation in pending_rejections:
            reject(name, operation)

        accept("standalone-version-three-recorder-owner",
               SOURCE_RELATIVE == "tools/reproduce_phase2_native_builds_v3.py"
               and PROTOCOL_RELATIVE
               == "oracle/phase2/NATIVE-SOURCE-BUILDS-V3.md")
        accept("strictly-distinct-version-three-schema-and-private-roots",
               SCHEMA == "rebar-phase2-independent-native-source-build-v3"
               and RECEIPT_SCHEMA == SCHEMA + "-durable-publication-receipt"
               and WORK_PREFIX == "rebar-phase2-native-build-v3-"
               and PRESERVED_V2_SCHEMA != SCHEMA)
        accept("preserve-immutable-version-two-source-and-protocol",
               PRESERVED_V2_SOURCE == (
                   "tools/reproduce_phase2_native_builds_v2.py",
                   "e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796",
                   136_677,
               ) and PRESERVED_V2_PROTOCOL == (
                   "oracle/phase2/NATIVE-SOURCE-BUILDS-V2.md",
                   "f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603",
                   13_032,
               ))
        for historical in PRESERVED_V2_RECORDS:
            family = historical["family"]
            accept(family + "-preserve-exact-authentic-version-two-result",
                   validate_preserved_v2_specification(historical) == historical)
            for key in (
                "build_status", "archive_path", "archive_sha256",
                "archive_bytes", "uncompressed_sha256", "uncompressed_bytes",
                "receipt_path", "receipt_sha256", "receipt_bytes",
                "process_count", "phase_outputs",
            ):
                poisoned = copy.deepcopy(historical)
                if key in ("archive_bytes", "uncompressed_bytes",
                           "receipt_bytes", "process_count"):
                    poisoned[key] += 1
                elif key == "build_status":
                    poisoned[key] = "FAIL" if historical[key] == "PASS" else "PASS"
                elif key == "phase_outputs":
                    poisoned[key] = tuple(reversed(historical[key]))
                    if poisoned[key] == historical[key]:
                        first = copy.deepcopy(historical[key][0])
                        role = next(iter(first))
                        first[role] = (
                            synthetic_digest(family + "-false-history"),
                            first[role][1],
                        )
                        poisoned[key] = (first, historical[key][1])
                elif key.endswith("sha256"):
                    poisoned[key] = synthetic_digest(family + "-" + key)
                else:
                    poisoned[key] += "-substituted"
                reject(family + "-reject-substituted-v2-" + key.replace("_", "-"),
                       lambda poisoned=poisoned:
                       validate_preserved_v2_specification(poisoned))
        accept("truthful-durable-zig-failure-publication",
               PRESERVED_V2_RECORDS[2]["family"] == "zig"
               and PRESERVED_V2_RECORDS[2]["build_status"] == "FAIL"
               and PRESERVED_V2_RECORDS[2]["phase_outputs"][0]["engine"][0]
               != PRESERVED_V2_RECORDS[2]["phase_outputs"][1]["engine"][0]
               and PRESERVED_V2_RECORDS[2]["phase_outputs"][0]["bridge"]
               == PRESERVED_V2_RECORDS[2]["phase_outputs"][1]["bridge"])
        source_only_plain = canonical({"schema": PRESERVED_V2_SCHEMA, "value": 1})
        source_only_archive = gzip.compress(source_only_plain, compresslevel=9, mtime=0)
        source_only_archive_sha256 = hashlib.sha256(source_only_archive).hexdigest()
        source_only_plain_sha256 = hashlib.sha256(source_only_plain).hexdigest()
        source_only_options = {
            "archive_sha256": source_only_archive_sha256,
            "archive_bytes": len(source_only_archive),
            "uncompressed_sha256": source_only_plain_sha256,
            "uncompressed_bytes": len(source_only_plain),
        }
        accept("bounded-canonical-single-member-v2-history-decoder",
               decompress_preserved_v2(source_only_archive, **source_only_options)
               == source_only_plain)
        for attack, raw in (
            ("truncated-member", source_only_archive[:-1]),
            ("concatenated-member", source_only_archive + source_only_archive),
            ("appended-member", source_only_archive + b"hidden"),
            ("empty-member", b""),
        ):
            reject("v3-reject-" + attack,
                   lambda raw=raw:
                   decompress_preserved_v2(raw, **source_only_options))
        for key in ("archive_sha256", "archive_bytes",
                    "uncompressed_sha256", "uncompressed_bytes"):
            hostile = dict(source_only_options)
            if key.endswith("sha256"):
                hostile[key] = synthetic_digest("wrong-" + key)
            else:
                hostile[key] += 1
            reject("v3-reject-resigned-" + key.replace("_", "-"),
                   lambda hostile=hostile:
                   decompress_preserved_v2(source_only_archive, **hostile))

        require(len(accepted) == len(set(accepted))
                and len(rejected) == len(set(rejected)),
                "every native build control must retain its exact distinct identity")
        require(all(guard.counts[key] == 0 for key in (
            "actual_file_reads", "actual_file_writes", "actual_processes",
            "actual_threads", "actual_clocks", "actual_network",
            "actual_candidate_imports", "actual_native_library_loads",
            "actual_holdout_reads",
        )), "synthetic controls performed a real external action")
        counters = dict(guard.counts)

    return {
        "schema": SCHEMA + "-synthetic-source-only-self-test",
        "status": "PASS",
        "synthetic": True,
        "positive_control_count": len(accepted),
        "positive_controls": accepted,
        "rejected_attack_count": len(rejected),
        "rejected_attacks": rejected,
        "guard_counters": counters,
        "family_count": 3,
        "candidate_workers_started": 0,
        "reference_workers_started": 0,
        "native_builds_started": 0,
        "native_libraries_loaded": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "candidate_correctness": "NOT MEASURED",
        "winner_selected": False,
        "holdout": "NOT OPENED",
    }


def main(arguments: list[str] | None = None) -> int:
    try:
        parsed = parse_arguments(list(sys.argv[1:] if arguments is None else arguments))
        if parsed["mode"] == "self-test":
            result = self_test()
            sys.stdout.buffer.write(canonical(result))
            sys.stdout.buffer.flush()
            return 0
        status, result = run_build(parsed)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return status
    except (BuildError, OSError, ValueError, UnicodeError) as error:
        sys.stderr.write(type(error).__name__ + ": " + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
