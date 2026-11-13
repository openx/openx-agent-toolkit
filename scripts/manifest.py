"""Write the manifest sync.py reads, from a backend's public.json.

Run from a checkout of the backend's repo, with this repo's scripts beside it:

    python toolkit/scripts/manifest.py --source . --out build/public-manifest.json

public.json names the backend and maps each file it publishes to its path here:

    {"backend": "example", "files": {"doc/tools.md": "docs/tools/example.md"}}

Anything it does not name stays private. This builder publishes files only; a backend that
publishes skills writes its own manifest with their catalogue.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ALLOWLIST = "public.json"


class ManifestError(Exception):
    pass


def build(source: Path, source_commit: str) -> dict:
    """The manifest for source/public.json, each file with the hash of its content."""
    try:
        allowlist = json.loads((source / ALLOWLIST).read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ManifestError(f"can't read {ALLOWLIST}: {error}") from error
    backend = allowlist.get("backend")
    if not isinstance(backend, str) or not backend:
        raise ManifestError(f"{ALLOWLIST} names no backend")
    if allowlist.get("skills"):
        raise ManifestError(f"{ALLOWLIST} lists skills; this builder publishes files only")
    mapping = allowlist.get("files")
    if not isinstance(mapping, dict) or not mapping:
        raise ManifestError(f"{ALLOWLIST} lists no files")
    files = []
    for origin, destination in mapping.items():
        path = source / origin
        if not path.is_file():
            raise ManifestError(f"{ALLOWLIST} lists {origin}, which does not exist")
        files.append({"from": origin, "to": destination, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return {"backend": backend, "source_commit": source_commit, "files": files, "skills": []}


def head_commit(source: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=source, check=True, capture_output=True, text=True
    ).stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", type=Path, default=Path("."), help="the backend's checkout")
    parser.add_argument("--source-commit", help="defaults to the checkout's HEAD")
    parser.add_argument("--out", type=Path, help="defaults to build/public-manifest.json in --source")
    args = parser.parse_args(argv)
    try:
        manifest = build(args.source, args.source_commit or head_commit(args.source))
    except ManifestError as error:
        print(f"**Manifest not written:** {error}")
        return 1
    out = args.out or args.source / "build" / "public-manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {out}: {len(manifest['files'])} files for {manifest['backend']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
