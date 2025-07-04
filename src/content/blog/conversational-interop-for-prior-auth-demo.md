---
title: "Conversational Interop for Prior Auth (demo!)"
date: 2025-04-25T15:38:00
slug: conversational-interop-for-prior-auth-demo
original_url: "https://www.linkedin.com/pulse/conversational-interop-prior-auth-demo-josh-mandel-md-wjwxe"
linkedin_id: wjwxe
---
![](https://media.licdn.com/mediaD4E12AQH_x5CG7GJiyA)

[Conversational Interop for Prior Auth (demo!)](/posts/conversational-interop-for-prior-auth-demo)
==================================================================================================

Created on 2025-04-25 15:38

Published on 2025-04-25 15:59

What if, instead of pre-specifying *every* data field and *every* possible workflow step, we could enable conversations between capable systems?

Today's **live demo** explores early steps toward this vision – using LLM agents with protocols like Agent-to-Agent (**A2A**) and Model Context Protocol (**MCP**) to connect directly to real EHR data (via **SMART on FHIR**) and tackle Prior Authorization more dynamically.

[LinkedIn Article: 7664374542596473597]

Demo at [https://youtu.be/BRX7HUBlEq](https://youtu.be/BRX7HUBlEqw)

### Key Perspectives Explored in the Demo:

1. **Interoperability Through Conversation, Not Just Schema:** The core thesis: LLMs allow us to bypass the bottleneck of pre-standardizing every interaction detail. By understanding intent and context, agents can communicate effectively using flexible payloads (text, files, dynamically generated structure like the demo's JSON) without rigid, pre-negotiated schemas *or* workflows. This allows for more adaptability than current structured approaches.
2. **Dynamic Structure Generation:** While avoiding *pre-defined* structure is key, structure itself is still valuable. The demo shows the LLM generating a structured JSON evidence package *when needed* based on the conversational context and policy requirements, complete with FHIR resource provenance for audibility. It's structure on demand, driven by the task.
3. **Adaptive, Multi-Turn Workflows:** The A2A protocol facilitates an asynchronous back-and-forth. The interaction isn't limited to a single request-response. The agents can ask clarifying questions, request specific documents, and iterate until the task (PA determination) is complete, mirroring real-world processes more closely than simple API calls.
4. **Optimized Human-AI Collaboration:** The "Liaison Agent" pattern automates data gathering and analysis within the EHR but strategically pauses the automated flow to request targeted input from the clinician *only* when human judgment or missing information requires it. This respects clinician time while leveraging AI efficiency.
5. **Expanding the Conversation (Patient Dyad):** While the demo focuses on the clinician, this conversational model could potentially extend to securely involve the patient for relevant inputs, truly supporting the patient-provider dyad.
6. **Facilitating Approvals Intelligently:** The AI aims to build the strongest case for approval based on policy and evidence. It also provides early, local feedback if criteria aren't met, helping clinicians understand gaps *before* submitting. And in all of this workflow, AI is never used to make denials, only to get faster approvals.

### Onward!

By combining robust data access (SMART on FHIR), dynamic tool protocols (MCP), and flexible conversational interop frameworks (A2A), we can build more intelligent and adaptable healthcare systems. This approach leverages LLMs for what they do best – understanding nuance and managing dialogue – while grounding them in reliable standards.

Related post: [https://www.linkedin.com/pulse/prior-auth-friction-cant-we-just-talk-josh-mandel-md-taq6c](/posts/prior-auth-is-friction-can-t-we-just-talk)

Explore the open-source implementation: <https://github.com/jmandel/health-record-mcp>