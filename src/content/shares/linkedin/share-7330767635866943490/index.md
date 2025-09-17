---
title: "USCDI: More Than A Suggestions Box?"
date: 2025-05-21T01:33:23
slug: share-7330767635866943490
share_url: "https://www.linkedin.com/feed/update/urn:li:share:7330767635866943490"
share_type: "share"
share_id: "7330767635866943490"
visibility: "MEMBER_NETWORK"
---

USCDI: More Than A Suggestions Box?

Welcome back to Fun with the CMS/ASTP/ONC RFI!

Today's Policy: Steward USCDI Development for Meaningful Interoperability
Full Recommentation & GitHub Links: https://lnkd.in/gFkDyfSq
Voice: EHR Vendor PM (Strictly off-record, capiche?)

---

Alright, let's talk USCDI. Again. It's supposed to be our common language, right? The foundation for actual interop. But between us, the way it plays out... it's a masterclass in meeting the letter, not the spirit.

The real mess isn't just USCDI itself. It’s the pipeline. ONC drops a new USCDI version. Fine. Then it lands in SDO-land, say, for the US Core IG. That's where the real fun begins. Every vendor has folks there. Officially, we're all about robust interoperability. Unofficially? Often it's how do we interpret this so it’s easiest for our current system and still gets us certified?

So, you see these tortured discussions. Someone proposes a solid, specific way to handle a complex data element. Then comes the chorus: Our legacy system only does X. Can we make Y and Z optional? or Can support just mean we can store it as an opaque blob? Slowly, strong requirements get diluted into something... technically compliant but practically useless for real data sharing. We advocate for trivial interpretations, then build products that conform perfectly to that weakened spec. We pass certification. Interoperable? Barely.

It's a cycle: vague top-level guidance leads to flexible (read: weak) IGs, which leads to products that check boxes but don't actually help clinicians or patients.

Now, this RFI response has a few points on Steward USCDI Development that, honestly, could make my job less about navigating ambiguity:

1. Evidence-Based USCDI Prioritization. Thank you! Add data elements with demonstrated, widespread real-world use. Not just because someone influential asked nicely.
2. Clear Functional Expectations from ONC for SDOs. This is gold. If ONC clearly says, When we add ElementX to USCDI, here’s what we expect systems to do with it, before it hits the SDOs, it gives everyone a much clearer target. It curtails the interpretive dance in IG development.
3. Iterative Refinement & Feedback Loop. Makes sense. See what’s working, what’s not. Adjust.
4. Conformance Testing aligned with SDO IGs (that reflect ONC's functional intent). If the IGs are actually robust because ONC's initial guidance was clear, then testing means something. Certified might start to mean actually works with others.

If these things happened, we'd spend less time arguing over what a vague spec meant and more time building genuinely useful, interoperable features. It raises the floor for everyone.
