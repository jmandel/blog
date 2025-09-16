---
title: "Which healthcare regulations should we kill?"
date: 2025-07-15T17:40:00
slug: which-healthcare-regulations-should-we-kill
original_url: "https://www.linkedin.com/pulse/which-healthcare-regulations-should-we-kill-josh-mandel-md-t8a3c"
linkedin_id: t8a3c
banner: ./banner.png
---

Created on 2025-07-15 17:40

Published on 2025-07-15 19:03

Yesterday, the comment period closed on the Agency for Healthcare Research and Quality RFI titled "Ensuring Lawful Regulation and Unleashing Innovation to Make America Healthy Again." The RFI asked stakeholders to pinpoint specific regulations that:

* Increase costs without benefits
* Impede innovation or competition
* Are obsolete or based on outdated technology
* Require excessive reporting or recordkeeping

The response included 646 comments from every corner of American healthcare. I fired up my [open-source comment analysis pipeline](https://github.com/jmandel/regulations.gov-comment-browser) to get an early look at what people said, creating this [theme hierarchy](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/themes).

Then using this open data set through my [Regulations.gov MCP](/posts/cms-rfi-mcp-now-it-s-your-turn-to-analyze-10k-pages), I asked Claude Opus 4 to synthesize the formal, data-heavy responses from major organizations together with the raw, often heartbreaking, stories from individual patients, clinicians, and families. The result is a sampling from **many stories, with substantial areas of alignment**.

A Universal Villain: Prior Authorization
----------------------------------------

No single issue united commenters more than prior authorization. The organizational data paints a grim national picture, while the individual stories reveal the human cost.

The **American Medical Association (AMA)** laid out the systemic failure: **93% of physicians report that prior authorization delays patient care**, and **29% report it has led to a serious adverse event**, including hospitalization, disability, and death. The AMA found that **82% of patients simply abandon treatment** due to these bureaucratic hurdles, and **40% of physician practices employ staff exclusively for PA** [(0490)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0490).

That's not an abstract statistic. That's the daily reality for **Dr. Margaret Chustecki**, an Associate Clinical Professor at Yale. Her practice spends **13 hours every week** on prior authorization alone—time that could be spent with patients [(0020)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0020). Her story is a perfect ground-truth validation of the AMA's national finding that physicians average 13 hours of staff time per week on PA.

Drowning in Clicks: The Administrative Burden
---------------------------------------------

Beyond prior authorization, the sheer weight of compliance is crushing clinicians with work that has no bearing on patient outcomes.

The **Cleveland Clinic** highlighted the absurdity: "The notion that a provider's ability to perform a basic wet mount or urine sediment review must be annually documented, while their ability to prescribe controlled substances, interpret imaging, or perform in-office procedures does not require such documentation, reflects a fundamental misalignment of regulatory scrutiny" [(0517)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0517).

This misalignment has a staggering cost. The Merit-based Incentive Payment System (MIPS) earned universal condemnation. The **AMA** cited data showing practices spend **$12,800 and 202 hours annually on MIPS compliance**, while a JAMA study found the program "approximately as effective as chance" in identifying quality [(0490)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0490). CMS's own 2025 estimate puts the total system-wide cost at **$70,166,672**.

This isn't just about money; it's about time stolen from care and the well-being of clinicians. An anonymous **Director of Nursing** with 30 years of experience reported that NHSN/SAMS COVID reporting requirements, which have never been reversed, **"take 8 hours per week from bedside care for an RN."** She lives in daily fear: "Everyday we fear for our licenses while state boards of nursing hold a power that is not warranted" [(0013)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0013). This burden extends to social services, where a **Head Start worker** described an annual renewal process that takes "months to complete" and is "consistently returned multiple times" for publicly available information [(0231)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0231).

When Rules Actively Deny Care
-----------------------------

In the most extreme cases, regulations designed to protect patients create insurmountable barriers to necessary treatment.

### The ADHD Medication Crisis

Several individual comments described the struggle to access Schedule II ADHD medications. An **entrepreneur** described failing three businesses before getting treated, after which they successfully reopened and maintained their business [(0473)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0473). But access remains a "full-time job," as one nursing student put it [(0366)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0366). The regulatory disconnect is stark: ADHD treatments remain classified with "fentanyl and methadone" despite a long safety record. An anonymous drug policy researcher explained the systemic cause: **DEA quota systems create artificial shortages** that drive patients toward counterfeit street drugs [(0024)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0024).

### Four Decades of Fighting for Treatment

**Leo and Claudia Soucy**, both 81, have been fighting regulatory battles since 1986 for their 56-year-old son Brendon, who has severe autism. They seek access to electrical stimulation devices (ESDs) to treat his self-injurious behavior after other approaches failed catastrophically: "Seclusion, restraint and isolation... was a heartbreaking failure," while heavy medications left him "toothless and has tardive dyskinesia." When Massachusetts banned ESDs, "Brendon regressed terribly." Now, the FDA proposes a national ban, forcing them to start over. "It is very unfair that my wife & I at our age 81 must fight & fight for this treatment," they wrote [(0107)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0107).

The Soucys' personal, decades-long battle mirrors the systemic fight from organizations like **Eli Lilly**, which challenged CMS’s Coverage with Evidence Development (CED) framework for creating access barriers to FDA-approved drugs. Lilly's core argument: "Access should never be contingent on enrollment in a research protocol" [(0526)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0526).

Innovation Blocked by Outdated Frameworks
-----------------------------------------

The regulatory system is consistently years, if not decades, behind the technology it governs.

* **Epic** detailed how 2016 FDA guidance threatens to regulate "over 150,000 unique CDS tools" because it misinterprets how clinical recommendations work, and how OCR rules still require "human translators" despite superior AI performance [(0630)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0630).
* **Zocdoc** pointed out that the 1972 Anti-Kickback Statute "predates digital technology" and creates ambiguity that blocks platforms from fixing scheduling inefficiencies that waste 20-30% of provider time [(0486)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0486).
* **Anthony Leo**, an innovator, challenged CLIA rules requiring credentialed Lab Directors who earn $160,000+ for minimal oversight, creating "de facto licensing cartels" that throttle new AI diagnostic tools [(0010)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0010).
* **Kassie Genna**, a patient with dysautonomia, proposed a zero-cost innovation: adding one question—"Do you taste saline when your IV is flushed?"—to intake forms. This patient-observed phenomenon could help identify patients needing early autonomic testing, but there's no regulatory pathway for such simple, patient-driven improvements [(0081)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0081).

Systemic Dysfunction & Unintended Consequences
----------------------------------------------

The comments reveal a system where rules create perverse incentives and impossible choices.

* **Rural Realities:** The **National Rural Health Association** reported that **"190 rural hospitals closed since 2010,"** with **"46% of rural hospitals operating with negative margins"** [(0631)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0631). **Christa Jones**, a rural Kansas provider, described how conflict-of-interest rules designed for urban areas create "impossible choices," forcing providers to "divest parts of their organizations" they cannot replace [(0090)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0090).
* **Cost-Sharing Burden:** The **Cleveland Clinic** argued for "shifting cost-sharing collection responsibilities to insurers," since they set the amounts. The clinic reported that in 2024, **"50% of co-pays for visits and services... were not paid, accounting for $70M in lost revenue"** [(0517)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0517).
* **Inside the VA:** Whistleblower **Gregory Romeu**, with insider experience, exposed systematic fraud draining **"BILLIONS of tax dollars"** from VA homeless veteran programs. He stated that VA oversight uses only "Yes Men" to suppress negative findings and argued for transferring housing control to DHHS [(0028)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0028).

A Mandate for Change
--------------------

These 646 comments are not a call for a regulatory bonfire. The child care owner who opposed deregulation saw safety rules as essential business infrastructure [(0603)](https://joshuamandel.com/regulations.gov-comment-browser/AHRQ-2025-0001-0001/#/comments/AHRQ-2025-0001-0603). The parents fighting for ESDs accept court-ordered treatment reviews.

What they oppose are regulations that are ineffective, outdated, or misaligned with the goal of patient care. The most striking finding is the consensus. The work for policymakers begins now.

---

Methodology and Resources
-------------------------

You can explore this data and the tools used to analyze it yourself.

* **Review the analyzed comments:** To browse the comments by theme and read the full text of every submission cited here, use the [user-friendly comment browser](https://joshuamandel.com/regulations.gov-comment-browser/).
* **See the raw data:** For the official, unfiltered source material, visit the [AHRQ docket on regulations.gov](https://www.regulations.gov/document/AHRQ-2025-0001-0001).
* **Check out the code:** The [open-source code](https://github.com/jmandel/regulations.gov-comment-browser) for the entire analysis pipeline is available on GitHub.
* **Learn about the technique:** For a detailed write-up on the methodology, including the use of the Model Context Protocol (MCP) server and Claude Code, see my [post on LinkedIn](/posts/cms-rfi-mcp-now-it-s-your-turn-to-analyze-10k-pages).