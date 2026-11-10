#!/usr/bin/env python3
"""Find the paper project a hook should write to, and say why it chose it.

TWO LAYOUTS, ONE RULE

A paper project can sit in either of two places, and a hook has to work in both:

  project is the session root          project is a child of the session root
  <root>/.claude/hooks/                <root>/.claude/hooks/
  <root>/submission/                   <root>/my-paper/submission/
  <root>/pipeline-config.md            <root>/my-paper/pipeline-config.md

The second layout exists because Claude Code resolves three things from the
session root and only the session root: skills in `.claude/skills/`, servers in
`.mcp.json`, and hooks in `.claude/settings.json`. Putting the hooks beside the
paper instead meant the session root could satisfy the hooks or the skills but
never both, and launching from the wrong one failed silently. So the hooks live
at the root with everything else, and this module finds the paper underneath.

WHY AMBIGUITY IS LOUD

With more than one paper under a root there is no honest way to guess which one
a session is about, and guessing wrong writes one paper's transcripts into
another's compliance record. That is worse than not logging, so this refuses and
says so. One paper per clone is the supported arrangement; a second paper gets a
second clone, which costs a few megabytes and removes the question.

    python3 project_root.py --doctor    # print the decision and the reason
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

MARKERS = ("submission", "pipeline-config.md")


TEMPLATE_DIR = "project-template"


def _is_project(d: Path) -> bool:
    """A paper project carries a submission package and a CONFIGURED pipeline config.

    Both halves matter. The shipped template carries the same two files, so a
    structural test alone counts it as a paper and then calls every real project
    ambiguous. A project becomes real when someone sets `project_name`, which is
    the first thing the setup instructions ask for, so an unconfigured copy is
    correctly ignored until it is actually a paper.
    """
    if d.name == TEMPLATE_DIR:
        return False
    if not ((d / "submission").is_dir() and (d / "pipeline-config.md").is_file()):
        return False
    try:
        for line in (d / "pipeline-config.md").read_text(errors="ignore").splitlines():
            if line.startswith("project_name:"):
                value = line.split(":", 1)[1].split("#")[0].strip()
                return bool(value) and not value.startswith("<")
    except Exception:
        return False
    return False


def resolve(hook_file: str | None = None) -> tuple[Path | None, str]:
    """Return (project_dir, reason). project_dir is None when a hook must not write.

    Never raises: a hook that dies takes the session's turn with it.
    """
    try:
        env = os.environ.get("CLAUDE_PROJECT_DIR")
        root = None

        if env:
            envp = Path(env)
            # Layout 1: the session root IS the paper project.
            if (envp / "submission").is_dir():
                return envp, "CLAUDE_PROJECT_DIR is itself a paper project"
            root = envp

        if root is None:
            base = Path(hook_file or __file__).resolve()
            # <root>/.claude/hooks/<file>.py
            root = base.parents[2]

        if (root / "submission").is_dir():
            return root, f"the session root is itself a paper project ({root.name})"

        # Layout 2: find the paper under the root.
        candidates = sorted(
            d for d in root.iterdir()
            if d.is_dir() and not d.name.startswith(".") and _is_project(d)
        )
        if len(candidates) == 1:
            return candidates[0], f"one paper project under the session root ({candidates[0].name})"
        if not candidates:
            return None, (f"no configured paper project under {root}; nothing to record "
                          f"yet. A project is a copy of {TEMPLATE_DIR}/ with project_name set.")
        names = ", ".join(c.name for c in candidates)
        return None, (f"{len(candidates)} paper projects under {root} ({names}). "
                      f"Refusing to guess which one this session is about: writing to the "
                      f"wrong one would corrupt a compliance record. Keep one project per "
                      f"clone, or set CLAUDE_PROJECT_DIR to the project you mean.")
    except Exception as exc:  # never take the turn down with us
        return None, f"project resolution failed: {exc!r}"


def resolve_or_none(hook_file: str | None = None) -> Path | None:
    project, reason = resolve(hook_file)
    if project is None and "nothing to record yet" not in reason:
        # Ambiguity and errors are worth a line; an empty clone is not.
        print(f"[pipeline hooks] not recording: {reason}", file=sys.stderr)
    return project


def main() -> int:
    project, reason = resolve()
    print(f"project: {project if project else '(none)'}")
    print(f"reason:  {reason}")
    return 0 if project else 1


if __name__ == "__main__":
    sys.exit(main())
