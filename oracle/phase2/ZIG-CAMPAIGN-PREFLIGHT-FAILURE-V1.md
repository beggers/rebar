# Preserve the actual Zig campaign preflight failure

This freezes the evidence for one real failed attempt to start the original
Zig correctness campaign. It does not run the campaign again, activate a
candidate, touch either original Zig library, publish failure evidence, or
claim that any regular-expression matching occurred.

## What actually happened

The once-only, completely pinned V1 original campaign process exited with
status 1 before activation and before any of its 13 candidate workers began.
Its complete captured standard error ends with:

```text
_rebar_owned_zig_original_campaign_v1_v6_activation_d3a9b08c1bf7e3408719.ActivationError: refuse an absent, linked, altered, or substituted original Zig engine inode
```

The process ID was NOT RECORDED. Standard output was exactly empty. The
entire original standard error, its final newline, SHA-256, byte count,
base64, all six actual traceback frames, and the fully pinned once-only
command are reproduced in the canonical machine contract. The source never
launches that command or invents an observed process ID.

The failure is infrastructure, not a matching result. The historical V2
native-owner reader genuinely returns exactly `relative`, `path`, `sha256`,
`size_bytes`, `device`, `inode`, and `mode`. The V6 owner comparison also
requires `nlink` and `uid`, neither of which that genuine V2 return value
contains. Consequently, even both correct original files are rejected. The
immutable V1 controller calls this check before entering the `try` block that
would publish a campaign failure. Therefore neither a successful campaign
archive nor a campaign failure archive exists.

Both real original Zig targets are present and unchanged. The original
engine is device 2064, inode 431260, mode `0700`, 478,432 bytes, link count
one, owner 1000, SHA-256
`b76eb6c7ecd60c1d221f6ddb822573a5f962641cf4e6f16da75d21561b104652`.
The original bridge is device 2064, inode 431274, mode `0700`, 134,112
bytes, link count one, owner 1000, SHA-256
`d8ac0da492d960716cbc74c25d7cb5027aea3fcfe2bf0a6fb2ec8e432345fb3b`.
The source-only freeze proves the owner-shape problem in memory. It never
opens, stats, links, replaces, or hashes either native target.

## Keep the original reference and historical results

The reference remains pinned CPython 3.14.6, all 13 original suites, all
31,237 planned case executions, and 13 named private waivers. Because zero
workers started, actual Zig matching cases executed are zero and the number
of matching differences is NOT MEASURED. A preflight failure is not a
candidate crash, a candidate result, or a zero-mismatch result.

V25 remains the most recent published result: 139 actual evidence owners and
144 authenticated historical references. The preserved C campaign has 13
workers, 7,325 passing cases, 1,262 mismatches, and no infrastructure
failure. Rust retains its real 28 build steps and both first-party repairs.
The genuine Zig source build retains its real 26 steps and its historical
135-owner, 140-reference build-time baseline. Historical Rust and Zig
matching failures remain 2,042 and 1,764. No candidate qualifies.

The final holdout is NOT OPENED. Speed, memory, undefined behavior, matching,
and confidence intervals are NOT MEASURED. The four original campaign
success/failure archive and receipt paths are required to remain absent.

## Separately authorized preservation

This three-owner source freeze publishes no result evidence. Only a later,
explicit, independently pinned `--preserve` may first verify both original
user-owned targets and create exactly two new files: a bounded, canonical,
single-member, zero-mtime gzip failure archive and its distinct durable
publication receipt. Both require exclusive no-follow mode-`0600` creation,
full readback, complete original traceback preservation, file and directory
fsync, and unchanged original native inode verification before and after
publication. It never reruns or activates the candidate.

Run ordinary and true sterile `env -i PATH=/usr/bin:/bin` forms of both
`--self-test` and `--verify-frozen-context`, each with the three separately
published source, protocol and contract SHA-256 pins. All must preserve
zero native target reads, stats, links, replacements, workers, activations,
campaign runs, clocks, holdout access, candidate imports, and workspace
mutations.

Status: SOURCE FROZEN; FAILURE PRESERVATION NOT RUN.
