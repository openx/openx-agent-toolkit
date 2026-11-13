import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _section(heading: str) -> str:
    """The README text under one `## heading`, up to the next one."""
    return (ROOT / "README.md").read_text().split(f"\n## {heading}\n", 1)[1].split("\n## ", 1)[0]


def test_every_skill_the_readme_lists_is_in_the_repo():
    """The sync adds and removes skill folders, and the README's table is edited by hand, so a
    row can outlive its skill."""
    listed = re.findall(r"^\| `([\w-]+)` \|", _section("Skills"), flags=re.MULTILINE)
    assert listed, "the Skills table lists no skill"
    missing = [name for name in listed if not (ROOT / "skills" / name / "SKILL.md").is_file()]
    assert not missing, f"README lists skills that are not under skills/: {missing}"


def test_the_command_the_readme_gives_as_an_example_is_a_skill_in_the_repo():
    """A skill's command is its name without the openx- prefix."""
    commands = re.findall(r"`/([\w-]+)`", _section("Using the skills"))
    assert commands, "the README gives no command as an example"
    missing = [command for command in commands if not (ROOT / "skills" / f"openx-{command}" / "SKILL.md").is_file()]
    assert not missing, f"README names commands with no skill under skills/: {missing}"


def test_the_readme_license_section_is_the_license_text():
    """README and LICENSE carry the repo notice word for word; skills carry SKILL_NOTICE.md instead."""
    readme = (ROOT / "README.md").read_text()
    section = readme.split("\n## License\n", 1)[1].strip()
    assert section == (ROOT / "LICENSE").read_text().strip()


def test_the_license_links_the_terms_over_https():
    text = (ROOT / "LICENSE").read_text()
    assert "https://select.openx.com/terms/" in text
    assert "http://" not in text


def test_the_skill_notice_is_its_own_text_and_links_the_terms_over_https():
    skill_notice = (ROOT / "SKILL_NOTICE.md").read_text()
    assert "https://select.openx.com/terms/" in skill_notice
    assert "http://" not in skill_notice
    assert skill_notice.strip() != (ROOT / "LICENSE").read_text().strip()
