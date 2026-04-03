---
title: "SMART Permission Tickets: Argonaut Launch!"
date: 2026-03-24T16:10:00
slug: smart-permission-tickets-argonaut-launch
original_url: "https://www.linkedin.com/pulse/smart-permission-tickets-argonaut-launch-josh-mandel-md-uvruc"
linkedin_id: uvruc
---

Tomorrow, we are launching a new Argonaut project: **SMART Permission Tickets**. The goal is to define a standard way for authorization decisions to travel to data holders in a portable, machine-readable, and verifiable form.

### The friction we are trying to solve

Today, SMART on FHIR authorization requires deep involvement and decision-making from individual authorization servers.

If a patient wants to use a third-party app to aggregate data from five different health systems, they typically have to complete five separate OAuth flows and log into five separate portals. Advances in vendor-managed workflows like MyChart Central would still leave patients navigating per-vendor or per-network setup steps that add friction to the connection process. While networks are expanding access today, they provide little opportunity for patients to constrain access or delegate to caregivers.

On the system-to-system side, the bottleneck is about scoping access. A SMART backend service might be registered at a hospital, but there is no standard way to set limits on exactly which patients that service is allowed to query. This broad access makes provider organizations anxious about rolling out and supporting these integrations. Even if a site manages to configure custom, tailored rules locally, those configurations do not scale across multiple health systems. Without a scalable way to prove authorization for specific patients, backend services cannot deliver broad value, and a public health investigator following up on a tuberculosis case report is left relying on phone calls and faxes instead of a targeted API query.

### What are we actually proposing?

We are proposing a mechanism for portable, verifiable authorization.

The idea is to build directly on the existing SMART ecosystem rather than inventing new endpoints. Conceptually, a Permission Ticket could be a cryptographically signed JSON Web Token (JWT) that rides along with standard SMART Backend Services client assertions. The Argonaut community will explore these technical tradeoffs and develop the actual specification together as we go.

### How the information flows

Here are two examples of how this could work in practice.

For individual access:

1. A patient uses an identity service to verify their identity and authorize an app to fetch their clinical data, choosing what will be shared (e.g., data type, geographic sources, or date ranges).
2. The identity service mints a signed Permission Ticket.
3. The app presents this ticket to the SMART token endpoints at multiple hospitals.
4. The hospitals validate the ticket signature and issue standard access tokens. The patient completes one authorization flow instead of five.

For a business use case like public health follow-up:

1. A hospital files an electronic case report for a reportable condition.
2. The hospital generates a Permission Ticket scoped to that specific case and patient.
3. The public health agency receives the case report and the accompanying ticket.
4. When the agency needs follow-up data later, they present the ticket back to the hospital's standard API to securely access the scoped records.

A little bit more formally, an incoming Permission Ticket payload might look something like this:

### How to participate

Our immediate goals for the project are building the community, scoping out the work, exploring technical tradeoffs, and hearing from a diverse group of stakeholders. We will be working on the specification as a community as we go.

To help us gather concrete feedback right now, we set up a semi-structured, AI-guided interview. If this project is relevant to your interests, please take a few minutes to participate here: <https://argonaut.exe.xyz/>

The interview will ask you questions based on your specific background and help us understand your use cases and constraints as we start to build this out.