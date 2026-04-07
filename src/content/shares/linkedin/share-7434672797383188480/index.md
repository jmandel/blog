---
title: "Today the SMART Health IT team published our response to ONC's Diagnostic…"
date: 2026-03-03T18:55:24
slug: share-7434672797383188480
share_url: "https://www.linkedin.com/feed/update/urn:li:share:7434672797383188480"
share_type: "share"
share_id: "7434672797383188480"
visibility: "MEMBER_NETWORK"
shared_url: "https://smarthealthit.org/2026/03/smart-health-it-comments-on-astp-diagnostic-imaging-interoperability-rfi"
---

[Shared link](https://smarthealthit.org/2026/03/smart-health-it-comments-on-astp-diagnostic-imaging-interoperability-rfi)

Today the SMART Health IT team published our response to ONC's Diagnostic Imaging Interoperability RFI. Quick context: after the imaging provisions of HTI-2 were withdrawn last year, ONC is taking a fresh look at how the certification program should handle diagnostic images. National Coordinator Thomas Keane  -- a radiologist -- has made this a priority. The RFI asks whether PACS and VNAs should be brought into the certification program, what standards to adopt, and whether the SMART Imaging Access spec could help. Comments close March 16.

The short version of our response: many building blocks already exist (SMART on FHIR, DICOMweb, OAuth token introspection). What's missing is the policy signal that tells the market to wire them together.

We make three recommendations.

First, ONC should articulate a clear functional vision: patients get a single sign-in covering clinical and imaging data, clinicians get a zero-click launch, backend services get fully automated access, and developers register once. No separate PACS portals, no separate credentials, no separate app registrations.

Second, ONC should extend Base EHR certification to cover imaging in a narrow way, with: imaging-specific authorization scopes, actionable metadata (à la FHIR ImagingStudy) with DICOMweb endpoint references, and policy-governed authorization that an external imaging system can enforce without its own identity and authorization policy stack.

Third, ONC should create a focused (not "Base EHR") certification criterion for imaging systems: serve DICOM via DICOMweb, rely on the EHR for access policy. That's it. If the EHR side is specified clearly, anyone can build the imaging side -- commercial PACS, open-source proxy, whatever.

There's a reason we're pushing hard on functional requirements over technical mandates. We've seen this movie before. A decade ago, EHRs were walled gardens with no standard API. We built the SMART on FHIR spec. The Argonaut Project proved it worked. But what actually drove adoption wasn't the spec -- it was ONC signaling through functional requirements that standardized APIs were the direction of travel. That regulatory pressure gave vendors the cover and the deadline to converge.

We're proposing the same playbook for imaging. The Argonaut Project has already demonstrated two viable approaches -- token introspection and "dual SMART launch" -- using today's certified EHR capabilities. ONC doesn't need to pick a winner. Set the functional bar, signal that specific standards will follow in future rulemaking, and let the industry align.

"https://lnkd.in/eaKn_Mqm
