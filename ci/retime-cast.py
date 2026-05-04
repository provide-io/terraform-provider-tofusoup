#!/usr/bin/env python3
"""Retime an asciinema v2 cast to a target duration."""

import json
import sys
from pathlib import Path
from typing import Any


def retime(input_path: str, output_path: str, target_duration: float) -> None:
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open(encoding="utf-8") as f:
        header = json.loads(f.readline())
        events = [json.loads(line) for line in f]

    if not events:
        with output_file.open("w", encoding="utf-8") as f:
            f.write(json.dumps(header) + "\n")
        return

    original_duration = events[-1][0] - events[0][0]
    scale = 1.0 if original_duration <= 0 else target_duration / original_duration
    first_ts = events[0][0]
    offset = 0.5

    new_events: list[Any] = []
    for event in events:
        new_ts = round(offset + (event[0] - first_ts) * scale, 3)
        new_events.append([new_ts, event[1], event[2]])

    with output_file.open("w", encoding="utf-8") as f:
        f.write(json.dumps(header) + "\n")
        for event in new_events:
            f.write(json.dumps(event) + "\n")


def main() -> None:
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} INPUT.cast OUTPUT.cast [TARGET_SECONDS]", file=sys.stderr)
        sys.exit(1)
    target = float(sys.argv[3]) if len(sys.argv) > 3 else 15.0
    retime(sys.argv[1], sys.argv[2], target)


if __name__ == "__main__":
    main()
