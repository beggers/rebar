# USER-ASK-3

Status: done
Owner: supervisor
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Keep the landing-page README concise and honest about actual compatibility progress, and decide whether cleanup work should move to a dedicated agent.

## Completion Note
- Shortened the README's generated phase and milestone summaries by switching the tracked state to single-sentence versions that the report sync consumes directly.
- Added an explicit compatibility heuristic and a published-slice note so `158/158` correctness passes are not read as near feature-complete stdlib `re` parity.
- Updated the landing-page prose and benchmark notes to reflect the current `139`-workload, `113`-measured, `26`-gap benchmark surface and the fact that the full suite still runs through the source-tree shim.
- Recorded the durable decision to keep periodic cleanup/reporting compaction under the supervisor for now instead of adding a separate cleanup agent; revisit only if cleanup becomes a recurring bottleneck distinct from queue/state ownership.
