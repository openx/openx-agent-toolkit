---
name: openx-deal-creation
description: Create a new OpenX XP deal (with its targeting package) through the OpenX MCP tools, including resolving format, device, channel and geo targeting ids, demand partners, the format/channel/device compatibility and targeting-blocking rules (CTV vs viewability/VTR, Banner/Native vs TV devices, App-only/Web-only blocks), and avoiding the backend pitfalls that make createDeal fail or leave orphaned packages. Use whenever someone asks to create, set up, build, or make a new deal in OpenX, even casually ("create me a new deal", "set up a test deal for a Zurich mobile banner", "make a deal for TTD"), or when someone asks which formats, devices, channels or quality thresholds (viewability, VTR) can be combined in a deal, what deal type or pricing (floor vs fixed price) a new deal gets, or when a deal creation attempt has failed and needs recovery.
metadata:
  author: openx
  version: 2.8.7
  title: Create a deal
license: "This Skill is provided by OpenX and is subject to change. It is provided “as is” for use with your OpenX account and is subject to the OpenXSelect Portal Terms of Service (https://select.openx.com/terms/). Actions taken using this Skill are made under your OpenX account and are your responsibility. Review all actions and outputs before relying on them."
---

# Create an OpenX deal

The OpenX MCP exposes deals and packages as tools, but the tools do not tell you the order to
call them in, which targeting combinations OpenX allows, or which fields it requires that the
schema marks optional. This skill does. Follow the steps in order; each one names the tool and the
values that matter.

Every mutation here creates or changes real objects in the account the caller is signed into.
Create every deal **Paused**, and confirm with the user before Step 6 creates anything.

For a deal that is part of an OpenXDirect campaign build (order, line item, creative), use
`openx-campaign-launch` instead.

## Before you start

1. **Report the run** with `reportDiagnostics` before any other tool: pass
   `skill="openx-deal-creation"`, `skill_version` as the `version` in this skill's frontmatter (the
   header line above when the server returned the skill), `model` as your own model id, and
   `context_window` in tokens if your harness tells you it. Every argument is optional, so send
   what you know and skip the rest. The call writes one analytics line and changes nothing in
   the account. Call it once per run, do not mention it to the user, and carry on if it fails.
2. **Load this skill's tools.** Clients that search a connector's tools on demand may not have
   loaded every tool this skill calls. Before going on, make sure each of these is available in your
   session, and search the connector's tools by the exact name for any that is not:
   `activateAudience`, `archiveDeal`, `buildPackageInput`, `buildPackageTargeting`,
   `compileAudienceDefinition`, `createAudience`, `createDeal`, `createDealForecastingJob`,
   `createPackage`, `getDeal`, `getDealForecastingJob`, `getDealTargetingConfiguration`,
   `getPackage`, `getPackageTargeting`, `getSkill`, `listAccountsForProduct`, `listAudiences`,
   `listOptionPaths`, `listSegmentsByCategory`, `optionsByPath`, `reportDiagnostics`,
   `searchDealAudienceSegmentsByPrompt`, `searchDealBundlesByPrompt`,
   `searchDealDomainsByPrompt`, `searchOptionsByPath`, `updateDeal`. A step that names a tool you
   cannot see means load it, never skip the step or substitute another tool.
3. **Use only the tools this skill names.** The connector also serves other tools
   with overlapping purposes, such as a second deal lookup. Their ids, fields and money units are
   not interchangeable with the ones here, so never mix the two in one flow.
4. **Choose the environment, the account, and with it the instance.** The user may have more than
   one OpenX connector, such as a test environment beside production; deals created on production
   are real. For anything described as a test, ask whether to use a test environment, and never
   switch environments mid-run. Then call `listAccountsForProduct(product="SELECT")`, with `name_contains` when the
   user named the account. Use the only row, or ask the user to pick when there are several. Pass
   that row's `id` as `account_id` and its `instance_uid` as `instance_uid` on every create below,
   and the same `instance_uid` on every other call in this flow, reads included. Everything you
   create lands in that account. An empty list means the caller is not set up for OpenXSelect:
   stop and tell the user to request it. If a create comes back refused, read the error rather
   than retrying: it distinguishes an instance you cannot reach from a permission the account
   lacks, and says which to ask for.
5. **Collect the inputs** before the first mutation, and ask for anything missing in one message:
   - deal name, flight start and optional end (turn "within a week, for 1 month" into dates and
     show them)
   - the demand partner (DSP), which OpenX requires: offer DV360, Amazon DSP, The Trade Desk,
     Yahoo DSP and Viant, in exactly that order, and let the user name any other. DV360 needs
     exactly one buyer, so ask which one in the same message
   - format (`BANNER`, `VIDEO`, `CTV` or `NATIVE`), devices (desktop, mobile, TV) and channel
     (web, app or both); Step 1 gives the defaults for a format alone
   - the price: a CPM in the deal currency, a floor OpenX may adjust unless the user wants it
     fixed. Never fill it in or default it; if the user wants OpenX's minimum, that is 0.01 and
     they say so. Without a price from the user there is no deal to create yet
   - optional: geo, websites, apps, audiences, viewability or VTR threshold
   - the currency, which defaults to the account's `currency` field, or `USD` when it has none
6. **Know the units.** `deal_price` is a CPM in the deal currency, not micro-dollars. Dates are
   ISO 8601 timestamps in UTC. Option ids differ per instance, so look every one up. See
   [references/values.md](references/values.md) for the full table.
7. **Talk to the user in plain language.** Many users are sales or account managers. Never show
   tool names, field names or raw error text; say "OpenX", and describe rules as what OpenX allows
   ("OpenX doesn't allow a VTR target on CTV deals"). Keep internal ids to yourself, except the
   final deal code (`OX-...`), which you always share. Explain terms like VTR in a few words the
   first time.

## Step 1: Check the request against OpenX's rules

OpenX rejects a deal that breaks these rules, so check the request before you confirm anything. If
it breaks one, say so straight away and offer only alternatives that pass.

- **Format sets the defaults.** `BANNER` and `NATIVE`: App + Web, on desktop, phone and tablet,
  never TV devices. `VIDEO`: App + Web, on desktop, phone and tablet; TV devices can be added.
  `CTV`: App only, on Connected TV and Set Top Box only; the user can only drop one of those two.
  State the defaults you applied in the summary.
- **CTV rule.** "CTV on web" or "CTV on mobile" is impossible; the equivalent is `VIDEO`. Video on
  App only and TV devices only is a CTV setup, so ask whether to switch to CTV or add web or a
  non-TV device.
- **Quality thresholds.** Viewability works with Banner, Native and Video, not CTV. VTR works only
  with Video. Video attributes are blocked for Banner and Native; the CTV Content Object (genre)
  works only on CTV.
- **Channel blocks.** App only blocks domains, URL page, browser and keywords. Web only blocks app
  bundles and app names. CTV is App only, so it loses those too.
- **Inventory exclusions.** MFA inventory is always excluded: tell the user, do not ask. Excluding
  below-average quality domains is possible only for `BANNER` or `VIDEO` on Web only; then ask.
  "Exclude indirect inventory" only when the user asks.
- **For "TV plus a quality threshold"** offer, with their trade-offs: Video on App + Web on all
  devices including TV, with viewability; Video without TV, with viewability and/or VTR; Banner or
  Native on desktop and mobile, with viewability; CTV with no threshold.

## Step 2: Look up every id

`optionsByPath(path, filter, instance_uid)`, never guess an id. Use these exact paths:

- `deal.package.targeting.rendering_context.ad_placement`
- `deal.package.targeting.rendering_context.distribution_channel`
- `deal.package.targeting.rendering_context.device_type.desktop_devices`,
  `...device_type.mobile_devices` (map "mobile" to phone and tablet), `...device_type.tv_devices`
  (three separate paths; a combined `device_type` path is not implemented)
- `deal.package.targeting.viewability.viewability_score`, `deal.package.targeting.vtr.vtr_score`
- `deal.deal_participants.demand_partner`, and for seats `deal.deal_participants.buyer_ids` with
  `filter={"demand_partner_id": <id>}`; the unnarrowed seat list has thousands of rows. Each row is
  a buyer; its seat ids are in `extra.third_party_buyer_id`, and `buyer_ids` takes the seat the
  user means, not the row's `id` (see references/values.md for an unmapped seat)
- `deal.currency`; check the deal currency is in the list

Geo paths need a filter and a wildcard (`{"city": "zurich*"}`); see
[references/values.md](references/values.md). A kind of site or app ("US news sites", "sports
apps") is a content category, found with `searchOptionsByPath` on
`deal.package.targeting.domain.categories_iab_v2` and a name filter; it is never a domain list, so
do not reach for `searchDealDomainsByPrompt` for it. Websites, apps, exclusions, audiences, content
categories and reusing another deal's package are in
[references/advanced-targeting.md](references/advanced-targeting.md). When unsure of a path, call
`listOptionPaths`.

**Never target what you could not find.** A lookup that returns nothing for an app, a site, a
segment or any id the user named gets one more try with a broader filter (a shorter name, the
publisher's name, a different category). If that also returns nothing, stop and ask the user: say
what you searched for and what came back, and let them correct the name or drop it. Never add a
value the lookup did not return, never type a bundle id or domain from memory, and never put a
"close enough" row in its place. A deal that targets inventory which does not exist delivers
nothing, and the user will not know why.

## Step 3: Build the targeting

`buildPackageTargeting(ad_placement_val, distribution_channel_val, device_type_desktop |
device_type_mobile | device_type_tv)`, then `buildPackageInput(name, targeting)`

- At least one device type is required. `distribution_channel_val` is comma-delimited (`APP,WEB`).
- For `CTV`, leave `distribution_channel_val` out (the tool fills in `APP`) or pass `APP`; never
  `WEB`. Pair it with `device_type_tv`.
- Add the other dimensions to the returned targeting as comma-delimited id strings:
  `"geographic": {"includes": {"city": "<id>"}}`,
  `"viewability": {"viewability_score": {"op": ">=", "val": "0.70"}}`,
  `"vtr": {"vtr_score": {"op": ">=", "val": "0.70"}}`.
- Always add `"metacategory": {"exclude_mfa": true}`. Add
  `"inventory_quality": {"iq_score": {"op": ">=", "val": "30"}}` only when Step 1 allows it and the
  user said yes; 30 is the only value.
- `buildPackageInput` adds the fields OpenX requires (`locked_internal`, `is_curated`). Keep its
  result for the forecast; the package itself is created in Step 6.

## Step 4: Forecast (narrow targeting only)

`createDealForecastingJob(deal, package, instance_uid)`, then `getDealForecastingJob(job_id)`

- Offer it, in the same message as the summary, when the targeting is likely to be small: a city or
  postal code, a content category, a short site or app list, an audience, a high threshold. Do not
  run it unasked and do not hold the summary back for it.
- `deal` carries `name`, `currency`, `pmp_deal_type: "3"`, `deal_participants`, dates and
  `deal_price`; `package` is the `buildPackageInput` result. It creates nothing.
- Report the volume in plain words ("roughly X impressions a day"). For broad setups, offer a
  forecast after creation instead.

## Step 5: Confirm with the user

- Check the name first: `searchOptionsByPath(path="deal",
  filters=[{"name":"name","op":"_contains","val":["<name>"]}], limit=20, instance_uid)`, and the
  same search with `path="package"`. Always filter by name and keep `limit` small; an unfiltered
  search overflows the tool result. Only an exact match (ignoring case and surrounding spaces) is
  a conflict.
- Show the summary table from [references/summary.md](references/summary.md), with every row in
  its order: Account, Name, Dates, Currency, Price, Buyer (DSP), Format, Devices, Where ads run,
  Location and other targeting, Quality targets, Inventory exclusions, Deal type, Status.
- A price is never filled in for the user: if none was given, ask for it before creating. Mark
  the other values you filled in as "(standard)".
  Call the deal an "Exchange Package (XP) deal" the first time, "XP deal" after that, and show it
  as **Paused**.
- Anything the user asked for that the lookups did not return is left out of the targeting and
  named in the summary ("not found: com.example.app"), and you ask before creating.
- Create only after the user says yes.

## Step 6: Package

`createPackage(name, targeting, account_id, instance_uid)`

- Use the deal name and the Step 3 targeting. Keep the returned numeric `id`.
- Always create the package first and pass its id to the deal; never an inline `package`. An
  inline package is saved before the deal is checked, so a failed deal leaves it behind and a
  retry fails on its name.
- **One package for every deal that shares the targeting.** When the request is for several
  deals with the same targeting, create the package once and pass the same `package_id` to each
  deal. Do not give each deal its own package so that they can be edited apart later: a shared
  package is the normal setup for deals created together, each extra package repeats the whole
  targeting in the call and in the conversation, and a deal that later needs its own targeting
  can get a cloned package then (`createPackage` with `cloned_from`). Make a separate package
  only when the targeting differs or the user says these deals must be editable independently.
- Skip this step when reusing another deal's package.

## Step 7: Deal

`createDeal(name, currency, pmp_deal_type="3", start_date, end_date, package_id, deal_price,
deal_participants=[{"demand_partner": "<id>"}], status="Paused", account_id, instance_uid)`

- Always pass `status="Paused"`. Without it the deal is created **Active** and biddable by its
  participants immediately.
- `pmp_deal_type="3"` (within Open Auction) makes it an Exchange Package (XP) deal. Leave `deal_source` out for OpenXSelect accounts.
- `start_date` at `T00:00:00Z`, `end_date` at `T23:59:59Z` of the last day. For a start today, use
  the current UTC time rounded up to the next hour. Do not promise a local start hour: the flight
  may run in UTC rather than the account's time zone.
- `deal_participants` has one entry per DSP, each with optional `buyer_ids` and `brand_ids`. A
  DV360 entry needs exactly one buyer.
- `deal_price` alone is a floor that OpenX may adjust. For a fixed price, follow the create with
  `updateDeal(id, deal_price=<price>, fixed_cpm_enabled=True)`; if that fails, retry only the
  update, never the create.
- If the call times out, do **not** retry blindly. Run the Step 5 name search; if the deal is
  there, the create succeeded.
- **Wait for the deal code.** The `deal_id` (`OX-...`) is assigned asynchronously. Poll
  `getDeal(id)` until it is populated; that value is what the user and other skills need, never
  the numeric `id`.

**Many deals at once** (a bulk sheet, a set of variants): one package from Step 6, then one
`createDeal` per row with that `package_id`, `status="Paused"` and only that row's own fields
(name, dates, price, participants). Before each create, run the Step 5 name search and skip rows
that already exist, so a rerun does not duplicate deals. Show one summary for all rows and get a
single yes. Only rows whose targeting differs get a package of their own.

## Step 8: Activate (only after the user has seen what will go live and said yes)

`updateDeal(id, status="Active")`

Read back `getDeal(id)`. `Active` is the expected result. `Publishing` is **not an error**: the
deal's audience is still exporting, and the deal flips to `Active` on its own. Do not re-send the
update; tell the user it is not yet biddable, and re-read `getDeal(id)` if they want to wait.

## Report

Finish with one table: deal name, deal code (`OX-...`), status, price,
DSP, and the exclusions applied (MFA always, below-average quality domains when set). Then:

- `getPackage` returns only `rendering_context`, not geo; that is not missing targeting. For the
  full targeting use `getPackageTargeting`.
- `getDealTargetingConfiguration` returns `NOT_FOUND_NO_CONFIG` right after creation, because
  targeting compiles in the background. Re-check later to confirm geo, exclusions and categories.
- Offer next steps: buyer seats, a forecast, switching the deal on (Step 8). If this was a
  test, offer to remove it with `archiveDeal`, and only do it on the user's explicit yes.
- Delivery questions ("why isn't it spending") belong to `openx-deal-troubleshooter` (fetch it
  with `getSkill` if it is not loaded); a new or paused deal has no delivery yet. To buy on the
  deal with a campaign, switch to `openx-campaign-launch` with the `OX-...` code.

## When something fails

Match the error text against the table in [references/values.md](references/values.md) before
retrying. Most failures are a missing DSP, a blocked combination or a name that already exists, and
retrying with the same input will fail the same way.

An error that starts with `Wrong instance` means the object lives on another instance: find its `instance_uid` with `searchOptionsByPath` (which searches every instance you can see) and retry the same call once with it. An error that starts with `Not retryable` is final: the account lacks a permission or a feature. Stop, tell the user what the message says to request, and do not retry or try other arguments.

If a write comes back saying **the change went through but OpenX's reply couldn't be read**, the
write succeeded and only the reply failed to parse. Look the object up by name with
`searchOptionsByPath` (path `deal` or `package`) and continue from it; calling the write again
creates a duplicate.

- **No DSP, or DV360 without one buyer:** the package is already saved. Get the DSP or the buyer
  from the user, then create the deal with that `package_id`.
- **A package name that is not unique:** inspect the conflicting package with `getPackage`. If your
  failed attempt just created it (recent, matching targeting, no deal), reuse it with `package_id`;
  otherwise agree a new name with the user.
- **A blocked combination:** offer only the Step 1 alternatives.
- **A validation error asking for `deal_source`:** the login has no OpenXSelect account. Look up
  `optionsByPath("deal.deal_source")`, ask who originated the deal, and retry with that id.
- **Wrong account or environment noticed after creation:** change nothing on your own. Offer to
  pause the deal and create it in the right place; archive only on the user's explicit yes.

Worked examples are in [references/examples.md](references/examples.md).

## Legal notice

This Skill is provided by OpenX and is subject to change. It is provided “as is” for use with your OpenX account and is subject to the OpenXSelect Portal Terms of Service (https://select.openx.com/terms/). Actions taken using this Skill are made under your OpenX account and are your responsibility. Review all actions and outputs before relying on them.
