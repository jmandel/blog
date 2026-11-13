---
title: "Certified EHRs Should Let Customers Bring Their Own Agents"
date: 2026-11-13T12:00:00
added_at: 2026-11-13
slug: ai-agents-as-ehr-users-without-vendor-permission
banner: ./banner.png
---

<style>
.gnt .scene { border-left: 3px solid #1c2321; padding: 0.1rem 0 0.1rem 1rem; margin: 0.9rem 0; }
.gnt .scene summary { cursor: pointer; font-weight: 700; font-size: 1rem; color: #363636; }
.gnt .scene summary:hover { color: #0066cc; }
.gnt .scene[open] summary { margin-bottom: 0.15rem; }
.gnt .scene .tag { margin-top: 0.3rem; }
.gnt .scene .tag { font-size: 0.82rem; color: #5a6662; margin: 0 0 0.6rem; }
.gnt .scene .tag a { font-family: ui-monospace, "SFMono-Regular", Menlo, monospace; font-size: 0.95em; }
.gnt .scene p.l { margin: 0.45rem 0; }
.gnt .scene p.l b { font-weight: 700; }
.gnt .scene p.n { margin: 0.6rem 0 0; font-size: 0.9rem; color: #5a6662; }
.gnt .reg { background: #f7f6f2; border-radius: 6px; padding: 0.9rem 1.1rem; margin: 1.2rem 0; font-size: 0.93rem; }
.gnt .reg p { margin: 0.55rem 0; }
.gnt .reg p.h { font-weight: 700; margin-top: 1rem; }
.gnt .reg p.h:first-child { margin-top: 0; }
.gnt .reg p.i { padding-left: 1.2rem; }
.gnt img[src*="gauntlet"] { display: block; height: auto; border-radius: 0; }
.gnt img[src*="gauntlet-tall"] { margin: 1.5rem auto 0; max-width: 100%; }
.gnt img[src*="gauntlet-wide"] { display: none; }
@media (min-width: 900px) {
  .gnt img[src*="gauntlet-tall"] { display: none; }
  .gnt img[src*="gauntlet-wide"] { display: block; width: 100%; max-width: 100%; margin: 1.5rem 0 0; }
}
.gnt p.cap { font-size: 0.88rem; color: #5a6662; margin-top: 0.5rem; }
</style>

<div class="gnt">

> **TL;DR:** A clinic that wants its clinicians to use an AI agent inside the EHR must today get the EHR vendor to agree, and the information blocking exceptions give the vendor a long series of permitted ways to price, redirect, and decline. ONC should stop treating this as a request to the vendor. A condition of certification should say that a customer may have software of its choosing operate the EHR's ordinary screens, under a clinician's login or an account the customer sets up for it, with no separate license, fee, or vendor approval. Draft regulatory text is below.

Agents that operate software the way a person does (reading the screen, clicking, typing) now work well enough to prepare a chart before a visit, draft replies to patient messages, and queue refills for a clinician to sign. For a practice this is a tool, like dictation software, or a new assistant who needs a login. For the regulations it is something else: a third party asking an EHR vendor for access, which starts a process built for a different problem.

The story below is fiction. The clinic, the startup, and the vendor are invented, and the calendar is stylized. Every step the vendor takes is one the current rules allow.

## The request

Three parties are involved.

- **The clinic.** Cedar Street Family Medicine has six clinicians. Its owner, Dr. Okafor, wants help with the patient message inbox.
- **The developer.** Maya founded Pencilwork, a four-person startup. Its agent works the EHR's screens the way a staff member would, under whatever account the clinic gives it.
- **The vendor.** Cedar Street's EHR is cloud-hosted by a company I'll call Quillon.

For each patient portal message, the agent reads the thread and the relevant chart history, drafts a reply for the clinician to review, and pends any refill for signature. It never sends or signs anything.

Message threads and the refill request queue are one click away on the EHR's screens. Neither is in USCDI, the standard data set that certified FHIR APIs must serve, in any version through v7.

Cedar Street has signed a pilot agreement and a HIPAA business associate agreement with Pencilwork. It wants the agent, will pay for it, and takes responsibility for it. Only the vendor is left.

![Flow diagram of the fictional request. Twelve steps over 96 business days: the clinic asks, the vendor points to its license, the developer requests access, three rounds of terms fail, the vendor offers the FHIR API, app registration takes the 15 business days allowed, the developer asks for the missing messages and for write access and is denied as a third party seeking modification, the clinic repeats the request, terms fail again, the vendor declares the request infeasible, and the clinic and developer file a complaint with no deadline for a decision.](./gauntlet-wide.svg)

![Flow diagram of the fictional request. Twelve steps over 96 business days: the clinic asks, the vendor points to its license, the developer requests access, three rounds of terms fail, the vendor offers the FHIR API, app registration takes the 15 business days allowed, the developer asks for the missing messages and for write access and is denied as a third party seeking modification, the clinic repeats the request, terms fail again, the vendor declares the request infeasible, and the clinic and developer file a complaint with no deadline for a decision.](./gauntlet-tall.svg)

<p class="cap">Day counts are business days. Dark pills are periods the regulations set; dashed pills are periods with no limit, where the story assumes a plausible wait.</p>

## What each step sounds like

Each step of the diagram as a short exchange. Open any one to read it.

<details class="scene">
<summary>Days 0 to 8: the license</summary>
<p class="tag">Customer license agreement · a contract term, with no clock for answering</p>
<p class="l"><b>Dr. Okafor:</b> We'd like our clinicians to use an AI agent in the EHR. It would work under their logins, or under its own account with a limited role if you prefer. Can you confirm that's fine?</p>
<p class="l"><b>Quillon account manager:</b> Section 4.2 of your agreement prohibits access "by automated means, including scripts, bots, or robotic process automation" and any access by third parties without our written consent. Third parties go through Partner Programs. I've sent them your developer's name.</p>
</details>

<details class="scene">
<summary>Days 9 to 34: the manner requested</summary>
<p class="tag"><a href="https://www.ecfr.gov/current/title-45/section-171.301">§171.301(a)</a> Manner exception · no time limit</p>
<p class="l"><b>Maya:</b> We're requesting that Cedar Street's clinicians be allowed to operate Quillon's screens through our agent, under accounts the clinic authorizes.</p>
<p class="l"><b>Dana, Partner Programs:</b> Happy to help. The program is $25,000 a year, plus four cents per automated interaction, plus 12% of revenue from joint customers. You'll grant us a license to feedback and improvements. Security review has a ten-week queue.</p>
<p class="l"><b>Maya:</b> A fee based on my revenue is barred by the Fees exception, and an IP grant-back is barred by the Licensing exception.</p>
<p class="l"><b>Dana:</b> Those conditions apply when we fulfill a request in an <em>alternative</em> manner. For the manner you requested, §171.301(a)(2) says our fees and licenses don't have to meet them. These are our market terms.</p>
<p class="l"><b>Dana, a week later:</b> Also, please stop the demo sessions. Our written security policy flags scripted input, and the test account has been locked.</p>
<p class="n">Three rounds of redlines follow. Dana is right about the rule text: the cost-based, nondiscriminatory conditions sit in the Fees and Licensing exceptions, and the Manner exception applies them only to an alternative manner. ONC has said it expects "market" terms for the manner requested and that unconscionable terms could still be information blocking, but its proposal to write that into the rule was deferred. As codified, the parties need only fail to "reach agreeable terms," with no deadline for finding that out. The lockout is defended under the Security exception, <a href="https://www.ecfr.gov/current/title-45/section-171.203">§171.203</a>.</p>
</details>

<details class="scene">
<summary>Days 34 to 39: the alternative manner</summary>
<p class="tag"><a href="https://www.ecfr.gov/current/title-45/section-171.301">§171.301(b)</a> · "without unnecessary delay"</p>
<p class="l"><b>Dana:</b> Since we couldn't agree, we'll fulfill your request in an alternative manner. First in the order of priority is certified technology. That's our FHIR API.</p>
<p class="l"><b>Maya:</b> The agent works the patient message inbox and the refill queue. Neither is in USCDI, so neither is in your FHIR API.</p>
<p class="l"><b>Dana:</b> It's what the order of priority gives us. If it doesn't meet your needs, we can discuss a flat-file extract next.</p>
</details>

<details class="scene">
<summary>Days 39 to 54: app registration</summary>
<p class="tag"><a href="https://www.ecfr.gov/current/title-45/section-170.404">§170.404(b)(1)</a> API condition · 10 business days to verify the developer, 5 more to enable the app</p>
<p class="l"><b>Maya:</b> Fine. We'll take the API so we can at least start testing chart retrieval.</p>
<p class="l"><b>Dana:</b> There's no charge to you for the certified API. We'll verify your company within ten business days and enable the app within five after that.</p>
<p class="n">The app is enabled on day 54. This is the one step where the rules give the developer a firm, short deadline and a price of zero, because the certified API has its own condition of certification.</p>
</details>

<details class="scene">
<summary>Days 54 to 70: the missing data, and write access</summary>
<p class="tag"><a href="https://www.ecfr.gov/current/title-45/section-171.204">§171.204(a)(3) and (b)</a> Infeasibility exception · written response within 10 business days</p>
<p class="l"><b>Maya:</b> The API returns medications, problems, labs, and notes. It has no patient messages and no refill requests, and it can't save a draft reply or pend a refill. Those are the product.</p>
<p class="l"><b>Dana, ten business days later, in writing:</b> For the messages, we can offer a nightly flat-file extract as a further alternative manner; licensing it would take up to 30 business days. Saving drafts and pending refills is a request to use EHI in order to modify EHI, and you are a third party. That is infeasible under the "third party seeking modification use" condition.</p>
<p class="l"><b>Maya:</b> A nightly file can't answer a message that arrived this morning. So there is no path?</p>
<p class="l"><b>Dana:</b> The modification condition doesn't apply when a health care provider asks its own business associate. Cedar Street could make the request.</p>
<p class="n">The 30-business-day window for the extract comes from the Licensing exception, <a href="https://www.ecfr.gov/current/title-45/section-171.303">§171.303(a)</a>: 10 business days to open negotiations and 30 to conclude.</p>
</details>

<details class="scene">
<summary>Days 71 to 95: the same ladder, a new requester</summary>
<p class="tag"><a href="https://www.ecfr.gov/current/title-45/section-171.301">§171.301</a> again, then <a href="https://www.ecfr.gov/current/title-45/section-171.204">§171.204(a)(4)</a> Manner exception exhausted</p>
<p class="l"><b>Dr. Okafor:</b> Then I'm asking. Let my clinicians use this agent. I'll provision it like any other staff account.</p>
<p class="l"><b>Quillon account manager:</b> We can amend section 4.2 with our Automation Enablement add-on: $90 per clinician per month, usage caps, and you indemnify us for anything the agent does.</p>
<p class="l"><b>Dr. Okafor:</b> That's more than we pay for the EHR seat. No.</p>
<p class="l"><b>Quillon, ten business days later, in writing:</b> We could not reach agreement on the manner requested. We have offered two alternative manners, the certified API and a flat-file extract. We do not provide the requested access to a substantial number of similarly situated customers. The request is infeasible.</p>
</details>

<details class="scene">
<summary>Day 96: the complaint</summary>
<p class="tag"><a href="https://www.law.cornell.edu/uscode/text/42/300jj-52">42 U.S.C. 300jj-52</a> · no deadline for a decision</p>
<p class="l"><b>Maya and Dr. Okafor</b> file an information blocking complaint through ONC's portal. The confirmation email has a case number and no timeline.</p>
<p class="n">The same month, Quillon announces Quillon Assist, its own agent, at $149 per clinician per month.</p>
</details>

<script>
(() => {
  const open = () => {
    if (!['#what-each-step-sounds-like', '#the-conversation-step-by-step'].includes(location.hash)) return;
    document.querySelectorAll('.gnt details.scene').forEach((d) => { d.open = true; });
    document.getElementById('what-each-step-sounds-like')?.scrollIntoView();
  };
  open();
  addEventListener('hashchange', open);
})();
</script>

## What the story shows

**The process took more than four months and produced a chart-retrieval integration that can't see the inbox the clinic wanted help with.** Of the 96 business days, 35 were periods the regulations themselves provide: 15 days for app registration and two 10-day response periods. The other 61 were waits with no limit at all.

**No single step is the problem.** Each exception was written for a reasonable case: a vendor shouldn't have to build every custom interface on demand, should be able to recover costs, license its technology, and protect security. Stacked together, and applied to a request that asks the vendor to build nothing, they become a procedure whose default outcome is delay.

**The requester needs a lawyer at every step.** Whether terms were at "market," whether an extract's royalty is "reasonable," whether a lockout was "tailored" are all judgments made first by the vendor and reviewed, if ever, after a complaint.

**The pending HTI-5 proposals would help only at the edges.** ONC [proposed](https://www.federalregister.gov/documents/2025/12/29/2025-23896/health-data-technology-and-interoperability-astponc-deregulatory-actions-to-unleash-prosperity) to say outright that "access" and "use" include robotic process automation and agentic AI, to remove the third-party modification condition, and to add contract-fairness tests to the Manner exception. The [October final rule](https://www.federalregister.gov/documents/2026/10/28/2026-21943/health-data-technology-and-interoperability-onc-deregulatory-actions-to-unleash-prosperity) deferred all of it. Even if finalized, the proposals leave the structure in place: the agent's developer is still a requester, the vendor still controls an "interoperability element," and the Licensing and Fees exceptions still frame the negotiation.

## A different premise: the agent works for the customer

Go back to the first scene. Before anyone made a "request," Cedar Street already had everything it needed: licensed seats, a way to create accounts and assign roles, and screens that show each account what its role allows. The agent needs nothing the clinic couldn't give a new staff member. It asks the vendor to build nothing and to disclose nothing new.

So the rule should start there: **when software operates the EHR's ordinary client, by whatever means, under an account the customer has authorized and within that account's permissions, it is the customer's own use.** No request to the vendor exists, so no exception process begins.

The customer can set this up in either of two ways, and both have long-standing precedents.

- **In a clinician's own session.** The agent works alongside the clinician with exactly that clinician's access. Speech recognition, text expanders, and screen readers already operate EHR screens this way, and nobody thinks the dictation vendor needs a license from the EHR vendor.
- **Under its own account.** The customer provisions the agent as it would a scribe, a student, or a medical assistant: a named account, a role limited to the job, and a sponsoring clinician who reviews and signs. The agent's actions are logged separately, and its access can be narrower than any clinician's and revoked on its own.

The second model will often be the better one, because it reuses the provisioning, role, and audit systems health systems already run. The rule should protect both and let the customer choose.

This keeps authority where it belongs.

- **The health system or practice decides.** It is the vendor's customer and the HIPAA covered entity. It chooses which agents may be used, signs the business associate agreement with the agent's supplier, and can say no. An employed physician gets no right to override their organization.
- **The clinician stays accountable.** The agent can see and do only what its account allows. Everything it does is logged, and the clinician who signs answers for it as they do for a scribe's draft or a dictated note.
- **The vendor keeps its product.** It may secure access, manage load, and price by usage, as long as the rules are the same whether a person or a program is at the controls. It does not have to support, test, or warrant anyone's agent.

## Proposed regulatory text

The rule would sit in the conditions every certified EHR developer already agrees to. One of them, the [Assurances condition](https://www.ecfr.gov/current/title-45/section-170.402), has developers promise not to engage in information blocking "or any other action that may inhibit" access to and use of health data. That broader promise doesn't run through the information blocking exceptions, so a vendor can't answer it with the licensing and fee process from the story. ONC has built on it before, to require full-record export. The mechanics borrow from [another condition](https://www.ecfr.gov/current/title-45/section-170.403) that already bars developers from gagging customers who talk about their software: an annual notice that contrary contract terms won't be enforced, and no new contracts containing them.

In plain terms, a certified developer would have to:

- Let a customer have software of its choosing operate the product's ordinary interfaces, under a clinician's account or an account the customer sets up for the software, within that account's permissions.
- Let customers create, restrict, and deactivate accounts for software with the same tools and terms they use for staff.
- Require no separate license, agreement, registration, fee, or approval from the customer or the software's supplier.
- Price and limit use only by published measures that apply the same way to people and software.
- Not treat the software's view of the screens as a breach of confidentiality or intellectual property terms.
- Tell customers each year that contrary contract terms won't be enforced, publish its policy, and attest to all of this twice a year.

Actions taken through the software count as the customer's, and the developer owes the software no support. A sentence added to the information blocking definitions says that operating an interface the customer already has is not a separately licensable "interoperability element."

The draft text, for discussion:

<div class="reg">
<p class="h">§170.402(a)(6) Customer-authorized software.</p>
<p class="i">(i) <em>General.</em> A health IT developer must not prohibit, restrict, or otherwise interfere with a customer operating any user-facing interface of the developer's health IT through software selected by the customer ("customer-authorized software"), where that software acts under an account the customer has authorized for it and performs only functions the interface makes available to that account. Such an account may be (A) the account of an authorized user who directs the software, or (B) an account the customer provisions for the software.</p>
<p class="i">(ii) <em>Accounts for software.</em> A health IT developer must permit a customer to provision, assign roles to, restrict, and deactivate an account described in paragraph (a)(6)(i)(B) of this section using the same capabilities, and on the same terms, that apply to accounts for the customer's workforce members with comparable roles.</p>
<p class="i">(iii) <em>No separate permission.</em> A health IT developer must not condition the use described in paragraph (a)(6)(i) of this section on the customer, or the supplier of the software, obtaining a license from, entering an agreement with, registering with, paying a fee to, or being approved or certified by the developer.</p>
<p class="i">(iv) <em>Neutral terms.</em> A health IT developer must not impose a fee, limit, or technical measure that applies on the basis of whether input to, or requests made through, a user-facing interface originate from a person or from customer-authorized software, or of how they are generated. A developer may price or limit use of its health IT by published, objective measures of use, and may implement security and performance practices, provided each applies identically to all accounts regardless of how they are operated.</p>
<p class="i">(v) <em>Confidentiality and intellectual property.</em> A health IT developer must not treat the display of a user-facing interface to customer-authorized software, or its processing by that software for the purpose of operating the interface on the customer's behalf, as a breach of any confidentiality or intellectual property term.</p>
<p class="i">(vi) <em>Responsibility.</em> For purposes of this subchapter, actions taken through customer-authorized software are actions of the customer and of the authorized user who directs or sponsors it. A health IT developer is not required to support, test, or warrant customer-authorized software, or to maintain any interface for its benefit, and does not fail to conform to a requirement of this part by reason of actions taken through it.</p>
<p class="i">(vii) <em>Customer authority.</em> Nothing in this paragraph limits a customer's authority to determine which software may be used under its accounts.</p>
<p class="i">(viii) <em>Definition.</em> User-facing interface means any interface a health IT developer makes available to a customer's accounts for interactive use of health IT that includes one or more certified Health IT Modules, including web, desktop, mobile, and remotely displayed clients and the means by which those clients communicate with the developer's health IT.</p>

<p class="h">§170.402(b)(5) Maintenance of Certification: customer-authorized software.</p>
<p class="i">(i) <em>Notice.</em> A health IT developer must, annually beginning in calendar year 2028, issue a written notice to all customers stating that any contract provision that contravenes paragraph (a)(6) of this section will not be enforced.</p>
<p class="i">(ii) <em>Contracts.</em> A health IT developer must not establish, renew, or enforce any contract or agreement that contravenes paragraph (a)(6) of this section.</p>
<p class="i">(iii) <em>Publication.</em> A health IT developer must publish, at a publicly accessible hyperlink, its policy implementing paragraph (a)(6) of this section and any measures of use adopted under paragraph (a)(6)(iv).</p>

<p class="h">§170.406(a)(2) Attestations.</p>
<p class="i">Revise to add §170.402(a)(6) and (b)(5) to the provisions a developer attests to semiannually.</p>

<p class="h">§171.102 Interoperability element.</p>
<p class="i">Add: "(3) An interoperability element does not include the operation, through customer-authorized software as described in §170.402(a)(6) of this subchapter, of a user-facing interface that the actor has already made available to the customer."</p>
</div>

Four choices in this text are worth explaining.

- **It asks vendors to build nothing.** No new certification criterion, no test procedure, no standard. The accounts paragraph only stops a vendor from excluding software from the account tools it already offers. That fits a deregulatory program and takes effect as soon as contracts stop being enforced.
- **It covers the whole product, not just certified functions.** HTI-5 is shrinking the list of certified functions, so a rule tied to "certified capabilities" would shrink with it. The definition follows the EHI Export approach: any product that includes a certified module.
- **It allows usage pricing.** Per-seat pricing assumes a person's pace. A vendor can charge an agent that works overnight for the load it creates, provided a person creating the same load pays the same, and an account costs the same whoever operates it. How vendors restructure their price lists is for them and their customers to work out.
- **The responsibility clause is modest on purpose.** ONC can't rewrite tort law. It can say that, inside the certification program, what the agent does is the customer's action and not the developer's nonconformity, and that the developer owes the agent no support.

## Objections

**"A hallucinating agent will write garbage into the chart."** The agent can do only what its account's role permits, and the customer can make that role as narrow as it likes: draft but not sign, pend but not send. Whether drafts need review before signing is a clinical governance question for the organization deploying the agent, the same one it already answers for scribes, students, and templates.

**"Agents will overload the system."** Performance rules that apply to every account remain available, and so does usage pricing. What goes away is a limit that applies only because a program is at the controls.

**"Clinicians will hand their passwords to a third party."** They don't have to. The customer can give the agent its own account, with its own credentials, a limited role, and a sponsoring clinician, exactly as it would for a new scribe. That is safer than password sharing and uses the access controls the vendor already built. Where the agent instead works inside a session the clinician opened, no credential changes hands at all. In both cases the supplier is the customer's business associate, and the customer can cut off the agent's access without touching anyone else's.

**"Our interface is our intellectual property."** It is, and the proposal leaves copying and competing-product restrictions alone. It removes one use of those terms: declaring that a customer's own tool looking at the customer's own screens is a breach.

**"ONC lacks authority to regulate license terms."** Certification is voluntary, and ONC already regulates developers' contracts under the Communications condition and their fees under the API condition. The statutory phrase "any other action that may inhibit" appropriate access and use is broad, and this is a direct application of it.

**"Retailers and airlines are fighting agents too. Why should EHR vendors be treated differently?"** In September Amazon [blocked Meta's Muse shopping agent](https://siliconangle.com/2026/09/21/amazon-blocks-metas-muse-agent-from-shopping-on-users-behalf/), saying Meta gave no notice and the agent never identified itself as an AI. Amazon has also [sued Perplexity](https://www.bloomberg.com/news/articles/2026-03-10/amazon-wins-court-order-blocking-perplexity-s-ai-shopping-bots) over its shopping agent, though an appeals court [has since sided with Perplexity](https://www.emarketer.com/content/perplexity-comet-amazon-ai-shopping-agents-ruling). And this week United Airlines [changed its contract of carriage](https://techcrunch.com/2026/11/12/united-airlines-blocks-ai-agents-from-booking-flights-citing-cybersecurity-risks/) to bar AI agents from booking or changing tickets, citing security, while Delta, American, and JetBlue [let customers decide](https://www.forbes.com/sites/suzannerowankelleher/2026/11/12/united-airlines-blocks-ai-agents-booking-flights/). This post takes no position on those fights, because health care differs in four ways.

- **Congress has already decided the question for health data.** The Cures Act prohibits interfering with access to and use of electronic health information, and makes that a condition of EHR certification. Retail and travel have no such statute.
- **The customer is a licensee, not a visitor.** A shopper's agent arrives at a free storefront whose business depends on the visit. A clinic pays for its EHR and runs its own operations on it, and the records inside are the clinic's and its patients'. The vendor holds them as the clinic's business associate. The closer analogy is a company automating its own accounting system.
- **The customer can't walk away.** A shopper can buy elsewhere in a minute. A practice that dislikes its vendor's agent policy faces a migration measured in months or years and a real risk to its records.
- **The agent is identified.** Amazon's complaint about Muse was that it never said it was an AI. Here the agent runs under an account the customer provisions, with its own role and its own audit trail.

## What this does for APIs

This proposal is not a retreat from standards-based APIs. An agent clicking through screens is slow and brittle compared with a good API, and both vendors and developers would rather use one. But today the vendor's alternative to offering a good API is offering nothing. If customers can always fall back on the screens they already pay for, the vendor's best move is to offer something better: a faster, safer, fairly priced API or MCP server that agents prefer. ONC's planned work on write APIs and automation in its next rulemaking would build on that floor.

Patients face the same problem with portals, and the same principle should apply there. I've [written about that](/blog/posts/interoperability-vs-absorption) separately. This proposal covers clinicians and the organizations that license EHRs.

---

Sources: [45 CFR Part 171](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-D/part-171) · [45 CFR Part 170, Subpart D](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-D/part-170/subpart-D) · [HTI-5 proposed rule, 90 FR 60970](https://www.federalregister.gov/documents/2025/12/29/2025-23896/health-data-technology-and-interoperability-astponc-deregulatory-actions-to-unleash-prosperity) · [HTI-5 final rule](https://www.federalregister.gov/documents/2026/10/28/2026-21943/health-data-technology-and-interoperability-onc-deregulatory-actions-to-unleash-prosperity) · [SMART Health IT comments on HTI-5](https://smarthealthit.org/2026/02/comments-on-the-hti-5-proposed-rule-rin-0955-aa16/)

</div>
