---
id: bench/tokenizer-throughput
class: bench
version: 1
title: Tokenizer throughput lane (gigatoken pattern)
owner: szl-holdings
receipt: 63e6d90d47a75d58caf07b919be6fb23df2cb3f898fcb9f6858ec439249775c4
tags:
  - tokenization
  - rust-grade-perf
assets:
  - szl-holdings/szl-engine-bench
---

# Tokenizer throughput

Wave-2 cherry-pick: marcelroed/gigatoken showed tokenization at GB/s is its own
frontier. This lane measures tokens/sec, MB/s, and per-1M-token latency for the
serving tokenizers in scope, so TTFT numbers are never silently
tokenizer-bound. Measured or BLOCKED; comparison across tokenizers requires
identical corpus + revision, else INVALID.
