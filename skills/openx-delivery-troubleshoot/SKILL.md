---
name: openx-delivery-troubleshoot
description: Diagnose why an OpenXDirect line item or campaign is not delivering, through the OpenX MCP. It only reads while it diagnoses, and applies a fix only when the user asks. Reads the delivery counters first (requests, bids, fills, impressions) to see where the funnel breaks, then walks a fixed checklist from the cheapest configuration causes to forecast and sibling comparison, and reports the first failing check and the fix. Use when asked why a line item, order or campaign is not delivering, not spending, not bidding, stalled, or shows Active but has no impressions.
metadata:
  author: openx
  version: 1.5.0
  title: Diagnose a line item
license: "This Skill is provided by OpenX and is subject to change. It is provided “as is” for use with your OpenX account and is subject to the OpenXSelect Portal Terms of Service (https://select.openx.com/terms/). Actions taken using this Skill are made under your OpenX account and are your responsibility. Review all actions and outputs before relying on them."
---

# Diagnose a line item that is not delivering

"Why isn't this campaign delivering?" almost always has a configuration answer, and the cheap checks
find it before any theory about targeting does. This skill reads the delivery counters to see where
the funnel breaks, then the line item, its creatives, its parent order and its deal in a fixed order,
and stops at the first check that fails. It only reads while it
diagnoses; the write tools in its list are for a fix the user asks for.

Do not change anything while diagnosing. Report the cause and the fix; run the fix only if the user
asks.

## Before you start

1. **Report the run** with `reportDiagnostics` before any other tool: pass
   `skill="openx-delivery-troubleshoot"`, `skill_version` as the `version` in this skill's frontmatter (the
   header line above when the server returned the skill), `model` as your own model id, and
   `context_window` in tokens if your harness tells you it. Every argument is optional, so send
   what you know and skip the rest. The call writes one analytics line and changes nothing in
   the account.
2. **Load this skill's tools.** Clients that search a connector's tools on demand may not have
   loaded every tool this skill calls. Before going on, make sure each of these is available in your
   session, and search the connector's tools by the exact name for any that is not:
   `activateCreative`, `activateLineItem`, `activateOrder`,
   `addLineItemCreatives`, `getDeal`, `getDealDelivery`, `getLineItem`,
   `getLineItemDelivery`, `getLineItemForecast`, `getOrder`,
   `getOrderDelivery`, `getPackage`, `listLineItemCreatives`,
   `listOrderLineItems`, `reportDiagnostics`, `searchOptionsByPath`,
   `updateDeal`, `updateLineItem`, `updateOrder`. A step that names a tool you cannot
   see means load it, never skip the step or substitute another tool.
3. **Use only the tools this skill names.** The connector also serves other tools
   with overlapping purposes; their ids and fields are not interchangeable with the ones here.
4. **Get the line item id.** If the user gives a name, find it with
   `searchOptionsByPath(path="bidder_lineitem", filters=[{"name":"name","op":"_contains","val":["<name>"]}], limit=20)`.
   If they give an order, list its line items with `listOrderLineItems(order_id)` and run the
   checklist on each one that should be delivering.
5. **Know the two status fields.** `status` is what the user asked for (Active or Paused).
   `delivery_status` is what the system is doing about it, and `delivery_status_reason` says why when
   it is not delivering. Report all three; a line item can be Active and still not delivering.
   [references/status-codes.md](references/status-codes.md) lists every value and what to do about it.

An error that starts with `Wrong instance` means the object lives on another instance: find its `instance_uid` with `searchOptionsByPath` (which searches every instance you can see) and retry the same call once with it. An error that starts with `Not retryable` is final: the account lacks a permission or a feature. Stop, tell the user what the message says to request, and do not retry or try other arguments. A `Not retryable (entitlement)` error means the account doesn't have OpenXDirect, and every tool this skill uses would refuse the same way, so end the skill there instead of moving on to the next step.

## Step 1: Is it bidding at all?

`getLineItemDelivery(id, range="LAST_7_DAYS")`

If this first read comes back `Not retryable (entitlement)`, stop here: the account doesn't have OpenXDirect, so every later step would be refused too. Tell the user what the message says to request.

The counters say where the funnel breaks before any configuration check does. They come from a daily
batch, so every window ends yesterday: a line item that started today has no data yet, and that is
not evidence of a problem.

The figures are this line item's own, even when sibling line items buy on the same deal (the
deal's own delivery is a separate read, Step 5).

Walk `counters` down the funnel, `requests_qualified`, `non_zero_bids`, `fills`, `impressions`,
and stop at the first zero:

| Pattern | Meaning | Where to look |
|---|---|---|
| `requests_qualified` 0 | The deal is not being offered any auctions: not active, not started, or its targeting matches nothing | Step 5, then Step 6 |
| requests, `non_zero_bids` 0 | Offered inventory and declining it: the line item is not bidding. Configuration | Steps 2 to 4 |
| bids, `fills` 0 | Bidding and losing every auction: price | Step 6, `max_bid_price` against the CPM band |
| fills, `impressions` 0 or far lower | Winning but not rendering: creative | Step 3 |
| all flowing, `delivery_pacing.vs_pace_pct` well below 0 | Delivering, just behind pace: budget, bid price or inventory, not a stalled line item | Step 6, report it as pacing |

`previous` holds the same counters for the window before this one; a funnel that was healthy and
then dropped to zero points at a recent change (Step 2's `modified_date`, a deal edit, a creative
paused). If the counters are healthy and the user still says "not delivering", they are probably
looking at today, which the counters never include; say so.

## Step 2: The line item itself

`getLineItem(id)`

Read these fields, in this order, and stop at the first problem:

- `delivery_status_reason` set: the server has already named the gate. Look it up in the reference
  table, confirm it with the matching step below, and report it. This is the fast path.
- `target_type` or `target_value` null: the line item has no delivery cap and **never bids**, while
  still showing `status: Active`. This is rare: the API sets the cap on every new line item, so
  it appears only where a caller cleared it. Fix: `updateLineItem(id, target_type="budget",
  target_value=<budget_total>)` (or `"impressions"` with an impression count on an impressions
  order).
- `status` Paused: the user paused it. Fix: `activateLineItem(id)`.
- `start_date` in the future or `end_date` in the past, **compared in UTC**, not the user's time
  zone. A line item that "starts today" may not have started yet on the server's clock.
- `deal_id` null: nothing to buy on. Fix: `updateLineItem(id, deal_id="<OX-... display code>")`.
- `budget_total` zero or `max_bid_price` set very low: note it now, it matters in Step 6.

## Step 3: Creatives

`listLineItemCreatives(line_item_id)`

There must be at least one attached creative with `status: Active` whose `ad_format` matches the
line item's. No creatives, only Paused ones, or only a Banner creative on a Video line item means
nothing else matters until this is fixed. Fix: `addLineItemCreatives(line_item_id,
creative_ids=[...])` for a missing attachment, `activateCreative(id)` for a paused one.

## Step 4: Parent order

`getOrder(id)` with the line item's `bidder_order_uid` (the numeric id works).

A paused or ended order stops every line item under it regardless of their own status. Check
`status`, `delivery_status`, `start_date`, `end_date` (UTC again) and whether `budget_total` is
plausible for the line items under it. `getOrderDelivery(id)` shows whether anything under the
order is being asked or bidding, and `delivery_pacing` whether the order has already spent its
budget. Fix: `activateOrder(id)` or `updateOrder`.

## Step 5: Deal

`getDeal(id)` with the `OX-...` display code the line item carries; the tool resolves the code
to the deal itself, so no search is needed first. A not-found error means no deal carries that
code; when the code is a character off, the error lists the codes that nearly match.

- `status` must be Active. Paused is a user choice; Publishing means the package audience is still
  exporting and the deal will flip to Active on its own. Fix for Paused: `updateDeal(id,
  status="Active")`.
- Deal `start_date` and `end_date` must cover today, in UTC.
- **Format must match.** A Banner line item needs a deal whose package targets ad placement
  `BANNER`; a Video line item needs `VIDEO` or `CTV`. Read it from the deal's
  `package.targeting.rendering_context.ad_placement.val`, which `getDeal` returns.
  Fix: point the line item at a deal of the right format.
- **Is the deal alive at all?** `getDealDelivery(id, range="LAST_7_DAYS")` with the `OX-...`
  code the line item carries gives the code's total across every deal behind it; with a numeric
  deal id it gives that one deal, which is how to tell which deal behind a shared code is the
  dead one (`getDeal` on a shared code refuses and names the candidate ids; use the one you
  mean). Use it when Step 1 showed a dead funnel: zero
  `requests_qualified` on the deal means the deal's targeting or status is the problem, not this
  line item; healthy deal counters with a dead line item point back at Steps 2 to 4.

## Step 6: Forecast

`getLineItemForecast(line_item_id)`

- `viability` RED means the deal's targeting plus the line item's settings leave no inventory to
  bid on; report the `warnings`. YELLOW is thin inventory.
- Compare the line item's `max_bid_price` with the forecast `cpm` band. A max bid below the band's
  lower bound means the line item bids but never wins.
- `unforecasted_fields` lists what the forecast ignored (frequency capping, day parting); a tight
  frequency cap or a narrow `daypart_schedule` can throttle a line item the forecast calls healthy.

## Step 7: Siblings

`listOrderLineItems(order_id)`

If sibling line items under the same order are delivering (`getLineItemDelivery` on one or
two of them), the problem is specific to this one and one of Steps 2 to 6 has it. If none of them
deliver, look at the order (Step 4) and the account: the order's budget may be exhausted, or the whole
account may be blocked upstream.

## Report

Finish with a short table, one row per step: check, what you read, pass or fail. Link the line
item and its order to the `url` that `getLineItem` and `getOrder` returned, so the user can open
them in OpenXDirect. Then state the
first failing check as the likely cause, in one sentence, and the fix in product terms.
Report `status`, `delivery_status` and `delivery_status_reason` together, and the funnel counters
with their window. If every step passes, say so plainly and hand the user the
counters, the forecast numbers and the bid price comparison as the remaining leads; do not invent a
targeting theory.

Keep tool names and field paths out of what the user reads: "paused", "no active creative", "bid below the forecast price range", not `activateLineItem` or `max_bid_price`.

## Legal notice

This Skill is provided by OpenX and is subject to change. It is provided “as is” for use with your OpenX account and is subject to the OpenXSelect Portal Terms of Service (https://select.openx.com/terms/). Actions taken using this Skill are made under your OpenX account and are your responsibility. Review all actions and outputs before relying on them.
