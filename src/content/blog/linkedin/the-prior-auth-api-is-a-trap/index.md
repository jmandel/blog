---
title: "The Prior Auth API is a Trap"
date: 2025-07-17T03:58:00
slug: the-prior-auth-api-is-a-trap
original_url: "https://www.linkedin.com/pulse/prior-auth-api-trap-josh-mandel-md-hkixc"
linkedin_id: hkixc
banner: ./banner.png
---

Created on 2025-07-17 03:58

Published on 2025-07-17 16:46

The Da Vinci DTR Implementation Guide aims to reduce prior authorization friction by standardizing the *format* for asking and answering clinical questions. It is a well-engineered specification for a "computable clipboard," a significant improvement over the fax machines and proprietary portals in use today.

The core problem with prior authorization, however, is not the format of the questions. The problem is that the detailed clinical rules driving the need for those questions are kept **secret**. We are building efficient digital highways to shuttle data into a black box adjudication engine.

The most pragmatic path forward is not to demand that payers re-engineer their complex internal rules into a new computable format overnight. The highest-impact step is a **simple "read-only" mandate**: require payers to publish their detailed, unabridged clinical necessity criteria in a clear, human-readable format. This is now a practical solution because modern AI agents can parse this expert text and translate it into real-time, upstream clinical guidance.

Two Layers of Payer Rules
-------------------------

To understand the problem, we need to look at the two distinct layers of rules that govern payer decisions. The friction and frustration for providers live in the gap between them.

### Layer 1: The Public Medical Necessity Policy

This is the document you can find on a payer's website—an Aetna Clinical Policy Bulletin (CPB) like [CPB 0236 for spinal imaging](https://www.aetna.com/cpb/medical/data/200_299/0236.html) is a good example. These documents provide high-level guidance, listing covered conditions and general requirements.

They are useful, but have two critical limitations:

1. **They are incomplete.** They provide general guidance but often lack the specific, granular criteria that lead to a denial.
2. **Their applicability is ambiguous.** It is often difficult or impossible for a provider to know which of these public policies applies to a specific patient's employer-sponsored plan. A single payer may have myriad variations of a policy for different employer groups.

### Layer 2: The Specific Adjudication Criteria

This is the real rulebook. It contains the detailed, evidence-based criteria—often licensed from vendors like MCG Health or InterQual—that the payer's adjudication system actually uses. This layer specifies the exact lab value thresholds, required timeframes for failed therapies, and other granular details that are absent from the public Layer 1 documents.

Today, this Layer 2 rulebook is a proprietary black box. It is the primary source of prior authorization denials and the root cause of provider abrasion. It is typically only revealed, in part, after a denial has already occurred.

### Example Gap in Practice: "Conservative Therapy"

A specific example from the Aetna policy illustrates the gap between Layer 1 and Layer 2. The public policy requires a trial of "conservative therapy" and, to its credit, provides a footnote:

> Footnote1\* Conservative therapy = moderate activity, analgesics, non-steroidal anti-inflammatory drugs, muscle relaxants.

This seems clear, but it is not. It is a Layer 1 summary of a more detailed Layer 2 rule. A denial could still easily occur based on the specifics hidden in that next layer.

Here is how the Layer 2 criteria would add the necessary, but currently secret, detail:

* **Specificity of Drugs:** The Layer 2 rule might require "a documented 4-week trial of a *prescription-strength* NSAID (e.g., Naproxen 500mg BID)." A patient who tried over-the-counter ibuprofen for 10 days meets the Layer 1 definition but would fail the Layer 2 adjudication rule.
* **Definition of Activity:** "Moderate activity" is clinically vague. The Layer 2 rule might require "a documented, provider-directed activity modification plan."
* **Logical Combination:** The commas in the Layer 1 definition are ambiguous. The Layer 2 rule would contain the precise Boolean logic, such as requiring "a trial of an NSAID *AND* a muscle relaxant."

The public policy provides a helpful guide, but it is not the full, auditable rule. The gap between the public footnote and the internal adjudication criteria is where denials happen.

Proposal: Publish the Layer 2 Rules
-----------------------------------

We should expect payers to publish their complete, unabridged Layer 2 clinical criteria. Crucially, they must also provide a mechanism to link these specific policies to the health plans they govern, so a provider can determine the rules for a specific patient.

The required format is not a complex computable artifact. It is simply well-structured, version-controlled, human-readable text, published at a stable, public URL. This is a publishing task, not a massive software re-engineering project.

### The AI Bridge: From Readable Text to Actionable Guidance

Once these detailed rules are public, frontier AI tools can serve as a universal translation layer, turning text into actionable guidance inside the clinical workflow. This transparency shapes not just downstream documentation, but upstream clinical decisions.

Here's how it would work in practice:

1. Dr. Reed sees her patient, David Lee, for back pain. She is considering starting conservative therapy.
2. An AI agent integrated into the EHR, aware of the patient's diagnosis and payer, proactively checks the public Layer 2 policy for a future, potential lumbar MRI.
3. The agent displays a concise summary directly in the workflow as Dr. Reed is drafting her treatment plan.

> **Plan-Specific Guidance for Future MRI:**

Dr. Reed now knows that prescribing over-the-counter ibuprofen will not satisfy the payer's eventual requirements. She instead prescribes a 6-week course of Naproxen. She is making an informed clinical decision at the point of care that aligns her patient's therapy with the specific rules that will govern future care, preventing a certain denial weeks or months later.

---

What Does Transparency Unlock?
------------------------------

### For Clinical Care and Documentation

Care would converge around public, evidence-based standards. Providers would be able to make **informed clinical decisions and document correctly from the start**, reducing the need for peer-to-peer calls and appeals.

### For Employers and Plan Sponsors

Plan design can go beyond premiums and network definition. Layer 2 rules can inform a more meaningful head-to-head comparison of benefits.

### For Policymakers

This approach provides a clear, high-leverage path to reform.

* **Mandate public posting** of all Layer 2 clinical criteria at stable, version-controlled URLs.
* **Require a mechanism** for providers to link a specific member and plan to the exact policy documents that apply to them.
* **Ensure the mandate has no loopholes** for "trade secret" exemptions on clinical necessity rules.

A handful of states have already started **forcing sunlight onto "Layer 2" rules**. For example:

* **Colorado**: 2024 [update](https://colorado.public.law/statutes/crs_10-16-112.5) to §10‑16‑112.5 orders carriers to post "current prior‑authorization requirements, including written clinical criteria" *and* yearly approval/denial data on a searchable website
* **Illinois**: [**Prior Authorization Reform Act**](https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=4201&ChapterID=22) makes plans publish "any PA requirements, *including the written clinical review criteria*," plus annual PA statistics.

These moves prove policymakers can demand real transparency, laying a clear runway for a nationwide mandate to publish the full Layer 2 rulebook.

Conclusion
----------

The current focus on standardizing the format of prior authorization questions is insufficient. The real bottleneck is the secrecy of the rules. A mandate for human-readable transparency of Layer 2 criteria is the most pragmatic and highest-impact next step. The technology to make this published text useful in real-time now exists. The most powerful API is a URL!