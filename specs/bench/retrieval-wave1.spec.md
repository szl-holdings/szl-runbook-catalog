---
id: bench/retrieval-wave1
class: bench
version: 1
title: Retrieval bench - wave-1 lane invocation
owner: szl-holdings
receipt: f939a1bd18f1e89ffdd302aea09394c3638701afb433dda49390bddd04395bc8
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
