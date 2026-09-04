---
id: gpu-jobspec/nemo-v3-rerun
class: gpu-jobspec
version: 1
title: Nemo v3 jobspec regeneration envelope
owner: szl-holdings
receipt: 9f8e7d6c5b4a39281706f5e4d3c2b1a09f8e7d6c5b4a39281706f5e4d3c2b1a
assets:
  - szl-holdings/szl-gpu-bridge
---

# Nemo v3 rerun envelope

The two engine-signature jobspecs (szl-gpu-bridge#93, #20) expired in August.
This catalog entry pins the regeneration contract: fresh expires_at, controller
regenerated (never hand-edited hashes), signed on the enrolled owner laptop,
verified by the bridge flipping the issue status off EXPIRED.

Wave-1 note (SkyPilot): scheduling metadata (cheapest-watt placement,
preemption policy) rides in the spec, and the placement decision itself emits a
receipt.
