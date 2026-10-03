# Android-authored app-card prototypes

English | [简体中文](README.zh-CN.md)

The [six-family collection](collection/README.md) contains Mail, Calendar, News,
Finance, Photos and YouTube prototypes authored and revised by DeepSeek on
Android. Each provides a declarative glance card and a Splash app with glance,
expanded and full-app presentation. All 25 final files are preserved byte for byte;
strict replay matches the recorded Android model mutations.

**Reviewed prototypes, not an accepted template collection.** Independent visual
review scores the collection **4.1/5**, below the **4.5/5 A− target**. Native tests
verify local actions, selection and navigation; Photos and YouTube demonstrate
honest unavailable-media states rather than photo loading or video playback.
The collection keeps session state in memory and does not connect to live services.

The user required the phone model to author designs, source and revisions.
Supervising agents supplied references, feedback, operator tools and evidence;
they did not hand-patch the app source. L0/L1/L2 label presentation depth, not
language admission levels or permission grants.

## Explore the collection

| Family | Exported glance | Native behavior evidence |
| --- | --- | --- |
| Mail | [Capture](collection/evidence/glances/mail.png) | Archive/undo, message identity, keyboard-accessible local-demo Send |
| Calendar | [Capture](collection/evidence/glances/calendar.png) | Independent RSVP state and corrected last-row detail navigation |
| News | [Capture](collection/evidence/glances/news.png) | Save/un-save, selected story and saved collection |
| Finance | [Capture](collection/evidence/glances/finance.png) | Watch/unwatch, instrument identity and last-row detail |
| Photos | [Capture](collection/evidence/glances/photo.png) | Local saved items and metadata detail; images unavailable |
| YouTube | [Capture](collection/evidence/glances/youtube.png) | Watch-later state and metadata detail; playback unavailable |

[Collection source, results and reproduction](collection/README.md) distinguish
behavior assertions, raw geometry findings, direct visual review and render-only
glance evidence. The actual Android keyboard screenshot is included. No blanket
44-point target claim is made for exported glances.

[Source receipt](collection/source-receipt.json),
[authorship replay](collection/model-authorship-validation.json),
[reference hashes](reference-index.json) and the
[archive hash inventory](artifact-inventory.json) bind the evidence. Successful
model writes/edits are archived; provider profiles, credentials and private
reasoning are excluded. Local Studio developer admission is separate from
unrun App Hub/store checks, publisher signing and publication.

## Earlier Mail comparison

The frozen [DeepSeek round 3 versus MiniMax final round 3 comparison](COMPARISON.md)
remains separate historical evidence. Its unfinished artifacts scored 3.4/5 and
3.3/5 respectively; different tool access, conversation history and feedback mean
this is not a general model ranking or an equal-budget benchmark.

| Frozen attempt | Source receipt | Representative original capture |
| --- | --- | --- |
| DeepSeek round 3 | [Receipt](attempts/deepseek-r3/source-receipt.json) | [Wrong sender in detail](attempts/deepseek-r3/evidence/deepseek-mail-r3-no-keyboard-suite/10-second-message-detail.png) |
| MiniMax final round 3 | [Receipt](attempts/minimax-r3/source-receipt.json) | [Full-app limitation](attempts/minimax-r3/evidence/minimax-mail-r3-suite/06-full-app.png) |

The [comparison replay](model-authorship-validation.json) matches all ten archived
files. From this `android-a2app-card-templates/` directory,
`python3 validate-model-authorship.py` reruns it without a phone;
`python3 validate-model-authorship.py --case-dir collection` checks the 25 final
collection files. Reproducibility from recorded mutations does not prove the
absence of every unrecorded historical intervention. Original manifest integrity
placeholders are preserved; their authorship is not a signing attestation.

Use the [review form](REVIEW-TEMPLATE.md) for later attempts. Keep failed evidence,
return app-source corrections to the phone model and state unrun checks explicitly.
