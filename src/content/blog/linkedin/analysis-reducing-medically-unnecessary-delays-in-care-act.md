---
title: "Analysis: \"Reducing Medically Unnecessary Delays in Care Act\""
date: 2025-03-29T16:51:00
slug: analysis-reducing-medically-unnecessary-delays-in-care-act
original_url: "https://www.linkedin.com/pulse/analysis-reducing-medically-unnecessary-delays-care-act-mandel-md-nryhc"
linkedin_id: nryhc
---
![](https://media.licdn.com/mediaD5612AQGvIgo2KUH2HA)


Created on 2025-03-29 16:51

Published on 2025-03-29 18:17

Prior authorization imposes a barrier to timely care. While tech solutions (including conversational AI agents using FHIR, [as I discussed last week](/posts/prior-auth-is-friction-can-t-we-just-talk)) offer potential paths to streamline this, policy sets the operational parameters. The newly (re-)introduced [**"Reducing Medically Unnecessary Delays in Care Act of 2025" bill**](https://markgreen.house.gov/_cache/files/0/7/07ab76c1-9639-4748-8832-4c92672c008b/20388E143170D9C5173A02CFB842FA1A.reducing-medically-unnecessary-delays-in-care-act-of-2025-1.pdf) proposes specific changes for Medicare prior authorization rules, with significant impacts for Medicare Advantage plans.

### The Physician Review Mandate (Sec 3(8)) - A Critical Ambiguity

**Requirement:** This section of the proposal mandates that "all preauthorizations and adverse determinations are made by a physician" (appropriately licensed and specialty-matched).

**Interpretation Challenge:** This wording is problematic, on my reading. The proposal defines "preauthorization" (Sec 2(9)) as the *process* of review, "adverse determination" (Sec 2(1)) as the *denial* outcome, and "authorization" (Sec 2(2)) as the *approval* outcome. My reading suggests that both *outcomes* – approvals ("authorizations") and denials ("adverse determinations") resulting from the preauthorization process – require physician sign-off.

**Direct Conflict with Automation & AI:** *If* this interpretation holds (that approvals require physician sign-off), it poses a direct threat to efficiency. Many straightforward PA requests meeting objective criteria could be efficiently handled via automated system rules or expedited review by non-physician staff following clear protocols. Crucially, this specific requirement within the proposed legislation would **undermine the** [**automated conversation-based approval workflow I outlined yesterday**](/posts/prior-auth-is-friction-can-t-we-just-talk)**.** The vision there is an efficient dialogue: EHR agent provides data -> payer agent/tool verifies against rules -> approval is granted. If, even after the AI agent successfully provides all necessary evidence demonstrating criteria are met, the process must halt and wait for a manual physician review just to issue the *approval*, the primary speed and efficiency benefits for "getting to yes" are lost. It renders sophisticated automation pointless for routine approvals, **forcing a human bottleneck** where objective criteria have already been satisfied.

**Unintended Consequences:** This ambiguity creates significant risk. Mandating physician review for every routine approval would drastically increase costs, introduce potentially massive delays for necessary care (ironically contradicting the proposal's title), and could disincentivize the use of PA altogether, possibly leading to broader utilization controls elsewhere. Clarity is essential. The focus should be on physician review for denials, not on impeding efficient approvals that meet established rules.

### Public Criteria Transparency (Sec 3(5))

**Requirement and Analysis:** This section mandates plans post PA requirements and clinical criteria online ("readily accessible," "easily understandable"). This is essential progress. Public criteria enable providers to understand requirements upfront, patients to make informed plan choices, and crucially, provides the foundational knowledge for technological tools to function effectively by interpreting and applying rules. This provision of the **Reducing Medically Unnecessary Delays in Care Act** directly addresses a long-standing barrier to efficiency and informed decision-making. Success depends on the practical accessibility and format (ideally, machine-readable) of the data.

### Public Statistics (Sec 3(7))

**Requirement and Analysis:** This mandates public posting of PA approval/denial stats. This builds upon existing CMS regulations requiring MA plans to *report* similar data to the agency. The **Reducing Medically Unnecessary Delays in Care Act** would **codify** such requirements, potentially broaden their scope across Medicare programs, and crucially mandate **public web access**. While increased transparency is positive, the specified data lacks critical process metrics (e.g., decision turnaround times, appeal rates/stages). Without this context, the statistics offer limited insight into operational efficiency or the actual burden experienced by patients and providers – a potential unintended consequence is focusing on outcome numbers without addressing process delays.

###