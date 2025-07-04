---
title: "Theory to Practice: LLM Agents Using MCP Tools on Real EHR Data (with demo)"
date: 2025-04-08T19:10:00
slug: theory-to-practice-llm-agents-using-mcp-tools-on-real-ehr-data-with-demo
original_url: "https://www.linkedin.com/pulse/theory-practice-llm-agents-using-mcp-tools-real-ehr-data-mandel-md-acknc"
linkedin_id: acknc
---
![](https://media.licdn.com/mediaD5612AQElZrWw7Gcq6w)

[Theory to Practice: LLM Agents Using MCP Tools on Real EHR Data (with demo)](/posts/theory-to-practice-llm-agents-using-mcp-tools-on-real-ehr-data-with-demo)
==============================================================================================================================================================

Created on 2025-04-08 19:10

Published on 2025-04-08 19:24

Last week, I [discussed](/posts/prior-auth-is-friction-can-t-we-just-talk) how LLM agents embedded in EHRs could transform complex workflows like prior authorization by using tools to interact conversationally, rather than relying solely on rigid structured data exchange. The idea was to let agents handle the dialogue, using reliable data access standards like FHIR as the foundation.

Today, I want to show you some underpinnings what that looks like in practice.

I've put together a short video demo showcasing a system that connects Large Language Models (LLMs) directly to electronic health record data using exactly this "agent + tools" pattern.

[Related Article: theory-to-practice-llm-agents-using-mcp-tools-on-real-ehr-data-with-demo](/posts/theory-to-practice-llm-agents-using-mcp-tools-on-real-ehr-data-with-demo)

### What's Under the Hood?

The demo architecture involves three key pieces:

1. **SMART on FHIR Client:** Uses standards (SMART, FHIR, US Core) to securely extract both structured data and unstructured clinical notes from an EHR – in this case, my own record fetched from my provider's patient portal (via Epic MyChart's FHIR endpoint).

2. **MCP Server:** This acts as a middle layer, taking the fetched FHIR data and exposing a set of *tools* (like grep, SQL queries, or even JavaScript execution via eval\_record) that an LLM can use to analyze that specific patient's data locally. It uses the **Model Context Protocol (MCP)** to define and offer these tools.

3. **AI/LLM Interface:** The agent (in the demo, Gemini 2.5 Pro via the Cursor IDE) that understands the available tools (thanks to MCP) and decides which ones to call to answer user questions about the EHR data.

### Why Tools Matter

As discussed previously, LLMs often struggle with large volumes of raw structured data like FHIR JSON. Pasting megabytes of JSON into the context window isn't efficient. However, LLMs excel at *using tools*. Give them a grep tool to search notes, or an eval tool to run code against the structured data, and they become much more powerful and efficient analysts.

### The Demo Shows

* **Fetching Real Data**: Connecting to a provider via SMART on FHIR, authorizing access, and pulling the US Core dataset into a local SQLite database.
* **Agent Querying**: The LLM using MCP-defined tools like *grep* to find active conditions.
* **Agent Analysis**: The LLM using *eval*  to execute JavaScript (iterating through FHIR Observations to calculate things like average blood pressure)
* **Agent Synthesis**: The LLM combining information from structured data and unstructured notes (found via grep) to provide comprehensive summaries (timeline of Post-concussion syndrome)

### The Role of MCP and Standardization

This demo leverages the **Model Context Protocol (MCP)** – a developing standard designed specifically for agent-to-tool communication. It allows the server to advertise its capabilities (the tools) and their documentation, enabling the LLM agent to intelligently select and use them.

This reinforces the idea from the last post: maybe our intense standardization efforts yield more value when focused on:

1. **Robust Data Access:** Reliable, performant APIs like FHIR for getting the necessary data *out* of the EHR.

2. **Interoperable Tool Protocols:** Standards like MCP for how agents *discover and interact* with tools that operate on that data.

### Early Days & Security

This is still evolving rapidly. The video touches on the crucial security aspects – OAuth flows for authorization (both between the user and the EHR, as well as between the LLM client and the MCP server), the emerging risks of prompt injection or malicious tool outputs influencing agent behavior, and the UX challenges of user confirmation before tool execution. We need robust security models as these capabilities mature.

### Check it Out

Watch the demo to see these concepts in action. The code is open source if you want to dig deeper into the implementation. Let's continue the discussion on how we can best leverage LLM agents and standards like FHIR and MCP to build better health IT.

* Video: <https://youtu.be/K0t6MRyIqZU>
* GitHub repo: [**https://github.com/jmandel/health-record-mcp**](https://github.com/jmandel/health-record-mcp)

#FHIR #LLM #AIinHealthcare #MCP #HealthIT #Interoperability #SMARTonFHIR #EHR #AgenticAI