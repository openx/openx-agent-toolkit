# From a persona brief to rows

Agency briefs describe audiences as personas: an archetype with demographics, a life stage, an
occupation, interests and a trigger. This file shows how each part maps onto dimensions and rows,
using two personas from an apparel-subscription RFP. Look up every id; none are given here.

## The mapping

| In the brief | Dimension and how to find it |
|---|---|
| Gender, age range ("women 25-54") | `demographic_gender` + `demographic_age` (one id per year), by exact `names` |
| Where they live ("suburban Columbus, Ohio") | `location`: the Columbus DMA segment (search "Columbus") or the `Ohio` state segment. If the brief means where ads show, that is the deal's geo targeting instead |
| Life stage ("married with kids", "new parent", "empty nester") | `predefined`: search "parents with kids at home", "new parent", "empty nesters" |
| Occupation ("teacher", "sales professional") | `predefined` occupation segments: "Occupation: Teacher/Educator", "Occupation Group: Sales" |
| Interests ("fashion", "sports", "gaming") | `predefined` browsing and propensity segments; `direct` partner segments when the brief names a partner or OpenX has nothing close |
| Purchase behaviour ("shops apparel online") | `predefined` purchase propensity ("Clothing & Fashion Retailers: Likely Purchaser", "TRX: Apparel Dollar: High") |
| Competitor conquesting ("shops at brand X") | `predefined` brand propensity ("<Brand>: Likely Purchaser"), one per competitor, in one criterion |
| Household income ("HHI $50K+") | income segments if a search finds them; say so if not |
| Triggers ("job searching", "back to school") | one search per trigger; keep by relevance. Health triggers (weight loss, pregnancy, medication) are sensitive: name the segment and get a yes before using it |
| First-party states ("active client", "lapsed client") | no tool; say so |
| Exclusions ("not current customers") | criteria on `excludes` |

## Persona 1: the busy suburban mother

Brief: women 25-54, married with school-age kids, teacher or office professional, fashion and
beauty interests, value-sensitive.

Searches, each with the search mode filter set to `OPENX_PROPRIETARY`:

1. `"parents with school-age kids at home"`
2. `"teachers and office professionals"`
3. `"women who shop for clothing and fashion"`

Rows for "a woman 25-54 who is a parent OR a teacher OR a fashion shopper":

```
nodes:    [{"id": "mother", "parent": "includes", "operator": "INTERSECT"},
           {"id": "mother.any", "parent": "mother", "operator": "UNION"}]
criteria: [{"node": "mother", "dimension": "demographic_gender", "segment_ids": [<Female>]},
           {"node": "mother", "dimension": "demographic_age", "segment_ids": [<25 ... 54>]},
           {"node": "mother.any", "dimension": "predefined", "segment_ids": [<parent, occupation, fashion ids>]}]
```

If the brief means "a parent AND a fashion shopper", put each in its own criterion on `mother`
with no UNION child, and check that `expression` reads `... AND predefined:{parent} AND
predefined:{fashion}`. Say which reading you used.

## Persona 2: the time-poor father

Brief: men 25-54, kids at home, sales professional, sports, gaming and tech interests, buys
complete outfits.

Same shape with `Male`. Partner rows such as Datonics "Sports" or Digiseg "Consumer Electronics"
show up in the same searches: offer them with their price, and when the user wants them add a
`direct` criterion on the UNION child next to the `predefined` one, so they widen the persona
rather than narrow it.

## Both personas in one audience

Two INTERSECT nodes under `includes`: the audience is anyone matching either. Estimate the whole
audience, and also each persona alone, so the user sees which one carries the reach.

## Reporting back to a planner

Planners think in reach, CPM and overlap. Give them:

- the OAID estimate per persona and combined
- for each segment: name, OpenX or partner, CPM, and the search's relevance
- the audience's total price from the pricing tool
- the parts of the brief with no segment (first-party states, income if missing, ad geography)
- that publishing takes about a day
