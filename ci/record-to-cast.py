#!/usr/bin/env python3
"""Record a command's terminal output as an asciinema v2 cast."""

import fcntl
import json
import os
import pty
import re
import struct
import subprocess  # nosec
import sys
import termios
import time
from pathlib import Path
from typing import Any

_STRIP_RE = re.compile(
    r"\x1b\["
    r"(?:"
    r"\?(?:1049|1047|47)[hl]"
    r"|\?25[lh]"
    r"|[23]J"
    r")"
)


def main() -> None:
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} OUTPUT.cast COMMAND [ARGS...]", file=sys.stderr)
        sys.exit(1)

    output_path = Path(sys.argv[1])
    command = sys.argv[2:]

    events: list[Any] = []
    start_time = time.time()
    cols, rows = 120, 40
    master_fd, slave_fd = pty.openpty()

    winsize = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)

    proc = subprocess.Popen(
        command,
        stdout=slave_fd,
        stderr=slave_fd,
        stdin=subprocess.DEVNULL,
        close_fds=True,
    )
    os.close(slave_fd)

    while True:
        try:
            chunk = os.read(master_fd, 4096)
        except OSError:
            break
        if not chunk:
            break
        elapsed = round(time.time() - start_time, 6)
        text = _STRIP_RE.sub("", chunk.decode("utf-8", errors="replace"))
        if text:
            events.append([elapsed, "o", text])
        sys.stdout.buffer.write(chunk)
        sys.stdout.flush()

    proc.wait()
    exit_code = proc.returncode
    os.close(master_fd)

    header = {
        "version": 2,
        "width": cols,
        "height": rows,
        "timestamp": int(start_time),
        "title": "tofusoup conformance suite",
        "env": {"TERM": "xterm-256color", "SHELL": "/bin/bash"},
    }

    with output_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(header) + "\n")
        for event in events:
            f.write(json.dumps(event) + "\n")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
