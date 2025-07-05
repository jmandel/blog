---
title: "EHR Association's Proposal Would Deregulate the Foundations of Patient Access and Population Management"
date: 2025-04-30T15:04:00
slug: ehr-association-s-proposal-would-deregulate-the-foundations-of-patient-access-and-population-management
original_url: "https://www.linkedin.com/pulse/ehr-associations-proposal-would-deregulate-patient-josh-mandel-md-xbzke"
linkedin_id: xbzke
---

Created on 2025-04-30 15:04

Published on 2025-04-30 15:32

A recent letter from the HIMSS Electronic Health Record (EHR) Association to ONC outlines recommendations ostensibly aimed at "[Smart Deregulation in Health IT](https://www.ehra.org/sites/ehra.org/files/EHR%20Association%20Letter%20to%20ASTP-ONC%20-%20Certification%20Program%20Deregulatory%20Suggestions.pdf)." While streamlining regulation is beneficial when done thoughtfully, the letter includes proposals that would dismantle critical data access capabilities mandated by the 21st Century Cures Act. Specifically, the recommendations to **remove the EHI Export criterion** and to **eliminate FHIR Bulk Data export support** from the Health IT Certification Program are deeply concerning.

These capabilities represent essential, complementary foundations required for robust individual patient data access and effective population data management. I believe removing these requirements would be a significant regression, undermining patient rights, hindering research and innovation, and ignoring the fundamental reasons these regulations were established.

Why Regulation Provides Essential Foundations
---------------------------------------------

In the complex healthcare IT market, incentives are not always aligned to ensure robust data liquidity. While EHR vendors compete on many features, providing comprehensive, easy-to-use *export* capabilities – especially for the entirety of a patient's record ("EHI Export") or for efficient, standardized export across populations ("Bulk Data") – requires significant investment. The primary value often accrues downstream to patients, providers switching systems, researchers, public health agencies, or application developers.

Without clear regulatory drivers like those in the Cures Act (and ONC's [Cures Act Final Rule](https://www.healthit.gov/topic/oncs-cures-act-final-rule)) the market historically underprovided these foundational capabilities, sometimes favoring vendor lock-in or implementing only the bare minimum. The ONC Certification Program established these export functions as baseline infrastructure, ensuring a level playing field and guaranteeing that essential data pathways exist, regardless of immediate market demand for specific downstream applications.

Deconstructing the Flawed Arguments for Removal
-----------------------------------------------

The EHRA letter justifies removing these criteria by citing low utilization, implementation burden, and perceived redundancy. These arguments miss the mark.

* **Addressing "Low Utilization":** Citing low current use, especially for Bulk Data, ignores that utilization is often a **lagging indicator** for any foundational infrastructure mandate. Adoption takes time as the ecosystem builds tools and workflows. Furthermore, emerging mandates and use cases – like CMS quality reporting requirements, Alternative Payment Model data needs, and real-world evidence generation for research increasingly *depend* on the scalable, standardized access Bulk Data provides. Removing it now cuts off support just as demand crystallizes.
* **Addressing "Implementation Burden":** While vendors face a one-time cost to implement these robust export capabilities, this pales in comparison to the **recurring, system-wide costs** currently borne by patients, providers, researchers, and public health agencies due to the lack of reliable, complete data access. Manual chart abstraction, redundant data entry, and complex one-off data requests represent immense friction and expense that standardized EHI and Bulk exports are designed to alleviate. Investing in the foundation reduces long-term, distributed burden.
* **Addressing "Redundancy":** Suggesting that standard APIs like SMART on FHIR substitute for these exports misunderstands their distinct roles. APIs offer crucial *transactional* access to *standardized* data points but cannot replace the **comprehensive depth** of a full EHI Export (including non-standardized data and notes) nor the **population-scale efficiency** of Bulk Data export. We need the right tool for the job: APIs for specific queries, Bulk Data for efficient scale, and EHI Export for complete coverage. They are complementary, not redundant.

**Don't Reward Poor Implementation:** The letter effectively blames the *requirements* for *failures in their implementation*. <!-- YOUTUBE:40DesxAUF\_c --> and broader industry observations show that vendor implementations are often lacking – documentation can be poor or missing (sometimes nonsensically pointing to summary CCDAs instead of full EHI), processes can be opaque or disabled, and data completeness may be questionable. Similarly, Bulk Data adoption requires EHR-side implementations that deliver data at scale, followed by time for the ecosystem to build tooling and establish workflows. These challenges demand *better enforcement, clearer guidance, and improved vendor implementation*, not regulatory abandonment. Removing the rules now simply rewards inaction or inadequate execution.

### Distinct, Complementary Roles (The "Fast and Full" Strategy)

EHI Export and Bulk Data serve different, essential purposes and are not interchangeable with other methods. We need both the "Full Coverage" of EHI Export for completeness and the "Fast Lane" of Bulk Data for standardized scale. Weakening either leaves a critical gap.

**FHIR Bulk Data = Fast Lane (Breadth & Efficiency):** This provides efficient, *standards-based* export of key data elements across *entire populations*. It's crucial for population health, quality reporting, large-scale research, and system transitions. Individual API calls are inefficient for this scale.

**EHI Export = Full Coverage (Depth):** This is the regulated backstop guaranteeing access to the entire, computable electronic record (standardized or not) with vendor documentation. EHI Export is the only mechanism ensuring access to the vast "long tail" of health data. Neither standard APIs (lacking depth/completeness) nor typical HIPAA DRS requests (lacking guaranteed computability and documentation) can replace these vital functions. It serves two critical, distinct functions, both targeted by the EHRA proposal:

* ***Single Patient EHI Export:*** Directly advances the patient's right of access to their *complete* record, far beyond just the data available via standardized APIs. This is fundamental for patient empowerment and control.
* ***Population EHI Export:*** Reduces provider switching costs and "data gravity," fostering EHR market competition, AND critically enables the full leverage of complete patient records at scale**.** This unlocks innovative pathways for advanced analytics, deep population health insights, comprehensive AI-oriented workflows, and research that requires complete data.

Foundations for Today's Needs and Tomorrow's Innovations
--------------------------------------------------------

These export capabilities are fundamental not just for meeting current needs – empowering patients with their data, enabling research, supporting public health, facilitating quality measurement – but also for enabling the next generation of health IT innovation.

As I've explored in previous posts (e.g., "[Prior auth is friction. Can't we just talk](/posts/prior-auth-is-friction-can-t-we-just-talk)?") and demos (e.g., "[Theory to practice with LLM Agents, MCP, and EHR search](/posts/theory-to-practice-llm-agents-using-mcp-tools-on-real-ehr-data-with-demo)"), advanced AI agents can transform workflows like prior authorization or clinical data analysis. However, these agents rely heavily on the foundational data access guaranteed by these regulations:

* **Fueling AI Agents:** An LLM agent needs reliable API access (at the population level, this means Bulk Data ) *and* often requires the deep, nuanced information found only in the complete record accessible via EHI Export (like unstructured notes or non-standard flowsheet data).
* **Enabling Tools on Data:** Giving agents tools (like grep, SQL, etc) to operate on data is powerful, but they need the *data* itself. EHI Export provides the comprehensive dataset (often in structured, tabular formats amenable to these tools), while Bulk Data delivers standardized slices efficiently.

Removing guaranteed access to the full EHI or efficient population-level standardized data fundamentally limits our ability to build, train, and deploy these powerful new tools safely and effectively. It pulls the rug out from under the innovation these regulations were intended to foster.

Preserve Foundations to Enable Choice and Competition
-----------------------------------------------------

In an era focused on reducing regulatory burdens and fostering market-driven healthcare solutions, it’s tempting to target existing rules. However, eliminating foundational data access capabilities like EHI Export and Bulk Data Access would be a profound mistake – undermining the very market functions deregulation aims to enhance.

These are not bureaucratic hurdles; they are the **essential infrastructure** mandated by Congress to ensure patients can access their complete record and that data can flow efficiently for system-wide improvements. Reliable access to these capabilities is the bedrock upon which patient choice, application innovation, research, and genuine market competition are built. Removing these guarantees doesn’t reduce friction; it rebuilds data silos and stifles the market.

Instead of dismantling necessary foundations, the focus should be on **ensuring they work reliably**. Effective verification of these capabilities – confirming EHI Exports are complete and usable, and Bulk Data performs as specified – delivers far more value than simply checking a box at certification.