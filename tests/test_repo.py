from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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
