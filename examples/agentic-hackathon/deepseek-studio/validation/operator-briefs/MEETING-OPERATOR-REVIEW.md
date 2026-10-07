# Meeting Planner source review before normal-host validation
Source currently generated/meeting-planner/bundle/main.splash (~15702bytes).
1. Same deletion bug as independently reproduced in Email: delete bookings[key] cannot be trusted. Rebuild the object excluding the intended entry using supported iteration. Verify receipt disappears and state no longer has it; keep busy fixtures.
2. confirm() only checks has(bookings,key), permitting this single Design review to be booked at BOTH14:00 and15:30. Requirement says ONE booking; block any second booking until explicit Undo, regardless of selected slot.
3. Blank question writes notice only in home while Q&A is full view. Make validation visible next to qinput.
4. Full view is a fixed View; busy-event prose, keyboard, model answers and receipt will overflow. Use one scrollable full view; Stop and Back remain reachable even for a long answer. Home heading Meeting Planner plus Demo data must fit at phone width without clipping.
5. Peer workspace is already accounts/device. Prompts should ask read_file calendar.json/state.json, not accounts/device/calendar.json. Apply same basename fix to Email's inbox/state prompt.
6. Add clearly labeled Reset demo to restore fake fixture and remove local demo booking/conflicts. Block or invalidate any in-flight response. This enables repeating All busy scenario without app-data injection.
7. After snapshot review a conflict change must still be rechecked at confirm; keep your passing late-conflict behavior. Model prose remains proposal-only.
Make source repairs yourself. Operator will independently exercise persistent normal-host behavior and live provider. No operator edits to generated main.splash.
