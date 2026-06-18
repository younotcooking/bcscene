"""Resolve which Basecamp environment a roster targets.

`personas.yaml` may declare a non-production target (local dev / staging) via a
`target:` selector and a named `environments:` map. This module is the single
source of truth for that resolution — consumed both by the Python runtime
(`cli_wrapper.py`, for token-refresh env vars) and by the bash setup script
(`bin/bcscene-setup-personas`, via the `__main__` CLI below).

Omitting `target:`/`environments:` (or `target: production`) yields no overrides,
so the basecamp CLI uses its production defaults — identical to legacy behavior.
"""

import os
import shlex
import sys

import yaml

# Env vars the basecamp CLI reads to target a non-production OAuth flow. The API
# host is NOT among these — it's baked into each profile via `--base-url` at
# `profile create` time — so runtime only needs these three for token refresh.
ENV_LAUNCHPAD = "BASECAMP_LAUNCHPAD_URL"
ENV_CLIENT_ID = "BASECAMP_OAUTH_CLIENT_ID"
ENV_CLIENT_SECRET = "BASECAMP_OAUTH_CLIENT_SECRET"

# Fields a non-production environment must define.
_ENV_FIELDS = ("base_url", "launchpad_url", "oauth_client_id", "oauth_client_secret")


class ConfigError(Exception):
    """Raised when personas.yaml declares an unusable target."""


def _repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _personas_path(repo_root=None):
    override = os.environ.get("BCSCENE_PERSONAS")
    if override:
        return override
    return os.path.join(repo_root or _repo_root(), "personas.yaml")


def load_personas(repo_root=None):
    """Load personas.yaml. Returns the parsed dict, or None if the file is absent.

    Runtime callers must degrade gracefully when there's no roster (→ production).
    """
    path = _personas_path(repo_root)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return yaml.safe_load(f) or {}


def _is_placeholder(value):
    """True if a config value is empty or an untouched template placeholder."""
    if value is None:
        return True
    s = str(value).strip()
    if not s:
        return True
    return s == "REGISTER_AND_PASTE" or s.startswith("YOUR_") or s == "..."


def _selected_target(cfg):
    if not cfg:
        return "production"
    return (cfg.get("target") or "production").strip()


def resolve(cfg):
    """Resolve the selected environment into a flat dict.

    Returns keys: target, account_id, base_url, launchpad_url, oauth_client_id,
    oauth_client_secret. Unset overrides are None (→ CLI defaults).

    Raises ConfigError for an unknown target name or a non-production target that
    is missing required fields (used by the setup CLI to fail fast).
    """
    cfg = cfg or {}
    target = _selected_target(cfg)
    resolved = {
        "target": target,
        "account_id": cfg.get("account_id"),
        "base_url": None,
        "launchpad_url": None,
        "oauth_client_id": None,
        "oauth_client_secret": None,
    }

    if target == "production":
        return resolved

    environments = cfg.get("environments") or {}
    if target not in environments:
        raise ConfigError(
            "target '{}' is not defined under 'environments:' in personas.yaml. "
            "Add it, or set 'target: production'.".format(target)
        )

    env = environments.get(target) or {}
    if env.get("account_id"):
        resolved["account_id"] = env["account_id"]
    for key in _ENV_FIELDS:
        resolved[key] = env.get(key)

    missing = [k for k in _ENV_FIELDS if _is_placeholder(resolved[k])]
    if missing:
        raise ConfigError(
            "environment '{}' is missing required field(s): {}. Fill these in under "
            "environments.{} — see 'Targeting a local or staging Basecamp' in SETUP.md "
            "(37signals local dev can use the stock 'bcq' fixture client).".format(
                target, ", ".join(missing), target
            )
        )

    return resolved


def env_overrides(cfg):
    """Env-var overrides to inject for the selected target.

    Lenient: returns only the launchpad/oauth vars that are actually set and
    non-placeholder. Production (or no roster) → {}. Does not raise on missing
    fields, so runtime injection never crashes a partially-configured roster
    (the basecamp CLI surfaces its own auth error instead).
    """
    cfg = cfg or {}
    if _selected_target(cfg) == "production":
        return {}
    try:
        environments = cfg.get("environments") or {}
        env = environments.get(_selected_target(cfg)) or {}
    except AttributeError:
        return {}

    overrides = {}
    mapping = (
        (ENV_LAUNCHPAD, env.get("launchpad_url")),
        (ENV_CLIENT_ID, env.get("oauth_client_id")),
        (ENV_CLIENT_SECRET, env.get("oauth_client_secret")),
    )
    for name, value in mapping:
        if not _is_placeholder(value):
            overrides[name] = str(value).strip()
    return overrides


def _main(argv):
    import argparse

    p = argparse.ArgumentParser(
        description="Resolve the Basecamp environment declared in personas.yaml."
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--target", action="store_true", help="Print selected target name")
    group.add_argument("--account-id", action="store_true", help="Print resolved account_id")
    group.add_argument("--base-url", action="store_true", help="Print resolved base_url (empty for production)")
    group.add_argument("--env-exports", action="store_true", help="Print shell `export` lines for launchpad/oauth vars")
    args = p.parse_args(argv)

    cfg = load_personas()
    try:
        resolved = resolve(cfg)
    except ConfigError as e:
        sys.stderr.write("✗ {}\n".format(e))
        return 1

    if args.target:
        print(resolved["target"])
    elif args.account_id:
        print(resolved["account_id"] or "")
    elif args.base_url:
        print(resolved["base_url"] or "")
    elif args.env_exports:
        for name, value in env_overrides(cfg).items():
            print("export {}={}".format(name, shlex.quote(value)))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
