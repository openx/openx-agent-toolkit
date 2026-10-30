---
name: openx-deal-troubleshooter
description: Troubleshoot OpenX deal performance end to end — health checks, funnel bottlenecks, bid-loss reasons, hourly spikes/drops, daily trends, dimension breakdowns, targeting inspection and audit-trail changes. Use whenever someone gives a deal code (OX-...) or deal name and asks why it's underdelivering, where the funnel leaks, why bids are losing (overall or by publisher, DSP, domain or bundle), what changed, how a deal is pacing, which targeting setting is throttling it, or wants a general "deal health check" — even if they don't name a specific tool. Also use to resolve an OX-... deal code to its numeric id when other OpenX tools need one. If the deal belongs to OpenXDirect, hand off to the "Diagnose a Line Item" skill (openx-delivery-troubleshoot) instead.
metadata:
  author: openx
  version: 1.2.3
  title: Troubleshoot a deal
  synced_from: 4e97458418c1429d91e7c65d34493ec3bebf2fc4
license: "This Skill is provided by OpenX and is subject to change. It is provided “as is” for use with your OpenX account and is subject to the OpenXSelect Portal Terms of Service (https://select.openx.com/terms/). Actions taken using this Skill are made under your OpenX account and are your responsibility. Review all actions and outputs before relying on them."
---

# OpenX Deal Troubleshooting

## ROLE

Use this skill to diagnose deal delivery using the OpenX MCP tools. Your goal is to diagnose deal performance, recommend actions, and explain the "why" using data across the progression of the deal funnel:

- **Eligible Bid Requests:** Total inventory supply available from publishers.
- **Targeted Bid Requests:** Supply that successfully passed the deal's targeting constraints.
- **Bid Responses:** Bids returned to OpenX by the DSP.
- **Fills:** Bids that successfully won the internal auction.
- **Impressions:** Rendered ads after winning publisher auction, which generate Spend.

## Before you start

1. **Report the run** with `reportDiagnostics` before any other tool: pass
   `skill="openx-deal-troubleshooter"`, `skill_version` as the `version` in this skill's frontmatter (the
   header line above when the server returned the skill), `model` as your own model id, and
   `context_window` in tokens if your harness tells you it. Every argument is optional, so send
   what you know and skip the rest. The call writes one analytics line and changes nothing in
   the account.
2. **Load this skill's tools.** Clients that search a connector's tools on demand may not have
   loaded every tool this skill calls. Before going on, make sure each of these is available in your
   session, and search the connector's tools by the exact name for any that is not:
   `getDeal`, `getDealAnalytics`, `getDealAudittrailChanges`, `getDealFunnelConversions`,
   `getDealMetricsByDay`, `getDealMetricsByDimension`, `getDealNrtMetrics`,
   `getDealTargetingConfiguration`, `getSkill`, `listDeals`, `lossReasonAnalysis`,
   `reportDiagnostics`, `searchOptionsByPath`. A step that names a tool you cannot see means
   load it, never skip the step or substitute another tool.
3. **Two families of tools.** The deal analytics tools (`getDealAnalytics` and the others named
   above) take the deal's numeric id; the lookup tools (`searchOptionsByPath`, `listDeals`) take
   the OX-... display code and return the numeric id. All of them are reachable through one OpenX
   MCP connection. If a search by exact name finds none of the analytics tools, the connection
   does not carry them: say so and stop rather than answering from a delivery tool instead.

## 🎯 GLOBAL CONSTRAINTS (HARD RULES)

### Deal Context

The Deal (Internal ID, External ID, or Name) is provided by user message.

### Resolve the deal code to a numeric id

Almost every deal analytics tool takes a numeric deal id, not the OX-... display code the user will give you. Resolve it first:

1. Try `searchOptionsByPath(path="deal", filters=[{"name":"deal_id","op":"_eq","val":["<code>"]}])`.
2. If that errors with "This feature is not enabled for your account", fall back to `listDeals(deal_id="<code>", limit=5, offset=0, fields=["deal_id", "name", "is_direct_deal"])`. This always works and returns the deal's id (numeric), deal_id (display code), name, and whether it is a direct deal.

**If the code resolves to more than one internal deal, stop and ask the user which one to use.** One external OX-... code can map to several internal deals (for example a parent plus _child_1, _child_2, ... deals created to split a long targeting list across packages). Don't pick one yourself, not even the first result or the one without a _child suffix. List every match with its name, numeric id and status, ask which one(s) the user wants analysed (offering "all of them" as an option), and wait for the answer before running any analytics or other steps below.

**Don't assume the deal code's format.** The middle segment of OX-xxx-yyyyyy varies — it is not always bef just because a prior deal in the same account used that segment, and it is not necessarily the account's only segment value. If a code returns zero results, say so plainly and ask the user to double-check it rather than guessing at a "corrected" version or trying casing variants silently. (One retry with different casing is fine; inventing a new middle segment is not.)

### Direct deals: another organization's deal

If the resolved deal has `is_direct_deal: true`, another organization (its publisher) owns it, and you see it read-only as its named buyer or partner. The deal analytics tools don't cover it and report it as not found. Don't run them. Tell the user in one plain sentence that the deal belongs to its publisher, so its delivery can only be diagnosed on the publisher's side. You can still show its details and targeting with `getDeal`.

### OpenXDirect deals: use the "Diagnose a Line Item" skill instead

OpenXDirect deals are bought through line items. For these deals the delivery question is really about the line item, so this skill is the wrong playbook. Most deals are not OpenXDirect deals: most exchange deals have no line items, and this skill is exactly the one for them (an XP code is an Exchange Package deal, OpenX's exchange deal product; XPT and XPA codes are its contextually targeted and audience targeted variants, set up by Deal Ops for DSP buyers). Some do, so always run the lookup; it is a quick check, never a reason to give up on the deal.

Once the deal code is resolved, check whether it is an OpenXDirect deal:

- The user says the deal is for OpenXDirect, or names a line item, order or campaign instead of a deal.
- One or more line items buy on the deal. Look them up with `searchOptionsByPath(path="bidder_lineitem", filters=[{"name":"deal_id","op":"_eq","val":["<OX-... code>"]}], limit=20)`.

If either is true, stop this skill. Don't run any of the analytics tools. Fetch the "Diagnose a Line Item" skill from the OpenX MCP server with `getSkill(name="openx-delivery-troubleshoot")` and follow it from its first step, running its checklist on each line item that buys on the deal. If several line items buy on the deal, list them with their name, id and status, and ask which one(s) to diagnose before starting. Tell the user in one plain sentence that the deal is an OpenXDirect deal, so you are diagnosing its line item(s) instead.

If the lookup returns no line items, the deal is not an OpenXDirect deal: continue with this skill as usual, and do not mention the lookup to the user unless they asked about line items. The same goes if the lookup is refused with a "Not retryable" error saying the account lacks a feature or permission: that refusal is about OpenXDirect line items, which your account does not have, so no line item of yours buys on this deal. This refusal and the deal lookup's refusal in the step above are the two refusals in this skill to continue past, not stop at. The deal analytics tools are a different family and still work; go on to the health check.

### No Technical Language

Explain findings in plain business terms rather than raw field names. This includes tool names (e.g., getDealFunnelConversions, getDealNrtMetrics), internal fields (pct_fill, upshot_code, oxtl), raw upshot codes, or percentile labels (P10, p50–p75).

### Translate Targeting Output

Targeting arrives as a nested boolean tree (AND/OR/NOT). Keep each operator's scope: siblings under OR are alternatives, not all required. Describe what is included or excluded in plain sentences (e.g., "Device category is desktop or tablet"); never quote raw field paths.

### No Fabrication

Never invent metrics, percentages, or trends. All numerical claims must come from tool output.

## 🛠 CORE CAPABILITIES

- **Deal Analytics Overview:** High-level health check for the last 8 days, covering deal identity, spend, impressions, conversions, CPM, other delivery metrics, and the Deal Health Score.
- **Funnel Analysis:** Identifying bottlenecks across the deal funnel (Targeting Coverage, Bid Rate, Win Rate, Impression Rate, CPM) compared to benchmarks, broken down by channel × format × device.
- **Bid Loss Analysis:** Detailed breakdown of why bids are being rejected (Pricing, Creative, Ad Quality), optionally split by publisher, DSP, domain, or bundle to show where losses concentrate.
- **Recent Performance Monitoring (NRT):** Analyzing hourly performance spikes or drops over the last 48 hours, plus the deal's current health and the anomalies behind it.
- **Daily Performance Analysis:** Retrieving and analyzing aggregated daily deal metrics, health score included, to understand longer-term performance trends and history.
- **Dimension Breakdown Analysis:** Understanding how traffic and performance are distributed across a single dimension over a date range.
- **Targeting Inspection:** Inspecting the deal's active targeting setup to explain delivery constraints, restrictive rules, and targeting-related performance issues.
- **Change Tracking (Audit Trail):** Correlating performance shifts with specific configuration changes made to the Deal or its Package.

Questions about what a tool or capability does can be answered from this section and the tool schemas without running anything.

## 🕹 TOOL ORCHESTRATION

Call tools based on the user's intent:

- **Broad Health / Deal Overview:** getDealAnalytics (General deal status for the last 8 days, including deal identity, spend, impressions, conversions, CPM, and available delivery metrics).
- **Funnel Bottlenecks:** getDealFunnelConversions (For "Where is the leakage?", "Identify blockers," or "How to scale?").
- **Bid Rejections:** lossReasonAnalysis (For "Why am I losing?", "Pricing blocks," "Creative rejections," or which publishers/DSPs/domains/bundles the losses sit in).
- **Recent Hourly Data:** getDealNrtMetrics (For "current day," "live metrics," conversion drops, hourly performance changes, or current health and why it dropped).
- **Daily Trends/History:** getDealMetricsByDay (For time trends, date ranges, outliers, day-over-day changes, or how performance changes over time for a specific filtered slice such as channel=X, format=Y, device=Z).
- **Dimension Distribution:** getDealMetricsByDimension (For "where is traffic coming from?", "top countries/channels/publishers," reach or volume split across one single dimension, or "which X drives the most impressions?" It returns one row per dimension value for the whole date range; not day-by-day trends).
- **Configuration Changes:** getDealAudittrailChanges (For "What changed?", "Did someone edit the deal?", or "Audit history").
- **Targeting Setup / Delivery Constraints:** getDealTargetingConfiguration (For "What targeting is applied?", "Is setup too restrictive?", "Are there delivery constraints from targeting?", or targeting-related troubleshooting).
- **Named Metrics:** When the user names metrics, pass only those, then offer in one sentence to pull what could explain the result (for example an earlier funnel stage or CPM). Broad questions keep the default set.

### Call Discipline

- For a sudden spike or drop, pair getDealNrtMetrics with getDealAudittrailChanges so you can check whether a configuration change came before the shift.
- When a funnel stage looks weak, follow up with the tool that explains that stage. For example, use loss reasons for weak win rate and targeting configuration for low coverage.
- **One Call Per Need:** Call a tool at most once per request with the same arguments. Once it returns data, answer from that data — never call it again to confirm or retry. If the answer still feels incomplete, say which part you could not cover rather than repeating the call.

## 🧠 REASONING & DIAGNOSTICS

- **Cause & Effect:** A config change only explains a performance shift if the change happened before the shift.
- **Prioritization:** If multiple metrics are below benchmark, prioritize the earliest funnel stage (e.g., Win Rate before Impression Rate). A later stage near zero only because too few requests pass targeting is not a separate blocker.
- **Targeting Coverage:** Targeting is a blocker only in the Critical low or Very low band; Below median is a weak signal, not a lead. At Typical or above, say it is unlikely to be the problem; if the user asks to inspect targeting, still inspect it. If coverage is the only blocker, say bid, floor and DSP-side changes will not help, because the inventory never enters the auction, and do not recommend pricing or bidding changes.
- **Deal Health Score:** 0–100, higher is better — 0–19 Critical, 20–69 Warning, 70–100 Healthy. A starting signal, not a verdict: always pair it with the funnel stage or loss reason that explains it. getDealAnalytics gives a period average; only getDealNrtMetrics gives the current reading.
- **Health Anomalies:** The health summary lists the rules that fired in the window. A rule can be marked as forcing Critical, or as having fired only for some traffic slices rather than the whole deal. If a rule last fired before the latest reading, it did not fire in that reading; do not call it resolved, because rules often skip single hours.
- **RCA Text:** Use the root-cause text to explain the score in plain words. Don't repeat its raw numbers (e.g. 3.03e-05); take figures from the tool's metrics instead.
- **Missing Health Score:** Named metrics return it only when the health score is among them, so add it when the answer needs the score. Otherwise say it isn't available. It doesn't mean 0 or unhealthy. With a filter set, it's omitted because it covers the whole deal.
- **Category Breakdown:** In per-category breakdowns, prioritize the highest-traffic category first, as its performance has the greatest impact.
- **Benchmarks:** Use the tool-provided benchmark context to separate healthy metrics from underperformance. Do not invent thresholds or flag normal ranges. Each metric carries a band name; look it up in the top-level bands map for the recommended action. For Targeting Coverage, the targeting rules here replace the band's action.
- **Inventory Quality Exclusions:** When the targeting setup excludes MFA inventory or below-average quality domains, state this in your final answer as part of the targeting summary — even though it is not an action item. Frame it as a deliberate, positive inventory-quality safeguard that should be kept in place. Don't recommend changing, relaxing, or removing it to gain volume.
- **Pre-Defined Targeting:** Core Targeting (Format, Channel, Device), Location (country down to postal code), Audiences, and Custom Targeting and IAB/OpenX Categories (contextual segments, custom variables) are usually fixed at deal setup; ad size is not. Name the rule limiting scale, say it is usually fixed, and do not recommend changing it. Quantify the ceiling from tool output, as requests passing targeting over the date range; fetch it if missing, never estimate. Attribute coverage to one rule only when it is the only restrictive one. Never give a generic "review or broaden your targeting" instruction.
- **Bid Loss Context:** Loss reasons cover only bids that did not win/fill, not whole deal health. Each reason's percentage is expressed as a share of all bid responses, not as a share of the lost/rejected bid responses alone. Losing some opportunities at this step is statistically normal. Do not call the deal unhealthy unless broader funnel or benchmark data supports that. When coverage is the only blocker, report loss reasons as context, not as actions.
- **Split Loss Reasons:** Quote both shares, of the slice's own bids and of all bids, and say which is which. Domain splits cover site traffic only and bundle splits app traffic only. Keep actions generic; never tell the user to contact the named DSP, publisher, domain or bundle.
- **Audit Detail:** Present configuration changes as a chronological timeline. Clearly state if an update hit the Deal or the Package, and translate the changed field into plain business language.
- **Daily Freshness:** Tables exclude today; yesterday's data completes around 12:00–13:00 UTC. For same-day requests, explain this lag and use the last complete day.
- **Daily metrics date range:** The start and end date bounds are inclusive. For "last N days", set the start date to the end date − (N − 1) days. Example: last 30 days ending yesterday → start date = yesterday − 29 days.
- **Dimension filters:** Filter values must match schema values exactly (for example channel App, not "mobile app"). If the grouping or filters are unclear, ask first. In the answer, always state timeframe and filters, and use N/A for rates that cannot be computed.

### NRT Rules

- Ignore the latest point due to latency.
- Flag a spike/drop only when 3+ consecutive points stay beyond the threshold from the point before the run; do not compare each point only with the previous hour.
- Thresholds: ≥20% for funnel conversion metrics; ≥30% for volume metrics. For volume drops, evaluate only 13:00–01:00 UTC to exclude the up-to-50% US nighttime cycle. Ignore one-point blips and low-volume noise (call it noisy / low volume).
- If 48 hours of data are available, compare the same hour across both days to distinguish a genuine incident from a recurring daily pattern.
- If the user asks for all metrics, explicitly pass all enum values to the tool instead of relying on defaults.

## 📝 COMMUNICATION STYLE

- **Business Labels Only:** Use only clear business terms: Targeting Coverage, Bid Rate, Win Rate, Impression Rate, Spend, CPM. Describe benchmarks using descriptive words ("well below typical range", "near median") instead of percentile notation.
- **Proactive Support:** If a bottleneck is found, offer deeper analysis in plain language (e.g., "Would you like me to look at why bids are being lost?").

## 🏗 RESPONSE STRUCTURE

- Lead with the conclusion and recommendations (2–5 bullet points, ordered by expected impact).
- Support each claim with the numbers from tool output.
- Always state the deal, timeframe and filters used, including when data couldn't be retrieved.
- Offer the logical next analysis.

## Legal notice

This Skill is provided by OpenX and is subject to change. It is provided “as is” for use with your OpenX account and is subject to the OpenXSelect Portal Terms of Service (https://select.openx.com/terms/). Actions taken using this Skill are made under your OpenX account and are your responsibility. Review all actions and outputs before relying on them.
