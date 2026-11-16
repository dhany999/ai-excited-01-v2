#!/usr/bin/env python3
"""ai-excited-01 entry 2: "Aurora Phoenix" — copy the bundled image.

Standard library only. Deterministic: the output bytes are exactly the
bundled entry.png bytes, so both grader runs produce identical output.
"""
import hashlib
import os
import shutil
import struct
import sys

MAX_BYTES = 1_048_576  # competition cap: 1 MiB
EXPECT_W, EXPECT_H = 1024, 1024


def png_size(path):
    """Return (width, height) from a PNG header, or None if not a PNG."""
    with open(path, "rb") as f:
        head = f.read(33)
    if len(head) < 33 or head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    if head[12:16] != b"IHDR":
        return None
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        print("entry.png missing next to main.py", file=sys.stderr)
        return 1
    if os.path.getsize(src) > MAX_BYTES:
        print("entry.png exceeds 1 MiB cap", file=sys.stderr)
        return 1
    size = png_size(src)
    if size != (EXPECT_W, EXPECT_H):
        print(f"entry.png is {size}, expected {(EXPECT_W, EXPECT_H)}",
              file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    # Output-side verification: size must match, and the written file
    # must still parse as the expected 1024x1024 PNG (catches a
    # truncated or corrupted write that a hash alone would also catch,
    # but with a precise diagnostic).
    if os.path.getsize(dst) != os.path.getsize(src):
        print("output size differs from bundled entry.png", file=sys.stderr)
        return 1
    if png_size(dst) != (EXPECT_W, EXPECT_H):
        print("output is not a valid 1024x1024 PNG", file=sys.stderr)
        return 1
    # Determinism self-check: the copy must be byte-identical to the bundle.
    want = sha256_file(src)
    got = sha256_file(dst)
    if want != got:
        print("copy mismatch", file=sys.stderr)
        return 1
    print(f"wrote {dst} ({os.path.getsize(dst)} bytes, sha256 {got[:16]}...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
