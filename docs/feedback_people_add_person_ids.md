---
name: people add needs BC3 person IDs, not launchpad identity IDs
description: basecamp people add expects the project/account's BC3 person ID (from `people list`), not the launchpad identity ID returned by `me`. Using the wrong ID reports success but grants no access.
type: feedback
---

A freshly created project only includes its creator. To let other personas post (chat, todos, comments), grant them access with `basecamp -P <owner> people add <person-id>... --in <project>`. The `<person-id>` must be the **BC3 person ID** — get it from `basecamp -P <owner> people list` — **not** the launchpad identity ID returned by `basecamp -P <persona> me` (`.data.identity.id`). The two ID spaces are different numbers for the same human.

**Why:** Granting access with the identity IDs from `me` returned `{"ok":true}` from `people add`, but the targeted personas then got `Access denied` (chat/comments) and `resource not found` (todos) on that project — because `people add` had been handed IDs that didn't correspond to those people as BC3 persons. The success envelope made it look like access was granted when it wasn't.

**How to apply:** Resolve BC3 person IDs first: `basecamp -P <owner> people list --json | jq -r '.data[] | "\(.id)\t\(.name)"'`, map by name, then `basecamp -P <owner> people add <bc3_id1> <bc3_id2> ... --in <project_id>`. Verify a granted persona can actually act (e.g. post a chat) before bulk-populating — a correct grant takes effect immediately.
