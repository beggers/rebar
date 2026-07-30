# Rust full-public semantic source build V32

Status: SOURCE FROZEN; NATIVE BUILD NOT RUN; CORRECTNESS NOT MEASURED.

Final holdout: INVALIDATED; REKEYED SUCCESSOR REQUIRED.

This immutable first-party freeze composes three independently frozen,
committed, pushed, and exclusively materialized semantic overlays. It preserves
the actual complete V30 native build, the actual original V26 PASS across all
31,237 cases and 13 suites, and the actual public V28 FAIL across 1,145 of
10,434 cases. The public mismatch partition is exactly scanner 470,
substitution 376, comment 297, and scoped Unicode 2. The separately counted
scanner/comment overlap is 15; substitution/comment overlap is 12. These
overlaps are never added to the disjoint 1,145-case partition.

## Authenticated complete source composition

- Scanner-complete Rust/C bridge:
  `candidates/rust/variants/complete_scanner_bridge_v1/py_bridge.c`,
  SHA-256 `f6253fbecc76b64750a22dc9393180d3ea6e3f2e29aace006c0479543e94342e`,
  178,472 bytes. Its independently frozen source, protocol, contract, and
  actual application are pinned and authenticated. The existing complete
  substitution/expansion, safe capture clamping, and removal of external
  introspection remain intact.
- Combined scoped-Unicode optimized Rust engine:
  `candidates/rust/variants/combined_scoped_unicode_engine_v1/lib.rs`,
  SHA-256 `7412a997975aa42ec18249bc28d17e3c39223a4089bd23e3f7d2ab8112993b38`,
  189,493 bytes. Its independently frozen source, protocol, contract, and
  actual application are pinned and authenticated. Mandatory anchor search,
  compiler allocation fast paths, 17,442 bounded differential checks, and
  zero external dependencies remain intact.
- Optimized first-party search source:
  `candidates/rust/variants/combined_search_compiler_fastpath_v2/search.rs`,
  SHA-256 `4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7`,
  24,305 bytes.
- Corrected complete comment/public adapter:
  `candidates/rust/variants/corrected_comment_adapter_v2/rust_candidate.py`,
  SHA-256 `f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227`,
  34,039 bytes. All four existing private-interface corrections and three
  additional comment repairs are preserved. V1's immutable, safely rejected
  preapplication failure is separately pinned; the independently frozen V2
  source, protocol, contract, and successful application are pinned.

No canonical Rust source, installed native library, or canonical public adapter
is replaced. Each actual private phase independently owns nine source files;
five canonical bytes are unchanged and four exact overlays are applied once.
Both source phases use the existing fully audited V16/V9/V7/V4 first-party
offline build kernel. Exactly 28 independently observed compiler/auditor
processes, two engine ELFs, two bridge ELFs, and cross-phase byte identity are
required. Cargo uses `build --release --locked --offline --frozen` and has zero
external dependencies. Every original canonical and runtime owner identity is
verified unchanged before durable publication.

## SOURCE-ONLY WALL

The irreversible deny-default audit wall is installed before the first owner
read. Only exact descriptor-pinned regular, private, single-link first-party
owners may be read. Every final proposal content open and every final proposal
metadata probe is denied. The historical retired-final hash is a constant
provenance pin only: no stat, lstat, open, or other proposal operation is
performed. Hidden cases, candidate execution/import, installed native opens,
native loading, private-root access, archives, process creation, clocks,
entropy, networking, Git metadata, and workspace mutations are forbidden.

Independently pin the source and protocol before rendering:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S \
      tools/reproduce_owned_rust_full_public_semantic_source_build_v32.py \
      --render-contract --source-sha256 SOURCE_SHA --protocol-sha256 PROTOCOL_SHA

Root may publish the rendered canonical JSON only as the exact third immutable
owner. Both normal and sterile environments must independently pass:

    --self-test --source-sha256 SOURCE_SHA --protocol-sha256 PROTOCOL_SHA \
      --contract-sha256 CONTRACT_SHA
    --verify-frozen-context --source-sha256 SOURCE_SHA \
      --protocol-sha256 PROTOCOL_SHA --contract-sha256 CONTRACT_SHA

Each self-test actually rejects candidate import, native open/load, private
root, retired final content, retired final metadata, public final V3 proposal,
hidden cases, native loading, compiler launch, candidate launch, networking,
clock, entropy, inherited descriptors, direct metadata, workspace writes,
directory enumeration, and foreign dynamic code compilation. No candidate is
executed, no native build occurs, no proposal content is opened, and no
proposal metadata is probed in any source gate.

## Separately authorized actual native build

The actual operation is forbidden before every source gate passes and the exact
source/protocol/contract triple has been committed and pushed. Only root may
provide `--root-authorized --frozen-committed-pushed`; frozen and pushed
commits must be identical. Root must independently caller-pin all nine
canonical owners and all scanner/scoped/comment source, protocol, contract,
application, historical V1 failure, V26 original PASS, V28 public gate, V30
native publication/root, and retained historical operational owners.

The actual operation consumes exclusively the pinned first-party overlays,
invokes exactly 28 real offline compiler/ELF-audit processes across two private
phases, validates byte-identical engine and bridge artifacts between phases,
restores all original owners, and exclusively publishes a gzip build archive,
durable publication receipt, and durable private-root provenance receipt.

Neither native publication PASS nor historical original PASS implies current
candidate correctness, runtime non-delegation, qualification, performance,
memory, or winner selection. Public 10,434-case and original 31,237-case
reruns, plus strict runtime non-delegation, remain separate root-authorized
operations. Candidate correctness remains NOT MEASURED, runtime non-delegation
remains NOT ESTABLISHED, and no candidate is qualified. The final holdout
remains INVALIDATED; REKEYED SUCCESSOR REQUIRED.
