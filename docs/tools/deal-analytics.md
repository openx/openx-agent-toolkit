# OpenX MCP tools: deal analytics and lookups

Deal analytics and troubleshooting, plus lookups for ad units, sites, apps, audience options, contracts, creatives and packages. Each heading is the name a client calls through `https://api.openx.com/mcp`.

---

## Tools

### `getAdunitFormats` · adunit

**Title:** Get Adunit Formats  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Get adunit formats filtered by distribution channel, or site ID.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `distributionChannel` | `String` | No | Distribution channel (WEB, MOBILE, LINEARVIDEO, NATIVE) |
| `siteId` | `Long` | No | Site ID |
| `limit` | `Integer` | No | Maximum number of results to return |

---

### `getAdunitSpecs` · adunit

**Title:** Get Adunit Specs  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Get supported adunit specifications

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `distributionChannel` | `DistributionChannel` | Yes | Distribution channel (WEB, MOBILE, LINEARVIDEO, NATIVE) |

---

### `getAppCategory` · application

**Title:** Get AppCategory  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Get appcategory by ID

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | `long` | Yes | AppCategory ID |

---

### `searchAppCategories` · application

**Title:** Search appcategories  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Search appcategories by filter

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `filter` | `AppCategoryFilter` | No | Query filter |
| `orderBy` | `List<OrderBy<AppCategoryOrderByField>>` | No | Order by |
| `offset` | `Integer` | No | Offset |
| `limit` | `Integer` | No | Maximum number of results to return (1-100, default: 20) |

---

### `searchAppCategoriesWithCursor` · application

**Title:** Search appcategories by filter with cursor based pagination  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Search appcategories by filter with cursor based pagination

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `filter` | `AppCategoryFilter` | No | Query filter |
| `orderBy` | `List<OrderBy<AppCategoryOrderByField>>` | No | Order by |
| `first` | `Integer` | No | Maximum number of results to return (1-100, default: 20) |
| `after` | `String` | No | After cursor |

---

### `getAudienceSearchOptions` · audience

**Title:** Get Audience Search Options  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Return the options an audience search is constructed from, for the caller's account: regions, segment search modes, data partners, and the segment taxonomy (categories and sub-categories).

Use when:
- Before producing any part of an audience search: call this first. Region codes, search modes, data partner ids and category ids must come only from this result - never invent one, and never carry one over from an earlier conversation.
- Region, countries and segmentsSearchMode have been chosen: call it again with them to get the data partners for exactly that search. The taxonomy does not depend on them, so send includeTaxonomy=false unless subCategories are needed again, narrowed with categories.

Returns:
- regions[]: send regions[].code as the search's region, on every search, including for the United States. An absent region is interpreted as the US rather than as every region, so omitting it is never the right way to widen a search.
- searchModes[]: scoped to the caller's account - a mode absent from this list must not be sent. The entry without a value searches every kind of segment the account can see: send no segmentsSearchMode for it. When no entry lacks a value (internal users), a segmentsSearchMode from this list must always be sent.
- dataPartners[]: accounts that own segments the search can be filtered by, possibly OpenXSelect itself. Only send a data partner id if the user explicitly asks for segments from a specific partner. Outside the US the caller's own account is always listed, but the search accepts it only if it sells segments. Empty in OWN_ONLY mode. In OPENX_PROPRIETARY mode it lists only OpenXSelect, for display: the search takes no data partners in OPENX_PROPRIETARY or OWN_ONLY mode, so send none there. When no searchModes entry lacks a value (internal users), the no-mode list holds every account and is not usable: call again with the chosen mode.
- categories[] and subCategories[]: the OpenX segment taxonomy the search can be filtered by - not IAB. Besides topics it holds demographic and location-like categories such as Age, DMA and Congressional District; these select segments, not the places the search runs in, which come from listUserLocations. A sub-category's parentId links it to its parent category. Sub-category names can repeat under different categories and the search does not tie a sub-category to its parent, so send its parentId in categories too. A name equal to its id is omitted. Both lists are omitted when includeTaxonomy=false.
- Always send ids/codes, never names.

Examples:
- no arguments -> {"regions": [{"code": "US", "name": "United States"}, ...], "searchModes": [{"name": "All Segments", ...}, {"value": "MARKETPLACE", "name": "OpenXSelect Data Marketplace", ...}], "dataPartners": [{"id": "...", "name": "Acxiom"}, ...], "categories": [{"id": "Automotive"}, ...], "subCategories": [{"id": "Auto Parts", "parentId": "Automotive"}, ...]}
- region=EU, countries=["DE"], includeTaxonomy=false -> regions and searchModes, with dataPartners limited to those selling segments in Germany, plus the caller's own account; no categories or subCategories
- segmentsSearchMode=OWN_ONLY -> the same lists, with dataPartners empty

Notes:
- This result does not contain places. Once a region is chosen, call listUserLocations with it to get the states, metro areas or countries that can be searched inside it.
- Options are read from OXS-BE as the caller; a caller OXS-BE does not accept receives FORBIDDEN.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `region` | `RegionCode` | No | Region the search will run in, exactly as returned in regions[].code. Scopes dataPartners to that region. Default: US |
| `countries` | `List<String>` | No | Country codes the search will run in, exactly as returned by listUserLocations' countries[].code (ISO two-letter, uppercase). Used only with a non-US region, to further scope dataPartners. Default: no country scoping |
| `segmentsSearchMode` | `SegmentSearchMode` | No | Search mode the search will run in, exactly as returned in searchModes[].value. In the US it scopes dataPartners to that mode; in every region OWN_ONLY empties them and OPENX_PROPRIETARY narrows them to OpenXSelect, which the search does not accept as a data partner. Default: no mode, i.e. every kind of segment |
| `categories` | `List<String>` | No | Category ids, exactly as returned in categories[].id. Narrows subCategories to these categories. Default: sub-categories of every category |
| `includeTaxonomy` | `Boolean` | No | Whether to return categories and subCategories. They do not depend on region, countries or segmentsSearchMode, so send false on a repeated call that needs only dataPartners. Default: true |

---

### `listUserLocations` · audience

**Title:** List User Locations  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

List the places an audience search can be narrowed to inside one region: states, metro areas (DMAs) and congressional districts for the United States, countries for every other region.

Use when:
- The user has named a place (state, metro area, congressional district or country) to narrow an audience search by, and the exact value the search takes is needed.
Do not call it speculatively, and do not call it twice for the same region in one conversation - it is an expensive lookup.

Returns:
- US: states[], dmas[] and congressionalDistricts[] as values - each one IS the value the search takes. Copy them exactly as returned. countries[] is empty.
- Any other region: countries[] with code and name - send countries[].code, never countries[].name. The US lists are empty.
Never guess a place value: every value written into a search must appear verbatim in this result. When a place the user named is missing, say so rather than substituting the nearest match.

Examples:
- region=US -> {"region": "US", "states": ["Alabama", ...], "dmas": ["Chicago", ...], "congressionalDistricts": ["Alabama 1st Congressional District", ...], "countries": []}
- region=EU -> {"region": "EU", "states": [], "dmas": [], "congressionalDistricts": [], "countries": [{"code": "DE", "name": "Germany"}, ...]}

Notes:
- Locations are read from OXS-BE as the caller; a caller OXS-BE does not accept also receives FORBIDDEN.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `region` | `RegionCode` | Yes | Region code, exactly as returned in getAudienceSearchOptions' regions[].code |

---

### `getContractById` · contract

**Title:** Get Contract By ID  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Retrieves a single contract by its internal ID — the publisher's legal and onboarding details together with their Google publisher configuration.

Use when:
- Looking up a contract's legal name, website, or onboarding status.
- Inspecting a publisher's Google configuration (publisher ID, account type, network code).
- Retrieving the contact emails, domains, or linked opportunity IDs for a contract.

Returns:
- Identity — id, uid, accountUid, accountId, legalName, website.
- status — the contract onboarding status (e.g. PENDING, OPPORTUNITY_CREATED, INVENTORY_CREATED).
- Google configuration — googlePubId, googleAccountType (GAM or ADMOB), googleNetworkCode.
- Collections — emails, domains, opportunityIds.

Notes:
- Only contracts belonging to an account visible to the caller are returned; a contract that does not exist, is soft-deleted or is not visible results in a not-found error.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | `long` | Yes | Contract ID |

---

### `getCreativeInfo` · creativeinfo

**Title:** Get CreativeInfo  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Get creative info by ID

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | `long` | Yes | CreativeInfo ID |

---

### `getCreativeInfos` · creativeinfo

**Title:** Get CreativeInfos  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Search creative infos with optional filters. Returns creative info summary fields.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `filter` | `CreativeInfoFilterInput` | No | Filters to apply to creative info search. Supports filtering by id, uid, account_uid, name, adomain, creativeType, and crid. |
| `orderBy` | `List<OrderBy<CreativeInfoOrderByInput>>` | No | Order by fields with direction (ASC/DESC) |
| `offset` | `Integer` | No | Offset for pagination (default: 0) |
| `limit` | `Integer` | No | Maximum number of creative info to return (1-100, default: 20) |

---

### `getDealDetails` · deal

**Title:** Get Deal Details  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Retrieves full details for a single Deal by its numeric id.

Use when:
- The user references a deal by id and needs its configuration, status, pricing, or
  participant details.

Returns:
- Identity & audit metadata: id, uid, instanceUid, name, status, dealId, dealType,
  typeFull, pmpDealType, dealSource, notes, createdWith, createdDate, modifiedDate,
  revision, ver, deleted.
- Account/package linkage: accountId, accountUid, packageId, packageUid, monetizingId,
  monetizingUid, accountManager, accountExecutive.
- Pricing & inventory controls: dealPrice, currency, priceConfig, dealExclusionRate,
  useMarketFloor, applyExchangeFee, bidReuseDisabled, openAuctionAccess, fixedCpmEnabled,
  lifetimeImpressionGoal.
- Scheduling: startDate, endDate.
- Participants & targeting: dealParticipants, dealSupplements (brand/creative/content/
  language filters), frequencyCapping, expectedAdCategory, deliveryRegion,
  hasMultiplePublishers.
- RBO (Rules-Based Optimization) config: rboConfig.
- Third-party fee/revenue config (see Notes for ACL gating): thirdPartyFees,
  thirdPartyFeesConfig, thirdPartyRevenue, segmentPartnerPlatformShare,
  segmentPartnerRevenueMethod, curatedDealBuyerDiscountEnabled, isRebateDisabled.
- DV360/sync/visibility flags: dv360InventoryPackage, enableDv360InventoryPackage,
  pdpDoSync, pdpConfig, amazonDoSync, oldTtdSyncAllowed, synchronizedWith, isPubVisible,
  isOaa, trackingEnabled, trackingPartnerId.
- Salesforce linkage: brandSalesforceId, agencySalesforceId.

Notes:
- Requires the pmp.read permission; callers without it receive a FORBIDDEN error.
- thirdPartyFees and thirdPartyFeesConfig are omitted unless the caller is an OAA partner
   or OA internal and has third_party_fees.read.
 - thirdPartyRevenue is omitted unless the caller is an OAA partner or OA internal and has
   third_party_fees.platform_share.read.
- Only deals visible to the current session's accounts are considered.
- Returns NOT_FOUND when no visible, non-deleted deal matches the id.
- Deal search/listing is not currently supported by this tool.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | `Long` | Yes | Internal numeric Deal ID (not the external dealId) |

---

### `listBuyers` · deal

**Title:** List Buyers  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

List the buyers, and their seats, available for one demand partner under the given account.

Use when:
- The user names a buyer for a deal's demand partner and its seat ids are needed. Call it after listDemandPartners, once per demand partner on the deal. Pass search with the seat id, or part of one, the user gave: it matches seat ids only, never buyer names. With only a buyer name, list without search and match the names across the pages.
- A seat id, e.g. dealParticipants[].buyerIds returned by getDealDetails, needs its buyer's name.

Returns:
- items: [{id, name, seatIds}], one page of at most pageSize buyers (default and maximum 50), and nextCursor. With search, each buyer lists only its seats whose id matches.
- Seat ids, not buyer ids: dealParticipants[].buyerIds and mainBuyerId hold values from a buyer's seatIds, never its id. When a buyer has more than one seat and the user did not say which applies, ask rather than picking. mainBuyerId is used for The Trade Desk only, and is one of the seat ids also in buyerIds.
- nextCursor: an opaque cursor while more buyers match - pass it back as cursor, with the same accountUid, demandPartnerId and search, to get the next page. Never parse or build a cursor; a cursor from another search is rejected with BAD_REQUEST. A page may hold fewer than pageSize buyers, even none, while nextCursor is set: keep paging until it is null. nextCursor is null on the last page: only then is a buyer absent from the search.
An empty result does not always mean the demand partner has no buyers: the list is account- and permission-scoped. Report it to the user rather than proceeding without buyers. Never guess or construct a seat id.

Examples:
- accountUid=<uid>, demandPartnerId=<id>, search="9900" -> {"items": [{"id": "<buyer id>", "name": "Acme Media", "seatIds": ["99001", "99002"]}], "nextCursor": null}
- accountUid=<uid>, demandPartnerId=<id> -> {"items": [... 50 buyers ...], "nextCursor": "<cursor>"}
- accountUid=<uid>, demandPartnerId=<id>, cursor="<cursor>" -> {"items": [... the next buyers ...], "nextCursor": null}
- No match -> {"items": [], "nextCursor": null}

Notes:
- Requires the pmp.read permission; callers without it receive FORBIDDEN.
- Buyers are read from OXS-BE as the caller; a caller OXS-BE does not accept also receives FORBIDDEN.
- accountUid must be the UID of an account the caller can see, e.g. 61e52f0c-accf-fff1-8123-6b040b. A malformed UID, or an account the caller cannot see or that does not exist, returns BAD_REQUEST: correct accountUid rather than retrying. SERVICE_UNAVAILABLE is an upstream failure.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `accountUid` | `String` | Yes | UID of the account whose deals the buyers are listed for |
| `demandPartnerId` | `String` | Yes | Id of the demand partner, as returned by listDemandPartners, e.g. 537073292 |
| `search` | `String` | No | Case-insensitive substring of a seat id to filter by; buyer names are not searched. Default: none - every buyer of the demand partner, a page at a time |
| `cursor` | `String` | No | Opaque nextCursor of the previous page of the same search; never parse or build one. Default: none - the first page |
| `pageSize` | `Integer` | No | Most buyers on the page, at least 1; a value above 50 is lowered to 50. Default: 50 |

---

### `listDemandPartners` · deal

**Title:** List Demand Partners  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

List the demand partners (DSPs) a deal can be exposed to under the given account.

Use when:
- The user names a DSP and you need its demand partner id, or need to check that a deal under the account can target that DSP. Pass search with the DSP name to narrow the results.
- A demand partner id needs a name, e.g. dealParticipants[].demandPartner returned by getDealDetails, which holds the same id as results[].id.
Never guess or construct a demand partner id: use only ids returned by this tool.

Returns:
- results: [{id, name}] - id identifies the demand partner; name is for matching and display.
The list is account- and permission-scoped, not global: an account may restrict which DSPs are targetable, and internal test DSPs are listed only to internal users. A DSP the user names may legitimately be absent - say so rather than substituting a similar one. At most ~100 entries, so no pagination.

Examples:
- accountUid=<uid>, search="trade" -> {"results": [{"id": "<id>", "name": "The Trade Desk"}]}
- accountUid=<uid> -> {"results": [{"id": "...", "name": "..."}, ...]} (every DSP targetable under the account)

Notes:
- Requires the pmp.read permission; callers without it receive FORBIDDEN.
- Demand partners are read from OXS-BE as the caller; a caller OXS-BE does not accept also receives FORBIDDEN.
- accountUid must be the UID of an account the caller can see, e.g. 61e52f0c-accf-fff1-8123-6b040b. A malformed UID, or an account the caller cannot see or that does not exist, returns BAD_REQUEST rather than an empty list: correct accountUid rather than retrying. SERVICE_UNAVAILABLE is an upstream failure.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `accountUid` | `String` | Yes | UID of the account whose deals the demand partners are listed for |
| `search` | `String` | No | Case-insensitive substring of the demand partner name to filter by, e.g. "trade". Default: none - every demand partner targetable under the account is returned |

---

### `getDealAnalytics` · dealtroubleshooting

**Title:** Get Deal analytics  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Retrieves broad deal analytics for an initial troubleshooting or health-check overview.

Use when:
- Starting troubleshooting for a deal.
- The user asks for deal analytics, deal health, overall status, or a general performance check.
- Checking basic deal identity, account, spend, delivery, and revenue metrics.

Input:
- dealId: Numeric deal identifier.

Returns:
- Deal identity: id, uid, accountId, accountUid, name.
- Optional high-level metrics when available: spend, CPM, viewability, VTR,
  impressions, eligible bid requests, targeted bid requests, bid responses,
  fills, publisher revenue, and third-party revenue.
- healthScore: Average Deal Health Score for the last 8 days ending yesterday, 0-100
  (0-19 Critical, 20-69 Warning, 70-100 Healthy).

Notes:
- This tool gives a broad overview only. Use more specific troubleshooting tools
  for deeper analysis when the user asks for details or when the overview shows
  possible issues.
- For the current Deal Health Score and its causes, use getDealNrtMetrics.
- Optional metrics may be missing/null if the downstream service does not return them.
- A response with only identity fields should be treated as partial data, not as no activity.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `dealId` | `Long` | Yes | Internal deal ID |

---

### `getDealAudittrailChanges` · dealtroubleshooting

**Title:** Get Deal Audittrail Changes  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Retrieve audit trail of deal configuration changes within a timeframe.

Purpose:
- analyze how config changes affect delivery, spend, and metrics
Use when: - investigating performance anomalies
 - troubleshooting deal issues
- correlating configuration changes with NRT metrics
 Input:
- dealId (Long): identifier of the deal
- startTime (timestamp, optional, default: now-48h)
- endTime (timestamp, optional, default: now)

Notes:
- package is resolved from the deal

Constraints:
- maximum time period: 30 daysReturns:
- audittrail: chronological events with:
   - objectType ("deal" or "package")
   - objectId (number)
   - timestamp
   - changes (map): field-level changes; oversized values are truncated


**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `dealId` | `Long` | Yes | Internal deal ID |
| `startTime` | `OffsetDateTime` | No | Start of the timeframe (ISO-8601, e.g. '2026-03-18T00:00:00Z'). Defaults to 48 hours before end_time when not provided. |
| `endTime` | `OffsetDateTime` | No | End of the timeframe (ISO-8601, e.g. '2026-03-20T00:00:00Z'). Defaults to now when not provided. |

---

### `getDealFilterOptions` · dealtroubleshooting

**Title:** Get Deal Filter Options  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

For a deal, return the top values of one dimension by impression volume. Use it to turn a qualitative filter request into the concrete values the other deal-troubleshooting tools (getDealMetricsByDay, getDealNrtMetrics, getDealMetricsByDimension, getDealMetricsByDimension) accept.

Use when:
- you need the concrete filter values for a dimension before calling another tool — e.g. to resolve "the Trade Desk DSP" or "video formats" into the exact stored values to pass as a filter argument.
- an earlier tool call returned no data and a filter value may be misspelled or wrong-cased.

Returns:
- items: [{ dimension_value, impressions }] sorted by impressions descending; NULL values of the chosen dimension are excluded.

Note: filter values are matched exactly and are case-sensitive — channel=["app"] will not match the stored value "App". If a query returns no data, discover the real values with this tool first, then retry.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `dealId` | `Long` | Yes | Internal deal ID |
| `dimension` | `DealDimension` | Yes | Dimension to group results by (one of the 14 enum values) |
| `limit` | `Integer` | No | Top-N cap (default 20, max 50) |
| `startDate` | `LocalDate` | No | Start date (YYYY-MM-DD). Default: 7 days before endDate |
| `endDate` | `LocalDate` | No | End date (YYYY-MM-DD). Default: yesterday (UTC) |
| `channel` | `List<String>` | No | Filter by channel (e.g. Site, App) |
| `format` | `List<String>` | No | Filter by format (e.g. Display, Video) |
| `device` | `List<String>` | No | Filter by device type (e.g. desktop, tablet, connected_tv) |
| `buyerName` | `List<String>` | No | Filter by buyer name |
| `dspName` | `List<String>` | No | Filter by DSP name (e.g. DV360 - RTB, The Trade Desk - RTB) |
| `publisherName` | `List<String>` | No | Filter by publisher name |

---

### `getDealFunnelConversions` · dealtroubleshooting

**Title:** Get Deal Funnel Conversions  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Retrieves a 7-day performance snapshot of deal funnel conversion rates and CPM, benchmarked against industry percentiles for the same channel, format, and device.

Use when:
- Pinpointing which funnel step (Targeting, Bid, Fill, or Impression Rate) is dropping traffic.
- Diagnosing spend scaling bottlenecks, low delivery, or deal under-pacing.
- Distinguishing between low incoming traffic volume vs. late-funnel drop-offs.

Returns:
- stats: Top 5 highest-traffic breakdown categories (channel × format × device). Metrics include: targeting coverage, bid rate, fill rate, impression rate, and CPM. Each metric contains a value and a band name referencing the top-level legend. Categories with lowSample=true have fewer than 30 comparable deals — treat their metrics as weak, low-confidence signals only.
- bands: A global map matching band names to troubleshooting actions. Look up a metric's band here to determine the exact recommended next step.

Does not cover:
- Root cause analysis explaining why a specific step is failing. Pair with Loss Reasons or Targeting Settings tools to uncover specific auction drop-off causes.
- Time-series trends or live anomalies. Use Spikes/Drops (NRT) for real-time tracking.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `dealId` | `Long` | Yes | Internal deal ID |

---

### `getDealMetricsByDay` · dealtroubleshooting

**Title:** Get Deal Metrics By Day  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Retrieves deal metrics per day for a date range, optionally filtered by channel, format, device, buyer, DSP or publisher.

Use when:
- Looking for trends or day-over-day changes in delivery, spend or funnel metrics.
- Checking how the Deal Health Score changed over the range.

Notes:
- HEALTH_SCORE is deal-level, so it is omitted when a filter is set.

Constraints:
- endDate minus startDate is at most 31 days.
- startDate cannot be earlier than the earliest available report date.

Does not cover:
- Hourly or current data. Use getDealNrtMetrics.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `dealId` | `Long` | Yes | Internal deal ID |
| `startDate` | `String` | No | Start date (YYYY-MM-DD). Defaults to 7 days ago |
| `endDate` | `String` | No | End date (YYYY-MM-DD). Defaults to yesterday |
| `metrics` | `List<DealDailyMetric>` | No | Metrics to retrieve. Defaults to ELIGIBLE_BID_REQUESTS, TARGETED_BID_REQUESTS, BID_RESPONSES, FILLS, IMPRESSIONS, SPEND, CPM, HEALTH_SCORE |
| `channel` | `List<String>` | No | Filter by channel (e.g. Site, App) |
| `format` | `List<String>` | No | Filter by format (e.g. Display, Video) |
| `device` | `List<String>` | No | Filter by device type (e.g. desktop, tablet, connected_tv) |
| `buyerName` | `List<String>` | No | Filter by buyer name |
| `dspName` | `List<String>` | No | Filter by DSP name (e.g. DV360 - RTB, The Trade Desk - RTB) |
| `publisherName` | `List<String>` | No | Filter by publisher name |

---

### `getDealMetricsByDimension` · dealtroubleshooting

**Title:** Get Deal Metrics By Dimension  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Retrieves deal performance metrics aggregated over a date range, broken down by a single dimension (e.g. channel, device, country, publisher, DSP, or IAB category).

Use when:
- Identifying which dimension values drive or block deal traffic (e.g. which channels or countries deliver the most impressions).
- Narrowing down a funnel drop-off to a specific slice before digging deeper with other tools.
- Comparing traffic share across publishers, buyers, DSPs, or any other supported dimension selected via the tool input.

Returns:
- rows: Top N dimension values (default 10, max 30) ranked by targeted_bid_requests. Each row contains dimension_value and the requested metrics. Default metrics: eligible_bid_requests, targeted_bid_requests, bid_responses, fills, impressions, spend, cpm.

Does not cover:
- Day-by-day trends. Use getDealMetricsByDay for time-series analysis over the same period.
- Cross-dimension breakdowns (e.g. channel × format simultaneously). Call this tool once per dimension of interest.
- Specific causes of funnel drop-offs. Use Loss Reasons or Targeting Settings tools for deeper diagnosis.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `dealId` | `Long` | Yes | Internal deal ID |
| `groupByColumn` | `DealDimensionGroupByColumn` | Yes | Dimension to group results by. Valid values: CHANNEL, FORMAT, DEVICE, COUNTRY, ADSIZE, DOMAIN, BUNDLE, PUBLISHER_NAME, DSP_NAME, BUYER_NAME, IABCATEGORY_1, IABCATEGORY_2, IABCATEGORY_3 |
| `startDate` | `LocalDate` | No | Start date. Defaults to 7 days ago. Earliest allowed: beginning of the previous calendar month |
| `endDate` | `LocalDate` | No | End date. Defaults to yesterday |
| `metrics` | `List<DealDimensionMetric>` | No | Metrics to retrieve. Defaults to ELIGIBLE_BID_REQUESTS, TARGETED_BID_REQUESTS, BID_RESPONSES, FILLS, IMPRESSIONS, SPEND, CPM |
| `limitGroupBy` | `Integer` | No | Number of top dimension values to return, ranked by targeted_bid_requests. Default: 10, max: 30 |
| `channel` | `List<String>` | No | Filter by channel (e.g. Site, App) |
| `format` | `List<String>` | No | Filter by format (e.g. Display, Video) |
| `device` | `List<String>` | No | Filter by device type (e.g. desktop, tablet, connected_tv) |
| `publisherName` | `List<String>` | No | Filter by publisher name |
| `dspName` | `List<String>` | No | Filter by DSP name (e.g. DV360 - RTB, The Trade Desk - RTB) |
| `buyerName` | `List<String>` | No | Filter by buyer name |

---

### `getDealNrtMetrics` · dealtroubleshooting

**Title:** Get Deal NRT Metrics  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Retrieve Near Real-Time (NRT) hourly metrics for a deal for the last 48 hours. Use when the user asks about recent performance changes, spikes, or drops, or about the deal's current health. Data is sampled and may not be fully accurate — use as directional signal only. Latency is 20-30 min — the most recent data point may be incomplete. HEALTH_SCORE is deal-level, so it is omitted when dspNames is set.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `dealId` | `Long` | Yes | Internal deal ID |
| `startTimestamp` | `OffsetDateTime` | No | Start timestamp in ISO-8601 UTC format, e.g. '2026-04-14T13:00:00Z'. Omit for 48h lookback. |
| `metrics` | `List<DealMetric>` | No | Metrics to include. Defaults to: ELIGIBLE_BID_REQUESTS, TARGETED_BID_REQUESTS, BID_RESPONSES, FILLS, IMPRESSIONS, SPEND, CPM, HEALTH_SCORE |
| `dspNames` | `List<String>` | No | Filter by DSP names |

---

### `getDealTargetingConfiguration` · dealtroubleshooting

**Title:** Get Deal Targeting Configuration  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Retrieves the compiled targeting configuration for a deal — the authoritative set of active targeting rules across all dimensions.

Use when:
- Inspecting active deal targeting.
- Diagnosing delivery issues caused by restrictive or incorrect targeting.
- Verifying that targeting changes have been compiled by ETL.
- Investigating targeting bottlenecks identified in funnel analysis.

Returns:
- retrievalStatus: FOUND — compiled targeting exists; NOT_FOUND_NO_PACKAGE — no package associated with the deal; NOT_FOUND_NO_CONFIG — package exists, but no compiled targeting configuration is available.
- targetingRules — structured targeting expression tree (when FOUND). Leaves may include a human-readable dimension label and description.

- validation — missingRequiredDimensions lists required dimensions absent from the targeting; nonStandardDimensions is true when the targeting includes attributes not supported by the current OpenX UI.


Notes:
- Use alongside getDealAnalytics for overall performance context.
- Use alongside getDealFunnelConversions when targeting coverage appears to be a bottleneck.
- Use alongside getDealMetricsByDimension to understand traffic distribution.
- Use alongside getDealAudittrailChanges to review recent changes.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `dealId` | `Long` | Yes | Internal deal ID |

---

### `lossReasonAnalysis` · dealtroubleshooting

**Title:** Loss Reason Analysis  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Analyzes why a deal's bids lose auctions, as loss reason groups ranked by lost bids, optionally split by publisher, DSP, domain or bundle to show where losses concentrate.

Use when:
- Determining whether losses come from price, targeting, inventory eligibility or bid errors.
- The user asks which publishers, DSPs, domains or bundles account for most of a loss reason.

Returns:
- items: loss reason groups over the bids this request matches — lost bids (value), share of those bids (pct, won auctions included in the denominator), a business explanation and a recommended action.
- rows: only when groupByColumn is set — one entry per dimension value and loss reason, with pctOfDimensionValue (share of that value's own bids) and pctOfTotal (share of the bids items covers). Compare the two to tell a slice-specific problem from a widespread one; the explanation and action stay in items.
- groupBy: the dimension rows are split by.

Reporting the numbers:
- items is deal-wide only when the call passes no filter and no groupByColumn. Report it as the slice that was asked about otherwise, and call the tool bare for deal totals.
- A dimension value's share says where losses concentrate, not who can resolve them. The fix is items[].recommendedAction; do not infer that the named counterparty is the party to contact.

Constraints:
- Splitting or filtering reads a larger table: roughly the last two months, at most 31 days per call. Without those parameters the range is unbounded.
- Bids whose split value is unknown are dropped, so a BUNDLE split covers app traffic only and a DOMAIN split site traffic only.
- limitGroupBy caps dimension values (10 by default, 30 at most, clamped not rejected). Narrow a wide split with a lossReason filter rather than raising it.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `dealId` | `Long` | Yes | Internal deal ID |
| `startDate` | `LocalDate` | No | Start date for analysis. Optional, defaults to 6 days before the end date, for a 7-day inclusive window |
| `endDate` | `LocalDate` | No | End date for analysis. Optional, defaults to yesterday (UTC), the last complete day. A later date is rejected |
| `groupByColumn` | `LossReasonDimension` | No | Dimension to split the loss reasons by. Valid values: PUBLISHER_NAME, DSP_NAME, DOMAIN, BUNDLE. Omit to get the deal-wide breakdown only |
| `limitGroupBy` | `Integer` | No | Number of top dimension values to return, ranked by lost bids. Default: 10, max: 30. Only used together with groupByColumn |
| `publisherName` | `List<String>` | No | Filter by publisher name (exact match) |
| `dspName` | `List<String>` | No | Filter by DSP name, exact match (e.g. DV360 - RTB, The Trade Desk - RTB) |
| `domain` | `List<String>` | No | Filter by site domain (exact match, e.g. example.com) |
| `bundle` | `List<String>` | No | Filter by app bundle (exact match) |
| `lossReason` | `List<String>` | No | Filter by loss reason group, case-insensitive, as returned in items[].lossReason (e.g. Low Price, No Bid, Self Compete) |

---

### `getPackages` · pkg

**Title:** Get Packages  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Retrieve a list of packages with optional filtering, ordering, and pagination. Returns list of package details including uid, id, name, account_uid, rate_card_cpm, discounted_cpm, targeting, private_market, tags[], is_curated

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | `Long` | No | Filter by exact package ID |
| `accountId` | `Long` | No | Filter by exact account ID |
| `name` | `String` | No | Filter by exact package name |
| `distributionChannel` | `String` | No | Filter by distribution channel |
| `maxRateCardCpm` | `Double` | No | Filter by maximum rate card CPM (inclusive) |
| `isCurated` | `Boolean` | No | Filter by curated status |
| `orderBy` | `List<OrderBy<PackageOrderByField>>` | No | Order by fields with direction (ASC/DESC) |
| `offset` | `Integer` | No | Offset for pagination (default: 0) |
| `limit` | `Integer` | No | Maximum number of packages to return (1-100, default: 20) |

---

### `getSite` · site

**Title:** Get Site  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Get site by ID

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | `long` | Yes | Site ID |

---

### `getSites` · site

**Title:** Get Sites  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

Search sites with optional filters. Returns site information including uid, id, name, url, account_uid, distribution_channel, delivery_medium, status, and IAB categories. For mobile apps, includes app_info details.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `filter` | `SiteFilterInput` | No | Filters to apply to site search. Supports filtering by account_id, status, distribution_channel, and ssp_enabled |
| `orderBy` | `List<OrderBy<SiteOrderByInput>>` | No | Order by fields with direction (ASC/DESC) |
| `offset` | `Integer` | No | Offset for pagination (default: 0) |
| `limit` | `Integer` | No | Maximum number of sites to return (1-100, default: 20) |

---

### `getUserInstances` · user

**Title:** Get User Instances  
**Hints:** read-only · idempotent · typed output schema  

**Description:**

List all OpenX platform instances the currently authenticated user has an account on. Takes no arguments — the user is identified from the session, so this always describes the caller and cannot be used to look up anyone else. Returns one entry per instance with its instanceUid (the platform hash) and the instance name. Deleted user records are excluded.

---

## Resources

### `appcategory` · application

**URI template:** `appcategory://{id}`  
**MIME type:** `application/json`  

AppCategory resource

---
