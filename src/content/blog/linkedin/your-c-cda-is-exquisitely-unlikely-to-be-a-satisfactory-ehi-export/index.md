---
title: "Your C-CDA Is Exquisitely Unlikely to Be a Satisfactory EHI Export"
date: 2026-02-16T15:33:00
added_at: 2026-04-03
slug: your-c-cda-is-exquisitely-unlikely-to-be-a-satisfactory-ehi-export
original_url: "https://www.linkedin.com/pulse/your-c-cda-exquisitely-unlikely-satisfactory-ehi-josh-mandel-md-gr90c"
linkedin_id: gr90c
banner: ./banner.jpg
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7429191089699581952"
  share_id: "7429191089699581952"
  share_type: "ugcPost"
  posted_at: "2026-02-16T15:53:03"
  visibility: "MEMBER_NETWORK"
  commentary: |
    About 25% of the EHRs I've reviewed so far appear to be surfacing C-CDA clinical summaries as full (b)(10) EHI exports. Read on to understand why lossy mapping falls short of the requirement to export everything (early data from my cross-vendor EHI Export analysis).
---

Under [§170.315(b)(10)](https://www.healthit.gov/test-method/electronic-health-information-export), certified health IT must be able to export **all** electronic health information stored by the product. Not a summary/highlights, but everything: billing, insurance, specialty clinical data, administrative records used for decision-making, anything in the [Designated Record Set](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-E/section-164.501) that's stored electronically.

So how are vendors actually doing it?

### The numbers

I've been [reviewing the published (b)(10) documentation](https://joshuamandel.com/ehi-export-analysis/) for certified products (using tons of AI and automation that wasn't possible the last time I did a survey) by accessing whatever each vendor has posted at their CHPL-registered EHI documentation URL and examining what it actually says. This is a work in progress (and I will have much more to say about it in upcoming articles) but the early qualitative and quantitative findings are striking.

Of the EHR product families analyzed so far, roughly **25% describe an export that is essentially just C-CDA**, with no indication of any supplemental data beyond what standard C-CDA templates can represent. None of these provide a product-specific data dictionary. None include sample export files. None describe how specialty or administrative data makes it into the export. Their documentation often consists of a brief description saying the export is "C-CDA XML" (sometimes with a link to the generic HL7 C-CDA spec) and nothing more.

### I'm not dissing C-CDA...

I should be clear: I'm not picking on C-CDA. I know many of spec authors, and C-CDA is a reasonable format for the job it was designed to do: **document-oriented exchange**. This means sharing a consultation note, a discharge summary, a referral package, a summary document... all the kinds of clinical documents that need to move between healthcare providers. That is an important and very hard job.

But even in its intended use case, C-CDA implementations are notoriously lossy. Back in 2013, I helped launch the [SMART C-CDA Collaborative](https://smarthealthit.org/2013/07/introducing-the-smart-c-cda-collaborative/) to investigate why C-CDA documents from different EHRs were so inconsistent, and to try to drive the industry toward better behaviors. The core problem is structural: C-CDA is a *mapping exercise*. Implementers look at their internal database, look at the available C-CDA templates, and try to find the closest match. When there's no good match (or when the mapping seems a little bit challenging) **they reach for an artisanally curated "flavor of null" instead.**

This is how C-CDA works. The specification provides a set of templates — medications, problems, allergies, procedures, results, vital signs, a handful of others — and implementers fill what they can. The question C-CDA is trying to answer is: *how do I meet a specific use case for document-oriented exchange?* It is explicitly **not** trying to answer: *how do I take every piece of information in my database and make sure it lands somewhere in this document so an outside party can reconstruct it?*

### Why this matters for EHI export

The (b)(10) requirement asks exactly that second question. The export must include **all** EHI stored by the product. Not just the data that happens to map cleanly into C-CDA sections.

Consider what a typical EHR actually stores beyond a “clinical summary”:

* Billing and revenue-cycle artifacts (charge capture details, remits/ERAs, claim statuses, denials, worklists)
* Specialty- or site-specific documentation (custom podiatry/dental/behavioral health/corrections templates and flowsheets)
* Medication *administration* history (who administered what, when, route/site, barcode scans, witnesses, overrides), not just a reconciled med list
* Scheduling/operational context (resource schedules, check-in/out timestamps, cancellations/no-shows, referral/authorization workflows)
* Internal messaging, tasks, routing rules, and queue state
* Scanned documents and images (often as unstructured attachments with minimal metadata)
* Arbitrary custom forms, questionnaires, and configurable fields that vary by customer

C-CDA can represent some related pieces (e.g., coverage/payers, administered medications at a summary level, and unstructured documents/attachments). But it was designed for standardized clinical documents (CCD/Discharge Summary/Progress Note), not as a complete, lossless export of the entire operational database of an EHR.

Could you extend CDA with local templates/sections to carry more of this? Yes, CDA is extensible. In practice, though, doing so becomes a new interoperability profile and a nontrivial engineering effort: you’d have to define, implement, and validate a large set of custom templates to cover customer-specific fields and operational artifacts. The result would be “a CDA-based EHI export,” but it wouldn’t resemble the off-the-shelf C-CDA exports that ship today.

What this quarter of vendors have done appears to be taking their **existing** C-CDA export (the one they built years ago for clinical document exchange) and relabing it as EHI export. The [ONC factsheet](https://www.healthit.gov/wp-content/uploads/2023/02/b10_EHI_Export_Factsheet_FINAL.pdf) even mentions C-CDA as an example of an acceptable export format, which may have given vendors the impression that their existing implementation would suffice. But the factsheet is talking about the *format*, not the *scope*. Using C-CDA as your export format is conceivably fine. Using your existing C-CDA clinical summary as your entire EHI export is not, unless your product happens to store nothing beyond what C-CDA templates represent and you have fully mapped everything in all cases, which for a real EHR is essentially never true.

*Note: (b)(10) conformance is attestation-based; it does not require ONC-ATL testing; developers attest to an ONC-ACB, which reviews the attestation. That likely contributes to the extreme variability in what vendors publish at their CHPL export-format documentation URL.*

### The telltale sign

> "EHI is exported in C-CDA XML format that complies with USCDI v1 requirements"

...and then links to the [generic HL7 C-CDA implementation guide](https://www.hl7.org/implement/standards/product_brief.cfm?product_id=492) as their format documentation, with no data dictionary, no schema, no sample files, and no description of what's actually in the export. That's a vendor who took their existing C-CDA export, pointed at it, and called it done.

USCDI defines a *minimum* floor for clinical data exchange. It is a subset of what an EHR stores. An export that "complies with USCDI v1 requirements" is, by definition, a summary. It might be a perfectly good summary. It is not EHI.

### What would be credible?

A credible EHI export using C-CDA as its format would need to:

1. **Document every data domain the product stores** and map each one to a specific location in the C-CDA output
2. **Use custom sections and entries** for data that doesn't fit standard C-CDA templates
3. **Provide a product-specific data dictionary** describing their conventions and custom extensions
4. **Include sample files** demonstrating that specialty data actually appears in the export

I haven't seen a single one of the C-CDA-only vendors do any of this.

It is, of course, possible that behind these thin documentation pages, some vendors have built comprehensive exports that happen to use C-CDA as the wire format and happen to not document it. But the whole point of the (b)(10) documentation requirement is that an outside party (e.g., a patient, a new provider, a health IT developer) should be able to look at the published documentation and understand what the export contains. If the documentation says "C-CDA" and links to the HL7 spec, the only reasonable interpretation is: you're getting a clinical summary.

---

The [full set of documentation reviews](https://joshuamandel.com/ehi-export-analysis/) is a work in progress, covering a growing number of product families. The [methodology](https://joshuamandel.com/ehi-export-analysis/#about) and [source data](https://github.com/jmandel/ehi-export-analysis) are open.

*Analysis by* [*Josh Mandel, MD*](https://www.linkedin.com/in/joshuamandel/)*. Assessments are AI-assisted and may contain mistakes (please* [*report errors or corrections*](https://github.com/jmandel/ehi-export-analysis/issues/new)*).*