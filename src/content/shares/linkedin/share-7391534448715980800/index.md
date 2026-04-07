---
title: "With an Argonaut Connectathon coming up this week (topic: writing clinical…"
date: 2025-11-04T17:59:01
slug: share-7391534448715980800
share_url: "https://www.linkedin.com/feed/update/urn:li:share:7391534448715980800"
share_type: "share"
share_id: "7391534448715980800"
visibility: "MEMBER_NETWORK"
---

With an Argonaut Connectathon coming up this week (topic: writing clinical notes to EHRs), I've been putting together testing tools... but with a different approach.

Background: Typical connectathon testing falls into two categories. First, you have conformance tools like Inferno and Touchstone that provide baseline evaluation. Just as important is the exploratory work: developers diving into API behaviors, tweaking parameters to understand edge cases, and iterating rapidly to see how servers behave.

LLM-based agents are a new category, combining automation with developer-like reasoning. I've begun to explore this by writing a Claude Skill (a packaged set of instructions and tools for the AI) that quickly brings a Claude instance up to speed on the Argonaut spec. It also provides built-in, deterministic tools for selecting a server, establishing an OAuth connection, and creating detailed logs of every query for downstream analysis.

Instead of encoding fixed test assertions, this skill gives Claude the FHIR specification, test scenarios, and tools to make API calls, then lets it explore.

It can reason through problems on its own. For example: "This conditional create failed. The OperationOutcome suggests an issue resolving an encounter reference. Let me try different reference formats to pinpoint the cause of the error."

This approach shines for rapid deep dives. For instance, I recently used this skill to investigate a search parameter issue. Rather than manually crafting test cases, I encouraged an agent to explore an unexpected behavior that it noticed. In about 5 minutes, it generated multiple test cases, identified the specific pattern that was failing, cross-referenced the behavior against the spec, and suggested the likely root cause. This easily could have been a 30-minute manual investigation. For an early draft specification like Writing Clinical Notes, this is particularly valuable. An agent that can systematically explore edge cases and reason about spec intent helps surface these issues faster.

Of course, LLM agents aren't a replacement for formal conformance testing or human expertise. They can misinterpret specs and may miss issues requiring deep domain expertise. But for early-stage implementation, debugging, and exploring "what if" scenarios before the connectathon, they are incredibly effective.

Testing tools are evolving to include more sophisticated validators, better observability, and now, LLM-augmented exploration. Each has its place. If you're preparing for this week's connectathon, having an agent that can conduct exploratory testing on demand is worth trying. It might become the tool you reach for first when something doesn't behave as expected.

"My "write-clinical-notes.skill" is open source at https://lnkd.in/g6nArTAF
