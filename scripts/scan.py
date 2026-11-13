"""Find a backend's internal terms in files about to be published.

The terms come from the backend's own repo, in its public-terms.txt, so this public repo
never lists them. One rule per line, "result: name: pattern", where result is "block",
which stops the sync, or "warn", which is reported while the sync goes ahead, and pattern
is a Python regular expression:

    block: codename: \\bPelican\\b
    block, outside links: chat room: #[a-z][a-z0-9-]{2,}
    warn: test environment: \\bstaging\\b

"outside links" reads each line with markdown link targets and hrefs taken out, so an
in-page anchor like [Deals](#deals) is not mistaken for a term. Credentials (API keys,
tokens, private keys) always block, whatever the backend lists.

The backend accepts a false positive in its public-allow.txt, one "path: term: reason" line
per finding, where path is the file's path in the backend's repo:

    skills/a-skill/SKILL.md: Pelican: the bird, not the codename
"""

from __future__ import annotations

import re
from dataclasses import dataclass

BLOCK = "block"
WARN = "warn"
_OUTSIDE_LINKS = ", outside links"

_MARKDOWN_LINK_TARGET = re.compile(r"\]\([^)]*\)")
_HREF = re.compile(r'href="[^"]*"')


@dataclass(frozen=True)
class Rule:
    name: str
    result: str
    pattern: re.Pattern[str]
    skip_link_targets: bool = False


CREDENTIALS = Rule(
    "credential",
    BLOCK,
    re.compile(
        r"\bgh[pousr]_[A-Za-z0-9]{36,}"
        r"|\bAKIA[0-9A-Z]{16}\b"
        r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
        r"|\bxox[abprs]-[A-Za-z0-9-]{10,}"
        r"|\bAIza[0-9A-Za-z_-]{35}"
        r"|\beyJ[\w-]{10,}\.eyJ[\w-]{10,}\.[\w-]{10,}"
    ),
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    term: str
    rule: str
    result: str


def scan_text(path: str, text: str, rules: tuple[Rule, ...]) -> list[Finding]:
    """Every rule match in the text, once per line, term and rule."""
    findings: list[Finding] = []
    seen: set[tuple[int, str, str]] = set()
    for number, line in enumerate(text.splitlines(), start=1):
        without_links = _HREF.sub("", _MARKDOWN_LINK_TARGET.sub("]", line))
        for rule in rules:
            for match in rule.pattern.finditer(without_links if rule.skip_link_targets else line):
                key = (number, match.group(0), rule.name)
                if key not in seen:
                    seen.add(key)
                    findings.append(Finding(path, number, match.group(0), rule.name, rule.result))
    return findings


def parse_terms(text: str) -> tuple[Rule, ...]:
    """The rules a public-terms.txt lists, after the credential rule every scan runs."""
    rules: list[Rule] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(": ", 2)
        result = parts[0].removesuffix(_OUTSIDE_LINKS)
        if len(parts) != 3 or result not in (BLOCK, WARN) or not parts[1].strip() or not parts[2]:
            raise ValueError(
                f"public-terms.txt line {number} should read 'block: name: pattern' or "
                f"'warn: name: pattern', not {raw!r}"
            )
        try:
            pattern = re.compile(parts[2])
        except re.error as error:
            raise ValueError(f"public-terms.txt line {number}: {error}") from error
        rules.append(Rule(parts[1].strip(), result, pattern, parts[0].endswith(_OUTSIDE_LINKS)))
    if not rules:
        raise ValueError("public-terms.txt lists no rules, so the scan would check nothing")
    return (CREDENTIALS, *rules)


def parse_allowlist(text: str) -> set[tuple[str, str]]:
    """The (path, term) pairs a public-allow.txt accepts. Every line needs a reason."""
    allowed: set[tuple[str, str]] = set()
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part.strip() for part in line.split(": ", 2)]
        if len(parts) != 3 or not all(parts):
            raise ValueError(
                f"public-allow.txt line {number} should read 'path: term: reason', not {raw!r}"
            )
        allowed.add((parts[0], parts[1]))
    return allowed
