# OpenX MCP tools: deals, campaigns and audiences

Orders, line items, creatives, deals, packages, audiences, delivery metrics and forecasting in OpenXDirect and OpenXSelect. Each heading is the name a client calls through `https://api.openx.com/mcp`.

103 tools: 66 read-only, 37 that make changes.

## Contents

- [audiences](#audiences) (10)
- [creatives](#creatives) (7)
- [curated deal buyer discounts](#curated-deal-buyer-discounts) (4)
- [deal prompt search](#deal-prompt-search) (3)
- [deals](#deals) (8)
- [diagnostics](#diagnostics) (1)
- [entity fields](#entity-fields) (1)
- [exports](#exports) (3)
- [line items](#line-items) (14)
- [normalized definition](#normalized-definition) (2)
- [options](#options) (3)
- [orders](#orders) (11)
- [packages](#packages) (8)
- [pixels](#pixels) (5)
- [platform](#platform) (4)
- [retargeting](#retargeting) (10)
- [segments](#segments) (7)
- [skills](#skills) (2)

## audiences

### activateAudience · **mutation**

Activate an Audience. Required before it can be referenced from a Package's targeting.audience.openaudience_custom, and therefore before it can be used in a Deal. Part of an audience build: read the openx-audience-build skill first (getSkill).

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Audience's id (uuid). The openaudience- prefixed form that package targeting carries (audience.openaudience_custom.val) is accepted too. |

Returns: The activated Audience's id. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### archiveAudience · **mutation**

Archive an Audience.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Audience's id (uuid). The openaudience- prefixed form that package targeting carries (audience.openaudience_custom.val) is accepted too. |

Returns: The archived Audience's id. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### countAudiences

Fetch the count of available Audiences.

Products: OpenXDirect, OpenXSelect

_No parameters._

Returns: The count of Audiences.

### createAudience · **mutation**

Create a new Audience. Must be activated (activateAudience) before it can be referenced from a Package's targeting (and therefore from a Deal). Read the openx-audience-build skill first (getSkill) for finding segments, compiling, sizing and pricing the definition before it is created.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | The descriptive short name for the Audience. |
| `export_type` | string | yes | The type of export: "oa_match", "bidstream", or "bidstream_plus". |
| `export_targets` | list of string | yes | Target match keys, e.g. ["cookie", "device", "idl", "ctv", "ip", "id5"] ("user" is a backward-compatible synonym for any person-level identifier). |
| `direct_audience_provider` | string | yes | The provider id of the Audience. |
| `normalized_definition` | object | yes | The Audience definition, as compileAudienceDefinition returns it. |
| `description` | string | no | The description of the Audience. |
| `account_id` | string | no | The account to create the Audience under. Defaults to the caller's account when omitted. Takes a numeric OpenXSelect account id, as listAccountsForProduct returns it; naming an account you may not create under is refused, not ignored. |

Returns: The created Audience with its id, name, and other fields, and as url its page in OpenXSelect, to show the user. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### estimateAudience

Dry-run an Audience's approximate reach, without creating it. Takes the same arguments as createAudience. Part of an audience build: read the openx-audience-build skill first (getSkill).

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | The descriptive short name for the Audience. |
| `export_type` | string | yes | The type of export: "oa_match", "bidstream", or "bidstream_plus". |
| `export_targets` | list of string | yes | Target match keys. |
| `direct_audience_provider` | string | yes | The provider id of the Audience. |
| `normalized_definition` | object | yes | The Audience definition, as compileAudienceDefinition returns it. |
| `description` | string | no | The description of the Audience. |

Returns: A list of approximate size estimates, one row per id type (OAIDs, cookies, etc). When the audience service returns no estimate, the tool retries once, then returns an empty list with estimate_available false and a message. That most often means a segment reference in normalized_definition does not resolve (an invented id, or a state code where a location Segment belongs), so check the references before retrying again.

### getAudience

Fetch a single Audience by its id.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Audience's id (uuid). The openaudience- prefixed form that package targeting carries (audience.openaudience_custom.val) is accepted too. |

Returns: The Audience, and as url its page in OpenXSelect, to show the user. An unknown id is a not-found error.

### getAudiencePricing

Price an Audience's third-party data before creating it, the same way createAudience prices it. Takes createAudience's arguments except account_id: the price is always worked out for your own account, whose own segments are free. An audience created under another account (createAudience with account_id) is priced for that account instead, so its total can differ from this one. Part of an audience build: read the openx-audience-build skill first (getSkill).

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | The descriptive short name for the Audience. |
| `export_type` | string | yes | The type of export: "oa_match", "bidstream", or "bidstream_plus". |
| `export_targets` | list of string | yes | Target match keys. |
| `direct_audience_provider` | string | yes | The provider id of the Audience. |
| `normalized_definition` | object | yes | The Audience definition, as compileAudienceDefinition returns it. |
| `description` | string | no | The description of the Audience. |

Returns: The data partners paid (each with its highest CPM and percent-of-media price among its included segments, and the account_ids that match it to segments) and the audience's total price. Percent-of-media values are fractions: 0.15 is 15%. How the total is formed depends on operator: UNION averages the partners' prices, because an impression matches one of them; INTERSECT sums them, because every partner is paid. Null when nothing in the audience is paid for, e.g. OpenX segments only.

### getAudienceReachReport

Fetch the reach report for an Audience. Requires that the Audience's report_status has changed to "complete".

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Audience's id (uuid). The openaudience- prefixed form that package targeting carries (audience.openaudience_custom.val) is accepted too. |

Returns: The reach report, broken down by dimension and metric.

### listAudiences

List a page of Audiences, each with its standard fields or the fields you choose. Prefer searchOptionsByPath(path="audience", filters=[...]) for finding audiences by name, status, dates or any other field: it reports an exact total_count. This tool takes the same filters and sort when you need more than id and name.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | yes | The number of Audiences to return. |
| `offset` | integer | yes | The offset from the first Audience. |
| `filters` | list of object (name, op, val) | no | Field filters, combined with AND. They take the same fields and operations as searchOptionsByPath(path="audience"). Each filter has exactly the keys "name", "op" and "val", e.g. {"name": "name", "op": "_contains", "val": ["Acme"]}. op is a SearchFilterOp name such as "_eq" or "_gte", never a symbol such as "==" or ">=". val is always a list, even for one value: ["123"], not "123". A field takes at most one filter per operation, and filters never combine with OR: to match any of several exact values use "_in"; to match any of several substrings, search once per substring. A filter on a field outside that list is refused. |
| `sort` | string | no | Field to sort by, as in searchOptionsByPath(path="audience"); prefix with "-" for descending, e.g. "-created_date". Omit it to keep the default order. |
| `fields` | list of string | no | The Audience fields to return, as dot paths relative to the audience, e.g. ["name", "status", "addressable_reach", "last_export.status"]. "<object>.*" returns every plain field under an object. id always comes back. listEntityFields(entity="audience") lists every path. With fields, limit is at most 200. Rows times selected fields is held to 2,000 values per call. |

Returns: {"audiences": [...]}, each with only the fields asked for, or its standard fields without fields. When part of a selection fails, the audiences that came back are returned with an "errors" list saying what failed and where.

### updateAudience · **mutation**

Update an existing Audience. Only the fields you pass are changed: a value replaces the current one, null clears the field, and a field left out keeps its value. name cannot be cleared.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Audience's id (uuid). The openaudience- prefixed form that package targeting carries (audience.openaudience_custom.val) is accepted too. |
| `name` | string | no | The descriptive short name for the Audience. |
| `description` | string | no | The description of the Audience. |
| `export_type` | string | no | The type of export: "oa_match", "bidstream", or "bidstream_plus". |
| `export_targets` | list of string | no | Target match keys. |
| `direct_audience_provider` | string | no | The provider id of the Audience. |
| `normalized_definition` | object | no | The Audience definition, as compileAudienceDefinition returns it. |

Returns: The updated Audience. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

## creatives

### activateCreative · **mutation**

Activate a Paused BidderCreative. Only Paused creatives can be activated. Requires OpenXDirect on the account. Part of a campaign build: read the openx-campaign-launch skill first (getSkill).

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The BidderCreative's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The activated BidderCreative. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### archiveCreative · **mutation**

Archive (soft delete) a BidderCreative. Requires OpenXDirect on the account.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The BidderCreative's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The archived BidderCreative's id. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### createCreative · **mutation**

Create a new BidderCreative, the ad markup a campaign line item serves. Requires OpenXDirect on the account. Part of a campaign build: read the openx-campaign-launch skill first (getSkill) for the identifier, unit and ordering rules.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | The creative name or label. Must be unique within the account. |
| `crid` | string | yes | External id of the creative. |
| `ad_format` | string | yes | "Banner" or "Video". |
| `markup_type` | string | yes | "HTML" or "VAST". |
| `markup_payload` | string | yes | The raw markup or tag payload. |
| `status` | string | yes | "Active" or "Paused" -- unusually, required on create (no default). |
| `account_id` | string | no | The parent account ID. Defaults to the caller's account when omitted. Accepts either the numeric account ID or the account UID. |
| `width` | string or integer | no | Width in pixels. Required for banner creatives (1-10000), not applicable for video. |
| `height` | string or integer | no | Height in pixels. Required for banner creatives (1-10000), not applicable for video. |
| `iab_categories` | list of string | no | List of IAB taxonomy categories. |
| `industries` | list of string | no | Industries (brand groups) the creative belongs to, as ids from optionsByPath(path="bidder_creative.industries"). |
| `language` | string | no | ISO 639-1 language code. Defaults to "en". |
| `advertiser_domain` | string | no | The advertiser's primary domain. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The created BidderCreative with its id, crid, name, and other fields, and as url its page in OpenXDirect, to show the user. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### getCreative

Fetch a single BidderCreative by its id. Requires OpenXDirect on the account.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The BidderCreative's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The BidderCreative, and as url its page in OpenXDirect, to show the user. An unknown id is a not-found error, and a creative on another instance is a "Wrong instance" error naming the instance_uid to pass.

### listCreatives

Page through BidderCreatives, each with its standard fields (markup included) or the fields you choose. Requires OpenXDirect on the account. This tool takes the same filters and sort as searchOptionsByPath(path="bidder_creative") at about the same cost per page, but search returns every creative's full record. To show a user a list, pass fields (e.g. ["name", "status"]) here for a far smaller response that leaves the markup out.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | no | The number of creatives to return. |
| `offset` | integer | no | The offset from the first creative. |
| `filters` | list of object (name, op, val) | no | Field filters, combined with AND. They take the same fields and operations as searchOptionsByPath(path="bidder_creative"). Each filter has exactly the keys "name", "op" and "val", e.g. {"name": "name", "op": "_contains", "val": ["Acme"]}. op is a SearchFilterOp name such as "_eq" or "_gte", never a symbol such as "==" or ">=". val is always a list, even for one value: ["123"], not "123". A field takes at most one filter per operation, and filters never combine with OR: to match any of several exact values use "_in"; to match any of several substrings, search once per substring. |
| `sort` | string | no | Field to sort by, as in searchOptionsByPath(path="bidder_creative"); prefix with "-" for descending, e.g. "-created_date". Omit it to keep the default order. |
| `fields` | list of string | no | The BidderCreative fields to return, as dot paths relative to the creative, e.g. ["name", "status", "width", "height"]. A path ending on an object returns its standard fields ("delivery_metrics"), or its plain fields when it has no standard set; "<object>.*" returns every plain field under it. id and instance_uid always come back. listEntityFields(entity="bidder_creative") lists every path. With fields, limit is at most 200, or 25 when any delivery_metrics path is selected; omitted, it is that maximum. Rows times selected fields is held to 2,000 values per call. |
| `range` | string | no | The window delivery_metrics covers: "YESTERDAY", "LAST_7_DAYS", "LAST_30_DAYS" (the default) or "FULL_FLIGHT". Only with a delivery_metrics path in fields; refused otherwise. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: {"bidderCreatives": [...]}: without fields each creative carries its standard fields; with fields, only those asked for. When part of a selection fails (delivery_metrics on an account without OpenXDirect), the creatives that came back are returned with an "errors" list saying what failed and where.

### pauseCreative · **mutation**

Pause an Active BidderCreative. Only Active creatives can be paused. Requires OpenXDirect on the account.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The BidderCreative's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The paused BidderCreative. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### updateCreative · **mutation**

Update an existing BidderCreative. Only the fields you pass are changed; a field left out keeps its value. null clears advertiser_domain only; every other field keeps its current value when sent null, so send a value for it. Requires OpenXDirect on the account. There is no crid argument -- crid is immutable after create.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The BidderCreative's id. |
| `name` | string | no | The creative name or label. |
| `status` | string | no | "Active" or "Paused" -- prefer pauseCreative/activateCreative for lifecycle transitions. |
| `ad_format` | string | no | "Banner" or "Video". |
| `width` | string or integer | no | Width in pixels. |
| `height` | string or integer | no | Height in pixels. |
| `markup_type` | string | no | "HTML" or "VAST". |
| `markup_payload` | string | no | The raw markup or tag payload. |
| `iab_categories` | list of string | no | List of IAB taxonomy categories. |
| `industries` | list of string | no | Industries (brand groups) the creative belongs to, as ids from optionsByPath(path="bidder_creative.industries"). |
| `language` | string | no | ISO 639-1 language code. |
| `advertiser_domain` | string | no | The advertiser's primary domain. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The updated BidderCreative. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

## curated deal buyer discounts

### createCuratedDealBuyerDiscount · **mutation**

Create a new Curated Deal Buyer Discount. Requires the CURATED_DEAL_BUYER_DISCOUNT feature flag. At least one of banner_and_video_discount/ctv_discount is required, and exactly one of demand_partner_id/seat_ids is required -- they're mutually exclusive.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | The descriptive name for the Curated Deal Buyer Discount. |
| `banner_and_video_discount` | number | no | The discount value applied to banner and video ad formats. |
| `ctv_discount` | number | no | The discount value applied to connected TV (CTV) devices. |
| `demand_partner_id` | string | no | The id of the demand partner this discount applies to. Must match the `id` field returned from optionsByPath(path="deal.deal_participants.demand_partner"). |
| `seat_ids` | list of string | no | Seat ids this discount applies to. Must match the `id` field returned from optionsByPath(path="curateddealbuyerdiscount.seat_ids", filter={"used_by_curateddealbuyerdiscount_account_id": <your_account_id>}), restricted to results where extra.used_by_curateddealbuyerdiscount is false. |
| `account_id` | string | no | The account to create the discount under. Defaults to the caller's account when omitted. Accepts the numeric account id or the account uid, from listAccountsForProduct or a searchOptionsByPath "account" result; the caller must have access to that account. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The created Curated Deal Buyer Discount. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### deleteCuratedDealBuyerDiscount · **mutation**

Delete a Curated Deal Buyer Discount. Requires the CURATED_DEAL_BUYER_DISCOUNT feature flag. Unlike other entities' archive mutations, this schema field returns JSON rather than the deleted id -- callers should not expect a plain string back.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Curated Deal Buyer Discount's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The deletion result as JSON, passed through as-is. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### listCuratedDealBuyerDiscounts

List Curated Deal Buyer Discounts. Requires the CURATED_DEAL_BUYER_DISCOUNT feature flag.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | yes | The number of discounts to return. |
| `offset` | integer | yes | The offset from the first discount. |
| `sort` | string | no | Sort expression forwarded to the underlying API, e.g. "-name". |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: A page of Curated Deal Buyer Discounts, with has_more/limit/offset paging metadata alongside the objects.

### updateCuratedDealBuyerDiscount · **mutation**

Update an existing Curated Deal Buyer Discount. Only the fields you pass are changed: a value replaces the current one, null clears the field, and a field left out keeps its value. name cannot be cleared. Requires the CURATED_DEAL_BUYER_DISCOUNT feature flag.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Curated Deal Buyer Discount's id. |
| `name` | string | no | The descriptive name for the Curated Deal Buyer Discount. |
| `banner_and_video_discount` | number | no | The discount value applied to banner and video ad formats. |
| `ctv_discount` | number | no | The discount value applied to connected TV (CTV) devices. |
| `seat_ids` | list of string | no | Seat ids this discount applies to -- see createCuratedDealBuyerDiscount. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The updated Curated Deal Buyer Discount. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

## deal prompt search

### searchDealAudienceSegmentsByPrompt

Open-ended discovery of audience segments, for when no category fits. Age, gender, location and the interest categories are deterministic: listSegmentsByCategory with the category and a names or search filter returns exactly those rows, so use it first, and read the openx-audience-build skill (getSkill) when building an Audience. Use this search for a description that spans categories, such as "adults 25-45 interested in travel". Any field set in filters takes precedence over the AI suggestion for that field. Use the result's segment ids, keeping predefined rows and direct rows with sellable true, and build the definition from them with compileAudienceDefinition: the result's own normalized_definition includes unsellable rows and estimateAudience rejects it as returned.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | yes | Free-text description of the audience being searched for, e.g. "adults 25-45 interested in travel". |
| `filters` | object | no | Optional raw dict matching AudienceSegmentSearchFiltersInput's nested shape: locationFilter ({values, type} -- type one of STATE/DMA/ CONGRESSIONAL_DISTRICT, exactly one location kind per request), goalUniqueUsersReach, demographicsGender, demographicsAge ({min, max}), segmentsCategories, segmentsSubCategories, segmentsSearchMode, segmentsDataPartners (partner ids from optionsByPath(path="segment.data_partner")). |
| `limit` | integer | no | How many of the most relevant segments to return, 20 by default; each segment row is about 1K characters. Default `20`. |

Returns: Up to `limit` matching segments. The metrics and the normalized_definition cover the full match set, not only the returned rows, so never pass that definition on: build the definition from the segment ids you keep with compileAudienceDefinition.

### searchDealBundlesByPrompt

Open-ended discovery of mobile apps (bundles) for a Deal's Package targeting, for when no named list fits. Named apps go straight into the package's app inventory targeting by bundle id, no search needed. Use this search for a description of apps, such as "casual mobile games with high engagement". Same filters and ranking caveat as searchDealDomainsByPrompt: slow, loosely ranked, keep what fits. For a deal build read the openx-deal-creation skill first (getSkill); it decides when a named app list replaces this search.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | yes | Free-text description of the inventory being looked for, e.g. "casual mobile games with high engagement". |
| `geography` | list of string | no | ISO country codes to restrict the search to, e.g. ["US", "PL"]. |
| `device_type` | list of string | no | Device types to restrict to. Allowed values: "phone", "mobile/tablet", "tablet", "desktop", "set-top-box", "connected tv". |
| `media_subtype` | list of string | no | Ad formats to restrict to. Allowed values: "Display", "Video", "Native". |
| `limit` | integer | no | How many of the most relevant bundles to return, 50 by default. total_results still reports the full match count. Default `50`. |

Returns: Up to `limit` matching bundles sorted by relevance (descending), the full match count in total_results, and the filters that were ultimately applied.

### searchDealDomainsByPrompt

Open-ended discovery of websites (domains) for a Deal's Package targeting, for when no category and no named list fits. Two deterministic routes come first and need no domain list at all: - A kind of site (news, sports, finance, cooking) is an IAB content category. Find it with searchOptionsByPath(path="deal.package.targeting.domain.categories_iab_v2", filters=[{"name": "name", "op": "_contains", "val": ["news"]}], limit=20) and target the category id; the deal then runs on every site classified that way. - Named sites go straight into the package's url_targeting as an allowlist or a blocklist. Use this search only for a description neither route covers, such as "independent cooking blogs with high viewability". It runs an LLM plus a vector search, so it is slow and loosely ranked: keep the domains that really fit and show the user a short list. Any filter passed here takes precedence over the AI suggestion for that filter. For a deal build read the openx-deal-creation skill first (getSkill); it decides when a category or a url list replaces this search.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | yes | Free-text description of the inventory being looked for, e.g. "independent cooking blogs with high viewability". |
| `geography` | list of string | no | ISO country codes to restrict the search to, e.g. ["US", "PL"]. |
| `device_type` | list of string | no | Device types to restrict to. Allowed values: "phone", "mobile/tablet", "tablet", "desktop", "set-top-box", "connected tv". |
| `media_subtype` | list of string | no | Ad formats to restrict to. Allowed values: "Display", "Video", "Native". |
| `limit` | integer | no | How many of the most relevant domains to return, 50 by default. total_results still reports the full match count. Default `50`. |

Returns: Up to `limit` matching domains sorted by relevance (descending), the full match count in total_results, and the filters that were ultimately applied.

## deals

### archiveDeal · **mutation**

Archive (delete) a Deal. Its package is archived too, unless another deal still uses it, in which case the package is left alone.

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Deal's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The archived Deal's id. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### createDeal · **mutation**

Create a new Deal. Read the openx-deal-creation skill first (getSkill) for the targeting ids, the format, channel and device compatibility rules, and how to recover from a failed create. If the deal is part of an OpenXDirect campaign build (an order and line items that buy on it), read openx-campaign-launch instead, for the identifier, unit and ordering rules. A Deal is biddable by its participants as soon as it is Active. Pass status="Paused" to create it in a safe state and activate it deliberately with updateDeal once the line items that buy on it are ready. Deals that share targeting share one Package. Create it once with createPackage and pass its id as `package_id` to every createDeal; pass `package` inline only for a one-off deal. An inline package repeats the whole targeting, block lists included, in every call and in the conversation, so a run of many deals built that way stops partway. Format and channel rules, which the API enforces on every package write: with rendering_context.ad_placement BANNER or NATIVE, targeting has no video, instream_content or vtr; with VIDEO, no instream_content; with CTV, no viewability or vtr. With rendering_context.distribution_channel APP, there is no url_targeting and targeting has no content.page_url, content.keywords, technographic.browser or metacategory.keywords; with WEB, no app_inventory.app_bundle_id or app_inventory.appgroup. A package with both url_targeting and app_inventory needs url_targeting.domain_app_inventory_operator: OR when both include, AND when either excludes. metacategory.includes.op is AND or OR, never INTERSECTS.

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | The descriptive name for the Deal. |
| `currency` | string | yes | The currency used in the Deal (e.g. "USD"). |
| `pmp_deal_type` | string | yes | Deal type. Must be set to "3" to operate within Open Auctions. |
| `start_date` | string | yes | The date when the Deal starts (ISO 8601 timestamp). |
| `deal_price` | number | yes | The CPM in the deal currency (not micro-dollars): a floor OpenX may adjust, or the fixed price once fixed_cpm_enabled is set. Ask the user for it, never fill it in: the API would otherwise save 0.01 without telling anyone. 0.01 is OpenX's minimum and is only right when the user asked for the market floor, or for the deal an OpenXDirect line item buys through (the openx-campaign-launch skill passes it; the line item's bid sets the price). |
| `account_id` | string | no | The account to create the Deal under. Defaults to the caller's account when omitted. Accepts the numeric account id or the account uid, from listAccountsForProduct or a searchOptionsByPath "account" result; the caller must have access to that account. The Deal's inline `package` is created under the same account, so do not set a different one there. |
| `package` | object | no | A new Package to create inline, for a one-off deal, with targeting configuration -- see buildPackageTargeting/buildPackageInput. For several deals with the same targeting use `package_id` instead. A CTV package (ad_placement CTV) must target distribution_channel APP or the backend rejects the deal with "When 'ad_placement' is set as CTV, the 'distribution_channel' must be explicitly set to APP"; buildPackageTargeting fills this in when no channel is given. Its targeting must meet the format and channel rules in this tool's description. Provide exactly one of `package` or `package_id`; if neither is given, the Deal is created unassociated with any Package. |
| `package_id` | string | no | An existing Package's id to reuse (e.g. from createPackage), instead of creating a new one inline. The form to use when several deals share targeting: create the package once, then pass its id here for each deal. Provide exactly one of `package` or `package_id`. |
| `deal_id` | string | no | Optional exchange-facing deal code. Normally assigned automatically. |
| `end_date` | string | no | The date when the Deal ends (ISO 8601 timestamp). |
| `deal_participants` | list of object | no | Demand platforms and buyers to bid on this deal. Each entry has demand_partner plus optional buyer_ids and brand_ids lists. The {id: true} map a Deal is read back with is accepted too (so participants copied from getDeal work as they are), and {} means none. |
| `third_party_fees_config` | list of object | no | Revenue share configuration(s) for the deal. |
| `enable_dv360_inventory_package` | boolean | no | Whether this deal will be synced as a DV360 Inventory Package. |
| `agency_salesforce_id` | string | no | Agency salesforce ID. |
| `brand_salesforce_id` | string | no | Brand salesforce ID. |
| `segment_partner_revenue_method` | string | no | Revenue method for multi-partner audiences ("CPM" or "POM"). |
| `status` | string | no | "Active" or "Paused". Omitted or "Active" creates the Deal Active (or Publishing while its package audience is still being exported), biddable as soon as the audience is ready. "Paused" creates it non-biddable until updateDeal sets it Active. |
| `deal_source` | string | no | Who or what originated the Deal. Must be an `id` from optionsByPath(path="deal.deal_source"); currently "Publisher", "Buyer Sourced", "OpenX - Buyer Dev Sourced", "OpenX - DSP Sourced" or "Tech Partner Sourced" (getDealDetails' enum names, such as TECH_PARTNER_SOURCED, are accepted too). Omit it for an OpenXSelect account -- the API derives it from the account's organization type. Required only for a caller with no OpenXSelect account to derive it from; such a caller gets a validation error when it is omitted. |
| `expected_ad_category` | string | no | The Deal's sensitive category. Must be an `id` from optionsByPath(path="deal.custom_pricing_ad_category"), e.g. "Alcohol" or "Gambling (Online)". Only Exchange Package (XP) deals accept a value (pmp_deal_type "3", within Open Auction). |
| `fixed_cpm_enabled` | boolean | no | When false (default), OpenX calculates the final deal floor based on market conditions; when true, deal_price is fixed and sent to DSPs as the floor. |
| `curated_deal_buyer_discount_enabled` | boolean | no | Whether Curated Deal Buyer Discounts apply to this Deal. |
| `pdp_config` | object | no | Configuration for PDP syncing with The Trade Desk. |
| `deal_id_prefix` | string | no | Optional prefix for the deal ID (format: "OX-aaa-"). |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The created Deal with its id, deal_id, name, and other fields. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### createDealForecastingJob · **mutation**

Start an async forecasting job for a prospective Deal configuration, without creating the Deal. This is a dry run -- poll getDealForecastingJob with the returned job_id to check status and retrieve results once the job completes. Part of a deal build: read the openx-deal-creation skill first (getSkill); it says when to forecast and how to read the result.

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `deal` | object | yes | Deal parameters for forecasting, keyed like DealForecastingDealParams (e.g. name, currency, deal_participants, deal_price, pmp_deal_type, start_date, end_date). Similar to createDeal's fields but every field is optional except deal_participants and pmp_deal_type. deal_price may be given as a number; it is sent as the string the API's Decimal type expects. |
| `package` | object | yes | Package (targeting) configuration, keyed like PackageCreateParams -- see buildPackageTargeting/buildPackageInput. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The forecasting job's JSON payload, including its job_id. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### getDeal

Fetch a single Deal by its id, with its package's format targeting: the deal a campaign line item buys on, with its status, flight and format, which a delivery troubleshoot checks against the line item. To find out why a deal underdelivers, where its funnel leaks or what changed, read the openx-deal-troubleshooter skill first (getSkill).

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Deal's numeric id or uid, or its display code (usually OX-..., the value the UI, Slack and a line item's deal_id carry). A display code costs one extra lookup through the deal list, and a code shared by several deals (a grouped deal) is refused with the candidates named, since it does not identify one. The numeric id is what listDeals, searchOptionsByPath and createDeal return. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The Deal. An id or code no deal carries is a not-found error (for a mistyped code it lists the codes that nearly match), and a deal on another instance is a "Wrong instance" error naming the instance_uid to pass. package.targeting.rendering_context carries the format the deal buys: ad_placement.val is BANNER, VIDEO or CTV (a Banner line item needs BANNER, a Video line item VIDEO or CTV), with distribution_channel and device_type alongside. For the package's full targeting (geo, audience, viewability, block lists) call getPackageTargeting(package.id). is_direct_deal is true for a deal another organization owns that you see read-only, as its named buyer or partner. Its package then carries the whole targeting and url_targeting, since getPackageTargeting cannot read that package. A direct deal can't be changed, and the deal analytics tools don't cover it.

### getDealDelivery

Delivery counters for a Deal from the OpenXDirect buyer's side: what your own bidder account requested, bid, won and served on it. Requires OpenXDirect on the account. For a full "why is this line item not delivering" diagnosis read the openx-delivery-troubleshoot skill first (getSkill). To see how a deal delivers as its OpenXSelect seller or curator, use getDealMetricsByDay and the openx-deal-troubleshooter skill instead. A deal is its own delivery grain, so this is the cleanest answer to "is my campaign buying on this deal?". Use it to tell a dead deal from a dead line item, and when comparing two deals. Windows end yesterday: the source is a daily batch.

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Deal's numeric id or uid for one deal's delivery, or its display code (usually OX-...) for the code's total. A display code is not unique: a grouped deal is several deals carrying one code, so the code form sums every deal the caller can read under it. Pass one numeric id to see a single deal behind a shared code. |
| `range` | string | no | "YESTERDAY", "LAST_7_DAYS", "LAST_30_DAYS" (default) or "FULL_FLIGHT" (the deal's own flight to date). Default `"LAST_30_DAYS"`. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: For a numeric id, deal_by_id: the deal's identifying fields plus delivery_metrics shaped like getLineItemDelivery. For a display code, deal_delivery_by_code: the same delivery_metrics shape for the whole code. An id no deal has, or a code no deal carries, is a not-found error. Either way: counters (requests_qualified, non_zero_bids, fills, impressions, clicks, spend, video and viewability), derived rates and the preceding window. spend, cpm and cpc are integer micro-dollars (1 USD = 1,000,000), not dollars -- divide before reporting a figure to a human. Null delivery_metrics means the deal could not be read or FULL_FLIGHT was asked of a deal with no start date.

### getDealForecastingJob

Fetch a Deal Forecasting job by its job_id. Use this to poll for job completion after starting a job with createDealForecastingJob.

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `job_id` | string | yes | The job identifier returned by createDealForecastingJob. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The job's current status and results as JSON.

### listDeals

Page through deals, each carrying the fields you choose. Without `fields`, each deal carries its id, instance_uid, deal_id and name. Pass `fields` to choose what each deal carries instead, e.g. its status or its package's name, across many deals in one call. `delivery_metrics` is your own OpenXDirect buying on the deal (your line items' delivery), not the deal's total, and is null when you have none. For a deal's own totals, select `deal_metrics.*` (or single fields such as `deal_metrics.spend`): its last 7 days to yesterday (spend, impressions and CPM in USD, its current health score, and each figure's change from the week before), as the OpenX UI's deals list shows them. You can filter and sort on those fields by name, so "which recent deals spent over $10k" is one call: `filters=[{"name": "spend", "op": "_gte", "val": ["10000"]}]`, `sort="-spend"` or `"-created_date"`. For one deal's day-by-day figures use getDealMetricsByDay. `is_direct_deal` is true for a deal another account owns that you see as its named buyer or fee partner. It's read-only: don't try to update, pause or archive it, and read its package and targeting from the deal itself, not with getPackage. This tool takes the same filters and sort as searchOptionsByPath(path="deal") and a page costs about the same as that search, but search returns every deal's full record, around 2 KB each. To show a user a list, pass fields (e.g. ["name", "status"]) here for a far smaller response. A delivery_metrics path is the slow case: it looks up each deal's delivery separately, several times slower per page.

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | yes | The number of deals to return. |
| `offset` | integer | yes | The offset from the first deal.. |
| `deal_id` | string | no | Only return Deals exactly matching this exchange-facing deal code, e.g. "OX-bef-abc123" -- not the numeric id; for that, use getDeal. Returns an empty list when no Deals match. |
| `filters` | list of object (name, op, val) | no | Field filters, combined with AND. They take the same fields and operations as searchOptionsByPath(path="deal"). Each filter has exactly the keys "name", "op" and "val", e.g. {"name": "name", "op": "_contains", "val": ["Acme"]}. op is a SearchFilterOp name such as "_eq" or "_gte", never a symbol such as "==" or ">=". val is always a list, even for one value: ["123"], not "123". A field takes at most one filter per operation, and filters never combine with OR: to match any of several exact values use "_in"; to match any of several substrings, search once per substring. is_archived takes "_eq" or "_ne" with "true" or "false"; archived rows are left out unless a filter names it. A filter on a field the Management API does not recognize is ignored, not rejected. |
| `sort` | string | no | Field to sort by, as in searchOptionsByPath(path="deal"); prefix with "-" for descending, e.g. "-created_date". Omit it to keep the default order. |
| `fields` | list of string | no | The Deal fields to return, as dot paths relative to the deal, e.g. ["deal_id", "status", "package.name", "deal_metrics.spend"]. A path ending on an object returns its standard fields ("delivery_metrics"), or its plain fields when it has no standard set ("deal_participants"); "package.*" returns every plain field of the package. Package targeting is not available in a list: read it per package with getPackageTargeting(package.id). id and instance_uid always come back. listEntityFields(entity="deal") lists every path. With fields, limit is at most 200, or 25 when any delivery_metrics path is selected. Rows times selected fields is held to 2,000 values per call. |
| `range` | string | no | The window delivery_metrics covers: "YESTERDAY", "LAST_7_DAYS", "LAST_30_DAYS" (the default) or "FULL_FLIGHT". Only with a delivery_metrics path in fields; refused otherwise. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: {"deals": [...]}, the deals between offset and offset + limit, each with only the fields asked for. When part of a selection fails (delivery_metrics on an account without OpenXDirect, a fee field the account may not read), the deals that came back are returned with an "errors" list saying what failed and where.

### updateDeal · **mutation**

Update an existing Deal. Only the fields you pass are changed; a field left out keeps its value. null clears end_date, agency_salesforce_id, brand_salesforce_id, segment_partner_revenue_method, pdp_config and expected_ad_category. Every other field keeps its current value when sent null (name, start_date, pmp_deal_type, status, deal_participants, third_party_fees_config, package) or is required and rejects it (deal_price, fixed_cpm_enabled, curated_deal_buyer_discount_enabled), so send a value for those. Format and channel rules, which the API enforces on every package write: with rendering_context.ad_placement BANNER or NATIVE, targeting has no video, instream_content or vtr; with VIDEO, no instream_content; with CTV, no viewability or vtr. With rendering_context.distribution_channel APP, there is no url_targeting and targeting has no content.page_url, content.keywords, technographic.browser or metacategory.keywords; with WEB, no app_inventory.app_bundle_id or app_inventory.appgroup. A package with both url_targeting and app_inventory needs url_targeting.domain_app_inventory_operator: OR when both include, AND when either excludes. metacategory.includes.op is AND or OR, never INTERSECTS.

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Deal's id. |
| `name` | string | no | The descriptive name for the Deal. |
| `deal_price` | number | no | Deal price for fixed price deals or deal floor for PMP auction, per mille. |
| `fixed_cpm_enabled` | boolean | no | When false (default), OpenX calculates the final deal floor based on market conditions; when true, deal_price is fixed and sent to DSPs as the floor. |
| `start_date` | string | no | The date when the Deal starts (ISO 8601 timestamp). |
| `end_date` | string | no | The date when the Deal ends (ISO 8601 timestamp). |
| `pmp_deal_type` | string | no | Deal type. Must be set to "3" to operate within Open Auctions. |
| `status` | string | no | "Active" or "Paused". To pause a deal, pass "Paused". |
| `deal_participants` | list of object | no | Demand platforms and buyers to bid on this deal. Each entry has demand_partner plus optional buyer_ids and brand_ids lists. The {id: true} map a Deal is read back with is accepted too (so participants copied from getDeal work as they are), and {} means none. |
| `third_party_fees_config` | list of object | no | Revenue share configuration(s) for the deal. |
| `package` | object | no | An update to the associated Package -- see buildPackageTargeting. There is no package_id argument on update; only a nested Package update is supported. Its targeting follows updatePackage's rules: with rendering_context it replaces the whole targeting; without it, it is a JSON merge patch (pass only the fields to change, null to clear one); left out, it is kept. A targeting from buildPackageTargeting is complete, so it replaces. Read the current document first with getPackageTargeting(package.id). Its targeting must meet the format and channel rules in this tool's description. To remove a field those rules refuse, send it as null where it sits: a targeting field inside package.targeting, e.g. package={"targeting": {"video": null}}, and the domain list as package={"url_targeting": null}; leaving it out keeps it. package.url_targeting is replaced whole, so to set its domain_app_inventory_operator, send it with the rest of the package's current url_targeting from getPackageTargeting. |
| `agency_salesforce_id` | string | no | Agency salesforce ID. |
| `brand_salesforce_id` | string | no | Brand salesforce ID. |
| `segment_partner_revenue_method` | string | no | Revenue method for multi-partner audiences ("CPM" or "POM"). |
| `pdp_config` | object | no | Configuration for PDP syncing with The Trade Desk. |
| `curated_deal_buyer_discount_enabled` | boolean | no | Whether Curated Deal Buyer Discounts apply to this Deal. |
| `expected_ad_category` | string | no | The Deal's sensitive category. Must be an `id` from optionsByPath(path="deal.custom_pricing_ad_category"), e.g. "Alcohol" or "Gambling (Online)". Only Exchange Package (XP) deals accept a value (pmp_deal_type "3", within Open Auction). Read the current value with getDeal first. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The updated Deal. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

## diagnostics

### reportDiagnostics

Record which agent is running a skill and which version of it. Call this once at the start of a skill run, before any other tool; skills list it as their first step. It reads and changes nothing in the account. Every argument is optional: send what you know and leave the rest out.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `model` | string | no | Your own model id as your harness reports it, e.g. "claude-fable-5-1" or "claude-sonnet-5". Leave it out rather than guessing. |
| `context_window` | integer | no | Your context window in tokens, only if your harness tells you. |
| `skill` | string | no | The skill you are following, e.g. "openx-campaign-launch". |
| `skill_version` | string | no | The version in that skill's frontmatter (the header line of the text getSkill returned, or metadata.version of a local copy). |

Returns: `recorded: true`, plus `served_skill_version` when the skill is one this server serves, and `skill_version_matches` when a version was sent. A skill sent under a name it had before gets a note naming its current name and saying to reinstall the local copy.

## entity fields

### listEntityFields

List the field paths a list tool's `fields` argument accepts for one entity, with each field's GraphQL type and description. The description says when a field needs a feature or permission (e.g. that delivery_metrics needs OpenXDirect). Pass a path from here in `fields` on listDeals ("deal"), listPackages ("package"), listOrders ("bidder_order"), listLineItems ("bidder_lineitem"), listCreatives ("bidder_creative"), listAudiences ("audience") or listSegments ("segment"). A path that ends on an object (e.g. "delivery_metrics") selects that object's standard fields, or its plain fields when it has no standard set. Package targeting is not listed: it is read one package at a time with getPackageTargeting.

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `entity` | string | yes | The entity whose fields to list. |
| `prefix` | string | no | Only list paths at or under this one, e.g. "delivery_metrics" or "package"; the full listing for orders and line items runs to about 220 paths. |

Returns: One entry per selectable path: path, type (e.g. "BigInt!", "[String!]") and description. A path that leads back to a type already above it (a line item's order's line items) is listed but not expanded again.

## exports

### getExport

Fetch a single Export by its id.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Export's id (uuid). |

Returns: The Export. An unknown id is a not-found error.

### listExports

List Exports -- the side effect of activating an Audience with an export_type.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | yes | The number of exports to return. |
| `offset` | integer | yes | The offset from the first export. |

Returns: A page of Exports with id, audience_id, status, export_type, and other fields.

### listExportsByAudienceId

List Exports for a given Audience.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | yes | The number of exports to return. |
| `offset` | integer | yes | The offset from the first export. |
| `audience_id` | string | yes | The Audience's id (uuid) to fetch Exports for. The openaudience- prefixed form that package targeting carries is accepted too. |

Returns: A page of Exports belonging to that Audience.

## line items

### activateLineItem · **mutation**

Activate a Paused BidderLineItem. Only Paused line items can be activated. Requires OpenXDirect on the account. Part of a campaign build: read the openx-campaign-launch skill first (getSkill) for the identifier, unit and ordering rules.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The BidderLineItem's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The activated BidderLineItem. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### addLineItemCreatives · **mutation**

Attach one or more BidderCreatives to a BidderLineItem. Creatives must belong to the same account as the line item. Existing associations are not duplicated. Requires OpenXDirect on the account. Part of a campaign build: read the openx-campaign-launch skill first (getSkill) for the identifier, unit and ordering rules.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `line_item_id` | string | yes | The BidderLineItem's id. |
| `creative_ids` | list of string | yes | BidderCreative ids (or uids) to attach. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The updated BidderLineItem. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### archiveLineItem · **mutation**

Archive (soft delete) a BidderLineItem. Requires OpenXDirect on the account.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The BidderLineItem's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The archived BidderLineItem's id. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### createLineItem · **mutation**

Create a new BidderLineItem, the campaign line item that buys on a deal with a budget, a bid and a flight. Requires OpenXDirect on the account. Part of a campaign build: read the openx-campaign-launch skill first (getSkill) for the identifier, unit and ordering rules. Note the asymmetry: end_date is required but start_date is optional. There is no creative_id argument here -- attach creatives via addLineItemCreatives after both the line item and creative(s) exist.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | The line item name. |
| `bidder_order_uid` | string | yes | The parent BidderOrder, as either its numeric id (the value createOrder, getOrder and listOrders return) or its uid. The server resolves either form, so pass the id you already have; a uid cannot be derived from an id. |
| `ad_format` | string | yes | "Banner" or "Video". |
| `end_date` | string | yes | The end date for the line item (ISO 8601 timestamp). Required. |
| `account_id` | string | no | The parent account ID. Defaults to the caller's account when omitted. Accepts either the numeric account ID or the account UID. |
| `deal_id` | string | no | The associated Deal's *deal_id* (the OX exchange display code, e.g. "OX-bef-*") -- NOT Deal.id, the internal numeric id, which is rejected here. The display code is assigned a short while after createDeal; poll getDeal/listDeals for it if the Deal was just created. |
| `start_date` | string | no | The start date for the line item (ISO 8601 timestamp). Optional, unlike end_date. |
| `budget_total` | string | no | The total budget for the line item (string-encoded, e.g. micro-dollars). |
| `budget_daily` | string | no | The daily budget for the line item (string-encoded). |
| `status` | string | no | The initial status: "Active" or "Paused". |
| `region` | string | no | "US", "EU", or "ASIA". |
| `strategy_and_kpi_type` | string | no | One of target_cpm, maximize_impressions, target_cpc, maximize_clicks, target_cpcv, maximize_completed_views, target_cpa, maximize_conversions. target_* pairs with strategy_and_kpi_value (a target cost-per metric); maximize_* maximizes volume within budget and does not use strategy_and_kpi_value. |
| `strategy_and_kpi_value` | string | no | Target cost-per metric (string-encoded micro-dollars), only used with a target_* strategy_and_kpi_type. |
| `max_bid_price` | string | no | Optional max bid price, $0.01-$1,000.00, string-encoded micro-dollars. |
| `pacing_strategy` | string | no | "even" or "asap". |
| `target_type` | string | no | The target constraint type. |
| `target_value` | string | no | The target constraint value. |
| `bid_scheme` | string | no | "fixed" or "dynamic". |
| `frequency_capping` | list of object | no | List of {impressions_limit, time_period_unit, time_period_value}. impressions_limit and time_period_value are integers (a numeric string is also accepted); time_period_unit is "hour", "day" or "week". At most three rules. |
| `programmatic_guaranteed` | boolean | no | Whether this is a programmatic guaranteed line item. |
| `seat_id` | string | no | The seat ID. |
| `daypart_mode` | string | no | Day parting reference frame ("local" or "advertiser"). Only meaningful when daypart_schedule is set. |
| `daypart_timezone` | string | no | A single IANA time zone (e.g. "America/Chicago"). Required whenever daypart_schedule is set. |
| `daypart_schedule` | object | no | Weekly day parting allow grid, e.g. {"Mon": [9, 10, 11]} (hour-of-day ints, 0-23, per weekday key Mon-Sun). Omit for 24/7 delivery. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The created BidderLineItem with its id, name, status, and other fields, and as url its page in OpenXDirect, to show the user. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### getLineItem

Fetch a single BidderLineItem by its id: the campaign line item with its budget, bid, flight, deal, status, delivery status and the reason it is not delivering. The first read when troubleshooting a line item or campaign. Requires OpenXDirect on the account. For a "not delivering" diagnosis read the openx-delivery-troubleshoot skill first (getSkill).

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The BidderLineItem's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The BidderLineItem, and as url its page in OpenXDirect, to show the user. An unknown id is a not-found error, and a line item on another instance is a "Wrong instance" error naming the instance_uid to pass. Budget fields are micro-dollars (1 USD = 1,000,000): divide before showing them to a person.

### getLineItemDealSummary

What a line item needs to know about a deal before linking it, looked up by the exchange deal id (the BidderLineItem.deal_id value, not the Deal's internal id). Requires OpenXDirect on the account. Part of a campaign build: read the openx-campaign-launch skill first (getSkill). Call it before createLineItem or updateLineItem sets deal_id, to pick the right region and to know which knobs the deal will override.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `deal_id` | string | yes | The exchange deal id, e.g. the deal_id field of a Deal from listDeals or the deal_id already set on a line item. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: bidder_line_item_deal_summary, or null when no deal has that id. Fields: programmatic_guaranteed -- true for a Real Time Guaranteed deal, whose line item is programmatic guaranteed with bidding, pacing and dayparting governed by the deal rather than the line item; tracking_enabled -- whether the exchange tracks delivery for the deal, and only then does delivery_region apply; delivery_region -- the region the deal's tracking runs in, which a tracking-enabled deal requires the line item's region to match; managed_by_oa -- true when the deal was created and is managed through this platform (the "oa" is the API's legacy name for it), false for a deal created elsewhere on the exchange and linked here by id.

### getLineItemDelivery

Delivery counters and pacing for a BidderLineItem: is it being asked, bidding, winning and serving. Requires OpenXDirect on the account. For a full "why is this not delivering" diagnosis read the openx-delivery-troubleshoot skill first (getSkill); for a pacing review across an order or account read the openx-pacing-review skill first. Use this before any configuration check when a line item is "not delivering". The counters come from a daily batch, so every window ends yesterday and a line item that started today has no data yet.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The BidderLineItem's id. |
| `range` | string | no | "YESTERDAY", "LAST_7_DAYS", "LAST_30_DAYS" (default) or "FULL_FLIGHT" (the line item's own flight to date). Default `"LAST_30_DAYS"`. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The line item's status fields plus delivery_metrics and delivery_pacing. delivery_metrics.counters holds the funnel: requests_qualified (auctions the deal was offered), non_zero_bids, fills (auctions won), impressions, clicks, spend, video and viewability counts; bid_rate, win_rate, cpm, ctr and cpc are derived from them, and previous holds the same counters for the preceding window. spend, cpm and cpc are integer micro-dollars (1 USD = 1,000,000), not dollars -- divide before reporting a figure to a human. The figures are this line item's own, even when sibling line items buy on the same deal. delivery_pacing compares delivered against the goal scaled to the elapsed flight (vs_pace_pct below zero is behind pace); its goal, delivered and expected are micro-dollars when goal_type is total_spend and an impression count when it is total_impressions. Zero non_zero_bids with requests means the line item is not bidding; bids without fills means it is losing auctions on price.

### getLineItemForecast

Forecast delivery for a BidderLineItem: expected impressions, bid request volume and the CPM band, for a campaign launch or a line item that is not delivering. Requires OpenXDirect on the account. Part of a campaign build: read the openx-campaign-launch skill first (getSkill) for the identifier, unit and ordering rules. When checking whether a line item that is not delivering can deliver at all, read the openx-delivery-troubleshoot skill first. Pass exactly one of line_item_id (a saved BidderLineItem -- its stored targeting is resolved server side) or context_params (a draft under edit, not yet saved). Both entry points produce identical forecaster requests. Forecast values are null when no forecast was possible.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `line_item_id` | string | no | The id of a saved BidderLineItem. Mutually exclusive with context_params. |
| `context_params` | object | no | Draft line-item context, keyed like BidderLineItemForecastContextParams (start_date, end_date, budget_total, target_type, target_value, max_bid_price, strategy_and_kpi_type, strategy_and_kpi_value, frequency_capping, daypart_schedule). Mutually exclusive with line_item_id. |
| `package_targeting` | object | no | The Package targeting document, passed to the forecaster verbatim -- see buildPackageTargeting. |
| `url_targeting` | object | no | The URL targeting document, passed to the forecaster verbatim. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: Viability, available bid request and CPM bands, warnings, unforecasted fields, and forecast metadata (including a request_id to quote when reporting a forecast issue).

### getLineItemsDelivery

Delivery counters and pacing for many BidderLineItems in one call, one row per requested id. Requires OpenXDirect on the account. For a pacing review across an order or account read the openx-pacing-review skill first (getSkill); to move budget from the line items that will not spend theirs to the capped ones, read openx-budget-reallocate. Use this instead of calling getLineItemDelivery once per line item when reviewing a whole order or a page of a list -- one request covers the page. Reach for getLineItemDelivery when looking at a single line item, since it also returns the status fields this one omits. The counters come from a daily batch, so every window ends yesterday and a line item that started today has no data yet.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `ids` | list of string | yes | BidderLineItem ids. At most 100 distinct ids per call -- more is rejected by the API, so page through a longer list. Duplicates collapse to one row. |
| `range` | string | no | "YESTERDAY", "LAST_7_DAYS", "LAST_30_DAYS" (default) or "FULL_FLIGHT" (each line item's own flight to date). Default `"LAST_30_DAYS"`. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: One row per distinct requested id, each holding that id plus metrics and pacing, and as url the line item's page in OpenXDirect, to show the user. An id that resolves to no line item yields a row with all three null and failed_fields empty rather than failing the whole page; failed_fields names any of metrics and pacing that failed to load. Check for nulls before reading a row. metrics and pacing are shaped exactly as in getLineItemDelivery; note spend, cpm and cpc are integer micro-dollars (1 USD = 1,000,000), as are pacing's goal, delivered and expected when goal_type is total_spend.

### listLineItemCreatives

Fetch the BidderCreatives attached to one BidderLineItem: the ads a campaign line item serves, and the first place to look when it is not delivering. Requires OpenXDirect on the account.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `line_item_id` | string | yes | The numeric ID of the BidderLineItem. |
| `limit` | integer | no | The number of creatives to return. |
| `offset` | integer | no | The offset from the first creative. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: A page of the line item's BidderCreatives.

### listLineItems

Page through BidderLineItems, each with its standard fields or the fields you choose. Requires OpenXDirect on the account. This tool takes the same filters and sort as searchOptionsByPath(path="bidder_lineitem") at about the same cost per page, but search returns every line item's full record. To show a user a list, pass fields (e.g. ["name", "status"]) here for a far smaller response; with fields it also reads e.g. the delivery counters of many line items in one call, which looks up each line item's delivery and is slower per page.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | no | The number of line items to return. |
| `offset` | integer | no | The offset from the first line item. |
| `sort` | string | no | Sort expression forwarded to the underlying API, e.g. "-start_date". |
| `delivery_status` | string | no | Filter to a single delivery state: "scheduled", "active", "stalled", "completed", "paused", or "archived". |
| `delivery_status_not_in` | list of string | no | Exclude line items in any of these delivery states (same values as delivery_status). ANDed with delivery_status. Omitted or empty adds no restriction. |
| `order_delivery_status_not_in` | list of string | no | Keep only line items whose parent order is visible and outside these delivery states -- e.g. ["archived", "completed"] to drop line items of finished orders. Omitted or empty adds no restriction. When non-empty the API filters by parent before paging, defaults limit to 10 and offset to 0, and requires limit 1..10000 and offset >= 0. |
| `filters` | list of object (name, op, val) | no | Field filters, combined with AND. They take the same fields and operations as searchOptionsByPath(path="bidder_lineitem"). Each filter has exactly the keys "name", "op" and "val", e.g. {"name": "name", "op": "_contains", "val": ["Acme"]}. op is a SearchFilterOp name such as "_eq" or "_gte", never a symbol such as "==" or ">=". val is always a list, even for one value: ["123"], not "123". A field takes at most one filter per operation, and filters never combine with OR: to match any of several exact values use "_in"; to match any of several substrings, search once per substring. ANDed with the delivery_status arguments. |
| `fields` | list of string | no | The BidderLineItem fields to return, as dot paths relative to the line item, e.g. ["name", "deal_id", "delivery_metrics.counters.impressions"]. A path ending on an object returns its standard fields ("delivery_metrics"), or its plain fields when it has no standard set; "<object>.*" returns every plain field under it. id and instance_uid always come back. listEntityFields(entity="bidder_lineitem") lists every path. With fields, limit is at most 200, or 25 when any delivery_metrics path is selected; omitted, it is that maximum. Rows times selected fields is held to 2,000 values per call. |
| `range` | string | no | The window delivery_metrics covers: "YESTERDAY", "LAST_7_DAYS", "LAST_30_DAYS" (the default) or "FULL_FLIGHT". Only with a delivery_metrics path in fields; refused otherwise. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: {"bidderLineItems": [...]}: without fields each line item carries its standard fields; with fields, only those asked for. When part of a selection fails (delivery_metrics on an account without OpenXDirect), the line items that came back are returned with an "errors" list saying what failed and where. Budget fields are micro-dollars (1 USD = 1,000,000): divide before showing them to a person.

### pauseLineItem · **mutation**

Pause an Active BidderLineItem. Only Active line items can be paused. Requires OpenXDirect on the account. To pause several line items, or everything under an order, read the openx-bulk-change skill first (getSkill): it shows the set with its spend before the first write and reports per line item.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The BidderLineItem's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The paused BidderLineItem. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### removeLineItemCreatives · **mutation**

Detach one or more BidderCreatives from a BidderLineItem. Requires OpenXDirect on the account.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `line_item_id` | string | yes | The BidderLineItem's id. |
| `creative_ids` | list of string | yes | BidderCreative ids (or uids) to detach. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The updated BidderLineItem. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### updateLineItem · **mutation**

Update an existing BidderLineItem. Only the fields you pass are changed; a field left out keeps its value. null clears strategy_and_kpi_value, max_bid_price and daypart_schedule; every other field keeps its current value when sent null, so send a value for it. Requires OpenXDirect on the account. For the same change across several line items (a budget, bid or KPI change over an order) read the openx-bulk-change skill first (getSkill); to move budget between an order's line items read openx-budget-reallocate.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The BidderLineItem's id. |
| `name` | string | no | The line item name. |
| `bidder_order_uid` | string | no | The parent BidderOrder, as either its numeric id or its uid (see createLineItem). |
| `ad_format` | string | no | "Banner" or "Video". |
| `deal_id` | string | no | The associated Deal's *deal_id* display code -- see createLineItem's docstring for the id-vs-deal_id distinction. |
| `start_date` | string | no | The start date (ISO 8601 timestamp). |
| `end_date` | string | no | The end date (ISO 8601 timestamp). |
| `budget_total` | string | no | The total budget (string-encoded). |
| `budget_daily` | string | no | The daily budget (string-encoded). |
| `status` | string | no | "Active" or "Paused" -- prefer pauseLineItem/activateLineItem for lifecycle transitions. |
| `region` | string | no | "US", "EU", or "ASIA". |
| `strategy_and_kpi_type` | string | no | See createLineItem's docstring for the target_*/maximize_* values. |
| `strategy_and_kpi_value` | string | no | Target cost-per metric (string-encoded micro-dollars). |
| `max_bid_price` | string | no | Max bid price, string-encoded micro-dollars. |
| `pacing_strategy` | string | no | "even" or "asap". |
| `target_type` | string | no | The target constraint type. |
| `target_value` | string | no | The target constraint value. |
| `bid_scheme` | string | no | "fixed" or "dynamic". |
| `frequency_capping` | list of object | no | List of {impressions_limit, time_period_unit, time_period_value}. impressions_limit and time_period_value are integers (a numeric string is also accepted); time_period_unit is "hour", "day" or "week". At most three rules. Pass [] to remove every rule. |
| `programmatic_guaranteed` | boolean | no | Whether this is a programmatic guaranteed line item. |
| `seat_id` | string | no | The seat ID. |
| `daypart_mode` | string | no | "local" or "advertiser". |
| `daypart_timezone` | string | no | A single IANA time zone. Required whenever daypart_schedule is set. |
| `daypart_schedule` | object | no | Weekly day parting allow grid. Send an empty dict to clear day parting (24/7 delivery); omit to leave unchanged. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The updated BidderLineItem. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

## normalized definition

### compileAudienceDefinition

Build an Audience's normalized_definition from flat rows. Use it for every definition you pass to createAudience, updateAudience, estimateAudience or the pricing tool, instead of writing the nested JSON yourself. An audience is `includes EXCEPT excludes`. Both are nodes that already exist and OR their children (UNION) unless you declare a node row with that id, parent null and another operator. Add a node row for each AND/OR you need, pointing at its parent, and a criterion row for each set of segments. Rows can be in any order, so add one row at a time as the audience takes shape, and compile and estimate after each step. Example: auto intenders aged 25-34 who are also in my customer list, or any woman; never anyone in two DMAs: nodes: [{"id": "autos", "parent": "includes", "operator": "INTERSECT"}] criteria: [{"node": "autos", "dimension": "predefined", "segment_ids": [<auto ids>]}, {"node": "autos", "dimension": "demographic_age", "segment_ids": [<ages>]}, {"node": "autos", "dimension": "direct", "segment_ids": [<my list>]}, {"node": "includes", "dimension": "demographic_gender", "segment_ids": [<female>]}, {"node": "excludes", "dimension": "location", "segment_ids": [<dmas>]}] Rules the API enforces: - segment_ids are Segment ids (UUIDs). Look up each criterion's ids with listSegmentsByCategory(category=<its dimension>), which explains how to find location and demographic Segments; dimension is the Segment's category. - Non-US segments need the market on their node: region (e.g. "EU") or countries. - The audience form opens two levels: a node under includes/excludes, and nodes under it whose criteria fit in one group. Deeper rows fail with the node named. Check `expression` before estimating: it is how the backend will evaluate the result. The rows mean exactly what they say; the compiler takes care of how the backend combines dimensions. Part of an audience build: read the openx-audience-build skill first (getSkill).

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `criteria` | list of object (dimension, node, operator, segment_ids) | yes | Segment leaves. Each needs node, dimension and segment_ids; operator (UNION by default) says whether any or all of its segments must match. |
| `nodes` | list of object (countries, id, operator, parent, region) | no | AND/OR nodes: id, parent and operator, plus region/countries for a non-US market. Omit when every criterion sits on includes or excludes. |

Returns: normalized_definition to pass on unchanged, the expression it evaluates to, and any warnings.

### explainAudienceDefinition

Turn an existing normalized_definition (from getAudience, listAudiences or a segment search) into the node and criterion rows compileAudienceDefinition takes, plus the expression the backend evaluates it as. To change an audience: explain its normalized_definition, edit the rows, compile them, then pass the result to updateAudience. Node ids are paths such as "includes.0.1". Rows carry segment ids only; match them against the audience's audience_segments for names. The rows follow what the backend does, not what the JSON appears to say. warnings lists every place those differ (for example several predefined/direct segments written as INTERSECT, which the backend ORs), and anything the backend ignores. Part of an audience build: read the openx-audience-build skill first (getSkill).

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `normalized_definition` | object | yes | The definition as stored on an Audience. |

Returns: nodes, criteria, the expression, and warnings.

## options

### listOptionPaths

Return the complete, authoritative catalog of every path `optionsByPath` and `searchOptionsByPath` support: which are options-only vs search-only, required filter arguments for each, and deprecation notes. Call this before guessing a path string -- most path failures are one level off a real path (e.g. guessing "deal.package.targeting.content" instead of its children like "deal.package.targeting.content.adunit_size") or missing a required filter (e.g. "deal.package.targeting.geographic.state" needs filter: {"state": ...}). This relays the live GraphQL schema's own `optionsByPath` field description, so it always matches what the backend actually supports -- it never goes stale independently of this tool's other docstrings.

Products: OpenXDirect, OpenXSelect

_No parameters._

Returns: The full path catalog as descriptive text.

### optionsByPath

Look up valid options for deal fields like demand partners, ad placements, etc. Use it for every enum id a campaign build needs (ad placement, distribution channel, device type, currency, demand partner) instead of guessing; searchOptionsByPath is the one for finding deals, orders, line items, creatives, packages, accounts, audiences and segments. Call listOptionPaths for the complete, authoritative list of supported paths and their required filters -- this is not exhaustive. Most fields take an option's `id`. Instream genre and content rating take its `name`: the allow/block lists of targeting.instream_content.genre and targeting.instream_content.contentrating refuse an id such as "7", so send e.g. {"genre": {"block": ["Comedy"]}, "contentrating": {"block": ["PG-13"]}}. A few lists are too large to return whole: the IAB content categories (deal.package.targeting.domain.categories and deal.package.targeting.domain.categories_iab_v2) run to 70K-100K characters. For those, call searchOptionsByPath with the same path, a name filter and a limit, e.g. path="deal.package.targeting.domain.categories_iab_v2", filters=[{"name": "name", "op": "_contains", "val": ["sports"]}], limit=20.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `path` | string | yes | The options path, e.g. "deal.deal_participants.demand_partner", "deal.package.targeting.rendering_context.ad_placement", "deal.currency". |
| `filter` | object | no | Optional filter to narrow results, e.g. {"state": "cal*"}. Some paths require one -- see listOptionPaths. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: A list of option objects with id, name, path and extra fields.

### searchOptionsByPath

Find deals, orders, line items, creatives, packages, accounts, audiences and segments by name, status, dates or any other field: one lookup returning id, name and the entity's record in `extra`, e.g. "the deal named X", "active orders", "line items ending this month" or "the audience named X". listDeals, listOrders, listLineItems, listCreatives, listPackages, listAudiences and listSegments take these same filters and sort at no more cost per page, plus `fields` to return only the fields you name: to show a user a list of many rows, one of them with e.g. fields=["name", "status"] is a far smaller response than this search's full records. Common shapes: path="deal", filters=[{"name": "name", "op": "_contains", "val": ["Acme"]}] path="deal", filters=[{"name": "deal_id", "op": "_eq", "val": ["OX-bef-abc123"]}] path="bidder_lineitem", filters=[{"name": "status", "op": "_eq", "val": ["Active"]}], sort="-modified_date" path="bidder_order", limit=20 (no filters: the most recent page of orders) path="audience", filters=[{"name": "q", "op": "_eq", "val": ["sports fans"]}] path="segment", filters=[{"name": "q", "op": "_eq", "val": ["auto intenders"]}] Mostly a superset of optionsByPath: every optionsByPath path also works here, returning its list with `limit`, `offset` and filters on `id` or `name` applied to it (total_count is the number of matches; without them, the complete list) -- EXCEPT segment.country, segment.region and segment.data_partner, which this query does not resolve (optionsByPath only; the "segment" entity path below is a different path). Call listOptionPaths for the complete list, including which paths are options-only vs search-only. Entity paths (bidder_order, bidder_lineitem, bidder_creative, deal, package, account, audience, segment) page through the corresponding entity list and support filtering on any searchable field; only the bidder_* paths need OpenXDirect. limit, offset, sort, fields and overload cannot be used as filter names. Except on audience and segment (see below), a filter on a field the backing API does not recognize is ignored, not rejected. On deal and package, archived rows are left out unless a filter names is_archived ("_eq" or "_ne", "true" or "false"), which matches the deleted flag their extra carries. Every deal.package.* path also works without the "deal." prefix, e.g. "package.targeting.content.adunit_size"; each result's path echoes the spelling requested. audience and segment search OpenAudience audiences and segments and differ from the other entity paths: - Each result's id is the audience or segment id; extra carries the owning account as account_id (numeric) and account_uid. - Only these fields can be filtered on; a filter on any other field is rejected with an error. audience: id, account_id, user_id, name, description, status, type, export_type, data_source, direct_audience_provider, region, report_status, error_code, created_with, reach, estimated_reach, addressable_reach, is_archived, is_multi_partner, created_date, updated_date, last_uds_timestamp. segment: id, account_id, parent_segment, lookalike_definition_id, name, full_name, description, external_id, provider_id, category, sub_category, segment_category, segment_sub_category, segment_type, type, sub_type, status, source, segment_source, propensity, segment_group_id, sharing_type, sellable, is_archived, is_leaf, is_nav_only, reach, computed_price_cpm, computed_price_pom, source_matched_count, source_provided_count, created_date, updated_date, expiration_date. - {"name": "q", "op": "_eq", "val": [text]} matches the text anywhere in name or description (audience), or name, full_name, description or external_id (segment). - account_id takes the numeric id or the uid, with _eq, _ne, _in, _notin, _isnull. - Archived rows are left out unless a filter names is_archived. - % and _ in a text match are literal, not wildcards. Matching on name ignores case, and the ordering ops (_gt, _range, ...) do not work on name. - An audience search returns your own account's audiences; a segment search also returns other accounts' public and sellable segments. - They search OpenXSelect data: naming, or being signed in to, an instance other than the OpenXSelect or OpenX corporate instance fails. - total_count is exact. deal.package.targeting.contextual.segments is paged the same way and additionally reports an exact total_count. It filters on the fields of its optionsByPath variant -- account_id, scope, provider_id, q, min_cpm, max_cpm, min_pom, max_pom -- each passed as an "_eq" filter in `filters`, e.g. filters=[{"name": "q", "op": "_eq", "val": ["sports"]}].

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `path` | string | yes | The path selecting what to search, e.g. "bidder_order". |
| `filters` | list of object (name, op, val) | no | Field filters for the search, combined with AND. Each filter has exactly the keys "name", "op" and "val", e.g. {"name": "name", "op": "_contains", "val": ["Acme"]}. op is a SearchFilterOp name such as "_eq" or "_gte", never a symbol such as "==" or ">=". val is always a list, even for one value: ["123"], not "123". A field takes at most one filter per operation, and filters never combine with OR: to match any of several exact values use "_in"; to match any of several substrings, search once per substring. name is the field to filter on (e.g. "name", "status", "start_date"); op is one of "_eq", "_ne", "_contains", "_notcontains", "_startswith", "_endswith", "_in", "_notin", "_gt", "_gte", "_lt", "_lte", "_range", "_notrange", "_isnull"; val values are strings (dates ISO format, booleans "true"/"false") -- "_in"/"_notin" take one or more, "_range"/"_notrange" exactly two, every other op exactly one. Values of "_in", "_notin", "_range" and "_notrange" cannot contain a comma. The text ops (_contains, _notcontains, _startswith, _endswith) work on text fields only; the ordering ops (_gt, _gte, _lt, _lte, _range, _notrange) work on number, date and text fields, not boolean or id fields. |
| `limit` | integer | no | Page size, 20 by default, capped at 500. A deal, order or line item row carries its whole record (about 2K characters), so keep pages small and narrow with filters; page further with offset while has_next_page is true. |
| `offset` | integer | no | Page offset. Defaults to 0. |
| `sort` | string | no | Field to sort by; prefix with "-" for descending, e.g. "-modified_date". Ignored for paths that are not entity searches. audience and segment also take a "+" (ascending) prefix and a "#null_first"/"#null_last" suffix, default to "name", and take "unsorted" to order by id only. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: results (option objects with id/name/path/extra, and for an order, line item, creative or audience a url: its page in OpenXDirect or OpenXSelect, to show the user), total_count (an exact count for the contextual segments, audience and segment paths -- otherwise null, page until has_next_page is false), and has_next_page.

## orders

### activateOrder · **mutation**

Activate a Paused BidderOrder. Only Paused orders can be activated. Requires OpenXDirect on the account. Part of a campaign build: read the openx-campaign-launch skill first (getSkill) for the identifier, unit and ordering rules.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The BidderOrder's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The activated BidderOrder. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### archiveOrder · **mutation**

Archive (soft delete) a BidderOrder. Requires OpenXDirect on the account.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The BidderOrder's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The archived BidderOrder's id. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### createOrder · **mutation**

Create a new BidderOrder, the campaign order that line items sit under, with a flight and a total budget. Requires OpenXDirect on the account. Part of a campaign build: read the openx-campaign-launch skill first (getSkill) for the identifier, unit and ordering rules.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | The order name or label. |
| `start_date` | string | yes | The start date of the order (ISO 8601 timestamp). |
| `end_date` | string | yes | The end date of the order (ISO 8601 timestamp). |
| `budget_total` | integer | yes | The total budget for the order, in the units implied by budget_type: micro-dollars when "total_spend", a count of impressions when "total_impressions". |
| `budget_type` | string | yes | "total_impressions" or "total_spend". |
| `account_id` | string | no | The parent account ID. Defaults to the caller's account when omitted. Accepts either the numeric account ID or the account UID. |
| `status` | string | no | The initial status of the order: "Active" or "Paused". |
| `notes` | string | no | Notes or description for the order. |
| `budget_daily` | integer | no | The daily budget for the order, in the same units as budget_total. |
| `frequency_capping` | list of object | no | List of {impressions_limit, time_period_unit, time_period_value}. impressions_limit and time_period_value are integers (a numeric string is also accepted); time_period_unit is "hour", "day" or "week". At most three rules. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The created BidderOrder with its id, name, status, and other fields, and as url its page in OpenXDirect, to show the user. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### getAdvertisersDelivery

Delivery counters for many advertisers in one call, one row per requested id in request order. An advertiser is the account that owns orders; take ids from listAccountsForProduct. Requires OpenXDirect on the account. Use this for an account-level rollup. For one order or a page of orders use getOrderDelivery/getOrdersDelivery, which also return pacing. The counters come from a daily batch, so every window ends yesterday. For a pacing review across an account read the openx-pacing-review skill first (getSkill).

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `ids` | list of string | yes | Advertiser (account) ids, at most 100 per call; page through a longer list. |
| `range` | string | no | "YESTERDAY", "LAST_7_DAYS" or "LAST_30_DAYS" (default). FULL_FLIGHT is not accepted, since an advertiser has no flight. Default `"LAST_30_DAYS"`. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: One row per requested id. An id that is not one of your advertisers yields a null row rather than failing the call. An advertiser with no delivery reads as zero counters. metrics is shaped as in getOrderDelivery; note spend, cpm and cpc are integer micro-dollars (1 USD = 1,000,000).

### getOrder

Fetch a single BidderOrder by its id: the campaign order that holds line items, with its flight dates, budget, status and delivery status. Read it when a campaign is not delivering, when reviewing pacing, or to check the parent of a line item. Requires OpenXDirect on the account. For a "not delivering" diagnosis read the openx-delivery-troubleshoot skill first (getSkill); for a pacing review read openx-pacing-review.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The BidderOrder's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The BidderOrder, and as url its page in OpenXDirect, to show the user. An unknown id is a not-found error, and an order on another instance is a "Wrong instance" error naming the instance_uid to pass. Budget fields are micro-dollars (1 USD = 1,000,000): divide before showing them to a person.

### getOrderDelivery

Delivery counters and pacing for a BidderOrder, summed over its line items' deals. Requires OpenXDirect on the account. For a full "why is this not delivering" diagnosis read the openx-delivery-troubleshoot skill first (getSkill); for a pacing review across an order or account read the openx-pacing-review skill first, and to move budget between the order's line items read openx-budget-reallocate. Use it to tell an order-wide problem (nothing under the order is being asked or bidding) from a single line item's, and to check the order's pace against its budget. Windows end yesterday: the source is a daily batch.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The BidderOrder's id. |
| `range` | string | no | "YESTERDAY", "LAST_7_DAYS", "LAST_30_DAYS" (default) or "FULL_FLIGHT" (the order's own flight to date). Default `"LAST_30_DAYS"`. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The order's status fields plus delivery_metrics and delivery_pacing, shaped like getLineItemDelivery: counters (requests_qualified, non_zero_bids, fills, impressions, clicks, spend), derived rates and the preceding window, all the order's own. spend, cpm and cpc are integer micro-dollars (1 USD = 1,000,000), and delivery_pacing's goal, delivered and expected are micro-dollars when goal_type is total_spend -- divide before reporting a figure to a human.

### getOrdersDelivery

Delivery counters and pacing for many BidderOrders in one call, one row per requested id. Requires OpenXDirect on the account. For a pacing review across an account read the openx-pacing-review skill first (getSkill). Use this instead of calling getOrderDelivery once per order when reviewing a page of orders -- one request covers the page. Reach for getOrderDelivery when looking at a single order, since it also returns the status fields this one omits. The counters come from a daily batch, so every window ends yesterday.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `ids` | list of string | yes | BidderOrder ids. Duplicates collapse to one row. Keep pages modest (the line-item twin caps at 100 ids) and page through a longer list. |
| `range` | string | no | "YESTERDAY", "LAST_7_DAYS", "LAST_30_DAYS" (default) or "FULL_FLIGHT" (each order's own flight to date). Default `"LAST_30_DAYS"`. |

Returns: One row per distinct requested id, each holding that id plus metrics and pacing. An id that resolves to no order yields a row with both null rather than failing the whole page, so check for nulls before reading a row. metrics and pacing are shaped exactly as in getOrderDelivery; note spend, cpm and cpc are integer micro-dollars (1 USD = 1,000,000), as are pacing's goal, delivered and expected when goal_type is total_spend.

### listOrderLineItems

Fetch the BidderLineItems under one BidderOrder: every line item of a campaign order, for a delivery troubleshoot, a pacing review or a change across the whole order. Requires OpenXDirect on the account. For a pacing review across an order or account read the openx-pacing-review skill first (getSkill); for a change across the order's line items read openx-bulk-change.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `order_id` | string | yes | The numeric ID of the parent BidderOrder. |
| `limit` | integer | no | The number of line items to return. |
| `offset` | integer | no | The offset from the first line item. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: A page of the order's BidderLineItems. Budget fields are micro-dollars (1 USD = 1,000,000): divide before showing them to a person.

### listOrders

Page through BidderOrders, each with its standard fields or the fields you choose. Requires OpenXDirect on the account. This tool takes the same filters and sort as searchOptionsByPath(path="bidder_order") at about the same cost per page, but search returns every order's full record. To show a user a list, pass fields (e.g. ["name", "status"]) here for a far smaller response; with fields it also reads e.g. the delivery counters of many orders in one call, which looks up each order's delivery and is slower per page.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | no | The number of orders to return. |
| `offset` | integer | no | The offset from the first order. |
| `sort` | string | no | Sort expression forwarded to the underlying API, e.g. "-start_date". |
| `delivery_status` | string | no | Filter to a single delivery state: "scheduled", "active", "stalled", "completed", "paused", or "archived". |
| `filters` | list of object (name, op, val) | no | Field filters, combined with AND. They take the same fields and operations as searchOptionsByPath(path="bidder_order"). Each filter has exactly the keys "name", "op" and "val", e.g. {"name": "name", "op": "_contains", "val": ["Acme"]}. op is a SearchFilterOp name such as "_eq" or "_gte", never a symbol such as "==" or ">=". val is always a list, even for one value: ["123"], not "123". A field takes at most one filter per operation, and filters never combine with OR: to match any of several exact values use "_in"; to match any of several substrings, search once per substring. ANDed with delivery_status. |
| `fields` | list of string | no | The BidderOrder fields to return, as dot paths relative to the order, e.g. ["name", "status", "delivery_metrics.counters.impressions"]. A path ending on an object returns its standard fields ("delivery_metrics"), or its plain fields when it has no standard set; "<object>.*" returns every plain field under it. id and instance_uid always come back. listEntityFields(entity="bidder_order") lists every path. With fields, limit is at most 200, or 25 when any delivery_metrics path is selected; omitted, it is that maximum. Rows times selected fields is held to 2,000 values per call. |
| `range` | string | no | The window delivery_metrics covers: "YESTERDAY", "LAST_7_DAYS", "LAST_30_DAYS" (the default) or "FULL_FLIGHT". Only with a delivery_metrics path in fields; refused otherwise. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: {"bidderOrders": [...]}: without fields each order carries its standard fields; with fields, only those asked for. When part of a selection fails (delivery_metrics on an account without OpenXDirect), the orders that came back are returned with an "errors" list saying what failed and where. Budget fields are micro-dollars (1 USD = 1,000,000): divide before showing them to a person.

### pauseOrder · **mutation**

Pause an Active BidderOrder. Only Active orders can be paused. Pausing the order stops delivery of every line item under it in one call and leaves their own statuses untouched; activating it again brings the same ones back. Requires OpenXDirect on the account. To hold spend across an order or pause its line items read the openx-bulk-change skill first (getSkill).

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The BidderOrder's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The paused BidderOrder. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### updateOrder · **mutation**

Update an existing BidderOrder. Only the fields you pass are changed; a field left out keeps its value. No order field can be cleared yet: a field sent as null keeps its current value, so send a value for every field you want changed. Requires OpenXDirect on the account.

Products: OpenXDirect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The BidderOrder's id. |
| `name` | string | no | The order name or label. |
| `start_date` | string | no | The start date of the order (ISO 8601 timestamp). |
| `end_date` | string | no | The end date of the order (ISO 8601 timestamp). |
| `status` | string | no | "Active" or "Paused" -- prefer pauseOrder/activateOrder for lifecycle transitions. |
| `notes` | string | no | Notes or description for the order. |
| `budget_total` | integer | no | The total budget for the order, in the units implied by budget_type: micro-dollars when "total_spend", a count of impressions when "total_impressions". |
| `budget_daily` | integer | no | The daily budget for the order, in the same units as budget_total. |
| `budget_type` | string | no | "total_impressions" or "total_spend". |
| `frequency_capping` | list of object | no | List of {impressions_limit, time_period_unit, time_period_value}. impressions_limit and time_period_value are integers (a numeric string is also accepted); time_period_unit is "hour", "day" or "week". At most three rules. Pass [] to remove every rule. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The updated BidderOrder. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

## packages

### archivePackage · **mutation**

Archive a Package. This is a soft delete -- the Package can be unarchived.

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Package's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The archived Package's id. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### buildPackageInput

Build a Package configuration to be passed as the 'package' argument to createDeal, for a one-off deal. When several deals share targeting, do not build an inline package per deal: create the package once with createPackage and pass its id as createDeal's package_id, otherwise every deal call repeats the whole targeting. Read the openx-deal-creation skill first (getSkill) when the package is for a new deal.

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | no | The name of the Package. |
| `targeting` | object (app_inventory, attention, audience, brand_safety, content, contextual_segment, custom, domain, exclude_non_direct, geographic, include_open_bidding_inventory, instream_content, inter_dimension_operator, inventory_format, inventory_quality, metacategory, rendering_context, retargeting_segment, technographic, video, viewability, vpvh, vtr) | no | Targeting criteria (audience, content, geo, etc). Must include 'inter_dimension_operator' ('AND' or 'OR'). |
| `url_targeting` | object (domain_app_inventory_operator, domain_targeting_option, inventorylist_id, type, urls) | no | URL (domain) allowlist (`type="whitelist"`) or blocklist (`type="blacklist"`) targeting. |
| `notes` | string | no | Any notes about the Package. |
| `cloned_from` | string | no | The ID of a package to clone from. |
| `rate_card_cpm` | number | no | Rate Card Price. |
| `logo` | string | no | Package logo link. |
| `domains` | string | no | Domains or App names. |
| `urls` | list of string | no | Sample URLs. |
| `private_market` | object | no | Private Market Package setup with 'discoverable' ('1' or '0') and optional CPM fields. |

Returns: A dictionary representing the Package, ready to pass as the 'package' argument to createDeal.

### buildPackageTargeting

Build the 'targeting' argument for createPackage/buildPackageInput/updatePackage, covering the mandatory rendering_context block plus Audience/retargeting-segment shortcuts. Every Package requires a fully-formed rendering_context (ad_placement, distribution_channel, and at least one device type) -- use optionsByPath with paths like "deal.package.targeting.rendering_context.ad_placement" to find valid values. CTV rule: when ad_placement is CTV the backend requires distribution_channel to be exactly APP (createPackage/createDeal reject anything else with "When 'ad_placement' is set as CTV, the 'distribution_channel' must be explicitly set to APP"). This tool applies that rule: for CTV it defaults distribution_channel to APP when none is given. Part of a deal build: read the openx-deal-creation skill first (getSkill) for the compatibility rules and the ids each dimension takes.

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `ad_placement_val` | string | yes | Ad placement type id (from optionsByPath "...rendering_context.ad_placement"). |
| `distribution_channel_val` | string | no | Distribution channel id, or comma-delimited ids (from optionsByPath "...rendering_context.distribution_channel"). Required unless ad_placement_val is CTV, where it defaults to APP (the only value the backend accepts). |
| `inter_dimension_operator` | string | no | Whether targeting dimensions must all match ("AND") or any one ("OR"). Default `"AND"`. |
| `device_type_desktop` | string | no | Desktop device id(s), comma-delimited (from optionsByPath "...device_type.desktop_devices"). |
| `device_type_mobile` | string | no | Mobile device id(s), comma-delimited (from optionsByPath "...device_type.mobile_devices"). |
| `device_type_tv` | string | no | TV device id(s), comma-delimited (from optionsByPath "...device_type.tv_devices"). At least one of device_type_desktop/device_type_mobile/device_type_tv must be given. |
| `audience_id` | string | no | An activated Audience's id, to target it via targeting.audience.openaudience_custom; its uuid or the openaudience- prefixed form, either way the prefix is sent once. |
| `retargeting_segment_ids` | list of string | no | Retargeting segment ids to target directly via targeting.retargeting_segment, bypassing Audience entirely. |

Returns: A targeting dict ready to pass to createPackage/buildPackageInput/updatePackage. Every other dimension (content, contextual_segment, custom, domain, geographic, technographic, video, viewability, vtr, brand_safety, metacategory, instream_content, app_inventory, inventory_quality, ...) is typed on those tools' 'targeting' argument -- consult that tool's schema for the shape, then add it as a key on the returned dict.

### createPackage · **mutation**

Create a new, standalone Package: the way to share targeting across Deals. When several deals share targeting (a bulk upload, a set of variants), create the package once here and pass its id as createDeal's package_id for each deal: not an inline `package` per deal, and not one package per deal either, since each repeats the whole targeting in every call. A shared package is the normal setup for deals created together; a deal that later needs its own targeting can get a clone (cloned_from) then. See buildPackageTargeting for building the 'targeting' argument. Read the openx-deal-creation skill first (getSkill) when the package is for a new deal. CTV rule: a package whose rendering_context.ad_placement is CTV must have rendering_context.distribution_channel set to APP, or the backend rejects it with "When 'ad_placement' is set as CTV, the 'distribution_channel' must be explicitly set to APP". buildPackageTargeting applies this for you when no channel is given. Format and channel rules, which the API enforces on every package write: with rendering_context.ad_placement BANNER or NATIVE, targeting has no video, instream_content or vtr; with VIDEO, no instream_content; with CTV, no viewability or vtr. With rendering_context.distribution_channel APP, there is no url_targeting and targeting has no content.page_url, content.keywords, technographic.browser or metacategory.keywords; with WEB, no app_inventory.app_bundle_id or app_inventory.appgroup. A package with both url_targeting and app_inventory needs url_targeting.domain_app_inventory_operator: OR when both include, AND when either excludes. metacategory.includes.op is AND or OR, never INTERSECTS.

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | no | The name of the Package. |
| `cloned_from` | string | no | The ID of a package to clone from. |
| `notes` | string | no | Any notes about the Package. |
| `account_id` | string | no | The account to create the Package under. Defaults to the caller's account when omitted. Accepts the numeric account id or the account uid, from listAccountsForProduct or a searchOptionsByPath "account" result; the caller must have access to that account. |
| `targeting` | object (app_inventory, attention, audience, brand_safety, content, contextual_segment, custom, domain, exclude_non_direct, geographic, include_open_bidding_inventory, instream_content, inter_dimension_operator, inventory_format, inventory_quality, metacategory, rendering_context, retargeting_segment, technographic, video, viewability, vpvh, vtr) | no | Targeting criteria (audience, content, geo, etc) -- see buildPackageTargeting. For a CTV ad placement, distribution_channel must be APP. For a location radius, use geographic.circles_v2, never the legacy geographic.circles. Keywords under metacategory.keywords (includes, excludes) and content.keywords are stored lowercase with hyphens for spaces (pearl-harbor); any other spelling is folded into that before sending. Contextual segments go in contextual_segment, the only place the API reads them from; never add ctx_ custom variables for them. |
| `url_targeting` | object (domain_app_inventory_operator, domain_targeting_option, inventorylist_id, type, urls) | no | URL (domain) allowlist (`type="whitelist"`) or blocklist (`type="blacklist"`) targeting. |
| `rate_card_cpm` | number | no | Rate Card Price. |
| `logo` | string | no | Package logo link. |
| `domains` | string | no | Domains or App names. |
| `urls` | list of string | no | Sample URLs. |
| `private_market` | object | no | Private Market Package setup with 'discoverable' ('1' or '0') and optional CPM fields. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The created Package with its id, uid, name, and other fields. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### getPackage

Fetch a single Package by its id, with its format targeting.

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Package's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The Package. An unknown id is a not-found error, and a package on another instance is a "Wrong instance" error naming the instance_uid to pass. targeting.rendering_context carries ad_placement (BANNER, VIDEO or CTV), distribution_channel and device_type; the rest of the targeting document is not returned here. To see or change the full targeting (geo, audience, viewability, content, block lists) use getPackageTargeting.

### getPackageTargeting

Fetch a Package's full targeting and its URL allow or block list, in the shape updatePackage takes. This is the read for the read, change, patch loop: every field it returns has the same name and shape as updatePackage's `targeting` and `url_targeting` arguments, so to change one thing, read it here, then call updatePackage with only the field you are changing (a targeting without rendering_context is merged into the current one; see updatePackage). Null fields are not set. getPackage returns only the format part of the targeting; the deal targeting tools return the compiled rule tree, which is not an input. Two upstream quirks to know when sending a document back. Never write legacy geographic.circles: the API accepts it, but the package's targeting then can't be read at all. Use geographic.circles_v2 for a location radius (rad in miles, 0.001 to 10), which has the same shape both ways. domain.op and content.categories_inter_dimension_operator exist only on the update input, so they never appear here, and a full replace (a targeting that carries rendering_context) clears them: one more reason to send only the fields that change.

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Package's id. For a deal's package, use the `package.id` getDeal returns. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The package's id, instance_uid, targeting (every dimension: rendering_context, geographic, audience, content, domain, viewability, video, technographic, metacategory, instream_content, app_inventory, brand_safety, contextual_segment, custom, retargeting_segment, and the operators) and url_targeting. Contextual segments are only in contextual_segment: custom never carries the ctx_ variables behind them. An unknown id is a not-found error, and a package on another instance is a "Wrong instance" error naming the instance_uid to pass. Documents can be large when a block list carries many domains. A direct deal's package (is_direct_deal) is not readable here; getDeal returns its whole targeting.

### listPackages

Page through Packages, each carrying its standard fields or the fields you choose. Without `fields`, each package carries its standard fields (name, rate card CPM, domains, URLs, private market settings) but not its targeting; read that with getPackageTargeting. Pass `fields` to choose what each package carries instead. This tool takes the same filters and sort as searchOptionsByPath(path="package") at about the same cost per page, but search returns every package's full record. To show a user a list, pass fields (e.g. ["name"]) here for a far smaller response.

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | yes | The number of Packages to return. |
| `offset` | integer | yes | The offset from the first Package. |
| `retargeting_segment_id` | string | no | Only return Packages that target this retargeting segment id. |
| `filters` | list of object (name, op, val) | no | Field filters, combined with AND. They take the same fields and operations as searchOptionsByPath(path="package"). Each filter has exactly the keys "name", "op" and "val", e.g. {"name": "name", "op": "_contains", "val": ["Acme"]}. op is a SearchFilterOp name such as "_eq" or "_gte", never a symbol such as "==" or ">=". val is always a list, even for one value: ["123"], not "123". A field takes at most one filter per operation, and filters never combine with OR: to match any of several exact values use "_in"; to match any of several substrings, search once per substring. is_archived takes "_eq" or "_ne" with "true" or "false"; archived rows are left out unless a filter names it. A filter on a field the Management API does not recognize is ignored, not rejected. |
| `sort` | string | no | Field to sort by, as in searchOptionsByPath(path="package"); prefix with "-" for descending, e.g. "-created_date". Omit it to keep the default order. |
| `fields` | list of string | no | The Package fields to return, as dot paths relative to the package, e.g. ["name", "rate_card_cpm", "private_market.*"]. A path ending on an object returns its standard fields, or its plain fields when it has no standard set ("url_targeting"); "private_market.*" returns every plain field under it. id and instance_uid always come back. targeting is not available in a list: read it per package with getPackageTargeting. listEntityFields(entity="package") lists every path. With fields, limit is at most 200. Rows times selected fields is held to 2,000 values per call. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: {"packages": [...]}, each with only the fields asked for. When part of a selection fails (a fee field the account may not read), the packages that came back are returned with an "errors" list saying what failed and where.

### updatePackage · **mutation**

Update an existing Package. Only the fields you pass are changed: a value replaces the current one, null clears the field, and a field left out keeps its value. name and targeting cannot be cleared; the API rejects null for them. To remove a field the format and channel rules refuse, send it as null; leaving it out of a partial targeting keeps it. url_targeting is replaced whole, so to set its domain_app_inventory_operator, send it with the rest of the package's current url_targeting from getPackageTargeting. Format and channel rules, which the API enforces on every package write: with rendering_context.ad_placement BANNER or NATIVE, targeting has no video, instream_content or vtr; with VIDEO, no instream_content; with CTV, no viewability or vtr. With rendering_context.distribution_channel APP, there is no url_targeting and targeting has no content.page_url, content.keywords, technographic.browser or metacategory.keywords; with WEB, no app_inventory.app_bundle_id or app_inventory.appgroup. A package with both url_targeting and app_inventory needs url_targeting.domain_app_inventory_operator: OR when both include, AND when either excludes. metacategory.includes.op is AND or OR, never INTERSECTS.

Products: OpenXDirect, OpenXSelect, OpenXControl

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Package's id. |
| `name` | string | no | The name of the Package. |
| `notes` | string | no | Any notes about the Package. |
| `targeting` | object (app_inventory, attention, audience, brand_safety, content, contextual_segment, custom, domain, exclude_non_direct, geographic, include_open_bidding_inventory, instream_content, inter_dimension_operator, inventory_format, inventory_quality, metacategory, rendering_context, retargeting_segment, technographic, video, viewability, vpvh, vtr) | no | Targeting criteria. Read the current document first with getPackageTargeting, then send only what changes. Two forms: with rendering_context it is complete and replaces the package's whole targeting, as before; without rendering_context it is partial and is applied to the current targeting as a JSON merge patch (objects merge, a value you pass replaces the current one, a field you pass as null is cleared, anything you leave out is kept). So to change one field, pass only that field; to swap a field for a sibling (region for country, say), pass the old one as null alongside the new one, or the old one stays in force. buildPackageTargeting builds a complete targeting (it always sets rendering_context), so use it only to replace the whole targeting; for a partial change, pass just the fields to change. Leave targeting out to change other fields without touching it. For a location radius, use geographic.circles_v2, never the legacy geographic.circles. Keywords under metacategory.keywords (includes, excludes) and content.keywords are stored lowercase with hyphens for spaces (pearl-harbor); any other spelling is folded into that before sending. Contextual segments go in contextual_segment, the only place the API reads them from; never add ctx_ custom variables for them. |
| `url_targeting` | object (domain_app_inventory_operator, domain_targeting_option, inventorylist_id, type, urls) | no | URL (domain) allowlist (`type="whitelist"`) or blocklist (`type="blacklist"`) targeting. Replaces the current list when passed, on its own or with other fields; left out, the list is kept. |
| `rate_card_cpm` | number | no | Rate Card Price. |
| `logo` | string | no | Package logo link. |
| `domains` | string | no | Domains or App names. |
| `urls` | list of string | no | Sample URLs. |
| `private_market` | object | no | Private Market Package setup. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The updated Package. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

## pixels

### archivePixel · **mutation**

Archive a Pixel.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Pixel's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The archived Pixel's id. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### createPixel · **mutation**

Create a new Pixel, the site tag that records one standard event. Its id is minted by the server and goes into the tag URL. Retargeting segments are built from Pixels: pass the new id as pixel_id in createRetargetingSegment's clauses.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | The Pixel's display name. It can be renamed later without redeploying the tag. |
| `event_type` | string | yes | The standard event the tag records, one of SignalEventType's short codes (api, atc, atw, cp, creg, ct, dn, fl, ic, ld, p, pv, s, sa, sch, st, sub, vc). Write-once: it cannot be changed after create, so a different event needs a new Pixel. |
| `account_id` | string | no | The account to create the Pixel under. Defaults to the caller's account when omitted. Use an id from listAccountsForProduct or a searchOptionsByPath "account" result. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The created Pixel with its id, account_id, name, event_type, and timestamps. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### getPixel

Fetch a single Pixel by its id.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Pixel's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The Pixel. An unknown id is a not-found error; pass instance_uid when the pixel lives on another instance.

### listPixels

List Pixels, the site tags an advertiser places to record events such as a page view or an add-to-cart.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | yes | The number of pixels to return. |
| `offset` | integer | yes | The offset from the first pixel. |
| `account_id` | string | no | Filter by the id of the Account the Pixels belong to. |
| `event_type` | string | no | Filter by event type, one of SignalEventType's short codes (api, atc, atw, cp, creg, ct, dn, fl, ic, ld, p, pv, s, sa, sch, st, sub, vc). |
| `sort` | string | no | Sort the results by a field name, e.g. "created_date". |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: A page of Pixels with id, account_id, name, event_type, and timestamps.

### updatePixel · **mutation**

Rename a Pixel. The name is the only field that can change; event_type is fixed at create, and the tag on the site keeps working after a rename.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Pixel's id. |
| `name` | string | yes | The new display name. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The updated Pixel. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

## platform

### getProvider

Fetch a single Provider by its id.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Provider's id. |

Returns: The Provider. An unknown id is a not-found error.

### listAccountsForProduct

List the accounts you can use for OpenXSelect ("SELECT": deals and packages) or OpenXDirect ("DIRECT": orders, line items and creatives), each with the instance it lives on. Call it before creating anything for either product: pass a row's id as account_id and its instance_uid as instance_uid on every create. You see your own account and every account under it; an OpenX administrator sees all of them. An empty list means you are not set up for that product. For any other account, use searchOptionsByPath with path "account" on the instance you want to work in.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `product` | string | yes | "SELECT" or "DIRECT". |
| `name_contains` | string | no | Only accounts whose name contains this text, case-insensitively. |
| `limit` | integer | no | The number of accounts to return. Defaults to 50. |
| `offset` | integer | no | The offset from the first account. |

Returns: Accounts sorted by name, each with id (the numeric account id), name, currency (null when none is configured) and instance_uid.

### listProviders

List Providers -- the data partners referenced by Segment.provider_id.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | yes | The number of providers to return. |
| `offset` | integer | yes | The offset from the first provider. |

Returns: A page of Providers with id, name, and allowed_export_types.

### ping

Check whether the upstream OpenX API is reachable, independent of this MCP server's own health check.

Products: OpenXDirect, OpenXSelect

_No parameters._

Returns: The literal string "pong" on success.

## retargeting

### archiveRetargetingSegment · **mutation**

Archive a management retargeting segment.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The RoutedSegment's id. |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The archived RoutedSegment's id. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### countRoutedSegments

Fetch the count of all routed Segments (predefined or retargeting).

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `type_full` | string | no | Explicitly select a source: "segment_predefined" or "segment_retargeting". |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The count of RoutedSegments.

### countRoutedSegmentsByCategory

Fetch the count of routed Segments (predefined or retargeting) belonging to a given category.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `category` | string | yes | The Segment category to filter by. |
| `type_full` | string | no | Explicitly select a source: "segment_predefined" or "segment_retargeting". |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The count of RoutedSegments in that category.

### createRetargetingSegment · **mutation**

Create a new retargeting segment -- the only kind of segment this API can create (predefined/provider-sourced Segments are read-only; see listSegments). Reference the result's id from Package.targeting.retargeting_segment (see buildPackageTargeting's retargeting_segment_ids argument) to target it directly, bypassing Audience entirely. A segment is built from Named Pixels: each clause names a Pixel on the segment's account and an event. Find the account's pixels with listPixels, or create one with createPixel.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `include_any` | list of object | yes | Clauses that qualify a user for this segment; matching any one is enough. Each is {pixel_id, event_type?, lookback ("P1D"\|"P7D"\|"P14D"\|"P28D"), match_scope? ("direct"\|"expanded")}. pixel_id is a live Pixel on the segment's account. event_type is one of SignalEventType's short codes and defaults to the pixel's own event; a different value targets a different audience. getRetargetingSegment reads clauses back in this same shape. |
| `disposition` | string | yes | "target" (segment defines who to reach) or "suppress" (segment defines who to exclude). |
| `exclude_any` | list of object | no | Clauses that disqualify a user from this segment, same shape as include_any. |
| `account_id` | string | no | The account to create the segment under. Defaults to the caller's account when omitted. Accepts the numeric account id or the account uid, from listAccountsForProduct or a searchOptionsByPath "account" result; the caller must have access to that account. |
| `name` | string | no | The segment name or label. |
| `activation_threshold` | integer | no | Minimum matched-user count before the segment activates. |
| `start_date` | string | no | The date when the segment starts (ISO 8601 timestamp). |
| `end_date` | string | no | The date when the segment ends (ISO 8601 timestamp). |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The created RetargetingSegment with its id, disposition, signals, and other fields. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

### getRetargetingSegment

Fetch a single routed Segment by its id. UUID values resolve through the legacy predefined path when type_full is omitted.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The RoutedSegment's id. |
| `type_full` | string | no | Explicitly select a source: "segment_predefined" or "segment_retargeting". |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The RoutedSegment. An unknown id is a not-found error; pass instance_uid when the segment lives on another instance.

### listRetargetingSegments

List routed Segments (predefined or retargeting). Omitting type_full preserves the upstream default source selection.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | yes | The number of segments to return. |
| `offset` | integer | yes | The offset from the first segment. |
| `type_full` | string | no | Explicitly select a source: "segment_predefined" or "segment_retargeting". |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: A page of RoutedSegments (PredefinedSegment or RetargetingSegment).

### listRoutedSegmentsByCategory

List routed Segments (predefined or retargeting) belonging to a given category.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | yes | The number of segments to return. |
| `offset` | integer | yes | The offset from the first segment. |
| `category` | string | yes | The Segment category to filter by. |
| `type_full` | string | no | Explicitly select a source: "segment_predefined" or "segment_retargeting". |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: A page of RoutedSegments in that category.

### listRoutedSegmentsByCountry

List routed Segments (predefined or retargeting) belonging to a given country.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | yes | The number of segments to return. |
| `offset` | integer | yes | The offset from the first segment. |
| `country` | string | yes | The country code to filter by. Must match the `id` field returned from `optionsByPath(path="segment.country")`. |
| `type_full` | string | no | Explicitly select a source: "segment_predefined" or "segment_retargeting". |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: A page of RoutedSegments in that country.

### listRoutedSegmentsByRegion

List routed Segments (predefined or retargeting) belonging to a given region. Includes Segments that have the region directly set, as well as Segments that have a country belonging to the region.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | yes | The number of segments to return. |
| `offset` | integer | yes | The offset from the first segment. |
| `region` | string | yes | The region code to filter by. Must match the `id` field returned from `optionsByPath(path="segment.region")`. |
| `type_full` | string | no | Explicitly select a source: "segment_predefined" or "segment_retargeting". |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: A page of RoutedSegments in that region.

### updateRetargetingSegment · **mutation**

Update an existing retargeting segment. Only the fields you pass are changed: a value replaces the current one, null clears the field, and a field left out keeps its value. The API rejects null for include_any, disposition and status, so those cannot be cleared. The schema's signals input requires include_any whenever signals are touched at all, so include_any and exclude_any always replace the *whole* signals object together -- pass include_any (with exclude_any if needed) to change either; passing exclude_any alone raises, since there's no schema-safe way to change just the exclude list without restating include_any.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The RoutedSegment's id. |
| `name` | string | no | The segment name or label. |
| `include_any` | list of object | no | Clauses that qualify a user, same shape as createRetargetingSegment. Required if exclude_any is given. To keep a clause the segment already has, send it back as getRetargetingSegment returns it. A clause read back with a null pixel_id predates Named Pixels and can't be sent back; leave include_any and exclude_any out to keep such a segment's clauses. |
| `exclude_any` | list of object | no | Clauses that disqualify a user, same shape as include_any. |
| `disposition` | string | no | "target" or "suppress". |
| `status` | string | no | "pending", "active", or "deleted". |
| `activation_threshold` | integer | no | Minimum matched-user count before the segment activates. |
| `start_date` | string | no | The date when the segment starts (ISO 8601 timestamp). |
| `end_date` | string | no | The date when the segment ends (ISO 8601 timestamp). |
| `instance_uid` | string | no | The OpenX instance to operate in. Defaults to the instance your credential authenticated against; pass it only to work in a different one. Any id argument must come from that same instance. |

Returns: The updated RetargetingSegment. Before calling this, tell the user exactly what will change and wait for their yes, unless they have said to go ahead without checking.

## segments

### countSegments

Fetch the count of all available Segments.

Products: OpenXDirect, OpenXSelect

_No parameters._

Returns: The count of Segments.

### countSegmentsByCategory

Fetch the count of Segments belonging to a given category.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `category` | string | yes | The Segment category to filter by. |
| `sub_category` | string | no | Only Segments with this sub-category, as for listSegmentsByCategory. |
| `search` | string | no | Only Segments whose name or description contains this text. |
| `names` | list of string | no | Only Segments whose name is exactly one of these. |

Returns: The count of Segments in that category.

### getSegment

Fetch a single Segment by its id.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | The Segment's id (uuid). |

Returns: The Segment. An unknown id is a not-found error.

### listSegments

List predefined (provider-sourced) Segments. Segments are read-only here -- reference them from an Audience's normalized_definition by their `id`, under the dimension named by their `category` (see compileAudienceDefinition). To find a segment by name, external id, provider or any other field, use searchOptionsByPath(path="segment", filters=[...]) instead of paging this list; this tool takes the same filters and sort when you need more than id and name. It lists leaf segments only, so a filter on is_leaf other than true returns nothing. Part of an audience build: read the openx-audience-build skill first (getSkill).

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | yes | The number of segments to return. |
| `offset` | integer | yes | The offset from the first segment. |
| `filters` | list of object (name, op, val) | no | Field filters, combined with AND. They take the same fields and operations as searchOptionsByPath(path="segment"). Each filter has exactly the keys "name", "op" and "val", e.g. {"name": "name", "op": "_contains", "val": ["Acme"]}. op is a SearchFilterOp name such as "_eq" or "_gte", never a symbol such as "==" or ">=". val is always a list, even for one value: ["123"], not "123". A field takes at most one filter per operation, and filters never combine with OR: to match any of several exact values use "_in"; to match any of several substrings, search once per substring. A filter on a field outside that list is refused. |
| `sort` | string | no | Field to sort by, as in searchOptionsByPath(path="segment"); prefix with "-" for descending, e.g. "-created_date". Omit it to keep the default order. |
| `fields` | list of string | no | The Segment fields to return, as dot paths relative to the segment, e.g. ["name", "external_id", "category", "provider.name"]. "<object>.*" returns every plain field under an object. id always comes back. listEntityFields(entity="segment") lists every path. With fields, limit is at most 200. Rows times selected fields is held to 2,000 values per call. |

Returns: {"segments": [...]}: without fields each has id, external_id, name, category and its other standard fields; with fields, only those asked for. When part of a selection fails, the segments that came back are returned with an "errors" list saying what failed and where.

### listSegmentsByCategory

List Segments in a category, optionally narrowed by sub_category, a name/description search, or exact names. The category is the audience-definition dimension: pass the ids you choose as `segment_ids` in a compileAudienceDefinition criterion whose dimension is this category. Location and demographic Segments describe the people in an audience, not where an ad is shown. A location Segment holds users seen in that place over the past 90 days, and a demographic Segment holds users thought to be of that age or gender. Both differ from geographic targeting on a package or line item, which matches the current location of each ad request (from its IP address and similar signals). For "people in Texas", use the Texas location Segment; for "ads shown in Texas", use geographic targeting (buildPackageTargeting). For location and demographics, use the Segments listed here, the ones the audience form offers, rather than similar-sounding Segments found by a name or prompt search: - location: sub_category "state", "dma", "congressional" or "zip". States go by full name ("Texas", "New York"), DMAs by market name, ZIPs by code. Use `names` for exact matches, several at once, or `search` for part of a name. - demographic_age: one Segment per year of age, 19-99, named by the age. A range is every year in it, e.g. names "25" through "34". - demographic_gender: two Segments, "Male" and "Female". - predefined, direct: `search` by name or description. - lookalike: list them. Part of an audience build: read the openx-audience-build skill first (getSkill).

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | yes | The number of segments to return. |
| `offset` | integer | yes | The offset from the first segment. |
| `category` | string | yes | The Segment category (the audience-definition dimension). |
| `sub_category` | string | no | Only Segments with this sub-category (for location: state, dma, congressional or zip). |
| `search` | string | no | Only Segments whose name or description contains this text. |
| `names` | list of string | no | Only Segments whose name is exactly one of these. |

Returns: A page of Segments in that category.

### listSegmentsByCountry

List Segments belonging to a given country.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | yes | The number of segments to return. |
| `offset` | integer | yes | The offset from the first segment. |
| `country` | string | yes | The country code to filter by. Must match the `id` field returned from `optionsByPath(path="segment.country")`. |

Returns: A page of Segments in that country.

### listSegmentsByRegion

List Segments belonging to a given region. Includes Segments that have the region directly set, as well as Segments that have a country belonging to the region.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | yes | The number of segments to return. |
| `offset` | integer | yes | The offset from the first segment. |
| `region` | string | yes | The region code to filter by. Must match the `id` field returned from `optionsByPath(path="segment.region")`. |

Returns: A page of Segments in that region.

## skills

### getSkill

Return the full text of a skill: the playbook body followed by its reference tables. Read it before starting the job it covers and follow its steps and rules.

Products: OpenXDirect, OpenXSelect

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | The skill's name as listed by listSkills, e.g. "openx-campaign-launch" or "openx-delivery-troubleshoot". |

Returns: The skill as markdown: a header line with the skill's name and version, the playbook, then the references under their own headings.

### listSkills

List the skills this server serves: step-by-step playbooks for multi-step jobs such as launching a campaign or diagnosing a line item that is not delivering. Call this at the start of any task that spans several tools, then read the matching skill with getSkill and follow it. Nothing needs to be installed on the user's machine; the skill text comes back from the server. The first entry, openx-connection-guide, holds the rules for every call; read it before your first.

Products: OpenXDirect, OpenXSelect

_No parameters._

Returns: One entry per skill with its name, its version and a one-line description of when to use it, the connection guide first. Skills: openx-connection-guide (OpenX connection guide, read first), openx-audience-build (Build an audience), openx-budget-reallocate (Reallocate budget), openx-bulk-change (Change line items in bulk), openx-campaign-launch (Launch a campaign), openx-deal-creation (Create a deal), openx-deal-troubleshooter (Troubleshoot a deal), openx-delivery-troubleshoot (Diagnose a line item), openx-pacing-review (Review pacing).
