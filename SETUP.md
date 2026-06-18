# Setup

This guide walks through everything from a clean macOS install. Estimated
time for first-time setup: 30-45 minutes (most of it is the OAuth dance
for your personas).

## Prerequisites

You need:

- macOS or Linux
- The basecamp CLI (v0.7.2 or later)
- Homebrew (for installing yq)
- yq (YAML query tool)
- Python 3.10+ with pyyaml
- OAuth credentials for each persona you want to set up

### Installing the basecamp CLI

If you don't have it already:

    brew install basecamp/tap/basecamp

Or follow instructions at https://github.com/basecamp/basecamp-cli for
your platform. Verify with:

    basecamp --version

You should see v0.7.2 or later.

### Installing yq

    brew install yq

### Installing pyyaml

    pip3 install pyyaml

## Configure your roster

### 1. Copy the template

    cp personas.example.yaml personas.yaml

`personas.yaml` is gitignored — never commit it.

### 2. Fill it in

Open `personas.yaml` in your editor. Replace:

- `YOUR_ACCOUNT_ID` — your demo Basecamp account ID. Find it in the URL
  when you're logged into the account: `https://3.basecamp.com/<account_id>/...`
- `YOUR_PROJECT_ID` — a project ID you'll use for testing. Find it in
  the project URL.
- The persona list — replace the three sample personas with your real
  ones. Keep `name` lowercase with no spaces (it becomes the basecamp
  profile name).

You can start with just 2-3 personas to validate the setup before
authorizing your full roster.

## Targeting a local or staging Basecamp (optional)

By default bcscene talks to production Basecamp (`3.basecampapi.com` for the
API, `launchpad.37signals.com` for OAuth). To point it at a local dev or
staging account instead, declare a `target` and an `environments` block in
`personas.yaml`:

    account_id: "181900405"        # the account ID in that environment
    target: local                  # which environment below to use

    environments:
      local:
        base_url: "http://3.basecampapi.localhost:4001"   # API host (port 4001)
        launchpad_url: "http://launchpad.localhost:3011"  # OAuth host
        # 37signals launchpad ships these as the "bcq" fixture client:
        oauth_client_id: "bcq_dev_client_id_37signals_local"
        oauth_client_secret: "bcq_dev_client_secret_37signals_local"

    personas:
      - name: jason
        # ...

Omitting `target` (or setting `target: production`) keeps the production
defaults — nothing else changes.

> **App host vs. API host.** Local dev serves the app on
> `3.basecamp.localhost:3001` but the API on `3.basecampapi.localhost:4001`
> (the `API_PORT`, default 4001) — the same split as production's
> `3.basecamp.com` vs `3.basecampapi.com`. `base_url` is the **API** host:
> point it at `:3001` and every request 404s. The account ID (the digits in
> your app URL) is identical on both.

### Why the OAuth client matters

The basecamp CLI ships with a built-in OAuth client that **only exists in
production launchpad**. A non-production launchpad doesn't know it, so OAuth
fails with `Client not found` — you need a client that exists in the target
launchpad.

**For 37signals local dev**, there's nothing to register: launchpad seeds a
fixture OAuth app named **bcq** ("Basecamp CLI") whose redirect URI is already
`http://127.0.0.1:8976/callback`. Use its credentials directly (the values
shown above) — they ship in the `signal_id` gem's `signal_oauth_clients`
fixtures.

**For staging or a launchpad without that fixture**, register your own OAuth
app instead:

1. Open `<launchpad_url>/integrations/new` and sign in.
2. Set its **redirect URI** to exactly `http://127.0.0.1:8976/callback` — the
   fixed port the CLI listens on during the flow.
3. Copy the resulting **client ID** and **client secret** into
   `environments.<name>.oauth_client_id` / `oauth_client_secret`.

`bin/bcscene-setup-personas` reads all of this (via `lib/config.py`), bakes
`base_url` into each profile, and exports `BASECAMP_LAUNCHPAD_URL`,
`BASECAMP_OAUTH_CLIENT_ID`, and `BASECAMP_OAUTH_CLIENT_SECRET` for the OAuth
flow. The same values are re-applied automatically at runtime so token refresh
keeps working.

### Switching an existing profile's target

If a profile was already authorized against a different target, re-run
`bin/bcscene-setup-personas`. It detects the mismatch (the profile's stored
`base_url` no longer matches the selected environment) and offers to delete and
re-authorize it. Authorizing against a different launchpad always requires a
fresh OAuth login — tokens are not portable across environments.

### Running basecamp commands by hand against a non-production target

bcscene injects the launchpad/OAuth env automatically when it runs a scene, so
scenes just work. But an *ad-hoc* `basecamp -P <persona> …` you type yourself
won't have those vars, so token refresh checks against **production** launchpad
and you'll see a misleading `invalid or expired token`. Export them for your
shell first:

    eval "$(python3 lib/config.py --env-exports)"

(The profile's `base_url` is baked in at creation, so you don't need to set
that — only the launchpad/OAuth vars.)

## Create profiles

### 3. Log out of Basecamp in your browser

Before running the setup script, log out of any Basecamp session you
have open as yourself. The script will open browser windows to authorize
each persona, and any active session will interfere.

### 4. Run the setup script

    bin/bcscene-setup-personas

For each persona, the script will pause and ask you to press Return.
When you do:

1. The basecamp CLI opens a browser window to authorize.
2. Log in as that persona's Basecamp identity.
3. Click "Authorize" when prompted.
4. The CLI captures the token; you return to the terminal.
5. **Log that persona out of Basecamp before continuing to the next.**

If you skip the logout step, the next persona's OAuth flow will silently
use the previous persona's session.

### 5. Verify

    basecamp profile list

You should see one profile per persona, all marked authenticated.

To verify each profile is actually a different identity (not all secretly
you):

    basecamp -P <persona-name> me

Run this for each persona. Each should return a different name and email.
If two return the same identity, your OAuth flow leaked — delete the
duplicate profile (`basecamp profile delete <name>`) and re-authorize.

## Run a scene

### 6. Customize the example scene

Open `scenes/morning-standup.yaml` and replace:

- `YOUR_PROJECT_ID` — your project ID (3 places).
- `YOUR_TODOLIST_ID` — a todolist ID in that project. Find it with
  `basecamp todolists --in <project_id>`.
- The persona names (`liza`, `alex`, `jordan`) — match names in your
  `personas.yaml`.

### 7. Dry-run first

    bin/bcscene scenes/morning-standup.yaml --dry-run

This prints what would run without actually invoking the CLI. Verify the
commands look right before running for real.

### 8. Run for real

    bin/bcscene scenes/morning-standup.yaml

Each step will fire with a 1-second pause between them. Adjust pacing
with `--pause N` (e.g., `--pause 3` for 3-second gaps).

## Writing your own scenes

Copy `scenes/morning-standup.yaml` to a new file in `scenes/` and edit.
The YAML format is documented in README.md.

For new action types not in the default list, edit
`lib/executor.py`'s `ACTION_HANDLERS` dict — each handler is a one-line
lambda mapping scene args to basecamp CLI arguments.

## Troubleshooting

**"profile X not authenticated"** — re-run `bin/bcscene-setup-personas`.
Tokens expire (typically after 14 days of inactivity).

**"No todolist specified"** — your scene's `todo-create` step is missing
the `list` arg. Find the todolist ID with
`basecamp todolists --in <project_id>` and add it to the scene.

**Scene fails partway through** — already-completed steps stay completed
in Basecamp; bcscene doesn't roll back. Edit the scene to remove the
finished steps and re-run, or just clean up manually.

**OAuth captured the wrong identity** — `basecamp profile delete <name>`
removes the profile, then re-run setup with strict logout discipline.
