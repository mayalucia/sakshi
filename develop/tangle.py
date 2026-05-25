"""develop/tangle.py — a minimal Python tangler for sakshi's codev/*.org.

sakshi's source-of-truth is codev/*.org. In Emacs, `org-babel-tangle`
produces the .py files. This script does the same job in a single
shell-invocable command, so the repository can be tangled without a
running Emacs.

The grammar supported:

    #+begin_src <lang> :tangle <path> [other-args-ignored]
    ...code body...
    #+end_src

    #+begin_src <lang> :tangle no
    ...code body (NOT tangled)...
    #+end_src

Paths are interpreted relative to the .org file's directory.

Concatenation: if multiple blocks specify the same :tangle path, their
bodies are concatenated (in source order) into that file.

Run:
    python develop/tangle.py            # tangle everything
    python develop/tangle.py --check    # exit non-zero if any tangled file
                                        # differs from disk (useful in CI)
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

# Regex: matches `#+begin_src LANG :tangle TARGET ...\n BODY \n#+end_src`
BLOCK_RE = re.compile(
    r"^\s*#\+begin_src\s+(?P<lang>\S+)(?P<args>[^\n]*)\n"
    r"(?P<body>.*?)\n"
    r"^\s*#\+end_src\s*$",
    re.MULTILINE | re.DOTALL,
)

TANGLE_ARG_RE = re.compile(r":tangle\s+(?P<target>\S+)")


def parse_org_file(path: Path) -> dict[Path, list[str]]:
    """Return {tangle_path: [block_body, ...]} for one .org file."""
    text = path.read_text(encoding="utf-8")
    tangle_map: dict[Path, list[str]] = defaultdict(list)
    for m in BLOCK_RE.finditer(text):
        args = m.group("args") or ""
        am = TANGLE_ARG_RE.search(args)
        if not am:
            continue
        target = am.group("target")
        if target == "no" or target.lower() == "nil":
            continue
        target_path = (path.parent / target).resolve()
        body = m.group("body")
        # Strip the trailing newline if present (we'll re-add when joining).
        tangle_map[target_path].append(body)
    return tangle_map


def collect_tangle_map(codev_dir: Path) -> dict[Path, list[str]]:
    """Walk codev/ and build a combined tangle map across all .org files."""
    combined: dict[Path, list[str]] = defaultdict(list)
    for org in sorted(codev_dir.rglob("*.org")):
        for target, bodies in parse_org_file(org).items():
            combined[target].extend(bodies)
    return combined


def write_tangled(
    tangle_map: dict[Path, list[str]], *, check_only: bool = False
) -> tuple[int, list[Path]]:
    """Write each tangled file. Returns (number_written_or_drift, drifted_paths).

    In check_only mode, no writes happen; we report drift instead.
    """
    drifted: list[Path] = []
    n = 0
    for target, bodies in tangle_map.items():
        content = "\n".join(bodies) + "\n"
        if check_only:
            if not target.exists() or target.read_text(encoding="utf-8") != content:
                drifted.append(target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            current = (
                target.read_text(encoding="utf-8") if target.exists() else None
            )
            if current != content:
                target.write_text(content, encoding="utf-8")
                n += 1
    return n, drifted


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write; exit non-zero if any tangled file would change.",
    )
    parser.add_argument(
        "--codev-dir",
        type=Path,
        default=None,
        help="Path to codev/ (default: ../codev relative to this script).",
    )
    args = parser.parse_args(argv)

    here = Path(__file__).resolve().parent
    codev_dir = args.codev_dir or (here.parent / "codev")
    if not codev_dir.is_dir():
        print(f"codev/ not found at {codev_dir}", file=sys.stderr)
        return 2

    tmap = collect_tangle_map(codev_dir)
    if not tmap:
        print(f"No tangle targets found under {codev_dir}", file=sys.stderr)
        return 1

    n, drifted = write_tangled(tmap, check_only=args.check)
    if args.check:
        if drifted:
            print(
                "Tangled outputs out-of-sync with codev/ sources:",
                file=sys.stderr,
            )
            for p in drifted:
                print(f"  {p}", file=sys.stderr)
            return 1
        print(f"Tangled outputs in sync with codev/ ({len(tmap)} files).")
        return 0
    print(f"Tangled {n} of {len(tmap)} target files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
