---
title: "A few aspects to untangle re: Individual Access under TEFCA! I'll touch on 1)…"
date: 2024-08-05T16:59:20
slug: share-7226270566305972224
share_url: "https://www.linkedin.com/feed/update/urn:li:share:7226270566305972224"
share_type: "share"
share_id: "7226270566305972224"
visibility: "MEMBER_NETWORK"
---

A few aspects to untangle re: Individual Access under TEFCA! I'll touch on  1) User Experience, 2) Developer Experience, and 3) Data... with a quick rundown and recommendations for each.
---

1. UX (user experience): How does a patient figure out where their data are, and how does a patient connect an app to each of these clinical sites? The "Your Your health records are coming to new apps" article (https://lnkd.in/gDSyF2Eg) seems to describe a system with no "record locator" functionality, and with site-specific logins to approve access -- i.e., the TEFCA approach appears to have the same key UX pain points as the non-TEFCA API-based ecosystem under current ONC regulations.

UX Recommendation: Require TEFCA QHINs to host a website where individuals can see which TEFCA participants...

A) ... hold my health records
B) ... have queried for my health records

Seating this requirement with QHINs will allow for focused solutions to the core problems of RLS and audit log access (mainly in the policy realm). Once these core problems are solved and RLS access is working via  "plain old website", QHINs can expand RLS availability via APIs. Before the core RLS functionality works for individual access, APIs are a distraction.
---

2. DX (developer experience): How does a developer register an app so it can  (with a user's permission) connect to health systems and retrieve data? The current TEFCA approach is limited to a class of "trusted" apps, which means that tinkerers and builders (i.e., patients solving their own problems with software) have no way to participate. TEFCA can do better.

DX Recommendation: Allow any app of a patient's choice to connect to TEFCA. This means solving a few key problems, but the core idea is "don't let an app sign its own permission slip!" Specifically, the following functions should be offered by QHINs on behalf of any individual-access TEFCA app:

A)  Identity verification. "Who is the user?"
B) Authorization. "What does the user want to share, and with whom?"

This way, only a small number of TEFCA-trusted services (offered by QHINs, and built atop strong common infrastructure like login.gov or on-device mobile driver's licenses + verifiable credentials) need to be responsible for the "hard stuff", and app developers can focus on their core health-related functionality.
---

3. Data: TEFCA is set up to support sharing diverse data, but the implementation focus is on the "Core" (USCDI) data set. Core is a good data set, and a good focus. That said, the Cure Act envisions API-based access to *all* Electronic Health Information, and TEFCA can take steps to enable this.

Data Recommendation: Define an automated path to access all EHI from any certified EHR, and include this functionality in TEFCA.

#health
#healthdata
#EHRs
#21stCenturyCures
#ONC
#TEFCA
#FHIR

"Dave deBronkart Hugo Campos James Cummings
