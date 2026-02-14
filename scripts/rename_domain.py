#!/usr/bin/env python3
"""Rename template domain.

This script is intentionally simple and uses a controlled set of replacements.
Review changes after running.
"""

from __future__ import annotations

import argparse
import pathlib


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--old", required=True, help="Old domain (e.g. hacs_template)")
    p.add_argument("--new", required=True, help="New domain (e.g. my_integration)")
    p.add_argument("--name", required=True, help='Integration name (e.g. "My Integration")')
    return p.parse_args()


def replace_in_file(path: pathlib.Path, old: str, new: str, old_name: str, new_name: str) -> bool:
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False

    updated = raw.replace(old_name, new_name).replace(old, new)
    if updated == raw:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    args = parse_args()
    repo_root = pathlib.Path(__file__).resolve().parents[1]

    old = args.old.strip()
    new = args.new.strip()
    old_name = "HACS Template"
    new_name = args.name.strip()

    if not old or not new or old == new:
        raise SystemExit("Invalid --old/--new")

    # 1) Rename folder
    old_dir = repo_root / "custom_components" / old
    new_dir = repo_root / "custom_components" / new
    if old_dir.exists() and not new_dir.exists():
        old_dir.rename(new_dir)

    # 2) Replace contents
    for path in repo_root.rglob("*"):
        if path.is_dir():
            continue
        if ".git/" in str(path):
            continue
        replace_in_file(path, old, new, old_name, new_name)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

