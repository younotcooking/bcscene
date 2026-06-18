# Getting started with bcscene

A friendly walkthrough for first-time users.

## What this does

bcscene lets you make multiple Basecamp personas (Liza, Alex, Chris,
etc.) chat, post messages, and create todos in your demo account —
without you manually logging in as each one. You describe what you
want in plain English (or write a "scene" file), and bcscene makes the
activity happen in Basecamp.

It's mainly used for producing demo content: videos, screenshots, and
keeping the demo account looking lived-in.

## How you'll actually use it

The recommended day-to-day workflow uses **Claude Desktop's Code tab**
(which runs Claude Code, an AI assistant that has access to your files
and terminal). You'll open Claude Desktop, switch to the Code tab,
launch a Claude Code session in the bcscene folder, and just describe
the scene you want. Claude figures out which personas to use and runs
the right commands.

This is the modern bcscene workflow. Older bcscene used a similar
setup but managed personas more painfully — the new version uses the
official basecamp CLI's profile system, which is much cleaner.

> **Important: don't use Claude Desktop's regular chat with the
> Basecamp connector for this.** That posts everything as you (your
> own account), not as personas. The Code tab is the one that runs
> Claude Code, which uses bcscene's persona profiles. We'll show you
> exactly which tab to click.

## Before you start

You'll need:

- About 45 minutes of focused time the first time through. Most of
  that is logging in as each persona one-by-one (the boring part).
- The login credentials for each persona you want to use. These are in
  1Password. When prompted for the persona, go into 1Password, search
  for the person's first name, then click on the result titled
  "Basecamp Demo."
- A Mac. (Linux works too, but this guide assumes Mac.)
- Claude Desktop installed (the chat app from Anthropic).
- Basecamp CLI installed.

You don't need to know git, Python, or what a YAML file is. We'll
explain everything.

## Skip-ahead checklist (for faster setup)

If you already have any of the prerequisites installed, you can skip
parts of Phase 1. Run these checks in Terminal to see what you've
already got:

| Run this | If it prints a version, skip |
|---|---|
| `brew --version` | Step 1 |
| `basecamp --version` | Step 2 |
| `yq --version` | Step 3 |
| `python3 -c "import yaml"` (silence = installed) | Step 4 |
| `gh --version` | Step 5 |
| `ls ~/Code/bcscene` (no errors = cloned) | Step 6 |

If all six checks pass, **skip directly to Phase 2** (configuring
personas).

Each step in Phase 1 also has its own "skip if you already have this"
note at the top.

## A note on the Terminal

Some setup steps happen in an app called **Terminal** — it comes with
macOS and lets you type commands instead of clicking. If you've never
used it, that's fine. We'll tell you exactly what to type.

To open it: press `Cmd+Space`, type "Terminal", press Return. A window
opens with a prompt that ends in `%` or `$`. That's where you type.

When this guide shows commands in boxes like this:

    cd ~/Code

...you type or paste them at the prompt and press Return.

**When commands ask for a password** (the Mac password or a website
password), the Terminal hides what you type. No dots, no asterisks,
just a blank space. That's normal. Type the password and press Return.

Once setup is done, you'll spend most of your time in Claude Desktop's
Code tab — not Terminal.

---

# Forking for a different Basecamp account (optional)

**Skip this section if you're using bcscene with 37signals' Enormicom
demo account** — the default setup already points at that. Continue
straight to Phase 1.

If you want to use bcscene against a different Basecamp account, the
easiest path is to **fork the repo** so you can customize it without
affecting upstream. Do this *before* Phase 1, then continue with the
rest of the guide using your fork instead of the original.

1. **Fork on GitHub.** Visit
   [github.com/younotcooking/bcscene](https://github.com/younotcooking/bcscene)
   and click the "Fork" button in the top right. GitHub creates a copy
   under your username (e.g., `yourname/bcscene`).

2. **In Phase 1 Step 6, clone *your fork* instead of the original.**
   When the guide tells you to run `gh repo clone younotcooking/bcscene`,
   use your fork instead:

       gh repo clone yourname/bcscene

3. **In Phase 2 Step 7, use the blank persona template.** When the
   guide tells you to copy `personas.example.yaml`, use the blank
   template instead:

       cp personas.blank.yaml personas.yaml

   Then edit `personas.yaml` to fill in your Basecamp account ID, a
   project ID for testing, and your personas. (If you'd rather start
   from the full Enormicom roster as a reference, use
   `personas.example.yaml` instead.)

4. **Everything else is the same.** Phase 1 install steps, Phase 3
   authorization, Phase 4 running scenes — all identical. Just
   substitute your personas for the Enormicom ones in any prompts.

Your fork is independent. Edit scenes, personas, docs however you
want — none of it affects upstream. If upstream gets new features
later and you want them, you can `git pull` from upstream into your
fork.

## Pointing at a local dev or staging Basecamp

The account doesn't have to be on production Basecamp. To target a local
dev (or staging) account, add a `target` + `environments` block to your
`personas.yaml` in Phase 2 — everything else in this guide is the same.
This is independent of forking.

    account_id: "181900405"        # the account ID in that environment
    target: local

    environments:
      local:
        base_url: "http://3.basecampapi.localhost:4001"   # API host (port 4001, not the app's 3001)
        launchpad_url: "http://launchpad.localhost:3011"
        # 37signals local dev ships the "bcq" fixture OAuth client — use it as-is,
        # no app registration needed:
        oauth_client_id: "bcq_dev_client_id_37signals_local"
        oauth_client_secret: "bcq_dev_client_secret_37signals_local"

Then run Phase 3 (`bin/bcscene-setup-personas`) normally — it reads this,
points the OAuth flow at your local launchpad, and bakes the API host into
each profile. See **Targeting a local or staging Basecamp** in
[SETUP.md](SETUP.md) for the full explanation (the app-vs-API host split,
and what to do for a launchpad without the `bcq` fixture).

---

# Phase 1: One-time setup

Do this once on your Mac. It takes about 15 minutes if you're starting
from zero, less if you skip steps from the checklist above.

## Step 1: Install Homebrew

> **Already have Homebrew?** Skip to Step 2. Verify with `brew --version`.

Homebrew is a tool for installing other tools. To check if you have it:

    brew --version

If it prints a version number (like `Homebrew 4.x.x`), skip to Step 2.

If it says "command not found," install it by pasting this command:

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/main/install.sh)"

It'll ask for your Mac password and take a few minutes. When it's
done, it usually prints two or three lines telling you to run extra
commands — do whatever those say. Then verify with `brew --version` again.

## Step 2: Install the basecamp CLI

> **Already have basecamp CLI?** Skip to Step 3. Verify with
> `basecamp --version` (should be 0.7.2 or higher).

The basecamp CLI is what bcscene uses to actually post things to
Basecamp.

    brew install basecamp/tap/basecamp

Verify:

    basecamp --version

You should see `basecamp version 0.7.2` or higher.

## Step 3: Install yq and jq

> **Already have yq and jq?** Skip to Step 4. Verify with `yq --version`
> and `jq --version`.

These help bcscene read configuration files.

    brew install yq jq

## Step 4: Install Python's YAML library

> **Already have pyyaml?** Skip to Step 5. Verify by running
> `python3 -c "import yaml"` — silence means it's installed.

Python is already on your Mac, but it needs a little extra to read YAML.

    pip3 install pyyaml

## Step 5: Install the GitHub CLI

> **Already have gh and authenticated?** Skip to Step 6. Verify with
> `gh --version` and `gh auth status`.

This makes downloading the bcscene repo easy.

    brew install gh

Then log in (it'll open a browser):

    gh auth login

Pick: GitHub.com → HTTPS → Yes (authenticate Git) → Login with web
browser. Follow the prompts.

## Step 6: Download bcscene

> **Already cloned the repo?** Skip to Phase 2. Verify with
> `ls ~/Code/bcscene` — should show files like `bin`, `lib`, etc.

Make a folder for code projects (if you don't already have one):

    mkdir -p ~/Code
    cd ~/Code

Download the bcscene repo:

    gh repo clone younotcooking/bcscene

Go into the new folder:

    cd bcscene

You're now in the bcscene folder. Verify with:

    ls

You should see files like `README.md`, `GUIDE.md`, `bin`, `lib`,
`scenes`, `personas.example.yaml`, and `CLAUDE.md`.

---

# Phase 2: Configure your personas

This tells bcscene which Basecamp personas you want to use.

## Step 7: Make your own personas file

Copy the template:

    cp personas.example.yaml personas.yaml

This creates `personas.yaml` — your personal copy. The template stays
unchanged. Your personal copy never gets uploaded to GitHub (it's
gitignored).

## Step 8: Edit your personas file

Open it with a simple editor called nano:

    nano personas.yaml

The bottom of the screen shows shortcuts. The two you need:

- **Ctrl+O** to save (then press Return when it asks the filename)
- **Ctrl+X** to exit

Use the arrow keys to move around. Edit these things:

- The line that says `account_id: "YOUR_ACCOUNT_ID"` — replace
  `YOUR_ACCOUNT_ID` with the demo Basecamp account ID. To find it: go
  to your demo Basecamp account in a browser. The URL looks like
  `https://3.basecamp.com/5185276/...`. The number after
  `3.basecamp.com/` is the account ID.

- The line that says `default_project_id: "YOUR_PROJECT_ID"` — replace
  with a project ID you'll use for testing. To find it: open a project
  in Basecamp. The URL has the project ID at the end.

- The personas list — leave it alone for now, or delete personas you
  don't need. **Each persona requires a separate login during setup,
  so fewer = faster setup.** A reasonable approach: start with 3 to
  validate things work, then come back later and add the rest.

Save with **Ctrl+O**, press Return, exit with **Ctrl+X**.

---

# Phase 3: Authorize each persona

This is the longest part. For each persona, you'll log into Basecamp
once and authorize bcscene. The basecamp CLI saves the login so you
never have to do it again (until tokens expire after a long period of
inactivity).

## Step 9: Log out of Basecamp in your browser

Important: log out of any Basecamp session you have open as yourself.
The setup script will open browser windows to authorize each persona —
if you're already logged in as yourself, it'll authorize you instead
of the persona. Bad.

## Step 10: Run the setup script

    bin/bcscene-setup-personas

For each persona in your file, the script will:

1. Print "Press Return to continue."
2. Wait for you.

When you press Return:

3. The basecamp CLI opens a browser window.
4. Log in with that persona's credentials (from 1Password).
5. Click "Authorize" when Basecamp asks.
6. The CLI captures the login. You return to the Terminal.
7. **Log that persona out of Basecamp** before pressing Return for the
   next one. Otherwise the next persona gets logged in as the previous
   one. (To log out: avatar in top-right → Log out.)

Repeat until done. Don't rush — getting the wrong identity attached to
a profile is annoying to undo.

> **Need a break, or want to verify a persona before continuing?**
>
> Press **Ctrl+C** at any "Press Return to continue" prompt to exit
> the script. You can then run any verification command (e.g.,
> `basecamp profile list`, or `basecamp -P alex me` to check who a
> profile is authenticated as).
>
> When you're ready to resume, just run `bin/bcscene-setup-personas`
> again — it picks up where you left off. Already-authorized personas
> get skipped automatically.

## Step 11 (recommended): Test before authorizing the rest

After authorizing your first 3 personas, take a break and verify
everything works end-to-end before slogging through the remaining 19.
This catches any setup issues early — and gives you a small win.

1. Press **Ctrl+C** to exit the setup script (it'll resume later).
2. Verify the 3 personas show up:

       basecamp profile list

3. **Open Claude Desktop.**
4. Click the **Code** tab.
5. In its terminal area, type:

       cd ~/Code/bcscene
       claude

6. Once Claude Code loads, give it a plain-English prompt using the 3
   personas you just authorized. For example, if your first 3 were
   alex, chris, christina:

   > "Have alex post a message asking what everyone's working on,
   > then chris replies with something they're stuck on, then
   > christina jumps in to help. Use our test project."

7. Claude Code should ask for a project ID, then dry-run the scene,
   then post for real on your approval. Watch your Basecamp project
   to confirm.

If that worked, great — return to Terminal and re-run
`bin/bcscene-setup-personas` to authorize the rest. If something
broke, fix it now while the setup is fresh in your mind.

## Step 12: Verify everything

Once all personas are authorized:

    basecamp profile list

You should see one row per persona, all marked "yes" under
Authenticated.

To make sure each profile is actually a different identity (not all
secretly you), pick one and run:

    basecamp -P liza me

Replace `liza` with whichever persona you want to check. It'll print a
name and email. The name and email should match that persona — not
your name. Repeat for any others you want to spot-check.

---

# Phase 4: Run scenes from Claude Desktop

This is the day-to-day workflow. From here on, you describe scenes in
plain English in Claude Desktop's Code tab.

## Step 13: Open Claude Code in the bcscene folder

> **Skip if you already did this in Step 11.** Same workflow.

1. Open **Claude Desktop**.
2. Click the **Code** tab.
3. The Code tab gives you a terminal-like input. Type:

       cd ~/Code/bcscene

   Press Return.

4. Then type:

       claude

   Press Return.

This launches a Claude Code session that knows about your bcscene
repo, your personas, and the scene format. The repo includes a
`CLAUDE.md` file that primes Claude Code on how bcscene works.

## Step 14: Describe a scene in plain English

Examples:

- **Replay a saved scene:** "Run the morning-standup scene file in
  scenes/."
- **Original scenes:** "Have Liza, Sara, and Marco have a debate about
  whether to use Postgres or MySQL. Make it last 6-8 messages."
- **Ambient activity:** "Make 4 random personas post something
  realistic about their day in our project."
- **Variations:** "Run morning-standup again but make Alex's blocker
  about a different topic."

Claude Code will:

1. Ask you which project to use if you didn't specify.
2. Generate the scene, dry-run it for preview, ask for approval.
3. On your approval, run the scene live. Posts and todos appear in
   Basecamp under the right personas.

If you're confident and want to skip the dry-run, just say "skip the
dry-run and run it directly."

## Step 15: Watch it happen

Open Basecamp in your browser, navigate to the project, and watch the
chat fill in as Claude executes the scene. The whole thing takes 5-10
seconds.

Done!

---

# Guide to prompting scenes successfully

Once setup is done, the real skill is writing prompts that get Claude
to do what you actually want — quickly, cleanly, without wrecking
existing projects. Here's what works.

## Start small (and somewhere safe)

If you're new to bcscene, **don't start by prompting against your main
demo project.** Make a fresh test project in your demo Basecamp
account and aim your first few prompts at that. You'll figure out
prompting style without risking work-in-progress on real projects.

Once you're comfortable, you can point bcscene at any project you want.

## Always start a session the same way

Every Claude Code session for bcscene starts with these two commands
in Claude Desktop's Code tab:

```
cd ~/Code/bcscene
claude
```

> **Then your very first prompt must specify which Basecamp account to work in.** Even if you've set a default profile, always name the account explicitly — by name *and* ID number. This protects you from accidentally posting to the 37signals account or a wrong project. Example:
>
> > "We're working in the Enormicom Demo account (5185276)."

Then in your *next* prompt (or in the same one, just after that
sentence), specify the project — ideally name *and* ID:

> "...in the Logo Redesign project (23913601)."

These two anchors at the start of a session are cheap insurance
against expensive mistakes.

## Prompting tips

- **Name the personas explicitly.** "Have alex, chris, and christina discuss..." beats "have a few people discuss..." — Claude won't guess which personas to use.
- **Use Basecamp terminology for actions.** Say "to-dos," "subtasks," "card," "comments below," "boost," "schedule entry." Claude maps these directly to CLI commands. Vague verbs like "post stuff" or "make things happen" produce vague results.
- **Cap each prompt at 4-5 tasks max.** Long prompts with 10+ actions get partially lost in translation. Smaller prompts succeed at a much higher rate.
- **Build on prompts when one would get unwieldy.** Most prompts should be one prompt — don't split things up just to split them. But when you'd be cramming in 8+ actions, or stacking unrelated work ("make this campfire thread *and* set up a card table for a different feature"), break it up. Run the first piece, see the result, then add to it. Claude tracks better and you can course-correct mid-stream.
- **Work *with* Claude, not at it.** If something isn't quite right, say so — Claude will fix it. Don't try to predict every edge case in your initial prompt; iteration is faster.

## Worked examples

**Bad prompt** (overloaded, vague):

> "Make a bunch of activity in our project — have everyone do stuff, add todos, have people comment, make it look real."

**Better prompt** (anchored, specific, well-scoped):

> "We're in Enormicom Demo (5185276), Logo Redesign project (23913601). Have liza post a message in the campfire asking for logo references, have kurt and harper each reply with a sentence, then add 3 to-dos assigned to kurt with deadlines next week — 'Pull reference logos,' 'Sketch direction options,' 'Share with Liza for feedback.'"

**A scene-style prompt** (good for video shoots, more structured):

> "We're in Enormicom Demo (5185276), Marketing Site Refresh (23913601). Run a 4-step scene with 3-second pauses: alex posts 'Standup time, what's everyone on?' in the campfire, chris replies they're stuck on the hero copy, christina says she'll help, then christina creates a to-do 'Pair with chris on hero copy' assigned to herself."

## When something goes wrong

- **Claude accidentally cleared other info inside a message, to-do, or card.** This happens occasionally. Just tell Claude — "you removed the existing description, can you put it back?" — and it will recognize the mistake and restore it.
- **You ran a prompt and want to undo it.** Ask Claude to undo the previous action. It can delete posts, todos, comments, and cards it just created. Mention what you want undone specifically (e.g., "undo that last to-do, but leave the chat post").

The general rule: **anything you can describe, Claude can fix.** Talk
to it.

---

# Common needs

## Pacing for video

If you're recording and want viewers to register each action:

> "Run morning-standup with 5-second pauses between steps."

## Saving scenes for reuse

> "Make a scene where Liza onboards a new team member, three personas welcome them, and someone creates a 'review onboarding doc' todo. Save it as scenes/onboarding.yaml so I can run it again later."

Once saved, you can just say "run scenes/onboarding.yaml" anytime.

## Adding a new persona later

If a new persona gets added to the demo account and you want to use
them in scenes:

1. Open `personas.yaml` in nano:

       nano personas.yaml

2. Add the new persona at the bottom of the `personas:` list,
   following the same format as existing entries:

       - name: newperson
         display_name: "New Person"
         email: newperson@enormicom.com

3. Save and exit (Ctrl+O, Return, Ctrl+X).

4. Re-run the setup script:

       bin/bcscene-setup-personas

   It'll skip everyone you already authorized and just OAuth the new
   persona.

## Fixing a persona authorized as the wrong identity

If `basecamp -P liza me` returns your name instead of Liza's (or any
persona's profile is attached to the wrong account), you OAuth'd the
wrong session. Fix it:

1. Delete the broken profile:

       basecamp profile delete liza

2. Make sure you're logged out of Basecamp in your browser.

3. Re-run the setup script:

       bin/bcscene-setup-personas

   It'll skip authorized personas and re-OAuth just `liza`. Pay
   attention to the browser this time — make sure the right persona
   is logging in.

## Changing the default persona

The "default" persona is who acts when you run `basecamp` commands
*without* specifying `-P <name>`. bcscene itself doesn't care about
the default — every scene step is explicit about who's acting. The
default only matters for ad-hoc commands you type yourself (e.g.,
`basecamp todolists --in 23913601`).

To change the default:

    basecamp profile set-default <name>

To see the current default:

    basecamp profile show

> **Tip:** Many people register their *own* Basecamp identity as a
> profile and set it as the default. That way, ad-hoc commands act as
> you instead of as a fictional persona — useful for looking up
> project IDs, todolist IDs, and so on.
>
> To register yourself, add yourself to `personas.yaml` like any other
> persona (use your real name and email), run
> `bin/bcscene-setup-personas` (it'll OAuth you), then:
>
>     basecamp profile set-default <yourname>

## Writing scenes by hand (instead of asking Claude)

If you prefer to write scenes as YAML files yourself, see `SETUP.md`
in the repo for the format and full action reference. Then run them
with `bin/bcscene scenes/your-scene.yaml`.

---

# When something goes wrong

## "command not found"

The Terminal doesn't recognize what you typed. Either:

- You misspelled it. Check the spelling.
- You skipped an install step. Go back to Phase 1 and check the
  skip-ahead checklist to figure out what's missing.

## "No such file or directory" when running bcscene commands

You're not in the bcscene folder. Terminal opens new windows in your
home directory by default, so any time you start a fresh window you
need to navigate back:

    cd ~/Code/bcscene

Confirm you're in the right place with `pwd` — it should print
`/Users/<yourname>/Code/bcscene`.

## "permission denied" when running scripts

Fix it with:

    chmod +x bin/bcscene bin/bcscene-setup-personas

Then try again.

## A scene fails partway through

Steps that already ran stay in Basecamp — bcscene doesn't undo
anything. Either ask Claude to clean up (it can delete posts and
todos), or clean up manually in Basecamp's UI. Then re-run the part
that failed.

## "No todolist specified"

A scene's `todo-create` step is missing the `list` field. Either ask
Claude to fix it, or find a todolist ID with:

    basecamp -P <persona> todolists --in <project_id>

...and add it to the scene file.

## Claude Desktop's chat says "I can only post as you"

You're in the wrong tab. The regular chat with the Basecamp connector
posts via API as your account, which can't be different personas.
Switch to the **Code tab** instead — that runs Claude Code, which uses
bcscene's persona profiles.

## Everything is broken and I don't know why

Ping Chad — that's me. Or open an issue on the repo:
https://github.com/younotcooking/bcscene/issues
