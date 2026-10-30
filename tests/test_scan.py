import pytest
import scan

# Made-up terms: this repo is public, so its tests never name a real internal one.
TERMS = """\
# a backend's public-terms.txt

block: codename: \\bPelican\\b
block, outside links: chat room: (?<![\\w&/])#[a-z][a-z0-9-]{2,}
warn: test environment: \\bstaging\\b
"""
RULES = scan.parse_terms(TERMS)


def terms(text: str, result: str | None = None) -> set[str]:
    return {f.term for f in scan.scan_text("f.md", text, RULES) if result is None or f.result == result}


def test_the_terms_file_gives_the_rules_after_the_credential_rule():
    assert [(rule.name, rule.result, rule.skip_link_targets) for rule in RULES] == [
        ("credential", scan.BLOCK, False),
        ("codename", scan.BLOCK, False),
        ("chat room", scan.BLOCK, True),
        ("test environment", scan.WARN, False),
    ]


def test_block_and_warn_terms_are_found_by_result():
    text = "Project Pelican, tested on staging."
    assert terms(text, scan.BLOCK) == {"Pelican"}
    assert terms(text, scan.WARN) == {"staging"}


def test_an_outside_links_rule_skips_anchors_and_hrefs():
    text = '[Deals](#deals) <a href="#top">top</a>, but ask in #sample-room'
    assert terms(text) == {"#sample-room"}


def test_a_rule_without_outside_links_still_reads_link_targets():
    assert terms("[home](https://example.com/Pelican)") == {"Pelican"}


def test_credentials_block_whatever_the_terms_file_lists():
    text = "token ghp_" + "a" * 36 + ", -----BEGIN RSA PRIVATE KEY-----"
    found = {(f.term, f.rule) for f in scan.scan_text("f.md", text, RULES)}
    assert found == {("ghp_" + "a" * 36, "credential"), ("-----BEGIN RSA PRIVATE KEY-----", "credential")}


def test_findings_carry_their_line_numbers():
    findings = scan.scan_text("skills/a/SKILL.md", "fine\nsee Pelican\nfine", RULES)
    assert [(f.path, f.line, f.term) for f in findings] == [("skills/a/SKILL.md", 2, "Pelican")]


@pytest.mark.parametrize(
    "line",
    ["block: codename", "stop: codename: x", "block: : x", "block: codename: ", "warn, everywhere: name: x"],
)
def test_terms_lines_need_a_result_a_name_and_a_pattern(line):
    with pytest.raises(ValueError, match="line 1"):
        scan.parse_terms(line)


def test_a_pattern_that_does_not_compile_names_its_line():
    with pytest.raises(ValueError, match="line 2"):
        scan.parse_terms("block: a: x\nblock: b: (unclosed")


def test_a_terms_file_with_no_rules_is_refused():
    with pytest.raises(ValueError, match="no rules"):
        scan.parse_terms("# nothing yet\n")


def test_allowlist_reads_path_and_term_and_skips_comments():
    text = "# accepted findings\n\nskills/a/SKILL.md: staging: the word, not the environment\n"
    assert scan.parse_allowlist(text) == {("skills/a/SKILL.md", "staging")}


@pytest.mark.parametrize(
    "line", ["skills/a/SKILL.md: staging", "skills/a/SKILL.md: staging: ", "just a note"]
)
def test_allowlist_lines_need_a_reason(line):
    with pytest.raises(ValueError, match="line 1"):
        scan.parse_allowlist(line)
