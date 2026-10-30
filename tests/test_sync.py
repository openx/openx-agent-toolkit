import json

import pytest
from conftest import NOTICE, REPO_NOTICE, clone, git, init_repo

SKILL = "---\nname: kestrel-launch\ndescription: Launch a campaign\n---\n\nSteps.\n"
TOOLS = "# Tools\n\n- [Deals](#deals)\n"
PUBLISHED_SKILL = (
    "---\nname: kestrel-launch\ndescription: Launch a campaign\n"
    f"license: {json.dumps(NOTICE)}\n---\n\nSteps.\n\n## Legal notice\n\n{NOTICE}\n"
)


def kestrel_files(workspace, **overrides):
    files = {"skills/kestrel-launch/SKILL.md": SKILL, "docs/tools.md": TOOLS, **overrides}
    workspace.write_source(files)
    return {
        "skills/kestrel-launch/SKILL.md": "skills/kestrel-launch/SKILL.md",
        "docs/tools.md": "docs/tools/kestrel.md",
    }


def test_dry_run_reports_the_files_and_writes_nothing(workspace):
    manifest = workspace.manifest(kestrel_files(workspace))
    code, out = workspace.sync(manifest, "--dry-run")
    assert code == 0
    assert "## Public sync: kestrel 80f3613 (dry run)" in out
    assert "2 added, 0 changed, 0 removed, 0 unchanged." in out
    assert "| added | `docs/tools/kestrel.md` |" in out
    assert sorted(path.name for path in workspace.public.iterdir()) == ["LICENSE", "SKILL_NOTICE.md"]


def test_sync_copies_the_files_and_records_what_the_backend_owns(workspace):
    skills = [{"name": "kestrel-launch", "title": "Launch a campaign", "description": "d", "version": "1.0"}]
    manifest = workspace.manifest(kestrel_files(workspace), skills=skills)
    code, _ = workspace.sync(manifest)
    assert code == 0
    assert (workspace.public / "skills/kestrel-launch/SKILL.md").read_text() == PUBLISHED_SKILL
    assert (workspace.public / "docs/tools/kestrel.md").read_text() == TOOLS
    state = json.loads((workspace.public / ".sync/kestrel.json").read_text())
    assert state["backend"] == "kestrel"
    assert state["source_commit"] == "80f3613abc"
    assert [file["path"] for file in state["files"]] == [
        "docs/tools/kestrel.md",
        "skills/kestrel-launch/SKILL.md",
    ]
    assert state["skills"] == skills


def test_resync_updates_changed_files_and_deletes_dropped_ones(workspace):
    workspace.sync(workspace.manifest(kestrel_files(workspace)))
    workspace.write_source({"docs/tools.md": TOOLS + "\nMore.\n"})
    manifest = workspace.manifest({"docs/tools.md": "docs/tools/kestrel.md"}, commit="9999999")
    code, out = workspace.sync(manifest)
    assert code == 0
    assert "0 added, 1 changed, 1 removed, 0 unchanged." in out
    assert (workspace.public / "docs/tools/kestrel.md").read_text().endswith("More.\n")
    assert not (workspace.public / "skills").exists()


def test_an_unchanged_manifest_has_nothing_to_sync(workspace):
    mapping = kestrel_files(workspace)
    workspace.sync(workspace.manifest(mapping))
    code, out = workspace.sync(workspace.manifest(mapping, commit="1111111"))
    assert code == 0
    assert "Nothing to sync." in out
    assert json.loads((workspace.public / ".sync/kestrel.json").read_text())["source_commit"] == "80f3613abc"


def test_a_path_another_backend_owns_is_refused(workspace):
    workspace.write_source({"skills/shared/SKILL.md": SKILL})
    workspace.sync(workspace.manifest({"skills/shared/SKILL.md": "skills/shared/SKILL.md"}, backend="heron"), backend="heron")
    code, out = workspace.sync(workspace.manifest({"skills/shared/SKILL.md": "skills/shared/SKILL.md"}))
    assert code == 1
    assert "skills/shared/SKILL.md belongs to heron" in out


def test_a_file_no_backend_owns_is_not_overwritten(workspace):
    (workspace.public / "skills/kestrel-launch").mkdir(parents=True)
    (workspace.public / "skills/kestrel-launch/SKILL.md").write_text("edited by hand")
    code, out = workspace.sync(workspace.manifest(kestrel_files(workspace)))
    assert code == 1
    assert "already exists here and no backend owns it" in out
    assert (workspace.public / "skills/kestrel-launch/SKILL.md").read_text() == "edited by hand"


@pytest.mark.parametrize(
    "destination", ["README.md", "skills", ".sync/kestrel.json", "skills/../README.md", "/skills/a.md", "./skills/a.md"]
)
def test_destinations_outside_the_synced_folders_are_refused(workspace, destination):
    workspace.write_source({"a.md": "text"})
    code, out = workspace.sync(workspace.manifest({"a.md": destination}))
    assert code == 1
    assert "**Sync stopped:**" in out
    assert sorted(path.name for path in workspace.public.iterdir()) == ["LICENSE", "SKILL_NOTICE.md"]


def test_a_stale_manifest_is_refused(workspace):
    manifest = workspace.manifest(kestrel_files(workspace))
    workspace.write_source({"docs/tools.md": "changed after the manifest was built"})
    code, out = workspace.sync(manifest)
    assert code == 1
    assert "docs/tools.md doesn't match its sha256" in out


def test_a_manifest_for_another_backend_is_refused(workspace):
    manifest = workspace.manifest(kestrel_files(workspace), backend="heron")
    code, out = workspace.sync(manifest, backend="kestrel")
    assert code == 1
    assert "the manifest is for 'heron', not 'kestrel'" in out


def test_a_blocking_finding_stops_the_sync_until_the_allowlist_accepts_it(workspace):
    mapping = kestrel_files(workspace, **{"docs/tools.md": TOOLS + "Ask in #sample-room.\nThe staging step.\n"})
    manifest = workspace.manifest(mapping)
    code, out = workspace.sync(manifest)
    assert code == 1
    assert "| block | `docs/tools.md` | 4 | `#sample-room` | chat room |" in out
    assert "| warn | `docs/tools.md` | 5 | `staging` | test environment |" in out
    assert not (workspace.public / "docs").exists()

    workspace.write_source({"public-allow.txt": "docs/tools.md: #sample-room: a test fixture\n"})
    code, out = workspace.sync(manifest)
    assert code == 0
    assert "1 finding(s) accepted by public-allow.txt." in out
    assert (workspace.public / "docs/tools/kestrel.md").exists()


def test_the_sync_stops_without_the_backends_term_list(workspace):
    manifest = workspace.manifest(kestrel_files(workspace))
    (workspace.source / "public-terms.txt").unlink()
    code, out = workspace.sync(manifest, "--dry-run")
    assert code == 1
    assert "public-terms.txt: the scan needs the backend's term list" in out


def test_terms_can_come_from_another_path(workspace):
    manifest = workspace.manifest(kestrel_files(workspace, **{"docs/tools.md": TOOLS + "Heron.\n"}))
    terms = workspace.root / "terms.txt"
    terms.write_text("block: other codename: \\bHeron\\b\n")
    code, out = workspace.sync(manifest, "--dry-run", "--terms", str(terms))
    assert code == 1
    assert "`Heron` | other codename |" in out


def test_commit_names_the_backend_and_source_commit(workspace):
    init_repo(workspace.public)
    code, _ = workspace.sync(workspace.manifest(kestrel_files(workspace)), "--commit")
    assert code == 0
    assert git(workspace.public, "log", "-1", "--format=%s").strip() == "Sync kestrel 80f3613"
    assert git(workspace.public, "status", "--porcelain") == ""


def test_commit_needs_a_clean_checkout(workspace):
    init_repo(workspace.public)
    (workspace.public / "stray.txt").write_text("not committed")
    code, out = workspace.sync(workspace.manifest(kestrel_files(workspace)), "--commit")
    assert code == 1
    assert "uncommitted changes" in out


def test_push_starts_over_when_another_backend_pushed_first(workspace, tmp_path):
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(remote))
    seed = clone(remote, tmp_path / "seed")
    (seed / "README.md").write_text("toolkit\n")
    (seed / "SKILL_NOTICE.md").write_text(NOTICE + "\n")
    git(seed, "add", "-A")
    git(seed, "commit", "-q", "-m", "Initial README")
    git(seed, "push", "-q", "origin", "main")
    behind = clone(remote, tmp_path / "behind")
    ahead = clone(remote, tmp_path / "ahead")

    workspace.write_source({"heron/SKILL.md": SKILL})
    heron = workspace.manifest({"heron/SKILL.md": "skills/heron-troubleshoot/SKILL.md"}, backend="heron")
    assert workspace.sync(heron, "--push", backend="heron", public=ahead)[0] == 0

    code, out = workspace.sync(workspace.manifest(kestrel_files(workspace)), "--push", public=behind)
    assert code == 0, out
    check = clone(remote, tmp_path / "check")
    assert (check / ".sync/heron.json").exists()
    assert (check / ".sync/kestrel.json").exists()
    assert git(check, "log", "--format=%s").splitlines() == ["Sync kestrel 80f3613", "Sync heron 80f3613", "Initial README"]


def test_only_skill_md_files_carry_the_notice(workspace):
    mapping = kestrel_files(workspace, **{"skills/kestrel-launch/references/values.md": "| a | b |\n"})
    mapping["skills/kestrel-launch/references/values.md"] = "skills/kestrel-launch/references/values.md"
    assert workspace.sync(workspace.manifest(mapping))[0] == 0
    assert (workspace.public / "skills/kestrel-launch/SKILL.md").read_text() == PUBLISHED_SKILL
    assert (workspace.public / "skills/kestrel-launch/references/values.md").read_text() == "| a | b |\n"
    assert (workspace.public / "docs/tools/kestrel.md").read_text() == TOOLS


def test_a_changed_license_rewrites_every_skill(workspace):
    mapping = kestrel_files(workspace)
    workspace.sync(workspace.manifest(mapping))
    (workspace.public / "SKILL_NOTICE.md").write_text("A new notice.\n")
    code, out = workspace.sync(workspace.manifest(mapping))
    assert code == 0
    assert "0 added, 1 changed, 0 removed, 1 unchanged." in out
    assert (workspace.public / "skills/kestrel-launch/SKILL.md").read_text().endswith("## Legal notice\n\nA new notice.\n")


@pytest.mark.parametrize("license_text", [None, "  \n"])
def test_the_sync_stops_without_a_license(workspace, license_text):
    if license_text is None:
        (workspace.public / "SKILL_NOTICE.md").unlink()
    else:
        (workspace.public / "SKILL_NOTICE.md").write_text(license_text)
    code, out = workspace.sync(workspace.manifest(kestrel_files(workspace)))
    assert code == 1
    assert "SKILL_NOTICE.md" in out
    assert not (workspace.public / "skills").exists()


def test_the_repo_license_stays_out_of_skills(workspace):
    workspace.sync(workspace.manifest(kestrel_files(workspace)))
    assert REPO_NOTICE not in (workspace.public / "skills/kestrel-launch/SKILL.md").read_text()


def test_a_license_the_source_already_has_is_replaced(workspace):
    source = SKILL.replace("description: Launch a campaign\n", "description: Launch a campaign\nlicense: Old text\n")
    workspace.sync(workspace.manifest(kestrel_files(workspace, **{"skills/kestrel-launch/SKILL.md": source})))
    published = (workspace.public / "skills/kestrel-launch/SKILL.md").read_text()
    assert "Old text" not in published
    assert published.count("license:") == 1


def test_a_notice_the_source_already_carries_is_not_repeated(workspace):
    source = SKILL + f"\n## Legal notice\n\n{NOTICE}\n"
    workspace.sync(workspace.manifest(kestrel_files(workspace, **{"skills/kestrel-launch/SKILL.md": source})))
    published = (workspace.public / "skills/kestrel-launch/SKILL.md").read_text()
    assert published.count("## Legal notice") == 1

