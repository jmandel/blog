---
title: "Understanding ACO Quality Reporting Through Simulation"
date: 2026-08-10T01:45:00
added_at: 2026-10-06
slug: understanding-aco-quality-reporting-through-simulation
original_url: "https://www.linkedin.com/pulse/understanding-aco-quality-reporting-through-josh-mandel-md-d22wc"
linkedin_id: d22wc
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7492397711032422400"
  share_id: "7492397711032422400"
  share_type: "ugcPost"
  posted_at: "2026-08-10T11:45:08"
  visibility: "MEMBER_NETWORK"
  commentary: |
    Last week I teased a little project to help me understand ACO quality reporting. Here it is: an open-source simulator for understanding how quality measure reporting choices flow into financial outcomes. I recorded a 20min guided tour and wrote up what I learned along the way. See video or article for full details + links.
---

Last week I [wrote up my newcomer's understanding](https://www.linkedin.com/feed/update/urn:li:activity:7491569677521805312/) of ACO quality reporting options and teased a new little simulation project. Well, here goes: an open source simulator for understanding how reporting choices flow through to shared savings: <https://joshuamandel.com/app-plus-quality-lab/>

I've attached a ~20 minute walkthrough if you're interested in a guided tour:

The gist is: take an ACO participating in CMS's **"Enhanced Track"** with **24,000 assigned lives** and a **$330M benchmark**. Beating the benchmark by **3%** savse CMS saves **~$10M**. The ACO is eligible to receive shared savings of **75%** (a **$7.4M check**), provided they pass the quality standard.

Whether they an **"eCQM"** or **"CQM"** reporting paths has a significant impact on the actual scores (with a whole lot of nuance we explore in simulation -- see video). The ACO can pass by reporting all five clinical measures on your full (all-payer) population, in which case they're **"deemed"** to meet the standard at full rate, almost regardless of their actual scores. Or the ACO can report on assigned Medicare patients only (which precludes deeming), and then their composite score (**8 measures, 0-10 points each**) has to clear **~74%**. Falling short scales the payout down.

### Some things I learned building this:

* Medicare-population reporting uses flat benchmarks (if the CY 2027 proposal is finalized), so every 10 points of blood pressure control earns a point. eCQMs grade on a historical curve, so 66% control rate might earn 3 points under the all-patient ladder instead of 6 under the Medicare-patient ladder.
* eCQMs are only permitted see what's structured in the EHR and slotted into predefined fields. Good care documented in a note (or an obscure data element) doesn't count.
* Quality matters differently in bad financial years. Overspend by 3% and a strong score caps your shared-loss rate at 40%; a weak score pushes it toward 75%. Deeming doesn't help here, only points do.
* The **"Complex Organization Adjustment"** adds a point per full-population eCQM measure -- a special incentive CMS only applies to full-population eCQM reporting

### Under the hood

Under the hood, eCQMs are based on an XML standard called **QRDA**, though CMS is pushing toward a **"dQM"** future leveraging **FHIR Bulk Export of US Core data + CQL over FHIR "QI Core" profiles**.

But CMS isn't really providing a pathway to incentivize (or explore / debug) early adoption (which is too bad because that is probably the best way to discover problems with this approach and fix them before they hit everyone).

If this all seems a bit complicated -- well yes, for sure! That's why I wanted a systematic, visual way to think about it.

*Your feedback and (especially) corrections are most welcome.*