#!/usr/bin/env sh
set -eu

py=${PYTHON:-/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14}
include=$($py -I -c 'import sysconfig; print(sysconfig.get_path("include"))')
suffix=$($py -I -c 'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX"))')
extra=${REBAR_VM_CFLAGS:-}

# Intentional word splitting lets callers pass sanitizer flags in REBAR_VM_CFLAGS.
# shellcheck disable=SC2086
cc -std=c11 -O3 -Wall -Wextra -Werror -fPIC -shared $extra -I"$include" candidates/_vm_native.c -o "candidates/_vm_native$suffix"
printf '%s\n' "built candidates/_vm_native$suffix"
