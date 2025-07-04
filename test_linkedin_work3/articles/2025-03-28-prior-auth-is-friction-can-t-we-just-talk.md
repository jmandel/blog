---
title: "Prior auth is friction. Can't we just talk?"
date: 2025-03-28T03:23:00
slug: prior-auth-is-friction-can-t-we-just-talk
original_url: "https://www.linkedin.com/pulse/prior-auth-friction-cant-we-just-talk-josh-mandel-md-taq6c"
linkedin_id: taq6c
banner: https://media.licdn.com/mediaD5612AQH02VU4jM2shg
---

Created on 2025-03-28 03:23

Published on 2025-03-28 12:05

Prior authorization is friction. We try to automate it with structured data, through consensus-based standards like HL7 Da Vinci's Burden Reduction FHIR IGs. Consensus is slow and bound by compromise, leading to rigid technical integrations. Better interoperability patterns are coming.

**Consider an LLM agent embedded in the EHR**. When Dr. Reed orders Adalimumab for David Lee's Rheumatoid Arthritis, the agent initiates a dialogue with the payer's "Prior Auth Tool" – a service endpoint, perhaps communicating via a simple, standardized protocol like [MCP's](https://spec.modelcontextprotocol.io) "tools/call" (the specific protocol matters less than the pattern: agents using tools).

### The Conversation Might Go Like This...

1. EHR Agent: "Checking if Adalimumab for patient David Lee needs PA. Here's basic context."
2. Prior Auth Tool: "Yes, PA required. Need clinical evidence: RA diagnosis, MTX trial >3mo failure/intolerance, recent severe activity score, negative TB screen. Provide narrative documentation."
3. EHR Agent: (Internally queries EHR via FHIR APIs and search) "Okay, found the diagnosis, labs, score. Synthesizing evidence summary..." (Sends summary) "Here's the clinical picture."
4. Prior Auth Tool: (Reviews evidence with Payor Agent) "Looks mostly good, but the MTX trial duration isn't explicitly confirmed >3 months in this summary. Please provide specific documentation for that point."
5. EHR Agent: (Internally searches notes/med history again) "Found Dr. Reed's note from [Date]: 'MTX ineffective after 4 months'. Sending that specific quote."
6. Prior Auth Tool: "Received. That confirms the duration requirement. Approved. Here's the auth number."
7. EHR Agent: (Updates EHR, notifies Dr. Reed) "PA secured."

### Why Is This Different?

* Local Intelligence: The EHR Agent leverages its secure, internal access (via FHIR APIs, proprietary tools, or robotic process automation) to find the relevant evidence within the full patient context.
* Embraces Nuance: The interaction prioritizes clinical meaning conveyed through narrative, supported by structured data, rather than being constrained by pre-defined fields.
* Flexibility: If the EHR Agent's LLM is sufficiently capable, perhaps it can adapt to variations in how payers organize their PA logic and workflow.

### Rethinking Standardization?

Maybe the intense focus on standardizing every possible data element for every complex interaction isn't the only path forward. If capable LLM agents can handle conversational variations, perhaps standardization efforts deliver more leverage when focused on:

* Reliable, interoperable agent-to-tool communication protocols.
* Comprehensive, performant data access APIs (like FHIR) to enable search and communication of health record content.

### The Bottom Line

This isn't FHIR vs. LLMs. Let FHIR provide the standardized, reliable data access. Then let LLM agents, communicating via agreed-upon protocols, handle the dynamic, narrative dialogue that complex PAs demand – the place where structured forms often break down.