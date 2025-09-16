---
title: "Deregulation of Certified Health IT: Cuts to Real World Testing"
date: 2025-07-02T21:07:00
slug: deregulation-of-certified-health-it-cuts-to-real-world-testing
original_url: "https://www.linkedin.com/pulse/deregulation-certified-health-cuts-real-world-testing-josh-mandel-md-odpdc"
linkedin_id: odpdc
banner: ./banner.png
---

Created on 2025-07-02 21:07

Published on 2025-07-02 22:56

*Personal note: The value proposition of regulation and deregulation is full of trade-offs. My personal take is that the Real World Testing cuts are a* ***reasonable, pragmatic place to ease off on requirements****, opening up time and attention for Certified Health IT products to focus on more pressing concerns. Still, I would have maintained a requirement for testing EHI Export, which otherwise risks falling into disrepair. The article below explores changes under the new enforcement regime.*

On Monday, ASTP/ONC [announced](https://www.healthit.gov/topic/real-world-testing-condition-and-maintenance-certification-requirements-enforcement) they will no longer enforce most Real World Testing (RWT) requirements for Certified Health IT. To most, this is an obscure policy shift. But it effectively ends a short-lived, and arguably unintentional, era of transparency into how health IT systems actually perform.

### What Was Real World Testing Supposed to Do?

The idea behind RWT, mandated by ONC's 21st Century Cures Act Final Rule, was simple. Instead of just proving software *can* work in a controlled lab to get certified, vendors had to publicly report on how their technology *does* work in the messy reality of day-to-day clinical practice. It was meant to measure performance "in the wild," tracking how data flows between different hospitals, clinics, and public health agencies.

The new policy eliminates this mandate for almost all areas, with one key exception: vendors must still report on the performance of the APIs that allow patient and provider applications to connect to their EHRs.

To see what this means in practice, let's look at the most recent reports from two vendors at different ends of the market: [Oracle Health](https://www.oracle.com/health/regulatory/certified-health-it/#real-world-testing-lnk), focused on large inpatient systems, and [athenahealth](https://www.athenahealth.com/onc-certified-health-it), focused on ambulatory practices. Their reports show exactly what kind of data we will now lose.

### What We Lose: A Public, Quantified View of the Interoperability Landscape

The primary loss from the end of broad Real World Testing is visibility into the performance of asynchronous, multi-party transactions. *These are precisely the areas where interoperability is most challenging, as success depends on multiple actors, not just the EHR vendor. The RWT reports provided a public accounting of this shared responsibility.*

Here are some concrete examples of what we will no longer see.

**From Oracle Health's Reports, we'll lose visibility into:**

* **EHR-to-Pharmacy Network Friction:** The 2023 e-prescribing report for the Millennium platform detailed specific reasons for failures in the national pharmacy network. It quantified issues such as a pharmacy rejecting a request due to a "delay in response," variations in state-specific compliance rules for certain medications, or a pharmacy not supporting a specific transaction type like a RxChange request. This data provided a diagnostic view of the friction points between the EHR and thousands of external pharmacy endpoints.
* **The Scale of Inpatient-to-Ambulatory Transitions:** The 2024 report showed that Millennium customers created **38.8 million** standards-conformant C-CDA documents per month for care transitions. This number served as a direct, public measure of the sheer volume of data being exchanged as patients move from the inpatient setting. Tracking this volume year-over-year would have provided a benchmark for the growth of hospital-based interoperability.
* **Legacy System Interoperability Challenges:** The 2024 report on the Soarian platform revealed an inbound C-CDA error rate of **92.96%**. While Oracle noted these errors originated from *external* systems, this data point provided a stark, public measurement of the difficulty a legacy platform faces when trying to receive data from the modern health IT ecosystem.

**From athenahealth's Reports, we'll lose visibility into:**

* **The Health of the Direct Messaging Network:** The 2023 report on C-CDA exchange detailed specific Direct Secure Messaging failures, including "Unable to verify trust certificate" and "Certificate is expired." This data provided a quantified look at the operational overhead and specific technical challenges required to maintain trusted communication channels across a fragmented network of thousands of independent ambulatory practices.
* **Public Health Reporting and Data Mapping Challenges:** The 2024 report on public health interfaces showed that for immunization submissions, there were **102,894 errors** that "must be managed directly by customers." It further specified that **526** of those errors were due to "EHR database to file mapping updates required because of individual registry requirements." This data highlighted the specific, burdensome work that practices must undertake to conform to varying state registry specifications.
* **The Scale of Patient-Initiated Interoperability:** The 2024 report for their patient portal (athenaCommunicator) documented **1.6 million successful views and downloads** of clinical summaries by patients over a three-month period. This was a direct measure of patient engagement with their own data through a core portal function, a metric that will now be lost.

In each of these cases, the RWT reports forced vendors to publicly document the messy, nuanced reality of how their systems interact with the outside world. This data provided a basis for objective analysis that is now gone.

### A Vulnerable Capability: EHI Export

Testing for Electronic Health Information (EHI) Export (§170.315(b)(10)) is a notable loss. This capability, which allows patient- and population-levle export all data, is a foundational backstop for data liquidity and patient rights under the Cures Act. Unlike standardized APIs, it often has low organic usage, making it particularly susceptible to neglect without a testing mandate. The RWT reports gave us a rare, public look at its real-world implementation.

**The data from athenahealth** shows specific, baseline usage across their network. Their **2024 RWT results** report that from January to September 2024 (for authorized users):

* **Single-patient exports:** **90 customers** performed **656** total export requests.
* **Multi-patient exports:** **168 customers** performed **3,283** total export requests.

These numbers establish a public baseline of both the volume and the breadth of adoption across their network.

**The timeline from Oracle Health** illustrates the direct impact of the policy change. Oracle's 2025 RWT *Plan* introduced EHI Export testing for the first time, with a methodology for testing single-patient and population capabilities across multiple products. For their "Patient Portal – MMD" module, where they noted no real-world requests for population export had been received, their plan was to conduct a "mock export that would closely mirror real world conditions" to prove functionality. The ONC's enforcement discretion, announced in June 2025, cancels the reporting requirement for these tests before the results for the 2025 cycle were due.

### Other Incidental Transparency We Lose

The RWT reports also provided objective data points on product strategy and adoption that are not typically found in marketing materials. For instance, **Oracle's 2023 report** on its Soarian platform justified its test methodology by stating there were **"no Soarian Clinicals clients live in production for real world testing"** of Electronic Case Reporting.

### What We Keep: A Snapshot of Vendor API Performance

The RWT requirements that remain focus on the performance of a vendor's own FHIR APIs (§170.315(g)(7)-(10)). These tests measure a direct, two-party interaction between a third-party application and the EHR's own production servers. In effect, we are left with a report that says, "my side is okay."

**1. Vendor Server Performance at Scale**

We will still get data on the reliability of a vendor's production infrastructure. Both vendors provide a clear metric for this.

* From **Oracle Health's 2024 report:** A **99.71% success rate** across **22.8 billion** single-patient FHIR API transactions.
* From **athenahealth's 2024 report:** A **99.81% success rate** for "API Requests Served (not including OAuth calls)."

This data provides an attested, public measure of infrastructure stability at scale. We will still know if a vendor's servers are online and performing well under load.

**2. Adoption Metrics for New API Standards**

We also retain a key measure of new technology adoption. The requirement for the (g)(10) criterion, which includes the Bulk FHIR API, remains.

* The **Oracle Health 2024 report** is highly specific on this point, noting that **17 customers** had completed a Bulk Data extract. This is a direct, public benchmark for tracking the adoption curve of this complex standard.
* The **athenahealth RWT plan** covers the (g)(10) criterion, but their results summary does not provide a specific count of customers who have adopted Bulk Data. Instead, it bundles all API performance into the overall success rates mentioned above.

Even under the current regime, the *specificity* of what vendors choose to disclose in their public reports can vary. The loss of broader RWT enforcement may encourage vendors to adopt a less-detailed reporting style even for the API domains where mandates remain.