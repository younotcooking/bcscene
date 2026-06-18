---
name: local/staging launchpad needs a registered OAuth client
description: The basecamp CLI's built-in OAuth client only exists in production launchpad; a local/staging launchpad rejects it with "Client not found". 37signals local dev ships the stock "bcq" fixture client; otherwise register your own. Point the CLI at it via env vars.
type: feedback
---

The basecamp CLI ships with a hard-coded OAuth client ID that is only registered in **production** launchpad (`launchpad.37signals.com`). Pointing the CLI at a local or staging launchpad (e.g. `http://launchpad.localhost:3011`) and running the OAuth flow fails with HTTP 400 `{"error":"Client not found. Register at https://integrate.37signals.com"}`. Setting `--base-url` alone is not enough — that only changes the API host; the OAuth/identity host and client are separate.

To authenticate against a non-production launchpad you need three things:

1. `BASECAMP_LAUNCHPAD_URL` — the launchpad host (e.g. `http://launchpad.localhost:3011`).
2. `BASECAMP_OAUTH_CLIENT_ID` / `BASECAMP_OAUTH_CLIENT_SECRET` — from an OAuth app you register **in that launchpad**, with redirect URI exactly `http://127.0.0.1:8976/callback` (the fixed port the CLI's local listener uses).
3. `--base-url` at `profile create` — the API host, baked into the profile.

**Why:** Setting up bcscene against a local dev account, every persona's OAuth flow 400'd until we discovered the production-only client. Worse, before `BASECAMP_LAUNCHPAD_URL` was set, the flow silently succeeded against *production* launchpad and minted real-identity tokens (verified with `basecamp -P <name> me` returning the production identity instead of the local seed user) — the profile looked authenticated but pointed at the wrong place.

**How to apply:** For 37signals **local dev** you don't need to register anything — launchpad seeds a fixture OAuth client named `bcq` ("Basecamp CLI") in the `signal_id` gem (`test/fixtures/signal_oauth_clients.yml`), with redirect URI already set to `http://127.0.0.1:8976/callback`. Use it directly: `oauth_client_id: bcq_dev_client_id_37signals_local`, `oauth_client_secret: bcq_dev_client_secret_37signals_local`. (Confirm it's live: an authorize request with that client_id should 302 to `/signin`, not 400 "Client not found".) For staging or a launchpad without the fixture, register your own app at `<launchpad>/integrations/new`. Either way, declare it in `personas.yaml` via `target:` + `environments:` and let `bin/bcscene-setup-personas` (through `lib/config.py`) export the env vars and pass `--base-url`; the same env is re-applied at runtime for token refresh. To verify identity after auth: `basecamp -P <persona> me` should return the local seed user, not your production account.
