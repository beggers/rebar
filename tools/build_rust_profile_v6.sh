#!/bin/sh
set -eu

# Build a separately loaded, instrumented Rust candidate under /tmp.
# The production Rust source, shared objects, and Python package are untouched.
python_bin=${PYTHON:-/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14}
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(CDPATH= cd -- "$script_dir/.." && pwd)
profile_dir=${REBAR_RUST_PROFILE_DIR:-}
profile_revision=${REBAR_RUST_PROFILE_REVISION:-}

test -x "$python_bin"
if [ -z "$profile_dir" ]; then
    profile_dir=$(mktemp -d /tmp/rebar-rust-profile-v6.XXXXXX)
fi
case "$profile_dir" in
    /tmp/rebar-rust-profile-v6.*) ;;
    *) printf '%s\n' 'profile directory must be /tmp/rebar-rust-profile-v6.*' >&2; exit 2 ;;
esac

package_dir=$profile_dir/candidates
mkdir -p "$package_dir"
snapshot_root=$repo_dir
if [ -n "$profile_revision" ]; then
    snapshot_root=$profile_dir/revision-snapshot
    mkdir -p "$snapshot_root"
    git -C "$repo_dir" archive --format=tar "$profile_revision" \
        candidates/rust/src/lib.rs candidates/rust/py_bridge.c \
        candidates/rust_candidate.py | tar -xf - -C "$snapshot_root"
fi
cp "$snapshot_root/candidates/rust/src/lib.rs" "$profile_dir/rust-source-snapshot.rs"
cp "$snapshot_root/candidates/rust/py_bridge.c" "$profile_dir/rust-bridge-snapshot.c"
cp "$snapshot_root/candidates/rust_candidate.py" "$package_dir/rust_candidate.py"

awk '
BEGIN { pending_export = -1 }
NR == 1 {
    print "use std::alloc::{GlobalAlloc, Layout, System};"
    print "use std::sync::atomic::{AtomicU64, Ordering};"
    print ""
    print "static RUST_PROFILE: [AtomicU64; 64] = [const { AtomicU64::new(0) }; 64];"
    print "#[inline(always)]"
    print "fn rust_profile_inc(index: usize) { RUST_PROFILE[index].fetch_add(1, Ordering::Relaxed); }"
    print "#[inline(always)]"
    print "fn rust_profile_add(index: usize, value: usize) { RUST_PROFILE[index].fetch_add(value as u64, Ordering::Relaxed); }"
    print "struct RustProfileAllocator;"
    print "unsafe impl GlobalAlloc for RustProfileAllocator {"
    print "    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {"
    print "        rust_profile_inc(19); rust_profile_add(22, layout.size());"
    print "        unsafe { System.alloc(layout) }"
    print "    }"
    print "    unsafe fn alloc_zeroed(&self, layout: Layout) -> *mut u8 {"
    print "        rust_profile_inc(19); rust_profile_add(22, layout.size());"
    print "        unsafe { System.alloc_zeroed(layout) }"
    print "    }"
    print "    unsafe fn dealloc(&self, pointer: *mut u8, layout: Layout) {"
    print "        rust_profile_inc(20); unsafe { System.dealloc(pointer, layout) }"
    print "    }"
    print "    unsafe fn realloc(&self, pointer: *mut u8, layout: Layout, size: usize) -> *mut u8 {"
    print "        rust_profile_inc(21); rust_profile_add(23, size);"
    print "        unsafe { System.realloc(pointer, layout, size) }"
    print "    }"
    print "}"
    print "#[global_allocator] static RUST_PROFILE_ALLOCATOR: RustProfileAllocator = RustProfileAllocator;"
    print "#[unsafe(no_mangle)]"
    print "pub extern \"C\" fn rebar_rust_profile_reset() {"
    print "    for counter in &RUST_PROFILE { counter.store(0, Ordering::Relaxed); }"
    print "}"
    print "#[unsafe(no_mangle)]"
    print "pub extern \"C\" fn rebar_rust_profile_get(index: usize) -> u64 {"
    print "    RUST_PROFILE.get(index).map_or(0, |counter| counter.load(Ordering::Relaxed))"
    print "}"
    print ""
}
{
    gsub(/state\.clone\(\)/, "rust_profile_clone(state)")
}
/^struct State[[:space:]]*\{/ { in_state = 1 }
in_state && /^\}/ {
    print
    print "#[inline(always)]"
    print "fn rust_profile_clone(state: &State) -> State {"
    print "    rust_profile_inc(8); Clone::clone(state)"
    print "}"
    in_state = 0
    clone_helper = 1
    next
}
/^fn eval\(/ {
    print
    print "    rust_profile_inc(7);"
    print "    match node {"
    print "        Expr::Seq(_) => rust_profile_inc(9),"
    print "        Expr::Alt(_) => rust_profile_inc(10),"
    print "        Expr::Group(_, _) => rust_profile_inc(11),"
    print "        Expr::Repeat(_, _, _, _) => rust_profile_inc(12),"
    print "        Expr::Look(_, _, _, _) => rust_profile_inc(28),"
    print "        Expr::Backref(_, _) => rust_profile_inc(29),"
    print "        _ => {},"
    print "    }"
    eval_seen = 1
    next
}
/^fn eq_lit\(/ { print; print "    rust_profile_inc(15);"; next }
/^fn category\(/ { print; print "    rust_profile_inc(17);"; next }
/^fn prepare_classes\(/ { print; print "    rust_profile_inc(27);"; next }
/^fn repeat_layout\(/ { print; print "    rust_profile_inc(25);"; next }
/^fn start_table\(/ { print; print "    rust_profile_inc(26);"; next }
/^[[:space:]]*fn emit\(&mut self, instruction: Instruction\) -> usize \{/ {
    print; print "        rust_profile_inc(57);"; next
}
/^[[:space:]]*fn compile\(root: &Expr\) -> Option<Program> \{/ {
    print; print "        rust_profile_inc(56);"; next
}
/^[[:space:]]*self\.program\.runs\.push\(CompiledRun \{/ {
    print "                    rust_profile_inc(58);"
    print
    next
}
/^fn class_match\(/ { pending_class = 1 }
pending_class && /^\) -> bool \{/ {
    print
    print "    rust_profile_inc(16);"
    pending_class = 0
    next
}
/^[[:space:]]*return table\[/ {
    print "        rust_profile_inc(18);"
    print
    next
}
/^[[:space:]]*&& width > 0[[:space:]]*$/ { pending_fast_repeat = 1 }
pending_fast_repeat && /^[[:space:]]*\{[[:space:]]*$/ {
    print
    print "                rust_profile_inc(13);"
    pending_fast_repeat = 0
    next
}
/^[[:space:]]*let limit = max\.unwrap_or_else/ {
    print "            rust_profile_inc(14);"
    print
    next
}
/^pub unsafe extern "C" fn rebar_compile\(/ { pending_export = 0 }
/^pub unsafe extern "C" fn rebar_match\(/ { pending_export = 1 }
/^pub unsafe extern "C" fn rebar_match_ascii\(/ { pending_export = 2 }
/^pub unsafe extern "C" fn rebar_collect_ascii\(/ { pending_export = 3 }
pending_export >= 0 && /^\) -> (\*mut Engine|i32|isize) \{/ {
    print
    printf "    rust_profile_inc(%d);\n", pending_export
    pending_export = -1
    next
}
/^fn run_match\(/ { pending_run = 1 }
/^fn run_match_legacy\(/ { pending_legacy = 1 }
pending_legacy && /^\) -> i32 \{/ {
    print
    print "    rust_profile_inc(47);"
    pending_legacy = 0
    next
}
pending_run && /^\) -> i32 \{/ {
    print
    print "    rust_profile_inc(4);"
    pending_run = 0
    next
}
/^[[:space:]]*for start in first_start\.\.=last_start \{/ {
    print
    print "        rust_profile_inc(5);"
    print "        rust_profile_inc(45);"
    next
}
/^[[:space:]]*&& starts\[context\.character\(start\) as usize\] == 0/ { pending_skip = 1 }
/^[[:space:]]*if first < 256 && starts\[first as usize\] == 0[[:space:]]*\{/ {
    pending_skip = 1
}
pending_skip && /^[[:space:]]*continue;[[:space:]]*$/ {
    print "            rust_profile_inc(6);"
    print "            rust_profile_inc(46);"
    print
    pending_skip = 0
    next
}
/^fn run_program\(/ { pending_vm_run = 1; vm_available = 1 }
pending_vm_run && /^\) -> Option<usize> \{/ {
    print
    print "    rust_profile_inc(24);"
    pending_vm_run = 0
    next
}
/^[[:space:]]*let instruction = program\.code\[pc\];[[:space:]]*$/ {
    print
    print "        rust_profile_inc(30);"
    next
}
/^[[:space:]]*Op::Literal => \{/ {
    print; print "                rust_profile_inc(42);"; next
}
/^[[:space:]]*Op::Category => \{/ {
    print; print "                rust_profile_inc(43);"; next
}
/^[[:space:]]*Op::Class => \{/ {
    print; print "                rust_profile_inc(41);"; next
}
/^[[:space:]]*Op::Anchor => \{/ {
    print; print "                rust_profile_inc(50);"; next
}
/^[[:space:]]*Op::Boundary => \{/ {
    print; print "                rust_profile_inc(49);"; next
}
/^[[:space:]]*Op::Split => \{/ {
    print; print "                rust_profile_inc(31);"; next
}
/^[[:space:]]*Op::Jump => \{/ {
    print; print "                rust_profile_inc(48);"; next
}
/^[[:space:]]*Op::Backref => \{/ {
    print; print "                rust_profile_inc(44);"; next
}
/^[[:space:]]*Op::Conditional => \{/ {
    print; print "                rust_profile_inc(53);"; next
}
/^[[:space:]]*Op::AtomicBegin => \{/ {
    print; print "                rust_profile_inc(51);"; next
}
/^[[:space:]]*Op::AtomicEnd => \{/ {
    print; print "                rust_profile_inc(52);"; next
}
/^[[:space:]]*Op::Look => \{/ {
    print; print "                rust_profile_inc(33);"; next
}
/^[[:space:]]*Op::Run => \{/ {
    print; print "                rust_profile_inc(32);"; next
}
/^[[:space:]]*Op::Accept => \{/ {
    print; print "                rust_profile_inc(40);"; next
}
/^[[:space:]]*choices\.push\(Choice \{/ {
    print "                rust_profile_inc(35);"
    print
    next
}
/^[[:space:]]*let Some\(choice\) = choices\.pop\(\) else \{/ {
    print "        rust_profile_inc(34);"
    print
    next
}
/^[[:space:]]*self\.overflow\.push\(value\);[[:space:]]*$/ {
    print "            rust_profile_inc(36);"
    print
    next
}
/^[[:space:]]*undo\.push\(CaptureUndo \{/ {
    print "    rust_profile_inc(37);"
    print
    next
}
/^[[:space:]]*undo\.push\(GuardUndo \{/ {
    print "    rust_profile_inc(38);"
    print
    next
}
/^[[:space:]]*let old_(begins|ends) = (begins|ends)\.to_vec\(\);[[:space:]]*$/ {
    print "                rust_profile_inc(39);"
    print
    next
}
/^[[:space:]]*vec!\[usize::MAX; program\.guards\][[:space:]]*$/ {
    print "        rust_profile_inc(55);"
    print
    next
}
/^[[:space:]]*if !\(begin\.\.begin \+ run\.width\)/ {
    print "                        rust_profile_inc(54);"
    print
    next
}
{ print }
END {
    if (!clone_helper || !eval_seen) {
        print "Rust engine architecture changed: update profiling anchors" > "/dev/stderr"
        exit 3
    }
}
' "$profile_dir/rust-source-snapshot.rs" > "$profile_dir/rust-instrumented.rs"

awk '
/^#include <stdint\.h>/ && !bridge_header {
    print
    print "static uint64_t rust_bridge_profile[32];"
    print "void rebar_rust_bridge_profile_reset(void) {"
    print "    for (size_t index = 0; index < 32; index++) rust_bridge_profile[index] = 0;"
    print "}"
    print "uint64_t rebar_rust_bridge_profile_get(size_t index) {"
    print "    return index < 32 ? rust_bridge_profile[index] : 0;"
    print "}"
    bridge_header = 1
    next
}
/^static PyObject \*bridge_compile\(/ {
    print; print "    rust_bridge_profile[12]++;"; next
}
/^static PyObject \*bridge_run\(/ {
    print; print "    rust_bridge_profile[0]++;"; run_seen = 1; next
}
/^static PyObject \*bridge_collect\(/ {
    print; print "    rust_bridge_profile[1]++;"; next
}
/^static PyObject \*bridge_findall\(/ {
    print; print "    rust_bridge_profile[2]++;"; next
}
/^static int rust_subject_open\(/ {
    print; print "    rust_bridge_profile[13]++;"; next
}
/^static int rust_subject_match\(/ {
    print
    print "    rust_bridge_profile[15]++;"
    print "    rust_bridge_profile[5] += (uint64_t)(subject->storage == NULL);"
    next
}
/^static PyObject \*rust_stream_collection\(/ {
    print
    print "    rust_bridge_profile[14]++;"
    print "    rust_bridge_profile[27] += (uint64_t)(subject->storage != NULL);"
    next
}
/^static PyObject \*bridge_pattern_match\(/ {
    print; print "    rust_bridge_profile[16]++;"; next
}
/^static PyObject \*bridge_bound_search\(/ {
    print; print "    rust_bridge_profile[17]++;"; next
}
/^static PyObject \*bridge_bound_match\(/ {
    print; print "    rust_bridge_profile[18]++;"; next
}
/^static PyObject \*bridge_bound_fullmatch\(/ {
    print; print "    rust_bridge_profile[19]++;"; next
}
/^static PyObject \*bridge_bound_findall\(/ {
    print; print "    rust_bridge_profile[20]++;"; next
}
/^static PyObject \*bridge_bound_literal_findall\(/ {
    print; print "    rust_bridge_profile[21]++;"; next
}
/^static int rust_index_arg\(/ {
    print; print "    rust_bridge_profile[24]++;"; next
}
/^[[:space:]]*int result = PyList_Append\(list, value\);[[:space:]]*$/ {
    print "    rust_bridge_profile[25]++;"
    print
    next
}
/^[[:space:]]*subject->storage = PyMem_Malloc\(subject->length \* \(sizeof\(uint32_t\)/ {
    print "        rust_bridge_profile[3]++;"
    print "        rust_bridge_profile[4] += subject->length;"
    print "        rust_bridge_profile[11]++;"
    print "        rust_bridge_profile[10] += (uint64_t)subject->length * (sizeof(uint32_t) * 2 + sizeof(uint8_t));"
    print
    next
}
/^[[:space:]]*storage = PyMem_Malloc\(length \* \(sizeof\(uint32_t\)/ {
    print "            rust_bridge_profile[3]++;"
    print "            rust_bridge_profile[4] += length;"
    print "            rust_bridge_profile[11]++;"
    print "            rust_bridge_profile[10] += (uint64_t)length * (sizeof(uint32_t) * 2 + sizeof(uint8_t));"
    print
    next
}
/^[[:space:]]*matched = rebar_match_ascii\(/ {
    print "        rust_bridge_profile[5]++;"
    print
    next
}
/^[[:space:]]*if \(!PyUnicode_IS_ASCII\(subject\)\) Py_RETURN_NONE;[[:space:]]*$/ {
    print "        if (!PyUnicode_IS_ASCII(subject)) {"
    print "            rust_bridge_profile[7]++;"
    print "            Py_RETURN_NONE;"
    print "        }"
    next
}
/^[[:space:]]*size_t capacity = range \* 2 \+ 1;[[:space:]]*$/ {
    print
    print "    rust_bridge_profile[9] += capacity;"
    next
}
/^[[:space:]]*intptr_t \*storage = PyMem_Malloc\(\(total \* 2 \+ capacity\)/ {
    print "    rust_bridge_profile[10] += (uint64_t)(total * 2 + capacity) * sizeof(intptr_t);"
    print "    rust_bridge_profile[11]++;"
    print
    next
}
/^[[:space:]]*intptr_t count = rebar_collect_ascii\(/ {
    print
    print "    if (count >= 0) rust_bridge_profile[8] += (uint64_t)count;"
    next
}
/^[[:space:]]*if \(found == 0\) break;[[:space:]]*$/ {
    print
    print "        rust_bridge_profile[8]++;"
    next
}
/^[[:space:]]*if \(stride > RUST_LOCAL_CAPTURE_WORDS\) \{[[:space:]]*$/ {
    print
    print "        rust_bridge_profile[29]++;"
    next
}
{ print }
END {
    if (!bridge_header || !run_seen) {
        print "Rust bridge architecture changed: update profiling anchors" > "/dev/stderr"
        exit 3
    }
}
' "$profile_dir/rust-bridge-snapshot.c" > "$profile_dir/rust-bridge-instrumented.c"

rustc --edition=2024 --crate-type cdylib --crate-name rebar_rust_profile_v6 \
    -C opt-level=3 -C lto=fat -C codegen-units=1 -C panic=abort \
    "$profile_dir/rust-instrumented.rs" -o "$package_dir/_rust_engine.so"

include_dir=$("$python_bin" -c 'import sysconfig; print(sysconfig.get_path("include"))')
extension_suffix=$("$python_bin" -c 'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX"))')
cc -std=c11 -O3 -fPIC -shared -Wall -Wextra -Werror "-I$include_dir" \
    "$profile_dir/rust-bridge-instrumented.c" -L"$package_dir" \
    -l:_rust_engine.so '-Wl,-rpath,$ORIGIN' \
    -o "$package_dir/_rust_bridge$extension_suffix"

printf 'profile_dir=%s\n' "$profile_dir"
if [ -n "$profile_revision" ]; then
    printf 'profile_revision=%s\n' "$profile_revision"
fi
printf 'production_source_sha256='
sha256sum "$profile_dir/rust-source-snapshot.rs" | awk '{print $1}'
printf 'production_bridge_sha256='
sha256sum "$profile_dir/rust-bridge-snapshot.c" | awk '{print $1}'
printf 'run with: PYTHONPATH=%s:%s %s %s/tools/rust_profile_v6.py --output /tmp/rebar-rust-v6-profile.json\n' \
    "$profile_dir" "$repo_dir" "$python_bin" "$repo_dir"
