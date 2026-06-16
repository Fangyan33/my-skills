#!/usr/bin/env python3
"""Render per-slide HTML files to PNG screenshots with Playwright CLI."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Screenshot HTML slides into PNG files.")
    parser.add_argument("--html-dir", default="html", help="Directory containing NN.html files.")
    parser.add_argument("--img-dir", default="img", help="Directory for output PNG files.")
    parser.add_argument("--selector", default=".ppt-slide", help="Selector to wait for before screenshot.")
    parser.add_argument("--viewport", default="1280x720", help="Viewport as WIDTHxHEIGHT or WIDTH,HEIGHT.")
    parser.add_argument("--channel", default="chrome", help="Playwright browser channel, e.g. chrome.")
    parser.add_argument("--browser", default="chromium", help="Playwright browser type.")
    parser.add_argument("--wait-ms", type=int, default=1000, help="Extra wait before screenshot.")
    return parser.parse_args()


def normalize_viewport(value: str) -> str:
    return value.lower().replace("x", ",")


def main() -> int:
    args = parse_args()
    html_dir = Path(args.html_dir)
    img_dir = Path(args.img_dir)
    files = sorted(html_dir.glob("*.html"))
    if not files:
        raise SystemExit(f"No HTML files found in {html_dir}")

    img_dir.mkdir(parents=True, exist_ok=True)
    viewport = normalize_viewport(args.viewport)

    for html_file in files:
        output = img_dir / f"{html_file.stem}.png"
        cmd = [
            "playwright",
            "screenshot",
            f"--browser={args.browser}",
            f"--channel={args.channel}",
            "--viewport-size",
            viewport,
            "--wait-for-selector",
            args.selector,
            "--wait-for-timeout",
            str(args.wait_ms),
            html_file.resolve().as_uri(),
            str(output),
        ]
        print(f"[render] {html_file} -> {output}")
        subprocess.run(cmd, check=True)

    print(f"Rendered {len(files)} images into {img_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
