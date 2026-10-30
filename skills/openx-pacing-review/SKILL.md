---
name: openx-pacing-review
description: Review delivery pacing across the line items of an OpenXDirect order or account through the read tools of the OpenX MCP. Scopes the set, pulls delivery and pacing for all of it in bulk, and produces one table with a flag per line item (on pace, behind, well behind, ahead, not started) plus the order's own pace, with the unit caveats that make the numbers honest. Use when asked which line items are underspending, behind or ahead of pace, how a campaign or order is pacing this week, or for a pacing or delivery check across an order.
metadata:
  author: openx
  version: 1.7.0
  title: Review pacing
license: "This Skill is provided by OpenX and is subject to change. It is provided “as is” for use with your OpenX account and is subject to the OpenXSelect Portal Terms of Service (https://select.openx.com/terms/). Actions taken using this Skill are made under your OpenX account and are your responsibility. Review all actions and outputs before relying on them."
---

# Review pacing across an order's line items

"Which line items are behind this week?" is a daily question for traders and ad ops, and the answer
is a table, not a theory. This skill scopes the set, reads delivery and pacing for all of it in one or
two calls, and classifies every line item against the server's own pace figures. Every tool it uses
is read-only.

It classifies, it does not diagnose. A row that is well behind pace hands off to the
`openx-delivery-troubleshoot` skill (`getSkill("openx-delivery-troubleshoot")`); do not start
theorising about targeting from a pacing table.

## Before you start

1. **Report the run** with `reportDiagnostics` before any other tool: pass
   `skill="openx-pacing-review"`, `skill_version` as the `version` in this skill's frontmatter (the
   header line above when the server returned the skill), `model` as your own model id, and
   `context_window` in tokens if your harness tells you it. Every argument is optional, so send
   what you know and skip the rest. The call writes one analytics line and changes nothing in
   the account.
2. **Load this skill's tools.** Clients that search a connector's tools on demand may not have
   loaded every tool this skill calls. Before going on, make sure each of these is available in your
   session, and search the connector's tools by the exact name for any that is not:
   `getDealDelivery`, `getLineItemDelivery`, `getLineItemsDelivery`,
   `getOrderDelivery`, `getSkill`, `listAccountsForProduct`, `listOrderLineItems`,
   `reportDiagnostics`, `searchOptionsByPath`. A step that names a tool you cannot see means load it, never skip
   the step or substitute another tool.
3. **Use only the tools this skill names.** The connector also serves other tools
   with overlapping purposes; their ids and fields are not interchangeable with the ones here.
4. **Know what pacing measures.** `delivery_pacing` compares what a line item has delivered over its
   flight to date with what it should have delivered by now: `goal` scaled by the fraction of the
   flight that has elapsed is `expected`, and `vs_pace_pct` is how far `delivered` sits above or
   below that, as a percentage. It always covers the flight to date, whatever `range` you pass; the
   range only sets the window for the counters. Use the server's figures as they are and never
   recompute them. [references/pacing-fields.md](references/pacing-fields.md) lists every field.
5. **Know the units.** `goal_type` says what the goal is counted in: `total_spend` means `goal`,
   `delivered` and `expected` are micro-dollars (1 USD = 1,000,000), `total_impressions` means they
   are impression counts. `spend`, `cpm` and `cpc` in the counters are always micro-dollars. Divide
   before a human sees a figure.
6. **Know the calendar.** The counters are a daily batch, ready around 10:00 UTC, so every window
   ends yesterday and `last_updated` names the latest day included. Today's activity is never in the
   numbers, a line item that started today has no data yet, and neither is a problem. "This week"
   means `range="LAST_7_DAYS"`.

An error that starts with `Wrong instance` means the object lives on another instance: find its `instance_uid` with `searchOptionsByPath` (which searches every instance you can see) and retry the same call once with it. An error that starts with `Not retryable` is final: the account lacks a permission or a feature. Stop, tell the user what the message says to request, and do not retry or try other arguments. A `Not retryable (entitlement)` error means the account doesn't have OpenXDirect, and every tool this skill uses would refuse the same way, so end the skill there instead of moving on to the next step.

## Step 1: Scope the set

Pacing is reviewed over a named set, never over "everything" by default.

If a read in this step comes back `Not retryable (entitlement)`, stop here: the account doesn't have OpenXDirect, so every later step would be refused too. Tell the user what the message says to request.

- **An order by name**:
  `searchOptionsByPath(path="bidder_order", filters=[{"name":"name","op":"_contains","val":["<name>"]}], limit=20)`
  and take the numeric `id` from `extra`. Ask if more than one matches.
- **An order's line items**:
  `searchOptionsByPath(path="bidder_lineitem", filters=[{"name":"bidder_order_id","op":"_eq","val":["<order id>"]}], limit=100)`.
  Each result's `extra` carries `id`, `status`, `delivery_status`, `delivery_status_reason`,
  `target_type`, `target_value`, `budget_total`, `pacing_strategy`, `start_date`, `end_date` and
  `deal_id`, which is everything the table needs besides the delivery figures.
  `listOrderLineItems(order_id, limit=100)` also works but returns fewer fields.
- **Across the account** ("all my active line items"): pick the account first with
  `listAccountsForProduct(product="DIRECT")` (use the only row, or ask), then
  `searchOptionsByPath(path="bidder_lineitem", filters=[{"name":"status","op":"_eq","val":["Active"]}, {"name":"account_id","op":"_eq","val":["<account id>"]}], sort="-modified_date", limit=100, instance_uid="<its instance_uid>")`,
  paging with `offset` while `has_next_page` is true. Without the account filter the search spans
  every account the caller can see, which for an OpenX administrator is all of them. Tell the user how many line items the review
  covers. Beyond a couple of hundred, ask them to narrow it to an order or an advertiser; each bulk
  delivery call takes a few seconds and a table that long is not read anyway.

Then split the set. Rows that should be delivering, `status` Active, `delivery_status` active and
the flight covering yesterday **in UTC**, go on to Step 2. Everything else, paused, scheduled,
completed, stalled or archived, is listed in the report under its status with
`delivery_status_reason` where set, and is not scored on pace: a paused line item is behind by
definition and scoring it hides the real answer.

## Step 2: Pull delivery for the whole set

`getLineItemsDelivery(ids=[...], range="LAST_7_DAYS")`

One call covers up to 100 line items and returns one row per id with `metrics` and `pacing`, shaped
exactly like the single-line-item tool's `delivery_metrics` and `delivery_pacing`. Page by 100 for
longer sets; duplicates collapse to one row. A row with both `metrics` and `pacing` null is an id
the API did not recognise, not a line item with no delivery.

Pick the range from the question: `YESTERDAY` for "yesterday", `LAST_7_DAYS` for "this week" and by
default, `LAST_30_DAYS` for a monthly view, `FULL_FLIGHT` for whole-flight totals. Pacing is the
same whichever you choose.

## Step 3: The order's own pace

`getOrderDelivery(order_id, range)` with the same range.

The order is the budget ceiling its line items share, and its pacing row goes at the top of the
report. One thing is worth a sentence when it happens:

- The line items' goals do not add up to the order's goal (compare the `target_value`s from Step 1
  with the order's `goal`). An order can read behind while every line item is on pace simply
  because they were not given enough of its budget between them.

## Step 4: Classify each row

For each Step 2 row, read the fields in this order and stop at the first that applies:

1. `metrics` null: **not found**. The id did not resolve; check it against Step 1.
2. `pacing` present with `vs_pace_pct` null: **not started**. Pace is undefined before the flight
   begins (`flight_elapsed_pct` is 0 and `window` is null).
3. `pacing` null: **no pace**. The API paces only with a goal and both flight bounds, the line
   item's own or its order's. Leave the pace columns blank.
4. Otherwise flag on `pacing.vs_pace_pct`, using these bands unless the user gives their own:

| `vs_pace_pct` | Flag |
|---|---|
| +10 or more | ahead (and **goal reached** when `delivered_pct` is 100 or more) |
| between -10 and +10 | on pace |
| between -25 and -10 | behind |
| below -25 | well behind |

Add two readings to every scored row:

- **Trend**: this window's `impressions` (or `spend` for a `total_spend` goal) against `previous`
  for the window before it. Flat within about 15% either way, otherwise rising or falling. A row on
  pace but falling fast is the one to watch.
- **Run-out risk**: `flight_elapsed_pct` above 80 with `delivered_pct` more than 10 points below it
  will not reach its goal on current form. Say so plainly.

Two notes from Step 1's payload. A `pacing_strategy` of `asap` is meant to run ahead of pace, so
"ahead" is by design there. `delivery_status_reason`, when set, already names why a row is not
delivering; carry it into the table rather than working it out again.

For a behind or well-behind row, one glance at the funnel says where to send the user:
`non_zero_bids` 0 with `requests_qualified` above 0 means it is not bidding, bids with `fills` 0
means it is losing auctions on price, fills with far fewer `impressions` points at the creative.
Name the pattern in the flag column and hand the row to `openx-delivery-troubleshoot`; do not diagnose
it here.

## Step 5: A closer look at one row

When the user asks about a single flagged line item, `getLineItemDelivery(id, range)` returns
the same figures plus `status`, `delivery_status` and `delivery_status_reason` on one object, and
`getDealDelivery(<display code or numeric deal id>, range)` shows whether the deal underneath is alive
at all; the code form sums every deal carrying the code.
Anything past that is the troubleshooting skill's job.

## Report

Lead with the window: the dates the counters cover and `last_updated`. Then the order's row: goal
with its unit, delivered, expected, delivered %, flight elapsed %, vs pace %.

Then the table, one row per scored line item: line item, `pacing_strategy`, goal with unit,
delivered, expected, delivered %, flight elapsed %, vs pace %, trend against the previous window,
flag. Link each line item to the `url` on its `getLineItemsDelivery` row, so the user can open it
in OpenXDirect. Percentages to one decimal, money in dollars and cents, impression counts with
thousands separators. Rows that were not scored follow under their status with the reason.

Close with one line per behind or well-behind row naming the funnel pattern and pointing at the
troubleshooting skill, and one line for any run-out risk. Do not project when a budget will run out
or invent a cause; the data says how far ahead or behind a line item is, and that is what to report.

Keep tool names and field paths out of what the user reads: "behind pace", "goal", "delivered so far", not `vs_pace_pct` or `delivery_pacing`.

## Legal notice

This Skill is provided by OpenX and is subject to change. It is provided “as is” for use with your OpenX account and is subject to the OpenXSelect Portal Terms of Service (https://select.openx.com/terms/). Actions taken using this Skill are made under your OpenX account and are your responsibility. Review all actions and outputs before relying on them.
