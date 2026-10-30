# Values, units and recovery

## Units and formats

| Field | Tool | Type | Unit |
|---|---|---|---|
| `budget_total`, `budget_daily` | `createOrder`, `updateOrder` | integer | micro-dollars when `budget_type` is `total_spend`; impressions when `total_impressions` |
| `budget_total`, `budget_daily` | `createLineItem`, `updateLineItem` | string | same unit as the parent order |
| `target_value` | line item tools | string | same unit as `target_type` (`budget` = micro-dollars, `impressions` = count) |
| `strategy_and_kpi_value`, `max_bid_price` | line item tools | string | micro-dollars |
| `deal_price` | `createDeal` | number | dollars per mille (CPM) |
| `frequency_capping[].impressions_limit`, `time_period_value` | order and line item tools | integer | counts; `time_period_unit` is `hour`, `day` or `week`; at most three rules |
| `start_date`, `end_date` | all | string | ISO 8601 timestamp, e.g. `2026-10-01T00:00:00` |

1 USD = 1,000,000 micro-dollars. $100 is `100000000`; $2,000 is `2000000000`.

## Identifiers

| What a tool asks for | Pass |
|---|---|
| `bidder_order_uid` | the order's numeric `id` from `createOrder` / `getOrder` / `listOrders` |
| `deal_id` on a line item | the deal's display code (`OX-...`) from `getDeal`, populated shortly after create |
| `creative_ids` | numeric creative ids from `createCreative` |
| `package_id` on a deal | the numeric package id from `createPackage` |
| `demand_partner` in `deal_participants` | the `id` from `optionsByPath(path="deal.deal_participants.demand_partner")` |
| `ad_placement_val`, `distribution_channel_val`, device type values | the `id` values from the matching `optionsByPath` paths |

The order's uid is readable when something genuinely needs it:
`searchOptionsByPath(path="bidder_order", filters=[{"name":"name","op":"_eq","val":["<order name>"]}])`
returns it in `extra.uid`. Do not reconstruct it from the numeric id.

## Enum values seen in production

Look them up each time with `optionsByPath`; these are what the lookups returned, for
orientation only.

| Path | Values |
|---|---|
| `...rendering_context.ad_placement` | `BANNER`, `CTV`, `NATIVE`, `VIDEO` |
| `...rendering_context.distribution_channel` | `APP`, `WEB` |
| `...device_type.desktop_devices` | `desktop` |
| `...device_type.mobile_devices` | `phone`, `tablet` |
| `...device_type.tv_devices` | `tv`, `set-top-box` |

A CTV package compiles to `ad_placement == "VIDEO"` in its targeting expression; that is expected.

A CTV package must use `distribution_channel` = `APP`; `buildPackageTargeting` defaults to it when
`distribution_channel_val` is omitted for a `CTV` ad placement.

## Error text and what to do

| Error contains | Cause | Fix |
|---|---|---|
| `This feature is not enabled for your account` or `unauthorized` / `invalid_token` | expired session or an account without OpenXDirect | ask the user to reconnect the MCP; if it persists, the account needs the feature enabled |
| `must be of type int` on `budget_total` | order budget sent as a float or string | send an integer in micro-dollars (or impressions) |
| `target_type must be "budget" or "impressions"` | line item has no delivery cap, or a bad explicit value | `updateLineItem(id, target_type="budget" or "impressions", target_value=<budget>)` |
| deal reference rejected on line item create | numeric deal id passed as `deal_id` | pass the `OX-...` display code; poll `getDeal` until it is populated |
| `is not IMPLEMENTED` on an options path | combined `device_type` path | use the three `desktop_devices` / `mobile_devices` / `tv_devices` paths |
| `Only Paused ... can be activated` | object already Active | skip it and continue with the next activation |
| `status must be "Active" or "Paused"` on deal create | another value passed as `status` | pass exactly `"Paused"` (recommended) or `"Active"` |
| MCP timeout on `createDeal` | slow create, outcome unknown | search the deal by name before retrying; a retry after a success makes a duplicate |
| empty `result` from `optionsByPath` | wrong path string | copy a path from the list in this file exactly |
| `Start date must not be in the past` | start compared with the server clock in UTC | move the start at least an hour ahead in UTC, or to noon on the next day |
| `When 'ad_placement' is set as CTV, the 'distribution_channel' must be explicitly set to APP` | a CTV package was built with `WEB` or a mixed distribution channel | rebuild the targeting with `distribution_channel_val="APP"` (or omit it and let `buildPackageTargeting` default it) |
| `Deal format (Banner) does not match line item format (Video)` | the deal's package ad placement does not match `ad_format` | pick a deal whose package targets `BANNER` for a Banner line item, `VIDEO` or `CTV` for a Video one |
| "The change went through, but this server couldn't read OpenX's reply …" after a create or attach | the write went through; only the reply failed to parse | look the object up by name with `searchOptionsByPath` and continue; do not call the write again |
| `result ... exceeds maximum allowed tokens` | unfiltered entity search | add a name filter and a `limit` of 20 or less |
