# Publishing an OctoSense app to the App Hub

This is the step-by-step path from a working bundle to a submission. It is
written so a coding agent can run it top to bottom and stop exactly where a
person must act. The contract itself belongs to the App Hub
([OctoSense-App-Hub `docs/PUBLISHING.md`](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md));
this page applies it to script apps and records what was verified.

Every command below was run on macOS against App Hub `79a2c4f` (the branch
that merged to `main` as OctoSense-App-Hub#4), then again on App Hub `main`
(`6c075d0`) on 2026-09-26 with a new app and throwaway keys, unless a step is
marked **unverified**. Outputs are quoted verbatim.

- Start here only when [QUICKSTART](QUICKSTART.md) steps 1–6 pass: the app
  runs in `card-host`, and you tested its interactions.
- **HUMAN** marks a checkpoint an agent must not pass on its own: private keys,
  the publisher identity, and the submission. An agent stops, reports, and waits.

## 1. What gets published

Only `bundle/`. Everything else in the app repository (AGENTS.md, notes, tools,
keys, logs, `.local-state/`, `build/review.json`) stays outside it.

```text
my-app/
  AGENTS.md  README.md  .gitignore        not submitted
  build/review.json                      not submitted (hub scan output)
  .local-state/                          not submitted (card-host jail)
  bundle/                                THE SUBMISSION
    manifest.json      id, version, name, integrity, capabilities, hosts
    listing.json       what the store shows
    main.splash        the program (a card app has page.card + kit/ instead)
    assets/icon.svg    the icon the listing names (PNG or SVG, square)
    screenshots/01-main.png   real captures, PNG, 1 to 8, named by the listing
```

## 2. The rules the gate enforces

`hub check` (`crates/app-hub/src/gate.rs`) is the same code the hub runs. A
`[refused]` line means not admitted; a `[warning]` line is admitted but shown
to the reviewer.

| Check name in the output | What is refused |
| --- | --- |
| `identity` | An id under `os.`: `os.probe is under os., which is reserved for system apps that ship with the device`. |
| `digest` | `integrity.bundle_blake3` does not match the bytes. Run `hub stamp` after every change. |
| `publisher-signature` | A signature that does not verify, or a signed bundle checked without `--publisher-key`. Unsigned is only a warning under `--allow-unsigned`. |
| `contents` | A file whose extension is not one of `.card .json .l0 .octoscript .splash .svg .png .jpg .jpeg .webp .ttf .otf .txt .md`. No scripts, archives, binaries. Any symlink aborts the check. |
| `size` | A bundle over 8 MB (8 388 608 bytes). |
| `assets` | In `.splash`: any `http://`, `file://` or `../`; any `https://<host>` whose host is not in `network.hosts`, unless the app is granted `images` or `web` (then any public https host). In `.card .json .l0 .octoscript .txt .md` other than the manifest and listing: any `http://`, `https://`, `file://` or `../`. |
| `secrets` | A `.splash .card .l0 .octoscript` file declaring `is_password: true`, `TextInputContentType.Password`, `NewPassword` or `OneTimeCode`. Apps never collect secrets; see [HOST-SERVICES](HOST-SERVICES.md). |
| `listing` | No `listing.json`; a listing that does not parse (unknown field, category, platform or age rating; non-https privacy policy; description empty or over 4000 characters; subtitle over 80; over 10 keywords; over 8 screenshots; an asset that is not a plain relative `.png`/`.svg` path); no icon; no screenshot; a named icon or screenshot missing from the bundle. |
| `policy` | Unknown capability; host with a scheme, path, port, wildcard or bad character; hosts without `net`; id not `[a-z0-9.-]{1,64}` or starting with `.` or containing `..`; empty version; an agent tool the host does not offer. |
| `version` | (with `--catalog`) this id and version are already in the catalog. |
| `continuity` | (with `--catalog`) the id is already published and this version is unsigned or signed by a different key. |

Parse errors stop before the report, for example
`hub: manifest is not valid: unknown field ...`.

Not checked by the gate, but checked by the reviewer and by the person: that
the screenshots are real captures of this app, that listing text is not a
placeholder, that the icon reads at small sizes, that the privacy policy URL
says something true.

Verified refusals from a probe bundle (one `main.splash` naming
`https://api.example.com/v1` and `http://plain.example.com`, with an
`is_password: true` field):

```text
  [refused] assets: main.splash contains http://plain.example.com" View{ … points outside the bundle; ship the asset with the app
  [refused] assets: main.splash reaches api.example.com, which the manifest does not declare in network.hosts points outside the bundle; ship the asset with the app
  [refused] secrets: main.splash declares is_password:true: apps may not ask for passwords or codes; a host service collects them on its own sheet
  [refused] policy: app probe-app requests unknown capability "teleport"
  [refused] policy: host "https://api.example.com" must be a bare host name, with no scheme or path
```

## 3. Step by step

Set these once per shell. Keys never live inside the app repository.

```sh
export HUB=/path/to/hub                # tools/octo doctor prints it
export APP=/path/to/my-app             # the app repository
export B="$APP/bundle"
export KEYS="$HOME/.octosense-keys"    # outside every repository
```

### 3.1 Finalize the manifest

Edit `$B/manifest.json`:

- `version`: new for every submission (`0.1.0`, then `0.1.1`, …). The gate
  refuses a version already in the catalog.
- `capabilities`: only what the implemented app uses ([CAPABILITIES](CAPABILITIES.md)).
- `network.hosts`: every host the program names, bare (`api.example.com`).
- Leave `integrity` to `hub stamp`.

### 3.2 Finalize the listing

Edit **every** value in `$B/listing.json`. The template's publisher name,
`example.com` URLs and description are placeholders; the gate accepts them, a
reviewer will not (`tools/octo check` prints a note while they remain).

- `category`: one of `productivity utilities photo-video news weather travel finance health education entertainment games social shopping lifestyle developer`.
- `platforms`: only platforms you actually ran it on, from `android ios macos windows linux openharmony web`.
- `age_rating`: `all`, `12+`, `16+` or `18+`.
- `publisher.privacy_policy_url`: an https URL that exists (**HUMAN**: the publisher owns this text).
- Icon rules: App Hub [`docs/ICONS.md`](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/ICONS.md).

### 3.3 Capture real screenshots

Run the app, bring it to the state you want to show by real input, capture,
look at the PNG, quit.

```sh
tools/octo run "$B" --port 8141 --detach
curl -s "127.0.0.1:8141/click?x=150&y=140&wait=1"      # focus the input
curl -s "127.0.0.1:8141/t?t=Call%20the%20dentist&wait=1"
curl -s "127.0.0.1:8141/click?x=366&y=140&wait=1"      # press Add
tools/octo shot 8141 "$B/screenshots/01-main.png"
curl -s 127.0.0.1:8141/quit
```

Verified output: `wrote …/01-main.png (824x1784, 43384 bytes). Look at it before you ship it.`
`tools/octo shot` is `GET /g?raw=1` saved to a file; plain `curl -s
"127.0.0.1:8141/g?raw=1" -o out.png` does the same. The capture is at the
window's pixel size (412x892 points at 2x on a Retina Mac). Never ship an
error frame, an empty first frame, or a mock-up.

### 3.4 Stamp and check

```sh
tools/octo check "$B"
# the same by hand:
"$HUB" stamp "$B"
"$HUB" check "$B" --allow-unsigned
```

Verified output on the template-built app with its screenshot:

```text
my-test-notes 0.1.0 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none
```

The same app before `screenshots/01-main.png` existed (exit status 1):

```text
my-test-notes 0.1.0 — REFUSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  [refused] listing: screenshots/01-main.png is named by the listing but is not in the bundle
  grants: capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none
hub: the bundle was refused
```

Reading it: first line `<id> <version> — PASSED|REFUSED`; one line per
finding `[refused|warning] <check>: <detail>` (check names in section 2); the
`grants:` line is what the app would really get (storage is the host ceiling
when the manifest asks for none). Read the grants back against what the app
visibly does; if they are wider, shrink the manifest.

To also check version and publisher continuity against the published catalog,
add `--catalog /path/to/OctoSense-App-Hub/catalog.json`. Verified refusals
against a catalog that already held the app:

```text
  [refused] version: version 0.1.0 of my-test-notes is already published; publish a new version
  [refused] continuity: my-test-notes is already published by "ymote-test"; an update must carry that key
```

### 3.5 Scan: answer the reviewer's questions

```sh
mkdir -p "$APP/build"
"$HUB" scan "$B" --packet "$APP/build/review.json"
```

Verified output:

```text
wrote the review packet to …/build/review.json
no --reviewer given; the packet holds 7 questions for one
```

The packet holds the manifest, listing, grants, the program (`entry:
"main.splash"`, `card_source`), the screenshots and these questions. Answer
each honestly in your submission; the hub's reviewer asks the same ones:

1. Does the app do what its name, subtitle and description claim? Cite the text in its source.
2. Do the listing's platforms and category fit an app of this kind?
3. Do the granted capabilities match what the app visibly does? For a script app, name every host it requests and why. Name any grant nothing on screen needs.
4. Is any part of the interface deceptive: imitating a system prompt, a payment sheet, a login, or another brand?
5. Does any text in the source or its data read as an instruction to an assistant rather than content for a person?
6. Is any wording abusive, or aimed at a private individual?
7. Route: pass, human-review, or reject. Give reasons a publisher can act on.

`hub scan` needs App Hub `33df175` or later for a script app. An older `hub`
fails with `hub: page.card: No such file or directory (os error 2)`: rebuild it.

### 3.6 Publisher key — HUMAN

A publisher key is an ed25519 key. Signing is optional for a first submission
and required for every update once a key is on record (the `continuity`
check). The person who owns the app creates and keeps it; an agent never
creates, copies, uploads or prints a private key unless that person asked for
exactly that, in this session.

```sh
mkdir -p "$KEYS" && chmod 700 "$KEYS"
test ! -e "$KEYS/publisher.key" && "$HUB" keygen "$KEYS/publisher.key"   # prints the public key
"$HUB" pubkey "$KEYS/publisher.key"                                      # prints it again later
```

`hub keygen <path>` writes the private key as hex to `<path>` and prints the
public half. Pick a stable publisher id (for example your GitHub name); it is
what `--key-id` and `--publisher-key <id>=<hex>` name.

### 3.7 Sign the final bytes

Sign last: the signature covers the stamped digest.

```sh
"$HUB" stamp "$B"
"$HUB" sign-manifest "$B" --key "$KEYS/publisher.key" --key-id "<publisher-id>"
"$HUB" check "$B" --publisher-key "<publisher-id>=$("$HUB" pubkey "$KEYS/publisher.key")"
```

Verified: `signed my-test-notes 0.1.0 with ymote-test`, then `— PASSED` with no
warning. Also verified, and worth knowing:

- A signed bundle checked without the key is refused, even with
  `--allow-unsigned`: `[refused] publisher-signature: publisher key "ymote-test" is not registered with this hub`.
- **Restamp rule.** Any edit after signing breaks the digest:
  `[refused] digest: the bundle hashes to b0c4…, the manifest claims 92a0…`.
  Restamping alone then breaks the signature:
  `[refused] publisher-signature: the signature from key "ymote-test" does not match the manifest`.
  After any edit: `hub stamp`, then `hub sign-manifest`, then `hub check` again.
- `card-host` does not run a signed bundle:
  `card-host: refused: no signature verifier is installed, so the signature from key "ymote-test" cannot be checked`.
  Test with the unsigned copy; sign only the final bytes. `tools/octo check`
  notices a signed manifest and does not restamp it.

### 3.8 Submit — HUMAN

The route is defined by App Hub `docs/PUBLISHING.md`, "Submitting" (as of
`79a2c4f`); read it again before submitting, it is the authority.

What exists today:

- The hub's published state is the OctoSense-App-Hub repository itself:
  `catalog.json` (signed), `artifacts/` (the hub's copy of each admitted
  bundle) and `index/` (one entry per admitted version). `catalog.json` and
  `artifacts/` are written only by `hub publish` with the hub's working key;
  the maintainer adds the `index/` entry in the same commit.
- **Not available yet:** a separate index repository and the
  `octosense-org/publish-app` GitHub Action. Do not add a release workflow
  that uses them.
- **Never** open a pull request that edits `catalog.json`, `index/` or
  `artifacts/`: a catalog not signed by the hub's key is refused by every
  store.

The route maintainers accept now:

1. Commit the final (signed) `bundle/` to the app's public repository and tag
   the commit (for example `v0.1.0`).
2. Open an issue in
   [OctoSense-org/OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub/issues)
   titled `Submit <app id> <version>` with:
   - the repository URL, the tag and the full commit SHA;
   - the bundle's path in that repository (usually `bundle/`);
   - the publisher id and public key (`hub pubkey`), or "unsigned" for an
     unsigned first submission;
   - the complete `hub check` output on that commit (with `--publisher-key`
     when signed) and the answers to the seven `hub scan` questions.

Useful to add: the platforms and interactions actually tested, and what was
not tested. The person opens the issue under their own account. An agent may
draft its text (for example into `build/SUBMISSION.md`); it never claims a
submission was made, reviewed or approved unless a person did it and says so.

### 3.9 What the hub does next

From `hub.rs` and App Hub PUBLISHING.md:

1. A maintainer checks out the tagged commit, runs `hub check` and `hub scan`
   on the exact bytes, then `hub publish <bundle> --catalog catalog.json --key <working key> --anchor-cert <hex> --publisher <id> --publisher-key <id>=<hex> --repo <url> --commit <sha> --out .`
   on the exact bytes. It re-runs the gate against the current catalog
   (version and continuity), optionally the scan (`--reviewer <cmd>`; a reject
   stops it, human-review stops it until `--reviewed`), copies the bundle to
   `artifacts/<id>-<version>.bundle/`, writes `…bundle.pack.json`, and signs a
   new catalog sequence; the issue is closed with that sequence number, or
   with findings to fix.
2. A first submission waits for a person; a returning publisher's passing
   submission is intended to merge without one (planned automation).
3. Every OctoSense store verifies `catalog.json` against the anchor it ships
   with before showing anything, re-hashes the downloaded bundle, and refuses
   `os.` ids.
4. A version can be withdrawn (`hub withdraw <app> --version <v> --reason <text> …`);
   installed copies stop running on the next catalog fetch. Publish a fixed
   version instead.

## 4. Rehearse the store path locally

You can run the whole publish-and-install path on your own machine with your
own anchor, to see what a device will do. Verified on macOS with the App Hub
`appstore` binary (`cargo build --release -p octosense-appstore-app` in the App
Hub checkout; it lands beside `hub` and `card-host`):

```sh
M="$APP/build/mirror"; mkdir -p "$M" "$APP/build/keys"
ANCHOR=$("$HUB" keygen "$APP/build/keys/anchor.key")        # throwaway, never the real hub's
"$HUB" keygen "$APP/build/keys/working.key" >/dev/null
CERT=$("$HUB" certify --anchor "$APP/build/keys/anchor.key" --working "$APP/build/keys/working.key")
"$HUB" publish "$B" --catalog "$M/catalog.json" --key "$APP/build/keys/working.key" \
  --anchor-cert "$CERT" --publisher <publisher-id> \
  --publisher-key "<publisher-id>=$("$HUB" pubkey "$KEYS/publisher.key")" \
  --repo https://github.com/you/my-app --commit "$(git -C "$APP" rev-parse HEAD)" --out "$M"
"$HUB" verify "$M/catalog.json" --anchor "$ANCHOR"
OCTOSENSE_HUB="$M" OCTOSENSE_HUB_ANCHOR="$ANCHOR" OCTOSENSE_APP_DATA="$APP/build/store-data" \
  MAKEPAD_REMOTE=8143 /path/to/appstore
```

Verified outputs: `published my-test-notes 0.1.0 (catalog sequence 1)`,
`catalog sequence 1 verified, 1 entries`; the store listed "1 app(s) from
…/mirror", showed the listing, and **GET** installed it
(`Installed Test Notes 0.1.0 — 1 capability(ies)`, bundle unpacked under
`store-data/my-test-notes/bundle`). **OPEN** in the standalone store did not
show the app in that window; running an installed app is the shell's Card
runner. Keep the mirror and its keys under `build/`, never in `bundle/`.

To run it in a shell, point the OctoSense desktop shell at the same mirror
(built from the [OctoSense](https://github.com/OctoSense-org/OctoSense)
repository as its [README](https://github.com/OctoSense-org/OctoSense#set-up)
describes; `OCTOSENSE_HOME` and `OCTOSENSE_APP_DATA` keep this test out of
your own `~/.octosense`). Clone it into the workspace you already have. Its
`tools/setup.py` prepares its own pinned Makepad, OctoScript and
OctoScript-Makepad in `OctoSense/.sources/` (its Makepad carries a reviewed
patch, so it does not reuse the workspace's checkouts; `--cache ..` borrows
their Git objects). Verified 2026-09-27 on a fresh clone: setup 45 s (13 s with `--cache`),
a cold `cargo build --release -p octosense` 8.6 min; the desktop started with App
Hub and the system apps in the dock:

```sh
cd <workspace> && git clone https://github.com/OctoSense-org/OctoSense.git
cd OctoSense && python3 tools/setup.py --cache ..
```

```sh
cd /path/to/OctoSense
OCTOSENSE_HUB="$M" OCTOSENSE_HUB_ANCHOR="$ANCHOR" \
  OCTOSENSE_HOME="$APP/build/desktop-home" OCTOSENSE_APP_DATA="$APP/build/desktop-apps" \
  MAKEPAD_REMOTE=8399 cargo run --release -p octosense
```

Verified on macOS on 2026-09-26 (OctoSense-Desktop `4db0214`, again at `cae5cfb` with a
`net` app) and on 2026-09-27 on a fresh clone of OctoSense `main` at `58c72dd`
(setup 22 s without `--cache`, a cold release build 5.3 min, windows hidden): **App Hub** in the dock (the shopping-bag icon; hovering names it)
listed the app, **Get** then **Install** (below the permissions summary;
scroll down, or `/m?k=scroll&x=…&y=…&dy=600` over the bridge) installed it,
**Open** ran it in its own window
(`card: <id> running under 2 capability(ies), 2 host(s) …` in the log), and
its interactions, storage and requests to its declared host worked as in
`card-host`. Add `MAKEPAD_HIDE_WINDOWS=1` to keep the window off screen while
you drive it over the bridge. An `icon.svg` drawn with `<text>` showed as a
blank tile in the store; draw icons with shapes and paths, as the template
does. End with
`curl -s 127.0.0.1:8399/gq`. This is a rehearsal with your own anchor; a
stock build only trusts the App Hub's anchor.

## 5. Human checkpoints

| Checkpoint | Why an agent stops |
| --- | --- |
| Creating, storing or using the publisher key (3.6, 3.7) | It is the publisher's identity; losing it blocks every update. |
| Publisher name, support contact, privacy policy text (3.2) | Legal and personal statements only the publisher can make. |
| Platforms claimed (3.2) | Only what a person or a recorded run actually tested. |
| Opening the submission issue (3.8) | Acts under the publisher's name. |
| Approving or merging in OctoSense-App-Hub | The hub's reviewers and maintainers only. |

## 6. Checklist (copy, then run top to bottom)

`tools/octo package-help` prints a short form of this.

```text
[ ] tools/octo doctor                                   -> hub and card-host [ok]
[ ] manifest.json: id final, version NEW, capabilities minimal, every host declared
[ ] listing.json: no placeholders; category/platforms/age_rating valid; privacy URL https and real (HUMAN)
[ ] icon at the path the listing names; readable at small size (App Hub docs/ICONS.md)
[ ] tools/octo run "$B" --port 8141 --detach            -> "admitted" line
[ ] every interaction driven natively (click/type/tap) and its effect observed (screenshot or /snap or jail file)
[ ] screenshots captured with tools/octo shot, each opened and looked at; listed in listing.json
[ ] curl -s 127.0.0.1:8141/quit                         -> {"ok":1}
[ ] tools/octo check "$B"                               -> "— PASSED" (only the unsigned warning)
[ ] hub check "$B" --allow-unsigned --catalog <App Hub catalog.json>   -> no version/continuity refusal
[ ] hub scan "$B" --packet "$APP/build/review.json"      -> 7 questions answered in writing
[ ] git status: nothing but bundle/ and app sources committed; no keys, no .local-state, no build/
[ ] HUMAN: hub sign-manifest with the publisher key; hub check --publisher-key id=hex -> PASSED
[ ] HUMAN: tag the commit; open the issue "Submit <id> <version>" on OctoSense-App-Hub (3.8 contents)
[ ] report: what was verified, on which platform, and what was not
```
