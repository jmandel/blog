---
title: "Health Tech Policy Peeps: EHI Exports are supposed to include patient/provider…"
date: 2026-02-13T15:24:42
slug: share-7428096789636935680
share_url: "https://www.linkedin.com/feed/update/urn:li:share:7428096789636935680"
share_type: "share"
share_id: "7428096789636935680"
visibility: "MEMBER_NETWORK"
shared_url: "http://docs.athenahealth.com/athenaone-dataexports"
---

[Shared link](http://docs.athenahealth.com/athenaone-dataexports)

Health Tech Policy Peeps: EHI Exports are supposed to include patient/provider secure message history (i.e., portal messages), yes?

I've been pulling b(10) export documentation from the CHPL API and looking at what certified EHR products actually document as included in their EHI exports.

athenahealth's Patient Engagement page (https://lnkd.in/dEG3kN_j) describes secure messaging as a core feature of their patient portal, integrated into athenaOne — which they market as their "fully-integrated EHR, medical billing & practice management, and patient engagement solution." But their EHI export documentation (https://lnkd.in/d9zThuJS) lists four export types spanning about 129 datasets, and I don't see secure messages in any of them.

[EDIT: Thanks to Joe Ganley in comments, who clarifies that portal messages appear as "Patient Cases"! https://lnkd.in/gRTzJF75 does not make this evident, but I'm delighted to know that it exists. Documentation is hard, and public examples alongside the public documentation would help. Read on for background, since I'll have the same questions about other EHRs as I proceed with a cross-cutting analysis.]



---

The certification criterion at 170.315(b)(10) requires exporting "all of a single patient's electronic health information that can be stored at the time of certification by the product, of which the Health IT Module is a part." The preamble to the Cures Act Final Rule (85 FR 25642) drives the point home: the export scope "is agnostic as to whether the EHI is stored in or by the certified Health IT Module or in or by any of the other 'non-certified' capabilities of the health IT product of which the certified Health IT Module is a part."
