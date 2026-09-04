# SZL Runbook Catalog

The estate's registry of **receipted task specs**. Pattern credit: SkyPilot's
catalog made reusable task specs a first-class artifact. The SZL evolution:
every spec is hash-committed, validated fail-closed, and carries a receipt
anyone can recompute offline.

## Layout

- `catalog.yaml` — the registry: every admitted spec, its class, its receipt
- `specs/` — the specs themselves (YAML front-matter + body)
- `catalog.py` — stdlib-only validator: schema, registry linkage, receipt
  recomputation. Exit non-zero on any violation. No third-party deps.
- `.github/workflows/mirror.yml` — receipted GitHub→HF Space sync

## Spec classes

| class | purpose |
|---|---|
| `bench` | benchmark lane invocations (retrieval / engine / quant / calibration) |
| `kernel-fixture` | deterministic kernel fixtures and expected invariants |
| `gpu-jobspec` | szl-gpu-bridge job envelopes (DSSE-signed downstream) |
| `vertical-asset` | wiring records binding a vertical to its repos/kernels/models |

## The receipt

`sha256` over the canonical payload: sorted keys, compact separators, the
`receipt` field excluded. Recompute any spec:

```bash
python3 catalog.py verify            # whole catalog, fail-closed
python3 catalog.py verify specs/bench/retrieval-wave1.spec.md   # one spec
```

Doctrine v11 — a spec that fails validation is BLOCKED, never grandfathered.
Apache-2.0 · SZL Holdings
