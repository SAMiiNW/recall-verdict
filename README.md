# Recall Verdict
### From conflicting notices to a lot-specific decision

A recall is not simply a product-name match. A regulator may name one batch and one market while a manufacturer describes a wider issue. Recall Verdict keeps the product, lot and region alongside the documents used to reach a decision.

## Follow a case
1. Call `open_case(i, product, lot, region, sources)`. Supply at least two distinct HTTPS URLs; the contract considers up to five.
2. Call `adjudicate(i)` while the case is OPEN. This call is permissionless.
3. Read `get_case(i)` for the frozen request and digests, then `get_verdict(i)` for the ruling. `list_cases()` exposes recorded cases.

IDs are trimmed, uppercased and bounded. Reusing a normalized ID or adjudicating a FINAL case is rejected.

## What the ruling means
| Action | Intended interpretation |
| --- | --- |
| RECALL | The submitted evidence supports recalling the specified lot. |
| HOLD | Pause and investigate before deciding. |
| CLEAR | The submitted records support clearing this case; not a universal safety certification. |
| INSUFFICIENT | The evidence does not establish a substantive ruling. |

Affected lots, conflicting source indexes, rationale and model-reported confidence accompany the action. Confidence is not a calibrated probability.

## Under the decision
A leader fetches the bounded document bodies and proposes a ruling. Validators refetch the same URLs, compare SHA-256 digests and independently assess the action, affected lots and conflicts. State is written after the nondeterministic consensus call returns.

The digest covers the first 12,000 body units processed, not an arbitrarily large complete document. Distinct URLs do not establish independent publishers, and the HTTPS check does not authenticate a regulator.

## Try the included case

### Reproduce a lot-specific ruling

Start with [the two notice fixtures](casebook/notices/), then read [the case test](checks/direct/test_contract.py). Its useful checks are preservation of source ordering, normalized duplicate IDs, rejection of a forged digest order and refusal to adjudicate twice.

Install the development dependencies with `python -m pip install -r requirements-dev.txt`. Run `python -m pytest checks/direct -q`, then `genvm-lint src/recall.py`. The direct suite uses mocked notices and model responses, not live regulator data.

For a network case, inspect [tools/smoke.py](tools/smoke.py): it opens a new reference, attempts a duplicate and reads back the final ruling. This workspace helper requires the untracked `accounts.env` four directories above the repository and selects account 1. Adapt that credential lookup before using a standalone clone; never publish keys. The script submits transactions and writes a new smoke record.

The original source and fixture commits are preserved in [casebook/deployment.json](casebook/deployment.json). A successful fixture run is evidence of that execution, not a claim that every real-world notice is handled correctly.

The synthetic Northwind Kettle fixture names lot NK-442 in Morocco. The recorded network run returned RECALL. It demonstrates contract execution against repository-hosted fixtures, not a real-world recall investigation.

[Contract source](src/recall.py) · [Direct tests](checks/direct/test_contract.py) · [Recorded case](casebook/network-run.json)

## Boundaries
There is no issuer allowlist, freshness deadline or appeal transition. Malformed model output or unavailable evidence may fail execution rather than produce INSUFFICIENT. Rationale and confidence are not independently bound by the custom validator. Do not use the result as a substitute for an official safety notice.

Deployment and network-run files are generated after execution; use the paths referenced above to inspect the current evidence.
