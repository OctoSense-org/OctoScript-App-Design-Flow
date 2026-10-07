# Phone workspace reply correction

English | [简体中文](README.zh-CN.md)

On 2026-10-05 the operator tapped Mail's L1 Reply on a OnePlus 6 and the reader
stayed visible. Android `MiniMax-M3.1-Flash-Preview` viewed that capture and read
its original source: `do_reply` changed `route`, but the editor's parent only
appeared at depth 2. The model added `depth = 2` to its own function, leaving
drafts and all other app behavior intact. The operator copied exact output bytes.

[`mail.main.splash`](mail.main.splash) replaces only
[`turn-14/card-templates/mail/bundle/main.splash`](../turn-14/card-templates/mail/bundle/main.splash).
[Provenance](provenance.json) records the successful edit and both hashes.
Executed from this directory:

```sh
python3 verify.py
```

Phone build `2026100504` then showed the editor from L1, accepted text with the
keyboard, and retained it after hiding the keyboard, collapsing and reopening
the workspace. The host's nested scrolling fix is separate from the model's
route correction. Captures: [before](screenshots/reply-before.png),
[editor opened](screenshots/reply-after.png), [keyboard](screenshots/keyboard.png),
[retained draft](screenshots/retained.png).

The large fixed header/footer still leave a small editing viewport with the
keyboard, and review controls can require scrolling or hiding it. This is not a
9/10 visual sign-off. No demo Queue reply or real SMTP send was invoked, and
this test did not install a new App Hub bundle or connect a mailbox.
