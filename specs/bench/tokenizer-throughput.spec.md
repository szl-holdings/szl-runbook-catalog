---
id: bench/tokenizer-throughput
class: bench
version: 1
title: Tokenizer throughput lane (gigatoken pattern)
owner: szl-holdings
receipt: 5e4d3c2b1a0987654321fedcba0987654321abcdef0123456789abcdef0123
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
