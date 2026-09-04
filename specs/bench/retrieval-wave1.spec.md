---
id: bench/retrieval-wave1
class: bench
version: 1
title: Retrieval bench - wave-1 lane invocation
owner: szl-holdings
receipt: 3f4f8f0d2b7b0e2a1b1e2a5f6c4d2c1a0f9e8d7c6b5a49382716f5e4d3c2b1a09
tags:
  - retrieval
  - bm25
  - rrf
assets:
  - szl-holdings/retrieval-bench
  - szl-holdings/szl-retrieval-bench
---

# Retrieval wave-1

Invoke the retrieval bench lanes: sparse BM25, dense, hybrid RRF, with
nDCG/Recall/MRR/MAP and fairness-gated comparisons. Receipts are hash-chained;
cross-revision comparisons are INVALID by construction.

Honesty: a lane without its corpus reports BLOCKED, never a fabricated metric.
