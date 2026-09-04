---
id: gpu-jobspec/nemo-v3-rerun
class: gpu-jobspec
version: 1
title: Nemo v3 jobspec regeneration envelope
owner: szl-holdings
receipt: 79d710f9ba9efe8815670ebda43038dc6fc56961f5851c73ce8efa05df7863b1
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
