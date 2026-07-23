#!/bin/sh
set -eu

# Generate an isolated, instrumented source for executor-count experiments.
# The optimized production source and build remain counter-free.
zig_bin=${REBAR_ZIG:-/tmp/rebar-design-survey/zig-0.16.0/zig}
python_bin=${PYTHON:-/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14}
profile_source=$(mktemp /tmp/rebar-zig-profile-v6.XXXXXX.zig)
trap 'rm -f "$profile_source"' EXIT HUP INT TERM
test -x "$zig_bin"
test -x "$python_bin"

sed \
  -e '/^const ParseError =/i\
var zig_profile = [_]u64{0} ** 12;\
pub export fn rebar_zig_profile_reset() void { zig_profile = [_]u64{0} ** 12; }\
pub export fn rebar_zig_profile_get(index: usize) u64 { return if (index < zig_profile.len) zig_profile[index] else 0; }\
' \
  -e '/^fn equal(/a\
    zig_profile[7] += 1;\
' \
  -e '/^fn classMatch(/a\
    zig_profile[5] += 1;\
    zig_profile[8] += @intFromBool(value < 256 and class.match_flags == flags & 0xffff);\
' \
  -e '/^fn runLength(/a\
    zig_profile[9] += 1;\
' \
  -e '/^            if (text.kind == 1 and class.match_flags == run.flags \& 0xffff) {/a\
                zig_profile[10] += 1;\
' \
  -e '/^            } else while (length < maximum and classMatch(program, class, text.at(pos + length), run.flags))/i\
                zig_profile[11] += 1;\
' \
  -e '/^fn runBytecode(/a\
    zig_profile[0] += 1;\
' \
  -e '/^fn runCapturedAt(/a\
    zig_profile[1] += 1;\
' \
  -e '/^    while (true) {/a\
        zig_profile[3] += 1;\
' \
  -e '/^            \.split => {/a\
                zig_profile[4] += 1;\
' \
  -e '/^            \.start_split => {/a\
                zig_profile[4] += 1;\
' \
  -e '/^        const found = runBytecode(/i\
        zig_profile[2] += 1;\
' \
  -e '/^        const finish = runCaptured(/i\
        zig_profile[2] += 1;\
' \
  -e '/^pub export fn rebar_zig_collect_records_wide(/a\
    zig_profile[6] += 1;\
' \
  candidates/zig/mini_regex.zig > "$profile_source"

ZIG_GLOBAL_CACHE_DIR=${ZIG_GLOBAL_CACHE_DIR:-/tmp/rebar-zig-global-cache}
ZIG_LOCAL_CACHE_DIR=${ZIG_LOCAL_CACHE_DIR:-/tmp/rebar-zig-local-cache}
export ZIG_GLOBAL_CACHE_DIR ZIG_LOCAL_CACHE_DIR
"$zig_bin" build-lib "$profile_source" -dynamic -lc -fallow-shlib-undefined -O ReleaseFast -fsoname=_zig_probe.so -femit-bin=candidates/_zig_probe.so
include_dir=$("$python_bin" -c 'import sysconfig; print(sysconfig.get_path("include"))')
extension_suffix=$("$python_bin" -c 'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX"))')
cc -std=c11 -O3 -fPIC -shared -Wall -Wextra -Werror "-I$include_dir" candidates/zig/py_bridge.c -Lcandidates -l:_zig_probe.so '-Wl,-rpath,$ORIGIN' -o "candidates/_zig_bridge$extension_suffix"
echo 'built temporary instrumented Zig matcher; rebuild with tools/build_zig_probe.sh before timing'
