---
id: kernel-fixture/attention-trio
class: kernel-fixture
version: 1
title: Attention kernel trio - deterministic fixture + console axes
owner: szl-holdings
receipt: c6b07f178508402a259eafb06efbfa51948226d418b6981be33b5dd4b6dac874
assets:
  - szl-holdings/szl-receipt-attn
  - szl-holdings/szl-maskmod
  - szl-holdings/szl-block-kv
  - szl-holdings/YARQA-ATTN
---

# Attention trio fixture

Deterministic 256-dim fixture for the SZL attention kernels. Invariants per
kernel: receipt chain present, deterministic replay equal, honesty label set.

Wave-2 note (MatthewBonanni/attn-viz): the kernel console renders per-variant
shape flow, FLOPs, memory traffic, and roofline position for MHA/GQA/MQA/MLA -
computed from declared dims, labeled METHOD, never measured-by-assertion.
