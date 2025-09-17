---
title: "ID Verification Wasn't Enough\": Data Breach Risks in TEFCA IAS"
date: 2025-05-27T19:56:27
slug: share-7333219555755925504
share_url: "https://www.linkedin.com/feed/update/urn:li:share:7333219555755925504"
share_type: "share"
share_id: "7333219555755925504"
visibility: "MEMBER_NETWORK"
shared_url: "https://joshuamandel.com/cms-rfi-collab/req_tefca_trustworthy_ias_architecture?1234"
---

[Shared link](https://joshuamandel.com/cms-rfi-collab/req_tefca_trustworthy_ias_architecture?1234)

ID Verification Wasn't Enough": Data Breach Risks in TEFCA IAS

Welcome back to Fun with the CMS/ASTP/ONC RFI!

Today's Policy: Mandate a Trustworthy and Accountable Architecture for All TEFCA Individual Access Services (IAS)

Full Rec: https://lnkd.in/gn4NMG7F
Voice: Patient Concerned About Data Breaches

---

I manage Type 1 diabetes and recently connected a new app to access my endocrinologist's records. The app verified my identity perfectly - government ID, facial recognition, the works. TEFCA requires this high-assurance identity verification (IAL2), and it worked smoothly.

But here's what keeps me up at night: verifying WHO I am isn't the same as verifying WHAT I authorized.

I selected "share from Dr. Smith's Endocrinology Practice" in the app. But there's no external validation of my limited consent. Once authenticated, the app can technically query every TEFCA participant nationwide - my mental health evaluations, my fertility history, even old college health records. Imagine what happens if the app is exploited. The current architecture has no way for responding systems to know that I only consented to share from one provider.

Imagine the breach headline: "Diabetes App Exposed Millions of Unrelated Health Records." The investigation would show perfect identity verification but no verifiable authorization boundaries. The app could be exploited to claim we "authorized" everything, with no proof otherwise.

This recommendation would complete TEFCA's security architecture. Just as identity must be verified through approved providers with cryptographic proof, authorization would require:

1. Trusted authorization services (not self-attestation by apps)
2. Cryptographically bound tokens proving exactly what was authorized
3. Clear audit trails of consent scope
4. Technical enforcement of authorization boundaries

Think of it this way: TEFCA currently checks your ID at the door but then lets you claim whatever permissions you want inside. This recommendation ensures both identity AND intent are cryptographically verified.

Without this, "share my endocrinologist records" could mean "access my entire medical history across America." That gap between user intent and technical capability? That's tomorrow's breach waiting to happen.

---

"Does knowing WHO without knowing WHAT concern you too?
