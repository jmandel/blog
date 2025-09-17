---
title: "Excited to share Kiln, a browser-based tool I've been hacking together for…"
date: 2025-09-11T20:47:43
slug: share-7372007960107147264
share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7372007960107147264"
share_type: "ugcPost"
share_id: "7372007960107147264"
visibility: "MEMBER_NETWORK"
---

Excited to share Kiln, a browser-based tool I've been hacking together for generating synthetic notes. Think: turn a quick clinical sketch into a full free-text note, and from there (optionaly) into a (mostly) valid FHIR Document Bundle, powered by LLMs and a bit of agentic elbow grease. 

In the FHIR trenches, we all know the pain of wrangling test data: it needs to be realistic, coded properly, and ready to throw at APIs without melting your validator. Why not let an AI handle the heavy lifting?

Start with something fun like "62-year-old female pirate with new angina" (arrr, chest pain on the high seas), and Kiln outlines a note structure, drafts sections with pirate flair, critiques for clinical chops (e.g., "Solid weave of voice and vitals: 85% pass"), then scaffolds it into FHIR JSON. From there, it's refinement time: agentic loops hunt SNOMED codes via terminology servers, patch JSON errors, and iterate until the bundle validates (barring the occasional XHTML gremlin in the narrative).

It's a mix of rote prompt flows for consistency and clever loops for smarts, like pausing mid-pipeline if OpenRouter hiccups, then resuming from checkpoints via IndexedDB. Runs locally (grab the FHIR validator on port 5173), all in JS with a lightweight workflow engine. Fork it, break it, improve it at https://lnkd.in/gKSJ3Vt8.

"Quick demo video below. If you're knee-deep in FHIR testing or LLM experiments, give it a whirl.
