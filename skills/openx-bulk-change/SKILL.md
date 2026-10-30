---
name: openx-bulk-change
description: Pause, resume or change many OpenXDirect line items at once through the OpenX MCP tools, one object at a time, safely. Scopes the set to one named order or a filter the user confirmed, shows every affected line item with its current spend before the first write, applies the change line item by line item, re-reads each one and reports per object what succeeded and what did not. Use when asked to pause everything under an order or campaign, hold or stop spend, resume or unpause a campaign, raise or lower the budget, bid or CPM on several line items, or make the same change across a set of line items.
metadata:
  author: openx
  version: 1.3.0
  title: Change line items in bulk
license: "This Skill is provided by OpenX and is subject to change. It is provided “as is” for use with your OpenX account and is subject to the OpenXSelect Portal Terms of Service (https://select.openx.com/terms/). Actions taken using this Skill are made under your OpenX account and are your responsibility. Review all actions and outputs before relying on them."
---

# Change many line items at once

The server has no batch operation: a change across an order is one call per line item, and
nothing rolls back when a call in the middle fails. This skill is the safe way to do it:
settle exactly which line items are in the set, show the set with its spend and get a yes,
write one object at a time, re-read each one, and report per object what happened. It
changes live delivery, so the user sees every change before it is made.

## Before you start

1. **Report the run** with `reportDiagnostics` before any other tool: pass
   `skill="openx-bulk-change"`, `skill_version` as the `version` in this skill's frontmatter (the
   header line above when the server returned the skill), `model` as your own model id, and
   `context_window` in tokens if your harness tells you it. Every argument is optional, so send
   what you know and skip the rest. The call writes one analytics line and changes nothing in
   the account.
2. **Load this skill's tools.** Clients that search a connector's tools on demand may not have
   loaded every tool this skill calls. Before going on, make sure each of these is available in your
   session, and search the connector's tools by the exact name for any that is not:
   `activateLineItem`, `activateOrder`, `getLineItem`, `getLineItemsDelivery`, `getOrder`,
   `getSkill`, `listAccountsForProduct`, `pauseLineItem`, `pauseOrder`, `reportDiagnostics`,
   `searchOptionsByPath`, `updateLineItem`. A step that names a tool you cannot see means load
   it, never skip the step or substitute another tool.
3. **Use only the tools this skill names.** The connector also serves other tools
   with overlapping purposes; their ids, fields and money units are not interchangeable with the
   ones here, so never mix the two in one flow.
4. **Take the instance from the objects.** There is no account to choose: every search result
   carries the line item's `instance_uid` in `extra`, and every call about that line item, reads
   and writes alike, passes it. Line items under one order share the order's instance.
5. **Know the units.** Money is micro-dollars (1 USD = 1,000,000): `budget_total`,
   `budget_daily` and `target_value` on a line item are strings in the parent order's unit
   (micro-dollars for a `total_spend` order, impression counts for a `total_impressions` one);
   `max_bid_price` and `strategy_and_kpi_value` are strings in micro-dollars. Spend in the
   delivery counters is integer micro-dollars. Compute every change in those units and show the
   user dollars. See [references/changes.md](references/changes.md) for the field each kind of
   change writes.

If the request is about one line item only, this skill is more ceremony than the job needs:
read it, show the change, confirm and write, in the same shape as Step 4 and Step 5 here.

## Step 1: Scope the set

A bulk change applies to a named set, never to "everything" by default.

- **An order by name or id**: `getOrder(id)` when the user gave the id, otherwise
  `searchOptionsByPath(path="bidder_order", filters=[{"name":"name","op":"_contains","val":["<name>"]}], limit=20)`
  and take the numeric `id` and `instance_uid` from `extra`. Ask if more than one matches.
- **The order's line items**:
  `searchOptionsByPath(path="bidder_lineitem", filters=[{"name":"bidder_order_id","op":"_eq","val":["<order id>"]}], limit=100, instance_uid="<the order's instance_uid>")`.
  Each result's `extra` carries `id`, `status`, `delivery_status`, `budget_total`,
  `budget_daily`, `target_type`, `target_value`, `strategy_and_kpi_type`,
  `strategy_and_kpi_value`, `pacing_strategy`, `start_date`, `end_date` and `deal_id`, and the
  row's own `name` is the line item's name. `max_bid_price` is not in the search result: for a
  bid change, read `getLineItem(id, instance_uid)` for each row before building the plan. Page
  with `offset` while `has_next_page` is true.
- **A filter inside the order** ("the underperforming ones", "the video line items", "the ones
  still active"): list the whole order first, then narrow it by the field the user named, or by
  the delivery figures from Step 2 when the user named performance. Say which rows the filter
  kept and which it dropped; the user may disagree with the cut.
- **"Pause everything", "hold all spend", "stop the campaign"** with no order named: do not
  resolve it to the whole account. Ask which order or campaign, and offer the active orders by
  name from `searchOptionsByPath(path="bidder_order", filters=[{"name":"status","op":"_eq","val":["Active"]}], limit=20)`
  when it helps. An account-wide change is only a bulk change once the user has named every
  order it covers.

Drop from the set what the change cannot apply to, and say so: a pause skips line items that
are already Paused, completed or archived; a resume skips the ones already Active; a budget
or bid change skips archived ones. A line item whose own `status` is fine but whose
`delivery_status` is `stalled`, `completed` or `scheduled` can still be changed, and the
report should name its delivery status so the user is not surprised that pausing it changed
nothing on the ground.

## Step 2: Read the spend

`getLineItemsDelivery(ids=[...], range="LAST_7_DAYS")`, one call for up to 100 ids, gives each
line item's `metrics` (spend, impressions, clicks for the window) and `pacing` (`delivered` and
`expected` for the flight to date). Use `range="YESTERDAY"` when the user asked about today's
pace of spend; the counters are a daily batch that ends yesterday, so nothing from today is in
them. A row with both `metrics` and `pacing` null is an id the API did not recognise, not a line
item with no delivery.

This is the figure the user weighs the change against: pausing a line item that spent $0
yesterday changes nothing, pausing one that spends $2,000 a day is the decision. Carry it into
the plan in Step 3.

## Step 3: Show the plan and get a yes

Before the first write, show one table: line item, id, current status, spend for the window,
the current value of every field the change touches, and the value it will become. Then the
sentence that names the set and the change ("pause these 12 line items under order 5678", "raise
`max_bid_price` by 10% on these 4") and ask whether to go ahead. Wait for the yes.

The request itself is not the yes, even when it names exactly what to change, unless the user
has said to go ahead without checking. One yes covers the whole set it was given; a set the user
then trims or widens gets shown again.

Two things to put in front of the user with the plan:

- **Pausing the order is one call.** `pauseOrder(id)` stops delivery of every line item under
  it at once and leaves each line item's own status untouched, so `activateOrder(id)` later
  brings the same ones back exactly as they were. Pausing 40 line items is 40 calls, and resuming
  them later means knowing which ones were Active before. When the user said "pause the order",
  "hold the campaign" or "stop everything under it", offer the order pause as the first option and
  the per-line-item pause as the alternative for when some line items must keep running. When the
  user named a subset, the per-line-item pause is the only one that fits.
- **A percentage change is computed per row.** "Raise the CPM 10%" means each line item's own
  `max_bid_price` times 1.1, rounded to a whole number of micro-dollars, written back as a string;
  the table shows the old and new value of each row in dollars so the user sees the spread, not one
  number. A budget increase is capped by the parent order's `budget_total`: read `getOrder(id)` and
  say when the new line item budgets together exceed it.

## Step 4: Apply, one line item at a time

For each row of the plan, in the order shown, one call with the row's `id` and `instance_uid`:

- pause: `pauseLineItem(id, instance_uid)`
- resume: `activateLineItem(id, instance_uid)`
- change a field: `updateLineItem(id, <field>=<new value>, instance_uid)` with only the fields
  that change. A field left out keeps its value, with one exception in
  [references/changes.md](references/changes.md): a budget change sets `target_value` to the new
  budget unless the call sends `target_value` too, and delivery stops at `target_value`, not at
  the budget, so a cap is never sent back above the new budget. A `maximize_*` KPI leaves
  `strategy_and_kpi_value` out.
- pause the order instead: `pauseOrder(id, instance_uid)`, one call, then Step 5 reads the
  order rather than each line item.

Keep going when one call fails: note the error against that row and move to the next. Stop
only when the error says the whole set would fail the same way, which is an error starting
with `Not retryable` (the account lacks a permission or a feature) or a `Wrong instance` error
on the first call (fix the `instance_uid` for the set and start again). Never retry a failed
row with different arguments to make it go through; the report says what failed and why, and
the user decides.

## Step 5: Re-read and report

`getLineItem(id, instance_uid)` for each line item that was written, and `getOrder(id)` after an
order pause. The read, not the write's reply, is the proof: `status` is what the pause or resume
set, `delivery_status` says whether delivery actually stopped or resumed, and the changed field
carries the new value. The API sets `delivery_status` on the save itself, so a paused line
item reads `paused` (or `draft` before its flight) straight away.

A pause or a change takes effect within about fifteen minutes, so a paused line item can keep
delivering for a few minutes after its status flips. Tell the user to expect spend for that long after a pause.

## Report

One table, one row per line item in the set: line item, id, what was asked, result (`done`,
`failed: <reason>`, `skipped: <reason>`), status before and after, and for a field change its
old and new value in dollars. Link each line item to the `url` its `getLineItem` read or its
`getLineItemsDelivery` row carries, so the user can open it in OpenXDirect. Then one line with
the count: how many done, how many failed,
how many skipped. A set with any failed row is reported as partly applied, never as done, and
the line says which rows the user still has to deal with and where the account stands now. If
the order was paused instead, the table has one row for the order and the line items are
listed under it with their unchanged statuses. After a pause, one line that spend can still show
for up to about fifteen minutes before the change takes effect.

Keep tool names and field paths out of what the user reads: "paused", "bid raised from $2.00 to
$2.20", "budget", not `pauseLineItem` or `max_bid_price`.

## When something fails

An error that starts with `Wrong instance` means the object lives on another instance: find its `instance_uid` with `searchOptionsByPath` (which searches every instance you can see) and retry the same call once with it. An error that starts with `Not retryable` is final: the account lacks a permission or a feature. Stop, tell the user what the message says to request, and do not retry or try other arguments. A `Not retryable (entitlement)` error on the first read means the account does not have OpenXDirect, and every tool this skill uses would refuse the same way, so end the skill there.

`Only Active ... can be paused` or `Only Paused ... can be activated` on one row means the row
was already in the target state: mark it `skipped`, not `failed`. A rejected value on
`updateLineItem` (a budget above the order's, a KPI value sent with a `maximize_*` type, a bid
outside $0.01 to $1,000.00) is a `failed` row with the message quoted; the table in
[references/changes.md](references/changes.md) says what the field takes. A client-side
`ValidationError` about the **response** means the write most likely went through: the re-read
in Step 5 settles it, so do not send the write again.

For a line item that is not delivering after the change, hand over to the delivery
troubleshoot with `getSkill(name="openx-delivery-troubleshoot")` rather than guessing at the cause
here.

## Legal notice

This Skill is provided by OpenX and is subject to change. It is provided “as is” for use with your OpenX account and is subject to the OpenXSelect Portal Terms of Service (https://select.openx.com/terms/). Actions taken using this Skill are made under your OpenX account and are your responsibility. Review all actions and outputs before relying on them.
