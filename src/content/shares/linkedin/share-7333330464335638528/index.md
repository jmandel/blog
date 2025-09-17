---
title: "Why My App Doesn't Know Your Labs Are Ready"
date: 2025-05-28T03:17:09
slug: share-7333330464335638528
share_url: "https://www.linkedin.com/feed/update/urn:li:share:7333330464335638528"
share_type: "share"
share_id: "7333330464335638528"
visibility: "MEMBER_NETWORK"
---

Why My App Doesn't Know Your Labs Are Ready

Today's Policy: Mandate FHIR Subscriptions for Event-Driven Workflows

Full Rec: https://lnkd.in/gCD3K_SD

Voice: Digital‑health developer working on a patient‑centric research and public‑health platform

---
Our users ask the same question every week: “MyChart pings me the minute a result posts—why is your oncology‑support app still hours behind?” The blunt answer is that first‑party apps sit inside the EHR’s private event queue, while every external app is forced to poll. Some EHRs request that we limit polling to two or three hits per day to protect their production databases. If our sync runs at 8 a.m. and 4 p.m., a neutropenic patient might wait sixteen hours for a critical lab that the hospital’s own portal surfaced instantly.

It isn’t just patient convenience. Public‑health teams we support monitor cohorts for reportable conditions. They would love to know—right now—when a positive culture or a new encounter lands. Instead, we drop 50 000 FHIR "_lastUpdated=yesterday” queries every night and hope nothing urgent slipped through.

FHIR Subscriptions would close the gap. The R4 “Subscriptions Backport” guide has been out for years, and the Argonaut “Patient Data Feed” defines a ready‑to‑use topic that servers can stand up today. Servers notify us only when something actually changes; we stop hammering their APIs with speculative polling, and patients get the same real‑time push that first‑party apps enjoy.  

Some EHR vendors already pilot topic‑based feeds, but without a certification requirement it remains optional plumbing. The result is a two‑tier ecosystem: the hospital’s own app runs on insider events, everyone else pieces together a best‑effort sync.

Making baseline FHIR Subscriptions—think “patient‑data‑feed” for single‑patients and bulk cohort topics for public health—a condition of certification would level that field overnight. No more negotiations over polling windows. No more batch delays that put high‑risk patients and outbreak detection on hold. Just one standard callback that any authorized app can register once and trust forever.

Real‑time data shouldn’t be gated by whether you wrote the EHR. Patients and public‑health agencies need the same speed the portal already gets. FHIR Subscriptions turn that from privilege into baseline infrastructure.
