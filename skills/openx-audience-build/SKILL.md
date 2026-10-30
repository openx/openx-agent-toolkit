---
name: openx-audience-build
description: Build, size, price and activate an OpenXSelect audience through the OpenX MCP tools - turn a plain-language description of who a campaign should reach into segments, a compiled definition, a reach estimate, a price, a saved audience and an export you can check on. Use when asked to find, build, size, estimate, price, create, edit or activate an audience in OpenXSelect, to turn a persona or RFP audience brief into a targetable audience, to answer "how many people are X in Y", or to check whether an audience has finished publishing. For the deal or line item that will target the audience (publishers, domains, apps, geo of the ad request), use openx-deal-creation or openx-campaign-launch instead.
metadata:
  author: openx
  version: 1.3.0
  title: Build an audience
license: "This Skill is provided by OpenX and is subject to change. It is provided “as is” for use with your OpenX account and is subject to the OpenXSelect Portal Terms of Service (https://select.openx.com/terms/). Actions taken using this Skill are made under your OpenX account and are your responsibility. Review all actions and outputs before relying on them."
---

# Build, size and activate an audience

An audience is a saved set of people: segments combined with AND, OR and EXCEPT. The platform
turns it into lists of ids and exports them, so a deal or line item can target it. The tools cover
every step, but they do not say which segments to use for each part of a brief, which segments are
unusable, or how to check that a definition means what the user asked for. This skill does.

An audience is about *who*. *Where* the ad runs (publishers, domains, apps, the location of the ad
request) is targeting on a package or line item, and this skill does not set it (see Step 8).

Lookups, compiling, estimating and pricing change nothing. Creating writes a draft audience;
activating starts an export that takes hours, so confirm with the user before Steps 6 and 7.

## Before you start

1. **Report the run** with `reportDiagnostics` before any other tool: pass
   `skill="openx-audience-build"`, `skill_version` as the `version` in this skill's frontmatter (the
   header line above when the server returned the skill), `model` as your own model id, and
   `context_window` in tokens if your harness tells you it. Every argument is optional, so send
   what you know and skip the rest. The call writes one analytics line and changes nothing in
   the account.
2. **Load this skill's tools.** Clients that search a connector's tools on demand may not have
   loaded every tool this skill calls. Before going on, make sure each of these is available in your
   session, and search the connector's tools by the exact name for any that is not:
   `activateAudience`, `archiveAudience`, `compileAudienceDefinition`, `createAudience`,
   `estimateAudience`, `explainAudienceDefinition`, `getAudience`, `getAudiencePricing`,
   `getAudienceReachReport`, `getExport`, `getSegment`, `getSkill`, `listAccountsForProduct`,
   `listAudiences`, `listExportsByAudienceId`, `listProviders`, `listSegmentsByCategory`,
   `optionsByPath`, `reportDiagnostics`, `searchDealAudienceSegmentsByPrompt`, `searchOptionsByPath`,
   `updateAudience`.
   A step that names a tool you cannot see means load it, never skip the step or substitute
   another tool.
3. **Use only the tools this skill names.** The connector also serves other tools
   with overlapping purposes; their ids and fields are not interchangeable with the ones here.
4. **Choose the account** before Step 6. Call `listAccountsForProduct(product="SELECT")`, with
   `name_contains` when the user named one. Use the only row or ask the user to pick, and pass its
   `id` as `account_id` on the create. The audience tools take no instance argument. Pricing in
   Step 5 is always worked out for your own account, so say that when the audience is for another
   account: its price can differ.
5. **Read the brief** for who to reach (age, gender, where they live, interests, purchase
   behaviour, life stage, occupation) and who to leave out, if anyone. A sizing question such as
   "how many people are runners in Texas" is enough to go straight to Steps 1 to 5. Ask only when
   you cannot tell who the audience is, and then in one message. The name, description and
   whether to activate are asked for at the end of Step 5, not here.

Terms used below (segment, dimension, OAID, export type) are defined in
[references/terminology.md](references/terminology.md). Values, statuses and error texts are in
[references/values.md](references/values.md).

## Step 1: Split the brief by dimension

Every segment belongs to one dimension, the Segment's `category`, and each part of a brief maps to
one. Write the brief down as rows before calling anything:

| Brief says | Dimension | Found with |
|---|---|---|
| age range | `demographic_age` | Step 2, exact `names` |
| gender | `demographic_gender` | Step 2, exact `names` |
| lives in / has been in a state, DMA, congressional district or ZIP | `location` | Step 2, exact `names` |
| interests, intent, purchases, life stage, occupation, browsing | `predefined` (OpenX, free) or `direct` (data partners, priced) | Step 3 |
| an existing lookalike | `lookalike` | Step 2, list them |

"People in Texas" is the Texas `location` segment: users seen there in the past 90 days.
"Ads shown in Texas" is geo targeting on the package or line item, not part of the audience. Read
a place in the brief as the `location` segment and say so in the Step 4 read-back; ask only when
the brief clearly means where the ads run. "People who read running sites" is an
audience (predefined browsing segments); "ads on running sites" is inventory, not an audience.

[references/persona-playbook.md](references/persona-playbook.md) maps the parts of an agency
persona brief onto dimensions, with two worked examples.

## Step 2: Look up demographic, location and lookalike ids

`listSegmentsByCategory(limit, offset, category, sub_category, search, names)`

- **Age:** `category="demographic_age"`, `names` = every year in the range as a string,
  `["25", "26", ..., "34"]`. There is one segment per year, 19 to 99, and no range segments.
- **Gender:** `category="demographic_gender"`, `names=["Female"]` or `["Male"]`.
- **Location:** `category="location"`, `sub_category` `"state"`, `"dma"`, `"congressional"` or
  `"zip"`. States go by full name (`"Texas"`, not `"TX"`), DMAs by market name, ZIPs by code. Use
  `names` for exact matches (several at once) and `search` for part of a name.
- **Lookalike:** `category="lookalike"`, then pick by name. Most listed today are expired.
- **Use these, not look-alikes from a search.** A prompt or name search also returns partner
  segments that sound like ages or places; they are not what the audience form uses and they
  are priced.
- **Keep only rows with `status: "ready"`.** The list includes expired segments and has no status
  filter, and an expired segment adds nobody to the audience.
- `names` must be a JSON list, even for one name.

## Step 3: Find interest segments

Use either or both, one call per trait cluster ("runners", "buys running shoes"), not one call
for the whole brief:

- `searchDealAudienceSegmentsByPrompt(query, filters)` searches by meaning across OpenX and data
  partner segments and returns prices. It has no limit: an unfiltered call returns about 30 rows
  and 25 KB or more. Keep queries specific. Setting the search-mode filter to `OPENX_PROPRIETARY`
  returns OpenX segments only (the tool's description lists the filter keys). The category filter
  takes a row's `segment_category` label, such as `"Activities/Interests"`, not a dimension:
  `["predefined"]` returns nothing.
- `listSegmentsByCategory(category="predefined", search="<word>", limit=20, offset=0)` (or
  `category="direct"`) matches a word in the name or description. Use it when you know the word.

Per row, keep it only when:

- `category` is `predefined` (OpenX rows show `sellable: false` too, and are free to use), or it is
  `direct` with `sellable: true`. A direct row with `sellable: false` shows a price of 0 because
  this account cannot buy it, not because it is free.
- its `status` is `"ready"` (listSegmentsByCategory rows; check with `getSegment(id)` when unsure).

**Take the ids, never the search's `normalized_definition`.** It folds in the unsellable rows, and
the estimate rejects it with `Cannot read properties of null (reading 'operator')`, even though the
tool description calls it ready to use. Compile your own in Step 4.

Show the user the shortlist (name, partner, OpenX or partner, CPM) before going on when the brief
leaves the choice open.

## Step 4: Compile the definition and read it back

`compileAudienceDefinition(nodes, criteria)` builds the `normalized_definition`. Never write that
JSON by hand. An audience is `includes EXCEPT excludes`; both roots exist already and OR their
children.

The usual persona is "this age AND this place AND (any of these interests, from any source)":

```
nodes:    [{"id": "persona",  "parent": "includes", "operator": "INTERSECT"},
           {"id": "interest", "parent": "persona",  "operator": "UNION"}]
criteria: [{"node": "persona",  "dimension": "demographic_age", "segment_ids": [<ages>]},
           {"node": "persona",  "dimension": "location",        "segment_ids": [<Texas>]},
           {"node": "interest", "dimension": "predefined",      "segment_ids": [<OpenX ids>]},
           {"node": "interest", "dimension": "direct",          "segment_ids": [<partner ids>]}]
```

- **Two interest criteria on the same INTERSECT node means "in both".** Putting the predefined and
  direct rows straight on `persona` compiles to `predefined AND direct`: a person has to be in an
  OpenX segment and in a partner segment. In a live run that cut the estimate from 3.2M to 0.6M
  OAIDs. Put interests that should OR in a UNION child node, as above, unless the brief really
  means both.
- Segments inside one criterion are ORed. Pass `operator: "INTERSECT"` on a criterion only when
  every segment in it must match.
- **Exclusions go under `excludes`** (`"node": "excludes"`), and nowhere else. A NOT on the deal's
  package targeting is not part of the audience.
- Two personas are two INTERSECT nodes under `includes`; the audience is anyone in either.
- A non-US segment needs `region` (e.g. `"EU"`) or `countries` on its node.
- **Read `expression` back to the user as a sentence** ("people aged 25 to 34 seen in Texas who
  are runners in an OpenX or a partner segment") and fix the rows until it matches the brief. The
  compiler does exactly what the rows say. Act on every line in `warnings`.

Add one row at a time when the audience is complex, and compile and estimate after each.

## Step 5: Estimate and price

Pass the compiled `normalized_definition` unchanged to both. The arguments are the same as Step 6's,
and neither writes anything, so iterate here. Both need a `name`: use a working name drawn from the
brief ("Runners 25-34 Texas") rather than asking the user for one.

`estimateAudience(name, export_type="oa_match", export_targets, direct_audience_provider="openaudience", normalized_definition)`

- One row per id type. `oaid` (OpenX's person-level id) is the headline number; also report
  `device` and `ip`. Cookie, IDL and ID5 rows can be 0 by design.
- An empty list with `estimate_available: false` usually means an id does not resolve (a typo, an
  expired segment, a state code where a location segment belongs). Check the ids before retrying.
- `non-existent segment ids in normalized definition` means an id is not a Segment id. Check each
  with `getSegment` and replace the ones that return nothing.

`getAudiencePricing(name, export_type="oa_match", export_targets, direct_audience_provider="openaudience", normalized_definition)`

- Returns each data partner paid, with its CPM and percent of media (`0.13` is 13%), and the
  audience total. Null means nothing in it is paid for, e.g. OpenX segments only.
- Partners under an OR are averaged and partners under an AND are summed. Partners in one OR
  criterion that is itself ANDed with other dimensions are summed too, which can double the price;
  in a live run, the shape in Step 4 priced two partners at $0.75 CPM, while the same partners
  directly on the INTERSECT node priced at $1.50. Use the Step 4 shape, and quote the total as the
  tool returns it.

Show the user the expression in words, the OAID, device and IP counts, and the partners with the
total price. For a sizing question, stop here. To save the audience, get a yes, and in the same
message ask for a name, a one-line description, and whether to activate it or stop at a draft.

## Step 6: Create (only with the user's yes)

`createAudience(name, description, export_type="oa_match", export_targets=["cookie", "device", "idl", "id5"], direct_audience_provider="openaudience", normalized_definition, account_id)`

- **Always pass `description`.** One line on who the audience is.
- `export_targets` keys are not validated: a misspelt key is accepted and matches nothing. Copy them
  from [references/values.md](references/values.md).
- `export_type` other than `oa_match` works only when every partner allows it (`listProviders`
  shows each provider's `allowed_export_types`); an audience with segments from several partners
  must be `oa_match`.
- `direct_audience_provider` is `openaudience` for OpenXSelect's own catalogue.
- The audience is created as `draft`. Keep the returned `id`.
- If the call times out, look for it by name in the same account before creating it again:
  `searchOptionsByPath(path="audience", filters=[{"name":"name","op":"_eq","val":["<name>"]}, {"name":"account_id","op":"_eq","val":["<account_id>"]}])`.

## Step 7: Activate, then check the export (only with the user's yes)

`activateAudience(id)`, then `getAudience(id)`.

- Publishing takes **hours** (about 14 to 30 for a first publish). Do not poll in a loop:
  give the user the id and a time to check back.
- `status` goes `draft`, `activated`, `publishing`, `exporting`, then **`exported`**, which is the
  finished, targetable state. Failure states end in `_failed`.
- **Do not update an activated audience** for a small change, a rename included: any update restarts
  the publish, and the deals that target it wait until it finishes. Ask first.
- `listExportsByAudienceId(limit=10, offset=0, audience_id)` lists one row per publish or refresh;
  the newest `created_date` is the current one, and `getExport(id)` reads one row. An empty list right
  after activating is normal.
- `getAudienceReachReport(id)` works only once the audience's `report_status` is `"complete"`; before
  that it errors. That is not a broken audience.

## Step 8: Hand off

Targeting the audience is the next job, and another skill covers it. Say which, and stop:

- a curated deal: `getSkill("openx-deal-creation")`. The package targets the audience by id; a deal
  created before the audience reaches `exported` waits in `Publishing` and starts on its own.
- an OpenXDirect campaign (order, line item, creative): `getSkill("openx-campaign-launch")`.

Publishers, domains, apps and the location of the ad request are set there, not here.

## Editing an existing audience

`getAudience(id)`, then `explainAudienceDefinition(normalized_definition)` turns its definition into
the same rows Step 4 takes, plus its expression and warnings. Edit the rows, compile, estimate and
price (Step 5), then `updateAudience(id, normalized_definition)` with the user's yes. Match the rows'
segment ids against the audience's `audience_segments` for names. For an activated audience, see the
rule in Step 7 first.

## What there is no tool for

Say so plainly instead of approximating:

- **Creating a lookalike.** Existing lookalikes can be used (Step 2); a new one cannot be built here.
- **Uploading a first-party list** (CRM file, hashed emails). Site visitors from the account's own
  pixel are retargeting segments, a separate flow.
- **Overlap between two segments** other than by estimating each alone and both together.

## Report

Finish with one table: audience id, name, status, the expression in words, OAID / device / IP
estimate, partners with CPM and the total price. Link the audience to the `url` that
`createAudience` or `getAudience` returned, so the user can open it in OpenXSelect. Then say what
happens next: when to check back on
the publish, and which skill attaches it to a deal or line item. If it was a test, offer
`archiveAudience(id)`.

## When something fails

Match the error text against the table in [references/values.md](references/values.md) before
retrying; most failures here are a definition problem, and the same input fails the same way.

An error that starts with `Wrong instance` means the object lives on another instance: find its `instance_uid` with `searchOptionsByPath` (which searches every instance you can see) and retry the same call once with it. An error that starts with `Not retryable` is final: the account lacks a permission or a feature. Stop, tell the user what the message says to request, and do not retry or try other arguments.

## Legal notice

This Skill is provided by OpenX and is subject to change. It is provided “as is” for use with your OpenX account and is subject to the OpenXSelect Portal Terms of Service (https://select.openx.com/terms/). Actions taken using this Skill are made under your OpenX account and are your responsibility. Review all actions and outputs before relying on them.
