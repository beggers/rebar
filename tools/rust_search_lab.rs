//! Dependency-free, deterministic literal and first-byte search experiments.
//!
//! Build: rustc --edition=2024 -C opt-level=3 -C lto=fat \
//!   -C codegen-units=1 -C panic=abort -D warnings \
//!   tools/rust_search_lab.rs -o /tmp/rebar-rust-search-lab
//! Run: taskset -c 15 /tmp/rebar-rust-search-lab

use std::ffi::c_void;
use std::hint::black_box;
use std::time::Instant;

#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

unsafe extern "C" {
    fn memchr(pointer: *const c_void, byte: i32, length: usize) -> *mut c_void;
    fn memmem(
        haystack: *const c_void,
        haystack_length: usize,
        needle: *const c_void,
        needle_length: usize,
    ) -> *mut c_void;
}

type LiteralSearch = fn(&[u8], &[u8]) -> Option<usize>;
type ClassSearch = fn(&[u8], &ByteSet) -> Option<usize>;

#[derive(Clone)]
struct ByteSet {
    table: [u8; 256],
    low_group: [u8; 16],
    high_group: [u8; 16],
}

impl ByteSet {
    fn from_test(test: impl Fn(u8) -> bool) -> Self {
        let mut result = Self {
            table: [0; 256],
            low_group: [0; 16],
            high_group: [0; 16],
        };
        for value in 0_u16..=255 {
            let byte = value as u8;
            if test(byte) {
                result.table[value as usize] = 1;
                let high = usize::from(byte >> 4);
                let low = usize::from(byte & 15);
                if high < 8 {
                    result.low_group[low] |= 1 << high;
                } else {
                    result.high_group[low] |= 1 << (high - 8);
                }
            }
        }
        result
    }
}

#[inline(never)]
fn scalar_windows(haystack: &[u8], needle: &[u8]) -> Option<usize> {
    if needle.is_empty() {
        return Some(0);
    }
    haystack.windows(needle.len()).position(|window| window == needle)
}

#[inline(never)]
fn scalar_first(haystack: &[u8], needle: &[u8]) -> Option<usize> {
    if needle.is_empty() {
        return Some(0);
    }
    if needle.len() > haystack.len() {
        return None;
    }
    let limit = haystack.len() - needle.len() + 1;
    (0..limit).find(|&position| {
        haystack[position] == needle[0]
            && &haystack[position..position + needle.len()] == needle
    })
}

#[inline(never)]
fn libc_memchr_search(haystack: &[u8], needle: &[u8]) -> Option<usize> {
    if needle.is_empty() {
        return Some(0);
    }
    if needle.len() > haystack.len() {
        return None;
    }
    let limit = haystack.len() - needle.len() + 1;
    let mut cursor = 0;
    while cursor < limit {
        let found = unsafe {
            memchr(
                haystack.as_ptr().add(cursor).cast::<c_void>(),
                i32::from(needle[0]),
                limit - cursor,
            )
        };
        if found.is_null() {
            return None;
        }
        let at = (found as usize) - (haystack.as_ptr() as usize);
        if &haystack[at..at + needle.len()] == needle {
            return Some(at);
        }
        cursor = at + 1;
    }
    None
}

#[inline(never)]
fn libc_memmem_search(haystack: &[u8], needle: &[u8]) -> Option<usize> {
    if needle.is_empty() {
        return Some(0);
    }
    if needle.len() > haystack.len() {
        return None;
    }
    let found = unsafe {
        memmem(
            haystack.as_ptr().cast::<c_void>(),
            haystack.len(),
            needle.as_ptr().cast::<c_void>(),
            needle.len(),
        )
    };
    if found.is_null() {
        None
    } else {
        Some((found as usize) - (haystack.as_ptr() as usize))
    }
}

#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "sse2")]
unsafe fn sse2_first_last_inner(haystack: &[u8], needle: &[u8]) -> Option<usize> {
    if needle.is_empty() {
        return Some(0);
    }
    if needle.len() > haystack.len() {
        return None;
    }
    let candidate_count = haystack.len() - needle.len() + 1;
    let first = _mm_set1_epi8(needle[0] as i8);
    let last = _mm_set1_epi8(needle[needle.len() - 1] as i8);
    let mut cursor = 0;
    while cursor + 16 <= candidate_count {
        let first_bytes = unsafe {
            _mm_loadu_si128(haystack.as_ptr().add(cursor).cast::<__m128i>())
        };
        let last_bytes = unsafe {
            _mm_loadu_si128(
                haystack
                    .as_ptr()
                    .add(cursor + needle.len() - 1)
                    .cast::<__m128i>(),
            )
        };
        let candidates = _mm_and_si128(
            _mm_cmpeq_epi8(first_bytes, first),
            _mm_cmpeq_epi8(last_bytes, last),
        );
        let mut bits = _mm_movemask_epi8(candidates) as u32;
        while bits != 0 {
            let at = cursor + bits.trailing_zeros() as usize;
            if &haystack[at..at + needle.len()] == needle {
                return Some(at);
            }
            bits &= bits - 1;
        }
        cursor += 16;
    }
    (cursor..candidate_count).find(|&at| {
        haystack[at] == needle[0]
            && haystack[at + needle.len() - 1] == needle[needle.len() - 1]
            && &haystack[at..at + needle.len()] == needle
    })
}

#[inline(never)]
fn sse2_first_last(haystack: &[u8], needle: &[u8]) -> Option<usize> {
    #[cfg(target_arch = "x86_64")]
    {
        // SSE2 is part of the x86-64 baseline.
        unsafe { sse2_first_last_inner(haystack, needle) }
    }
    #[cfg(not(target_arch = "x86_64"))]
    {
        scalar_first(haystack, needle)
    }
}

#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "avx2")]
unsafe fn avx2_first_last_inner(haystack: &[u8], needle: &[u8]) -> Option<usize> {
    if needle.is_empty() {
        return Some(0);
    }
    if needle.len() > haystack.len() {
        return None;
    }
    let candidate_count = haystack.len() - needle.len() + 1;
    let first = _mm256_set1_epi8(needle[0] as i8);
    let last = _mm256_set1_epi8(needle[needle.len() - 1] as i8);
    let mut cursor = 0;
    while cursor + 32 <= candidate_count {
        let first_bytes = unsafe {
            _mm256_loadu_si256(haystack.as_ptr().add(cursor).cast::<__m256i>())
        };
        let last_bytes = unsafe {
            _mm256_loadu_si256(
                haystack
                    .as_ptr()
                    .add(cursor + needle.len() - 1)
                    .cast::<__m256i>(),
            )
        };
        let candidates = _mm256_and_si256(
            _mm256_cmpeq_epi8(first_bytes, first),
            _mm256_cmpeq_epi8(last_bytes, last),
        );
        let mut bits = _mm256_movemask_epi8(candidates) as u32;
        while bits != 0 {
            let at = cursor + bits.trailing_zeros() as usize;
            if &haystack[at..at + needle.len()] == needle {
                return Some(at);
            }
            bits &= bits - 1;
        }
        cursor += 32;
    }
    (cursor..candidate_count).find(|&at| {
        haystack[at] == needle[0]
            && haystack[at + needle.len() - 1] == needle[needle.len() - 1]
            && &haystack[at..at + needle.len()] == needle
    })
}

#[inline(never)]
fn avx2_first_last(haystack: &[u8], needle: &[u8]) -> Option<usize> {
    #[cfg(target_arch = "x86_64")]
    {
        if is_x86_feature_detected!("avx2") {
            return unsafe { avx2_first_last_inner(haystack, needle) };
        }
    }
    sse2_first_last(haystack, needle)
}

#[inline(never)]
fn scalar_table(haystack: &[u8], set: &ByteSet) -> Option<usize> {
    (0..haystack.len()).find(|&at| set.table[usize::from(haystack[at])] != 0)
}

#[inline(never)]
fn iterator_table(haystack: &[u8], set: &ByteSet) -> Option<usize> {
    haystack
        .iter()
        .position(|&byte| set.table[usize::from(byte)] != 0)
}

#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "ssse3")]
unsafe fn ssse3_table_inner(haystack: &[u8], set: &ByteSet) -> Option<usize> {
    let low_table = unsafe { _mm_loadu_si128(set.low_group.as_ptr().cast::<__m128i>()) };
    let high_table = unsafe { _mm_loadu_si128(set.high_group.as_ptr().cast::<__m128i>()) };
    let bit_values: [u8; 16] = [1, 2, 4, 8, 16, 32, 64, 128, 1, 2, 4, 8, 16, 32, 64, 128];
    let bit_table = unsafe { _mm_loadu_si128(bit_values.as_ptr().cast::<__m128i>()) };
    let nibble = _mm_set1_epi8(15);
    let seven = _mm_set1_epi8(7);
    let zero = _mm_setzero_si128();
    let mut cursor = 0;
    while cursor + 16 <= haystack.len() {
        let bytes = unsafe { _mm_loadu_si128(haystack.as_ptr().add(cursor).cast()) };
        let lows = _mm_and_si128(bytes, nibble);
        let highs = _mm_and_si128(_mm_srli_epi16(bytes, 4), nibble);
        let low_members = _mm_shuffle_epi8(low_table, lows);
        let high_members = _mm_shuffle_epi8(high_table, lows);
        let high_select = _mm_cmpgt_epi8(highs, seven);
        let members = _mm_or_si128(
            _mm_andnot_si128(high_select, low_members),
            _mm_and_si128(high_select, high_members),
        );
        let bits = _mm_shuffle_epi8(bit_table, highs);
        let matches = _mm_and_si128(members, bits);
        let nonmatches = _mm_movemask_epi8(_mm_cmpeq_epi8(matches, zero)) as u32;
        let found = (!nonmatches) & 0xffff;
        if found != 0 {
            return Some(cursor + found.trailing_zeros() as usize);
        }
        cursor += 16;
    }
    (cursor..haystack.len()).find(|&at| set.table[usize::from(haystack[at])] != 0)
}

#[inline(never)]
fn ssse3_table(haystack: &[u8], set: &ByteSet) -> Option<usize> {
    #[cfg(target_arch = "x86_64")]
    {
        if is_x86_feature_detected!("ssse3") {
            return unsafe { ssse3_table_inner(haystack, set) };
        }
    }
    scalar_table(haystack, set)
}

#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "avx2")]
unsafe fn avx2_table_inner(haystack: &[u8], set: &ByteSet) -> Option<usize> {
    let low128 = unsafe { _mm_loadu_si128(set.low_group.as_ptr().cast::<__m128i>()) };
    let high128 = unsafe { _mm_loadu_si128(set.high_group.as_ptr().cast::<__m128i>()) };
    let bit_values: [u8; 16] = [1, 2, 4, 8, 16, 32, 64, 128, 1, 2, 4, 8, 16, 32, 64, 128];
    let bits128 = unsafe { _mm_loadu_si128(bit_values.as_ptr().cast::<__m128i>()) };
    let low_table = _mm256_broadcastsi128_si256(low128);
    let high_table = _mm256_broadcastsi128_si256(high128);
    let bit_table = _mm256_broadcastsi128_si256(bits128);
    let nibble = _mm256_set1_epi8(15);
    let seven = _mm256_set1_epi8(7);
    let zero = _mm256_setzero_si256();
    let mut cursor = 0;
    while cursor + 32 <= haystack.len() {
        let bytes = unsafe { _mm256_loadu_si256(haystack.as_ptr().add(cursor).cast()) };
        let lows = _mm256_and_si256(bytes, nibble);
        let highs = _mm256_and_si256(_mm256_srli_epi16(bytes, 4), nibble);
        let low_members = _mm256_shuffle_epi8(low_table, lows);
        let high_members = _mm256_shuffle_epi8(high_table, lows);
        let high_select = _mm256_cmpgt_epi8(highs, seven);
        let members = _mm256_blendv_epi8(low_members, high_members, high_select);
        let bits = _mm256_shuffle_epi8(bit_table, highs);
        let matches = _mm256_and_si256(members, bits);
        let nonmatches = _mm256_movemask_epi8(_mm256_cmpeq_epi8(matches, zero)) as u32;
        let found = !nonmatches;
        if found != 0 {
            return Some(cursor + found.trailing_zeros() as usize);
        }
        cursor += 32;
    }
    (cursor..haystack.len()).find(|&at| set.table[usize::from(haystack[at])] != 0)
}

#[inline(never)]
fn avx2_table(haystack: &[u8], set: &ByteSet) -> Option<usize> {
    #[cfg(target_arch = "x86_64")]
    {
        if is_x86_feature_detected!("avx2") {
            return unsafe { avx2_table_inner(haystack, set) };
        }
    }
    ssse3_table(haystack, set)
}

fn next_random(seed: &mut u64) -> u64 {
    *seed ^= *seed << 13;
    *seed ^= *seed >> 7;
    *seed ^= *seed << 17;
    *seed
}

fn validate() {
    let literal_searches: [(&str, LiteralSearch); 5] = [
        ("scalar-windows", scalar_windows),
        ("scalar-first", scalar_first),
        ("libc-memchr", libc_memchr_search),
        ("libc-memmem", libc_memmem_search),
        ("avx2-first-last", avx2_first_last),
    ];
    let class_searches: [(&str, ClassSearch); 4] = [
        ("scalar-table", scalar_table),
        ("iterator-table", iterator_table),
        ("ssse3-table", ssse3_table),
        ("avx2-table", avx2_table),
    ];
    let mut seed = 0x5245_4241_525f_5336_u64;
    let mut literal_checks = 0_u64;
    let mut bitmap_checks = 0_u64;
    for _ in 0..512 {
        let length = (next_random(&mut seed) % 768) as usize;
        let mut haystack = vec![0_u8; length];
        for byte in &mut haystack {
            *byte = next_random(&mut seed) as u8;
        }
        for needle_length in [0, 1, 2, 3, 7, 15, 16, 17, 31, 32, 33, 63] {
            let mut needle = vec![0_u8; needle_length];
            for byte in &mut needle {
                *byte = next_random(&mut seed) as u8;
            }
            if needle_length != 0
                && needle_length <= haystack.len()
                && next_random(&mut seed) & 1 != 0
            {
                let start = (next_random(&mut seed) as usize)
                    % (haystack.len() - needle_length + 1);
                needle.copy_from_slice(&haystack[start..start + needle_length]);
            }
            let expected = scalar_windows(&haystack, &needle);
            for (name, search) in literal_searches {
                let found = search(&haystack, &needle);
                assert_eq!(
                    found, expected,
                    "literal {name}: haystack={} needle={} seed={seed:#x}",
                    haystack.len(),
                    needle.len()
                );
                literal_checks += 1;
            }
        }
        let mut selected = [false; 256];
        for value in &mut selected {
            *value = next_random(&mut seed) & 15 == 0;
        }
        let set = ByteSet::from_test(|byte| selected[usize::from(byte)]);
        let expected = scalar_table(&haystack, &set);
        for (name, search) in class_searches {
            let found = search(&haystack, &set);
            assert_eq!(
                found, expected,
                "bitmap {name}: haystack={} seed={seed:#x}",
                haystack.len()
            );
            bitmap_checks += 1;
        }
        for byte in 0_u16..=255 {
            let singleton = [byte as u8];
            let expected = if selected[byte as usize] {
                Some(0)
            } else {
                None
            };
            for (name, search) in class_searches {
                assert_eq!(search(&singleton, &set), expected, "single {name}");
                bitmap_checks += 1;
            }
        }
    }
    println!(
        "{{\"type\":\"correctness\",\"seed\":\"0x52454241525f5336\",\"literal_checks\":{literal_checks},\"bitmap_checks\":{bitmap_checks},\"avx2\":{},\"ssse3\":{}}}",
        is_x86_feature_detected!("avx2"),
        is_x86_feature_detected!("ssse3"),
    );
}

fn measure_literal(search: LiteralSearch, haystack: &[u8], needle: &[u8]) -> f64 {
    let iterations = (2_097_152 / haystack.len().max(1)).clamp(8, 20_000);
    let mut trials = [0_u128; 5];
    for trial in &mut trials {
        let started = Instant::now();
        for _ in 0..iterations {
            black_box(search(black_box(haystack), black_box(needle)));
        }
        *trial = started.elapsed().as_nanos();
    }
    trials.sort_unstable();
    trials[2] as f64 / iterations as f64
}

fn measure_class(search: ClassSearch, haystack: &[u8], set: &ByteSet) -> f64 {
    let iterations = (2_097_152 / haystack.len().max(1)).clamp(8, 20_000);
    let mut trials = [0_u128; 5];
    for trial in &mut trials {
        let started = Instant::now();
        for _ in 0..iterations {
            black_box(search(black_box(haystack), black_box(set)));
        }
        *trial = started.elapsed().as_nanos();
    }
    trials.sort_unstable();
    trials[2] as f64 / iterations as f64
}

fn benchmark_literals() {
    let searches: [(&str, LiteralSearch); 5] = [
        ("scalar-windows", scalar_windows),
        ("scalar-first", scalar_first),
        ("libc-memchr", libc_memchr_search),
        ("libc-memmem", libc_memmem_search),
        ("avx2-first-last", avx2_first_last),
    ];
    for length in [64, 256, 1024, 4096, 16_384, 65_536, 262_144] {
        for needle_length in [1, 4, 12, 32] {
            if needle_length > length {
                continue;
            }
            for scenario in ["miss-distinct", "late-hit", "miss-common-first"] {
                let mut needle = (0..needle_length)
                    .map(|offset| b'A' + ((offset * 7 + 3) % 25) as u8)
                    .collect::<Vec<_>>();
                if needle_length == 1 && scenario == "miss-common-first" {
                    continue;
                }
                let fill = if scenario == "miss-common-first" {
                    needle[0]
                } else {
                    b'q'
                };
                if fill == b'q' && needle[0] == b'q' {
                    needle[0] = b'~';
                }
                let mut haystack = vec![fill; length];
                if scenario == "late-hit" {
                    haystack[length - needle_length..].copy_from_slice(&needle);
                }
                let expected = scalar_windows(&haystack, &needle);
                let baseline = measure_literal(scalar_windows, &haystack, &needle);
                for (name, search) in searches {
                    assert_eq!(search(&haystack, &needle), expected);
                    let elapsed = if name == "scalar-windows" {
                        baseline
                    } else {
                        measure_literal(search, &haystack, &needle)
                    };
                    println!(
                        "{{\"type\":\"literal\",\"scenario\":\"{scenario}\",\"haystack\":{length},\"needle\":{needle_length},\"algorithm\":\"{name}\",\"median_ns\":{elapsed:.3},\"vs_scalar\":{:.6}}}",
                        baseline / elapsed.max(f64::MIN_POSITIVE)
                    );
                }
            }
        }
    }
}

fn benchmark_classes() {
    let searches: [(&str, ClassSearch); 4] = [
        ("scalar-table", scalar_table),
        ("iterator-table", iterator_table),
        ("ssse3-table", ssse3_table),
        ("avx2-table", avx2_table),
    ];
    let names = ["digit", "word", "newline", "punctuation", "sparse"];
    for length in [64, 256, 1024, 4096, 16_384, 65_536, 262_144] {
        for name in names {
            let set = ByteSet::from_test(|byte| match name {
                "digit" => byte.is_ascii_digit(),
                "word" => byte.is_ascii_alphanumeric() || byte == b'_',
                "newline" => byte == b'\n',
                "punctuation" => matches!(byte, b'@' | b'/' | b'=' | b':' | b';'),
                "sparse" => matches!(byte, 0 | 0x1b | 0x80 | 0xfe | 0xff),
                _ => unreachable!(),
            });
            for scenario in ["miss", "late-hit"] {
                let fill = if name == "word" { b'-' } else { b'a' };
                let mut haystack = vec![fill; length];
                if scenario == "late-hit" {
                    haystack[length - 1] = match name {
                        "digit" => b'7',
                        "word" => b'z',
                        "newline" => b'\n',
                        "punctuation" => b'@',
                        "sparse" => 0xfe,
                        _ => unreachable!(),
                    };
                }
                let expected = scalar_table(&haystack, &set);
                let baseline = measure_class(scalar_table, &haystack, &set);
                for (algorithm, search) in searches {
                    assert_eq!(search(&haystack, &set), expected);
                    let elapsed = if algorithm == "scalar-table" {
                        baseline
                    } else {
                        measure_class(search, &haystack, &set)
                    };
                    println!(
                        "{{\"type\":\"class\",\"class\":\"{name}\",\"scenario\":\"{scenario}\",\"haystack\":{length},\"algorithm\":\"{algorithm}\",\"median_ns\":{elapsed:.3},\"vs_scalar\":{:.6}}}",
                        baseline / elapsed.max(f64::MIN_POSITIVE)
                    );
                }
            }
        }
    }
}

fn main() {
    validate();
    benchmark_literals();
    benchmark_classes();
}
