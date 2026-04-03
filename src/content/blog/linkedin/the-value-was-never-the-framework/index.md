---
title: "The Value Was Never the Framework"
date: 2026-01-22T20:56:00
slug: the-value-was-never-the-framework
original_url: "https://www.linkedin.com/pulse/value-never-framework-josh-mandel-md-rc6gc"
linkedin_id: rc6gc
banner: ./banner.jpg
---

Back in 2016, I pushed back against the idea of "Custom Resources" in FHIR.

My objection wasn't about chaos or control. It was about using the right tool for the job. If your wanted to design a new API outside of the standards process, technologies like OpenAPI and JSON Schema were simply better. They were purpose-built for defining data structures, with excellent tooling and straightforward design.

We didn't need a "FHIR-flavored" API toolkit. If you strip away the shared consensus -- the agreement on what a patient or an observation *means* -- then FHIR is just a heavy, complex modeling framework. Why use a worse version of those dedicated tools?

The only reason to endure FHIR's complexity was to get the **Shared Models**. It was the fact that thousands of us agreed.

But looking at **FHIR R6**, it seems we've done exactly what I argued against: We've architecturalized "Additional Resources." We've evicted resources like InventoryItem and Permission from the core specification, moving them into "Incubator IGs." We've created a pathway for resources to be developed outside the monolithic ballot cycle.

Surprisingly, I think it's the right move. Not because we're endorsing FHIR as a generic toolkit, but because we've finally built a better maturity model.

**Monospec**

For FHIR's first decade, we operated on a "One Big Build." Every resource, from the foundational Patient to a cutting-edge GenomicStudy, was locked to the same multi-year release train.

This created impossible tension. Domains that needed to iterate weekly were shackled to infrastructure that needed to move glacially. We prioritized the purity of a single, synchronized model over the reality of software development.

R6 formalizes a split. The core models (infrastructure, terminology, administrative resources, most clinical content) enters a long-term stable state. This lets the semantic foundation solidify. Simultaneously, we acknowledge that not all content matures at the same pace.

**Incubators: A Better Maturity Model**

The technical change in R6 is subtle but profound. A resource's meaning is no longer defined solely by its resourceType string (like "Patient"). It is now keyed to a canonical, versioned URI, as seen in examples like "ViewDefinition", whose full type is http://hl7.org/fhir/uv/sql-on-fhir/StructureDefinition/ViewDefinition|2.0.0-pre.

This still isn't an open invitation to use FHIR as a toolkit (though that remains a possibility). It's a refinement of FHIR's governance and change management. HL7 retains authority over the namespace. An "Incubator" is a dedicated, managed track within HL7's own processes, allowing specific Working Groups to iterate on content at a more appropriate velocity without dragging the entire specification or waiting for a core ballot. It is, in essence, a formalization of the maturity model we always needed but didn't have.

**The AI Factor**

Yes, "Additional Resources" are a way to iterate *within* HL7. But a separate, parallel reality has always existed: using FHIR's open-source tooling and specifications as a standalone toolkit for your own projects, without seeking formal HL7 compliance or blessing.

In 2016, I dismissed this approach. The interoperability cost was too high. If you built your own models with FHIR's tools, anyone receiving your data needed a human to decipher your custom definitions and write manual mapping code.

Today, that cost has collapsed. This is where LLMs change the calculus. If you use FHIR tooling privately as your framework, the burden on a recipient is no longer a human analyst. An LLM can ingest your custom StructureDefinitions and map them to core FHIR resources or another proprietary model with minimal effort. The penalty for choosing a complex framework over a sleek one is dramatically lower when the translation layer is automated.