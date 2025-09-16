---
title: "Connect the Dots for Prior Auth:  A2A && MCP?"
date: 2025-04-09T16:56:00
slug: connect-the-dots-for-prior-auth-a2a-mcp
original_url: "https://www.linkedin.com/pulse/connect-dots-prior-auth-a2a-mcp-josh-mandel-md-mt3te"
linkedin_id: mt3te
banner: ./banner.png
---

Created on 2025-04-09 16:56

Published on 2025-04-09 17:13

*Another day, another open protocol!*

In previous posts, we explored how agents can use **MCP tools** (`grep`, query, eval) to analyze EHR data fetched via **SMART on FHIR** ([Theory to Practice](/posts/theory-to-practice-llm-agents-using-mcp-tools-on-real-ehr-data-with-demo)), and envisioned a more conversational prior authorization (PA) workflow ([Prior Auth is Friction](/posts/prior-auth-is-friction-can-t-we-just-talk)).

Today, perhaps a new puzzle has emerged with the **Agent-to-Agent (A2A) protocol**. While it's very early days for A2A, this article offers a *speculative take*, based on an initial read of the protocol's design and samples, on how it *could potentially* serve as a communication link between clinical and payer agents in PA workflows.

The core challenge remains: how do the EHR-side agent (having analyzed data via MCP tools) and the payer-side agent actually *have* the necessary dialogue for PA, especially when it's asynchronous and involves structured data or forms?

### A2A: A Communication Fabric?

Based on its just-released specification, A2A appears designed for **asynchronous, task-based communication between independent agents**. It could provide a standardized messaging layer for systems like our Clinical and Payer Agents to collaborate, even as black boxes to each other. From an initial look, A2A seems to offer features relevant to PA:

1. **Agent Discovery (`AgentCard`):** A potential mechanism for Clinical Agents to find appropriate Payer Agents by discovering their capabilities, endpoints, and supported interaction modes.

2. **Task-Oriented Model:** Its task structure (`tasks/send`, tasks/get) with defined states (`working`, input-required, completed) naturally maps to the PA lifecycle.

3. **Asynchronous Design:** Acknowledges that PA isn't instantaneous, fitting A2A's asynchronous nature.

4. **Rich Payloads & Forms:** The Part system (TextPart, FilePart, DataPart) looks flexible enough to carry PA request/response data (like FHIR resources or form structures). The protocol's samples demonstrate form-like interactions, crucial for requests for additional information.

5. **Streaming & Push Notifications:** Capabilities like tasks/sendSubscribe and pushNotification *could* enable real-time status updates or proactive completion notifications, reducing polling burdens.

### Proposed Separation of Concerns: SMART on FHIR + MCP + A2A

If A2A fulfills its potential, the roles of these protocols could become clearer, creating a synergistic stack:

1. **SMART on FHIR:** Remains the secure **data access** layer for the *Clinical Agent* to fetch the patient record snapshot.

2. **MCP (Model Context Protocol):** Remains the **LLM-to data interaction layer** for the *Clinical Agent* to *analyze* the fetched snapshot using tools like grep, query, eval (or equivalent internal functions). MCP tools operate *locally* on the secured data. (Here, "local" means within the control of the provider-side system, even if the actual LLM execution and tools are remotely hosted in provider-trusted infrastructure) .

3. **A2A (Agent-to-Agent):** *Could become* the **inter-agent communication** layer for the dialogue *between* the Clinical Agent and the Payer Agent, managing the task lifecycle and data exchange across organizational boundaries.

### The Prior Auth Workflow with A2A?

How might A2A fit into the PA conversation?

1. **Initiation & Data Gathering:** Unchanged. Clinical Agent uses **SMART** to fetch, **MCP tools** to analyze EHR content.

2. **Formulate & Discover:** Unchanged. Clinical Agent prepares the PA request. It *could* use an A2A-aware directory to find the Payer Agent's AgentCard.

3. **Submit PA Task via A2A:** Clinical Agent sends an A2A tasks/send request to the Payer Agent's endpoint. The payload (message.parts) carries the PA data.

4. **Payer Processing & A2A Updates:** Payer Agent processes the A2A PA task, potentially using A2A status updates or forms to request more information before returning the final determination via A2A.

5. **Outcome Handling:** Clinical Agent receives the final A2A update.

### Complementarity and Caveats

This proposed integration leverages each protocol's strengths: MCP-based tools for secure, rich clinical context analysis, and A2A for managing the asynchronous, potentially multi-step dialogue between independent systems.

This is an *early interpretation* based on the initial documentation and samples. How A2A evolves, how widely it's adopted, and how its features (like push notifications, security models between arbitrary agents, and complex state management) are implemented in practice will determine its true role.

The key challenges identified previously – robust security between agents, standardizing PA data payloads within A2A messages, ensuring reliable error handling across protocols, managing user experience, and agent discoverability – remain critical hurdles to overcome for *any* agent-based PA solution, including one potentially using A2A.

### The Path Forward: Exploration

The emergence of A2A adds another potential tool to our interoperability toolkit. It encourages the community to think about standardizing not just data access (SMART on FHIR) and LLM/tool integration (MCP), but also the *conversations* between collaborating agents. Evaluating A2A for prior authorization seems like a worthwhile step toward intelligent, efficient, and interoperable healthcare systems. The open nature of A2A, like MCP and SMART and FHIR, invites experimentation.