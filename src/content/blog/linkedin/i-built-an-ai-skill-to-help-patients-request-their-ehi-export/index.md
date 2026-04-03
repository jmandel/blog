---
title: "I Built an AI Skill to Help Patients Request Their EHI Export"
date: 2026-03-02T14:34:00
slug: i-built-an-ai-skill-to-help-patients-request-their-ehi-export
original_url: "https://www.linkedin.com/pulse/i-built-ai-skill-help-patients-request-ehi-export-josh-mandel-md-77bjc"
linkedin_id: 77bjc
---

Every patient in the US has the right to a complete electronic copy of their medical record. Since December 2023, every certified EHR system has been required to support a feature called “EHI Export” that produces exactly this: a bulk export of all structured data in a patient’s chart. This is different from (deeper than) the "Core Data" that comes standardized in FHIR, and often includes operational detail not otherwise exposed to patients (e.g. billing reconciliation, room wait times, internal staff messaging about prescription requests).

Most patients don’t know this feature exists. Most providers haven’t used it. And there is usually no button a patient can click to request it. Often the most reliable way to make the request is to fill out a paper form and send it by fax.

**So I built an AI skill that automates the whole thing**: identifies the provider’s EHR system, finds or generates the right request form, fills it out with the patient’s details, attaches a cover letter and a vendor-specific appendix explaining what EHI Export is, collects an electronic signature and photo ID, and faxes the completed package to the provider’s medical records department.

The project is at [request-my-ehi.joshuamandel.com](https://request-my-ehi.joshuamandel.com) (source on [GitHub](https://github.com/jmandel/request-my-ehi)). It’s packaged as a "Skill" -- a set of instructions and tools that any AI agent with web access and local command-line capabilities can use to guide a patient through the process conversationally. The instructions include a getting-started guide for [claude.ai](http://claude.ai), but the approach is portable to any agentic harness that can search the web, make outbound requests, and run local scripts.

### Why this matters now

Earlier this month, [I published an analysis of EHI export documentation from 217 certified EHR vendors](/blog/posts/i-graded-265-ehrs-on-the-export-everything-requirement-median-grade-was-d). That project used AI agents to research each vendor’s products, download their export documentation, parse data documentation about EHI Exports in every format from TSV to JSON to CBOR, and produce structured assessments of what each vendor’s export actually contains. The result is a [public database](https://joshuamandel.com/ehi-export-analysis/) covering product families with grades, entity counts, field counts, export formats, and documentation URLs.

That database now powers this skill. When a patient names their provider, the skill identifies (through web search) which EHR system the provider uses, then pulls the vendor’s specific details from my database (product name, export format, entity count, documentation URL) into a customized appendix that tells the provider’s IT team exactly what’s being requested and where to find instructions for producing it. For example, the appendix for an Epic provider explains that the export produces TSV files and points to [open.epic.com/EHITables](http://open.epic.com/EHITables). The appendix for an athenahealth provider explains that the export produces NDJSON and points to athenahealth’s data export documentation. Each one is generated programmatically from the vendor database, so every request arrives with the specifics that the recipient needs to act on it.

*The timing is opportune: ASTP/ONC just launched the* [*EHIgnite Challenge*](https://www.challenge.gov/?challenge=ehignite)*, a nearly $500,000 competition seeking new tools that “improve the usability of single patient EHI exports.”* The contest is looking for approaches to EHI summarization, interactive patient tools, integration across settings, and streamlined workflows -- all of which start with the patient actually having their EHI in hand. Requesting the export is the first step, and right now it’s the hardest one. This skill exists to make it easier.

### What the skill actually does

The skill combines a 700-line "SKILL.md" file (explaining how to handle the end-to-end workflow) with a set of scripts and backend services managing signature collection and fax submission. The agent adapts its approach based on what it finds. But the general flow has ten steps:

1. **Understand the patient’s situation.** The first question is simple: “What’s the name of the doctor or clinic you want to request records from?” No jargon about EHR vendors or certification criteria. The skill explains what EHI Export is and why it matters in plain language.
2. **Identify the EHR vendor.** The agent searches the web to figure out which EHR system the provider uses -- checking patient portal URLs, web search results, and the CHPL database. The patient shouldn’t need to know (or care) that their doctor runs Epic or athenahealth.
3. **Look up vendor-specific details.** The agent queries the [vendor database](https://joshuamandel.com/ehi-export-analysis/data/vendors.json) to pull export format, entity count, documentation URL, and other metadata. It can also fetch the full analysis report for deeper context.
4. **Gather patient details.** Name, date of birth, address, phone, email. The patient can type these in or upload a file (even a FHIR Patient resource).
5. **Find the provider’s request form.** The agent searches for the provider’s own Release of Information form -- checking their website, medical records pages, and parent health system. If the form has fillable fields, the agent uses them. If it’s a flat or scanned PDF, the agent transcribes it to Markdown (preserving all the original content) and converts it to a clean, filled PDF. If no form can be found online, there’s a generic HIPAA Right of Access form as a fallback.
6. **Find the provider’s fax number.** While searching for the form, the agent also looks for the medical records department’s fax number and address.
7. **Fill the form.** The agent fills in the patient’s details, checks the right boxes (“all records,” “all dates,” “electronic format”), and marks the purpose as patient access. It defaults to maximal data collection (i.e., requesting everything) and lets the patient adjust if they want.
8. **Collect signature and photo ID.** The agent generates a link to a secure signing page where the patient draws their signature and can photograph their driver’s license, sine providers sometimes require a copy of photo ID with records requests. Both are captured on a single mobile-friendly page. The agent embeds the signature and ID page into the PDF package.
9. **Generate the cover letter and appendix.** The cover letter identifies the patient and routes the request to the right department. The appendix is the vendor-specific document explaining what EHI Export is, citing the legal basis (HIPAA Right of Access, 21st Century Cures Act, ONC certification requirement), and giving the provider’s IT team specific instructions for their EHR system. These are merged with the filled form into a single PDF package.
10. **Submit the request.** If the relay server is configured with a fax provider, the agent can fax the completed package directly -- but only after showing the patient the final PDF and getting explicit approval. Otherwise, it provides the fax number, mailing address, and guidance for submitting in person or online.

### Why a skill, not an app?

Of course, you could build an application around this workflow -- and today you’d probably build it on top of a generative AI harness. But I chose to package this as a skill rather than a standalone app for several reasons.

First, **skills invite exploration and tinkering.** A skill is a set of instructions and scripts that live in a directory. Anyone can read the prompts, understand the logic, tweak the approach, and share improvements back. If a user discovers a better strategy for finding a provider’s fax number, or a cleaner way to handle a scanned form, they can submit that change as a pull request. The skill format makes the entire workflow transparent and forkable in a way that a hosted application doesn’t.

Second, **users bring their own agent subscriptions.** Running AI models costs real money; the tokens consumed during a single EHI request workflow are non-trivial, especially when the agent is doing web research, reading PDFs, and writing scripts. By packaging this as a skill rather than a hosted service, each user pays for their own model usage through whatever agent platform they’re already subscribed to. There’s no service to fund, no usage limits to impose, and no billing relationship to maintain.

Third, **the agent provides a resilience layer.** The space of possible paths through this workflow is enormous. Some providers publish a fillable PDF with clean form fields. Some publish a scanned image of a paper form. Some have multiple forms and the agent needs to pick the right one. Some providers don’t publish a form at all. Some URLs are bot-blocked. Some forms are buried four clicks deep. When the agent encounters something unexpected, it can reason about it in real time. And when it makes a mistake, the patient can point out the problem in conversation and the agent can try a different approach. That conversational recovery loop is what makes this practical even at an early stage.

### The vendor database connection

The request-my-ehi skill is directly downstream of the [EHI export analysis](/blog/posts/i-graded-265-ehrs-on-the-export-everything-requirement-median-grade-was-d) I published earlier this month. That project used AI agents to analyze export documentation from 217 certified EHR vendors, producing structured data about each vendor’s export format, coverage, and documentation quality.

The skill consumes this data in two ways:

**Vendor lookup.** When the agent identifies a provider’s EHR system, it queries the vendor database to retrieve metadata: developer name, product name, export formats, entity and field counts, documentation URL, and quality grade. This drives the content of the appendix: each request package includes vendor-specific instructions that cite the exact product name, export format, and documentation location.

**Informed guidance.** The analysis reports give the agent context about what to expect. If a vendor’s export is graded “A” with comprehensive coverage and thousands of documented entities, the agent can confidently tell the patient what they should receive. If a vendor is graded “D” with minimal documentation, the agent can set expectations accordingly and suggest the patient push back if they receive an incomplete export.

This connection from the landscape analysis to the per-patient request tool was part of my motivation for building the vendor database in the first place. Understanding the ecosystem is useful, but helping individual patients exercise their rights is the point.

### How robust is it?

Honestly, it’s early. The repository includes an end-to-end test harness with [38 test cases](https://github.com/jmandel/request-my-ehi/blob/main/tests/e2e/test-cases.json). But 38 test cases across a universe of hundreds of thousands of providers is not broad coverage. The skill can handle many scenarios (and one of the advantages of an agent-based approach is that when it encounters something new, it can usually reason through it) but there will be edge cases, broken assumptions, and outright failures. The form-finding step in particular depends on web search quality and provider website structure, both of which vary wildly.

The flip side of building on an agent is that users can help it recover. If the agent picks the wrong form, the patient can say “that’s the wrong one, I need the patient access form, not the third-party release.” If the agent can’t find the fax number, the patient can provide it. If the form-filling goes wrong, the patient can describe the problem and the agent can try a different approach. This conversational recovery loop doesn’t exist in a static application. It doesn’t make the tool reliable in a formal sense, but it makes it useful in a practical one.

### The submission gap

I’ve been advocating for years that EHR vendors should offer APIs for patients to access their EHI electronically. Or in the absence of an API, a “Download my complete record” button in every patient portal, producing an export that any application can consume. Some vendors are closer to this than others, but most are nowhere near it.

In the meantime, the only universal mechanism for requesting health records is the one that’s existed for decades: a signed authorization form, delivered by fax or mail. It’s analog, slow, and presents a high barrier to entry -- especially for patients who don’t have access to a fax machine, don’t know what EHI Export is, and have never heard of the (b)(10) certification criterion.

The skill encapsulates this entire workflow into something a patient can complete in a conversation. That doesn’t fix the underlying infrastructure problem; we still desperately need electronic APIs. But in the meantime, we can lower the barrier for patients who want their data now, with the tools that exist today.

### Get started

Setup instructions and the skill download are at:

[*https://request-my-ehi.joshuamandel.com*](https://request-my-ehi.joshuamandel.com)

The source is open under Apache-2.0 on [GitHub](https://github.com/jmandel/request-my-ehi).

> **Early days.** This is a new project and has not been broadly tested. With so many different providers, forms, and EHR systems, you should expect to encounter bugs or rough edges. If you run into problems, please [report them on GitHub](https://github.com/jmandel/request-my-ehi/issues) to help improve the skill for everyone.

---

*For background on the vendor analysis that powers this skill, see* [*“I Graded 265 EHRs on the Export Everything Requirement”*](/blog/posts/i-graded-265-ehrs-on-the-export-everything-requirement-median-grade-was-d) *and* [*“How I Used AI Agents to Assess the State of EHI Export.”*](https://www.linkedin.com/pulse/how-i-used-ai-agents-assess-state-ehi-export-josh-mandel-md-jiqfc/)