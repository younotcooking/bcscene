"""Wrapper for invoking the basecamp CLI as different profiles."""

import os
import subprocess
import json

import config


class BasecampError(Exception):
    pass


# Env-var overrides for a non-production target (local dev / staging), resolved
# once from personas.yaml. These let the basecamp CLI refresh OAuth tokens
# against the right launchpad at runtime. Empty for production / no roster, so
# the subprocess simply inherits the ambient environment as before.
try:
    _ENV_OVERRIDES = config.env_overrides(config.load_personas())
except Exception:
    _ENV_OVERRIDES = {}


def run(profile, args, dry_run=False):
    """Run a basecamp command as the given profile.

    Returns parsed JSON if the command supports --json, otherwise
    returns {"raw": <stdout>}.

    Raises BasecampError if the command fails. Surfaces the CLI's
    structured error from the JSON envelope when available.
    """
    cmd = ["basecamp", "-P", profile] + list(args) + ["--json"]

    if dry_run:
        print("  [dry-run] " + " ".join(cmd))
        return {"dry_run": True}

    env = {**os.environ, **_ENV_OVERRIDES} if _ENV_OVERRIDES else None
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)

    # Try to parse stdout as JSON regardless of exit code — the basecamp CLI
    # returns structured errors in the JSON envelope on failure.
    parsed = None
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError:
        pass

    # Treat as failure if either: non-zero exit OR JSON envelope says ok=false
    failed = result.returncode != 0
    if parsed and isinstance(parsed, dict) and parsed.get("ok") is False:
        failed = True

    if failed:
        # Build the most informative error message we can
        error_parts = []
        if parsed and isinstance(parsed, dict):
            if parsed.get("error"):
                error_parts.append(parsed["error"])
            if parsed.get("hint"):
                error_parts.append("Hint: " + parsed["hint"])
        if result.stderr.strip():
            error_parts.append(result.stderr.strip())
        if not error_parts:
            error_parts.append("(no error message; exit code {})".format(result.returncode))

        raise BasecampError(
            "basecamp -P {} {} failed:\n  {}".format(
                profile, " ".join(args), "\n  ".join(error_parts)
            )
        )

    if parsed is not None:
        return parsed
    return {"raw": result.stdout}
