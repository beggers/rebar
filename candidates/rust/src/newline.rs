//! Exact bounded newline scans for CPython's native Unicode storage.
//!
//! Positions and window bounds are always character indexes, even for
//! unaligned two-byte and four-byte source data.

#[cfg(unix)]
use std::ffi::c_void;

#[cfg(target_arch = "x86")]
use std::arch::x86::*;
#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

#[cfg(unix)]
unsafe extern "C" {
    fn memchr(pointer: *const c_void, byte: i32, length: usize) -> *mut c_void;
}

/// Return the next U+000A in `[from, min(end, character_count))`.
///
/// `kind` is CPython's native Unicode width: one, two, or four bytes.
/// Invalid kinds, empty windows, and incomplete trailing units return `None`.
#[inline]
pub(crate) fn next_newline(data: &[u8], kind: u8, from: usize, end: usize) -> Option<usize> {
    let width = match kind {
        1 => 1,
        2 => 2,
        4 => 4,
        _ => return None,
    };
    let end = end.min(data.len() / width);
    if from >= end {
        return None;
    }

    match kind {
        1 => next_byte(data, from, end),
        2 => next_half(data, from, end),
        4 => next_wide(data, from, end),
        _ => unreachable!("the Unicode kind was validated"),
    }
}

/// Prepared UTF-32 compatibility for the original character-slice boundary.
#[allow(dead_code)]
#[inline]
pub(crate) fn next_newline_chars(chars: &[u32], from: usize, end: usize) -> Option<usize> {
    let bytes = unsafe {
        // SAFETY: u32 has no padding, chars stays alive for the entire call,
        // and every valid Rust slice fits the addressable byte range.
        std::slice::from_raw_parts(chars.as_ptr().cast::<u8>(), std::mem::size_of_val(chars))
    };
    next_newline(bytes, 4, from, end)
}

#[inline]
fn next_byte(data: &[u8], from: usize, end: usize) -> Option<usize> {
    #[cfg(unix)]
    {
        // SAFETY: from..end is a checked, nonempty region in `data`; memchr
        // never writes and returns either null or a pointer into that region.
        let found = unsafe {
            memchr(
                data.as_ptr().add(from).cast::<c_void>(),
                i32::from(b'\n'),
                end - from,
            )
        };
        if found.is_null() {
            None
        } else {
            // SAFETY: a successful memchr points into the original slice.
            Some(unsafe { found.cast::<u8>().offset_from(data.as_ptr()) } as usize)
        }
    }
    #[cfg(not(unix))]
    {
        data[from..end]
            .iter()
            .position(|&byte| byte == b'\n')
            .map(|position| from + position)
    }
}

#[inline]
fn half_at(data: &[u8], position: usize) -> u16 {
    let offset = position * 2;
    u16::from_ne_bytes([data[offset], data[offset + 1]])
}

#[inline]
fn wide_at(data: &[u8], position: usize) -> u32 {
    let offset = position * 4;
    u32::from_ne_bytes([
        data[offset],
        data[offset + 1],
        data[offset + 2],
        data[offset + 3],
    ])
}

#[inline]
fn scalar_half(data: &[u8], from: usize, end: usize) -> Option<usize> {
    (from..end).find(|&position| half_at(data, position) == u16::from(b'\n'))
}

#[inline]
fn scalar_wide(data: &[u8], from: usize, end: usize) -> Option<usize> {
    (from..end).find(|&position| wide_at(data, position) == u32::from(b'\n'))
}

#[inline]
fn next_half(data: &[u8], from: usize, end: usize) -> Option<usize> {
    if half_at(data, from) == u16::from(b'\n') {
        return Some(from);
    }

    #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
    {
        if end - from >= 16 && is_x86_feature_detected!("avx2") {
            // SAFETY: runtime detection ensures AVX2, and the loop bounds
            // guarantee that each unaligned load is entirely inside `data`.
            return unsafe { avx2_half(data, from, end) };
        }
        if end - from >= 8 && is_x86_feature_detected!("sse2") {
            // SAFETY: runtime detection ensures SSE2 and bounded loads.
            return unsafe { sse2_half(data, from, end) };
        }
    }

    scalar_half(data, from + 1, end)
}

#[inline]
fn next_wide(data: &[u8], from: usize, end: usize) -> Option<usize> {
    if wide_at(data, from) == u32::from(b'\n') {
        return Some(from);
    }

    #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
    {
        if end - from >= 8 && is_x86_feature_detected!("avx2") {
            // SAFETY: runtime detection ensures AVX2, and the loop bounds
            // guarantee that each unaligned load is entirely inside `data`.
            return unsafe { avx2_wide(data, from, end) };
        }
        if end - from >= 4 && is_x86_feature_detected!("sse2") {
            // SAFETY: runtime detection ensures SSE2 and bounded loads.
            return unsafe { sse2_wide(data, from, end) };
        }
    }

    scalar_wide(data, from + 1, end)
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "sse2")]
unsafe fn sse2_half(data: &[u8], from: usize, end: usize) -> Option<usize> {
    let newline = _mm_set1_epi16(i16::from(b'\n'));
    let mut cursor = from;
    while cursor + 8 <= end {
        let values = unsafe { _mm_loadu_si128(data.as_ptr().add(cursor * 2).cast()) };
        let matches = _mm_movemask_epi8(_mm_cmpeq_epi16(values, newline)) as u32;
        if matches != 0 {
            return Some(cursor + matches.trailing_zeros() as usize / 2);
        }
        cursor += 8;
    }
    scalar_half(data, cursor, end)
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "avx2")]
unsafe fn avx2_half(data: &[u8], from: usize, end: usize) -> Option<usize> {
    let newline = _mm256_set1_epi16(i16::from(b'\n'));
    let mut cursor = from;
    while cursor + 16 <= end {
        let values = unsafe { _mm256_loadu_si256(data.as_ptr().add(cursor * 2).cast()) };
        let matches = _mm256_movemask_epi8(_mm256_cmpeq_epi16(values, newline)) as u32;
        if matches != 0 {
            return Some(cursor + matches.trailing_zeros() as usize / 2);
        }
        cursor += 16;
    }
    scalar_half(data, cursor, end)
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "sse2")]
unsafe fn sse2_wide(data: &[u8], from: usize, end: usize) -> Option<usize> {
    let newline = _mm_set1_epi32(i32::from(b'\n'));
    let mut cursor = from;
    while cursor + 4 <= end {
        let values = unsafe { _mm_loadu_si128(data.as_ptr().add(cursor * 4).cast()) };
        let matches = _mm_movemask_ps(_mm_castsi128_ps(_mm_cmpeq_epi32(values, newline))) as u32;
        if matches != 0 {
            return Some(cursor + matches.trailing_zeros() as usize);
        }
        cursor += 4;
    }
    scalar_wide(data, cursor, end)
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "avx2")]
unsafe fn avx2_wide(data: &[u8], from: usize, end: usize) -> Option<usize> {
    let newline = _mm256_set1_epi32(i32::from(b'\n'));
    let mut cursor = from;
    while cursor + 8 <= end {
        let values = unsafe { _mm256_loadu_si256(data.as_ptr().add(cursor * 4).cast()) };
        let matches =
            _mm256_movemask_ps(_mm256_castsi256_ps(_mm256_cmpeq_epi32(values, newline))) as u32;
        if matches != 0 {
            return Some(cursor + matches.trailing_zeros() as usize);
        }
        cursor += 8;
    }
    scalar_wide(data, cursor, end)
}

#[cfg(test)]
mod tests {
    use super::{next_newline, next_newline_chars};

    fn encode(values: &[u32], kind: u8) -> Vec<u8> {
        let mut result = Vec::with_capacity(values.len() * usize::from(kind));
        for &value in values {
            match kind {
                1 => result.push(value as u8),
                2 => result.extend_from_slice(&(value as u16).to_ne_bytes()),
                4 => result.extend_from_slice(&value.to_ne_bytes()),
                _ => unreachable!("test kinds are valid"),
            }
        }
        result
    }

    fn reference(values: &[u32], kind: u8, from: usize, end: usize) -> Option<usize> {
        let stop = end.min(values.len());
        if from >= stop {
            return None;
        }
        values[from..stop]
            .iter()
            .position(|&value| match kind {
                1 => value as u8 == b'\n',
                2 => value as u16 == u16::from(b'\n'),
                4 => value == u32::from(b'\n'),
                _ => false,
            })
            .map(|index| from + index)
    }

    fn next_random(seed: &mut u64) -> u64 {
        *seed ^= *seed << 13;
        *seed ^= *seed >> 7;
        *seed ^= *seed << 17;
        *seed
    }

    #[test]
    fn invalid_kinds_and_empty_windows() {
        let data = b"abc\ndef";
        for kind in [0, 3, 5, 8, u8::MAX] {
            assert_eq!(next_newline(data, kind, 0, data.len()), None);
        }
        for kind in [1, 2, 4] {
            let encoded = encode(&[u32::from(b'a'), 10, u32::from(b'b')], kind);
            assert_eq!(next_newline(&encoded, kind, 0, 0), None);
            assert_eq!(next_newline(&encoded, kind, 3, 3), None);
            assert_eq!(next_newline(&encoded, kind, 4, usize::MAX), None);
            assert_eq!(next_newline(&encoded, kind, usize::MAX, usize::MAX), None);
        }
        assert_eq!(next_newline(&[], 1, 0, usize::MAX), None);
        assert_eq!(next_newline_chars(&[], 0, usize::MAX), None);
    }

    #[test]
    fn non_newline_high_bytes_never_match() {
        let values = [
            0x010a,
            0x0a00,
            0x0a0a,
            0x10_0a00,
            0x010a_0000,
            0x000a_0000,
            0x00ff_0a00,
        ];
        for kind in [2, 4] {
            let encoded = encode(&values, kind);
            assert_eq!(next_newline(&encoded, kind, 0, usize::MAX), None);
        }
        let mut with_newline = values.to_vec();
        with_newline.push(10);
        for kind in [2, 4] {
            let encoded = encode(&with_newline, kind);
            assert_eq!(
                next_newline(&encoded, kind, 0, usize::MAX),
                Some(values.len())
            );
        }
    }

    #[test]
    fn vector_boundaries_and_unaligned_storage() {
        for kind in [1, 2, 4] {
            for length in [0, 1, 3, 4, 7, 8, 15, 16, 17, 31, 32, 33, 63, 64, 65, 127] {
                for location in 0..=length {
                    let mut values = vec![u32::from(b'x'); length];
                    if location < length {
                        values[location] = 10;
                    }
                    let bytes = encode(&values, kind);
                    for padding in 0..4 {
                        let mut storage = vec![0xa5; padding];
                        storage.extend_from_slice(&bytes);
                        let unaligned = &storage[padding..];
                        for from in [0, 1, 3, 4, 7, 8, 15, 16, length, usize::MAX] {
                            for end in [0, 1, 7, 8, 15, 16, length, usize::MAX] {
                                assert_eq!(
                                    next_newline(unaligned, kind, from, end),
                                    reference(&values, kind, from, end),
                                    "kind={kind} length={length} newline={location} padding={padding} from={from} end={end}"
                                );
                            }
                        }
                    }
                }
            }
        }
    }

    #[test]
    fn arbitrary_unicode_and_bounded_windows() {
        let mut seed = 0x5245_4241_525f_4e36_u64;
        for case in 0..1_024 {
            let length = (next_random(&mut seed) % 769) as usize;
            let mut values = vec![0_u32; length];
            for value in &mut values {
                *value = match next_random(&mut seed) & 15 {
                    0 => 10,
                    1 => 0x010a,
                    2 => 0x0a00,
                    3 => 0x0a0a,
                    4 => 0x010a_0000,
                    _ => (next_random(&mut seed) % 0x11_0000) as u32,
                };
            }
            let starts = [
                0,
                1,
                3,
                4,
                7,
                8,
                15,
                16,
                31,
                32,
                63,
                64,
                length.saturating_sub(1),
                length,
                length.saturating_add(1),
                usize::MAX,
            ];
            let ends = [
                0,
                1,
                3,
                4,
                7,
                8,
                15,
                16,
                31,
                32,
                63,
                64,
                length,
                length.saturating_add(1),
                usize::MAX,
            ];
            for kind in [1, 2, 4] {
                let encoded = encode(&values, kind);
                for from in starts {
                    for end in ends {
                        let want = reference(&values, kind, from, end);
                        assert_eq!(
                            next_newline(&encoded, kind, from, end),
                            want,
                            "case={case} kind={kind} from={from} end={end} length={length} seed={seed:#x}"
                        );
                    }
                }
            }
            for from in starts {
                for end in ends {
                    assert_eq!(
                        next_newline_chars(&values, from, end),
                        reference(&values, 4, from, end)
                    );
                }
            }
        }
    }

    #[test]
    fn incomplete_units_are_never_read() {
        let complete_half = encode(&[u32::from(b'x'), 10], 2);
        let mut partial_half = complete_half;
        partial_half.extend_from_slice(&[10]);
        assert_eq!(next_newline(&partial_half, 2, 0, usize::MAX), Some(1));
        assert_eq!(next_newline(&partial_half, 2, 2, usize::MAX), None);

        let complete_wide = encode(&[u32::from(b'x'), 10], 4);
        for extra in 1..4 {
            let mut partial = complete_wide.clone();
            partial.extend(std::iter::repeat_n(10_u8, extra));
            assert_eq!(next_newline(&partial, 4, 0, usize::MAX), Some(1));
            assert_eq!(next_newline(&partial, 4, 2, usize::MAX), None);
        }
    }
}
