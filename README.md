# bcscene

Run scripted multi-persona activity in a Basecamp demo account.

You describe what you want in plain English (in Claude Desktop's Code
tab) or write a YAML scene file, and bcscene executes the activity by
invoking the official basecamp CLI as a different authenticated
profile per persona. The result: realistic-looking activity across
multiple users in seconds.

## What it's for

Producing demo content. Specifically:

- Recording videos that show realistic Basecamp activity without
  manually logging in as multiple people.
- Capturing screenshots that need cross-persona context (a chat with
  three replies, a project with mixed contributors, etc.).
- Keeping a demo Basecamp account looking lived-in over time.

## Getting started

**New to this?** Read **[GUIDE.md](GUIDE.md)** — a step-by-step walkthrough
written for non-technical users. Covers everything from installing
prerequisites to running your first scene through Claude Desktop. About
45 minutes start to finish, mostly waiting on OAuth flows.

**Already comfortable with the command line?** See
**[SETUP.md](SETUP.md)** for the condensed reference.

## How it works

bcscene is a thin runner on top of the basecamp CLI's native
multi-profile support. Each persona maps to a `basecamp profile` — a
separately authenticated identity — and bcscene runs each scene step
using the right profile.

There is no credential juggling. The basecamp CLI handles tokens; you
authorize each persona once via OAuth and bcscene just invokes the
CLI.

The recommended day-to-day workflow uses **Claude Desktop's Code tab**
(which runs Claude Code). You launch a Claude Code session in the
bcscene folder and describe scenes in plain English. The repo includes
a `CLAUDE.md` file that primes Claude Code with everything it needs to
know — what the personas are, what actions are available, when to ask
for clarification, when to dry-run.

You can also write scene files by hand in YAML and run them with
`bin/bcscene <scene-file>`. Both workflows work; pick what suits you.

## Using bcscene with a different Basecamp account

bcscene's default setup is tailored to 37signals' Enormicom demo
account. If you want to use it against a different account, the
easiest path is to **fork the repo** so you can customize it without
affecting upstream.

1. **Fork on GitHub.** Visit
   [github.com/younotcooking/bcscene](https://github.com/younotcooking/bcscene)
   and click the "Fork" button in the top right. GitHub creates a copy
   under your username (e.g., `yourname/bcscene`).

2. **Clone your fork** (not the original):

   ```
   gh repo clone yourname/bcscene
   cd bcscene
   ```

3. **Use the blank persona template:**

   ```
   cp personas.blank.yaml personas.yaml
   ```

   Then edit `personas.yaml` to fill in your Basecamp account ID, a
   project ID for testing, and your personas. (If you'd rather start
   from the full Enormicom roster as a reference, use
   `personas.example.yaml` instead.)

4. **Follow [GUIDE.md](GUIDE.md) from Phase 2 onward** — Phase 1
   (installing prerequisites) is the same, and Phase 3 (authorizing
   personas) just authorizes whoever you listed instead of the
   Enormicom cast.

Your fork is independent. Edit scenes, personas, docs however you
want — none of it affects upstream. If upstream gets new features
later and you want them, you can `git pull` from upstream into your
fork.

## Using bcscene against local dev or staging

bcscene talks to production Basecamp by default, but it can target a
local dev or staging account instead. Add a `target` and an
`environments` block to `personas.yaml`:

```yaml
target: local
environments:
  local:
    # base_url is the API host on port 4001 — NOT the app host (3.basecamp.localhost:3001).
    base_url: "http://3.basecampapi.localhost:4001"
    launchpad_url: "http://launchpad.localhost:3011"
    # 37signals launchpad ships these as the "bcq" fixture client — use as-is.
    oauth_client_id: "bcq_dev_client_id_37signals_local"
    oauth_client_secret: "bcq_dev_client_secret_37signals_local"
```

> **Host split:** local dev serves the app on `3.basecamp.localhost:3001` and the
> API on `3.basecampapi.localhost:4001` (mirroring production's `3.basecamp.com`
> vs `3.basecampapi.com`). `base_url` must point at the **API** host/port, or every
> call 404s. The account ID is the same in both URLs.

The CLI's built-in OAuth client only exists in production launchpad. For
**37signals local dev** you don't need to register anything: launchpad ships
a stock fixture OAuth app named **bcq** (Basecamp CLI), already wired to the
CLI's redirect URI — just use the `oauth_client_id` / `oauth_client_secret`
above.

For **staging or a non-fixture launchpad**, register your own app instead:
open `<launchpad_url>/integrations/new`, set the **Redirect URI** to exactly
`http://127.0.0.1:8976/callback`, and copy the resulting Client ID / Secret
into the block above.

`bin/bcscene-setup-personas` reads this, bakes `base_url` into each profile,
and exports the launchpad/OAuth env for the auth flow (re-applied at runtime
for token refresh). See **Targeting a local or staging Basecamp** in
[SETUP.md](SETUP.md) for more detail.

## Available scene actions

A scene step uses one of these actions:

- `chat-post` — post to a project chat (args: message, project)
- `todo-create` — create a todo (args: title, project, list, optionally
  description, assignee, due)
- `todo-complete` — complete a todo (args: todo_id)
- `comment` — comment on a target (args: target_id, message)
- `message-post` — post a message board entry (args: title, body, project)

To add new actions, edit `lib/executor.py`'s `ACTION_HANDLERS` dict.

## Limitations

- One scene at a time (no parallel execution — the CLI uses a
  per-machine profile store, so two scenes running at once could
  collide).
- No undo. Posts and todos created by a scene stay in Basecamp.
- Personas must be real Basecamp users. There's no way to fake
  activity from a user you don't have a real OAuth token for.

## Repo layout

```
bcscene/
├── bin/
│   ├── bcscene                    # scene runner
│   └── bcscene-setup-personas     # one-time profile creation
├── lib/
│   ├── cli_wrapper.py             # subprocess calls to basecamp CLI
│   ├── config.py                  # resolves the target environment (prod/local)
│   ├── executor.py                # runs a scene
│   └── loader.py                  # parses YAML
├── scenes/
│   └── morning-standup.yaml       # example scene
├── docs/
│   └── MEMORY.md                  # known gotchas with the basecamp CLI
├── personas.example.yaml          # template roster (Enormicom)
├── personas.blank.yaml            # template roster (for forks)
├── personas.yaml                  # your real roster (gitignored)
├── GUIDE.md                       # step-by-step walkthrough
├── SETUP.md                       # condensed setup reference
└── CLAUDE.md                      # context for Claude Code
```
