# What each kind of change writes

All money is micro-dollars (1 USD = 1,000,000) and every line item money field is a string:
$2.20 is `"2200000"`, $5,000 is `"5000000000"`. Round a computed value to a whole number of
micro-dollars before writing it.

| The user asks to | Tool and field | Rules |
|---|---|---|
| pause, hold, stop spend | `pauseLineItem(id)` | only an `Active` line item; one already `Paused` is skipped. `pauseOrder(id)` stops every line item under the order in one call and leaves their own statuses untouched |
| resume, unpause, restart | `activateLineItem(id)` | only a `Paused` line item; the parent order must be `Active` too, or nothing delivers (`activateOrder(id)`) |
| raise or lower the bid, the CPM, the max bid | `updateLineItem(id, max_bid_price="<micro-dollars>")` | $0.01 to $1,000.00 (10000 to 1000000000 micro-dollars); a percentage is applied to each row's own current value |
| raise or lower the budget | `updateLineItem(id, budget_total="<value>")`; the API sets `target_value` to the new budget unless the call sends `target_value`, and delivery stops a line item at `target_value`, whatever its budget, so let the cap follow the budget, and send a lower `target_value` only when the user wants the line item to stop short of its budget; never a higher one | same unit as the parent order; the Active line item budgets under an order cannot exceed the order's `budget_total`, so read the order first and say when they would |
| change the daily budget | `updateLineItem(id, budget_daily="<value>")` | same unit as the parent order |
| set or change the KPI target | `updateLineItem(id, strategy_and_kpi_type="target_cpm" (or `target_cpc`, `target_cpa`, `target_ctr`), strategy_and_kpi_value="<micro-dollars>")` | a `target_*` type needs a value; a `maximize_*` type (`maximize_clicks`, `maximize_impressions`, `maximize_conversions`) takes none, so switch to it with the type alone and the server clears the value |
| change the flight end | `updateLineItem(id, end_date="<ISO 8601 UTC>")` | the end date can move; do not move the start date of a line item that has already spent, since the spend before the new start drops out of the flight and pacing resets |
| change pacing | `updateLineItem(id, pacing_strategy="even" or "asap")` | |

`updateLineItem` changes only the fields it is given; a field left out keeps its value, and
sending a field as null keeps it too except for `strategy_and_kpi_value`, `max_bid_price` and
`daypart_schedule`, which null clears.

## Reading the current values

`searchOptionsByPath(path="bidder_lineitem", ...)` returns the current budgets, targets, KPI
type and value, pacing strategy, dates and statuses in each row's `extra`, so a pause, resume,
budget or KPI plan is built from the search without a read per row. It does not return
`max_bid_price`, `frequency_capping` or the daypart fields: a plan that changes one of those
reads `getLineItem(id)` per row first. The re-read after the write is `getLineItem(id)` as
well, which also carries `delivery_status` and `delivery_status_reason`.
