# Rust build and Python-boundary lab

This lab tests ways to build the from-scratch Rust regex engine and its Python extension. It never wraps an outside regex package, never delegates to Python `re`, and never uses unseen holdout cases to choose compiler settings.

## Result

The strongest portable practice-only build is `rust-unroll-512` at 1.1000× (95% interval 1.0810–1.1189×). It has 1 practice slowdown above 20%; `finditer` on `cal.expanded.byte-buffer.00` is 21.36% slower. The fastest portable build with no slowdown above 20% is `rust-unroll-1024` at 1.0943× (95% interval 1.0754–1.1141×). These are practice-only results; they do not measure the holdout or authorize a production build change.

The experiment attempts **68 builds**; **67 pass the import and correctness gates**. The accepted comparison covers **444 frozen practice cases** across **196 categories**, **7 paired trials**, **248,640 raw timings**, and **497,280 result checks**. Each build runs in its own Python process; alternatives are randomly interleaved for every individual case and trial. Intervals resample both cases and trials.

Each pilot uses at most **16 operations** per timing and **4 untimed warmups**. These caps are for choosing builds; the separately frozen project holdout keeps its original operation counts.

This is a build-selection experiment, not the project's full holdout score. All results below compare with the existing portable Rust release build: **1× means the same speed; higher is faster**.

The case counts use the same frozen practice cases for every build. A large slowdown means the case took more than 20% longer than the current Rust build. The baseline has no faster-case count because it is being compared with itself. Every large slowdown is individually identified in the evidence bundle by workload, Python operation, measured speed, and slowdown.

| Build | Speed | 95% interval | Faster cases | Large slowdowns | Portable | Extension size |
| --- | ---: | ---: | ---: | ---: | :---: | ---: |
| `rust-unroll-512` | 1.1000× | 1.0810–1.1189× | 380/444 | 1 | yes | 112,200 B |
| `rust-unroll-1024` | 1.0943× | 1.0754–1.1141× | 378/444 | 0 | yes | 112,200 B |
| `bridge-clang` | 1.0269× | 1.0072–1.0471× | 281/444 | 4 | yes | 94,544 B |
| `bridge-clang-no-plt` | 1.0208× | 1.0014–1.0418× | 275/444 | 1 | yes | 93,736 B |
| `bridge-clang-lto` | 1.0182× | 0.9969–1.0382× | 266/444 | 4 | yes | 94,488 B |
| `bridge-clang-o2` | 1.0129× | 0.9923–1.0353× | 248/444 | 5 | yes | 94,584 B |
| `bridge-native-tune` | 1.0115× | 0.9926–1.0312× | 253/444 | 6 | yes | 112,280 B |
| `bridge-no-interposition` | 1.0094× | 0.9906–1.0283× | 242/444 | 4 | yes | 112,200 B |
| `bridge-no-plt` | 1.0093× | 0.9905–1.0291× | 242/444 | 4 | yes | 107,224 B |
| `bridge-zig-cc` | 1.0072× | 0.9911–1.0220× | 245/444 | 4 | yes | 240,208 B |
| `bridge-hidden` | 1.0071× | 0.9888–1.0263× | 232/444 | 6 | yes | 112,200 B |
| `rust-inline-1000` | 1.0047× | 0.9876–1.0215× | 237/444 | 5 | yes | 112,200 B |
| `rust-unroll-256` | 1.0047× | 0.9887–1.0217× | 224/444 | 5 | yes | 112,200 B |
| `bridge-static-clang` | 1.0041× | 0.9895–1.0193× | 234/444 | 1 | yes | 2,221,408 B |
| `bridge-symbolic-functions` | 1.0034× | 0.9853–1.0228× | 228/444 | 3 | yes | 112,200 B |
| `bridge-zig-cc-native` | 1.0020× | 0.9874–1.0163× | 227/444 | 1 | no | 240,520 B |
| `bridge-static-gc-strip` | 1.0014× | 0.9854–1.0173× | 220/444 | 4 | yes | 648,152 B |
| `baseline` | 1.0000× | 1.0000–1.0000× | — | 0 | yes | 112,200 B |
| `rust-inline-300` | 0.9993× | 0.9804–1.0190× | 217/444 | 9 | yes | 112,200 B |
| `rust-thin-lto` | 0.9988× | 0.9823–1.0160× | 207/444 | 6 | yes | 112,200 B |
| `bridge-zig-cc-lto` | 0.9978× | 0.9852–1.0106× | 183/444 | 1 | yes | 265,432 B |
| `rust-symbolic-functions` | 0.9977× | 0.9810–1.0135× | 209/444 | 3 | yes | 112,200 B |
| `rust-inline-225` | 0.9973× | 0.9783–1.0172× | 217/444 | 6 | yes | 112,200 B |
| `rust-thin-cgu-8` | 0.9966× | 0.9795–1.0129× | 208/444 | 6 | yes | 112,200 B |
| `bridge-static-rust` | 0.9964× | 0.9784–1.0151× | 211/444 | 6 | yes | 2,235,816 B |
| `rust-cgu-4` | 0.9951× | 0.9785–1.0125× | 192/444 | 10 | yes | 112,200 B |
| `rust-no-slp-vectorize` | 0.9948× | 0.9785–1.0109× | 206/444 | 5 | yes | 112,200 B |
| `bridge-static-hidden` | 0.9944× | 0.9771–1.0105× | 204/444 | 5 | yes | 2,234,792 B |
| `bridge-native-arch` | 0.9943× | 0.9757–1.0127× | 215/444 | 5 | no | 108,104 B |
| `rust-thin-x86-64-v3` | 0.9943× | 0.9745–1.0148× | 203/444 | 6 | no | 112,200 B |
| `bridge-gcc-lto` | 0.9940× | 0.9801–1.0078× | 199/444 | 6 | yes | 112,192 B |
| `rust-x86-64-v2` | 0.9938× | 0.9733–1.0129× | 201/444 | 10 | no | 112,200 B |
| `rust-inline-150` | 0.9934× | 0.9768–1.0103× | 209/444 | 5 | yes | 112,200 B |
| `rust-inline-75` | 0.9934× | 0.9768–1.0098× | 203/444 | 3 | yes | 112,200 B |
| `rust-inline-550` | 0.9923× | 0.9730–1.0121× | 199/444 | 11 | yes | 112,200 B |
| `rust-inline-450` | 0.9921× | 0.9731–1.0120× | 206/444 | 11 | yes | 112,200 B |
| `rust-cgu-16` | 0.9919× | 0.9749–1.0076× | 202/444 | 10 | yes | 112,200 B |
| `rust-no-loop-vectorize` | 0.9915× | 0.9757–1.0070× | 179/444 | 3 | yes | 112,200 B |
| `rust-unroll-128` | 0.9911× | 0.9743–1.0073× | 198/444 | 9 | yes | 112,200 B |
| `bridge-static-gc-native` | 0.9902× | 0.9760–1.0042× | 192/444 | 2 | no | 2,192,992 B |
| `rust-thin-cgu-16` | 0.9863× | 0.9674–1.0046× | 184/444 | 9 | yes | 112,200 B |
| `bridge-clang-no-interposition` | 0.9855× | 0.9683–1.0027× | 191/444 | 10 | yes | 94,544 B |
| `rust-opt-2` | 0.9855× | 0.9669–1.0050× | 180/444 | 15 | yes | 112,200 B |
| `rust-native-inline-450` | 0.9852× | 0.9640–1.0051× | 198/444 | 15 | no | 112,200 B |
| `bridge-static-zig-native` | 0.9844× | 0.9704–0.9992× | 176/444 | 5 | no | 641,888 B |
| `bridge-static-zig` | 0.9841× | 0.9683–1.0014× | 191/444 | 12 | yes | 641,856 B |
| `bridge-static-gc` | 0.9827× | 0.9658–0.9996× | 178/444 | 8 | yes | 2,234,792 B |
| `bridge-static-thin-strip` | 0.9824× | 0.9683–0.9961× | 175/444 | 4 | yes | 668,632 B |
| `rust-inline-700` | 0.9824× | 0.9650–0.9987× | 180/444 | 8 | yes | 112,200 B |
| `rust-cgu-8` | 0.9823× | 0.9657–0.9993× | 176/444 | 13 | yes | 112,200 B |
| `bridge-static-strip-all` | 0.9816× | 0.9639–1.0001× | 172/444 | 12 | yes | 648,152 B |
| `rust-inline-350` | 0.9811× | 0.9618–1.0004× | 178/444 | 17 | yes | 112,200 B |
| `bridge-static-strip-debug` | 0.9800× | 0.9612–0.9990× | 180/444 | 16 | yes | 733,416 B |
| `rust-thin-cgu-4` | 0.9799× | 0.9634–0.9979× | 161/444 | 10 | yes | 112,200 B |
| `rust-inline-100` | 0.9796× | 0.9632–0.9959× | 178/444 | 8 | yes | 112,200 B |
| `rust-no-lto` | 0.9786× | 0.9592–0.9969× | 181/444 | 20 | yes | 112,200 B |
| `bridge-static-rust-native` | 0.9761× | 0.9617–0.9900× | 156/444 | 6 | no | 2,194,016 B |
| `rust-inline-25` | 0.9756× | 0.9600–0.9909× | 166/444 | 10 | yes | 112,200 B |
| `rust-x86-64-v3` | 0.9739× | 0.9523–0.9947× | 165/444 | 16 | no | 112,200 B |
| `bridge-static-thin` | 0.9738× | 0.9594–0.9886× | 155/444 | 6 | yes | 2,320,912 B |
| `rust-thin-native` | 0.9700× | 0.9480–0.9917× | 167/444 | 25 | no | 112,200 B |
| `bridge-static-gc-x86-64-v3` | 0.9642× | 0.9507–0.9779× | 115/444 | 12 | no | 2,192,024 B |
| `bridge-o2` | 0.9538× | 0.9410–0.9671× | 111/444 | 10 | yes | 96,160 B |
| `rust-unroll-64` | 0.9536× | 0.9363–0.9705× | 111/444 | 25 | yes | 112,200 B |
| `rust-native` | 0.9484× | 0.9286–0.9685× | 130/444 | 33 | no | 112,200 B |
| `rust-opt-s` | 0.9013× | 0.8846–0.9185× | 66/444 | 91 | yes | 112,200 B |
| `rust-opt-z` | 0.6909× | 0.6758–0.7060× | 18/444 | 380 | yes | 112,200 B |

Builds rejected before timing:
- `bridge-static-zig-lto`: ld.lld: error: /tmp/rebar-rust-build-final-v1/targets/b6a590ef25436ccd4631/release/deps/librebar_rust_continuation.a(rebar_rust_continuation.rebar_rust_continuation.78caecf99bcbdc62-cgu.0.rcgu.o): Unknown attribute kind (105) (Producer: 'LLVM22.1.6-rust-1.97.1-stable' Reader: 'LLVM 21.1.0')

An earlier report incorrectly flagged a 20% slowdown only once it exceeded 25%. Every original timing was audited again with the correct `speedup < 1 / 1.2` boundary. The unchanged raw measurements, corrected counts, and original rejected summary are all preserved in the evidence bundle.

CPU-specific `native` and `x86-64-v2/v3` builds are explicitly marked nonportable: they must not become the default for a drop-in Python replacement. Zig's C compiler also selects the host CPU by default; a Zig result is marked portable only when explicitly compiled with `-mcpu=baseline`.

## Experiments kept, including rejections

- Early time-separated build runs are preserved in full. They produced contradictory apparent winners because changing machine load affected whole variant blocks. Their case-only confidence intervals did not capture that drift; their rankings are rejected.
- Direct Rust-to-extension static linking, hidden exports, section-level dead-code removal, and symbol stripping are measured and their exact binary sizes are included above.
- GCC, Clang, and Zig's C compiler are separately tested. True cross-language link-time optimization is recorded as rejected when Rust's LLVM 22 bitcode cannot be read by Zig's LLVM 21.
- Zig's default host-specific machine code and an initially unloadable static extension are retained as failed experiments. Only explicit baseline CPU selection, correct unwind linkage, and a passing real Python import qualify a Zig-built variant.
- Profile-guided Rust builds were actually generated and trained against the frozen practice suite. LLVM 18 cannot merge Rust's LLVM 22 raw profile, and a separately recorded header-conversion experiment proves the profile layouts are incompatible.
- An offline dependency-tree check confirms the engine has zero outside packages.

## Reproduce

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONPATH=. "$PY" tools/rust_build_probe.py list
PYTHONPATH=. "$PY" tools/rust_build_probe.py paired --workspace /tmp/rebar-rust-build-reproduction --samples-per-category 3 --max-ops 16 --trials 7 --bootstraps 2000 --batch-size 6
```

The deterministic, compressed lab includes the complete measurements, frozen practice-case hashes, build commands, source hashes, all rejected raw pilots, LLVM diagnostics, and the original training profile: [`rust-v6-build-lab.json.gz`](rust-v6-build-lab.json.gz).

Bundle SHA-256: `691bb0b5891c4f3ea85fe67be674bc6d103488f85006e73e63323f7c014acc76`.
