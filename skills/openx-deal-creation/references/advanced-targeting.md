# Advanced targeting

Read this when the request includes websites, apps, exclusions, audiences, content categories or
"the same targeting as another deal". The compatibility rules in SKILL.md Step 1 still apply:
domains do not work on App-only deals, apps do not work on Web-only deals.

## Finding websites (domains)

Decide which of three cases the request is before calling anything:

1. **A kind of site** ("US news sites", "sports sites", "finance sites") is a content category,
   not a domain list. Find it with `searchOptionsByPath(path="deal.package.targeting.domain.categories_iab_v2",
   filters=[{"name": "name", "op": "_contains", "val": ["news"]}], limit=20)` and target the id
   (see the content categories section below). Add the country as geo targeting. The deal then
   runs on every site classified that way, with no list to maintain.
2. **Named sites** go straight into the package's `url_targeting` as an allowlist
   (`type="whitelist"`), or as a blocklist (`type="blacklist"`) for the ones to exclude ("but not
   dailymail.co.uk"). No search needed.
3. **A description neither covers** ("independent cooking blogs with high viewability") is the
   only case for `searchDealDomainsByPrompt(query, geography=[ISO codes], device_type,
   media_subtype, limit)`. `media_subtype` is `Display` (for Banner), `Video` or `Native`. It
   returns at most `limit` domains (50 by default), loosely ranked: keep the ones that really fit
   and show the user a short list to approve. Never add domains the user has not seen.

## Finding publisher apps

Look up every app the user named with `searchDealBundlesByPrompt` (with `geography`,
`device_type`, `media_subtype`, `limit`) and target only the bundle ids it returns; a name alone
is never enough to build an id from. When the user names websites but also wants apps, offer
App + Web and look up the publishers' apps the same way. Scan for
bundle ids that really belong to the publisher: Android ids often carry the reversed domain
(`com.examplenews.app`), Apple App Store ids are plain numbers, so go by the `platform` field and the name,
not the id shape. Tell the user which apps you found and which you did not, and do not pad the
list with unrelated apps. An app the user named that no lookup returns is never added: after one
retry with a broader query, stop, say which apps were found and which were not, and ask whether to
go ahead without it or try another name.

## Exclusions (geo, domains, apps)

- Geo exclusions go in the `excludes` branch next to `includes`, e.g.
  `"geographic": {"excludes": {"city": "<id>"}}`. Check the `buildPackageTargeting` /
  `buildPackageInput` schema for this shape before using it, and after creation confirm with
  `getDealTargetingConfiguration` that it shows as blocked, not targeted.
- For domain or app block lists, check the same schema for the field rather than guessing a key.
  An exclusion that silently becomes an inclusion is the worst outcome; if the schema does not make
  the shape clear, tell the user you cannot add that exclusion reliably yet.

## Audiences

An audience is a separate object that must exist and be active before a package can use it.
Ask before creating one, and reuse a suitable one found with `listAudiences`.

1. Find segments. Age, gender, location and the interest categories are exact lookups:
   `listSegmentsByCategory(category, names or search)` returns those rows directly, so use it
   first. Only a description that spans categories ("adults 25-45 interested in travel") needs
   `searchDealAudienceSegmentsByPrompt(query, filters, limit)`, which returns at most `limit`
   segments (20 by default) with their combined reach. Let the user approve them. A segment the user
   named that neither lookup returns is never added: say so and ask, as with apps.
2. Build the definition from the approved segment ids with `compileAudienceDefinition` (Step 4
   of the openx-audience-build skill, read it with `getSkill`). Then `createAudience(...)` with the
   compiled definition and the `account_id`, then `activateAudience`.
3. Reference it from the package targeting; look up the field in the schema, do not guess it.
4. While the audience exports, the deal shows **Publishing** instead of Active or Paused. Tell the
   user this is expected.

This flow has not been run end to end yet. If any step fails, explain plainly and offer the deal
without the audience.

## Reusing an existing package

For "the same targeting as <deal>" or several deals sharing targeting, find the package id with
`getDeal`, show its targeting from `getPackageTargeting(package_id)` in plain words, then pass
`package_id` to `createDeal`. Explain that the deals share one setup, so a targeting change on one
changes all of them. If the user wants them independent, build a new package.

## Genre and content categories (IAB v2)

- **Genre** (`instream_content.genre`) is part of the CTV Content Object category, blocked for
  Banner, Native and Video. It works only on CTV deals.
- Genre and content rating (`instream_content.contentrating`) take the option's `name` from
  `optionsByPath`, not its `id`; an id such as `"7"` is refused. For example:
  ```json
  "instream_content": {"genre": {"block": ["Comedy"]}, "contentrating": {"block": ["PG-13"]}}
  ```
- On other formats, offer **content categories**: they classify the whole site or app by the IAB
  Content Taxonomy 2.0 and work for every format.
- Look them up with `searchOptionsByPath(path="deal.package.targeting.domain.categories_iab_v2",
  filters=[{"name": "name", "op": "_contains", "val": ["comedy"]}], limit=20)`; the unfiltered
  list is about 700 rows and far too long to read. Each row has `id`, `name` and `extra.parent`.
- Offer every close match. For "comedy" on the tested instance: Humor and Satire (440, under Pop
  Culture 432; broadest), Comedy TV (646), Comedy Movies (330), Comedy Events (183), Comedy (Music
  and Audio) (348). Re-check ids on yours.
- Set it as (several ids comma-delimited mean "any of"):
  ```json
  "domain": {"categories_iab_v2": {"op": "INTERSECTS", "val": "440"}}
  ```
- Tell the user the category applies to whole sites and apps, not sections, and that category plus
  location can shrink inventory a lot, so suggest a forecast.
- **Known quirk:** `buildPackageInput` echoed the key as `categories_iab_v_2`. Make sure the package
  you pass reads `categories_iab_v2`, and confirm with `getDealTargetingConfiguration` after
  creation.

## Verifying exclusions

Once processed, `getDealTargetingConfiguration` lists the quality exclusion as
`Inventory Quality - Exclude Below-Average Quality Domains` "is at least 30.00", and MFA as a
blocked `OpenX Categories` value `mfa`. If a processed deal shows no such line, it is not on.
