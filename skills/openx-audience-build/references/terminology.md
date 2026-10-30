# Terminology

Use these meanings when reading tool output and when talking to the user.

| Term | Here it means |
|---|---|
| **Segment** | A named set of people from one source: "Avid Runners: High", age "27", "Texas". Read only; you combine segments, you do not edit them. |
| **Dimension** | The kind of segment: age, gender, location, predefined, direct, lookalike. The Segment's `category`. |
| **OpenX segment (`predefined`)** | OpenX's own catalogue: interests, browsing, purchase propensity, occupation, life stage. Free. |
| **Partner segment (`direct`)** | A data partner's segment (Epsilon, Stirista, Webbula ...). Priced. `sellable: false` means this account cannot buy it. |
| **Location segment** | People seen in a place over the past 90 days. Not the same as geo targeting, which uses where each ad request comes from. |
| **Lookalike** | People similar to a seed list. Existing ones can be used; new ones cannot be built through these tools. |
| **Retargeting segment** | Visitors to the account's own Named Pixels. A separate flow. |
| **Audience** | A saved combination of segments: `includes EXCEPT excludes`. What this skill creates. |
| **Definition (`normalized_definition`)** | The audience's stored JSON. Built by compileAudienceDefinition from rows, read back into rows by explainAudienceDefinition. |
| **Node / criterion** | The rows compileAudienceDefinition takes. A node is an AND or OR; a criterion is a set of segments of one dimension on a node. |
| **Expression** | The definition written as a formula, the way the backend evaluates it. Read it back to the user before estimating. |
| **Estimate** | A dry run: how many ids of each type the audience would have, nothing created. |
| **OAID** | OpenX's person-level id. The estimate's headline number. |
| **Id types / export targets** | The id spaces an audience is exported into: `cookie`, `device` (mobile ad ids), `idl` (RampID), `id5`, `ctv`, `ip`. |
| **Export type** | How the audience leaves the platform: `oa_match` (through OpenX's identity graph, the default), `bidstream`, `bidstream_plus`. |
| **Provider** | The source an audience is attributed to; `openaudience` is OpenXSelect's own catalogue. |
| **CPM / PoM** | Partner price per thousand impressions, or percent of media cost. OpenX segments have neither. |
| **Reach** (on a segment) | The partner's catalogue size. Not this audience's size. |
| **Publish / export** | What activation starts: resolve the audience into ids and write them out. Hours. `exported` is done. |
| **Persona** | The plain-language description the user starts from. One persona is one INTERSECT node; see [persona-playbook.md](persona-playbook.md). |
