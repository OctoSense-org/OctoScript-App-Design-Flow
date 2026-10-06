Robrix2 widgets for the Octoscript image-to-app pipeline

2026-09-16 · Local source assessment. No widgets were ported, no dependency pins were changed, and no Robrix or Signal app was built or launched. Compatibility and performance still require native tests.

The inspected Robrix2 checkout has origin `https://github.com/Project-Robius-China/robrix2` and inspected commit `7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8`. Its tracked working tree was clean. This is the checkout named `robrix`, not a missing directory named `robrix2`.

Recommendation: extract a small protocol-neutral chat widget module into Octoscript-Makepad. Start with unread badges, typing indicators, avatars and conversation rows, then add a virtual timeline and composer. Robrix's interaction and state-management code is more valuable than copying entire Matrix screens. Keep the image atlas responsible for the new app's appearance and use extracted native widgets for behavior.

| Local component | Useful behavior | Extraction work |
| --- | --- | --- |
| [UnreadBadge](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/shared/unread_badge.rs) | Unread dot, mention marker, count and `99+` | Low coupling: Makepad-only Rust imports; adapt shared text/color tokens and verify updates in recycled rows. |
| [BouncingDots](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/shared/bouncing_dots.rs) | Animated typing indicator | Low coupling: expose active/inactive state; stop animation when hidden or unmounted. |
| [JumpToBottomButton](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/shared/jump_to_bottom_button.rs) | Unread count and smooth return to the latest messages | Low coupling: replace `RobrixIconButton`, icon/resource references and style tokens; wire to our PortalList and unread state. |
| [Timestamp](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/shared/timestamp.rs), [ProgressBar](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/shared/progress_bar.rs) | Detailed timestamp tooltip; attachment progress | Small native helpers. Timestamp also uses chrono and has locale-specific formatting; accept localized display data. ProgressBar uses runtime shader updates that need verification on the pinned framework. |
| [Avatar](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/shared/avatar.rs) | Circular image or text fallback | Medium: preserve drawing, remove Matrix user/room IDs, profile navigation and avatar caches. Supply neutral identity and image data. |
| [RoomsListEntry](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/home/rooms_list_entry.rs) | Avatar/title/preview/time/unread row, selection, responsive variants, secondary actions | Medium: replace `OwnedRoomId`, `RoomsListScopeProps` and app-global dependencies with a conversation model and typed actions. |
| [CommandTextInput](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/shared/command_text_input.rs) | Generic trigger-based suggestion popup, keyboard selection, focus handling | Useful composer foundation. Rust imports are Makepad and unicode-segmentation; preserve native TextInput access and IME state. Do not copy the much more coupled MentionableTextInput wrapper. |
| [RoomScreen](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/home/room_screen/mod.rs), [message templates](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/home/room_screen/dsl.rs), [Message](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/home/room_screen/message.rs) | Virtual timeline, message layout, date dividers, selection, replies, receipts and scroll restoration | High coupling: extract templates/controller patterns, not the whole screen. Replace Matrix timeline items, request dispatch, IDs and caches. |
| [ImageViewer](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/shared/image_viewer.rs) | Image preview, zoom/pan and loading states | Later: retain presentation and gestures; replace Matrix event metadata, media downloads and cache ownership with local media handles. |
| [RoomInputBar](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/room/room_input_bar.rs), [MentionableTextInput](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/shared/mentionable_text_input.rs) | Reply/edit/attachment composition and member suggestions | High coupling: use as behavior references. Rebuild a smaller composer around neutral state; do not import Matrix power levels, room membership or request handling. |
| [Audio player](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/shared/audio_message_player.rs), [video player](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/shared/video_message_player.rs), [HtmlOrPlaintext](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/shared/html_or_plaintext.rs) | Media playback and selectable rich message content | Later: separate local media/text presentation from Matrix sources, links and caches. Playback widgets do not implement Signal calls. Plain/selectable text is sufficient for the first messaging milestone. |

The inspected [library root](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/src/lib.rs) exposes an application, including Matrix sync, account management and caches. It does not offer an isolated widgets-only crate/feature. Adding the entire `robrix` crate as a dependency would bring those dependencies into the consumer.

There is also a real framework-version boundary. Robrix's [Cargo patches](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/Cargo.toml) resolve Makepad to `ZhangHanDong/makepad` revision `1dd8d372cfb65b20160a3782586ed4d593cf8193`, confirmed in its lockfile. Our [Octoscript-Makepad runtime manifest](../../octoscript-makepad/runtime.json) pins `OctoSense-org/makepad` at `d4502ef1e4d196d2829a07aa137740cb0581e9b4`. Both use Makepad 2 `script_mod!`, but that does not establish compatibility. Adapt extracted code to the existing shared pin; do not switch the application to Robrix's fork or introduce a second Makepad graph. Cargo patches in a dependency also do not replace the consuming workspace's dependency policy.

The basic virtual-list implementation is already available in our [pinned Makepad PortalList](../../makepad/widgets/src/portal_list.rs). It exposes `ReachedStart`, `ReachedEnd`, `is_at_end`, `set_first_id_and_scroll` and `smooth_scroll_to_end`. The useful Robrix contribution is the surrounding chat behavior: saving/restoring per-conversation UI state, choosing when to follow new messages and keeping message state outside recycled row instances. No framework fork switch is needed merely to obtain a virtual list.

For a new timeline controller, use stable message IDs and a visible-message/pixel-offset anchor. Resolve the anchor to the current PortalList index after prepending history, deleting messages or updating search results. Robrix's saved index plus scroll offset is useful implementation evidence, but an index alone is not a stable identifier after the dataset changes. Follow incoming messages only when already at the bottom; otherwise retain the reading position and update the jump badge. Reset every recycled row's identity, selection, media and receipt state when rebinding it.

The image-to-app integration needs changes in both repositories:

| Existing integration point | Required addition |
| --- | --- |
| [Semantic annotation](../lab/core/semantic_widgets.py) and the scene's reviewed semantic map | Explicit chat component boundaries and native child bindings. Do not assume names in an image or a Robrix screen automatically become semantic components. |
| [Recipe exporter](../lab/sketch-to-appcard/export_app_recipes.py) | Recognize proposed chat recipe kinds, preserve source IDs and retain inspectable text/input/button children. |
| [Native design translator](../../octoscript-makepad/crates/octoscript-makepad/src/design.rs) | Extend `kit_contract` validation for each supported chat kind, including required parts and dynamic row bindings. |
| [Native kit registration and actions](../../octoscript-makepad/crates/octoscript-widgets/src/kit_shared.rs) | Register extracted widgets, bind neutral data/actions, preserve text/focus/selection, and clean up popups/animations on unmount. |
| [Semantic interaction checks](../lab/core/semantic_interactions.py) and built-in native instrument evidence | Exercise the new components through real native inputs and verify their resulting public state and layout. |

The translator currently accepts exactly `KitButton`, `KitFormField`, `KitTabBar`, `KitBottomNavigation`, `TaskplanProjectCard` and `CamoTrackRow`. A contract naming `ChatTimeline` or `RobrixAvatar` currently returns `unknown semantic native widget`. Registering a widget's `script_mod` alone is therefore insufficient for this pipeline. Small decorative helpers can initially be internal parts of a chat composite instead of becoming separate public contract kinds.

The existing binding rules require native Button/Radio children for `control`, native TextInput for `input`, and stable IDs on the selected child paths. Preserve those guarantees when extending the contract; do not turn the chat screen into one opaque painted widget.

One concrete composer trap: `CommandTextInput` implements `Widget::text()` by returning an empty string, while its typed `text_input_ref().text()` reads the actual draft. Our existing kit controller reads text from its bound content widget. Binding it to the unchanged wrapper would lose the draft value. Bind to the native child or implement an explicit composer adapter; preserve the instance, caret and IME composition during updates instead of rebuilding the entire input for every keystroke.

Suggested ownership and interfaces below are proposals, not directories or APIs already implemented:

```text
octosense-org/
  octoscript-makepad/
    crates/octoscript-widgets/src/chat/   # shared rendering, gestures, UI state
    crates/octoscript-makepad/           # contract validation and translation
  Octosense-Service-AppCards/
    apps/signal/                        # atlas, scene contracts, reducer, native app
    lab/                                # pipeline mappings and validation tools
```

Keep the shared module free of Matrix and Signal dependencies. For example, `ConversationRowModel` can contain an opaque conversation ID, title, preview, formatted time, avatar handle and unread state. `MessageRowModel` can contain an opaque message ID, direction, body, reply preview, attachment handles and delivery state. Composer state owns the draft and reply target. Typed UI actions such as `OpenConversation(id)`, `SendDraft`, `LoadOlder(before_id)`, `OpenAttachment(id)` and `JumpToLatest` go to the app controller; protocol requests and media fetching remain in the app's worker. Network/database work must not run inside widget event or draw methods.

Implement in these increments:

1. Extract the small helpers, Avatar and ConversationRow into Octoscript-Makepad. Build them against its existing Makepad pin with fictional fixtures and preserve MIT provenance for copied code.
2. Expose a reviewed `ChatConversationRow` semantic contract and prove an atlas → mapped scene → L0 → native row path. Keep geometry, text and colors derived from the approved design rather than inheriting Robrix's theme wholesale.
3. Add `ChatComposer` and `ChatTimeline`, using the existing PortalList. Prove long variable-height threads, history prepend anchoring, per-conversation drafts, incoming-message behavior and input handling before connecting a service.
4. Bind the Signal adapter described in [the feasibility report](signal-app-feasibility.md). UI reuse does not establish Signal interoperability, protocol security, background delivery or backend licensing compatibility.
5. Promote the validated Octoscript-Makepad revision through the existing runtime-lock workflow so all consuming apps use the same framework revision.

Required native checks for an implementation:

- Long fictional conversations with mixed short/long messages, CJK and emoji; verify that mounted row count stays bounded as history grows. Record measurements rather than assuming Robrix's source proves performance.
- Prepending history retains the visible message and offset; new messages while scrolled up do not pull the user to the bottom; jump-to-latest clears the correct unread state.
- Composer draft, cursor and selection survive receipt/list updates and navigation; Android IME composition, keyboard resizing, suggestion selection and send actions work without duplicate submission.
- Row recycling does not leak a previous conversation's avatar, unread state, message selection or attachment; reused shader/Animator state updates on the shared Makepad pin.
- Run an owned release instance using the [built-in native instrument procedure](../lab/core/NATIVE-INSTRUMENT.md), with a hidden native GPU window on macOS when needed. Do not adopt Robrix's older Studio harness. Use the documented Android device procedure and app-owned capture; desktop tests alone do not prove phone behavior.

Robrix declares MIT in [Cargo.toml](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/Cargo.toml), and its [LICENSE-MIT](https://github.com/Project-Robius-China/robrix2/blob/7ddd84d2c7057fde3139f240c9d2ecb8eb40cab8/LICENSE-MIT) requires preserving the copyright and license notice in copies or substantial portions. Retain the full MIT text and original attribution with extracted code, record the source commit and local modifications, and check separately any copied fonts/icons/assets and third-party code. The original Apache-2.0 notices of our repositories do not replace these upstream notices. The separate Signal dependency questions remain as recorded in the feasibility report.

This investigation checked source and local dependency declarations only. It establishes a practical extraction path, not a completed ChatKit or a tested Signal client.
