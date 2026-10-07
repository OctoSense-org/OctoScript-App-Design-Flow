# Evidence and model feedback

Use the project's existing report format when available. The following is a
minimal record, not an automatic pass generator. Store public fictional-data
captures outside runnable bundle source; keep personal-account evidence private.
A masked UI field can still leak through a native snapshot or log.

## Run receipt

Record:

- Task/scope, app or publisher identity, presentation depth and source language.
- Source/manifest/fixture hashes, host revision, local runtime patch or source
  hashes when dirty, binary/APK hash and version, device/viewport/theme.
- Fictional versus real-service data; authoring provider/model and fallback
  behavior for model-authored work. No provider profiles, tokens or private reasoning.
- Who authored source, injected input and reviewed pixels; exact tool surface.
- For each case: precondition, input, expected result, observed UI and saved state,
  verdict, original capture path/hash, and relevant log or native geometry evidence.
- First failure and each correction as separate runs; which source revision each
  capture proves. Do not relabel old captures as evidence of new source.
- Unverified/not-applicable scope, unresolved issues, visual judgment and cleanup.

A compact case table can be:

| Case | Source/build | Input | Expected / observed | Verdict | Evidence |
| --- | --- | --- | --- | --- | --- |
| Descriptive task id | Hashes or run receipt | Reproducible sequence | State and pixels, not just a tool success flag | pass / fail / unverified / not applicable with reason | Original PNG and state/geometry receipt |

Keep separate conclusions for local UI behavior, real model/agent execution,
event-triggered operation, external action/delivery, and product visual approval.
For example, sending a fixture to a card renderer does not prove an incoming email
triggered the agent or that a reply was sent. A model-turn test must record actual
provider attribution and observed tools/results, not only the configured model.

## Focused repair request

```text
Author and environment: use the designated model/tool host; no silent fallback.
Artifact: exact source receipt and host build.
Starting state and input: reproducible item, route, selection and actions.
Expected: what the person must be able to see or accomplish.
Observed: actual mismatch, with original screenshot and state/geometry evidence.
Repair boundary: smallest relevant behavior; preserve data, working actions,
identities and constraints. Distinguish app source from a suspected host defect.
Retest: affected journey plus dependent behavior, including keyboard or return
state when relevant. Report changed files and unresolved issues, not a grade.
```

For image review, prove delivery of the captured image through the provider's
supported input path; a filename, successful PNG save or widget dump is not proof
that the model saw pixels. Preserve the original source and successful edit/write
records so the returned bytes can be compared or replayed without local repair.

For repeated failures, first distinguish a bad selector, intermediate capture,
wrong focused package, hidden parent view, denied tool and actual source/runtime
error. Keep the failed evidence and record why the follow-up differs. Do not lower
assertions, invent evidence, or expand permissions to manufacture acceptance.
