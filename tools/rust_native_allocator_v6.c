#define _GNU_SOURCE

#include <stddef.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdlib.h>

/*
 * Optional, independently loaded glibc allocation profiler. Compile into
 * /tmp and use LD_PRELOAD; never replace a production Rust shared object.
 * The __libc entry points prevent dlsym and dynamic-loader recursion.
 */
extern void *__libc_malloc(size_t);
extern void *__libc_calloc(size_t, size_t);
extern void *__libc_realloc(void *, size_t);
extern void __libc_free(void *);

struct rebar_rust_allocation_counters {
    _Atomic uint64_t malloc_calls;
    _Atomic uint64_t calloc_calls;
    _Atomic uint64_t realloc_calls;
    _Atomic uint64_t free_calls;
    _Atomic uint64_t malloc_bytes;
    _Atomic uint64_t calloc_bytes;
    _Atomic uint64_t realloc_bytes;
    _Atomic uint64_t failed_calls;
};

/*
 * Loader initialization can allocate dynamic thread-local storage. Using
 * thread-local counters in an interposed free() would recursively enter the
 * loader. Relaxed process-global atomics are safe and are sufficient for the
 * deliberately single-threaded, correctness-gated measurements.
 */
static struct rebar_rust_allocation_counters rebar_rust_counts;
static _Atomic unsigned rebar_rust_counting;

__attribute__((visibility("default")))
void rebar_rust_osprofile_begin(void) {
    atomic_store_explicit(&rebar_rust_counting, 0, memory_order_relaxed);
    atomic_store_explicit(&rebar_rust_counts.malloc_calls, 0, memory_order_relaxed);
    atomic_store_explicit(&rebar_rust_counts.calloc_calls, 0, memory_order_relaxed);
    atomic_store_explicit(&rebar_rust_counts.realloc_calls, 0, memory_order_relaxed);
    atomic_store_explicit(&rebar_rust_counts.free_calls, 0, memory_order_relaxed);
    atomic_store_explicit(&rebar_rust_counts.malloc_bytes, 0, memory_order_relaxed);
    atomic_store_explicit(&rebar_rust_counts.calloc_bytes, 0, memory_order_relaxed);
    atomic_store_explicit(&rebar_rust_counts.realloc_bytes, 0, memory_order_relaxed);
    atomic_store_explicit(&rebar_rust_counts.failed_calls, 0, memory_order_relaxed);
    atomic_store_explicit(&rebar_rust_counting, 1, memory_order_relaxed);
}

__attribute__((visibility("default")))
void rebar_rust_osprofile_end(void) {
    atomic_store_explicit(&rebar_rust_counting, 0, memory_order_relaxed);
}

__attribute__((visibility("default")))
void rebar_rust_osprofile_snapshot(uint64_t *output, size_t fields) {
    if (output == NULL) {
        return;
    }
    const uint64_t values[] = {
        atomic_load_explicit(&rebar_rust_counts.malloc_calls, memory_order_relaxed),
        atomic_load_explicit(&rebar_rust_counts.calloc_calls, memory_order_relaxed),
        atomic_load_explicit(&rebar_rust_counts.realloc_calls, memory_order_relaxed),
        atomic_load_explicit(&rebar_rust_counts.free_calls, memory_order_relaxed),
        atomic_load_explicit(&rebar_rust_counts.malloc_bytes, memory_order_relaxed),
        atomic_load_explicit(&rebar_rust_counts.calloc_bytes, memory_order_relaxed),
        atomic_load_explicit(&rebar_rust_counts.realloc_bytes, memory_order_relaxed),
        atomic_load_explicit(&rebar_rust_counts.failed_calls, memory_order_relaxed),
    };
    const size_t available = sizeof(values) / sizeof(values[0]);
    const size_t count = fields < available ? fields : available;
    for (size_t index = 0; index < count; index++) {
        output[index] = values[index];
    }
}

__attribute__((visibility("default")))
void *malloc(size_t size) {
    void *result = __libc_malloc(size);
    if (atomic_load_explicit(&rebar_rust_counting, memory_order_relaxed)) {
        atomic_fetch_add_explicit(&rebar_rust_counts.malloc_calls, 1, memory_order_relaxed);
        atomic_fetch_add_explicit(&rebar_rust_counts.malloc_bytes, size, memory_order_relaxed);
        if (result == NULL && size != 0) {
            atomic_fetch_add_explicit(&rebar_rust_counts.failed_calls, 1, memory_order_relaxed);
        }
    }
    return result;
}

__attribute__((visibility("default")))
void *calloc(size_t number, size_t size) {
    void *result = __libc_calloc(number, size);
    if (atomic_load_explicit(&rebar_rust_counting, memory_order_relaxed)) {
        atomic_fetch_add_explicit(&rebar_rust_counts.calloc_calls, 1, memory_order_relaxed);
        if (number != 0 && size > SIZE_MAX / number) {
            atomic_store_explicit(
                &rebar_rust_counts.calloc_bytes, UINT64_MAX, memory_order_relaxed
            );
        } else {
            atomic_fetch_add_explicit(
                &rebar_rust_counts.calloc_bytes, number * size, memory_order_relaxed
            );
        }
        if (result == NULL && number != 0 && size != 0) {
            atomic_fetch_add_explicit(&rebar_rust_counts.failed_calls, 1, memory_order_relaxed);
        }
    }
    return result;
}

__attribute__((visibility("default")))
void *realloc(void *pointer, size_t size) {
    void *result = __libc_realloc(pointer, size);
    if (atomic_load_explicit(&rebar_rust_counting, memory_order_relaxed)) {
        atomic_fetch_add_explicit(&rebar_rust_counts.realloc_calls, 1, memory_order_relaxed);
        atomic_fetch_add_explicit(&rebar_rust_counts.realloc_bytes, size, memory_order_relaxed);
        if (result == NULL && size != 0) {
            atomic_fetch_add_explicit(&rebar_rust_counts.failed_calls, 1, memory_order_relaxed);
        }
    }
    return result;
}

__attribute__((visibility("default")))
void free(void *pointer) {
    if (pointer != NULL && atomic_load_explicit(&rebar_rust_counting, memory_order_relaxed)) {
        atomic_fetch_add_explicit(&rebar_rust_counts.free_calls, 1, memory_order_relaxed);
    }
    __libc_free(pointer);
}
