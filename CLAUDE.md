# bcscene context for Claude Code

This file gives you (Claude Code) the context you need to help users
run bcscene scenes. Read it on session start; you don't need to ask
the user to re-explain bcscene.

## What bcscene is

bcscene runs scripted multi-persona activity in a Basecamp demo
account. The user describes what each persona should do; bcscene
invokes the basecamp CLI as a different authenticated profile per
persona to make the activity actually happen as those identities.

The user normally interacts with you in plain English ("have Liza post
about X, then Alex respond"). You translate that into the right
basecamp CLI commands and run them.

## Repo layout

- `personas.yaml` — the user's roster of personas (gitignored, local
  to this machine). Read this to know which personas exist.
  `personas.example.yaml` is the template; ignore it for runtime.
  It may also declare a non-production `target:` + `environments:`
  block (local dev / staging); `lib/config.py` resolves it and the
  rest of the workflow is unchanged. Omitting it means production.
- `scenes/` — saved scene files in YAML. Read existing scenes for
  format examples; save new scenes here when the user asks you to.
- `bin/bcscene <scene-file>` — runs a saved scene file end to end.
- `lib/executor.py` — defines available actions if you need to look up
  syntax. The actions are: `chat-post`, `todo-create`, `todo-complete`,
  `comment`, `message-post`. See the file for arg shapes.

## How to run actions

Two ways, both fine:

1. **Direct CLI calls.** Run `basecamp -P <persona> <verb> <args>` for
   each step. Good for ad-hoc activity that doesn't need a saved
   scene file. Always include `--json` so errors come back parseable.

2. **Saved scene files.** Build a YAML file matching the format in
   `scenes/morning-standup.yaml`, then run `bin/bcscene <path>`. Good
   when the user wants reusability.

## Available CLI verbs (most common)

- `basecamp -P <persona> chat post "<message>" --in <project_id>`
- `basecamp -P <persona> todo "<title>" --in <project_id> --list <todolist_id>`
- `basecamp -P <persona> message post "<title>" "<body>" --in <project_id>`
- `basecamp -P <persona> todolists --in <project_id>` (list todolists in a project)
- `basecamp profile list` (see all configured personas)
- `basecamp -P <persona> me` (see who a profile is authenticated as)

When uncertain about a verb's exact syntax, run `basecamp <verb> --help`
to check.

## Things to ask the user about (don't guess)

The user may give you a prompt that's missing key details. **Ask for
clarification rather than guessing** when:

- **Project ID is missing.** There's no default project. Always ask
  which Basecamp project the scene should happen in.
- **Todolist ID is missing for a `todo-create` step.** The basecamp
  CLI requires `--list` for todos. Either ask the user, or ask if
  you can look up the todolists in the project and pick one (and
  confirm before posting).
- **Persona doesn't exist in personas.yaml.** Don't substitute a
  similar name. Tell the user the persona isn't authorized and ask
  who they meant.
- **Action is ambiguous.** "Have Alex respond" — respond with what?
  Either ask, or propose specific content and let the user approve.
- **Multiple things could match.** "Run the standup scene" when
  there are three standup-related scene files — ask which one.

## Dry-run policy

- **Existing scene file the user already wrote and is asking to
  run** → just run it. No dry-run unless the user asks. They've
  already reviewed it.
- **You're generating new content from a prompt** ("have Liza post
  about X") → dry-run first, show the user the planned messages,
  then run for real on their approval. Invented content has more
  failure modes (wrong attribution, awkward phrasing, wrong
  project) and a 2-second preview catches them cheaply.
- **User explicitly says skip dry-run** → respect that. Don't
  re-prompt for confirmation if they've said go.

## Things that are not undoable

Basecamp doesn't have undo. Once a chat is posted, a todo is created,
or a message is filed, it's there. The user (or you) can manually
delete things, but the action of "posting" can't be reversed. This is
why dry-run for invented content is the default — it's cheap insurance.

If a scene fails partway, already-completed steps stay completed. Help
the user clean up via deletion if they want, or just acknowledge what
landed and what didn't.

## Tone for invented content

Personas should feel like real coworkers having normal Basecamp
conversations. Avoid: overly formal language, perfect grammar, every
message ending with a question, robotic transitions. Lean into:
contractions, mild typos occasionally, casual sign-offs, references
to "the call" or "yesterday" without explanation, normal-length
messages (not paragraphs). Vary persona voices — not all crisp PMs,
not all rambling engineers. The user will tell you if a persona has a
particular voice they want; otherwise vary it naturally.

## Known gotchas

Before making non-trivial changes to Basecamp content (especially
todos, mentions, HTML bodies, or chat posts in multi-room projects),
**read `docs/MEMORY.md`** — it indexes a small set of basecamp-CLI and
BC3 API gotchas that have burned past sessions. Each entry has a
"How to apply" section with the correct invocation.

When you discover a new gotcha worth remembering, add a feedback file
to `docs/` and link it from `docs/MEMORY.md`. The format is documented
at the bottom of that file.

## What to do if a CLI command fails

The basecamp CLI returns structured JSON errors when you use `--json`.
Read the `error` and `hint` fields, fix the command, and try again
without making the user debug. Common ones:

- "No todolist specified" → add `--list <todolist_id>`
- "Profile not authenticated" → tell the user to re-run
  `bin/bcscene-setup-personas`; their token may have expired
- "Project not found" → confirm the project ID is correct

If you can't fix it after one retry, surface the error to the user
plainly and ask how they want to proceed.
