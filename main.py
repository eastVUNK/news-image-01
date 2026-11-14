"""news-image-01 entry: validate and copy the composed image.

v2: before copying, verify the bundled asset is a well-formed PNG of
exactly 1024x1024 pixels and at most 1 MiB (PNG magic bytes, IHDR
dimensions, IEND trailer). Any failure exits 1 with a message on
stderr instead of writing a bad file. The copy itself is verbatim
(temp file + atomic rename), so the output bytes are exactly the
asset's bytes. Deterministic, no network, stdlib only.

The image was composed by compose.py (three generated panels plus
PIL vector text) and is bundled as assets/entry.png.
"""
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET = os.path.join(HERE, "assets", "entry.png")
OUT_DIR = "/output"
OUT_PATH = os.path.join(OUT_DIR, "entry.png")

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
PNG_IEND = b"\x00\x00\x00\x00IEND\xaeB`\x82"
MAX_BYTES = 1048576
EXPECT_W, EXPECT_H = 1024, 1024


def fail(msg):
    print("entry check failed: " + msg, file=sys.stderr)
    sys.exit(1)


def validate(data):
    if len(data) < 8 or data[:8] != PNG_MAGIC:
        fail("not a PNG file (bad magic bytes)")
    if len(data) > MAX_BYTES:
        fail("file is %d bytes, over the 1 MiB limit" % len(data))
    if len(data) < 33 or data[12:16] != b"IHDR":
        fail("missing IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (EXPECT_W, EXPECT_H):
        fail("dimensions are %dx%d, expected 1024x1024" % (width, height))
    if data[-12:] != PNG_IEND:
        fail("missing IEND trailer (truncated file?)")


def main():
    with open(ASSET, "rb") as f:
        data = f.read()
    validate(data)
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, OUT_PATH)
    # Re-read and confirm the output is exactly the validated asset.
    with open(OUT_PATH, "rb") as f:
        if f.read() != data:
            fail("output does not match the validated asset")
    print("wrote %s (%d bytes, %dx%d)" % (OUT_PATH, len(data),
                                          EXPECT_W, EXPECT_H))


if __name__ == "__main__":
    main()
