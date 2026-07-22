#!/usr/bin/env sh
set -eu

target_dir=${REBAR_RUST_TARGET_DIR:-/tmp/rebar-rust-target}
cargo build --manifest-path candidates/rust/Cargo.toml --release --offline --target-dir "$target_dir"
cp "$target_dir/release/librebar_rust_continuation.so" candidates/_rust_engine.so
python_bin=${PYTHON:-/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14}
include_dir=$("$python_bin" -c 'import sysconfig; print(sysconfig.get_path("include"))')
extension_suffix=$("$python_bin" -c 'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX"))')
cc -std=c11 -O3 -fPIC -shared -Wall -Wextra -Werror "-I$include_dir" candidates/rust/py_bridge.c -Lcandidates -l:_rust_engine.so '-Wl,-rpath,$ORIGIN' -o "candidates/_rust_bridge$extension_suffix"
printf '%s\n' 'built candidates/_rust_engine.so and candidates/_rust_bridge'
