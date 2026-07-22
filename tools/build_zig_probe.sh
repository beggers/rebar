#!/bin/sh
set -eu
zig_bin=${REBAR_ZIG:-/tmp/rebar-design-survey/zig-0.16.0/zig}
test -x "$zig_bin"
ZIG_GLOBAL_CACHE_DIR=${ZIG_GLOBAL_CACHE_DIR:-/tmp/rebar-zig-global-cache}
ZIG_LOCAL_CACHE_DIR=${ZIG_LOCAL_CACHE_DIR:-/tmp/rebar-zig-local-cache}
export ZIG_GLOBAL_CACHE_DIR ZIG_LOCAL_CACHE_DIR
"$zig_bin" build-lib candidates/zig/mini_regex.zig -dynamic -lc -fallow-shlib-undefined -O ReleaseFast -fsoname=_zig_probe.so -femit-bin=candidates/_zig_probe.so
python_bin=${PYTHON:-/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14}
include_dir=$("$python_bin" -c 'import sysconfig; print(sysconfig.get_path("include"))')
extension_suffix=$("$python_bin" -c 'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX"))')
cc -std=c11 -O3 -fPIC -shared -Wall -Wextra -Werror "-I$include_dir" candidates/zig/py_bridge.c -Lcandidates -l:_zig_probe.so '-Wl,-rpath,$ORIGIN' -o "candidates/_zig_bridge$extension_suffix"
echo 'built candidates/_zig_probe.so and candidates/_zig_bridge'
