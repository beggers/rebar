//! Allocation-free inline stacks without eager initialization.
//!
//! The initialized-prefix invariant is explicit: inline elements in
//! `0..min(length, N)` have been written, and the overflow vector stores the
//! remaining `length.saturating_sub(N)` elements. Elements are `Copy`, so
//! truncation never needs to run a destructor on uninitialized storage.

use std::mem::MaybeUninit;

/// A stack that keeps its first `N` copyable entries in uninitialized storage.
pub(crate) struct InlineStack<T: Copy, const N: usize> {
    inline: [MaybeUninit<T>; N],
    overflow: Vec<T>,
    length: usize,
}

impl<T: Copy, const N: usize> InlineStack<T, N> {
    /// Create an empty stack without writing the inline allocation.
    #[inline]
    pub(crate) fn new() -> Self {
        Self {
            inline: [MaybeUninit::uninit(); N],
            overflow: Vec::new(),
            length: 0,
        }
    }

    /// Return the number of initialized inline and overflow entries.
    #[inline]
    pub(crate) fn len(&self) -> usize {
        self.length
    }

    /// Initialize the next inline entry or append it to the overflow vector.
    #[inline]
    pub(crate) fn push(&mut self, value: T) {
        if self.length < N {
            self.inline[self.length].write(value);
        } else {
            self.overflow.push(value);
        }
        self.length += 1;
    }

    /// Remove and return the last initialized entry.
    #[inline]
    pub(crate) fn pop(&mut self) -> Option<T> {
        if self.length == 0 {
            return None;
        }
        self.length -= 1;
        if self.length < N {
            // SAFETY: push initializes every inline slot below the old
            // length; pop/truncate never expose a slot above the new length.
            // T: Copy guarantees that no destructor can observe the slot.
            Some(unsafe { self.inline[self.length].assume_init_read() })
        } else {
            self.overflow.pop()
        }
    }

    /// Discard all entries after `length` without touching uninitialized data.
    #[inline]
    pub(crate) fn truncate(&mut self, length: usize) {
        if length >= self.length {
            return;
        }
        if self.length > N {
            self.overflow.truncate(length.saturating_sub(N));
        }
        self.length = length;
    }
}

impl<T: Copy, const N: usize> Default for InlineStack<T, N> {
    #[inline]
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::InlineStack;
    use std::mem::size_of;

    #[derive(Clone, Copy, Debug, PartialEq, Eq)]
    struct NoDefault(u64);

    #[derive(Clone, Copy, Debug, PartialEq, Eq)]
    struct WideChoice([usize; 9]);

    fn next_random(seed: &mut u64) -> u64 {
        *seed ^= *seed << 13;
        *seed ^= *seed >> 7;
        *seed ^= *seed << 17;
        *seed
    }

    fn verify_capacity<const N: usize>() {
        let mut seed = 0x5245_4241_525f_5337_u64 ^ N as u64;
        for case in 0..256 {
            let mut actual = InlineStack::<NoDefault, N>::new();
            let mut expected = Vec::<NoDefault>::new();
            for step in 0..2_048 {
                match next_random(&mut seed) & 7 {
                    0..=3 => {
                        let value = NoDefault(next_random(&mut seed));
                        actual.push(value);
                        expected.push(value);
                    }
                    4..=5 => {
                        assert_eq!(
                            actual.pop(),
                            expected.pop(),
                            "N={N} case={case} step={step}"
                        );
                    }
                    _ => {
                        let target = (next_random(&mut seed) % 192) as usize;
                        actual.truncate(target);
                        expected.truncate(target);
                    }
                }
                assert_eq!(
                    actual.len(),
                    expected.len(),
                    "N={N} case={case} step={step}"
                );
            }
            while let Some(value) = expected.pop() {
                assert_eq!(actual.pop(), Some(value), "N={N} case={case}");
            }
            assert_eq!(actual.pop(), None);
            assert_eq!(actual.len(), 0);
        }
    }

    #[test]
    fn zero_inline_capacity_keeps_exact_overflow_order() {
        let mut actual = InlineStack::<NoDefault, 0>::new();
        for value in 0..256 {
            actual.push(NoDefault(value));
        }
        assert_eq!(actual.len(), 256);
        actual.truncate(128);
        for value in (0..128).rev() {
            assert_eq!(actual.pop(), Some(NoDefault(value)));
        }
        assert_eq!(actual.pop(), None);
        verify_capacity::<0>();
    }

    #[test]
    fn inline_boundary_and_overflow_round_trip() {
        for width in [0, 1, 2, 23, 24, 25, 31, 48, 64, 128] {
            let mut actual = InlineStack::<NoDefault, 24>::new();
            for value in 0..width {
                actual.push(NoDefault(value));
            }
            assert_eq!(actual.len(), width as usize);
            for value in (0..width).rev() {
                assert_eq!(actual.pop(), Some(NoDefault(value)));
            }
            assert_eq!(actual.pop(), None);
        }
    }

    #[test]
    fn truncation_at_every_inline_and_overflow_boundary() {
        for target in 0..=80 {
            let mut actual = InlineStack::<NoDefault, 24>::new();
            for value in 0..64 {
                actual.push(NoDefault(value));
            }
            actual.truncate(target);
            let wanted = target.min(64);
            assert_eq!(actual.len(), wanted);
            for value in (0..wanted).rev() {
                assert_eq!(actual.pop(), Some(NoDefault(value as u64)));
            }
            assert_eq!(actual.pop(), None);
        }
    }

    #[test]
    fn default_does_not_require_default_elements() {
        let mut actual = InlineStack::<NoDefault, 8>::default();
        assert_eq!(actual.len(), 0);
        actual.push(NoDefault(17));
        assert_eq!(actual.pop(), Some(NoDefault(17)));
    }

    #[test]
    fn wide_vm_choices_preserve_layout_and_values() {
        assert_eq!(size_of::<WideChoice>(), 72);
        let mut actual = InlineStack::<WideChoice, 24>::new();
        for value in 0..96_usize {
            actual.push(WideChoice([value; 9]));
        }
        actual.truncate(63);
        for value in (0..63_usize).rev() {
            assert_eq!(actual.pop(), Some(WideChoice([value; 9])));
        }
        assert_eq!(actual.pop(), None);
    }

    #[test]
    fn seeded_randomized_inline_capacity_one() {
        verify_capacity::<1>();
    }

    #[test]
    fn seeded_randomized_inline_capacity_two() {
        verify_capacity::<2>();
    }

    #[test]
    fn seeded_randomized_inline_capacity_twelve() {
        verify_capacity::<12>();
    }

    #[test]
    fn seeded_randomized_choice_capacity() {
        verify_capacity::<24>();
    }

    #[test]
    fn seeded_randomized_capture_capacity() {
        verify_capacity::<48>();
    }

    #[test]
    fn seeded_randomized_large_overflow_capacity() {
        verify_capacity::<96>();
    }
}
