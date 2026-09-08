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
- `.github/workflows/validate.yml` - source-artifact validation on pull requests
  and `main`

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

The whole-catalog command fails closed when `catalog.yaml` or `specs/` is
missing, when no specs are discovered, or when registry IDs and spec artifacts
do not match exactly. CI also runs adversarial tests for those cases.

## Provider ownership

This repository is source-only. It does not upload `estates.json`,
`verticals.json`, or any other artifact to Hugging Face. The Constellation
release lane exclusively owns publication of the canonical manifests in
`SZLHOLDINGS/szl-constellation`; catalog validation requires no provider token.

Doctrine v11 — a spec that fails validation is BLOCKED, never grandfathered.
Apache-2.0 · SZL Holdings
