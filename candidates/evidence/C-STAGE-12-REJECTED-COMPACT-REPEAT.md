# Rejected C experiment: preserve optional captures

The independently implemented C engine needs to compile huge multi-character repeats without expanding billions of instructions. Its [first compact-repeat patch](C-STAGE-12-REJECTED-COMPACT-REPEAT.patch) adds a native, input-bounded repeat instruction and keeps the existing optimized single-character path.

The [one actual frozen bounded verification](rust-v8-vm-stage-12-bounded-manual-path-diagnostic.json) rejects that implementation:

| Frozen diagnostic | Actual result |
| --- | ---: |
| Manual patterns attempted | 2/16 |
| Real Python-comparison checks | 98 |
| First pattern | 49/49 correct |
| Second pattern | 2 observable differences |
| Isolated pattern timeout | 3 seconds |
| Global diagnostic bound | 60 seconds |

For the original pattern `((a)?)*`, standard Python records the first optional capture as an empty string when an inverted matching window still permits zero repetitions. The rejected C implementation instead records that capture as unmatched. Both `match` and `scanner.match` reveal the difference.

The original failed C source hashes are `c24705dd008f83b2d268482cb1fb0b1269e160a38e6a0b13b9514c2dd7eed0a5` for the Python compiler and `66ddb1c9282e556ec2de0f8df518ca876b0a939f06fc87bed9895b8a548098c3` for the native engine. The loaded native library was `636d398906d409c6362d904b2126417801b857ec2818825a3e1796f2118f2983`. The [complete source patch](C-STAGE-12-REJECTED-COMPACT-REPEAT.patch) and [all actual mismatch records](rust-v8-vm-stage-12-bounded-manual-path-diagnostic.json) are preserved.

The remaining **14** manual patterns and the full extended campaign were **NOT MEASURED** for this rejected design. No hidden benchmark was accessed, no speed was measured, and the broken candidate was not committed as production source.
