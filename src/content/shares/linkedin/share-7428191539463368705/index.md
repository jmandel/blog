---
title: "After the marathon of registering Health Skillz across 500+ Epic organizations…"
date: 2026-02-13T21:41:12
slug: share-7428191539463368705
share_url: "https://www.linkedin.com/feed/update/urn:li:share:7428191539463368705"
share_type: "share"
share_id: "7428191539463368705"
visibility: "MEMBER_NETWORK"
---

After the marathon of registering Health Skillz across 500+ Epic organizations (and working around thousands of portal clicks, and debugging broken OAuth servers), I am excited to share a walkthrough of what that effort is unlocking! I have just published a demo of Health Skillz vNext, which brings two major features requested by early power users: Long-Term Access and Data Redaction (preview).

Full demo video: https://lnkd.in/gZVsvp-A
Try Health Skillz vnext: https://lnkd.in/gYtXXHkk

We review:

1. Long-Term Connections (Refresh Tokens). Previously, Health Skillz was a one-time download tool. Now, thanks to the confidential client registration I have been writing about, you can maintain a persistent connection. You can connect to providers like UW Health or Mass General Brigham once, then come back days or weeks later and click Refresh to fetch new data without logging into the portal again.

2. Redaction This is a new layer of control. Before you share data with an AI agent or download it for yourself, you can now apply Redaction Profiles. The app scans your record for names and identifiers, allowing you to scrub these from both structured FHIR data and unstructured clinical notes inside your browser before the data ever moves.  This is an early preview and I recommend that you download the data yourself and have a look to see if the redaction worked as you expect!
---

We show two core workflows.

A) download your records, redact them, and save them as a JSON file or an AI Skill zip for local use, or

B) Direct-to-AI flow, where an agent like Claude.ai will request your data via an end-to-end encrypted session.

I also show the configuration needed in Claude to allow it to fetch the skill and communicate with the encrypted session.

The vNext features are currently hosted on a staging domain linked in the repository and will be rolled into the main site soon.

Code and Docs: https://lnkd.in/gtJfa72K

"(Note: Health Skillz is an open-source personal project and is not affiliated with Microsoft, Epic, or Anthropic.)
