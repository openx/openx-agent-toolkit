from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest
import sync

NOTICE = "This Skill is an example: provided for use with your OpenX account."
REPO_NOTICE = "Copyright © 2026 Example. Licensed for use with an active OpenX account only."
# Made-up terms, as in test_scan.py: this repo is public.
TERMS = "block: codename: \\bPelican\\b\nblock, outside links: chat room: (?<![\\w&/])#[a-z][a-z0-9-]{2,}\nwarn: test environment: \\bstaging\\b\n"


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def init_repo(path: Path) -> Path:
    """A git repo at path, with whatever is already there (the workspace's notices) committed."""
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q", "-b", "main")
    configure(path)
    git(path, "add", "-A")
    git(path, "commit", "-q", "--allow-empty", "-m", "Initial commit")
    return path


def configure(path: Path) -> None:
    git(path, "config", "user.name", "Test")
    git(path, "config", "user.email", "test@example.com")


def clone(remote: Path, path: Path) -> Path:
    git(remote.parent, "clone", "-q", str(remote), str(path))
    configure(path)
    return path


class Workspace:
    """A backend's checkout (source) and a checkout of this repo (public) under tmp_path."""

    def __init__(self, root: Path, capsys: pytest.CaptureFixture[str]):
        self.root = root
        self.source = root / "source"
        self.public = root / "public"
        self.source.mkdir()
        self.public.mkdir()
        (self.public / "LICENSE").write_text(REPO_NOTICE + "\n")
        (self.public / "SKILL_NOTICE.md").write_text(NOTICE + "\n")
        (self.source / "public-terms.txt").write_text(TERMS)
        self._capsys = capsys

    def write_source(self, files: dict[str, str]) -> None:
        for relative, text in files.items():
            path = self.source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)

    def manifest(
        self,
        mapping: dict[str, str],
        backend: str = "kestrel",
        commit: str = "80f3613abc",
        skills: list[dict[str, str]] | None = None,
    ) -> Path:
        files = [
            {"from": origin, "to": destination, "sha256": hashlib.sha256((self.source / origin).read_bytes()).hexdigest()}
            for origin, destination in mapping.items()
        ]
        path = self.root / f"{backend}-manifest.json"
        path.write_text(json.dumps({"backend": backend, "source_commit": commit, "files": files, "skills": skills or []}))
        return path

    def sync(self, manifest: Path, *flags: str, backend: str = "kestrel", public: Path | None = None) -> tuple[int, str]:
        self._capsys.readouterr()
        code = sync.main(
            [
                "--backend", backend,
                "--manifest", str(manifest),
                "--public", str(public or self.public),
                "--source", str(self.source),
                *flags,
            ]
        )
        return code, self._capsys.readouterr().out


@pytest.fixture
def workspace(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> Workspace:
    return Workspace(tmp_path, capsys)
