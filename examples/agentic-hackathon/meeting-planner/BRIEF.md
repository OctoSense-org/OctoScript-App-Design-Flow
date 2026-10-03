# Meeting Planner

A 30-minute design review for Alex, Maya and Jordan on Monday 5 October 2026,
all in UTC. Use fictional calendars only. Show busy events and candidate
slots, explain conflicts, review the exact invitation and commit to a local
demo calendar only after confirmation. Recheck availability at commit.
Repeated confirmation never duplicates a booking. Undo removes only this
booking; reset restores the fixture. Keep state across restart.

The real app agent can read the fake calendar and recommend times or answer
questions. Its prose never bypasses the app's interval checks. A labeled
offline calculation finds the first available slot without calling a model.
Show provider absence, blank questions, busy state, conflicting slots,
changed availability, no available times and a persistent action receipt.

Capabilities: storage, octos.turn.start and octos.turn.interrupt. No network,
Mail or Calendar service permissions. Test native desktop input/rendering
first, then Android. Live model delivery and offline behavior are distinct.
