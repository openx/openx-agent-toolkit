---
name: openx-budget-reallocate
description: Move budget between the line items of one OpenXDirect order through the OpenX MCP tools. Reads every line item's budget, spend to date and pace, proposes a split that keeps the order's total (decreases first, never below what a line item has spent, only into line items whose forecast can absorb it), gets a yes, applies it one line item at a time, re-reads each one and reports per line item. Use when asked to move money or budget between line items, shift budget from underspending to capped line items, rebalance or reallocate an order's budget, or give one line item more at another's expense.
metadata:
  author: openx
  version: 1.2.0
  title: Reallocate budget
license: "This Skill is provided by OpenX and is subject to change. It is provided “as is” for use with your OpenX account and is subject to the OpenXSelect Portal Terms of Service (https://select.openx.com/terms/). Actions taken using this Skill are made under your OpenX account and are your responsibility. Review all actions and outputs before relying on them."
---

# Reallocate budget across an order's line items

"Two of these line items won't spend their budget by the end of the month and the other three
are capped. Move the money." The server has no reallocation operation: this is one budget change
per line item, and the API checks each change against the order. It refuses an Active line item
whose new budget would push the total of the order's Active line item budgets above the order's
budget, so the order's budget is the ceiling and the decreases have to land before the increases.
Nothing stops a budget being set below what the line item has already spent, and that stops the
line item on the spot, so the floor is on you. The user sees the whole split, with where every
number comes from, before anything moves.

## Before you start

1. **Report the run** with `reportDiagnostics` before any other tool: pass
   `skill="openx-budget-reallocate"`, `skill_version` as the `version` in this skill's frontmatter
   (the header line above when the server returned the skill), `model` as your own model id, and
   `context_window` in tokens if your harness tells you it. Every argument is optional, so send
   what you know and skip the rest. The call writes one analytics line and changes nothing in
   the account.
2. **Load this skill's tools.** Clients that search a connector's tools on demand may not have
   loaded every tool this skill calls. Before going on, make sure each of these is available in your
   session, and search the connector's tools by the exact name for any that is not:
   `getDeal`, `getLineItem`, `getLineItemForecast`, `getLineItemsDelivery`, `getOrder`,
   `getOrderDelivery`, `getPackageTargeting`, `getSkill`, `reportDiagnostics`,
   `searchOptionsByPath`, `updateLineItem`, `updateOrder`.
   A step that names a tool you cannot see means load it, never skip the step or substitute
   another tool.
3. **Use only the tools this skill names.** The connector also serves other tools
   with overlapping purposes; their ids, fields and money units are not interchangeable with the
   ones here, so never mix the two in one flow.
4. **Take the instance from the objects.** Every search result carries the line item's
   `instance_uid` in `extra`, and every call about the order or a line item, reads and writes
   alike, passes it. Line items under one order share the order's instance.
5. **Know the unit.** The order's `budget_type` sets the unit of every figure here: micro-dollars
   (1 USD = 1,000,000) for `total_spend`, an impression count for `total_impressions`. The order's
   `budget_total` is an integer in that unit, a line item's `budget_total` and `target_value` are
   strings in the same unit, and the pacing figures (`goal`, `delivered`, `expected`) come back in
   it too. Compute the split in that unit and show the user dollars and cents, or impression
   counts with thousands separators. [references/split.md](references/split.md) has the field
   table and the arithmetic.

## Step 1: Scope the order

A reallocation moves money inside one order. "Move the money" with no order named is a
question back to the user, never a guess across the account.

- **The order**: `getOrder(id)` when the user gave the id, otherwise
  `searchOptionsByPath(path="bidder_order", filters=[{"name":"name","op":"_contains","val":["<name>"]}], limit=20)`
  and take the numeric `id` and `instance_uid` from `extra`; ask if more than one matches. From
  the order keep `budget_total` (the ceiling), `budget_type` (the unit), `status`, `start_date`
  and `end_date`.
- **Its line items**:
  `searchOptionsByPath(path="bidder_lineitem", filters=[{"name":"bidder_order_id","op":"_eq","val":["<order id>"]}], limit=100, instance_uid="<the order's instance_uid>")`.
  Each row's `extra` carries `id`, `status`, `delivery_status`, `budget_total`, `budget_daily`,
  `target_type`, `target_value`, `pacing_strategy`, `start_date` and `end_date`; the row's own
  `name` is the line item's name. Page with `offset` while `has_next_page` is true.

Only Active line items count toward the order's ceiling, and only they can take budget without
being activated first. Paused, draft, completed and archived ones are listed for the user and
left out of the split unless the user names one; a paused line item that is reactivated later
brings its budget back into the sum, so say so if the user plans to.

## Step 2: Read spend and pace

`getLineItemsDelivery(ids=[...], range="LAST_7_DAYS", instance_uid=...)`, one call for up to
100 ids. Each row's `pacing` is the flight to date whatever the range: `delivered` is what the
line item has spent (or served) so far, `goal` is its budget, `expected` is where it should be,
`delivered_pct`, `flight_elapsed_pct` and `vs_pace_pct` say how it is doing. `metrics` is the
last seven days, for the recent run rate. The counters are a daily batch that ends yesterday, so
today's spend is not in them; a line item that started today has no data.

`getOrderDelivery(id)` gives the order's own pace.

Read each row in this order and stop at the first that applies:

1. `metrics` null: the id did not resolve; leave the row out and say so.
2. `pacing` present with `vs_pace_pct` null: the flight has not started (`flight_elapsed_pct` 0,
   `window` null), so there is no pace to judge yet. Leave it alone unless the user names it.
3. `pacing` null: no goal or flight bounds to pace against, the line item's own or its order's.
   Leave it alone unless the user names it.
4. Otherwise the row is a candidate. Carry `pacing` and the seven-day `spend` (or
   `impressions`) into Step 3.

The figures are each line item's own, even when sibling line items buy on the same deal, so a
row's seven-day spend can be sized from directly.

## Step 3: Size the split

Unless the user named the line items, pick them from the pace:

- **Givers** are the line items that will not spend their budget: `vs_pace_pct` below -25 with
  the flight well under way (`flight_elapsed_pct` above 25), or `flight_elapsed_pct` more than
  10 points above `delivered_pct` late in the flight. A `pacing_strategy` of `asap` runs ahead by
  design, so an `asap` line item behind pace is a stronger signal, not a weaker one.
- **Takers** are the capped ones: `delivered_pct` at or above 95 with flight left, or `vs_pace_pct`
  at +10 or more with a rising trend.

How much each gives and takes, and the two limits, are in
[references/split.md](references/split.md). The limits:

- **The ceiling.** The order's `budget_total`. The proposed Active line item budgets add up to at
  most that, which makes the move net-zero inside the order. Giving the takers more than the givers
  free up means raising the order with `updateOrder(id, budget_total=...)`, which is its own line
  in the plan and its own yes, never something folded in quietly.
- **The floor.** A giver keeps at least what it has delivered plus what it will deliver before the
  change lands: `pacing.delivered` plus one day at its seven-day daily rate. The API does not check
  this, and a budget under spend to date stops the line item immediately.

Before a taker gets money, forecast the money it would get, not the budget it has. A forecast
by `line_item_id` is built from the saved line item, its current budget over its whole flight,
past days included, so a capped taker that has spent most of its budget comes back `GREEN` at
that budget and the check says nothing about the extra. Forecast the proposal as a draft
instead:

1. `getLineItem(id, instance_uid=...)` for the taker's `end_date`, `target_type`,
   `max_bid_price`, `strategy_and_kpi_type`, `strategy_and_kpi_value`, `frequency_capping`,
   `daypart_schedule` and `deal_id`.
2. `getDeal(deal_id)` for `package.id`, then `getPackageTargeting(package.id, instance_uid=...)`
   for the package's `targeting` and `url_targeting`: the draft path does not load the stored
   targeting, so the forecast needs them passed in.
3. `getLineItemForecast(context_params={"start_date": <today, ISO 8601 UTC>, "end_date": <the
   taker's end_date>, "budget_total": "<proposed budget minus delivered so far>",
   "target_type": <the taker's, or "budget" when it has none>, "target_value": "<the same
   amount>", "max_bid_price": ..., "strategy_and_kpi_type": ..., "strategy_and_kpi_value": ...},
   package_targeting=<targeting>, url_targeting=<url_targeting>, instance_uid=...)`.

That asks the forecaster whether the inventory exists for the remaining money over the
remaining days. Read `meta.forecast_version` first: a version containing `stub` is placeholder
numbers, so the forecast cannot gate the taker; say so and let the user decide. Otherwise a
`viability` of `RED` means the inventory is not there and the money would move from one
underspender to another, so that taker drops out and the user hears why; `YELLOW` means ask;
quote the `warnings`. The forecaster ignores frequency capping and day parting (always in
`unforecasted_fields`), so say so when the taker has either. The call takes around ten seconds
per line item, so forecast only the takers, once each, and do not retry one that times out:
report the forecast as missing for that row and let the user decide.

Two fields move with a budget. Delivery ignores `budget_total`: a line item stops when
its spend reaches `target_value`, so the cap is what limits spend, and the API sets
`target_value` to the new `budget_total` on every budget write unless the call sends
`target_value`. So no row ends with a cap above its proposed budget: a giver's cap comes down
with its budget (let the API set it, or send a lower one), and a cap sent back explicitly is at
most the new budget. A taker whose cap is to stay below its new budget will not spend the extra,
which the plan says on its own line. Show the cap next to the budget for every row.
`budget_daily` must stay at or below `budget_total`, so a giver whose daily budget would end up
above its new total gets the daily lowered in the same call.

## Step 4: Show the plan and get a yes

One table, one row per line item in the order, Active ones first: line item, id, status, current
budget, delivered so far, pace (`delivered_pct` against `flight_elapsed_pct`, and `vs_pace_pct`),
proposed budget, delta, and for a taker its forecast viability. Then a totals line: current sum
of Active budgets, proposed sum, the order's budget, and any amount left unassigned. Then the
sentence that names the move ("move $4,000 from line items 12 and 15 to 17 and 19 under order
5678, order total unchanged") and ask whether to go ahead. Wait for the yes.

The request itself is not the yes, even when it names exactly what to move, unless the user has
said to go ahead without checking. A split the user changes gets shown again, with the limits
re-checked, before it is applied.

## Step 5: Apply, decreases first

Every change is one `updateLineItem(id, budget_total="<new>", instance_uid=...)`, with
`target_value` in the same call only when the plan keeps a cap below the new budget, and
`budget_daily` when Step 3 said it has to come down.

1. If the plan raises the order, `updateOrder(id, budget_total=<new>, instance_uid=...)` first.
2. Then every decrease, one line item at a time.
3. Then every increase, one line item at a time.

The order matters because the API checks an increase against the other Active line items'
current budgets: an increase sent before the decreases have landed is refused with
"Total active line item budgets (N) would exceed order budget (M)", even though the plan as a
whole fits.

A failed decrease holds back the increases it was paying for: apply the other decreases, then
only the increases the landed decreases cover, and report the rest as not applied. A failed
increase leaves its money unassigned; say so, since the order's Active budgets then add up to
less than before. Never retry a failed row with different numbers to make it go through, and
stop the run on an error that starts with `Not retryable`.

## Step 6: Re-read and report

`getLineItem(id, instance_uid=...)` for every line item that was written, and `getOrder(id)`
if the order was raised. The read is the proof: the new `budget_total` (and `target_value`,
`budget_daily` when they moved), `status` unchanged, `delivery_status` as before.

## Report

One table, one row per line item in the plan: line item, id, budget before and after, delivered
so far, result (`done`, `failed: <reason>`, `held: <the decrease that failed>`), and the
forecast viability for takers. Link each line item to the `url` its `getLineItem` read or its
`getLineItemsDelivery` row carries, so the user can open it in OpenXDirect. Then one line with
the totals: the Active line item budgets
before and after against the order's budget, and any money left unassigned. A plan with any
failed or held row is reported as partly applied, never as done, with what the user still has
to decide. A line item that received budget starts spending it within about fifteen
minutes.

Keep tool names and field paths out of what the user reads: "budget", "spent so far", "behind
pace", not `budget_total` or `vs_pace_pct`.

## When something fails

An error that starts with `Wrong instance` means the object lives on another instance: find its `instance_uid` with `searchOptionsByPath` (which searches every instance you can see) and retry the same call once with it. An error that starts with `Not retryable` is final: the account lacks a permission or a feature. Stop, tell the user what the message says to request, and do not retry or try other arguments. A `Not retryable (entitlement)` error on the first read means the account does not have OpenXDirect, and every tool this skill uses would refuse the same way, so end the skill there.

`Total active line item budgets (N) would exceed order budget (M)` on an increase means a
decrease has not landed or the ceiling is lower than the plan assumed: re-read the order and
the Active line items with Step 1 and Step 2 and show the user the corrected totals; never raise
the order to make the plan fit without its own yes. `Daily budget cannot exceed total budget`
means `budget_daily` has to come down with the total: resend the row with both. A client-side
`ValidationError` about the **response** means the write most likely went through; the re-read in
Step 6 settles it, so do not send it again.

For a taker whose forecast is `RED`, or a giver that is behind for a reason the pace does not
explain, hand over to the delivery troubleshoot with `getSkill(name="openx-delivery-troubleshoot")`
rather than moving money around the problem.

## Legal notice

This Skill is provided by OpenX and is subject to change. It is provided “as is” for use with your OpenX account and is subject to the OpenXSelect Portal Terms of Service (https://select.openx.com/terms/). Actions taken using this Skill are made under your OpenX account and are your responsibility. Review all actions and outputs before relying on them.
