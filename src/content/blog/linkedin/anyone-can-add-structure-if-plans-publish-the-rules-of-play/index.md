---
title: "Anyone Can Add Structure... If Plans Publish the Rules of Play"
date: 2026-04-02T21:10:00
slug: anyone-can-add-structure-if-plans-publish-the-rules-of-play
original_url: "https://www.linkedin.com/pulse/anyone-can-add-structure-plans-publish-rules-play-josh-mandel-md-x9kwc"
linkedin_id: x9kwc
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7445579422860226560"
  share_id: "7445579422860226560"
  share_type: "ugcPost"
  posted_at: "2026-04-02T21:14:26"
  visibility: "MEMBER_NETWORK"
  commentary: |
    While the healthcare industry rushes to fix prior authorization by standardizing data formats and building APIs, a deeper bottleneck is transparency: anyone (with help from AI Agents) cna make coverage rules computable, but only if health plans actually publish their rules of play.
---

There is a lot of pressure right now to improve prior authorization. Some of that work is overdue and useful: fewer portals, less faxing, cleaner transactions, better ways to move documentation from the chart into the request. CMS’s interoperability and prior authorization rule, finalized in January 2024, pushes the system in that direction by requiring impacted payers to stand up a Prior Authorization API by 2027. ASTP/ONC’s HTI-4 rule, finalized in July 2025, adds health IT certification criteria tied to the Da Vinci prior authorization workflow stack. All of that may make prior authorization more electronic. **None of it, by itself, solves a more basic problem: a coverage rule cannot be encoded if it is not published in enough detail.**

I ran into that problem while building a structured coverage model for *obstructive sleep apnea* from 27 public CMS documents. I picked OSA because it sits at a useful intersection. Some treatment paths rest on national Medicare policy. Others depend almost entirely on regional contractor policy. The billing layer adds its own logic on top. I wanted to know whether the published Medicare rulebook was rich enough to reconstruct the actual decision logic in a form that was usable, comparable, and computable. The resulting prototype is here: <https://joshuamandel.com/cms-ncd-browser-demo>

Put briefly: The Medicare rulebook and narrative-based APIs were detailed enough for frontier LLM agents to read, process, and structure.

**Anyone can add structure, if plans publish the rules of play.** That changed how I think about the bottleneck. A lot of the discussion around computable coverage assumes the hard part is format: the policy exists, but it is trapped in prose, so what we need is a schema. After building the OSA model, I think that gets the emphasis wrong. When the source material is detailed and public, structure is the easier part. The harder problem is disclosure.

### Medicare has two very different transparency regimes

To see why that matters, it helps to separate two Medicare worlds that often get blurred together.

In traditional fee-for-service Medicare, the coverage rules are at least put on the record. At the top are National Coverage Determinations, which are Medicare-wide coverage policies for particular items or services. Below them are Local Coverage Determinations, written by regional Medicare Administrative Contractors when no national rule exists or when local implementation detail is needed. Then there are companion Articles, which often carry coding, billing, and documentation instructions, and Response to Comments records, which preserve the history of how a local policy was revised.

Medicare Advantage is different. MA plans are still bounded by traditional Medicare for basic benefits. The governing regulation requires them to cover Medicare Part A and Part B services and to comply with national coverage determinations, general Traditional Medicare coverage and benefit conditions, and applicable written local contractor decisions. Plans may create internal coverage criteria only when the relevant Medicare criteria are not fully established, and if they do, **those criteria are supposed to be publicly accessible** along with the evidence considered, the sources of that evidence, and the rationale for using the criteria. Where a plan is adding criteria to interpret or supplement general Medicare provisions, it must also explain why those added criteria are highly likely to improve benefits more than harms.

On paper, that is a fairly strong disclosure rule. It tells plans when they may fill gaps, and it tells them that if they do, they have to show their work. But implementation is inconsistent at best.

### Disclosure rule exists but the public record is patchy.

In [May 2025, GAO published a review of nine Medicare Advantage organizations](https://files.gao.gov/reports/GAO-25-107342/index.html) that together covered about 45 percent of MA beneficiaries in 2024. The review focused on selected behavioral health services, and it was not designed to be statistically generalizable, but the findings were still striking. GAO found that posted criteria were often incomplete. **Among the eight publicly accessible internal coverage criteria it reviewed, none contained all required components.** Some included a summary of evidence. Some included sources of evidence. None included the required rationale. None included the explanation of how the clinical benefits of using those criteria likely outweighed the harms.

Worse, **GAO could not locate the public internal coverage criteria used by three of the nine organizations** for all selected services. Two of those organizations cited third-party developer issues; one said its contract with a third-party developer did not allow the criteria to be made public. Even when criteria were available, they were often hard to locate, posted in inconsistent places, or not clearly identified as the criteria applicable to MA members. CMS officials told GAO that plans had been confused about what counted as internal coverage criteria in the first place, especially where vendor-developed material had been used for years.

**CMS clearly saw the discoverability problem.** In the proposed rule for contract year 2026, the agency proposed more concrete website requirements: a prominent page listing all items and services with internal coverage criteria, clearer labeling, vendor attribution, no-login access, and pages that were machine-readable, searchable, and downloadable. **But** **CMS did not finalize those provisions in the April 2025 final rule; it deferred them** for future rulemaking.

That is the backdrop for the OSA exercise. Traditional Medicare is the relatively good case: the rules may be fragmented and verbose, but much of the rulebook is public. MA is the harder case: plans may be using detailed criteria that are still too hard to find, too incomplete, or too thinly published to inspect.

### Why the current standards push does not fix this

This is the part that gets muddled in a lot of health IT conversations.

CMS-0057-F and the related Da Vinci stack improve exchange and workflow. CRD can help an EHR learn whether prior authorization is required and what documentation is needed. DTR can help assemble that documentation in a structured way. PAS can help submit the request and check its status. HTI-4 gives health IT developers certification targets for pieces of that workflow. All of that is useful.

But none of it, by itself, gives you a canonical, inspectable representation of the underlying coverage rule: the threshold, the exclusion, the step-therapy gate, the provider requirement, or the link back to the Medicare baseline.

A questionnaire that asks, “Does the patient have a history of X” is not the same thing as a public coverage object that says how this information will be evaluated together with the rest of the patient history to make a coverage determination.

That is why so much of the current excitement feels slightly off the critical path. Better transport is good. Better workflow is good. But if the underlying rulebook is not public enough to inspect, then the standards stack is moving around an object that still has not been fully disclosed.

###