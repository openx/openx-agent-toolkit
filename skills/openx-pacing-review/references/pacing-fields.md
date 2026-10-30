# Pacing and delivery fields

From `getLineItemsDelivery` (rows of `metrics` and `pacing`), `getLineItemDelivery` and
`getOrderDelivery` (`delivery_metrics` and `delivery_pacing`).

## `delivery_pacing`

Always the flight to date, whatever range was requested.

| Field | Meaning |
|---|---|
| `goal_type` | `total_spend` or `total_impressions`: the unit every other pacing figure is in |
| `goal` | The target: micro-dollars for `total_spend`, an impression count for `total_impressions` |
| `delivered` | Delivered so far, in the same unit |
| `expected` | `goal` scaled by the elapsed fraction of the flight; may be fractional |
| `flight_elapsed_pct` | How much of the flight has passed, 0 to 100 |
| `delivered_pct` | `delivered` as a percentage of `goal`; above 100 when over-delivering |
| `vs_pace_pct` | Percentage ahead of (positive) or behind (negative) `expected`; null before the flight starts |
| `window` | The flight-to-date dates the figures cover; null until a day of the flight has completed |

`delivery_pacing` is null when the line item has no goal or flight bounds to pace against. Before the
flight starts it is present with zero progress: `flight_elapsed_pct` 0, `vs_pace_pct` null, `window`
null.

## `delivery_metrics`

| Field | Meaning |
|---|---|
| `range`, `window` | The requested range and the dates it resolved to; windows end yesterday |
| `counters` | The funnel for the window: `requests_qualified`, `non_zero_bids`, `fills`, `impressions`, `clicks`, `spend`, video and viewability counts |
| `previous`, `previous_window` | The same counters for the window immediately before |
| `cpm`, `ctr`, `cpc`, `win_rate`, `bid_rate`, `viewability`, `vcr` | Derived rates; null when the denominator is zero, and null is not zero |
| `last_updated` | Latest report day included, `YYYY-MM-DD`; null when there is no data |

`spend`, `cpm` and `cpc` are integer micro-dollars (1 USD = 1,000,000). Divide before reporting.

## Whose figures these are

Every figure is the entity's own: delivery is keyed by the line item, order or creative itself, so
two line items buying on one deal each read their own delivery and an order reads its own, not a
sum over its children's deals. There is no shared-deal caveat to apply.

## Ranges

| `range` | Window |
|---|---|
| `YESTERDAY` | The most recent complete day |
| `LAST_7_DAYS` | The seven complete days ending yesterday (the default for "this week") |
| `LAST_30_DAYS` | The thirty complete days ending yesterday |
| `FULL_FLIGHT` | The entity's own flight to date |

## Flags

| `vs_pace_pct` | Flag |
|---|---|
| +10 or more | ahead; goal reached when `delivered_pct` is 100 or more |
| -10 to +10 | on pace |
| -25 to -10 | behind |
| below -25 | well behind |

Trend: this window's `impressions` (or `spend` on a `total_spend` goal) against `previous`; flat
within about 15%, otherwise rising or falling. Run-out risk: `flight_elapsed_pct` above 80 with
`delivered_pct` more than 10 points below it.

## Search shapes for Step 1

```
searchOptionsByPath(path="bidder_order", filters=[{"name":"name","op":"_contains","val":["<name>"]}], limit=20)
searchOptionsByPath(path="bidder_lineitem", filters=[{"name":"bidder_order_id","op":"_eq","val":["<order id>"]}], limit=100)
searchOptionsByPath(path="bidder_lineitem", filters=[{"name":"status","op":"_eq","val":["Active"]}], sort="-modified_date", limit=100, offset=0)
```

Each `bidder_lineitem` result's `extra` carries `id`, `status`, `delivery_status`,
`delivery_status_reason`, `target_type`, `target_value`, `budget_total`, `pacing_strategy`,
`start_date`, `end_date`, `deal_id` and `bidder_order_id`.
