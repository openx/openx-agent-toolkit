# OpenX agent toolkit

Skills and tool reference for AI agents that work with OpenXSelect and OpenXDirect through the OpenX MCP server at `https://api.openx.com/mcp`.

## What's here

- `skills/`: step-by-step playbooks an agent follows for multi-step jobs. Each skill is a folder with a `SKILL.md`, and most have a `references/` folder the skill points to.
- `docs/tools/`: the reference for every tool the OpenX MCP server offers, with its parameters.

## Skills

| Skill | What it does |
| --- | --- |
| `openx-connection-guide` | Rules for every OpenX call: instances, accounts, errors and confirmation. Read before your first call. |
| `openx-campaign-launch` | Launches an OpenXDirect campaign end to end: order, creative, line item, forecast and activation. |
| `openx-bulk-change` | Pauses, resumes or changes many OpenXDirect line items at once. |
| `openx-budget-reallocate` | Moves budget between the line items of one OpenXDirect order. |
| `openx-pacing-review` | Reviews delivery pacing across the line items of an OpenXDirect order or account. |
| `openx-delivery-troubleshoot` | Diagnoses why an OpenXDirect line item or campaign is not delivering. |
| `openx-audience-build` | Builds, sizes, prices and activates an OpenXSelect audience. |
| `openx-deal-creation` | Creates a new OpenX deal with its targeting package. |
| `openx-deal-troubleshooter` | Troubleshoots the performance of an OpenX deal. |

## Using the skills

You need an active OpenX account. Connect your AI client to `https://api.openx.com/mcp` and sign in with your OpenX login.

The OpenX MCP server serves these skills itself. A connected agent lists them with `listSkills` and reads one with `getSkill`, and clients that support MCP prompts offer them as commands, such as `/campaign-launch`. A local copy is optional.

To install a local copy with the `skills` command line tool:

```
npx skills add openx/openx-agent-toolkit
```

You can also copy the folders under `skills/` into your agent's skills directory.

## How this repository is updated

`skills/` and `docs/tools/` are published from the OpenX MCP servers each time they change, and `.sync/` records which server each file came from. An edit made here directly is replaced by the next update. `scripts/` holds the tooling that publishes them, and `make test` runs its tests.

## License

Copyright © 2026 OpenX Technologies, Inc. All rights reserved. These tools and Skills are licensed solely for use with an active OpenX account and are subject to the OpenXSelect Portal Terms of Service ([OpenXSelect](https://select.openx.com/terms/)). No other license is granted. You may not copy, modify, or redistribute these materials except as needed to use them with your OpenX account.
