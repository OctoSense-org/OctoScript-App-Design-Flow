# Check the host before changing card source

Read the actual OctoSense checkout and its runtime pins, or the exact source
revision behind the installed build. App Flow's standalone renderer and
a phone build may expose different capabilities. Route host changes to their
own repository; preserve the generated program instead of rewriting it around
a host layout defect. Continue only work already authorized in that repository.

| Symptom | Check in the target host | Card-side check |
| --- | --- | --- |
| Full app is blank | `crates/shell/src/glance_card.rs`: a Splash `Fill` root needs a nonzero workspace viewport; natural-height content needs an appropriate scroller | Successful admission is not a populated first frame. Confirm initialization and source language before changing layout. |
| Larger full program is rejected | `crates/shell/src/glance.rs`: installed `SOURCE_MAX` and any separate `SCRIPT_MAX`; capture the real admission error | Do not assume `.card` and `.splash` share a limit, or increase limits merely to make a test pass. |
| Editor disappears with keyboard | `glance_card.rs` and `glance_sheet.rs`: final viewport, focus, nested scroll ancestors and action visibility | Check inner scrolling, fixed headers/footers and whether the editor's parent page is visible. Hiding the keyboard is not a substitute for typing comfortably. |
| Chat says it changed a reply but review is stale | `mail_review.rs`, `glance_chat.rs`, `apps/mail/host-service/src/drafts.rs` and the bound draft/account/revision | Review must read authoritative state, not a separate generated text copy. A local demo editor is not a host Mail draft. |
| Card Chat has the wrong powers | Publisher identity/account, consent, declared app agent and `ContextKind` in the host | Generic Card context is not a Mail draft-edit lease. A declared tool still needs admission, grants and a real executable handler. |
| Choosing Reply shows nothing | Inspect parent depth/page visibility as well as the child route | Activating a child editor while its parent remains hidden does not open the reply view. |
| Text is complete in inspection but clipped on screen | Actual ink, viewport, inherited style and target device scale | Bound long captions so they wrap; size navigation for labels, selected markers, padding and spacing without sacrificing usable targets. |
| Collapse loses edits | Retained workspace identity and dirty-state/cache policy | Distinguish collapse/reopen from process restart and saved business state. |
| Phone model cannot connect | Foreground/lock state, allowed network access and provider error receipt | Waking a permitted test device and returning the test app to foreground may resolve background restrictions. Do not change model source or silently switch provider. Do not bypass an OS restriction. |

Use the source files that exist in the selected revision; paths above are
navigation hints, not a promise about every future release.

## Runtime contracts worth preserving

- A host workspace supplies the transition out of the Glance feed. It should not
  depend on a generated card launching the full native app to gain screen space.
- Keep the original publication's account and item binding. Local state supplied
  to an agent is context, not authority, an approval, or proof of a backend effect.
- Use existing host-owned Card/Chat or Email/Chat integration where supported;
  avoid adding a second, disconnected assistant UI inside generated source.
- Mail's reviewed host path requires a physical human approval of the exact saved
  message. ADB, Studio synthetic input, model output or developer mode must not
  be represented as that approval. Check current platform support.
- A native geometry test establishes layout invariants. App-texture inspection
  establishes app pixels. A platform screenshot can establish keyboard/notification
  overlap. None alone establishes an end-to-end model-triggered business action.

## Dated evidence, not prerequisites or reusable grades

The 2026-10-05 [OctoSense acceptance change](https://github.com/OctoSense-org/OctoSense/pull/334)
records 33 input configurations on an isolated OnePlus 6 package. Its
[source-bound report](https://github.com/OctoSense-org/OctoSense/blob/1cf112d4425d7fbe81d6a7fda9969b10de8f736e/docs/testing/all-card-ux-2026-10-05/README.md)
separates rendering/local actions from business integration and does not sign off
9/10 production UX. Check merge and installed-build status before relying on fixes.
The test counts, device, old source limits and scores are not future acceptance gates.

Android authors corrected their own sources in the
[template archive](https://github.com/OctoSense-org/OctoSense-App-Flow/pull/146):
[DeepSeek receipts](https://github.com/OctoSense-org/OctoSense-App-Flow/blob/3d07d3a96626b5ff6dffdcb0d391b6de0a483728/examples/android-a2app-card-templates/continuations/deepseek/workspace-ux-20261005/provenance.json)
and [MiniMax receipts](https://github.com/OctoSense-org/OctoSense-App-Flow/blob/3d07d3a96626b5ff6dffdcb0d391b6de0a483728/examples/android-a2app-card-templates/continuations/minimax/workspace-ux-20261005/provenance.json)
show hashes and successful mutations. Use comparable provenance when requested;
these collections are examples, not mandatory dependencies or published apps.
