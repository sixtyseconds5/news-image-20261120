#!/usr/bin/env python3
"""Copy the finished poster into the harness output directory.

The make.fun harness runs this file and collects whatever lands in
$MAKEFUN_OUTPUT_DIR (default /output). The poster itself is drawn by
gen_poster.py and shipped as entry.png next to this script; this file
only moves bytes, using nothing outside the standard library.
"""

import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    if not os.path.isfile(source):
        print(f"error: entry.png not found next to main.py ({source})", file=sys.stderr)
        return 1

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    destination = os.path.join(out_dir, "entry.png")
    shutil.copyfile(source, destination)
    print(f"copied {source} -> {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
