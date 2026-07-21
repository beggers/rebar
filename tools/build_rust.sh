#!/usr/bin/env sh
set -eu

target_dir=${REBAR_RUST_TARGET_DIR:-/tmp/rebar-rust-target}
cargo build --manifest-path candidates/rust/Cargo.toml --release --offline --target-dir "$target_dir"
cp "$target_dir/release/librebar_rust_continuation.so" candidates/_rust_engine.so
printf '%s\n' 'built candidates/_rust_engine.so'
