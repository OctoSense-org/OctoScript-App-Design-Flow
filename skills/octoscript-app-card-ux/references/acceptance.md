# Card acceptance criteria

Apply rows relevant to the requested product. Mark each **pass**, **fail**,
**unverified**, or **not applicable with a reason**. Record source/build and
fixture identity with each run. Missing device access leaves phone checks
unverified; it does not turn a desktop result into a phone pass.

## Presentation and interaction

| Area | Exercise | Evidence needed |
| --- | --- | --- |
| Summary and expansion | Open the compact summary, expand, reach the full task, collapse and reopen | The same item and selection remain; the transition exposes usable space without an unintended app launch. Unrelated feed cards do not occupy the active workspace. |
| Action grouping | Read the content, find the primary action, perform it and return | Related controls stay together; avoid scattering Details/Reply/Chat across competing rows. Labels and primary/secondary emphasis match the task. |
| Native input | Focus every required editor, type a distinctive value, move focus, hide/show keyboard | Editor, caret and needed actions are reachable. Scroll nested containers and bottom content; neither keyboard nor feed overlays block input. |
| Shared editing state | Ask for a distinct change through chat, inspect saved state, switch to editor/review; edit directly and return to chat | Exact requested value, item identity and revision agree. Stale generated copy or an assistant's confirmation cannot substitute for a saved result. |
| Local retention | Make a choice or leave unsent input, visit other workspaces, then reopen | Local state and unsent input survive as specified. Exercise beyond the host's actual clean-workspace cache capacity. Test process restart separately if durability is promised. |
| Lists and identity | Open second and last items, filter, scroll to the end, return | Correct detail and independent state; no accidental jump to a different item or stale scroll offset. |
| States | Exercise implemented loading/empty/error/retry and unavailable/denied-agent paths | The state actually occurs and offers an appropriate next step. A demo state selector tests its presentation, not a real network failure. |
| Text and targets | Use long titles, dates, locations, explanations, signed values and requested languages | Full essential content is readable in pixels. Check logical-point target bounds and platform/project requirements, not just screenshot pixel dimensions. |
| Appearance | Exercise promised light/dark styles and relevant device widths | Contrast, wrapping, focus and selected states work. A white model surface in a dark host is readable contrast at most, not proof of adaptive dark design. |
| Access needs | Exercise requested language, font scaling, orientation and assistive input | Record exactly what ran; ordinary portrait screenshots do not establish accessibility or full localization. |

For an email approval task, include a concrete round trip: change an appointment
time in Chat, verify that exact time in the saved draft, switch to Email/Edit,
make another edit, return to Chat, then review the saved recipient/subject/body.
Sending is a separate host-approved business action. If it is not authorized or
not executed, retain the draft and mark delivery unverified.

## Performance

Measure the user's troublesome path: feed scrolling, summary expansion,
workspace switching, or typing with the keyboard. Use the agreed budget and
record device, build, dataset size, gesture sequence and sample count.

Distinguish CPU frame markers from actual presented frames and from a verified
input-to-visible-content response. Keep gesture/active-span boundaries and
idle-inclusive statistics available. ADB waits between gestures are not continuous
scrolling stalls; excluding them must be explained, not silently applied. Include
p50, p95, maximum and missed-frame/outlier counts when the tool supplies them.
Explicitly say whether post-release fling was measured. A small sample supports
that scenario, not an overall performance guarantee.

## Review and scoring

Judge these dimensions separately: task clarity/action grouping, content
legibility, keyboard/editing comfort, state continuity, motion/responsiveness,
and visual consistency. Cite the capture or observation behind each finding.
Preserve the requested rubric; if no score was requested, verdicts and issues
are sufficient. Identify whether the reviewer is the author, another agent or a
human. Honor a flow's human visual-approval checkpoint without inventing approval.

If a numerical assessment is requested, use explicit anchors: a blocked core task
cannot pass; usable but awkward behavior still needs work; polished behavior must
survive the relevant states, sizes and repeated journey. A 9/10 assessment needs
that evidence and no unresolved critical interaction/readability defect. Do not
average away a hidden composer, wrong saved reply, or clipped essential content.
The report must distinguish scoped acceptance with caveats from release sign-off.
