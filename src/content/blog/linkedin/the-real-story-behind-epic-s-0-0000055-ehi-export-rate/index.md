---
title: "The Real Story Behind Epic's 0.0000055% EHI Export Rate"
date: 2025-06-21T15:58:00
slug: the-real-story-behind-epic-s-0-0000055-ehi-export-rate
original_url: "https://www.linkedin.com/pulse/real-story-behind-epics-00000055-ehi-export-rate-josh-mandel-md-vuo7c"
linkedin_id: vuo7c
banner: ./banner.png
---

Created on 2025-06-21 15:58

Published on 2025-06-21 16:56

### Epic's Argument: Nobody Uses It, and Nobody Wants It

In their recent response to CMS and ONC's "Health Technology Ecosystem" RFI, Epic Systems stated:

> **"EHI Export has not achieved widespread adoption as a data-exchange mechanism and therefore may have limited utility regarding LLM adoption. Across our customer community, EHI Export accounted for only ~0.0000055% of medical-record requests from December 2024 – May 2025. Our customers have told us that EHI Export releases... fail to meet the needs of requestors."**

To put Epic's 0.0000055% figure in perspective: this suggests only a handful of people across the entire country successfully obtained an EHI Export during those six months. Not a handful per hospital, not a handful per state—a handful total, nationwide.

Epic argues that minimal usage and user dissatisfaction suggest EHI Export lacks value. However, this conclusion misses the mark:

* The negligible usage reflects implementation barriers, not lack of need
* The dissatisfaction stems from execution challenges that Epic has not resolved

To Epic's credit, they've engaged with feedback. When I identified missing data elements like vital signs in early exports, Epic's team worked to populate these fields. They've answered questions on calls. But fundamental usability issues persist.

---

### Epic's Evolving Position: From Removal to Redefinition

Initially, Epic and the Electronic Health Record Association (EHRA) advocated removing the EHI Export requirement entirely. Their latest position suggests keeping it -- but limiting "all EHI" to USCDI elements already available through FHIR standards.

This shift represents a tactical retreat -- recognizing that outright removal is unlikely, they're now attempting to gut the requirement from within. The term "core data" in USCDI should alarm us: it explicitly indicates a subset rather than the comprehensive access patients deserve "without special effort" under the Cures Act.

---

### My Testing Experience: Two Hospitals, Too Many Barriers

I tested EHI Export from two Epic institutions. Both experiences were deeply frustrating:

### Hospital A: Initial Promise, Then Regression

* Hospital A's portal initially featured an "Export My Record" button
* My first request stalled until an Epic executive noticed my public feedback and facilitated resolution
* Epic's team engaged constructively, adding missing data elements based on my input
* Unfortunately, Hospital A later removed the button entirely, requiring phone-based HIM requests

### Hospital B: Unprepared for the Requirement

* No visible export option existed in the portal
* HIM staff hadn't heard of EHI Export, though they worked diligently once educated
* The manual process eventually succeeded, but revealed systemic training gaps

### The Documentation Challenge

Both hospitals provided TSV files mirroring Epic's Clarity structure. Epic answered many technical questions during support calls, but these individual clarifications rarely translated into improved documentation. The exports included:

* Extensive table and column listings
* Basic field descriptions
* Missing: explanation of many terms, basic orientation to the concepts and modeling techniques employed, details on foreign key relationships and join logic, and practical usage guidance

Even with Epic's team responding to my specific questions, the lack of comprehensive documentation made meaningful analysis exceptionally difficult.

---

### Design Choices

Epic exports data using their internal Clarity warehouse structure -- a format designed for hospital analysts familiar with Epic's ecosystem. While Epic's team helped me navigate some of this complexity when I raised specific issues, a more accessible approach would better serve patients and external developers.

Epic should provide:

* Data structured as the EHR internally represents it, with consumer-friendly documentation
* The same comprehensive documentation that internal teams access via UserWeb
* Or alternatively: Self-describing formats that don't assume extensive Epic knowledge

---

### Defending Comprehensive Access

When Epic suggests limiting "all EHI" to USCDI elements, they're proposing a significant reduction in scope. While USCDI captures essential data, patients' rights under the Cures Act explicitly extend to all electronic health information. Epic's technical engagement on specific issues doesn't justify narrowing the overall scope.

---

### Collaboration Opportunity: Human-Readable Formats

One straightforward improvement would augment EHI Export tables with PDF representations -- i.e., providing human readable content directly alongside the structured data.

Epic already generates comprehensive, readable PDFs for full records releases. HIM departments use this functionality daily to fulfill release of information requests. Adding a human and LLM-readable PDF representation of the full chart (or patient-selected sections) to the EHI Export would:

* Give patients immediate access to their information in a familiar format
* Provide context that makes the structured data meaningful
* Enable LLMs to extract and understand information without reverse-engineering Epic's database schema
* Serve as a Rosetta Stone for understanding the TSV relationships

The infrastructure already exists and would be a powerful adjunct to the current EHI Export pipeline.

---

### From Mandate to Market Leadership

I appreciate the help Epic provided in generating and working with my EHI Export last year, and I look forward to continued collaboration on improving these capabilities. The next steps are clear:

**For Epic and other EHRs:**

* Make portal controls visible and easily accessible
* Transform support interactions like mine into systematic documentation improvements
* Develop tiered export options including structured as well as human- and LLM-readable PDFs (simple for patients, comprehensive for developers)
* Enable EHI Export access for patient-designated apps through SMART on FHIR, alongside existing USCDI data

**For the broader ecosystem:**

* Maintain accountability for comprehensive implementation
* Share successful implementation patterns across institutions
* Create community resources to supplement vendor documentatioFrom

The negligible usage of EHI Export isn't a verdict on its value, but a clear signal that the current design is not fit for purpose. This is not a reason to abandon the goal, but an invitation to perfect the mechanism. By shifting from a compliance mindset to one of user-centered design, EHRs have a unique opportunity to convert a mandated function into a celebrated feature.

The solutions +visible portal controls, layered export formats including PDFs, and transparent documentation) are not insurmountable technical hurdles. They are the necessary steps to build a bridge from a frustrating process to genuine patient empowerment. This is a moment to lead the industry, turning a point of friction into a powerful demonstration of its commitment to the entire health ecosystem.