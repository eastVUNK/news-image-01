"""news-image-01 entry: copy the composed image to the output directory.

Deterministic, no network, stdlib only. The image itself was composed by
compose.py (three generated panels plus PIL vector text) and is bundled
as assets/entry.png, so every run writes the same bytes.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = "/output"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "assets", "entry.png"),
                    os.path.join(OUT_DIR, "entry.png"))


if __name__ == "__main__":
    main()
