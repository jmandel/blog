---
title: "What 170 Organizations Told CMS About Publishing the Rules of Play"
date: 2026-04-03T20:25:00
added_at: 2026-10-06
slug: what-170-organizations-told-cms-about-publishing-the-rules-of-play
original_url: "https://www.linkedin.com/pulse/what-170-organizations-told-cms-publishing-rules-play-josh-mandel-md-m9qoc"
linkedin_id: m9qoc
banner: ./banner.jpg
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7445930620779868160"
  share_id: "7445930620779868160"
  share_type: "ugcPost"
  posted_at: "2026-04-03T20:29:58"
  visibility: "MEMBER_NETWORK"
  commentary: |
    Yesterday's post got me thinking: CMS came pretty close to regulating this "how to find the rules" problem away. Hundreds of commenters responded to the proposal. And then (well, nothing). See article for the story.
---

In [yesterday's post](https://www.linkedin.com/feed/update/urn:li:activity:7445579423405477888/), I argued that the bottleneck for computable coverage isn't format: it's disclosure. When the underlying coverage rules are detailed and public, structure is the easier part. When they aren't published at all, no amount of standards work can fill the gap.

That post was prompted in part by a CMS proposal in the [CY 2026 Medicare Advantage rule (CMS-4208-P)](https://www.federalregister.gov/documents/2024/12/10/2024-27939/medicare-and-medicaid-programs-contract-year-2026-policy-and-technical-changes-to-the-medicare) that would have required MA plans to publish their internal coverage criteria in machine-readable, searchable, downloadable format, with a txt file in the root directory of the website domain linking to the machine-readable file, no login required, no paywall, prominently displayed in the website footer. It was the most concrete attempt CMS has ever made to close the disclosure gap I described.

CMS received roughly 31,000 comments on the proposed rule. I reviewed the extracted chunks from 173 comment letters that touched on coverage criteria discoverability. What follows is a summary of what those commenters said, what CMS decided in the April 2025 final rule, and what it means for the interoperability stack.

---

### The comments overwhelmingly confirmed the disclosure problem

CMS itself acknowledged in the proposed rule preamble that "the average person faces difficulty accessing an MA organization's website for the purpose of determining whether or not the MA plan applies internal coverage criteria to the particular Medicare item or service." Commenters confirmed this with specifics.

The **Medicare Rights Center** described the practical state of affairs:

> The criteria pages are not prominent and may have ambiguous or non-intuitive titles like "Medicare Guidelines" and be filed under member forms or other resources... the documents in many cases cannot be printed, leaving readers unable to create a resource for themselves... the information is presented without clear guideposts to distinguish between internal and Medicare-originating criteria.

The **American Physical Therapy Association** documented a specific case in detail — navigating UnitedHealthcare's prior authorization program for rehabilitative services required finding relevant information across three separate documents housed in different locations on the UHC website, creating an account with Change Healthcare on a separate platform, and spending a minimum of 15-20 minutes just to locate the relevant documents. APTA concluded:

> While this information is, in some ways, technically "publicly available" as is currently required, understanding what to look for, where to find it, and how to access and interpret it likely does not meet the intent or spirit of what CMS envisions for transparency.

Other commenters — including the **California Hospital Association**, **Greater New York Hospital Association**, and **American Medical Rehabilitation Providers Association** — confirmed the same pattern from hospital and post-acute perspectives: MAOs consistently fail to meet existing transparency requirements, and proprietary criteria that are more restrictive than traditional Medicare remain pervasive and difficult to locate.

---

### The machine-readable requirement drew strong support... and opposition along a clean fault line

The proposed requirement for machine-readable, searchable, downloadable publication of internal coverage criteria was one of the most concrete interoperability-relevant provisions in the rule. Support and opposition split almost perfectly along a stakeholder line.

**Provider organizations, patient advocates, medical societies, device manufacturers, and laboratories** broadly supported the requirement. The **Federation of American Hospitals** endorsed "a downloadable and searchable machine-readable file that is available without charge and is directly linked in a .txt file in the root directory of the MA organization's website domain." **America's Essential Hospitals** said the requirement would "enhance usability for providers, patients, and other stakeholders." The **Medical Device Manufacturers Association** "strongly agrees with CMS' determination that by making this information more easily available to automated searches and data pulls, it will help third parties and researchers conduct studies to examine the clinical value of the internal coverage criteria being used by MA plans."

**MA plans, third-party criteria developers, and their trade associations** opposed it. **UnitedHealth Group** argued that "the proposed requirement that such content must be downloadable and available in a machine-readable format effectively puts third-party content such as InterQual in the public domain and may constitute a taking of private property." **MCG Health**, which develops clinical criteria used by many MA plans, objected directly: "MCG would object to any requirement that third-party licensed content be made freely available in downloadable machine-readable format, as such a requirement would vitiate third-party intellectual property rights and threaten the viability of third-party creation of criteria." **Blue Cross Blue Shield Association** recommended CMS "not require MA plans to publish the health equity analysis in a machine-readable file format." **Humana** noted the proposed requirements go "above and beyond what is published for Original Medicare, as NCDs and LCDs are not currently published in a list in a machine-readable text file."

**CVS Health** raised a different objection: that "posting potentially highly technical documentation about coverage criteria runs the risk that consumer's only interaction with the required posted material will be indirect" — through AI tools that "indiscriminately crawl and consume publicly available material." This inadvertently concedes the core point of my [earlier post](https://www.linkedin.com/feed/update/urn:li:activity:7445579423405477888/): once material is published, structure and analysis follow naturally. The concern that AI tools will read the criteria and attempt to interpret them is, from a transparency perspective, exactly the desired outcome.

---

### Several commenters independently proposed the same infrastructure

Multiple organizations (without apparently coordinating) proposed the same structural solution: a centralized, searchable MA coverage database analogous to CMS's existing Medicare Coverage Database for NCDs and LCDs.

The **American College of Physician Advisors** and an individual clinician commenter both proposed that "CMS consider creating a Medicare Advantage Coverage Database analogous to the Medicare Coverage Database which would allow searching internal coverage criteria across plans and in specific jurisdictions." **AMRPA** urged CMS to "make this information available to the general public through a centralized CMS repository." **LeadingAge** recommended that "CMS adopt a policy to require plans to submit their list of ICCs directly to CMS... and make this information available to the public in a centralized location." The **AMA** recommended "that these data also be published on a centralized, public website — such as a CMS webpage — to ensure easy access to the information, as well as facilitate comparison between plans."

The convergence is notable. These organizations represent different constituencies — physician advisors, rehabilitation providers, aging services, the medical profession broadly — but arrived at the same conclusion: plan-by-plan disclosure, even if improved, is insufficient without aggregation.

---

### An individual clinician showed what becomes possible when rules are detailed

One commenter (CMS-2024-0345-16075) — an individual, not an organization — did something that illustrates the thesis of my [earlier post](https://www.linkedin.com/feed/update/urn:li:activity:7445579423405477888/). They walked through specific clinical scenarios for upper and lower GI bleeding, criterion by criterion, comparing what widely-used treatment guidelines actually say against what InterQual applies in practice. For upper GI bleeding:

> InterQual, in its publicly available December 2024 release, currently lists a hemoglobin >= 7.0 as a requirement to qualify for "observation," and lists a hemoglobin of <7.0 as one of a few criteria that can support an "acute" (e.g. inpatient) level of care. InterQual does not directly cite evidence supporting the usage of the transfusion threshold in this manner. The ACG guideline does not consider using the hemoglobin level to distinguish inpatient vs observation, nor assert that the hemoglobin level is predictive of the expected duration of necessary hospital care.

This is what becomes possible when coverage criteria are accessible: independent clinical review. The commenter reconstructed the decision logic, compared it against the cited evidence, and identified specifically where the coverage criterion departed from the guideline it claimed to rest on. They could do this because InterQual's criteria for this particular service happened to be accessible. For most MA internal coverage criteria, this kind of analysis remains impossible — not because the analysis is hard, but because the source material is not available.

---

### What CMS decided: defer the entire section

The [CY 2026 final rule (CMS-4208-F)](https://www.federalregister.gov/documents/2025/04/15/2025-06008/medicare-and-medicaid-programs-contract-year-2026-policy-and-technical-changes-to-the-medicare), published April 15, 2025, did not finalize any of the internal coverage criteria provisions. Not the definition. Not the prohibitions on criteria lacking clinical benefit. Not the machine-readable requirement. Not the website footer rule. Not the txt file in the root directory.

The final rule's treatment is brief. Table 4 lists "Enhancing Rules on Internal Coverage Criteria (§ 422.101)" among the provisions whose finalization is "deferred for subsequent rulemaking." The preamble states:

> In this final rule, we are not summarizing or responding to comments received with respect to the provisions of the proposed rule that we are not addressing or finalizing at this time. Rather, as appropriate, and if applicable, we will address those comments at a later time in a subsequent rulemaking document.

There is no discussion of the comments, no explanation of the deferral, and no timeline for a subsequent rule. The 173 comment letters, the detailed clinical examples, the proposed definitions, the machine-readability requirements — all of it is set aside without response.