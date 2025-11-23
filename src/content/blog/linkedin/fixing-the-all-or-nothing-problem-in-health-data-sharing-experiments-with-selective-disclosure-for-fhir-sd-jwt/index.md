---
title: 'Fixing the "All or Nothing" Problem in Health Data Sharing: Experiments with Selective Disclosure for FHIR (SD-JWT)'
date: 2025-11-21T23:27:00.000Z
slug: fixing-the-all-or-nothing-problem-in-health-data-sharing-experiments-with-selective-disclosure-for-fhir-sd-jwt
original_url: "https://www.linkedin.com/pulse/fixing-all-nothing-problem-health-data-sharing-fhir-josh-mandel-md-9k6gc"
linkedin_id: 9k6gc
banner: "https://media.licdn.com/mediaD5612AQEDC8wO0UHucA"
---

The IETF recently published **RFC 9901**, standardizing *Selective Disclosure for JSON Web Tokens* (SD-JWT). This is a significant technical milestone for how we handle verifiable clinical information.

I’ve focused throughout my career on the mechanics of sharing health data. As the lead author on the SMART Health Cards and Links specifications, I’ve seen the trade-offs required to get credentials working at a global scale.

With the publication of the new RFC, I want to outline why SD-JWT offers an important new capability for health credentials, and share a prototype I’ve built to demonstrate how it works with FHIR.

*If you'd rather see a guided tour + live demo, check out the video version of this post...*

### The Spectrum of SharingIn healthcare, "sharing" covers a massive range of needs.

Most of the time, **verifiability isn't strictly required**. Patients are authoritative sources for how they feel and what they’ve experienced. If a patient uses a SMART Health Link to share a record of their daily step counts or a list of the meds they (actually!) take, the recipient doesn't need cryptographic proof that the patient hasn't tampered with the data. (After all: what would "tampering" even mean for patient-attested data, patient-reported outcomes, and so on?)

Even for externally-sourced EHR data, the value of verifiability is often limited. But there is a narrow, critical slice of use cases where **provenance and integrity are non-negotiable**. These include data like:

- Proof of vaccination.

- Negative infectious disease tests.

- Proof of insurance coverage for a specific date.

- Drug screenings.

In these scenarios, the recipient ("Verifier") needs to know that the data originated from a trusted issuer and hasn’t been tampered with, even if it passed through the patient’s ("Holder's") hands.

### Privacy and the SMART Health Card CompromiseWhen sharing verifiable data, we usually want to minimize disclosure. If you need to prove a specific vaccination status for work or travel, you shouldn't necessarily have to hand over your home address, phone number, or unrelated medical history.

We designed SMART Health Cards (SHC) to solve the verification problem during the height of the COVID-19 pandemic. We prioritized speed and broad platform support, using standard JWTs where the digital signature covers the *entire* payload. You can't redact a field in a standard JWT without breaking the signature.

To protect privacy within those constraints, we relied on **Minimal Disclosure via Profiling**.

We defined rigid schemas that stripped out non-essential data at the source. The "COVID-19 Immunization" profile, for example, forced issuers to include *only* the patient's name, birth date, and vaccine details. Data like "home address" was simply forbidden from the payload.

This was a necessary compromise for a pandemic response, but it doesn't scale well. It is difficult to create a global consensus profile for every possible permutation of data a patient might need to share (e.g., "School Sports Physical" vs. "Insurance Prior Auth").

### Enter SD-JWT (RFC 9901)SD-JWT introduces a more flexible approach. It allows an Issuer to sign a large, comprehensive dataset (like a full FHIR Bundle), while enabling the Holder to selectively conceal specific data elements before presenting it to a Verifier—**without breaking the issuer's signature.**

### How It WorksTo explain the mechanism, it helps to visualize the data as physical objects rather than a string of code.

**1. The Issuer (Packaging)** Imagine the Issuer takes your health record and puts individual data elements (Name, DOB, Diagnosis) into separate, locked boxes. They place these boxes on a pallet and apply a "Master Seal" (the digital signature) to the entire collection. They hand this pallet to you.

**2. The Holder (The Logic)** You are the Holder. You have the keys to the boxes. When you need to share data, you decide which boxes to unlock. If you want to share your vaccine status but keep your address private, you simply leave the address box locked. You are not altering the data; you are just choosing what to reveal.

**3. The Verifier (The Check)** The Verifier looks at the pallet. They check the Master Seal to ensure the collection is authentic and hasn't been tampered with. They can read the contents of the unlocked boxes. They can see that the locked boxes exist and are part of the signed collection, but they cannot see inside them.

*(****Technical Note:**** For those interested in the underlying mechanics: The "locked boxes" are essentially salted hashes—or "digests"—of the individual JSON values. The Issuer signs a payload containing these digests. When the Holder discloses a value, they provide the plaintext value and the salt. The Verifier hashes that input and confirms it matches the signed digest. Because the Issuer signed the digests, the signature remains valid even if the Holder withholds the plaintext for other fields.)*

### The Frontiers: Unlinkability and Holder BindingWhile SD-JWT is excellent for selective disclosure, it is worth noting where it fits in the broader landscape of privacy and security features.

**Unlinkability:** If a patient presents the same SD-JWT to two different Verifiers, those Verifiers can potentially collude to track the user based on the issuer's unique signature. SD-JWT does not solve this "correlation" problem. To achieve true unlinkability—where a user can prove facts about themselves without being tracked across sessions—we would need to look toward more advanced cryptographic primitives (like Zero Knowledge Proofs/BBS+ signatures). This is a powerful capability, but one that is still maturing.

**Holder Binding:** There are cases where knowing *what* happened isn't enough; you need to know that the person presenting the data is the correct subject. Standard SMART Health Cards are "bearer tokens"—if you email your card to a friend, they can present it. SD-JWT supports **Key Binding**, allowing the Holder to prove they possess a specific private key or secure device associated with the credential. This adds a layer of assurance regarding the presenter's identity.

### Applying SD-JWT to FHIRRFC 9901 gives us the mechanism, but we need conventions to apply it to healthcare data safely. FHIR is a complex, nested tree structure. If we allowed redaction at the character level, the data would be unusable.

I have built a reference implementation that wraps standard FHIR data in SD-JWT. To make this practical, I enforced a few implementation choices regarding granularity and safety:

- **Data Type Granularity:** We don't redact part of a date or one line of an address. We treat FHIR Data Types (like HumanName, Address, Coding) as atomic units. You either disclose the whole HumanName or none of it. This keeps the data semantically readable.

- **Recursive Logic:** For container elements (like a Bundle.entry or a Resource property), we disclose the container but allow redaction of the children.

- **The "Modifier" Safety Rule:** This is critical. In FHIR, "Modifier Elements" (like a status of entered-in-error or not-given on a vaccine record) change the meaning of the entire resource. You cannot safely interpret a resource if a modifier is hidden. My implementation ensures that if a resource is disclosed, its modifier elements are *mandatory*—they cannot be redacted.

### Introducing: FHIR Redaction StudioTo demonstrate this, I’ve released the **FHIR Redaction Studio**. It’s a browser-based tool where you can play the role of the Holder.

[**Try the Demo: joshuamandel.com/fhiredaction-studio/**](https://joshuamandel.com/fhiredaction-studio/)

*(Source: *[*https://github.com/jmandel/fhiredaction-studio*](https://github.com/jmandel/fhiredaction-studio)*)*

In the studio:

- **The Artifact:** On the left, you see a verifiable FHIR bundle signed by an issuer.

- **The Action:** You use a cursor (styled as a permanent marker) to cross out the fields you don't want to share.

- **The Result:** As you redact fields (like "Family Name" or specific identifiers), the tool re-packages the SD-JWT in real-time.

- **Verification:** You can inspect the raw output to see exactly what the Verifier receives: a sparse JSON tree where redacted values are replaced by incomprehensible hashes, yet the cryptographic integrity remains 100% intact.

This tool uses an open-source library I wrote to implement the SD-JWT spec, wrapped with the FHIR-specific logic described above.

### The Path ForwardThis technology offers a practical path toward a future version of verifiable health records. Instead of relying on rigid profiles, we could issue comprehensive patient summaries and empower patients to decide exactly how much of that story to tell in any given context.

It preserves privacy, maintains data integrity, and thanks to RFC 9901, it is now a standard that we can begin to build against.