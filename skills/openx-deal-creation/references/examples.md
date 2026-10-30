# Worked examples and open items

## Example 1: straightforward create with a leftover package

User: "Name: Example banner test. Start within a week, for 1 month. Banner on mobile, for Zurich,
Switzerland." Later: "create with TTD."

- Dates 2026-10-05T00:00:00Z to 2026-11-05T23:59:59Z. USD, `pmp_deal_type` "3", Paused.
- Targeting: BANNER, `APP,WEB`, mobile `phone,tablet`, city looked up with `zurich*` and checked
  against `extra.country`.
- DSP: The Trade Desk, id from `optionsByPath`.
- A first attempt without a DSP was rejected but left a package; the retry reused it with
  `package_id`. Result: a paused deal with an `OX-...` code at the user's price.

## Example 2: blocked combinations

User: "Example CTV test, starting tomorrow, TTD, CTV on web devices." Then: "add viewability on
70%." Then "CTV with VTR", "banner on TV devices", "native on TV devices", "CTV on mobile?"

Each breaks a Step 1 rule: CTV requires App, CTV blocks viewability and VTR, Banner and Native
block TV devices, CTV cannot target mobile. Answer the first message straight away: CTV is
App-only on TV devices with no viewability or VTR, and offer the alternatives. For "TV plus
viewability" the closest valid option is Video on App + Web, on Desktop, Mobile and TV, with 70%
viewability.

## Example 3: DV360 without a buyer, quality exclusion on Web

User: "create a deal: banner on web." Then: "Example banner web test, start tomorrow, dv360."
Then: "yes, exclude them." Later: "change it then to TTD."

- Banner on Web only, so the below-average quality question applies; the user said yes, so the
  package got `metacategory.exclude_mfa: true` and `inventory_quality.iq_score >= "30"`.
- DV360 without a buyer was rejected but the package was saved. "Before you start" now asks for the buyer up
  front.
- The user switched to The Trade Desk; the deal reused the saved package. Result: a paused Exchange Package (XP) deal
  with an `OX-...` code at the user's price.

## Example 4: genre on a banner deal, solved with a content category

User: "Spring banner test, starting Monday for 1 month, banner on mobile in Poland, The Trade
Desk." Then: "add genre: comedy." Then: "Humor and Satire sounds good." Then: "write more
precisely what is targeted."

- BANNER, `APP,WEB`, `phone,tablet`, country `pl` (looked up with `poland*`). MFA excluded; the
  quality exclusion does not apply (App + Web).
- Genre is CTV-only, so comedy categories were offered; the user chose Humor and Satire,
  `domain.categories_iab_v2` `INTERSECTS` `"440"`.
- The precise summary named each dimension and the category id, and explained that the category
  applies to whole sites and apps.
