---
title: "Patient Access Across Sites: What Makes a Request Trustworthy?"
date: 2026-04-28T19:21:00
added_at: 2026-10-06
slug: patient-access-across-sites-what-makes-a-request-trustworthy
original_url: "https://www.linkedin.com/pulse/patient-access-across-sites-what-makes-request-josh-mandel-md-ml0we"
linkedin_id: ml0we
banner: ./banner.png
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7454978812603375616"
  share_id: "7454978812603375616"
  share_type: "ugcPost"
  posted_at: "2026-04-28T19:44:15"
  visibility: "MEMBER_NETWORK"
  commentary: |
    The American Hospital Association posted comments last Friday on TEFCA individual access: hospitals are being asked to release records based on patient instructions captured elsewhere, while still carrying much of the risk if the request is wrong. While AHA demands delay (and a provider safe harbor, and new regulation of third-party apps)... I think the cleaner move is to make request issuance an explicit role, with real obligations, so capable apps can do it themselves and lightweight apps can rely on certified issuers.
    
    See my article below for a more complete thought :-)
also_posted:
  - share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7455003625812230144"
    share_id: "7455003625812230144"
    posted_at: "2026-04-28T21:22:51"
    commentary: |
      For cross-site patient access to work, data holders have to act on authorization requests captured by someone else -- and identity-proofing the patient does not, by itself, make those requests trustworthy. This document lays out what does, and how the obligations should sit in the ecosystem so lightweight apps can participate without each one carrying the full weight.
---

We are trying to move toward a model where a patient chooses an app, completes a setup ceremony that includes IAL2 identity verification, and then uses the app to retrieve data from multiple data holders.

Many data holders are reluctant to rely on **"IAL2 plus the app's representation of what the patient wants to share"** as the whole basis for release. If the patient's instructions are being captured and translated outside the holder's own workflow, the holder wants confidence that this has been done correctly, safely, and accountably.

This is the most immediate practical blocker to cross-site patient access. The safeguards a data holder would want here are mostly the same ones a patient should want, whether or not they would think to ask for them.

### What identity proofing does and does not establish

IAL2 helps establish **who the person is**.

But it does not, by itself, establish:

* what options the patient was shown for data sharing,
* what they selected,
* how those selections were translated into a data request,
* whether the request was later changed,
* whether mistakes or misuse can be detected,
* or whether the resulting request can be revoked, investigated, or disputed.

### Why this matters — to patients as well as data holders

A data holder is being asked to trust that the patient's instructions were captured faithfully, translated correctly, protected from tampering, and can later be explained if something goes wrong. That's a bigger ask than identity alone, and pushback from holders on this point is reasonable.

The patient has the same questions, even if they rarely phrase them this way:

* Did the app actually ask me what I meant to share, or did it ship a broader request than I intended?
* If someone later produces a release that claims to be from me, can I see it, challenge it, and have it reversed?
* If the app is compromised, or the company is sold, or the product is shut down, what happens to requests made in my name?
* Who, besides the app itself, has confirmed any of this is working correctly?

When these controls are missing, the patient absorbs the consequences — broader sharing than they meant, no way to challenge a release they didn't authorize, no recourse when something goes wrong.

### What can go wrong if this role is not done well

When an app gets this work wrong, patients usually absorb the harm and data holders end up holding the downstream liability.

### The request can be broader than the patient intended

A patient may have meant "share my records from CA but not TX," or "only the past two years," or "my medication list but not my full clinical notes." Poor defaults, confusing UX, loose mapping from user choices to request scope, or product incentives that favor over-collection can all produce a request broader than intended.

### Good-faith apps can still get it wrong

Bugs, matching errors, misconfigured defaults, faulty site-selection logic, or incorrect handling of time limits and data categories all happen. Without good records, these errors may be hard to detect and even harder to reconstruct later.

### Compromise at the app can turn into false or unsafe requests

If an app's admin systems, release pipeline, credentials, or signing keys are compromised, an attacker may be able to generate requests that appear legitimate downstream. Identity-proofing the patient at some earlier point doesn't help here; what matters is whether the app's security controls are strong enough for others to rely on its assertions.

### There may be no reliable way to investigate disputes

If a patient later says "I did not approve this" or "that is not what I meant," the ecosystem needs to answer basic questions: what was shown, what was selected, when it happened, what request was generated, and whether anything changed afterward. If the app cannot produce that evidence, the patient has no recourse and trust in the system breaks down.

### There may be no clear revocation or status model

Patients change their minds. Security incidents happen. Companies change ownership, shut down, or abandon products. If an app is effectively issuing instructions that others rely on, there needs to be a dependable way to expire, revoke, or invalidate them.

### Governance can change over time

An app that seems careful today may later change business model, ownership, staffing, or security posture. Data holders are right to worry about year five, not just day one.

### The ecosystem can end up limited by its weakest implementation

Some apps can do this work well; others cannot. If the ecosystem treats all trusted-directory apps as equally able to take on this role without stronger requirements, the practical level of trust gets set by the weakest implementation others are expected to accept.

### Capabilities that matter

Here is what "doing this well" looks like concretely. The list below is framed around what a data holder would reasonably want before relying on app-managed instructions, but each item is also something the patient benefits from directly. The "effort" note gives a sense of what an app would take on to build each capability itself. These capabilities are independent of the specific technology used (e.g., FAST Consent vs SMART Permission Tickets) — what matters is that the controls actually exist.

### 1. Accurate capture of patient instructions

* **Why it matters:** Both the holder and the patient need confidence that the request really reflects what the patient was shown and chose.
* **What "good" looks like:** The system keeps a structured record of the choices presented, the defaults, the selections made, and the time of issuance.
* **Effort if built directly by an app:** Moderate — product work plus durable recordkeeping.

### 2. Strong binding to the authenticated patient at the moment of issuance

* **Why it matters:** IAL2 shows who the person is, not that the right person gave these instructions at this moment.
* **What "good" looks like:** The app ties the issued request to a fresh, recent authenticated event rather than a stale session or background process.
* **Effort if built directly by an app:** Modest to moderate — mostly flow design, session discipline, and evidence retention.

### 3. Safe translation from patient choices into request scope

* **Why it matters:** Even a well-intentioned app can over-request if its defaults, mapping logic, or site-selection rules are wrong.
* **What "good" looks like:** Each patient choice maps clearly to what sites, time periods, and data categories may be requested; defaults cannot silently expand scope.
* **Effort if built directly by an app:** Modest to moderate — more design and testing discipline than deep infrastructure.

### 4. Tamper-evident issuance records

* **Why it matters:** If something goes wrong, the ecosystem — and the patient — needs to reconstruct what happened and detect after-the-fact changes.
* **What "good" looks like:** Append-only or otherwise tamper-evident records link the patient interaction, the resulting request, and any later status changes.
* **Effort if built directly by an app:** High — one of the main net-new engineering burdens.

### 5. Protection of signing and issuance infrastructure

* **Why it matters:** If issuance credentials, keys, admin tools, or release pipelines are compromised, false requests may look legitimate downstream.
* **What "good" looks like:** Keys are tightly controlled, signing operations are logged, admin access is limited, changes are reviewed, and critical infrastructure is monitored.
* **Effort if built directly by an app:** Moderate to high — usually requires real security engineering and operational maturity.

### 6. Revocation, expiration, and status checking

* **Why it matters:** Patients change their minds; incidents happen; companies shut down or change hands. Others need a reliable way to know whether a previously valid request is still valid.
* **What "good" looks like:** Requests expire on a clear schedule; there is a dependable status or revocation mechanism; emergency invalidation is possible.
* **Effort if built directly by an app:** Moderate — new service plumbing plus support processes.

### 7. Patient visibility and dispute handling

* **Why it matters:** Trust breaks down fast if a patient cannot see what was issued in their name or challenge it.
* **What "good" looks like:** The patient can view active or recent requests, understand what they authorized, and trigger investigation or revocation when needed.
* **Effort if built directly by an app:** Moderate to high — product work plus support and operations.

### 8. Ongoing governance and continuity

* **Why it matters:** Data holders and patients are not just trusting the app on day one; they are trusting the organization over time.
* **What "good" looks like:** There are controls for code changes, vendor risk, incident response, ownership changes, shutdown, and record retention.
* **Effort if built directly by an app:** Moderate ongoing burden — part engineering, part compliance, part operations.

### 9. Independent review

* **Why it matters:** Nobody — patient, holder, or regulator — should be relying only on the app's own description of its controls.
* **What "good" looks like:** The app or service can point to a meaningful external review of these capabilities, not just a privacy-policy statement or general attestation.
* **Effort if built directly by an app:** Moderate to high ongoing cost — depends on how formal the review program becomes.The practical answer: allow both models

If we are clear about the precise obligations, we can design a trust fabric where:

* **Highly capable apps can do the work themselves** if they are willing to meet the higher bar and demonstrate that they have done so.
* **Lightweight apps can rely on a specialized external issuer or network service** for this part of the job, while still delivering a good patient experience.

An app that wants to own these controls has to actually run them. An app that doesn't shouldn't have to build an entire issuance infrastructure just to participate — it should be able to inherit that work from someone who has.