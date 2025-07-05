---
title: "Evaluating FHIR's Evolution: AI-Assisted Analysis of R4→R6 Changes"
date: 2025-05-09T18:38:00
slug: evaluating-fhir-s-evolution-ai-assisted-analysis-of-r4-r6-changes
original_url: "https://www.linkedin.com/pulse/evaluating-fhirs-evolution-ai-assisted-analysis-r4r6-josh-mandel-md-2srmc"
linkedin_id: 2srmc
banner: https://media.licdn.com/dms/image/v2/D5612AQH8UJ1qvdU-pw/article-cover_image-shrink_720_1280/B56Za2mF3cGgAI-/0/1746820165955?e=2147483647&v=beta&t=hN2fKMa0sAknPB0mf7ChtVL5prLIKr3-z6nGaf2depM
---

Created on 2025-05-09 18:38

Published on 2025-05-09 19:56

As the FHIR community steers towards our R6 release, a key objective is to provide stable, mature resources. With the first normative ballot in the R6 publication sequence anticipated this fall, let's assess how FHIR is evolving.

This post describes a quick experiment to automate analysis of FHIR's evolution from R4 to the current R6 draft build, with the aim of creating migration guides detailing changes relevant to FHIR spec editors and implementers. (I also analyzed downstream impact on Implementation Guides, taking the US Core IG as a representative example.)

This work tests a set of techniques using Large Language Models (LLMs) to establish a coherent cross-specification view (a notable challenge given FHIR's scale).

If you just want to check out the analysis pipeline + results, everything is open-source at <https://github.com/jmandel/fhir-diff/tree/main/analysis> .

### The Challenge: Tracking Changes in a Large, Evolving Specification

Getting a holistic view of the accumulated changes from FHIR R4 to R6 means analyzing decisions from dozens of workgroups over 6+ years of develpoment and ~150 resource definitions. Changes accrue in modeling style, data organization, and resource scope, not to mention minor updates to cardinalities, data types, terminology bindings, and constraints.

### AI-Driven Analysis Pipeline

This experiment centered on using an LLM for analytical tasks, with an opinionated, phased information flow from raw HTML and JSON inputs toward comprehensive migration reports. This involved crafting detailed instructions to guide the LLM, including:

* **Defining Output Structure:** Specifying Markdown format with consistent section headers.
* **Guiding Focus:** Prioritizing "actionability & implementer focus" and "meaningful changes."
* **Providing Examples:** Using well-crafted examples of desired output.

The project's workflow, orchestrated by TypeScript scripts (run with Bun), followed these phases:

Figure 1: High-level project workflow.

1. **Data Ingestion & Preparation:** HTML definitions for R4 and R6 resources were scraped. For US Core, JSON StructureDefinitions were also retrieved, preprocessed, and organized into a profile hierarchy.
2. **LLM Analysis – Phase 1 (Base Resources):** The LLM first generated structured Markdown summaries for each resource version. Then, it compared these summaries to produce a "migration guide."
3. **LLM Analysis – Phase 2 (US Core IG Impact):** For US Core profiles, the LLM received the profile's definition and the relevant base resource R4-R6 migration guide, then analyzed how base changes affected profile constraints.

### Outputs and Selected Findings

The project produced Markdown reports:

* **Base Resource Migration Guides**: Detailing R4-to-R6 changes per resource. See [**analysis/diff.**](https://github.com/jmandel/fhir-diff/tree/main/analysis/diff)
* **US Core Profile Impact Reports**: Assessing R6 impact on specific US Core profiles. See [**analysis/us-core-migration.**](https://github.com/jmandel/fhir-diff/tree/main/analysis/us-core-migration)

### Selected Findings

Here are a few examples of patters the LLM-assisted analysis surfaced.

**For Specification Editors (Core Spec & Implementation Guides):**

* Improved Status Semantics: There's clearer differentiation in status concepts. For example, Device.status in R6 now specifically refers to the record's status, with physical availability addressed by the new "Device.availabilityStatus". Similarly, Encounter.status (overall encounter) is now distinct from the new "Encounter.subjectStatus" (patient's state within the encounter).
* Base resource element changes directly necessitate IG updates. For instance, the removal of "DocumentReference.authenticator" from the R6 base requires the US Core DocumentReference profile (which mandates authenticator) to be revised to use the new R6 attester element.

**For Implementers:**

* Implementers need to adapt to shifts in how core relationships are modeled. A key example is the removal of direct linkage elements like Device.patient from the R4 Device resource. In R6, such associations are now managed via separate linking resources (e.g., DeviceAssociation), requiring changes to data models and API interaction patterns.
* Modifications to search parameter behavior, such as Observation.value-string in R6 only searching Observation.valueString (unlike R4 which also searched valueCodeableConcept.text), could break existing R4-based queries and necessitate client-side adaptations.

### Conclusion

This experimental project explored an LLM-assisted methodology for analyzing FHIR specification evolution. The process generated structured, human-readable reports that identify key changes and their implications. While not a substitute for human expertise or formal specification processes, this approach shows potential as a tool to aid the FHIR community in navigating the complexities of standards development. The insights generated are a starting point for the detailed work that HL7 work groups and the community perform to refine and ballot the standard.