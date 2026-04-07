---
title: "MCP: Practical Considerations for LLM and EHR Integration. (Conversation with Farzad & Aledade Team)"
date: 2025-05-07T14:59:00
slug: mcp-practical-considerations-for-llm-and-ehr-integration-conversation-with-farzad-aledade-team
original_url: "https://www.linkedin.com/pulse/mcp-practical-considerations-llm-ehr-integration-team-josh-mandel-md-qjhqc"
linkedin_id: qjhqc
banner: ./banner.png
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7325908624155779074"
  share_id: "7325908624155779074"
  share_type: "ugcPost"
  posted_at: "2025-05-07T15:45:24"
  visibility: "MEMBER_NETWORK"
  commentary: |
    Great discussion with Farzad Mostashari and the Aledade, Inc. team on applying Model Context Protocol (MCP) for LLM-EHR interaction! We touch on data access, authorization & the future of AI in healthcare. Full writeup + YouTube link here...
---

Yesterday I had the pleasure of joining [**Farzad Mostashari**](https://www.linkedin.com/in/ACoAAAAH7jcB1ePZlK0k2Bwyg5jPtD8zKviPjU8?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAAAH7jcB1ePZlK0k2Bwyg5jPtD8zKviPjU8) and the [**Aledade, Inc.**](https://www.linkedin.com/company/aledade/) team (Nicholas Gerner, Ashok Srinivasan, and Jonas Goldstein) to explore the application of Model Context Protocols (MCPs) in healthcare IT.

Our conversation began by examining the fundamental challenge of how Large Language Models (LLMs) access and interact with Electronic Health Record (EHR) data, for both read and write operations. We considered the spectrum of data-feeding strategies: from tightly scripting the entire information context provided to an LLM, to empowering the model with more autonomy to use 'tools' for dynamic data retrieval and action execution (e.g., a tool to 'fetch the latest lab results for patient X'), and exploring hybrid approaches that balance control with flexibility. This foundational discussion framed the central problem MCPs seek to address: enabling LLMs to obtain timely, accurate, and contextually relevant data from EHRs—and, crucially, to contribute information back—without resorting to manual processes or brittle, custom integrations. MCPs, as we discussed, aim to provide a standardized mechanism for LLMs to discover and utilize these 'tools'—functions they can invoke—to query systems like EHRs or execute actions, always following proper authorization. Thanks to Aledade for hosting and for allowing me to share these points.

For everyone interested, the full discussion can be viewed <div class="youtube-embed"><iframe width="560" height="315" src="https://www.youtube.com/embed/AMPuz56qhx4" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div> -- but alas I recorded the session ineptly and our audio levels are not well balanced. I've posted a [full transcript here](https://gist.github.com/jmandel/1d80316cddaaa3b45c14cb9a825f2c8a#file-transcript-md).

### Key Technical Points from Our Discussion:

**MCP as a Standardized "Glue" for Data Access & Action:** MCPs function as an interface layer between LLMs and various underlying data access and action mechanisms. It's important to recognize the current landscape:

* ***Standardized APIs (e.g., FHIR, US Core):*** *Ideal for accessing common, well-defined data elements. However, vendors may limit the scope of data available through these APIs, especially for patient-facing applications.*
* **Full Proprietary Data Exports (e.g., EHI):** Offer more complete data sets but are not standardized, making them harder for LLMs (and even human experts) to parse and utilize reliably due to varying formats and often less comprehensive documentation. \*
* **Robotic Process Automation (RPA) / Computer Use APIs:** Serve as a "last resort" to emulate end-user actions (like screen scraping or UI clicks) when structured API access is insufficient or unavailable.

**Authorization and Transparency are Fundamental (Especially for Writes):** The demonstration connecting an application to an EHR via SMART on FHIR and OAuth highlighted the necessity of robust authorization. This becomes even more critical for write-back operations. Before MCP-facilitated tool invocation, establishing who is accessing/modifying what data for which patient under what permissions is essential. The ability for users and auditors to inspect which tools an LLM invoked, what data it retrieved, and what changes it proposed or made, is vital for trust and safety.

**LLM Tool Utilization is an Evolving Capability:** While MCPs standardize the interface for tool discovery and invocation, the LLM's proficiency in reliably selecting the correct tool, formulating appropriate query parameters, and robustly interpreting results (for reads) or generating safe and accurate inputs (for writes) is still an area of active development. For specific, deterministic tasks, directly providing pre-queried, structured data to an LLM (for reads) or using highly constrained, human-in-the-loop workflows (for writes) might currently be more reliable than relying on fully autonomous tool use.

**Potential for "Internal EHR Agents" and Business Model Shifts:** Farzad suggested a scenario where EHR vendors could leverage MCP-like principles not just for third-party app integration, but to build and deploy their own "internal agents" or "scalable workers." These AI agents could perform tasks such as pre-filling documentation, summarizing patient histories, or even managing routine clinical workflows under supervision. This could involve MCP as an internal architectural component for the EHR vendor's own AI-driven functionalities, potentially hinting at new service models beyond traditional software licensing, where organizations subscribe to specific AI-driven capabilities.

**Standardized Tool Definitions are Necessary for Ecosystem Growth:** For an MCP ecosystem to scale, especially with multiple tool providers and LLM consumers, the standardization of how these tools are defined—their names, input parameter schemas, and output schemas (for both read and write operations)—is essential. MCP itself is a relatively lean protocol; its effectiveness will be determined by the quality, interoperability, and safety of the tool ecosystem it enables.

Looking Ahead The integration of LLMs into healthcare workflows is an ongoing process, and the utility and safety of MCPs, especially for write-back scenarios, will depend on several factors:

* Continued development of robust, well-documented, and secure APIs (both read and write) from EHRs and other health data systems.
* Advancements in LLM capabilities for reliable and safe tool utilization, including robust error handling and understanding of clinical context.
* Clear governance, authorization, and audit models to ensure patient privacy, data integrity, and clinical safety, particularly critical for any operations that modify patient records.
* Progress in this field will necessitate a collaborative community effort to define useful toolsets, promote necessary standardization, and establish best practices for safe LLM-EHR interaction.

This is an area requiring continued technical focus, rigorous testing, and practical experimentation. The discussion with the Aledade, Inc. team was a good step in exploring these aspects.