---
title: "Why Every Certified EHR Needs to Support CDS Hooks"
date: 2025-05-28T03:10:42
slug: share-7333328840586338308
share_url: "https://www.linkedin.com/feed/update/urn:li:share:7333328840586338308"
share_type: "share"
share_id: "7333328840586338308"
visibility: "MEMBER_NETWORK"
shared_url: "https://joshuamandel.com/cms-rfi-collab/req_mandate_cds_hooks"
---

[Shared link](https://joshuamandel.com/cms-rfi-collab/req_mandate_cds_hooks)

Why Every Certified EHR Needs to Support CDS Hooks

More fun with the CMS/ASTP/ONC RFI.

Today's Policy: Mandate CDS Hooks for Seamless Clinical Decision Support Integration

Full Rec: https://lnkd.in/gFUd8s7u

Voice: Technical Lead, Cloud‑Based CDS Vendor

---

We run a clinical‑decision‑support service that spots medication‑adherence gaps and social‑risk triggers in real time. The math is hard; the biology is harder. Yet what slows us down the most is integrating with EHRs that still don’t speak the same language at the point of care.

When an EHR implements CDS Hooks, life is simple. A prescriber opens the medication‑order screen, the EHR fires an order‑select hook, we get the FHIR context, and we answer with a card that says, “Patient missed 3 of the last 4 fills—consider adherence counseling before escalating dose.” Time from contract to go‑live: measured in days.

Without CDS Hooks, we burn months:

• One‑off “embedded widgets” for Vendor A, maintaining separate code just to launch an iframe.

• A legacy proprietary rules engine for Vendor B that wants an XML payload over VPN.

• Batch flat‑file drop‑offs for Vendor C because they can’t surface anything in real time.

Multiply that by a dozen health‑systems and a half‑dozen EHR families and you see the problem: we spend more effort on plumbing than on refining algorithms or proving clinical value.

The gap isn’t for lack of standards. CDS Hooks has been stable since 2018 and is now at version 2.0, used in production by Epic, Altera Touchworks, and others. It rides the same OAuth and FHIR pipes that every certified patient‑access API already exposes. The only thing missing is a universal requirement that every certified EHR must implement a baseline set of hooks—patient‑view, order‑sign, and order‑select—with SMART‑on‑FHIR authorization and predictable prefetch.

If ONC makes that part of certification, three things happen immediately:

1. Vendors like us focus on what we’re good at (clinical intelligence) instead of writing adapters.
2. Health‑systems deploy innovation faster, because “install” becomes “enable.”
3. Patients benefit sooner, because their clinicians see the right insight at the right moment instead of an inbox report a week later.

"Clinical decision support is only as good as the path it travels. Standardizing that path is the next mile marker for real interoperability.
