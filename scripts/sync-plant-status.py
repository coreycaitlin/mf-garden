#!/usr/bin/env python3
"""Sync plant markdown status from plant-log.json.

For any log entry with a planted_date, sets the corresponding plant's
frontmatter status to "planted" (unless already "established").
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
LOG_FILE = REPO / "docs" / "plant-log.json"
PLANTS_DIR = REPO / "plants"

UPGRADE_FROM = {"planned", "purchased"}


def update_status(plant_file: Path, new_status: str) -> bool:
    """Update status in frontmatter. Returns True if changed."""
    text = plant_file.read_text()
    match = re.search(r'^(status:\s*)(["\']?\w+["\']?)', text, re.MULTILINE)
    if not match:
        return False
    current = match.group(2).strip("\"'")
    if current == new_status or current not in UPGRADE_FROM:
        return False
    updated = text[: match.start(2)] + f'"{new_status}"' + text[match.end(2) :]
    plant_file.write_text(updated)
    return True


def main():
    if not LOG_FILE.exists():
        print(f"Log file not found: {LOG_FILE}", file=sys.stderr)
        sys.exit(1)

    log = json.loads(LOG_FILE.read_text())

    # Collect slugs that have been planted
    planted_slugs = {
        entry["plant_slug"]
        for entry in log
        if entry.get("planted_date")
    }

    changed = []
    for slug in planted_slugs:
        plant_file = PLANTS_DIR / f"{slug}.md"
        if not plant_file.exists():
            print(f"Warning: no plant file for slug '{slug}'", file=sys.stderr)
            continue
        if update_status(plant_file, "planted"):
            changed.append(slug)

    if changed:
        print(f"Updated status to 'planted': {', '.join(sorted(changed))}")
    else:
        print("No status changes needed.")


if __name__ == "__main__":
    main()
