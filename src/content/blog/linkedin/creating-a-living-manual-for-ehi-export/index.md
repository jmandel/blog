---
title: "Creating a \"Living Manual\" for EHI Export"
date: 2025-06-26T17:27:00
slug: creating-a-living-manual-for-ehi-export
original_url: "https://www.linkedin.com/pulse/creating-living-manual-ehi-export-josh-mandel-md-8bzrc"
linkedin_id: 8bzrc
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7345862527995559937"
  share_id: "7345862527995559937"
  share_type: "ugcPost"
  posted_at: "2025-07-01T17:15:06"
  visibility: "MEMBER_NETWORK"
  commentary: |
    How can we make EHI Exports easier to work with? Check out (and help me curate!) the new "Living Manual".
---

It is a significant undertaking to maintain and document a modern EHR database spanning diverse clinical domains and workflows. It's no surprise that a database optimized for clinical care and hospital operations contains thousands of tables. In its native context, that complexity is a feature. But for patients, developers, and data engineers trying to use an Electronic Health Information (EHI) export, navigating this terrain of accreted complexity can be daunting, especially without a map.

Last week, I wrote about some challenges of accessing and analyzing Epic's EHI exports. Let's leave access challenges for another time; today I'm sharing a draft of an open-source project to help with analysis: The **EHI Living Manual**. This guide is for anyone who has been handed a folder of TSV files and needs to make them useful -- whether you're an individual with your own health data, a developer building a new application, or a data engineer tasked with integrating a large-scale export.

* **Explore the manual:** [**https://joshuamandel.com/ehi-living-manual**](https://joshuamandel.com/ehi-living-manual)
* **Contribute on GitHub:** [**https://github.com/jmandel/ehi-living-manual**](https://github.com/jmandel/ehi-living-manual)

The manual includes:

* **Interactive SQL Examples.** Run and modify queries directly in the browser against my real, personal (lightly redacted) EHI dataset.
* **Emphasis on Core Patterns.** Teaches fundamental concepts like identifier types and modeling pattern

### Why a "Living Manual"? Let's Read the Official Docs...

Epic provides a comprehensive list of [EHI table documentation files](https://open.epic.com/EHITables/Index). The challenge is that the official documentation is generated from content intended for Epic customers and consultants *who also have access to Epic-internal supporting materials*. The current documentation frequently surfaces partial, circular, or confusing definitions. The export also includes myriad tables with redundant information, joined up to support specific, unexplained analytics workflows. Without guidance, it's nearly impossible to tell what you're looking at.

For a simple example that I ran into this afternoon, take ED\_PAT\_STATUS. The ED prefix suggests "Emergency Department," but my own export is populated with records from (among other things) routine annual physical exams, logging operational details like when I was brought into an exam room vs when a clinician arrived. (To be clear, this kind of full operational visibility provides important opportunities for analysis, and exemplifies the power of EHI over summary data like USCD, particularly at the population level.) The official table description shines little light on the semantics, telling you *what the table technically contains* without telling you *what it means*:

> **Description:** The ED\_PAT\_STATUS table contains information about ED patients' "patient" status...

### Documentation is Evolving...

To get philosophical for a moment: the **authorship and readership of technical documentation is changing**! It's no longer just by and for humans; it's also, to a growing extent, by and for LLMs. With frontier LLMs and command-line agents that can use their own tools, the work of writing documentation becomes an iterative dialogue. To produce the first draft of the EHI Living Manual, I stared by asking Claude and Gemini CLI agents to conduct automated data explorations; create an outline of topics; formulate a research plan to flesh it out; then refine the chapters based on my feedback.

Still, making full sense of these data defies expert capabilities for developers (like me) unfamiliar with Epic's internals. We can make educated guesses, but we will sometimes arrive at the wrong conclusions. Much of the draft material likely contains semantic errors in joining and interpreting the EHI tables. But it’s open source; the content is just a set of Markdown files with embedded <example-query> blocks, making it easy for anyone in the community to **contribute feedback, corrections, and suggestions**.

---

*What's the one thing you wish you knew when you first saw an Epic EHI export?*

#EpicEHR #HealthIT #Interoperability #EHI #HealthcareAnalytics #DataEngineering #OpenSource #21stCenturyCuresAct