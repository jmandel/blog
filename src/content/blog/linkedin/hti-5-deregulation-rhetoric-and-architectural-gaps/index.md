---
title: "HTI-5: Deregulation, Rhetoric, and Architectural Gaps"
date: 2026-01-14T17:04:00
added_at: 2026-04-03
slug: hti-5-deregulation-rhetoric-and-architectural-gaps
original_url: "https://www.linkedin.com/pulse/hti-5-deregulation-rhetoric-architectural-gaps-josh-mandel-md-7gw1c"
linkedin_id: 7gw1c
banner: ./banner.jpg
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7417252773387493376"
  share_id: "7417252773387493376"
  share_type: "ugcPost"
  posted_at: "2026-01-14T17:14:27"
  visibility: "MEMBER_NETWORK"
  commentary: |
    On ASTP’s HTI-5 proposal: removing legacy mandates clears the floor for FHIR, but dismantling reporting requirements leaves us without the data to measure the transition. Click for the full article...
---

The latest proposed rule from ASTP/ONC frames a significant deregulation of the Health IT Certification Program as a necessary pivot toward a "FHIR-forward future." The document uses the rhetoric of modernization to justify the removal of long-standing requirements for legacy standards like C-CDA and Direct, and I'm generally a fan (but the devil is in the details).

The agency’s logic is effectively "addition by subtraction": by deleting the floor for older technologies, developer resources will naturally reallocate toward modern, FHIR-based exchange.

> America’s interoperability arc in health care has bent decisively toward FHIR-based APIs... we propose to aggressively reduce and remove long-standing functionality-oriented and non-FHIR-based certification criteria from the Certification Program... it enables ASTP/ONC to reset the Certification Program’s regulatory scope and establish a new foundation on which to build FHIR-based API requirements in the future. (Preamble)

There is undeniable value in regulatory focus. Still, the specific mechanisms proposed here rest on a hypothesis that may not hold up in practice: that existing interoperability capabilities will persist in the market even after the regulatory mandate disappears.

While true for incumbents with established networks, this assumption becomes decreasingly true over time, particularly for new market entrants. By removing the floor for legacy standards without defining a clear bridge to the new ones, and by removing the tools we use to observe the ecosystem, the rule introduces significant architectural gaps.

### Removing the C-CDA Floor

The rule proposes removing the certification criteria for **Consolidated CDA creation performance (§ 170.315(g)(6))** and **Direct Project transport (§ 170.315(h)(1))**. Additionally, it simplifies the **Transitions of care** criterion (§ 170.315(b)(1)) to focus primarily on receiving, rather than sending, data.

The agency justifies this by pointing to widespread adoption:

> Our review of industry adoption of the [Transitions of Care] certification criterion indicates widespread adoption. Review also indicates that its capabilities are widely implemented and used in health IT at this time and thus not likely to go away as supported capabilities by developers of certified health IT solely on the basis of removal of the criterion... (Preamble)

This logic holds for Epic, Oracle, and other major vendors who cannot simply sever referral networks for their existing customers. However, this creates a distinct bifurcation for new market entrants.

A greenfield EHR startup entering the market in 2027 will face zero regulatory requirement to support C-CDA generation or Direct messaging. If they build strictly to the certified floor -- which will consist largely of FHIR RESTful APIs -- they will be structurally unable to push clinical documents to the legacy ecosystem that still relies on these document-based exchanges.

We are left with an interoperability strategy that removes the requirement for the old document standard (C-CDA) before the new one (FHIR Documents) is mature or mandated. We lack widespread industry experience or mature implementation guidance for using FHIR Documents as a drop-in replacement for the clinical density of C-CDA transition of care documents. The rule clears the site, but the blueprints for the new building are not yet approved.

### AI Agents and the Integration Gap

The rule is forward-thinking in its treatment of autonomous agents. The proposed updates to **§ 171.102** explicitly broaden the definitions of "access" and "use" to include automated actors:

> We propose to explicitly codify that access means the ability or means necessary to make EHI available for exchange or use, including by automation technologies such as robotic process automation and autonomous artificial intelligence systems.

This clarification is critical. It validates screen scrapers and autonomous agents as first-class citizens in the interoperability landscape.

However, the "AI-enabled interoperability" envisioned in the preamble faces a structural barrier in the Information Blocking regulations. If an EHR vendor classifies their user interface -- or the specific endpoints an agent attempts to access -- as an "interoperability element," they may leverage the **Licensing Exception (§ 171.303)** to require contracts and fees before allowing access.

A fairer architectural principle might align the licensing model with the interaction model. If an AI agent interacts with the system "from the outside" just as a human user does -- whether through the user interface or client-side APIs -- it should be treated as a user. The economics should follow suit: these agents should arguably be licensed on a "per seat" or equivalent basis, consistent with human access. Treating the standard interface of the EHR as a distinct, licensable "interoperability element" simply because the user is a bot creates an artificial toll booth that contradicts the rule's explicit validation of these technologies.

Furthermore, despite the rhetorical pivot to automation, the rule leaves a glaring hole regarding complete data access. The proposal rightfully removes the legacy **Application Access -- All Data Request (§ 170.315(g)(9))** criterion. This deletion is fine on its own -- (g)(9) was an awkward, document-based criterion that has been superseded by US Core support in FHIR APIs.

The problem is what remains missing. We currently have a requirement for **EHI Export (§ 170.315(b)(10))** to capture the full scope of electronic health information (EHI), including the long tail of data not mapped to FHIR. However, this export capability is still manual and out-of-band. Patients often have to make calls, navigate complex portals, and (in my personal experience) struggle to explain these export requests to HIM/ROI staff.

To truly enable the AI agents ASTP wants to encourage, we need a standardized API wrapper for this process. We need a simple, automatable way for an authorized agent to request and retrieve the full data dump defined in (b)(10). The payload itself does not need to be standardized -- it can remain a vendor-specific mess of CSVs and PDFs -- but the *mechanism of retrieval* must be standardized to allow agents to function without human hand-holding. Without this API mandate, the "full EHI" remains locked behind human workflows that AI cannot navigate.

### Losing Observability

Finally, the rule proposes gutting the **Insights Condition of Certification (§ 170.407)** under the banner of burden reduction. The proposal deletes nearly every metric that would provide context on how APIs are actually being used.

> We propose to remove the following measures...

The only metric that survives is a generic counter for "Use of FHIR in apps."

If the goal of HTI-5 is a "FHIR-forward future," eliminating observability is a strategic error. By removing the specific measures for **Individuals' access** and **Applications supported**, we lose necessary context. We will know *that* APIs are being hit, but we lose the signal required to understand traffic patterns, user demographics, and deployment success. Is the traffic coming from one successful integration or fifty? Are errors spiking for specific user types?

The deletion of the **Bulk Data** metric is particularly confusing. Bulk FHIR (NDJSON) is the primary architectural solution for population health and value-based care analytics -- areas where ASTP/ONC has historically pushed for modernization. Removing the requirement to report on Bulk Data usage suggests the agency is no longer interested in verifying if this critical pipeline is working at scale. You cannot effectively manage an ecosystem transition while voluntarily blinding yourself to the results.

### Keeping TEFCA Optional

The **TEFCA Manner Exception (§ 171.403)** is rightfully removed in this proposal, eliminating a potential shield that incumbents could have used to deny direct API access. That is a win for architectural integrity.

### Advancing FHIR?

For all the preamble’s talk of a "FHIR-enabled future," it is critical to distinguish between the agency's vision and the rule’s actual mechanics. The regulation mandates zero new FHIR capabilities. There is no requirement to support FHIR Writes, no migration to US Core v7, and no expansion of the API surface area developers must maintain. The proposal clears the playing field, but it declines to set the rules for the next game, relying entirely on the assumption that developers will voluntarily standardize around modern features that are not strictly required.