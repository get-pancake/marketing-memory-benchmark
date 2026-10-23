# Fixed-context recommendation pilot

This is an executable **prepared** Claude/GPT comparison, not recorded provider
results. `providers.example.json` deliberately leaves model IDs and rates unset.
Current access and pricing must be established before an actual run.

The pilot uses 16 already-known development cases. Both providers and both
methods receive exactly the same selected current company context per case.
One prompt is a capable direct baseline; the other adds a candidate-checking
checklist. Each raw proposal is also evaluated after a common deterministic
validator. The 64 possible model calls therefore support 128 dependent
raw/validated evaluations, not 128 independent examples. No mock supplies a
missing provider answer. Formal eligibility is not strategic usefulness.

Offline preparation, without credentials or network:

```sh
python benchmarks/recommendation/run.py \
  --config benchmarks/recommendation/providers.example.json \
  --output experiments/recommendation/new-plan
python -m unittest tests.test_recommendation_benchmark -v
```

Actual pilot (only after access and an explicit budget are available):

```sh
python benchmarks/recommendation/run.py --execute \
  --config .cache/provider-config.json \
  --approved-usd-limit "$APPROVED_RESEARCH_USD_LIMIT" \
  --output experiments/recommendation/new-provider-pilot
```

Configure `RESEARCH_OPENAI_API_KEY` and `RESEARCH_ANTHROPIC_API_KEY` via managed
environment secrets. The platform reserves `OPENAI_*` target names. Conventional
`OPENAI_API_KEY` and `ANTHROPIC_API_KEY` names remain supported outside that
configuration workflow. The secrets
are read only to form authentication headers, never written into requests,
manifests or logs. Required destinations are `api.openai.com` and
`api.anthropic.com`. Official pricing documentation must also be reachable or
supplied with provenance. The configured model IDs, rates, source URL and check
date are required; no chat-subscription credentials are reused. Provider-native
sampling/reasoning options are explicit in the config and receipts; absent
options use provider defaults rather than invented identical seeds.

Before every request the runner reserves a conservative input-byte-based token
bound plus a framing allowance and the full output cap. It stops before
exceeding the approved estimate. All issued requests retain their reservation,
including timeouts or unknown usage. Observed usage outside that assumption
stops the run. Rates and this accounting are an estimate, not a provider bill.
The current prepared plan's bound fits 4,096 input tokens and 768 output tokens
per request. Raw provider usage and response identifiers are retained.

No automatic retries or model fallbacks. Reuse the exact command with `--resume`
after an interruption: an exclusive lock prevents concurrent runs; issued
requests lacking an outcome are marked interrupted and never reissued. A
different source/config/data requires a new output directory. Successful JSON
parsing, tests and a dry-run plan do not establish a real model benchmark.
