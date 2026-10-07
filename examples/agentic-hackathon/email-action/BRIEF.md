# Email Action

A contestant reference using the script-app and model-validation flows.
Three fictional messages: a school permission request, a meeting request,
and a newsletter. Keep sender, message identity and source text visible.

The person opens an action card, reviews/edits a draft and confirms delivery
into a local demo outbox. Never send email or connect a real account. Mark
and undo affect only the selected message. Persist drafts, handled state,
outbox and an activity record across restart.

The Agent tab calls the app's own octos conversation over fake data. The agent
answers questions and drafts a reply; no model response is evaluated as code
or sends anything. A labeled sample suggestion works without a provider.
Cover busy, unavailable, blank input, duplicate delivery and empty filters.

Capabilities: storage for account-scoped fixtures/state; octos.turn.start
for conversation and drafts; octos.turn.interrupt for Stop. No network,
Mail or Calendar service access. Fictional data can reach the configured
provider when the person asks the agent.

Validate desktop native rendering and input, second-message identity, edited
replies, duplicate prevention, undo and restart, then Android. Record real
agent validation separately from the offline walkthrough.
