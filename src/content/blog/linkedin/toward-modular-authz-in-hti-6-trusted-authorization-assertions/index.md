---
title: "Toward Modular AuthZ in HTI-6: Trusted Authorization Assertions"
date: 2026-05-01T17:16:00
added_at: 2026-10-06
slug: toward-modular-authz-in-hti-6-trusted-authorization-assertions
original_url: "https://www.linkedin.com/pulse/toward-modular-authz-hti-6-outsourcing-trusted-josh-mandel-md-9kure"
linkedin_id: 9kure
banner: ./banner.png
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7456030066825768961"
  share_id: "7456030066825768961"
  share_type: "ugcPost"
  posted_at: "2026-05-01T17:21:34"
  visibility: "MEMBER_NETWORK"
  commentary: |
    Thanks Aneesh Chopra for prompting me to think about the kinds of modularity we want in access permissions across the diverse EHRs, PACS, Document Repositories, Genomics Servers, and many other nooks and crannies where clinical data live... here are my thoughts about what a future round of certification might aspire to.
---

Certified EHR technology should allow a clinical organization to configure trusted external services that issue signed authorization assertions for use at the EHR's FHIR API.

The external service does not issue EHR access tokens, bypass the EHR authorization server, or replace the EHR's responsibility to apply local rules. It supplies a trusted authorization assertion that the EHR uses as one input — among several — when deciding what access to grant.

A typical assertion tells the EHR:

> This authenticated client, using this bound key, is acting for this person, who is requesting access to this patient or subject — identified either by a locally resolved EHR identifier or by an external identifier or linkage reference — for these scopes, for this purpose or workflow, for this amount of time.

The EHR validates the assertion, confirms the issuer is trusted by the clinical organization, applies EHR-held consents, restrictions, privacy rules, sensitive-data policies, and organizational policy, and issues an EHR access token only for the access that remains permitted after those local checks.

The authorization assertion is a trusted input to the EHR authorization decision, but it's not the final authorization decision.

### Why this division of work?

The clinical organization is the API Information Source. It carries the legal, regulatory, and clinical responsibility for what is released from its FHIR endpoint, and it holds the consent, restriction, segmentation, and proxy-access data needed to make release decisions correctly. That data lives in the EHR and cannot be safely replicated to outside parties.

Identity proofing, application trust evaluation, network governance, delegation capture, patient approval workflows, and local patient matching are different problems. They are specialized, change frequently, and benefit from concentration of expertise and tooling. A clinical organization may reasonably prefer to procure these capabilities from a service it deploys and configures for that purpose, rather than build them into the EHR core or duplicate them at every endpoint.

This requirement formalizes that split. External services handle identity, trust, approval and delegation capture, and resolution. The EHR continues to enforce what only it can enforce: local policy, local consent, and the actual release of data. External approval or delegation may inform the EHR's decision, but it does not override EHR-held consent, restriction, segmentation, proxy-access, or sensitive-data rules.

### Terminology

An **Authorization Assertion Issuer** is a service that evaluates facts outside the EHR's authorization server — such as identity, app trust, patient approval, delegation, network membership, purpose, workflow, legal basis, and (when deployed by or on behalf of the clinical organization) local subject resolution — and issues a signed **authorization assertion** that conveys those facts together with an access ceiling.

An authorization assertion is intended to be presented to the EHR authorization server and exchanged for an EHR-issued access token, after the EHR applies local checks. The assertion is not itself an access token for the EHR FHIR API.

A **Trusted Authorization Assertion Issuer**, referred to below as a *trusted issuer*, is an Authorization Assertion Issuer that the clinical organization has configured the EHR to trust.

A **locally deployed issuer** is operated by, or under contract to, the clinical organization, with access to the EHR sufficient to resolve a request to a specific local patient or subject record before issuing an assertion. The assertion carries the resolved local identifier.

A **network issuer** is operated by a third party — for example, a patient-access network or trust framework — that does not have local subject-resolution access at every participating EHR. A network issuer references a subject by an external identifier or by a previously established account linkage, leaving final resolution to the EHR.

Both patterns are in scope. The functional requirement must support both.

### Proposed functional requirement

A Health IT Module certified for standardized FHIR API access must support configuration, validation, exchange, and enforcement of authorization assertions issued by trusted external services.

The Health IT Module must allow an API Information Source, or an authorized administrator acting on its behalf, to configure one or more Trusted Authorization Assertion Issuers. A client must be able to present an authorization assertion from a configured trusted issuer to the EHR authorization server. The EHR authorization server must validate the assertion and, where permitted by local policy, exchange it for an EHR-issued access token.

The authorization assertion must be an intermediate authorization artifact. It must not itself be an access token for the EHR FHIR API.

The assertion mechanism must be defined by an openly published specification usable across issuers and EHRs that have not entered into bilateral integration agreements. An EHR must be able to validate an assertion from any issuer the clinical organization configures as trusted using the openly published specification, configured trust material, and standardized issuer or trust-framework metadata. Mechanisms that require pairwise custom integration between a specific issuer and a specific EHR do not satisfy this requirement.

The Health IT Module must define interoperable failure responses for rejected or narrowed assertions, sufficient for a client to distinguish broad categories such as issuer trust, assertion validity, client binding, subject-resolution failure, local-policy denial, or scope reduction, while avoiding disclosure of sensitive patient, consent, restriction, or segmentation information.

### Separation of responsibilities

A trusted issuer may assert facts including:

1. the identity of the requesting person;
2. the identity or trust status of the client application;
3. the client key, certificate, or trust-framework identity that must be used;
4. the subject for whom access is requested, expressed either as a locally resolved EHR identifier (for locally deployed issuers) or as an external identifier or linkage reference (for network issuers);
5. the relationship between requester and subject;
6. patient approval or delegation;
7. network membership or app-library status;
8. purpose, workflow, or legal basis;
9. requested or permitted FHIR scopes; and
10. requested or permitted duration of access.

The EHR authorization server must validate the assertion and combine it with local EHR-controlled authorization logic. At minimum, it must determine whether:

1. the assertion issuer is configured as trusted;
2. the assertion is cryptographically valid;
3. the assertion is intended for the receiving EHR, organization, endpoint, network, or trust framework;
4. the assertion has not expired;
5. the presenting client satisfies the assertion's client-binding requirements;
6. the asserted subject identifier — whether locally resolved by the issuer or external — corresponds to a current, valid local subject record at the time of exchange;
7. local policy allows the requested access;
8. EHR-held consent, restriction, privacy, segmentation, proxy-access, or sensitive-data rules further limit access;
9. the requested scopes fit within the assertion's access ceiling; and
10. any mandatory assertion constraints are understood and enforceable.

For assertions that carry a locally resolved subject identifier from a locally deployed issuer, the EHR authorization server must be able to rely on that resolved identifier, subject to revalidation that the identifier is current, valid, and not merged, split, retired, or otherwise restricted at the time of exchange. The Health IT Module may perform additional checks, but it must not require fresh primary identity matching as a condition of using this pattern.

The FHIR resource server must enforce the EHR-issued access token and associated constraints. It must not treat the assertion as a substitute for EHR-issued access tokens or EHR resource-server enforcement.

### Assertion as ceiling, not command

An authorization assertion establishes an authorization ceiling. The Health IT Module may narrow access based on local policy, consent, privacy restrictions, identifier revalidation, client registration, technical capability, or other enforceable controls. It must not grant access broader than the assertion permits.

Final authorized access must be no broader than the intersection of:

1. the access ceiling expressed in the assertion;
2. the scopes requested by the client;
3. the scopes and capabilities permitted for the authenticated client;
4. the subject resolved or revalidated by the EHR at exchange time;
5. the API Information Source's local policy;
6. EHR-held consent, privacy, segmentation, and restriction rules; and
7. the resources, interactions, and data supported by the certified FHIR API.

### Example 1: patient access through a network app

A patient chooses an app that participates in a recognized patient-access network. The app does not pre-register at every EHR-vendor-specific registration endpoint.

The clinical organization configures its EHR to trust an Authorization Assertion Issuer associated with that network. The network issuer verifies the app's identity and network participation, verifies the patient's identity, and issues an assertion stating that this app, using this client key, is acting for this verified patient and may request patient access for these scopes and this duration. Because the network issuer does not have direct EHR access at every participating site, the assertion references the patient by a network-level identifier or a previously established linkage.

The app presents the assertion to the EHR authorization server. The EHR validates the assertion, confirms the issuer is trusted, confirms the app is using the bound key, resolves the subject reference to a local record, applies local policy and consent restrictions, and issues an access token for the access that remains permitted.

This enables network-based patient access using an app of the patient's choice without separate registration at every EHR endpoint, while preserving the clinical organization's final decision role.

### Example 2: locally deployed issuer with verified patient identity

A clinical organization deploys, or contracts with, an Authorization Assertion Issuer that has access sufficient to resolve patients to local records.

The issuer verifies that the app belongs to a trusted app library, the app is using a recognized client key, the patient's identity has been proofed, and the patient is requesting access to their own record. It resolves the patient to the local subject identifier and issues an assertion carrying that identifier together with a broad patient-access ceiling.

The EHR validates the assertion, confirms the local identifier is still current, applies local restrictions, and issues an access token for the access that remains permitted. The EHR authorization server is not performing patient matching at this step; that work was already done by the specialized service the clinical organization deployed for it.

### Example 3: lower-trust app with explicit patient approval

A clinical organization may decide that lower-trust apps can participate only with explicit patient approval.

The patient interacts with an Authorization Assertion Issuer, signs in, reviews the app's request, and approves only certain categories of data. The issuer creates an assertion stating, for example, that this app, using this key, may request this patient's medication and allergy data for 24 hours.

The EHR validates the assertion, applies local restrictions, and issues a token limited to the approved categories. The lower-trust app can participate, but it receives only the data reflected in the assertion and permitted by the EHR.

### Example 4: external context plus EHR-internal consent

A patient may have a local restriction in the EHR that prevents disclosure of certain sensitive notes, proxy-restricted data, or other segmented information. An external issuer may issue an assertion authorizing a request, but when the assertion is presented, the EHR still applies its internal consent and restriction data.

The final token may exclude sensitive notes, proxy-restricted information, or other locally restricted data even when the assertion would have permitted them. This is the intended model: the assertion tells the EHR who is asking and what they are allowed to request; the EHR determines what it can actually release.

### Summary

Certified EHRs should be able to trust authorization assertions issued by external services, exchange them for EHR-issued access tokens, and enforce them together with local EHR policy — so that external identity, app-trust, patient approval, delegation, subject resolution, and network workflows can be performed by services the clinical organization has chosen and deployed to specialize in those tasks, without bypassing the EHR's final authorization role.