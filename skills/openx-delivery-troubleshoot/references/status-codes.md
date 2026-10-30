# Status vocabulary and what each value means for delivery

## `delivery_status` on line items and orders

| Value | Meaning | What to do |
|---|---|---|
| `draft` | Never activated; flight has not started | Activate when ready (`activateLineItem` / `activateOrder`) |
| `scheduled` | Active, start date in the future (UTC) | Nothing; check the date is the one intended |
| `active` | Delivering, no upstream blocker | If impressions are still zero, go to Steps 5 and 6 (deal format, forecast, bid price) |
| `stalled` | Within flight but blocked by a parent, deal or creative gate | Read `delivery_status_reason`; the table below names the step |
| `completed` | Flight ended; cannot resume | Extend `end_date` only if the user wants it to run again |
| `paused` | User paused it | `activateLineItem` / `activateOrder` |
| `archived` | Soft deleted | Nothing to deliver |

## `delivery_status_reason` on line items

| Reason | Meaning | Step | Fix |
|---|---|---|---|
| `missing_deal_id` | No deal on the line item | 2 | `updateLineItem(id, deal_id="OX-...")` |
| `missing_parent_order` | Parent order missing or unreadable | 4 | Check `bidder_order_uid`; the order may be archived |
| `parent_order_not_active` | Order is Paused | 4 | `activateOrder(id)` |
| `deal_not_found` | Deal does not exist or is archived | 5 | Point the line item at a live deal |
| `deal_not_active` | Deal is Paused or Publishing | 5 | `updateDeal(id, status="Active")`; Publishing resolves on its own |
| `deal_not_started` | Deal start date in the future (UTC) | 5 | Wait, or change the deal dates |
| `deal_ended` | Deal end date in the past (UTC) | 5 | Extend the deal, or pick another |
| `no_active_creative` | No Active creative attached | 3 | Attach or activate a creative |
| `flight_not_started` | Line item start date in the future (UTC) | 2 | Wait, or move the start date |
| `flight_ended` | Line item end date in the past (UTC) | 2 | Extend `end_date` |

A line item with no reason set, `delivery_status: active` and zero impressions is the case the
reason codes do not cover. Work Steps 2, 5 and 6: a null `target_type`, a deal of the wrong format,
or a max bid below the forecast CPM band are the usual answers.

## Format matching

| Line item `ad_format` | Deal package `ad_placement` |
|---|---|
| `Banner` | `BANNER` |
| `Video` | `VIDEO` or `CTV` |

Read the deal's format from `getDeal(id).package.targeting.rendering_context.ad_placement.val`
(`getPackage(id).targeting.rendering_context` carries the same for a package).

## Delivery counters

From `getLineItemDelivery`, `getOrderDelivery` and `getDealDelivery`, under
`delivery_metrics.counters`.
Windows end yesterday.

| Counter | What it counts |
|---|---|
| `requests_qualified` | Auctions the deal was offered that passed its targeting |
| `non_zero_bids` | Auctions the line item actually bid on |
| `fills` | Auctions the line item won |
| `impressions` | Won auctions that rendered |
| `spend` | USD spent on those impressions |
