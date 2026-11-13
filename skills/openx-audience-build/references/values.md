# Values, statuses and error texts

## Dimensions

A Segment's `category` is its dimension: the `dimension` of a compileAudienceDefinition criterion,
and the `category` argument of listSegmentsByCategory.

| Dimension | Holds | How to find ids |
|---|---|---|
| `demographic_age` | one segment per year of age, 19 to 99, named by the year | `names=["25", ..., "34"]` |
| `demographic_gender` | `Male`, `Female` | `names=["Female"]` |
| `location` | users seen in a place over the past 90 days | `sub_category` `state` / `dma` / `congressional` / `zip`; states by full name |
| `predefined` | OpenX's own segments: interests, browsing, purchase propensity, occupation, life stage. Free. | prompt search, or `search` on listSegmentsByCategory |
| `direct` | data partner segments. Priced per CPM or percent of media. | prompt search (`sellable: true` rows only), or `search` |
| `lookalike` | lookalikes already built for an account | list them; most are expired |

Segment ids are UUIDs.

## Field values

| Field | Tool | Values |
|---|---|---|
| `export_type` | create / estimate / pricing / update | `oa_match` (default; required when segments come from several partners), `bidstream`, `bidstream_plus` (only where every partner's `allowed_export_types` includes it) |
| `export_targets` | create / estimate / pricing / update | any of `cookie`, `device` (mobile ad ids), `idl` (RampID), `id5`, `ctv`, `ip`. Not validated: a typo is accepted and matches nothing. Default `["cookie", "device", "idl", "id5"]` |
| `direct_audience_provider` | create / estimate / pricing / update | `openaudience` for OpenXSelect's own catalogue; other ids from `listProviders` |
| search mode filter | prompt search | `OPENX_PROPRIETARY` (OpenX only), `MARKETPLACE` (both), `OWN_ONLY` |
| gender and age filters | prompt search | `MALE` / `FEMALE`; `{"min": 25, "max": 54}`. They narrow the search; they do not add demographic segments |
| location filter | prompt search | `{"values": ["TX"], "type": "STATE"}`; `type` `STATE`, `DMA` or `CONGRESSIONAL_DISTRICT`, one kind per call. Narrows the search; it does not add a location segment |
| data partner filter | prompt search | partner ids from `optionsByPath(path="segment.data_partner")` |
| `limit`, `offset` | every list tool | required integers |

## Prompt search row fields

| Field | Meaning |
|---|---|
| `category` | `predefined` (OpenX) or `direct` (data partner) |
| `sellable` | for a `direct` row, whether this account can buy it; `false` with price 0 means unavailable, not free. OpenX rows show `false` and are usable |
| `segment_category` | the taxonomy label (`Activities/Interests`, `Purchase Behavior` ...); the value the search's category filter takes |
| `price_cpm`, `price_pom` | partner price per thousand impressions, or percent of media as a fraction |
| `reach` | the partner's catalogue size, not this audience's size; 0 is possible on browsing segments |
| `account_name` | the data partner (`OpenAudience` for OpenX rows) |
| `relevance` | 0 to 100 match score, highest first |
| `metrics` (top level) | totals over every row returned, not over the ones you keep |

## Audience `status`

| Value | Meaning | What to do |
|---|---|---|
| `draft` | created, never activated | activate when the user says so |
| `activated`, `publishing`, `exporting` | building and exporting | wait; hours |
| `exported` | **finished and targetable** | done |
| `expiring`, `expired` | a source segment stopped refreshing | build a replacement |
| `activate_failed`, `publish_failed`, `export_failed`, `expire_failed` | that step failed | report it and do not re-activate blindly |

`report_status` is separate: null until activation, then `processing`, then `complete`, when
the reach report starts working. `addressable_reach` is null until the audience has exported.

## Publish timing

| Event | Typical |
|---|---|
| Compile, estimate, pricing, create | under a few seconds |
| Activate to `exported`, first publish | 14 to 30 hours |
| Refresh | about a day |

## Error text and what to do

| Error contains | Cause | Fix |
|---|---|---|
| `Cannot read properties of null (reading 'operator')` on estimate | the prompt search's `normalized_definition` passed on as is | take its ids and compile your own |
| `non-existent segment ids in normalized definition` on estimate | an id is not a Segment id: a typo, or an audience, provider or account id | check each id with `getSegment` and replace the ones that return nothing |
| `estimate_available: false` / empty estimate | an id does not resolve: a typo, an expired segment, a state code instead of a location segment | check each id with `getSegment`, then retry |
| `Multi-provider audience has to have oa_match type` | segments from several partners with another export type | use `oa_match` |
| compile error naming a row | duplicate id, unknown parent, a cycle, a non-UUID id, excludes without includes, or more than two levels | fix that row |
| `names` `Input should be a valid list` | one name passed as a string | pass `["Texas"]` |
| reach report errors before `report_status` is `complete` | not computed yet | wait for `complete` |
| "The change went through, but this server couldn't read OpenX's reply …" after create or activate | the write went through; the reply did not parse | `getAudience(id)` and continue; do not create again |
