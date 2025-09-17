---
title: "Bulk Data: Can I Get an Amen for a Working \"_since\" Parameter?"
date: 2025-05-21T01:52:51
slug: share-7330772531684999168
share_url: "https://www.linkedin.com/feed/update/urn:li:share:7330772531684999168"
share_type: "share"
share_id: "7330772531684999168"
visibility: "MEMBER_NETWORK"
shared_url: "https://joshuamandel.com/cms-rfi-collab/req_update_bulk_data_cert"
---

[Shared link](https://joshuamandel.com/cms-rfi-collab/req_update_bulk_data_cert)

Bulk Data: Can I Get an Amen for a Working "_since" Parameter?

Welcome back to Fun with the CMS/ASTP/ONC RFI!

Today's Policy: Keep Bulk Data API Certification Current with FHIR Bulk Data Specifications
Full Rec: https://lnkd.in/gJjnti8K
Voice: Overworked Population Health Analyst (Send Coffee & Clean Data)

---

Okay, team, huddle up. Let's talk about getting usable data out of EHRs in bulk. Not for one patient, but thousands. This is population health bedrock: trends, cohorts, who's falling through cracks. The FHIR Bulk Data spec is supposed to make this easier. Supposed to.

My reality: I need an analysis on our diabetic cohort – updated labs, meds, encounters. Sounds simple. But getting that data? Frustrating. Some systems we connect to barely support the since parameter in their Bulk Data API. So, every update often means re-downloading everything for everyone. Gigabytes of redundant data. My servers cry. My timelines weep.

Then there's getting specific data. I can usually ask for just Observation resources, or just MedicationRequest resources using the type parameter; that's mostly okay. But what if I only need Observations for HbA1c, or Encounters that were hospitalizations? The Bulk IG has ways for this granular filtering, using parameters like _typeFilter. But consistent support for these within a Bulk Data export? Wildly inconsistent. So, I often pull all Observations or all Encounters for my cohort, then filter myself. More data than needed, more processing, more delays.

And Group management! Don't start. Defining a cohort for export should be easy via API. "Here's patient IDs, give me their data." But it's often clunky, needs manual EHR setup, or has arbitrary size limits. Like ordering custom pizza but with only three toppings allowed and a paper form per slice.

This recommendation, "Keep Bulk Data API Certification Current with FHIR Bulk Data Specifications," is my cry for help in policy form. It means ONC must ensure certified EHRs support current, useful, critical parts of the spec.

Specifically:
1. Mandate real support for essential parameters like the since parameter. I want incremental updates that work, only getting new or changed data.
2. Ensure robust support for granular data scoping, like the _typeFilter parameter or equivalent advanced search, usable within Bulk Data. So I can ask for specific subsets (like certain lab codes within Observations) and get just that, not the whole firehose for that resource type.
3. Require EHRs to support standardized API-based ways to create and manage FHIR Group resources for exports, without silly limitations. And signal that better, community-developed group management is coming.

If this happens, I spend less time wrestling broken APIs, more time analyzing data to improve patient outcomes. More timely insights. My coffee might stay warm before I finish cleaning the latest data dump.

---

"What's your biggest Bulk Data headache?
