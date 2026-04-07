---
title: "By far the hardest thing about building an end-to-end agent skill that helps a…"
date: 2026-02-19T16:17:27
slug: share-7430284391249063937
share_url: "https://www.linkedin.com/feed/update/urn:li:share:7430284391249063937"
share_type: "share"
share_id: "7430284391249063937"
visibility: "MEMBER_NETWORK"
---

By far the hardest thing about building an end-to-end agent skill that helps a patient submit a full EHI export request to their healthcare provider is.. getting current frontier models to **correctly fill out a PDF form** when the form has not been annotated with proper form fields. After dabbling in a great many heuristics, I have settled on a workaround: retranscribe the entire form as a markdown document, which frontier models can do brilliantly well. I'm not sure if providers will accept this, but I prefix the transcribed form with:

> Note to Medical Records Department: Your published authorization form is a non-fillable PDF (it lacks interactive form fields), which prevents electronic completion. Pursuant to 45 CFR § 164.524(b)(1), covered entities may not impose unreasonable measures that serve as barriers to individuals requesting access. This document faithfully reproduces all content from your authorization form with the required information completed.
> Form source: https://lnkd.in/gz9HKNyt

"Deven McGraw I would love your perspective on whether forcing patients to use a non-fillable form might in fact be considered an unreasonable measure that serves as a barrier to individuals requesting access :-)
