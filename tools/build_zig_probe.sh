#!/bin/sh
set -eu
zig_bin=${REBAR_ZIG:-/tmp/rebar-design-survey/zig-0.16.0/zig}
test -x "$zig_bin"
ZIG_GLOBAL_CACHE_DIR=${ZIG_GLOBAL_CACHE_DIR:-/tmp/rebar-zig-global-cache}
ZIG_LOCAL_CACHE_DIR=${ZIG_LOCAL_CACHE_DIR:-/tmp/rebar-zig-local-cache}
export ZIG_GLOBAL_CACHE_DIR ZIG_LOCAL_CACHE_DIR
"$zig_bin" build-lib candidates/zig/mini_regex.zig -dynamic -lc -O ReleaseFast -femit-bin=candidates/_zig_probe.so
echo 'built candidates/_zig_probe.so'
