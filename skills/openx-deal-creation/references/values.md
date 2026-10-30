# Values, lookups and recovery

## Units and formats

| Field | Tool | Type | Unit |
|---|---|---|---|
| `deal_price` | `createDeal`, `updateDeal` | number | CPM in the deal currency (not micro-dollars; see open items in [examples.md](examples.md)) |
| `start_date`, `end_date` | `createDeal`, `createDealForecastingJob` | string | ISO 8601 in UTC, e.g. `2026-10-05T00:00:00Z`; end at `T23:59:59Z` |
| `pmp_deal_type` | `createDeal` | string | always `"3"` (within Open Auction: an Exchange Package, XP, deal) |
| `status` | `createDeal`, `updateDeal` | string | exactly `"Paused"` or `"Active"`; omitted means Active |
| `distribution_channel_val` | `buildPackageTargeting` | string | comma-delimited ids, e.g. `APP,WEB` |
| `viewability_score`, `vtr_score` | package targeting | string | option id, e.g. `"0.70"`, with `"op": ">="` |
| `iq_score` | package targeting | string | always `"30"`, with `"op": ">="` |

## Identifiers

| What a tool asks for | Pass |
|---|---|
| `account_id` | the `id` from `listAccountsForProduct(product="SELECT")` |
| `instance_uid` | the same row's `instance_uid`, on every call in the flow |
| `package_id` on a deal | the numeric id from `createPackage`, or an existing deal's package from `getDeal` |
| `demand_partner` in `deal_participants` | the `id` from `optionsByPath("deal.deal_participants.demand_partner")` |
| `buyer_ids` | seat ids. Each row of `optionsByPath("deal.deal_participants.buyer_ids", filter={"demand_partner_id": ...})` is a buyer whose seats are in `extra.third_party_buyer_id`; pass the seat the user means (ask when a buyer has several), never the row's `id`, which is OpenX's internal buyer id. A seat id the user gives (e.g. "99001") goes in as it is. If it isn't in that list, or the API answers "Seat … does not exist", the seat hasn't been mapped in OpenX yet: tell the user their OpenX account team can map it, and don't substitute another seat. |
| targeting values | the `id` values from the matching `optionsByPath` paths |
| the deal code users know | `deal_id` (`OX-...`) from `getDeal`, populated shortly after create |

## Option paths

| Path | Values seen (look them up each time) |
|---|---|
| `deal.package.targeting.rendering_context.ad_placement` | `BANNER`, `CTV`, `NATIVE`, `VIDEO` |
| `deal.package.targeting.rendering_context.distribution_channel` | `APP`, `WEB` |
| `...rendering_context.device_type.desktop_devices` | `desktop` |
| `...rendering_context.device_type.mobile_devices` | `phone`, `tablet` |
| `...rendering_context.device_type.tv_devices` | `tv` (Connected TV), `set-top-box` (Set Top Box) |
| `deal.package.targeting.viewability.viewability_score` | `0.10` to `0.95` (steps of 10 to 50%, then 5); each means "X% or greater" |
| `deal.package.targeting.vtr.vtr_score` | `0.10` to `0.90` in steps of 10 |
| `deal.deal_participants.demand_partner` | per instance; labels like "DV360 - RTB" |
| `deal.deal_participants.buyer_ids` | needs `filter={"demand_partner_id": ...}` |
| `deal.currency` | per instance |
| `deal.package.targeting.domain.categories_iab_v2` | about 700 rows; see [advanced-targeting.md](advanced-targeting.md) |
| `deal.deal_source` | only when OpenX asks for it |

There is no option path for `iq_score`, and it is not one of the `metacategory.excludes` options.

## Geo lookups

- Geo paths need a filter named after the path, e.g. `deal.package.targeting.geographic.city`
  with `filter: {"city": ...}`. Other geo paths (country, state, region, dma, msa, postal_code)
  work the same way.
- **Use a wildcard prefix.** `{"city": "zur"}` can return nothing; `{"city": "zur*"}` works. Use
  lowercase ASCII without diacritics ("zurich", not "Zürich").
- **Disambiguate by `extra.country` and `extra.state`.** The same city name often exists in several
  places ("springfield*"). Pick the one the user meant, and ask when it is unclear.
- Geo goes in the package under `geographic.includes`, as comma-delimited id strings.

## Error text and what to do

| Error contains | Cause | Fix |
|---|---|---|
| `Deal participants required` | no DSP, or `deal_participants=[]` | get a DSP; create the deal with the existing `package_id` |
| `Demand partner "DV360 - RTB" requires a single buyer.` | DV360 without exactly one buyer | ask for one buyer, or another DSP; reuse the saved package |
| `Field name value "<name>" is not unique (id of conflicting package: …)` | package name already used, often by a failed earlier attempt | inspect it; reuse if it is yours, else rename |
| `When 'ad_placement' is set as CTV, the 'distribution_channel' must be explicitly set to APP` | CTV with Web | CTV is App only; offer Video for web |
| `'Viewability' cannot be set when format is CTV.` | CTV with viewability | offer the alternatives in SKILL.md Step 1 |
| `'View Through Rate' cannot be set when format is CTV.` | CTV with VTR | offer the alternatives in SKILL.md Step 1 |
| `When 'device_type.tv_devices' is set, 'ad_placement' cannot be BANNER or NATIVE.` | Banner/Native on TV devices | drop TV devices or switch to Video |
| `is not IMPLEMENTED` on an options path | combined `device_type` path | use the three device paths |
| validation error asking for `deal_source` | login without an OpenXSelect account | look up `deal.deal_source`, ask the user, retry |
| `status must be "Active" or "Paused"` | another status value | pass exactly `"Paused"` |
| MCP timeout on `createPackage` / `createDeal` | outcome unknown | search by name before retrying; a retry after a success duplicates |
| empty result from `optionsByPath` | wrong path string or missing wildcard | copy the path exactly; add `*` to geo filters |
