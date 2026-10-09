# Development review

English | [简体中文](REVIEW.zh-CN.md)

Author self-review of the native-tested fixture, not Hub administrator approval.
The `hub scan` packet is generated outside the bundle.

1. **Claim:** the title is “API Migration Lab”; the UI says “AI is optional”.
   `keep`, `generate`, `publish` and `withdraw` in `bundle/main.splash` implement
   the offered actions. Missing services produce explicit messages, not success.
2. **Platform/category:** macOS is the only claimed platform; this is a
   productivity/developer example. Native behavior was exercised there.
3. **Permissions:** `storage` saves the draft, `model` requests an optional
   summary, `glance` publishes/withdraws the reviewed card. There are no direct
   network hosts, unused account grants, credentials or background tasks.
4. **Imitation:** ordinary editor controls; no login, payment or approval sheet.
5. **Model instructions:** the fixed `task` string is intentional application
   logic. User text is passed separately in `input`; it is not concatenated
   into instructions. No external content is fetched.
6. **Content:** synthetic walk-planning text, with no private individual targeted.
7. **Route:** suitable as a development example with stated limits. Public
   publication remains a separate human review; successful inference and Glance
   publication are unverified, and no release/platform approval is claimed.
