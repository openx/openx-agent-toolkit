# Changelog

- **2.8.7**: Hands off to `openx-campaign-launch` and `openx-audience-build`, the campaign and audience skills' names with the `openx-` prefix.

- **2.8.6**: The tool-scope rule says the connector serves other tools with overlapping
  purposes, without naming backends.

- **2.8.5**: Names the products OpenXSelect and OpenXDirect, the spelling OpenX uses.

- **2.8.4**: `buyer_ids` takes seat ids, the `extra.third_party_buyer_id` values of a
  `deal.deal_participants.buyer_ids` option row, not the row's `id` (OpenX's internal buyer id,
  which the API refuses as "Seat … does not exist"). A seat that isn't mapped yet goes to the
  user's OpenX account team rather than being swapped for another.

- **2.8.3**: Names no internal environments: the environment step speaks of a test environment
  beside production, and the time-zone and geo-exclusion notes keep their checks without calling
  the behaviour unconfirmed. The list of behaviours still to test left `references/examples.md`, so
  agents no longer read it with the skill.

- **2.8.2**: Deals are called "Exchange Package (XP) deals" in what the user sees (the expansion
  first, as OpenX uses it externally), not plain "XP deal"; `pmp_deal_type="3"` is named "within Open
  Auction". `url_targeting` names its `type` values: `"whitelist"` for an allowlist, `"blacklist"`
  for a blocklist.

- **2.8.1**: "When something fails" keys on the server's own message for a reply it couldn't
  read ("The change went through, but this server couldn't read OpenX's reply …") instead of a
  `ValidationError` naming the response, which the server no longer returns for that case.

- **2.4.0**: Steps follow the repository skill template: inputs collected in "Before you start";
  action steps that each open with the tool call (rules, ids, targeting, forecast, confirm,
  package, deal); new Step 8 to activate on the user's go; tables moved to `references/`;
  standard `Not retryable` and response `ValidationError` handling in "When something fails".
- **2.3.1**: Fixed repository checks: unquoted `metadata.version`; package name checks use
  `searchOptionsByPath(path="package")`; `getSkill` added to the tool-loading list; no tools from
  other backends named.
- **2.3.0**: Restructured to the repository skill format: `author`, `version` and `title` in the
  frontmatter metadata; "Before you start" checklist; numbered steps; reference material moved to
  `references/` (values and errors, advanced targeting, summary formats, examples and open items).
  No behaviour changes.
- **2.2.0**: Run reporting moved to the very start and aligned with `oxs-campaign-launch`:
  `reportDiagnostics` before any other tool, with `context_window` when known, once per run,
  silent to the user, and non-blocking if it fails.
- **2.1.0**: Aligned with `oxs-campaign-launch`: explicit tool-loading list and "only these tools"
  rule; package-first creation instead of inline packages; polling `getDeal` for the `OX-...`
  code; timeout handling; `limit=20` on deal searches; exact device paths and the one-device
  minimum; `deal.currency` check; bulk deals; hand-off to `oxs-campaign-launch`.
- **2.0.0**: Diagnostics, environment and account selection; multi-DSP guidance; dates and time
  zones; floor vs fixed price; domains, exclusions, audiences and package reuse; pre-creation
  forecast; exact-match name check; explicit `status`, `account_id` and `instance_uid`;
  `deal_source` and wrong-account recovery; hand-off to `openx-deal-troubleshooter`; open items.
- **1.x**: Initial version.
