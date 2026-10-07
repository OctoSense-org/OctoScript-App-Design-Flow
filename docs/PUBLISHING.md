# Publishing an OctoSense app to the App Hub

English | [简体中文](PUBLISHING.zh-CN.md)

Take a working script app to a bundle that is ready to sign: the final
manifest and listing, real screenshots, a passing gate with the review
questions answered, and a rehearsal of the store path on your own machine. A
coding agent can run these steps top to bottom and stop exactly where a
person must act.

Two App Hub documents own the rest:

| You need | Read |
| --- | --- |
| The gate's rules, capability names, reserved ids, manifest and listing fields, signing | App Hub [PUBLISHING.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md) |
| Signing, tagging, the submission issue, what reviewers check, common refusals | App Hub [SUBMITTING.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md) |

- Start here when [QUICKSTART](QUICKSTART.md) §1–6 pass: the app runs in
  `card-host`, and you have tested its interactions.
- **HUMAN** marks a checkpoint an agent must not pass on its own: private
  keys, the publisher identity and privacy text, the platforms claimed, the
  release tag and the submission. An agent stops, reports and waits.

## 1. What gets published

Only `bundle/`. Everything else in the app repository (`AGENTS.md`, notes,
tools, keys, logs, `.local-state/`, `build/review.json`) stays outside it.

```text
my-app/
  AGENTS.md  README.md  .gitignore        not submitted
  .gitattributes                         copied by tools/octo new: bundle/** -text, so Git never rewrites the bundle
  build/review.json                      not submitted (hub scan output)
  .local-state/                          not submitted (card-host jail)
  bundle/                                THE SUBMISSION
    manifest.json      id, version, name, integrity, capabilities, hosts
    listing.json       what the store shows
    main.splash        the program (a card app has page.card + kit/ instead)
    assets/icon.svg    the icon the listing names (PNG or SVG, square)
    screenshots/01-main.png   real captures, PNG, 1 to 8, named by the listing
```

`bundle/` holds only file types the gate knows. macOS Finder adds
`.DS_Store` files to folders you open, and the gate refuses them; delete them
before you stamp. The published reference apps keep `PRIVACY.md`,
`publisher.json` and a `review/` folder beside `bundle/`:
[SUBMITTING §1](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#1-lay-out-the-repository)
shows that layout.

## 2. The rules the gate enforces

`hub check` is the gate: the same code App Hub runs on your submission. It
prints `<id> <version> — PASSED` or `<id> <version> — REFUSED`, then one line
per finding. A `[refused]` line blocks admission; a `[warning]` line does
not, but the reviewer sees it. The rule-by-rule reference is
App Hub's
[rules the gate enforces](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#rules-the-gate-enforces).
The fixes for the refusals people hit most are in
[Common refusals and how to fix them](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#common-refusals-and-how-to-fix-them).

The gate does not judge whether the screenshots are real captures of this
app, whether the listing text is true, whether the icon reads at small
sizes, or whether the privacy policy says something true. Reviewers do.

## 3. Step by step

Set these once per shell:

```sh
export HUB=/path/to/hub                # tools/octo doctor prints it
export APP=~/apps/my-app               # the app repository
export B="$APP/bundle"
```

### 3.1 Finalize the manifest

Edit `$B/manifest.json`:

- `id`: final. Its last segment is not a reserved name
  ([QUICKSTART §3](QUICKSTART.md#3-create-an-app)).
- `version`: new for every submission (`0.1.0`, then `0.1.1`, …). The gate
  refuses a version already in the catalog, and the release tag carries the
  same number.
- `capabilities`: only what the implemented app uses ([CAPABILITIES](CAPABILITIES.md)).
- `network.hosts`: every host the program names, bare (`api.example.com`).
- Leave `integrity` to `hub stamp`.

App Hub's [The manifest](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#the-manifest)
lists every field.

### 3.2 Finalize the listing

Edit **every** value in `$B/listing.json`. The template's publisher name,
`example.com` URLs and description are placeholders. The gate accepts them, a
reviewer does not, and `tools/octo check` prints a note while they remain.

- `platforms`: only the platforms you ran the app on (**HUMAN** confirms). A
  `card-host` run on a Mac is `macos`. `tools/octo new` wrote the ones you
  passed with `--platform`; remove any you did not test.
- `category`, `age_rating` and the other fields take the values in App Hub's
  [The listing](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#the-listing).
- `publisher.privacy_policy_url`: an HTTPS URL that exists (**HUMAN**: the
  publisher owns this text). If the bundle ships `tools.json`, the app has an
  agent; say so in the listing and the privacy text.
- The icon: follow App Hub's [`docs/ICONS.md`](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/ICONS.md).

The listing is part of the signed version: changing its text later takes a
new version.

### 3.3 Capture real screenshots

Run the unsigned app, bring it to the state you want to show by real input,
capture it, look at the PNG, and quit:

```sh
tools/octo run "$B" --port 8141 --hidden --detach
curl -s "127.0.0.1:8141/click?x=150&y=140&wait=1"      # focus the input
curl -s "127.0.0.1:8141/t?t=Call%20the%20dentist&wait=1"
curl -s "127.0.0.1:8141/click?x=366&y=140&wait=1"      # press Add
tools/octo shot 8141 "$B/screenshots/01-main.png"
curl -s 127.0.0.1:8141/quit
```

`shot` prints `wrote …/01-main.png (824x1784, … bytes). Look at it before you
ship it.` It waits for the app's widgets and a settled frame, then saves
`GET /g?raw=1`. A plain `curl -s "127.0.0.1:8141/g?raw=1" -o out.png` saves
whatever frame is current, which can be half drawn. The capture is at the
window's pixel size: 412x892 points at 2x on a Retina Mac.

- Capture before you sign: `card-host` refuses a signed bundle.
- Name up to 8 screenshots in `listing.json`.
- Never ship an error frame, an empty first frame, a mock-up, or an image
  redrawn from `/snap`.

### 3.4 Stamp and check

```sh
tools/octo check "$B"
# the same by hand:
"$HUB" stamp "$B"
"$HUB" check "$B" --allow-unsigned
```

On the template-built app with its screenshot:

```text
my-notes 0.1.0 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none
```

The same app before `screenshots/01-main.png` existed (exit status 1):

```text
my-notes 0.1.0 — REFUSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  [refused] listing: screenshots/01-main.png is named by the listing but is not in the bundle
  grants: capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none
hub: the bundle was refused
```

Read the `grants:` line against what the app visibly does, and shrink the
manifest if the grants are wider. `storage 16777216 bytes` is the 16 MiB store
ceiling. An app gets it when it declares `storage` without
`storage.max_bytes`; without `storage`, it gets `storage none` and cannot
save anything.

To check the version against the published catalog, add
`--catalog <App Hub checkout>/catalog.json` to either command. A version that
is already published is refused:

```text
  [refused] version: version 0.1.0 of org.octosense.samples.githubnotes is already published; publish a new version
```

`tools/octo check` restamps an unsigned bundle before it checks, so it passes
even when the digest you committed is stale. Run it as the last step before
every commit. The final check runs from a fresh clone of the release tag
(§3.8).

### 3.5 Answer the review questions

```sh
mkdir -p "$APP/build"
"$HUB" scan "$B" --packet "$APP/build/review.json"
```

```text
wrote the review packet to …/build/review.json
no --reviewer given; the packet holds 7 questions for one
```

The packet holds the manifest, the listing, the grants, the program, any
agent files and the questions. It holds no screenshots, so attach them to the
issue yourself. There are seven questions, and an eighth about the agent
files when the bundle ships `tools.json`, `AGENT.md` or skills. Answer each one in writing,
for example in `$APP/review/ANSWERS.md`; the reviewer asks the same ones
([SUBMITTING §8](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#8-what-reviewers-check)).
On a signed bundle, `hub scan` needs `--publisher-key <publisher-id>=<hex public key>`.

### 3.6 Publisher key — HUMAN

A publisher key is an Ed25519 key that identifies the publisher across every
version: App Hub refuses an update signed by a different key. The person who
owns the app creates and keeps it. An agent never creates, copies, uploads or
prints a private key unless that person asked for exactly that, in this
session.

`hub keygen <key-file>` writes the private key as hex and prints the public
half; `hub pubkey <key-file>` prints the public half again. Keep the key
outside every repository:

```sh
"$HUB" keygen <key-file>
```

`keygen` never overwrites. If a file or a symlink already exists at that
path, it stops with
`hub: cannot create new signing key "<key-file>": File exists (os error 17)`;
choose a new path, and never delete a key you have published with. On macOS
and Linux, it creates the file with mode 0600, readable only by you. On
Windows, keep the key in a folder that only you can read. A `hub` built
before App Hub's current `main` overwrites without asking and uses your
default permissions; rebuild it first.

[SUBMITTING §5](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#5-produce-the-final-bytes)
gives the publisher id and the signing commands, and
[SUBMITTING §1](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#1-lay-out-the-repository)
shows what `publisher.json` holds; App Hub's
[Signing](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md#signing)
is the reference.

### 3.7 Sign the final bytes — HUMAN

Sign last. The signature covers the manifest, and the manifest carries the
digest of every other file. Once the bundle is signed:

- any edit breaks the digest, and restamping alone then breaks the signature,
  so a person stamps and signs again;
- `card-host` refuses the bundle, so capture screenshots and test before
  signing;
- `tools/octo check` no longer restamps it, and refuses it unless you pass
  `--publisher-key <publisher-id>=<hex public key>`.

[SUBMITTING §5](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#5-produce-the-final-bytes)
gives the commands and their output.

### 3.8 Submit — HUMAN

A person commits the signed bundle, tags that commit, runs `hub check` on a
fresh clone of the tag (without restamping), and opens a `Submit <app id> <version>`
issue on OctoSense-App-Hub. App Hub's SUBMITTING describes each step:
[§6 Freeze and verify the release](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#6-freeze-and-verify-the-release)
and
[§7 Open the submission issue](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#7-open-the-submission-issue),
with every field the issue needs.

- Never move or recreate a tag. To change anything, release a new version.
- Never open a pull request that edits App Hub's `catalog.json`, `index/` or
  `artifacts/`. Only `hub publish` with App Hub's catalog key writes them,
  and every store refuses a catalog that key did not sign.
- An agent may draft the issue text, for example into `build/SUBMISSION.md`.
  It never claims a submission was made, reviewed or approved unless a person
  did it and says so.

### 3.9 What App Hub does next

A maintainer runs the gate and the scan on the exact bytes of your tag, then
publishes the bundle into a new signed catalog or answers with findings to
fix. [SUBMITTING §9](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/SUBMITTING.md#9-after-you-submit)
covers what follows and how to ship a fix.

## 4. Rehearse the store path locally

Run the whole publish-and-install path on your own machine, signed with your
own trust anchor (a throwaway root key in place of App Hub's), to see what a
device does. The rehearsal also runs the app's host services, which
`card-host` cannot. Keep the mirror and its keys under `build/`, never in
`bundle/`.

### 4.1 Publish into a local mirror

Publish the signed bundle into a mirror with throwaway hub keys, then verify
the mirror. The publisher's public key is the hex string `hub pubkey` prints;
the private key is not needed. `keygen` refuses an existing file, so remove
`$APP/build/keys` (throwaway keys only) before you run this block again:

```sh
M="$APP/build/mirror"; mkdir -p "$M" "$APP/build/keys"
ANCHOR=$("$HUB" keygen "$APP/build/keys/anchor.key")        # throwaway, never App Hub's
"$HUB" keygen "$APP/build/keys/working.key" >/dev/null
CERT=$("$HUB" certify --anchor "$APP/build/keys/anchor.key" --working "$APP/build/keys/working.key")
"$HUB" publish "$B" --catalog "$M/catalog.json" --key "$APP/build/keys/working.key" \
  --anchor-cert "$CERT" --publisher <publisher-id> \
  --publisher-key "<publisher-id>=<hex public key>" \
  --repo https://github.com/you/my-app --commit "$(git -C "$APP" rev-parse HEAD)" --out "$M"
"$HUB" verify "$M/catalog.json" --anchor "$ANCHOR"
```

Expected output, recorded on macOS with an earlier App Hub and a test app
named Test Notes (`my-test-notes`): `publish` prints
`published my-test-notes 0.1.0 (catalog sequence 1)` and `verify` prints
`catalog sequence 1 verified, 1 entries`.

### 4.2 Install and open the app in the desktop shell

Point the OctoSense desktop shell at the mirror. Clone
[OctoSense](https://github.com/OctoSense-org/OctoSense) into your workspace
and set it up as its [README](https://github.com/OctoSense-org/OctoSense#set-up)
describes. `tools/setup.py` puts pinned copies of Makepad, OctoScript and
OctoScript-Makepad in `OctoSense/.sources/`, with OctoSense's reviewed
patches applied to Makepad, so the shell does not reuse the workspace's
checkouts; `--cache ..` reuses their Git objects. Setup takes under a minute;
a cold `cargo build --release -p octosense` takes 5 to 9 minutes:

```sh
cd <workspace> && git clone https://github.com/OctoSense-org/OctoSense.git
cd OctoSense && python3 tools/setup.py --cache ..
```

```sh
cd <workspace>/OctoSense
OCTOSENSE_HUB="$M" OCTOSENSE_HUB_ANCHOR="$ANCHOR" \
  OCTOSENSE_HOME="$APP/build/desktop-home" OCTOSENSE_APP_DATA="$APP/build/desktop-apps" \
  MAKEPAD_REMOTE=8399 cargo run --release -p octosense
```

`OCTOSENSE_HOME` and `OCTOSENSE_APP_DATA` keep this test out of your own
`~/.octosense`. Add `MAKEPAD_HIDE_WINDOWS=1` to keep the window off screen
while you drive it over the bridge. Then:

1. Open **App Hub** in the dock. Your app is listed.
2. Click **Get**, then **Install**.
3. Click **Open**. The app runs in its own window, and the log shows
   `card: <app id> running under …`.
4. Drive the app, then end with `curl -s 127.0.0.1:8399/gq`.

Verified on macOS: the app's interactions, storage and requests to its
declared host behave as in `card-host`.

- An `icon.svg` drawn with `<text>` showed as a blank tile in the store.
  Draw icons with shapes and paths, as the template does.
- An app that declares `auth` needs a shell built from OctoSense `main`
  (`desktop-v0.1.0-beta.2` or later); a beta.1 store refuses the capability.
  The shell you build here has no provider registrations until you supply
  them, and they never go in the app. Either set the build variables, such as
  `OCTOSENSE_GITHUB_CLIENT_ID`, when `cargo` compiles the shell
  ([configure a release](https://github.com/OctoSense-org/OctoSense/blob/main/crates/oauth-service/README.md#configure-a-release-maintainers)), or write
  `$OCTOSENSE_APP_DATA/.host/oauth/clients.json` (here
  `$APP/build/desktop-apps/.host/oauth/clients.json`), which replaces the
  compiled set ([advanced operator override](https://github.com/OctoSense-org/OctoSense/blob/main/crates/oauth-service/README.md#advanced-operator-override)).
  Live use with the real providers is largely unverified
  ([CAPABILITIES § Limits](CAPABILITIES.md#limits)).
- This is a rehearsal with your own trust anchor. A stock build trusts only
  App Hub's anchor.

### 4.3 Optional: install with the standalone store

App Hub's standalone `appstore` installs from the same mirror without the
shell, but it cannot open apps: only the shell's Card runner runs an
installed app.

`octosense-appstore-app` keeps App Hub's `text-input-state-query` feature
on, so it builds only against OctoSense's patched Makepad. On plain Makepad it
stops with `no variant … TextInputStateQuery`. Keep your working workspace
plain, because `tools/setup-native.py --check` refuses a patched Makepad
tree, and build the store in a second workspace:

1. Lay out a second workspace as in
   [QUICKSTART §1](QUICKSTART.md#1-prerequisites).
2. Apply OctoSense's Makepad patches to its `makepad/` in the order that
   `runtime-patches.lock.json` lists them: its `patch` first, then each
   `stacked` entry. With the OctoSense checkout from §4.2:

   ```sh
   cd <second-workspace>
   python3 - <workspace>/OctoSense <<'EOF'
   import json, subprocess, sys
   octosense = sys.argv[1]
   lock = json.load(open(f"{octosense}/runtime-patches.lock.json"))["makepad"]
   for patch in [lock["patch"]] + [s["patch"] for s in lock["stacked"]]:
       subprocess.run(["git", "-C", "makepad", "apply", f"{octosense}/{patch}"], check=True)
   EOF
   ```

3. Build the store in that workspace's App Hub checkout. The `appstore`
   binary lands in its `target/release/`:

   ```sh
   cd <second-workspace>/OctoSense-App-Hub
   cargo build --release -p octosense-appstore-app
   ```

4. Open the mirror in the store:

   ```sh
   OCTOSENSE_HUB="$M" OCTOSENSE_HUB_ANCHOR="$ANCHOR" OCTOSENSE_APP_DATA="$APP/build/store-data" \
     MAKEPAD_REMOTE=8143 <second-workspace>/OctoSense-App-Hub/target/release/appstore
   ```

Expected result, recorded on macOS with an earlier App Hub: the store lists
"1 app(s) from …/mirror" and shows the listing. Its buttons are labelled in
capitals. **GET** installs the app
(`Installed Test Notes 0.1.0 — 1 capability(ies)`) and unpacks the bundle
under `store-data/my-test-notes/bundle`; **OPEN** does not show the app.

## 5. Human checkpoints

| Checkpoint | Why an agent stops |
| --- | --- |
| Creating, storing or using the publisher key (3.6, 3.7) | It is the publisher's identity; losing it blocks every update. |
| Publisher name, support contact, privacy policy text (3.2) | Legal and personal statements only the publisher can make. |
| Platforms claimed (3.2) | A platform claim must match a run that a person did or recorded; an agent cannot vouch for one. |
| Tagging the release (3.8) | The tag names the exact bytes reviewers check; it never moves. |
| Opening the submission issue (3.8) | It acts under the publisher's name. |
| Approving or merging in OctoSense-App-Hub | App Hub's reviewers and maintainers only. |

## 6. Checklist (copy, then run top to bottom)

`tools/octo package-help` prints a shorter version; this one adds the
`--hidden`, `.DS_Store` and fresh-clone steps.

```text
[ ] tools/octo doctor                                   -> hub and card-host [ok]
[ ] manifest.json: id final (last segment not reserved), version NEW, capabilities minimal, every host declared
[ ] listing.json: no placeholders; category/platforms/age_rating valid; privacy URL HTTPS and real (HUMAN)
[ ] icon at the path the listing names; readable at small size (App Hub docs/ICONS.md)
[ ] tools/octo run "$B" --port 8141 --hidden --detach   -> "admitted" line
[ ] every interaction driven natively (click/type/tap) and its effect observed (screenshot or /snap or jail file)
[ ] screenshots captured from the unsigned bundle with tools/octo shot, each opened and looked at; listed in listing.json
[ ] curl -s 127.0.0.1:8141/quit                         -> {"ok":1}
[ ] find "$B" -name .DS_Store -delete                    -> only known file types in bundle/
[ ] tools/octo check "$B"                               -> "— PASSED" (only the unsigned warning)
[ ] tools/octo check "$B" --catalog <App Hub catalog.json>   -> no version or continuity refusal
[ ] mkdir -p "$APP/build"; hub scan "$B" --packet "$APP/build/review.json"   -> 7 questions answered in writing (8 with tools.json, AGENT.md or skills)
[ ] git -C "$APP" check-attr text -- "$B/manifest.json"   -> "text: unset" (QUICKSTART §3)
[ ] git status: only bundle/ and app sources; no keys, .local-state or build/
[ ] HUMAN: sign last; hub check --publisher-key <publisher-id>=<hex public key> -> PASSED (App Hub SUBMITTING §5)
[ ] HUMAN: commit, tag v<version>, plain hub check on a fresh clone of the tag (SUBMITTING §6)
[ ] HUMAN: open the issue "Submit <app id> <version>" on OctoSense-App-Hub (SUBMITTING §7)
[ ] report: what was verified, on which platform, and what was not
```
