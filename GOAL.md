/goal Complete this falsifiable experiment.

Create multiple independent Python re replacements and find any that are compatible and materially faster end-to-end. The winner must support "import rebar as re". Pin latest stable CPython as oracle/baseline. Languages, engines, bindings, and strategies are unconstrained; discover them experimentally. Ignore prior project content/history except push metadata.

Before any mutation, make GOAL.md exactly "/goal " plus this objective. Never edit it; record amendments separately and link its hash from README. Commit and push this bootstrap.

Proceed only through these phases:
1. CORRECTNESS ORACLE. Before code, freeze a comprehensive versioned P0 matrix and suite from CPython plus differential/property/fuzz tests. Validate stdlib-vs-stdlib; preserve seeds/failures; allow only named private waivers. Gate: every obligation mapped, deterministic reproduction, zero unexplained self-oracle failures.
2. CANDIDATES. After phase 1 is documented, committed, and pushed, build at least three materially distinct independently runnable replacements behind one public contract. Each must implement complete P0 and pass the same frozen oracle. Candidates sharing a semantic parser/compiler/executor/engine count as one family; wrappers/configurations do not count separately. Explore broadly without prescribing or prematurely choosing a design. No candidate may directly or indirectly delegate production work to stdlib re, _sre, CPython's regex engine, or another candidate. Stdlib is allowed only in isolated oracle/benchmark processes. Audit zero delegation. No fallback, approximation, hardcoded oracle answers, benchmark detection, or weakened tests. Gate: three complete candidates with zero unexplained P0 mismatches/crashes/UB.
3. PERFORMANCE ORACLE. After phase 2 is documented, committed, and pushed, freeze balanced weights, protocol, seeds, and holdout. Benchmark every candidate and unmodified stdlib re against each other under identical conditions. Correctness-gate every case. Cover representative APIs/workloads, lifecycles, time, memory, and boundary costs. Use paired trials, confidence intervals, raw data, and show all cases/regressions. Select no winner early.
4. OPTIMIZE/FALSIFY. Profile and add architectures only when evidence supports them; rerun both oracles and correctness-gate every timing. Preserve all candidates/results/rejections. Select the simplest fully compatible winner supported by total evidence and expose it as rebar.

Success requires three correctness-qualified candidates benchmarked; the winner has zero unexplained P0 mismatches/crashes/UB, >=1.5x holdout geomean speedup over stdlib, is statistically faster on >=60% of cases, and explains every regression >20%.

A chunk is one oracle category, candidate feature, benchmark cohort, or experiment. After each: run gates; update README/evidence/graphs; make one focused commit; push the feature branch. Bootstrap with "git push -u origin HEAD". Never batch chunks, force-push, rewrite pushed history, mix unrelated work, or push broken/default branches. If blocked, retain commits, show unpushed count, report why, and retry.

README must be scannable and correct at every commit. Lead with phase/gate/verdict, next chunk, versioned correctness tested/total, candidate completion/results, benchmark coverage/ranking, failures/gaps, and evidence links. Use NOT MEASURED, never guesses. Generate reproducible committed charts for correctness, speed/confidence, memory, regressions, and rankings. Never hand-edit, cherry-pick, hide losses, or change denominators silently.

Leave source, lockfiles, oracles, data, and candidates. Never release/deploy or use destructive git.

A plan/prototype is not completion. Either all gates pass, or after three serious materially distinct attempts with no evidence-backed next path, preserve everything and push a rigorous negative report explaining why no faster compatible drop-in was achieved.

Do this all on the main branch. Delete what's already there.
