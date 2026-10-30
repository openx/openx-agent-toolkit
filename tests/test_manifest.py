import hashlib
import json

import manifest
import pytest
from conftest import git, init_repo


def write(root, files):
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


PUBLIC = {"backend": "example", "files": {"doc/tools.md": "docs/tools/example.md"}}


def test_the_manifest_lists_each_file_with_its_hash(tmp_path):
    write(tmp_path, {"public.json": json.dumps(PUBLIC), "doc/tools.md": "# Tools\n"})
    assert manifest.build(tmp_path, "abc1234") == {
        "backend": "example",
        "source_commit": "abc1234",
        "files": [
            {
                "from": "doc/tools.md",
                "to": "docs/tools/example.md",
                "sha256": hashlib.sha256(b"# Tools\n").hexdigest(),
            }
        ],
        "skills": [],
    }


@pytest.mark.parametrize(
    ("public", "message"),
    [
        ({"files": {"doc/tools.md": "docs/tools/example.md"}}, "names no backend"),
        ({"backend": "example", "files": {}}, "lists no files"),
        ({"backend": "example", "files": {"doc/missing.md": "docs/tools/example.md"}}, "doc/missing.md"),
        ({"backend": "example", "skills": ["a-skill"], "files": {}}, "files only"),
    ],
)
def test_a_public_json_it_cannot_publish_is_refused(tmp_path, public, message):
    write(tmp_path, {"public.json": json.dumps(public), "doc/tools.md": "# Tools\n"})
    with pytest.raises(manifest.ManifestError, match=message):
        manifest.build(tmp_path, "abc1234")


def test_main_writes_the_manifest_for_the_checkouts_head(tmp_path, capsys):
    write(tmp_path, {"public.json": json.dumps(PUBLIC), "doc/tools.md": "# Tools\n"})
    init_repo(tmp_path)
    head = git(tmp_path, "rev-parse", "HEAD").strip()
    assert manifest.main(["--source", str(tmp_path)]) == 0
    written = json.loads((tmp_path / "build" / "public-manifest.json").read_text())
    assert written["source_commit"] == head
    assert "1 files for example" in capsys.readouterr().out


def test_sync_accepts_the_manifest_it_writes(workspace):
    write(workspace.source, {"public.json": json.dumps(PUBLIC), "doc/tools.md": "# Tools\n"})
    out = workspace.root / "example-manifest.json"
    assert manifest.main(["--source", str(workspace.source), "--source-commit", "abc1234", "--out", str(out)]) == 0
    code, report = workspace.sync(out, "--dry-run", backend="example")
    assert code == 0
    assert "| added | `docs/tools/example.md` |" in report
