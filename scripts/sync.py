"""Copy one backend's public files into this repo, exactly as its manifest lists them.

Run from a checkout of the backend's repo, with this repo checked out at ./public:

    python public/scripts/sync.py --backend example \\
        --manifest build/public-manifest.json --public public --dry-run

The backend's CI builds the manifest. Each "from" path is relative to the backend's
checkout, each "to" path is under skills/ or docs/tools/ here, and each sha256 is the
file's content hash:

    {
      "backend": "example",
      "source_commit": "80f3613",
      "files": [{"from": "docs/tools.md", "to": "docs/tools/example.md", "sha256": "..."}],
      "skills": [{"name": "...", "title": "...", "description": "...", "version": "..."}]
    }

A backend owns the paths in its .sync/<backend>.json, the manifest it last synced. A sync
scans every file against the backend's own term list (scan.py, reading public-terms.txt in
the backend's checkout) before writing anything, refuses a path another backend owns, writes
the new and changed files and deletes the ones the backend dropped. Without a term list it
stops.

Every SKILL.md it writes carries the skill notice in SKILL_NOTICE.md, as its frontmatter
license and in a "Legal notice" section at the end, so a skill copied out of the repo keeps it;
the sync stops if SKILL_NOTICE.md is missing. LICENSE holds the notice for the repo as a whole
and is not copied into skills.

With no mode flag the sync writes files only. --dry-run writes nothing. --commit also
commits, and --push also pushes, starting over from the remote's tip when another backend
pushed first. Either way it prints a markdown report, for a CI job summary. Exit status 1
means a blocking finding or an error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))

import scan

SYNCED_ROOTS = (PurePosixPath("skills"), PurePosixPath("docs/tools"))
STATE_DIR = ".sync"
BACKEND_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ALLOWLIST = "public-allow.txt"
TERMS = "public-terms.txt"
NOTICE_FILE = "SKILL_NOTICE.md"
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_LICENSE_LINE = re.compile(r"^license:.*(?:\n|$)", re.MULTILINE)


class SyncError(Exception):
    """A manifest or repository state the sync refuses to act on."""


@dataclass
class Manifest:
    backend: str
    source_commit: str
    files: list[dict[str, str]]
    skills: list[dict[str, str]]

    @property
    def short_commit(self) -> str:
        return self.source_commit[:7]


@dataclass
class Plan:
    added: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)


def _relative(raw: str, what: str) -> PurePosixPath:
    path = PurePosixPath(raw)
    if path.is_absolute() or ".." in path.parts or str(path) != raw:
        raise SyncError(f"{what} {raw!r} must be a plain relative path")
    return path


def load_manifest(path: Path, backend: str) -> Manifest:
    if not BACKEND_NAME.match(backend):
        raise SyncError(f"backend name {backend!r} must be lowercase letters, digits and hyphens")
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise SyncError(f"can't read the manifest {path}: {error}") from error
    if data.get("backend") != backend:
        raise SyncError(f"the manifest is for {data.get('backend')!r}, not {backend!r}")
    commit = data.get("source_commit")
    if not isinstance(commit, str) or not commit:
        raise SyncError("the manifest has no source_commit")
    entries = data.get("files")
    if not isinstance(entries, list) or not entries:
        raise SyncError("the manifest lists no files")
    files: list[dict[str, str]] = []
    for entry in entries:
        if not isinstance(entry, dict) or not all(
            isinstance(entry.get(key), str) and entry[key] for key in ("from", "to", "sha256")
        ):
            raise SyncError(f"every manifest file needs from, to and sha256: {entry!r}")
        _relative(entry["from"], "source path")
        destination = _relative(entry["to"], "destination")
        if not any(root in destination.parents for root in SYNCED_ROOTS):
            roots = " or ".join(f"{root}/" for root in SYNCED_ROOTS)
            raise SyncError(f"destination {entry['to']} is outside {roots}")
        if any(entry["to"] == other["to"] for other in files):
            raise SyncError(f"destination {entry['to']} is listed twice")
        files.append({key: entry[key] for key in ("from", "to", "sha256")})
    skills = data.get("skills", [])
    if not isinstance(skills, list):
        raise SyncError("the manifest's skills must be a list")
    return Manifest(backend, commit, files, skills)


def read_sources(manifest: Manifest, source: Path) -> dict[str, bytes]:
    """Each destination's content, read from the backend's checkout and checked against its hash."""
    contents: dict[str, bytes] = {}
    for entry in manifest.files:
        try:
            data = (source / entry["from"]).read_bytes()
        except OSError as error:
            raise SyncError(f"can't read {entry['from']}: {error.strerror}") from error
        if hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise SyncError(f"{entry['from']} doesn't match its sha256 in the manifest; rebuild the manifest")
        contents[entry["to"]] = data
    return contents


def scan_files(
    manifest: Manifest, contents: dict[str, bytes], terms: Path, allowlist: Path
) -> tuple[list[scan.Finding], int]:
    """Findings in every text file, minus the ones the allowlist accepts, and how many it accepted."""
    if not terms.exists():
        raise SyncError(f"no {terms}: the scan needs the backend's term list")
    try:
        rules = scan.parse_terms(terms.read_text())
        allowed = scan.parse_allowlist(allowlist.read_text()) if allowlist.exists() else set()
    except ValueError as error:
        raise SyncError(str(error)) from error
    findings: list[scan.Finding] = []
    accepted = 0
    for entry in manifest.files:
        try:
            text = contents[entry["to"]].decode("utf-8")
        except UnicodeDecodeError:
            continue
        for finding in scan.scan_text(entry["from"], text, rules):
            if (finding.path, finding.term) in allowed:
                accepted += 1
            else:
                findings.append(finding)
    return findings, accepted


def load_notice(public: Path) -> str:
    try:
        notice = (public / NOTICE_FILE).read_text().strip()
    except OSError as error:
        raise SyncError(f"{NOTICE_FILE} is missing from {public}; every published skill carries its text") from error
    if not notice:
        raise SyncError(f"{NOTICE_FILE} in {public} is empty; every published skill carries its text")
    return notice


def with_notice(contents: dict[str, bytes], notice: str) -> dict[str, bytes]:
    """The contents to publish: each SKILL.md with the skill notice as its frontmatter license
    and in a Legal notice section at the end. A license the source already has is replaced, and
    the section is left out when the source's own text already carries the notice."""
    published: dict[str, bytes] = {}
    for destination, data in contents.items():
        if PurePosixPath(destination).name == "SKILL.md":
            data = _skill_with_notice(data.decode("utf-8"), notice).encode("utf-8")
        published[destination] = data
    return published


def _skill_with_notice(text: str, notice: str) -> str:
    frontmatter, body = "", text
    if match := _FRONTMATTER.match(text):
        fields = _LICENSE_LINE.sub("", match.group(1)).rstrip("\n")
        # A JSON string is valid YAML and keeps a colon in the notice from breaking the frontmatter.
        frontmatter = f"---\n{fields}\nlicense: {json.dumps(notice, ensure_ascii=False)}\n---\n"
        body = text[match.end() :]
    if notice not in body:
        body = body.rstrip("\n") + f"\n\n## Legal notice\n\n{notice}\n"
    return frontmatter + body


def load_states(public: Path) -> dict[str, dict]:
    return {path.stem: json.loads(path.read_text()) for path in sorted((public / STATE_DIR).glob("*.json"))}


def make_plan(backend: str, contents: dict[str, bytes], public: Path, states: dict[str, dict]) -> Plan:
    owners = {
        file["path"]: name
        for name, state in states.items()
        if name != backend
        for file in state.get("files", [])
    }
    previous = {file["path"] for file in states.get(backend, {}).get("files", [])}
    plan = Plan()
    clashes: list[str] = []
    for destination, data in sorted(contents.items()):
        target = public / destination
        if destination in owners:
            clashes.append(f"{destination} belongs to {owners[destination]}")
        elif not target.exists():
            plan.added.append(destination)
        elif destination not in previous:
            clashes.append(f"{destination} already exists here and no backend owns it")
        elif target.read_bytes() == data:
            plan.unchanged.append(destination)
        else:
            plan.changed.append(destination)
    if clashes:
        raise SyncError("; ".join(clashes))
    plan.removed = sorted(previous - contents.keys())
    return plan


def apply(plan: Plan, contents: dict[str, bytes], public: Path, manifest: Manifest) -> None:
    for destination in plan.added + plan.changed:
        target = public / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(contents[destination])
    for destination in plan.removed:
        target = public / destination
        target.unlink(missing_ok=True)
        folder = target.parent
        while folder != public and folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()
            folder = folder.parent
    state = {
        "backend": manifest.backend,
        "source_commit": manifest.source_commit,
        "files": [
            {"path": entry["to"], "sha256": entry["sha256"]}
            for entry in sorted(manifest.files, key=lambda entry: entry["to"])
        ],
        "skills": manifest.skills,
    }
    (public / STATE_DIR).mkdir(exist_ok=True)
    (public / STATE_DIR / f"{manifest.backend}.json").write_text(json.dumps(state, indent=2) + "\n")


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def report(manifest: Manifest, plan: Plan, findings: list[scan.Finding], accepted: int, mode: str) -> str:
    heading = f"## Public sync: {manifest.backend} {manifest.short_commit}"
    lines = [heading + (" (dry run)" if mode == "dry-run" else ""), ""]
    lines.append(
        f"{len(plan.added)} added, {len(plan.changed)} changed, {len(plan.removed)} removed, "
        f"{len(plan.unchanged)} unchanged."
    )
    changes = (
        [("added", path) for path in plan.added]
        + [("changed", path) for path in plan.changed]
        + [("removed", path) for path in plan.removed]
    )
    if changes:
        lines += ["", "| Change | Path |", "| --- | --- |"]
        lines += [f"| {change} | `{path}` |" for change, path in changes]
    if findings:
        lines += ["", "### Scan findings", "", "| Result | File | Line | Term | Rule |", "| --- | --- | --- | --- | --- |"]
        ordered = sorted(findings, key=lambda f: (f.result != scan.BLOCK, f.path, f.line))
        lines += [
            f"| {f.result} | `{_cell(f.path)}` | {f.line} | `{_cell(f.term)}` | {f.rule} |" for f in ordered
        ]
    if any(finding.result == scan.BLOCK for finding in findings):
        lines += [
            "",
            f"Blocking findings stop the sync. To accept a false positive, add `path: term: reason` to {ALLOWLIST}.",
        ]
    if accepted:
        lines += ["", f"{accepted} finding(s) accepted by {ALLOWLIST}."]
    return "\n".join(lines) + "\n"


def git(public: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=public, check=check, capture_output=True, text=True)


def require_clean(public: Path) -> None:
    if git(public, "status", "--porcelain").stdout.strip():
        raise SyncError(f"{public} has uncommitted changes; --commit and --push need a clean checkout")


def commit(public: Path, manifest: Manifest) -> None:
    git(public, "add", "-A")
    git(public, "commit", "-q", "-m", f"Sync {manifest.backend} {manifest.short_commit}")


def push(public: Path) -> bool:
    """True once pushed, False when the remote has commits this checkout lacks."""
    result = git(public, "push", "-q", "origin", "HEAD", check=False)
    if result.returncode == 0:
        return True
    if "rejected" in result.stderr:
        return False
    raise SyncError(f"git push failed: {result.stderr.strip()}")


def reset_to_remote(public: Path) -> None:
    branch = git(public, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    git(public, "fetch", "-q", "origin", branch)
    git(public, "reset", "-q", "--hard", f"origin/{branch}")


def run(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.manifest, args.backend)
    contents = read_sources(manifest, args.source)
    findings, accepted = scan_files(
        manifest, contents, args.terms or args.source / TERMS, args.allow or args.source / ALLOWLIST
    )
    blocking = any(finding.result == scan.BLOCK for finding in findings)
    if args.mode in ("commit", "push"):
        require_clean(args.public)
    attempts = args.attempts if args.mode == "push" else 1
    for attempt in range(1, attempts + 1):
        if attempt > 1:
            reset_to_remote(args.public)
        states = load_states(args.public)
        published = with_notice(contents, load_notice(args.public))
        plan = make_plan(manifest.backend, published, args.public, states)
        text = report(manifest, plan, findings, accepted, args.mode)
        if args.mode == "dry-run" or blocking:
            print(text, end="")
            return 1 if blocking else 0
        changed = plan.added or plan.changed or plan.removed
        if not changed and states.get(manifest.backend, {}).get("skills") == manifest.skills:
            print(text + "\nNothing to sync.\n", end="")
            return 0
        apply(plan, published, args.public, manifest)
        if args.mode != "write":
            commit(args.public, manifest)
        if args.mode != "push" or push(args.public):
            print(text, end="")
            return 0
    raise SyncError(f"the push was rejected {attempts} times; another backend kept pushing first")


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--backend", required=True, help="the backend's name, as in .sync/<backend>.json")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--public", type=Path, required=True, help="a checkout of this repo")
    parser.add_argument(
        "--source", type=Path, default=Path("."), help="the backend's checkout, which from paths are relative to"
    )
    parser.add_argument("--terms", type=Path, help=f"defaults to {TERMS} in --source")
    parser.add_argument("--allow", type=Path, help=f"defaults to {ALLOWLIST} in --source")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="mode", action="store_const", const="dry-run")
    mode.add_argument("--commit", dest="mode", action="store_const", const="commit")
    mode.add_argument("--push", dest="mode", action="store_const", const="push")
    parser.set_defaults(mode="write")
    parser.add_argument("--attempts", type=int, default=3, help="pushes to try before giving up")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        return run(args)
    except SyncError as error:
        print(f"**Sync stopped:** {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
