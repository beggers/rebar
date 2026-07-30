//! Exact, dependency-free byte-start filters for the Rust regex engine.
//!
//! Prepare a `StartSet` once per compiled pattern. Its vector filters preserve
//! the complete 256-byte start table; they never approximate a character class.

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


const ANCHOR_SET_CAPACITY: usize = 8;
const ANCHOR_SAMPLE: usize = 64;

/// At one proven fixed offset, admit every byte in a complete necessary set.
#[derive(Clone, Copy)]
pub(crate) struct AnchorSet {
    offset: usize,
    bytes: [u8; ANCHOR_SET_CAPACITY],
    count: u8,
}

impl AnchorSet {
    #[inline]
    pub(crate) fn new(offset: usize, values: &[u8]) -> Option<Self> {
        if values.is_empty() || values.len() > ANCHOR_SET_CAPACITY {
            return None;
        }
        let mut result = Self { offset, bytes: [0; ANCHOR_SET_CAPACITY], count: 0 };
        for &value in values {
            if result.bytes[..usize::from(result.count)].contains(&value) {
                continue;
            }
            result.bytes[usize::from(result.count)] = value;
            result.count += 1;
        }
        Some(result)
    }

    #[inline(always)]
    fn admits(&self, value: u8) -> bool {
        self.bytes[..usize::from(self.count)].contains(&value)
    }
}

/// Candidate positions are only filtered; the ordered regex VM remains final.
#[derive(Clone)]
pub(crate) struct AnchorPlan {
    first: AnchorSet,
    second: Option<AnchorSet>,
    width: usize,
}

impl AnchorPlan {
    #[inline]
    pub(crate) fn new(first: AnchorSet, second: Option<AnchorSet>, width: usize) -> Option<Self> {
        if width == 0 || first.offset >= width
            || second.is_some_and(|value| value.offset >= width || value.offset == first.offset)
        {
            return None;
        }
        Some(Self { first, second, width })
    }

    /// Return the earliest necessary candidate within the exact Python window.
    #[inline]
    pub(crate) fn next(&self, haystack: &[u8], from: usize, end: usize) -> Option<usize> {
        let end = end.min(haystack.len());
        if from > end || self.width > end.saturating_sub(from) {
            return None;
        }
        let last = end - self.width;
        if self.first.admits(haystack[from + self.first.offset])
            && self.second.is_none_or(|other| other.admits(haystack[from + other.offset]))
        {
            return Some(from);
        }

        let mut primary = self.first;
        let mut secondary = self.second;
        let available = last - from + 1;
        if available >= ANCHOR_SAMPLE * 2
            && let Some(other) = secondary
        {
            let samples = ANCHOR_SAMPLE.min(available);
            let first_count = (0..samples)
                .filter(|&index| primary.admits(haystack[from + index + primary.offset]))
                .count();
            let other_count = (0..samples)
                .filter(|&index| other.admits(haystack[from + index + other.offset]))
                .count();
            if other_count < first_count {
                primary = other;
                secondary = Some(self.first);
            }
        }

        #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
        if available >= 32 && is_x86_feature_detected!("avx2") {
            // SAFETY: feature detection precedes the call, and every 32-lane
            // load fits entirely inside the bounded Python subject window.
            return unsafe { avx2_anchor_search(haystack, from, last, &primary, secondary) };
        }

        scalar_anchor_search(haystack, from, last, &primary, secondary)
    }
}

#[inline]
fn scalar_anchor_search(
    haystack: &[u8],
    from: usize,
    last: usize,
    primary: &AnchorSet,
    secondary: Option<AnchorSet>,
) -> Option<usize> {
    let mut cursor = from;
    while cursor <= last {
        let candidate = if primary.count == 1 {
            let stop = last + primary.offset + 1;
            next_singleton(haystack, primary.bytes[0], cursor + primary.offset, stop)?
                - primary.offset
        } else {
            let mut found = cursor;
            while found <= last && !primary.admits(haystack[found + primary.offset]) {
                found += 1;
            }
            if found > last {
                return None;
            }
            found
        };
        if secondary.is_none_or(|other| other.admits(haystack[candidate + other.offset])) {
            return Some(candidate);
        }
        cursor = candidate + 1;
    }
    None
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "avx2")]
unsafe fn avx2_anchor_membership(values: __m256i, allowed: &AnchorSet) -> __m256i {
    let mut accepted = _mm256_setzero_si256();
    for &value in &allowed.bytes[..usize::from(allowed.count)] {
        accepted = _mm256_or_si256(
            accepted,
            _mm256_cmpeq_epi8(values, _mm256_set1_epi8(value as i8)),
        );
    }
    accepted
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "avx2")]
unsafe fn avx2_anchor_search(
    haystack: &[u8],
    from: usize,
    last: usize,
    primary: &AnchorSet,
    secondary: Option<AnchorSet>,
) -> Option<usize> {
    let mut cursor = from;
    while last - cursor >= 31 {
        // SAFETY: cursor + 31 <= last and every anchor offset is below the
        // proven required width, so both unaligned loads stay in the window.
        let initial = unsafe {
            _mm256_loadu_si256(haystack.as_ptr().add(cursor + primary.offset).cast::<__m256i>())
        };
        // SAFETY: this function is called only after AVX2 feature detection.
        let mut accepted = unsafe { avx2_anchor_membership(initial, primary) };
        if _mm256_movemask_epi8(accepted) != 0
            && let Some(other) = secondary
        {
            // SAFETY: the second fixed offset has the same checked bounds.
            let following = unsafe {
                _mm256_loadu_si256(haystack.as_ptr().add(cursor + other.offset).cast::<__m256i>())
            };
            // SAFETY: AVX2 was authenticated before this function was entered.
            accepted = _mm256_and_si256(
                accepted,
                unsafe { avx2_anchor_membership(following, &other) },
            );
        }
        let matches = _mm256_movemask_epi8(accepted) as u32;
        if matches != 0 {
            return Some(cursor + matches.trailing_zeros() as usize);
        }
        cursor += 32;
        if cursor > last {
            return None;
        }
    }
    scalar_anchor_search(haystack, cursor, last, primary, secondary)
}

/// A compiled, exact representation of any subset of the 256 possible bytes.
#[derive(Clone)]
pub(crate) struct StartSet {
    table: [u8; 256],
    low_group: [u8; 16],
    high_group: [u8; 16],
    small: [u8; 8],
    count: u16,
}

impl StartSet {
    /// Prepare shuffle tables once, outside the subject-searching hot path.
    #[inline]
    pub(crate) fn new(table: &[u8; 256]) -> Self {
        let mut result = Self {
            table: *table,
            low_group: [0; 16],
            high_group: [0; 16],
            small: [0; 8],
            count: 0,
        };
        for value in 0_u16..=255 {
            if table[usize::from(value)] == 0 {
                continue;
            }
            let byte = value as u8;
            if result.count < result.small.len() as u16 {
                result.small[result.count as usize] = byte;
            }
            result.count += 1;
            let high = usize::from(byte >> 4);
            let low = usize::from(byte & 15);
            if high < 8 {
                result.low_group[low] |= 1 << high;
            } else {
                result.high_group[low] |= 1 << (high - 8);
            }
        }
        result
    }

    /// Find the first admitted byte within `[from, min(end, haystack.len()))`.
    #[inline]
    pub(crate) fn next(&self, haystack: &[u8], from: usize, end: usize) -> Option<usize> {
        let end = end.min(haystack.len());
        if from >= end || self.count == 0 {
            return None;
        }
        if self.count == 256 || self.table[usize::from(haystack[from])] != 0 {
            return Some(from);
        }
        let window = &haystack[from..end];
        if self.count == 1 {
            return find_singleton(window, self.small[0]).map(|position| from + position);
        }

        #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
        {
            if window.len() >= 32 && is_x86_feature_detected!("avx2") {
                let result = if self.count <= 2 {
                    // SAFETY: feature detection precedes the AVX2 call; the
                    // implementation only performs fully bounded loads.
                    unsafe { avx2_small(window, self) }
                } else {
                    // SAFETY: feature detection precedes the AVX2 call; the
                    // implementation only performs fully bounded loads.
                    unsafe { avx2_table(window, self) }
                };
                return result.map(|position| from + position);
            }
            if window.len() >= 16 && is_x86_feature_detected!("ssse3") {
                // SAFETY: feature detection precedes the SSSE3 call; the
                // implementation only performs fully bounded loads.
                return unsafe { ssse3_table(window, self) }.map(|position| from + position);
            }
        }

        scalar_table(window, &self.table).map(|position| from + position)
    }
}

/// Convenient one-off start search. Cache `StartSet` for repeated engine calls.
#[allow(dead_code)]
#[inline]
pub(crate) fn next_start(
    table: &[u8; 256],
    haystack: &[u8],
    from: usize,
    end: usize,
) -> Option<usize> {
    let end = end.min(haystack.len());
    if from >= end {
        return None;
    }
    let window = &haystack[from..end];
    if window.len() < 64 {
        return scalar_table(window, table).map(|position| from + position);
    }
    StartSet::new(table).next(haystack, from, end)
}

#[inline]
fn scalar_table(haystack: &[u8], table: &[u8; 256]) -> Option<usize> {
    haystack
        .iter()
        .position(|&byte| table[usize::from(byte)] != 0)
}

/// Find one exact byte within the safely clamped `[from, end)` window.
#[inline]
pub(crate) fn next_singleton(haystack: &[u8], byte: u8, from: usize, end: usize) -> Option<usize> {
    let end = end.min(haystack.len());
    if from >= end {
        return None;
    }
    find_singleton(&haystack[from..end], byte).and_then(|position| from.checked_add(position))
}

#[inline]
fn find_singleton(haystack: &[u8], byte: u8) -> Option<usize> {
    #[cfg(unix)]
    {
        // SAFETY: the pointer and length describe the complete live slice.
        // `memchr` does not write, and a non-null result lies within the slice.
        let found = unsafe {
            memchr(
                haystack.as_ptr().cast::<c_void>(),
                i32::from(byte),
                haystack.len(),
            )
        };
        if found.is_null() {
            None
        } else {
            // SAFETY: a successful `memchr` returns a pointer into haystack.
            Some(unsafe { found.cast::<u8>().offset_from(haystack.as_ptr()) } as usize)
        }
    }
    #[cfg(not(unix))]
    {
        haystack.iter().position(|&candidate| candidate == byte)
    }
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "ssse3")]
unsafe fn ssse3_table(haystack: &[u8], set: &StartSet) -> Option<usize> {
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

    scalar_table(&haystack[cursor..], &set.table).map(|position| cursor + position)
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "avx2")]
unsafe fn avx2_table(haystack: &[u8], set: &StartSet) -> Option<usize> {
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

    scalar_table(&haystack[cursor..], &set.table).map(|position| cursor + position)
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "avx2")]
unsafe fn avx2_small(haystack: &[u8], set: &StartSet) -> Option<usize> {
    let mut cursor = 0;
    while cursor + 32 <= haystack.len() {
        let bytes = unsafe { _mm256_loadu_si256(haystack.as_ptr().add(cursor).cast()) };
        let mut matches = _mm256_setzero_si256();
        for index in 0..set.count as usize {
            matches = _mm256_or_si256(
                matches,
                _mm256_cmpeq_epi8(bytes, _mm256_set1_epi8(set.small[index] as i8)),
            );
        }
        let found = _mm256_movemask_epi8(matches) as u32;
        if found != 0 {
            return Some(cursor + found.trailing_zeros() as usize);
        }
        cursor += 32;
    }

    scalar_table(&haystack[cursor..], &set.table).map(|position| cursor + position)
}

#[cfg(test)]
mod tests {
    use super::{StartSet, next_start};

    fn expected(table: &[u8; 256], haystack: &[u8], from: usize, end: usize) -> Option<usize> {
        let stop = end.min(haystack.len());
        if from >= stop {
            None
        } else {
            haystack[from..stop]
                .iter()
                .position(|&byte| table[usize::from(byte)] != 0)
                .map(|position| from + position)
        }
    }

    fn next_random(seed: &mut u64) -> u64 {
        *seed ^= *seed << 13;
        *seed ^= *seed >> 7;
        *seed ^= *seed << 17;
        *seed
    }

    #[test]
    fn empty_full_and_bounded_windows() {
        let empty = [0_u8; 256];
        let full = [1_u8; 256];
        let haystack = b"abc\x00\x7f\x80\xfe\xffxyz";
        for table in [&empty, &full] {
            let prepared = StartSet::new(table);
            for from in 0..=haystack.len() + 2 {
                for end in [0, 1, 3, haystack.len() - 1, haystack.len(), usize::MAX] {
                    let want = expected(table, haystack, from, end);
                    assert_eq!(prepared.next(haystack, from, end), want);
                    assert_eq!(next_start(table, haystack, from, end), want);
                }
            }
        }
    }

    #[test]
    fn every_singleton_and_high_bit_value() {
        let haystack = (0_u16..=255).map(|value| value as u8).collect::<Vec<_>>();
        for byte in 0_u16..=255 {
            let mut table = [0_u8; 256];
            table[usize::from(byte)] = if byte % 2 == 0 { 1 } else { 255 };
            let prepared = StartSet::new(&table);
            for (from, end) in [
                (0, 256),
                (0, byte as usize),
                (byte as usize, 256),
                ((byte as usize).saturating_add(1), 256),
                (0, usize::MAX),
            ] {
                let want = expected(&table, &haystack, from, end);
                assert_eq!(prepared.next(&haystack, from, end), want, "byte={byte}");
                assert_eq!(
                    next_start(&table, &haystack, from, end),
                    want,
                    "byte={byte}"
                );
            }
        }
    }

    #[test]
    fn arbitrary_classes_and_unaligned_vector_boundaries() {
        let mut seed = 0x5245_4241_525f_5336_u64;
        for case in 0..1_024 {
            let mut table = [0_u8; 256];
            for entry in &mut table {
                if next_random(&mut seed) & 15 == 0 {
                    *entry = (next_random(&mut seed) | 1) as u8;
                }
            }
            let length = (next_random(&mut seed) % 1_025) as usize;
            let mut haystack = vec![0_u8; length];
            for byte in &mut haystack {
                *byte = next_random(&mut seed) as u8;
            }
            let prepared = StartSet::new(&table);
            let starts = [
                0,
                1,
                15,
                16,
                17,
                31,
                32,
                33,
                63,
                64,
                65,
                length.saturating_sub(1),
                length,
                length.saturating_add(1),
                usize::MAX,
            ];
            let ends = [
                0,
                15,
                16,
                31,
                32,
                63,
                64,
                length / 2,
                length,
                length.saturating_add(1),
                usize::MAX,
            ];
            for from in starts {
                for end in ends {
                    let want = expected(&table, &haystack, from, end);
                    assert_eq!(
                        prepared.next(&haystack, from, end),
                        want,
                        "prepared case={case} from={from} end={end} len={length} seed={seed:#x}"
                    );
                    assert_eq!(
                        next_start(&table, &haystack, from, end),
                        want,
                        "one-off case={case} from={from} end={end} len={length} seed={seed:#x}"
                    );
                }
            }
        }
    }

    #[test]
    fn sparse_small_sets_retain_order_and_boundaries() {
        let candidates = [0, 1, 9, 10, 31, 32, 64, 127, 128, 129, 254, 255];
        let haystack = (0_u16..=255).map(|value| value as u8).collect::<Vec<_>>();
        for width in 1..=8 {
            let mut table = [0_u8; 256];
            for byte in candidates.iter().take(width) {
                table[*byte as usize] = 1;
            }
            let prepared = StartSet::new(&table);
            for from in 0..haystack.len() {
                for end in [from, from + 1, 16, 32, 64, 128, 255, 256, usize::MAX] {
                    let want = expected(&table, &haystack, from, end);
                    assert_eq!(prepared.next(&haystack, from, end), want);
                    assert_eq!(next_start(&table, &haystack, from, end), want);
                }
            }
        }
    }
}


#[cfg(test)]
mod anchor_position_tests {
    use super::{AnchorPlan, AnchorSet};

    fn expected(haystack: &[u8], from: usize, end: usize, width: usize,
                first: (usize, &[u8]), second: Option<(usize, &[u8])>) -> Option<usize> {
        let end = end.min(haystack.len());
        if from > end || width > end.saturating_sub(from) {
            return None;
        }
        (from..=end - width).find(|&position| {
            first.1.contains(&haystack[position + first.0])
                && second.is_none_or(|other| other.1.contains(&haystack[position + other.0]))
        })
    }

    fn random(seed: &mut u64) -> u64 {
        *seed ^= *seed << 13;
        *seed ^= *seed >> 7;
        *seed ^= *seed << 17;
        *seed
    }

    #[test]
    fn exact_bounds_high_bytes_and_vector_edges() {
        let mut seed = 0x5245_4241_525f_4131_u64;
        for _case in 0..768 {
            let length = (random(&mut seed) % 193) as usize;
            let mut arena = vec![0_u8; length + 1];
            for byte in &mut arena {
                *byte = random(&mut seed) as u8;
            }
            let haystack = &arena[1..];
            let width = (random(&mut seed) % 16 + 1) as usize;
            let first_offset = (random(&mut seed) as usize) % width;
            let second_offset = (random(&mut seed) as usize) % width;
            let first_bytes = [0, 0x80, 0xff, random(&mut seed) as u8];
            let second_bytes = [b'A', b'B', random(&mut seed) as u8];
            let first = AnchorSet::new(first_offset, &first_bytes).unwrap();
            let second = (second_offset != first_offset)
                .then(|| AnchorSet::new(second_offset, &second_bytes).unwrap());
            let plan = AnchorPlan::new(first, second, width).unwrap();
            for from in [0, 1, 15, 16, 31, 32, 63, 64, length,
                         length.saturating_add(1), usize::MAX] {
                for end in [0, 1, 15, 16, 31, 32, 63, 64, length, usize::MAX] {
                    let want = expected(
                        haystack, from, end, width, (first_offset, &first_bytes),
                        (second_offset != first_offset)
                            .then_some((second_offset, &second_bytes)),
                    );
                    assert_eq!(plan.next(haystack, from, end), want);
                }
            }
        }
    }

    #[test]
    fn opposite_anchor_density_and_overlaps_preserve_leftmost_order() {
        let first = AnchorSet::new(0, b"a").unwrap();
        let last = AnchorSet::new(5, b"b").unwrap();
        let plan = AnchorPlan::new(first, Some(last), 6).unwrap();
        let mut dense = vec![b'a'; 2048];
        dense.push(b'b');
        assert_eq!(plan.next(&dense, 0, dense.len()), Some(2043));

        let first = AnchorSet::new(0, b"b").unwrap();
        let last = AnchorSet::new(5, b"a").unwrap();
        let plan = AnchorPlan::new(first, Some(last), 6).unwrap();
        let mut sparse = vec![b'b', b'd'];
        sparse.extend(std::iter::repeat_n(b'a', 2048));
        assert_eq!(plan.next(&sparse, 0, sparse.len()), None);
        assert_eq!(plan.next(b"bbcaaaa", 0, 7), Some(1));
    }
}
