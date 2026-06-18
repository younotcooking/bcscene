---
name: local dev API host is a different host AND port than the app
description: For local dev, base_url must be the API host 3.basecampapi.localhost:4001 — not the app host 3.basecamp.localhost:3001. Pointing at the app host/port makes every API call 404.
type: feedback
---

Local Basecamp dev splits the app and the API across different hosts *and* ports, mirroring production's `3.basecamp.com` (app) vs `3.basecampapi.com` (API):

- **App:** `http://3.basecamp.localhost:3001/<account_id>` (what you see in the browser)
- **API:** `http://3.basecampapi.localhost:4001/<account_id>` (what the CLI must talk to — the `API_PORT`, default 4001, per bc3 `lib/bc3.rb`)

The CLI builds `<base_url>/<account_id>/projects.json`, so `base_url` must be the API host:port. The account ID is the same in both URLs (extracted from the path by bc3's `AccountSlug::Extractor` middleware — any 7+ digit leading segment).

**Why:** Setting `base_url` to the app host (`http://3.basecamp.localhost:3001`, copied from the browser URL) made every API call return `resource not found`/404 — even listing projects — while OAuth still succeeded (auth goes through launchpad, a third host). The 404 looked like an empty account or an auth problem; it was the wrong API host/port. An authenticated request to the app host gets a 302→signin or 404 because bc3 only treats the configured `api_host` as an API request.

**How to apply:** In bcscene's `personas.yaml`, set `environments.<name>.base_url: "http://3.basecampapi.localhost:4001"`. To sanity-check a token+host combo directly: `curl -H "Authorization: Bearer $(basecamp -P <persona> auth token | tr -d '\"')" -H "Accept: application/json" http://3.basecampapi.localhost:4001/<account_id>/projects.json` should return 200 with JSON.
