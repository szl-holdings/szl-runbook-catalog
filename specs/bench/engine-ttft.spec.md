---
id: bench/engine-ttft
class: bench
version: 1
title: Engine bench - TTFT and throughput percentiles
owner: szl-holdings
receipt: 91d8a7526b1ce486f427c45a5084b6c19228396c59e391a0e022ed68247de957
assets:
  - szl-holdings/frontier-bench
  - szl-holdings/szl-engine-bench
---

# Engine TTFT lane

Vendor-neutral OpenAI-compatible benchmarking across vLLM, SGLang, TGI,
llama.cpp, MLX, Transformers. Measured TTFT p50/p95/p99 and tok/s only.
Unconfigured engines report BLOCKED. Pattern note (wave-2 audit): tokenizer
throughput is a first-class co-lane - see bench/tokenizer-throughput.
