---
title: "Better Browser APIs for Sharing SMART Health Cards, FHIR Bundles, and other Digital Credentials"
date: 2025-05-15T21:52:00
slug: better-browser-apis-for-sharing-smart-health-cards-fhir-bundles-and-other-digital-credentials
original_url: "https://www.linkedin.com/pulse/better-browser-apis-sharing-smart-health-cards-fhir-other-mandel-md-tguxc"
linkedin_id: tguxc
banner: ./banner.png
---

Created on 2025-05-15 21:52

Published on 2025-05-15 22:11

*Josh Mandel Explores New Presentation APIs for Digital Health Data.*

**To hear my real voice, watch the YouTube demo below :-) This third-person article is an experiment working with LLM-prompted "objective analysis" of the full audio + video content. I think it's pretty cool, but I'd love your feedback on the format as well as the content. And I'm happy to share prompts if anyone's curious.**

[Related Article: better-browser-apis-for-sharing-smart-health-cards-fhir-bundles-and-other-digital-credentials](/posts/better-browser-apis-for-sharing-smart-health-cards-fhir-bundles-and-other-digital-credentials)

For years, the promise of truly portable, user-controlled digital credentials has shimmered on the horizon of health IT. We’ve made strides, notably with SMART Health Cards and Links, which Dr. Josh Mandel himself was instrumental in developing. These FHIR-based credentials provided a crucial, verifiable way to share health information like vaccination status and test results during a global crisis. Yet, as many of us know, the everyday act of *presenting* these credentials can still feel a bit… 2010. The dance of QR codes between screens, or the fumbling to get a phone to scan its own display, isn't quite the seamless future we envision.

Recently, Dr. Mandel offered a characteristically insightful and hands-on "deep dive" into an emerging solution: Google's experimental implementation of the W3C Digital Credentials API for Chrome and Android. This wasn't a polished product announcement, but rather a developer's journey, complete with the "alpha pain points" that offer invaluable lessons for our community as we navigate these new waters.

**The Vision: A Smoother Credential Handshake**

The core idea is to streamline how users present credentials stored in their mobile wallets to websites, whether on a desktop or mobile browser. Imagine a patient registering for a new clinic online. The clinic’s portal, using this new API, could request, say, their insurance information.

Mandel’s demonstration painted a clear picture:

1. A **relying party website** (e.g., a clinic portal on desktop Chrome) initiates a request for a specific type of credential using navigator.identity.get.

2. The desktop browser displays a **QR code**.

3. The user scans this QR code with their **Android phone**. (An amusing detail Mandel pointed out: the Android prompt still said "Use passkey," hinting at the API's evolution and underlying platform components.)

4. A **Bluetooth proximity check** verifies that the two devices are near each other—a crucial security layer.

5. The Android OS then **discovers installed wallet applications** that have registered to handle the requested credential type.

6. Mandel's custom "SHL Wallet" app, which he built for this exploration, signals it can fulfill the request.

7. The Android system displays a **standardized card selection screen** to the user, showing what information is about to be shared. This screen is populated with metadata provided by the wallet.

8. Upon selecting a credential, the user is shown an in-wallet consent screen. If consent is granted, the wallet prepares the actual response data (including **credential data**). In this case, the response includes a SMART Health Card JWS with insurance coverage details that are securely transmitted back to the relying party website.

**Under the Hood: The WASM Matcher and Platform Mediation**

A particularly innovative aspect of Google's approach is the use of WebAssembly (WASM) "matchers." Wallet developers don't just store credentials; they also provide a small, sandboxed WASM binary to the Android platform. When a credential request comes in, the platform executes these registered matchers.

Each matcher's job is to:

* Determine if it holds any credentials relevant to the request.
* If so, provide metadata (like card title, image, and a list of attributes that would be shared) for the Android system to display on the consent screen.

This architecture is clever. It allows for wallet-specific logic in matching and presentation, but keeps the actual card selection and data transfer mediated by the trusted platform. This means the platform doesn't need to understand every credential format under the sun; that responsibility lies with the wallet and its matcher. For our SMART Health IT context, this means a wallet could register a matcher specifically for "smart-health-card" or "smart-health-link" protocols.

**"Alpha Pain Points": Invaluable Lessons for Developers**

Dr. Mandel’s willingness to share the snags he encountered is a gift to the developer community. These "alpha pain points" are where the rubber meets the road:

1. **Documentation Discrepancies:** The official documentation for the Android credential registration API (specifically RegisterCredentialRequest) was out of sync with the actual Kotlin function signatures, particularly around an intent parameter. While the compiler helped, this caused initial confusion.

2. **The "Magic String":** This was a significant time-sink. To successfully register a verifiable credential (VC), the type field *had* to be set to the precise string com.credman.IdentityCredential. Using a more intuitive, application-specific type like me.fhir.shcwallet.DigitalCredential (as documentation might imply) would lead to successful registration but silent failures during the matching process. Mandel spent nearly two days on this, a testament to the frustrations of early-stage, under-documented APIs.

3. **WASM Woes:**

* *Lack of Build Documentation*: There was no clear guidance on how the WASM matcher binaries should be compiled (e.g., the required C function signatures for the WASM host to call, or the target like WASI). Mandel had to infer much of this from Google's C sample code.
* *Missing Entropy in WASI*: Perhaps the most technically obscure issue, he found that the WASI environment provided by the Android platform seemed to lack a source of randomness (entropy). This caused his Rust-based WASM matcher to panic whenever it tried to instantiate a HashSet (which requires entropy for its hashing). The only feedback was a silent failure – no matched cards. This highlights the need for more robust debugging tools and clearer environmental specifications for these sandboxed components.

These insights underscore the need for meticulous platform documentation, consistent API design, and better developer tooling for these nascent credentialing ecosystems.

**The Broader Landscape: OpenID4VP, mdoc, and the Quest for Ubiquity**

While Mandel’s demo focused on a custom protocol for SMART Health Links, he rightly contextualized this within the larger digital identity standards world. The navigator.identity.get API itself is designed to be protocol-agnostic. This is vital because various powerful standards are emerging:

* OpenID for Verifiable Presentations (OpenID4VP): This standard, evolving within the OpenID Foundation, aims to provide a standardized protocol layer for how relying parties request VCs and how wallets present them. It builds on the familiar OpenID Connect framework.
* ISO 18013-5 (mDL) and mdoc: This is the international standard for mobile Driving Licenses, often using the "mdoc" (mobile document) CBOR-based format. It's heavily focused on selective disclosure and strong cryptography for high-assurance identity.

The Google API, by providing a thin transport and card selection layer, can support interactions using OpenID4VP to request and present credentials in formats like mdoc or W3C VCs (which SHCs are an early, opinionated profile of). Getting these different layers and standards to interoperate smoothly is the grand challenge.

The broader ecosystem for digital credentials hinges significantly on other major players and regulatory landscapes. Apple, historically more guarded with its platform APIs, is anticipated to launch Digital Credentials API support (likely mdoc-focused) with iOS 19, though details remain speculative. Their approach will be critical for widespread adoption, and the health IT community will be watching closely to see how it aligns—or diverges—from the model Google is pioneering, particularly concerning support for multiple wallet providers and flexibility to allow permissionless protocol innovation. Simultaneously, the European Union's ambitious EUDI Wallet initiative is establishing a comprehensive regulatory framework with stringent requirements for digital identity wallets, aiming to provide citizens with secure, interoperable, and user-controlled means of identification and attribute sharing across member states. This EU-driven standardization, encompassing aspects from security to data minimization and user consent, will undoubtedly shape the features and capabilities expected from *all* digital wallet platforms, including those from Apple and Google, potentially driving a convergence towards more robust and privacy-preserving designs globally.

**Looking Ahead: LLMs and the Future of Credential Interaction**

Dr. Mandel briefly touched on the exciting potential of Large Language Models (LLMs) in this domain:

* LLM-Mediated Selective Disclosure: For complex credentials like a FHIR bundle representing an entire health record, an LLM could help a user understand a relying party's request and select only the necessary data elements to share, without being overwhelmed by hundreds of technical attribute choices.
* Questionnaire Filling: Imagine an LLM in your health wallet that could, with your permission, analyze an intake questionnaire from a clinic and intelligently pre-fill it using your stored health data, turning a tedious task into a quick review and confirmation.

**The Path Forward**

Dr. Mandel’s exploration is a valuable contribution. His open-source SHL Wallet and testbed (on GitHub at <https://github.com/jmandell/shl-wallet>) provide a concrete starting point for others. It’s clear that while the technology is still in "alpha," the foundational pieces for a more streamlined, secure, and user-controlled digital credential ecosystem are being laid.

For the SMART Health IT community, this means keeping a close eye on these developments. The ability to easily and securely present SMART Health Cards and Links through native browser and OS integrations could significantly improve patient experience and administrative workflows. However, as Mandel’s experience shows, early adoption requires patience, a willingness to dive deep into technical details, and robust community feedback to help these platforms mature. The journey "beyond the QR code" is underway, and it's one that promises a more empowered digital future for patients and providers alike.