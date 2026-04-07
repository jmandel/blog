---
title: "From MCP Server to AI Skill: A Simpler, More Powerful Way to Analyze Federal Regulation Comments"
date: 2026-03-09T18:26:00
slug: from-mcp-server-to-ai-skill-a-simpler-more-powerful-way-to-analyze-federal-regulation-comments
original_url: "https://www.linkedin.com/pulse/from-mcp-server-ai-skill-simpler-more-powerful-way-josh-mandel-md-hyh1c"
linkedin_id: hyh1c
banner: ./banner.png
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7436843829607133185"
  share_id: "7436843829607133185"
  share_type: "ugcPost"
  posted_at: "2026-03-09T18:42:18"
  visibility: "MEMBER_NETWORK"
  commentary: |
    My regulations dot gov analysis tool... now with SKILL.md support! How I replaced my 8k line MCP server with 400 lines of markdown and improved the user experience in the process.
---

Last summer I shared an MCP server that let AI tools query public comments on federal regulations. It worked — but hosting and maintaining it was a pain. Today I'm replacing it with something better.

**The MCP problem**

The MCP server required a running backend (I hosted on [Fly.io](http://Fly.io) with a scale-to-zero VM), had payload size limits that needed workarounds, exposed limited/fragile search APIs, and added a dependency that could break. Users had to either connect to a remote HTTP endpoint or clone the repo and run the server locally. Every docket update meant redeploying.

**The replacement: a static AI Skill**

The new approach is a single markdown file — SKILL.md — generated automatically as part of the GitHub Pages build. No server. No deployment. No runtime dependencies.

The skill file teaches an AI assistant how to fetch and analyze the published JSON data directly via public URLs. It includes:

* Which regulation dockets are available (currently 6, with 11k+ comments)
* The URL pattern to fetch any data file
* Full schemas for every JSON endpoint (themes, entities, comments, indexes)
* A decision tree: when to use pre-built theme summaries vs. fetching full comments and searching

When the analysis pipeline processes a new docket, the build regenerates the skill with updated stats. The data was always static JSON on GitHub Pages — the MCP server was just an intermediary that's no longer needed.

**Why this is stronger**

An MCP server gives an AI model a set of tool calls. A skill gives it *understanding*. Instead of searchComments(query="TEFCA", limit=50) and hoping the tool returns useful results, the model knows the data structure, knows that theme summaries exist for broad questions, knows to grep full comments for specific quotes, and knows which indexes map entities to comment IDs. It makes better decisions about how to approach a query because it has the full picture.

And it's zero infrastructure. The skill file is served as a static asset alongside the dashboards. Anyone can point their AI tool at it — or just read it themselves to understand the dataset.

**The numbers tell the story: this change deleted 7,500 lines of server code — Express routes, Dockerfile,** [**Fly.io**](http://Fly.io) **config, search engine, caching layer, tests — and replaced them with 400 lines of build-time template that generates a single markdown file.**

Example query for Claude Web UI below. Just click to try it! (You'll need your [sandbox config](https://claude.ai/settings/capabilities) to enable access to joshuamandel.com.)

> [*Hi Claude, Please read joshuamandel.com/.../SKILL.md and analyize HTI-5 proposed rule comments to [<your own question here>]*](https://claude.ai/new?q=Read+https%3A%2F%2Fjoshuamandel.com%2Fregulations.gov-comment-browser%2Fskill%2FSKILL.md+and+analyize+HTI-5+proposed+rule+comments+to+understand+the+role+of+BigTech+based+on+their+own+comments+and+their+mentions+in+others%27+comments)

The skill is live now: [**https://joshuamandel.com/regulations.gov-comment-browser/skill/SKILL.md**](https://joshuamandel.com/regulations.gov-comment-browser/skill/SKILL.md)

Previously: [CMS RFI MCP: Now It's Your Turn to Analyze 10k Pages](/blog/posts/cms-rfi-mcp-now-it-s-your-turn-to-analyze-10k-pages)