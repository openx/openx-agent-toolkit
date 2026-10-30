# Sizing a split

## Where each number comes from

| Figure | Source | Unit |
|---|---|---|
| ceiling | `getOrder(id).budget_total` | the order's `budget_type`: micro-dollars for `total_spend`, impressions for `total_impressions` |
| a line item's budget | `extra.budget_total` on the search row, or `getLineItem(id).budget_total` | same as the order, as a string |
| delivered so far | `pacing.delivered` from `getLineItemsDelivery` (flight to date) | same |
| where it should be | `pacing.expected` | same |
| pace | `pacing.vs_pace_pct`, `pacing.delivered_pct`, `pacing.flight_elapsed_pct` | percentages |
| recent daily rate | `metrics.counters.spend` (or `impressions`) for `LAST_7_DAYS`, divided by the days in `metrics.window` | same as the order, per day |
| days left | the line item's `end_date` minus today, in UTC | days |
| forecast for the extra money | `getLineItemForecast(context_params=..., package_targeting=..., url_targeting=...)` with today as `start_date`, the taker's `end_date` and the proposed budget minus delivered as `budget_total`; targeting from `getPackageTargeting` on the deal's package: `viability`, `available_bid_requests`, `warnings`, `unforecasted_fields` | |

All money is micro-dollars (1 USD = 1,000,000): $4,000 is `4000000000`. A line item budget is
written as a string, the order budget as an integer.

## How much a giver gives

projected total = delivered so far + recent daily rate × days left

give = current budget − projected total, rounded down to whole dollars (or whole impressions),
and never more than current budget − floor, where

floor = delivered so far + one day at the recent daily rate

A giver with no seven-day delivery at all (zero spend) has a daily rate of
zero: its projected total is what it has delivered, and it can give everything above the floor.

## How much a taker takes

Takers share what the givers free up, in proportion to how far ahead of pace they are, capped
per taker by the forecast of its remaining money over its remaining days: a `RED` viability takes
nothing, and `available_bid_requests` against the taker's recent fill rate says roughly how much
more it can serve in the days left. A forecast by `line_item_id` covers the current budget over
the whole flight and says nothing about the extra, so it is not the check. When the
givers free up more than the takers can absorb, the rest stays unassigned and the plan says so;
when they free up less than the user wants to move, the plan shows raising the order as its own
line.

## The checks before the plan is shown

- proposed Active line item budgets add up to at most the order's `budget_total` (or the raised
  one the plan proposes)
- every giver's proposed budget is at or above its floor
- every giver's `budget_daily`, where set, is at or below its proposed `budget_total`
- every row's cap (`target_value`) is at or below its proposed budget: delivery stops a line
  item at `target_value`, whatever its `budget_total`, and the API sets `target_value` to the new
  budget unless the call sends it, so a cap is sent back only when it is to stay below the budget

## Example

Order 5678, `total_spend`, budget $20,000, four Active line items, 20 days into a 30-day flight.

| line item | budget | delivered | pace | reading |
|---|---|---|---|---|
| 12 | $5,000 | $1,400 | -58% | giver: at $70/day it ends near $2,100 |
| 15 | $5,000 | $2,000 | -40% | giver: at $100/day it ends near $3,000 |
| 17 | $5,000 | $4,900 | +47% | taker: capped, forecast GREEN |
| 19 | $5,000 | $4,600 | +38% | taker: near cap, forecast GREEN |

Expected at day 20 is $3,333 for each, which gives the pace column. Line item 12 projects to
$1,400 + $70 × 10 = $2,100 and gives $2,900; line item 15 projects to $2,000 + $100 × 10 =
$3,000 and gives $2,000. Floors $1,470 and $2,100 are respected. The $4,900 goes $2,700 to 17
and $2,200 to 19, in proportion to how far ahead each is. Proposed budgets $2,100 / $3,000 /
$7,700 / $7,200, total $20,000, order unchanged. Applied as: 12 down, 15 down, then 17 up, 19 up.
