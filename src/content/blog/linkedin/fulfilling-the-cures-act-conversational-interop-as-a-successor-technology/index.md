---
title: 'Fulfilling the Cures Act: Conversational Interop as a "Successor Technology"'
date: 2025-10-17T21:03:00.000Z
slug: fulfilling-the-cures-act-conversational-interop-as-a-successor-technology
original_url: "https://www.linkedin.com/pulse/fulfilling-cures-act-conversational-interoperability-josh-mandel-md-jevoe"
linkedin_id: jevoe
banner: "https://media.licdn.com/mediaD4E12AQG8KZDVx8QSUA"
---

The 21st Century Cures Act set a clear north star: a patient’s electronic health information must be reachable “without special effort” through “APIs or their successor technologies.” Congress did not freeze the future on any single standard; it obligated the industry to keep removing friction from health data exchange.

FHIR has removed a great deal of that friction. Today, an app can pull a patient's medications, a payer can run bulk analytics, and EHRs are certified on their API capabilities. Yet for a stubborn class of workflows, progress remains stalled. Prior authorizations still spawn fax trees, referrals travel by portal-and-PDF, and disease registries rely on one-off spreadsheets. For this long tail, the standards are often incomplete, and it is impractical to assume we can develop a perfect, consensus-based specification for every niche. The gap is rarely a missing API endpoint; it is the endless, costly re-negotiation of what to send, how to send it, and why.

A successor technology for this challenge is already emerging:  **Conversational Interoperability (COIN)**.

Picture authenticated software agents that hold short, flexible conversations, with data access approved (and auditable) by patients:

“Show me the last three HbA1c values for this referral, and a summary of any clinical note content in the past 6 months relevant to diabetic retinopathy.”

“Here they are, along with a receipt of this disclosure for the patient.”

There is no consensus process to pre-negotiate a data profile in a 100-page implementation guide. Each exchange is bounded by a specific purpose and logged with an immutable receipt. The patient (or their designated agent) can see every dialog turn and file attached.

To make this conversational paradigm trustworthy and scalable, we need to build a foundational trust fabric: a **Minimum Interoperability Network for Trust (MINT)**. The core purpose of such a network would be to establish patient-accountable access pathways, ensuring every exchange is safe, transparent, and directly auditable by the individual whose data is in motion. This network should be a thin layer built on open specifications. It could wrap FHIR where such APIs exist; where they don’t, AI-backed connectors could translate diverse underlying formats into the conversational protocol. 

*MINT + COIN create a powerful opportunity for systems with electronic data but without modern APIs to leapfrog the current generation of standards and participate directly in a flexible, dynamic ecosystem.*

This approach aligns perfectly with the Cures Act’s statutory vision, even if it is ahead of the specific regulations expressed in ONC's Cures Act Final Rule. It directly maximizes electronic access, minimizes special effort, and embeds transparency by design. The industry does not need to wait for another rulemaking cycle to build the future the statute already anticipated. This model allows established systems to solve the stubborn "long tail" workflows that bleed time and money, while simultaneously providing a path for less-developed systems to join a modern, secure network without a massive rebuild.

*The Cures Act anticipated successor technologies; let’s build one!*