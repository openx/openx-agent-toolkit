# Summary formats

## Standard summary

Before Step 6, open with one friendly line ("The name is available and everything's ready to go."),
or explain a problem in plain words instead of the table. Then show a two-column table
(`Setting | What I'll use`) with these rows, in this order. Never drop a row; write "None" when a
value is empty.

| Setting | What to show |
|---|---|
| Account | Account name, plus the environment in brackets when it is not production |
| Name | The deal name |
| Dates | Concrete start date with the user's phrase in brackets (e.g. "30 Sep 2026 (tomorrow)"), and the end date or "No end date". Show the local time too when the start is today or tomorrow. |
| Currency | e.g. "USD (standard)" when the user did not choose it |
| Price | The CPM, and floor (OpenX may adjust it) or fixed. There is always one: it comes from the user, never from a default |
| Buyer (DSP) | Plain name without "- RTB" or ids, plus "any seat" or the named seats, for every DSP. DV360 always shows its one buyer, never "any seat". |
| Format | Banner / Native / Video / CTV |
| Devices | Everyday names, e.g. "Computers, phones and tablets", "Smart TVs and TV boxes" |
| Where ads run | "Apps", "Websites" or "Apps and websites" |
| Location and other targeting | Plain names (cities with country), sites, apps, audiences, or "None (all locations)" |
| Quality targets | Viewability / VTR in plain words, or "None". Only when the format allows them. |
| Inventory exclusions | Always "MFA inventory excluded (standard)", plus the below-average quality answer when Step 1 allows it |
| Deal type | "Exchange Package (XP)", plus "fixed price" when set |
| Status | "**Paused**: nothing runs until you switch it on" (or "Live" if the user asked) |

Mark values filled in automatically with "(standard)". If the format does not allow quality
targets, say so in one plain sentence below the table. End with one friendly question asking
whether to go ahead, naming the optional things not yet set (end date, location).

## Example

> The name is available and everything's ready to go. Here's what I'll set up:
>
> | Setting | What I'll use |
> |---|---|
> | Account | Example Media |
> | Name | Example CTV test |
> | Dates | Starts 30 Sep 2026 (tomorrow), no end date |
> | Currency | USD (standard) |
> | Price | 2.50 CPM floor (OpenX may adjust it) |
> | Buyer (DSP) | The Trade Desk, any seat |
> | Format | CTV |
> | Devices | Smart TVs and TV boxes (standard for CTV) |
> | Where ads run | Apps (standard for CTV) |
> | Location and other targeting | None (all locations) |
> | Inventory exclusions | MFA inventory excluded (standard) |
> | Deal type | Exchange Package (XP) |
> | Status | **Paused**: nothing runs until you switch it on |
>
> CTV deals can't have a VTR or viewability target, so there's none on this one. MFA ("made for
> advertising") inventory is left out by default, as on every deal.
>
> Shall I go ahead and create it? If you like, you can first add an end date or a location.

## Precise summary

When the user asks what exactly is targeted, the plain-language rule relaxes: name the OpenX
targeting dimension, the value and category ids. Still keep tool names, raw JSON and internal deal
and package ids out. Use the standard table with these changes:

| Setting | What to show |
|---|---|
| Dates | Exact start and end with time and time zone, e.g. "5 Oct 2026, 00:00 UTC (Monday) to 5 Nov 2026, 23:59 UTC" |
| Price | The CPM, and floor (OpenX may adjust it) vs fixed |
| Buyer (DSP) | Add "(no buyer or brand restrictions)" when no seats are set |
| Format | "Ad placement: Banner" |
| Devices | "Device type: Mobile, meaning Smart Phone and Tablet (no desktop, no TV)" |
| Where ads run | "Distribution channel: App and Web" |
| Location | "Geography, include: Country = Poland" |
| Content category | Its own row: "Domain categories (IAB v2), includes any of: Humor and Satire (ID 440)" |
| Quality targets | Name what is absent and why, e.g. "Viewability: none (VTR isn't available for banner)" |
| Targeting logic | New row: "All of the above must match together (AND between dimensions)" |
| Deal type | "Exchange Package (XP), floor price (not fixed)" |

Above the table, explain any less obvious setting in two or three sentences: where it sits in the
targeting (e.g. "Domain → Categories (IAB v2)"), its id and parent, the match rule and what it
covers. Below it, say you will check the compiled targeting after creation.
