---
name: octoscript-app-card-ux
description: Design, review, and validate OctoScript app cards in OctoSense Glance, including glance/expanded/full-app presentation, Card/Chat or Email/Chat interactions, keyboard reachability, retained state, and model-authored repair. Use for new app cards or card UX acceptance; complement the flow chosen in App Flow and its publishing gates.
---

# OctoScript App Card UX

Turn a card brief into a usable, source-bound interaction and an honest acceptance
report. Start with the person's actual task, such as changing an appointment and
reviewing the saved reply, rather than a gallery of attractive static screens.

This is a **development skill**. Installing or reading it does not provision an
OctoSense system/app agent, grant tools, or install instructions in an app bundle.

## Establish the contract

Locate the user's App Flow checkout and read its `AGENTS.md`, selected
`flows/*/FLOW.md` and `docs/MODEL-VALIDATION.md`. Use their local copies; the
[repository](https://github.com/OctoSense-org/OctoSense-App-Flow) provides
fallback references if no checkout was supplied. Keep the flow's admission,
visual-review and publishing requirements; this skill supplements them.

Record the requested card families, platforms, author/model, permitted test
surface, real versus fictional data, persistence needs and quality target.
Use information already provided. Ask only for missing details that affect the
work. A single-card request does not require a six-family or two-model benchmark.
Do not hard-code a provider, device, account, source limit or historical score.

Separate two concepts: **L0/L1/L2 presentation** means glance, expanded actionable
card and full-app experience; **Octoscript L0** is the `.card` language. Splash
`.splash` is a different language. Check the pinned parser, host and granted APIs.
Read [host checks](references/host-checks.md) for Glance integration or suspected
runtime failures; an app source change cannot manufacture a missing host feature.

## Design one complete task

Use [acceptance criteria](references/acceptance.md) to specify the target journey
before implementation. Reuse the requested A2App templates when available and
compatible, preserving their source attribution; do not substitute a different
design workflow for the user's chosen one.

- Make the glance summary answer what happened, why it matters and the next
  useful action. Expansion keeps the same item and its state.
- On a host with resident workspaces, let the shell expand the card into usable
  app space. Keep unrelated Glance cards out of the active interaction area.
- Group related actions near the content they affect. Keep one clear primary
  action and understandable return/collapse behavior; avoid redundant tab rows.
- When chat can modify content, chat, direct editing and review must observe the
  same authoritative saved state. Prove that a requested change appears in the
  editable content and final review. An assistant saying “updated” is insufficient.
- Build the non-AI path and applicable unavailable/denied states. A card without
  a declared app agent must not gain a fabricated Chat tab or tool privileges.

First complete one vertical slice: open the summary, perform the main task,
review the observed result, collapse and return. Extend the pattern only after
this works. For a design-only assignment, deliver the contract and explicitly
leave runtime acceptance unverified.

## Exercise, inspect, repair

Choose supported tools using `docs/MODEL-VALIDATION.md` and
`flows/core/NATIVE-INSTRUMENT.md` in the checkout. Prefer an owned hidden native
instance for desktop iteration. Test actual phone keyboard, notifications and
lifecycle on an assigned device when required. Label ADB/platform captures,
Studio app-texture captures and Makepad geometry tests separately. A rendered
L0 PNG does not prove exported-card input or a shell transition.

Run relevant criteria from [acceptance](references/acceptance.md), capturing
actual pixels and resulting state. Inspect full strings and visible controls;
OCR and widget text alone can miss clipping. Keep dependent open/input/inspect/
close operations sequential. Wait for observable state, not just a successful
open call, and verify the focused package and intended item before input.

For designated model-authored work, the reviewer may write test harnesses and
feedback but returns card/app source repairs to that author. Supply the exact
source identity, original screenshot, input sequence, expected/observed result
and smallest affected behavior. Verify the model received the actual image if
visual understanding is required. Import exact returned bytes and preserve the
successful mutations and provider attribution; do not hand-edit the result and
call it model-authored. Otherwise follow the project's normal authorship rules.

After a repair, rerun affected behavior and dependent paths on the new source.
Keep failed attempts and corrected follow-ups separate. Diagnose repeated failures
without new evidence instead of repeatedly requesting broad rewrites. For an
external action with an uncertain outcome, check its recorded state before any
retry. Use only existing authorization and the host's actual approval path.

## Deliver a reviewable result

Use the [evidence format](references/evidence.md). Report functional outcomes,
visual findings, performance and external business effects separately. A passed
local Save/Reply/Watch control is not evidence of a remote action. A numeric score
cannot override a blocked task, unreadable content or inaccessible input.

Include exact source/build receipts, original captures, who authored/drove/
reviewed the run, remaining issues and unverified scope. Distinguish “checks
executed” from “all requirements passed”; do not reuse an old 4.5/5 or 9/10 grade.
Stop owned test instances and restore only temporary settings changed for the
run. Follow the selected flow for any requested submission or publication.
