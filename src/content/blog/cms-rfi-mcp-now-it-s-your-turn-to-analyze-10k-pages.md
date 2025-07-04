---
title: "CMS RFI MCP: Now It&#x27;s Your Turn to Analyze 10k Pages ;)"
date: 2025-07-02T04:22:00
slug: cms-rfi-mcp-now-it-s-your-turn-to-analyze-10k-pages
original_url: "https://www.linkedin.com/pulse/cms-rfi-mcp-now-its-your-turn-analyze-10k-pages-josh-mandel-md-qm4mc"
linkedin_id: qm4mc
---
![](https://media.licdn.com/mediaD5612AQFRRl8V34YHUw)

[CMS RFI MCP: Now It's Your Turn to Analyze 10k Pages ;)](/posts/cms-rfi-mcp-now-it-s-your-turn-to-analyze-10k-pages)
=====================================================================================================================

Created on 2025-07-02 04:22

Published on 2025-07-02 11:15

A few weeks ago, I shared an [interactive dashboard](https://joshuamandel.com/regulations.gov-comment-browser/CMS-2025-0050-0031/) summarizing public comments on the CMS Health Tech Ecosystem RFI. Now for the next step: **make the underlying data more amenable to new, dynamic analyses**.

Toward this end, I'm sharing a data set, a tool, some sample prompts, and lessons learned along the way.

### 1. AI-Ready Data: Regulations.gov MCP Server

The first step was to make the dataset of ~1,000 comments easily accessible to AI tools. To do this, I have exposed the corpus of faithfully-summarized comments via a **Model Context Protocol server**. This allows any language model or AI agent to programmatically query the data, opening the door for much more dynamic query and analysis flows.

### Try the MCP Server

You can connect your own tools to this server today.

* **Web:** If your MCP Client supports the Streamable HTTP Transport, you can use "<https://regulations-gov-comment-browser-mcp.fly.dev/mcp>" as your endpoint (no auth).
* **Locally:** If your MCP Client only supports STDIO transport, you'll need to run a copy locally. You can do this via "git clone <https://github.com/jmandel/regulations.gov-comment-browser>". Inside the "mcp" dir, you can "bun install"; then "./src/cli.ts" is your MCP Server entrypoint.
* **Source Code:** You can find the code and setup instructions in the GitHub repository here: <https://github.com/jmandel/regulations.gov-comment-browser>

### 2. Lesson Learned: Overcoming "Context Blur"

Making the data available is easier than making it useable! In my own experiments, I ran into a challenge that will be familiar to anyone who has worked with LLM analysis of large text corpora.

Let's say you want to understand the feedback on TEFCA, which is mentioned in nearly 400 comments. If you feed all of that text into a single, massive context window and ask an agent to summarize the themes, you encounter what I call **"context blur."** The details start to wash out. The model can pick out high-level structures, but distinct, nuanced, and even conflicting ideas blur together into a generic summary.

You get much better, more consistent, and higher-quality results on smaller datasets. But then you need a strategy for bringing those detailed analyses back into a coherent, high-level picture.

(And a bonus lesson: MCP clients can have varied limitations on how large a payload an MCP tool is allowed to respond with. In Claude Code, the agent receives an error message if the response is too large, and is given the chance to issue follow-up queries. So in my MCP Server, by default I try to respond with a full-detail comment summary, and I offer the option to request "chunks" in a follow-up if the model receives an error from its tool-calling harness.)

### 3. A Pattern That Works: "Analyze Small, Synthesize Up"

The most effective pattern I've found is a strategy I call "Analyze Small, Then Synthesize Up." I implement this using the claude command-line agent from [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) and its powerful (but under-documented!) "subtask" feature. Here’s how it works:

1. **Agentic Breakdown:** Instead of a hard-coded script, the main agent thread first decides what batches need to be run and what questions should be tackled by each sub-agent. For a complex topic, it might create dozens of subtasks.
2. **Parallel Deep Dives:** If you ask nicely, the agent will spawn these subtasks to run in parallel. Crucially, **each subtask runs in its own isolated context** and writes its output to a file. This allows one subtask to do a deep dive on comments from health systems, while another simultaneously analyzes feedback from patient advocates, all without confusing the two or blurring the context window.
3. **Synthesis:** Once the deep dives are complete, the main agent thread reads the output files from the subtasks and performs a final synthesis. It’s now summarizing concise summaries, which results in a final report that is more comprehensive detail-rich.

### 4. Try This Workflow: Slash Commands for Claude Code

To make the "Analyze Small, Synthesize Up" pattern easy to use, I've packaged it into a few custom "slash commands" for the Claude Code CLI. This workflow is a two-step process you can run right from the command line.

**Step 1: Investigate.** You start by giving the "/analysis-workflow" command a high-level mission (e.g., "Investigate themes of 'patient access' in the CMS RFI"). It automatically deconstructs the request, plans the work, and launches parallel subtasks to perform deep analysis on small batches of comments. The results are saved as detailed notes in a new analysis/ directory.

**Step 2: Synthesize with a Persona** Once the investigation is complete, you choose a synthesis persona to create the final report from the files in the analysis directory:

* /synthesis-advisor: Creates a concise, "bottom-line-up-front" briefing for a busy executive.
* /synthesis-journalist: Writes a compelling long-form article, finding the human element and narrative thread.
* /synthesis-moderator: Structures a neutral debate guide, "steel-manning" all sides of the core arguments.

The commands together with an ".mcp.json" (pre-configuring the MCP Server for Claude) are available at <https://github.com/jmandel/regulations.gov-comment-browser/tree/main/mcp/.claude/commands> .

### Let's Analyze Together!

I’m sharing all this to empower you to try your explorations in your client of choice. But to make it even easier, here's a special offer ;-)

**Each day while requests come in, I will run one analysis through this workflow and share the results back here!**

*What is your burning question? Is there a specific topic or a cross-section of comments or a niche theme you're curious about? Post your request in a clear articulation here. I’ll add it to my queue and share the results.*