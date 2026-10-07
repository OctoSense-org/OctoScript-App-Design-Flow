# Model attempt review

English | [简体中文](REVIEW-TEMPLATE.zh-CN.md)

**Blank form — no result is implied.** Copy this form when importing a real
attempt. Use “not run”, “not available” or “failed” where appropriate.

## Provenance

- Attempt ID, time and actual provider/model:
- Android device, OS, APK SHA-256, source commit, features and runtime pins:
- Family and presentation depth (L0 glance / L1 expanded / L2 full app):
- Actual language/profile and entrypoint:
- Sanitized prompt, referenced source paths/commits and SHA-256 values:
- Model transcript and file hashes; successful write/edit replay comparison:
- Retries, supervisor feedback, runtime changes and model revisions:
- Final source digest, admission result and source-preservation result:

Do not import provider settings, credentials, account data, private reasoning or
unrelated logs. Retain the tool-call and final-answer evidence needed to establish
authorship. An image filename alone does not prove the model received the image;
record the actual delivery result if available.

## Observed behavior

| Check | Expected behavior from the model's design | Native action and artifact | Result / limitation |
| --- | --- | --- | --- |
| Open each presentation depth | | | Not run |
| Move between depths; preserve entity identity | | | Not run |
| Primary action and return/back | | | Not run |
| Empty, loading, unavailable and error states | | | Not run |
| Long content, scrolling and keyboard where applicable | | | Not run |
| Persistence/reopen where applicable | | | Not run |
| Light/dark and English/Chinese where supported | | | Not run |
| Data provenance and host permission boundary | | | Not run |

Record fixture versus live data explicitly. Link original native captures and
scoped widget snapshots. State whether keyboard evidence is app-only or includes
the Android screen. Separate automated geometry checks from direct visual review.
Do not claim live mail delivery, financial transactions or video playback from a
fixture or a navigation event alone.

## Comparison and score

Compare attempts using the same brief, reference set, fixture data, device,
viewport and required actions. List differences before drawing a conclusion.
Provider failure and incomplete output remain part of the record.

| Dimension | Evidence to assess | Score / 5 |
| --- | --- | --- |
| Visual clarity | Hierarchy, readable text, contrast, spacing and original native captures | Not scored |
| Three-depth consistency | Recognizable family, stable entities and clear depth transitions | Not scored |
| Interaction | Real input, navigation, state updates and relevant restart/error behavior | Not scored |
| Runtime correctness | Actual supported APIs, admission, declared data and permissions | Not scored |
| Reproducibility | Model authorship, hashes, exact steps, failures and review artifacts | Not scored |

Score anchors: 1 unusable; 2 major gaps; 3 useful with substantial corrections;
4 core behavior works with remaining weaknesses; 4.5 meets the agreed acceptance
checks with minor limitations; 5 consistently strong with complete evidence.
The A− target is at least 4.5 in every dimension, not an average that hides a
failed dimension. Leave a dimension unscored when its required evidence is absent.

- Reviewer and reviewed artifacts:
- Decision: pending / revise / accepted for the stated scope:
- Concrete strengths and remaining issues:
- Feedback sent to the phone model and next attempt ID:
- Unverified features/platforms and publication status:
