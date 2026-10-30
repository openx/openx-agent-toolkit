---
name: openx-campaign-launch
description: Launch an OpenXDirect campaign end to end through the OpenX MCP tools - create the order, creative and line item, attach the creative, forecast, then activate - with the id, unit and lookup rules each step needs. Use when asked to create, set up, launch or test a campaign, order, line item or creative in OpenXDirect, or to run the campaign flow through the OpenX MCP.
metadata:
  author: openx
  version: 1.11.0
  title: Launch a campaign
license: "This Skill is provided by OpenX and is subject to change. It is provided “as is” for use with your OpenX account and is subject to the OpenXSelect Portal Terms of Service (https://select.openx.com/terms/). Actions taken using this Skill are made under your OpenX account and are your responsibility. Review all actions and outputs before relying on them."
---

# Launch an OpenXDirect campaign

The OpenX MCP exposes every campaign object as a tool, but the tools do not tell you the
order to call them in, which identifier each one wants, or what units a number is in. This skill
does. Follow the steps in order; each one names the tool and the values that matter.

Every mutation here creates or changes real objects in the account the caller is signed into.
Create everything **Paused**, and confirm with the user before Step 7 activates anything.

## Before you start

1. **Report the run** with `reportDiagnostics` before any other tool: pass
   `skill="openx-campaign-launch"`, `skill_version` as the `version` in this skill's frontmatter (the
   header line above when the server returned the skill), `model` as your own model id, and
   `context_window` in tokens if your harness tells you it. Every argument is optional, so send
   what you know and skip the rest. The call writes one analytics line and changes nothing in
   the account.
2. **Load this skill's tools.** Clients that search a connector's tools on demand may not have
   loaded every tool this skill calls. Before going on, make sure each of these is available in your
   session, and search the connector's tools by the exact name for any that is not:
   `activateCreative`, `activateLineItem`, `activateOrder`,
   `addLineItemCreatives`, `archiveCreative`, `archiveLineItem`, `archiveOrder`,
   `buildPackageTargeting`, `createCreative`, `createDeal`, `createLineItem`,
   `createOrder`, `createPackage`, `getDeal`, `getLineItem`,
   `getLineItemForecast`, `getOrder`, `getPackage`, `listAccountsForProduct`, `listOrders`,
   `optionsByPath`, `reportDiagnostics`, `searchOptionsByPath`, `updateDeal`,
   `updateLineItem`, `updateOrder`. A step that names a tool you cannot see means load it,
   never skip the step or substitute another tool.
3. **Use only the tools this skill names.** The connector also serves other tools
   with overlapping purposes, such as a second deal lookup. Their ids, fields and money units are
   not interchangeable with the ones here, so never mix the two in one flow.
4. **Choose the account, and with it the instance.** Call
   `listAccountsForProduct(product="DIRECT")`, with `name_contains` when the user named the
   account. Use the only row, or ask the user to pick when there are several. Pass that row's
   `id` as `account_id` and its `instance_uid` as `instance_uid` on every create below, and the
   same `instance_uid` on every other call in this flow, reads included. Everything you create
   lands in that account. An empty list means the caller is not set up for OpenXDirect: stop
   and tell the user to request it. If a create comes back refused, read the error rather than
   retrying: it distinguishes an instance you cannot reach from a permission the account lacks,
   and says which to ask for.
5. **Collect the inputs** before the first mutation, and ask for anything missing:
   - order name, flight start and end, total budget and whether it is a spend or impressions budget
   - line item name, ad format (`Banner` or `Video`), its budget, optional bidding strategy
   - the deal to buy on: its display code (`OX-...`), or the targeting to create one from
   - the creative: name, external id (`crid`), markup, and width and height for banners
   - whether to activate after a healthy forecast, or leave everything paused for review
6. **Know the units.** Money is micro-dollars (1 USD = 1,000,000). Order budgets are integers, line
   item budgets are strings. Dates are ISO 8601 timestamps. See
   [references/values.md](references/values.md) for the full table.

## Step 1: Deal (only when the user has no deal yet)

A line item buys inventory through a deal, and the deal's targeting comes from its package. Skip
this step when the user already has a deal display code.

1. **Look for an existing deal first**:
   `searchOptionsByPath(path="deal", filters=[{"name":"name","op":"_contains","val":["<name>"]}], limit=20, instance_uid)`.
   Always filter by name and keep `limit` small; an unfiltered deal search returns every deal in the
   account and overflows the tool result. A deal's format has to match the line item: a Banner line
   item needs a deal whose package targets the `BANNER` ad placement, a Video line item one that
   targets `VIDEO` or `CTV`. Read it from the deal's package with `getPackage(id)` before reusing
   a deal the user agrees to.
2. **Look up every enum id, never guess.** Use `optionsByPath` with these exact paths:
   - `deal.package.targeting.rendering_context.ad_placement`
   - `deal.package.targeting.rendering_context.distribution_channel`
   - `deal.package.targeting.rendering_context.device_type.desktop_devices`,
     `...device_type.mobile_devices`, `...device_type.tv_devices` (three separate paths; a combined
     `device_type` path is not implemented)
   - `deal.deal_participants.demand_partner`
   - `deal.currency`
3. **Build the targeting** with `buildPackageTargeting(ad_placement_val, distribution_channel_val,
   device_type_desktop | device_type_mobile | device_type_tv)`. At least one device type is required.
   - **CTV rule.** A `CTV` ad placement must have `distribution_channel` set to `APP`; the backend
     rejects any other value with `When 'ad_placement' is set as CTV, the 'distribution_channel'
     must be explicitly set to APP`. For a CTV package leave `distribution_channel_val` out (the
     tool fills in `APP`) or pass `APP`; never pass `WEB` or `APP,WEB`. Pair it with
     `device_type_tv`.
4. **Create the package** with `createPackage(name, targeting, account_id, instance_uid)`. One
   package serves every deal that shares its targeting, so for several deals create it once and
   pass the same id in item 5; never build an inline `package` per deal, and do not give each
   deal its own package so that they can be edited apart later. A shared package is the normal
   setup for deals created together, and a deal that later needs its own targeting can get a
   cloned package then. Make a separate package only when the targeting differs or the user says
   the deals must be editable independently.
5. **Create the deal** with `createDeal(name, currency, pmp_deal_type="3", start_date, end_date,
   package_id, deal_price=0.01, deal_participants=[{"demand_partner": "<id from step 2>"}],
   status="Paused", account_id, instance_uid)`.
   - `deal_price=0.01` is right here without asking: this deal exists only as the channel the
     line item buys through, and the line item's own bid decides what it pays. A higher deal floor
     would only sit between the line item and the inventory. Do not ask the user for a deal price
     in a campaign launch; the line item's budget and bid are the prices that matter.
   - Always pass `status="Paused"`. Without it the deal is created **Active** and biddable by its
     participants immediately. Activate it in Step 7 with `updateDeal(id, status="Active")`
     once the line item that buys on it is ready.
   - If the call times out, do **not** retry blindly. Run the search from item 1 on the deal name;
     if it is there, the create succeeded.
6. **Wait for the display code.** The `deal_id` (`OX-...`) is assigned asynchronously. Poll
   `getDeal(id)` until `deal_id` is populated; that value is what the line item needs, never the
   numeric `id`.

**Many deals at once** (a bulk sheet, a set of variants): create the package once, then one
`createDeal` per row with `package_id`, `status="Paused"` and only that row's own fields (name,
dates, price, participants). Before each create, search the account by deal name as in item 1 and
skip rows that already exist, so a rerun does not duplicate deals. An inline `package` on every row
repeats the whole targeting, block lists included, in every call and in the conversation, which is
what stops a long run partway.

## Step 2: Order

`createOrder(name, start_date, end_date, budget_total, budget_type, status="Paused", account_id, instance_uid)`

- `budget_type` is `"total_spend"` or `"total_impressions"`; `budget_total` is an **integer** in the
  matching unit (micro-dollars or an impression count).
- `start_date` is checked against the server clock in UTC. Put the start at least an hour ahead in
  UTC, or at noon on the next day, or the create fails with `Start date must not be in the past`.
- Do not pass `advertiser_id`; the owning account is the advertiser.
- Keep the returned numeric `id`. It is the only order identifier you need.

## Step 3: Creative

`createCreative(name, crid, ad_format, markup_type, markup_payload, status="Paused", width, height,
account_id, instance_uid)`

- `name` must be unique in the account; `crid` is the user's external id for the creative.
- `markup_type` is `"HTML"` for banners and `"VAST"` for video. Banners need `width` and `height`.
- `status` is required on create, unusually. Use `"Paused"`.

## Step 4: Line item

`createLineItem(name, bidder_order_uid, ad_format, start_date, end_date, budget_total, deal_id,
strategy_and_kpi_type, status="Paused", account_id, instance_uid)`

- `bidder_order_uid` takes the order's **numeric id** from Step 2. The server resolves it. Never try
  to derive a uid from an id.
- `deal_id` is the deal's **display code** (`OX-...`) from Step 1, not its numeric id, and the deal's
  format must match `ad_format` (see Step 1); a mismatch is rejected with
  `Deal format (Banner) does not match line item format (Video)`.
- `budget_total` is a **string** of micro-dollars (or impressions on an impressions order).
- Leave `target_type` and `target_value` out. The server derives the delivery cap from the parent
  order's budget type and this budget. Set them only when the user wants a different cap.
- `strategy_and_kpi_type`: `maximize_*` values need nothing else; `target_*` values also need
  `strategy_and_kpi_value` as string micro-dollars.
- Frequency capping entries are integers with a unit of `hour`, `day` or `week`, at most three:
  `[{"impressions_limit": 3, "time_period_unit": "day", "time_period_value": 1}]`.
- Check the response: `target_type` and `target_value` should be populated. If they are null, set
  both with `updateLineItem` before forecasting.

## Step 5: Attach the creative

`addLineItemCreatives(line_item_id, creative_ids=[<creative id>])`

Both objects must exist first; there is no creative argument on line item create. Repeat with more
ids to attach several creatives.

## Step 6: Forecast

`getLineItemForecast(line_item_id)`

- `viability` is `GREEN`, `YELLOW` or `RED`. Report it with `available_bid_requests`, the `cpm`
  band and every entry in `warnings`.
- `unforecasted_fields` lists what the forecaster ignored (frequency capping and day parting are
  always in it); mention them so the user does not read the forecast as covering them.
- On `RED`, stop and show the warnings; do not activate. On `YELLOW`, ask. Quote `meta.request_id`
  when reporting a forecast problem.

## Step 7: Activate (only after the user has seen what will go live and said yes)

Before asking, read the deal each line item buys on with `getDeal(id)`, including a deal the user
brought rather than one created in Step 1. If it isn't `Active` (for example `Paused`, `Publishing`
or ended), say so in what will go live: the order and line item would activate, but nothing
delivers until the deal is `Active`. Activating a deal you didn't create in Step 1 is a separate
change: name it and ask for it on its own, never as part of the launch.

Activate parents before children, in this order:

1. `updateDeal(id, status="Active")` if the deal was created in Step 1
2. `activateOrder(id)`
3. `activateCreative(id)` for each creative
4. `activateLineItem(id)`

Read back `getDeal(id)` after step 1. `Active` is the expected result. `Publishing` is
**not an error** and not a failed update: the deal's package audience is still exporting, and
the deal flips to `Active` on its own when it finishes. Do not re-send the update and do not
retry. Continue with steps 2-4 either way; the order, creatives and line item all activate
normally against a Publishing deal, but nothing delivers on it until it reaches `Active`.
Report the deal as `Publishing` in the final table, say it is not yet biddable, and let the
user choose whether to wait; if they want to wait, re-read `getDeal(id)` rather than
re-sending the update.

Then read back `getLineItem(id)`: `status` should be `Active` and `delivery_status`
`scheduled` (flight in the future) or `active`. Activating an order also unblocks any of its other
paused line items, so say so if the order was reused.

## Report

Finish with one table: object, id, status, and for the line item its deal display code, budget,
target type and value, and the forecast viability. Link the order, creative and line item to the
`url` their create call returned, so the user can open each one in OpenXDirect; the deal and
package have no link. If this was a test, offer to tear it down with
`archiveLineItem`, `archiveCreative`, `archiveOrder` (and the deal and package if
they were created here).

Keep tool names and field paths out of what the user reads: "order", "budget", "forecast: healthy", not `budget_total`, `target_value` or `viability`.

## When something fails

Match the error text against the table in [references/values.md](references/values.md) before
retrying. Most failures are an identifier of the wrong kind or a number in the wrong unit, and
retrying with the same input will fail the same way.

An error that starts with `Wrong instance` means the object lives on another instance: find its `instance_uid` with `searchOptionsByPath` (which searches every instance you can see) and retry the same call once with it. An error that starts with `Not retryable` is final: the account lacks a permission or a feature. Stop, tell the user what the message says to request, and do not retry or try other arguments.

If a write comes back saying **the change went through but OpenX's reply couldn't be read**, the
write succeeded and only the reply failed to parse. Look the object up by name with
`searchOptionsByPath` (path `bidder_order`, `bidder_lineitem` or `bidder_creative`) and continue
from it; calling the write again creates a duplicate.

## Legal notice

This Skill is provided by OpenX and is subject to change. It is provided “as is” for use with your OpenX account and is subject to the OpenXSelect Portal Terms of Service (https://select.openx.com/terms/). Actions taken using this Skill are made under your OpenX account and are your responsibility. Review all actions and outputs before relying on them.
