# Known gotchas

A running log of non-obvious things we've learned about working with
the basecamp CLI and the BC3 API. Each entry is a separate markdown
file in this folder, with reproduction context and how to work around
the issue.

Add new entries here as they come up — both for future you and for
Claude Code (which reads this folder per `CLAUDE.md`'s instructions).

## Index

- [Basecamp `todos update --due` is silently broken](feedback_basecamp_todos_update_due.md) —
  CLI reports success but doesn't apply the due date; use raw API PUT instead.
- [Basecamp todo PUT clobbers unsent fields](feedback_basecamp_todo_put.md) —
  PUT on a BC3 todo replaces unsent fields; always include all fields you want preserved.
- [Basecamp @mentions in HTML bodies](feedback_basecamp_mentions.md) —
  Markdown mention syntax doesn't work in HTML bodies; embed raw
  `<bc-attachment content-type="application/vnd.basecamp.mention">` instead.
- [basecamp chat post `--room` flag](feedback_basecamp_chat_room_flag.md) —
  For projects with multiple chat rooms, specify with `--room <id>`
  (not `--campfire`, which is a command alias).
- [Local/staging launchpad needs a registered OAuth client](feedback_local_launchpad_oauth.md) —
  The CLI's built-in OAuth client is production-only; register your own app in
  the local launchpad and set `BASECAMP_LAUNCHPAD_URL` + client id/secret
  (37signals local dev ships the `bcq` fixture client for this).
- [Local dev API host is a different host AND port than the app](feedback_local_dev_api_host.md) —
  `base_url` must be `http://3.basecampapi.localhost:4001`, not the app host
  on `:3001`; wrong host/port makes every API call 404.
- [`people add` needs BC3 person IDs, not launchpad identity IDs](feedback_people_add_person_ids.md) —
  Use IDs from `people list`, not from `me`; the wrong ID reports success but
  grants no access.

## How to add a new gotcha

1. Make a new file: `feedback_<short_name>.md`
2. Include: what you observed, why it's worth remembering, how to apply the fix
3. Add it to the index above
4. Commit

Format roughly:

    ---
    name: short title
    description: one-line description
    type: feedback
    ---

    [paragraph describing the issue]

    **Why:** [context for why we know this — what burned us]

    **How to apply:** [the workaround or correct invocation]
