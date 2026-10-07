---
title: "Software Statements for the Medicare App Library"
date: 2026-05-26T19:40:00
added_at: 2026-10-06
slug: software-statements-for-the-medicare-app-library
original_url: "https://www.linkedin.com/pulse/software-statements-medicare-app-library-josh-mandel-md-robze"
linkedin_id: robze
banner: ./banner.png
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7465132578774138881"
  share_id: "7465132578774138881"
  share_type: "ugcPost"
  posted_at: "2026-05-26T20:11:42"
  visibility: "MEMBER_NETWORK"
  commentary: |
    With one neat trick, CMS could give a boost to apps throughout the Health Tech Ecosytem ;-) Read on for a modest proposal.
    
    (Amy Gleason Zac Jiwa Anthony Polizzi FYI!)
---

### Why this is worth CMS's attention

CMS Health Tech Ecosystem has dozens of Aligned Networks and a growing App Library of vetted patient-facing apps. When an app shows up at a network, how can that server tell it is a real CMS-listed app, validate its identity, and learn what policies should apply? Right now there is no shared answer, so every network embarks on a path toward inventing one: a custom portal, a certificate authority, a trust-community scheme, a registration protocol. Reading wide consensus might take a year of working-group effort and, in the meantime, a different onboarding process for every network an app wants to reach.

CMS will not make all this complexity go away. A network still runs its own registration, manages client IDs, and sets policy. What can go away is the manual re-vetting, app identification, and key collection that duplicate work CMS already conducts.

CMS already makes a trust decision by publishing apps in its App Library. This proposal asks CMS to write that decision down as a signed, verifiable artifact. A developer can carry it to a network, or a portal or API can fetch it on demand. It is a building block the rest of the ecosystem can leverage, reducing work that every network would otherwise redo for every app.

*Throughout this post "network" is shorthand for a CMS Aligned Network together with the data holders participating in it: the endpoints an app actually registers with and reads data from. The same artifact is equally usable by a data holder that belongs to no Aligned Network and simply chooses to accept a CMS-signed statement.*

### TL;DR

For every active Medicare App Library listing, CMS should sign and publish a short-lived JWT (a software statement) recording the app's identity, its key location, its Library status, and the data it is eligible to request, so that any CMS Aligned Network can automate app registration instead of re-vetting.

### What CMS already has... (and one gap)

CMS has built almost all of the trust machinery already. App Library admission requires identity verification, FHIR R4, SMART on FHIR, integration with a CMS Aligned Network, and independent review by a recognized vetting partner. Blue Button's CMS Aligned Network flow already authenticates apps asymmetrically: the app must be listed in the Library and must register a JWK Set URL, and its token-request JWT carries a kid resolvable at that URL.

What is missing is a way to carry that trust. Today the result of CMS's review lives in a webpage and in a JWKS URL emailed (!) to the Blue Button team. Every other network that wants to accept the same app starts over: confirm it is really listed, collect its keys, decide what it may request. The review happened once, but the result is not portable.

### Now... in a world where CMS takes this one incremental step

CMS signs the decision and publishes it. For each active app, CMS exposes a path like:

A CMS Aligned Network fetches it, verifies the CMS signature against CMS's published key, and reads everything it needs to register the app. No email, no ticket, no independent re-vetting. The statement is short-lived (e.g. 24 hours); CMS stops re-issuing it the moment an app is suspended or delisted, so a stale statement cannot keep a removed app alive.

A statement looks something like this:

Three things carry the weight:

* software\_id: a link back to this software's library entry, so authorization servers can correlate registrations and stay up to date on library status
* jwks\_uri: the app's key location, which CMS verified the app controls (a CMS nonce published at a .well-known path) and monitors thereafter. The app rotates its own keys at that URL with no CMS involvement; nothing in the statement freezes.
* library\_status: active, suspended, delisted. A network checks one field instead of re-confirming a listing.

A network consumes the statement however suits it: ingest a CMS feed of all active statements and pre-provision in bulk; accept the statement at an RFC 7591 /register endpoint as the software\_statement; or have a portal pre-fill its manual form from it. Same artifact, three doors.

Runtime does not change. Apps still authenticate with private\_key\_jwt and a kid, exactly as cms\_smart already does. The statement governs registration, not the token call.

Security note: Because the CMS statement is bound to the app's verified jwks\_uri, it is only useful to someone who controls the corresponding private keys; an attacker copying the statement still cannot authenticate. To prevent unauthorized "junk" registrations, networks can require the client to present a short-lived, self-signed JWT in the Authorization header. By verifying this token against the keys retrieved from the CMS-approved jwks\_uri, the network confirms key ownership at registration time without departing from standard RFC 7591 structures.

### What it removes

The statement does not replace a network's registration; it removes the manual work inside it. Instead of confirming the listing, collecting keys, and deciding what the app may request, a network reads those facts from a CMS-signed artifact: verify one signature, read four fields. The vetting review, the key-collection email, the ticket... all that can melt away. A developer carries the statement to whatever network or portal they are registering with; a portal or API discovers it when it needs it.

It is deliberately not a certificate authority. CMS does not need to issue x509 certs, apps do not buy or manage certs, and there is no CRL or OCSP to operate. The statement is one signed JWT: a format CMS's own services already produce and verify. That is what makes it fast: it asks CMS to publish what it already knows, in a format it already uses, not to stand up new infrastructure.

### What CMS would need to do

* Verify and record an app's jwks\_uri at admission (HTTPS-origin challenge); monitor it afterward.
* Sign and publish one statement per active app, re-issued on a short cycle, and publish CMS's signing key at a well-known location.

This reuses the App Library's existing review workflow and a standard JWT signing path. It is a small, self-contained feature -- the kind of thing that can be prototyped and put in front of networks quickly.

### References

CMS, "Submit your app to the Medicare App Library." <https://www.cms.gov/priorities/health-technology-ecosystem/overview/medicare-app-library/submit-your-app>

CMS Blue Button API, "CMS Aligned Networks Developer Documentation." <https://bluebutton.cms.gov/cms-aligned-networks-documentation/>