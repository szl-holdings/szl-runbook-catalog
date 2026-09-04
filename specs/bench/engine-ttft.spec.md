---
id: bench/engine-ttft
class: bench
version: 1
title: Engine bench - TTFT and throughput percentiles
owner: szl-holdings
receipt: 8a1c2e4f6b8d0a2c4e6f8a0c2e4b6d8f0a2c4e6b8d0f2a4c6e8b0d2f4a6c8e0b2
assets:
  - szl-holdings/frontier-bench
  - szl-holdings/szl-engine-bench
---

# Engine TTFT lane

Vendor-neutral OpenAI-compatible benchmarking across vLLM, SGLang, TGI,
llama.cpp, MLX, Transformers. Measured TTFT p50/p95/p99 and tok/s only.
Unconfigured engines report BLOCKED. Pattern note (wave-2 audit): tokenizer
throughput is a first-class co-lane - see bench/tokenizer-throughput.
