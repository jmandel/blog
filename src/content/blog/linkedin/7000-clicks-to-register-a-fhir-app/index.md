---
title: "7,000+ Clicks to Register a FHIR App"
date: 2026-02-11T19:59:00
slug: 7000-clicks-to-register-a-fhir-app
original_url: "https://www.linkedin.com/pulse/7000-clicks-register-fhir-app-josh-mandel-md-ta7ic"
linkedin_id: ta7ic
banner: ./banner.jpg
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7427443439530811392"
  share_id: "7427443439530811392"
  share_type: "ugcPost"
  posted_at: "2026-02-11T20:08:31"
  visibility: "MEMBER_NETWORK"
  commentary: |
    I built a script to save myself 7,000 clicks on Epic's developer portal. Read on for a deep dive into patient access, app registration, data sets (including USCDI flavors), SMART User Access Brand Bundles, and more.
---

**TL;DR:** I built [Health Skillz](https://github.com/jmandel/health-skillz) to help patients connect their health records to an AI assistant. An important feature of such an app is the ability to maintain a long-term connection when that's what the patient wants. Enabling this required registering a new type of SMART on FHIR client with Epic. Epic deserves credit for having a system that distributes patient-facing apps to hundreds of health systems automatically. (Not every EHR vendor offers anything like this.) But the developer experience around that system is rough. Activating my app required confirming the exact same credential, one organization at a time, through a 7-click modal workflow — over 3,500 clicks for a single registration, and over 7,000 to reach all available organizations. I had Claude Code inspect the network traffic to understand the underlying API calls. Along the way I uncovered deeper issues with the registration model.

> **Update (Feb 12, 2026):** Based on feedback from an Epic representative, I've amended several sections below regarding US health systems that appeared on the management page but not in the Brands bundle. These organizations are in the process of going live on Epic and aren't live yet — they appear on the management page so developers can activate and test pre-go-live, and endpoints will be published at launch. Most are currently live on another EHR and do publish FHIR endpoints through that system. Updated sections are marked with **[Edited Feb 12]**. The developer experience issues — no way to distinguish live from pre-go-live orgs on the management page, and the 7-click-per-org activation workflow — remain as described.

---

### What Epic Gets Right

Before diving into the problems, the baseline matters.

Epic has an [Automatic Client Record Distribution](https://fhir.epic.com/Documentation?docId=patientfacingfhirapps) system that pushes client IDs for qualifying USCDI apps to all eligible community members. When a developer registers a patient-facing, read-only FHIR app using only USCDI APIs and marks it production-ready, the app's client record automatically appears at every participating organization. No action needed from each organization's IT staff. No site-by-site negotiations.

This is important. Not every EHR vendor offers a centralized distribution model like this. Many still require developers to negotiate access at each health system separately — a process that can take months per site, often involves legal review, and effectively limits FHIR app development to companies with business development teams. Epic's auto-sync means a solo developer like me can register an app and have it reach hundreds of health systems. That's the right vision.

*But auto-sync for apps with long-term access is full of friction.*

### Two Lanes of Auto-Sync

Epic's [documentation](https://fhir.epic.com/Documentation?docId=patientfacingfhirapps) describes two conditions for automatic distribution. The key distinction:

> Does not use refresh tokens **OR** uses refresh tokens and has a client credential uploaded by the vendor for that community member

**Lane 1 (no refresh tokens):** The app's client ID syncs to all community members fully automatically. Zero developer action per org. True "set it and forget it."

**Lane 2 (uses refresh tokens):** The client ID is *queued* at each community member, but auto-sync doesn't complete until the developer "uploads a client credential" for that specific community member. In practice, "uploads a client credential" means going to Epic's "Review & Manage Downloads" page and clicking through a per-org modal workflow to assign the app's JWK Set URL to that community member's non-production and production environments, then confirming.

Here's the thing: **the credential being "uploaded" is the same JWK Set URL every time.** There's nothing org-specific about it. The app already has a JWK Set URL configured at the app level. The portal simply requires you to confirm it individually, per org, through a 7-click sequence.

[Health Skillz](https://github.com/jmandel/health-skillz) started in Lane 1 as a public SMART on FHIR client — fully automatic distribution, no per-org work. But Health Skillz users were telling me they didn't want to have to sign into their patient portal over and over again just to keep their health records current in their AI assistant. They wanted to connect once and have their data stay up to date. That means refresh tokens — and Epic doesn't issue refresh tokens to public clients. You need a **confidential client** with JWT-based authentication. But registering one moved me from Lane 1 to Lane 2, and Lane 2's developer experience has some serious problems.

### The Problem: 500 Organizations × 7 Clicks

After registering the confidential client, auto-sync did its job: ~500 organizations appeared on my "Review & Manage Downloads" page, each with a queued client ID request waiting for me to confirm my app-level JWK Set URL.

The per-organization confirmation workflow:

1. Click **"Activate for Non-Production"**
2. Select **"JWK Set URL (Recommended)"** radio button in the modal dialog
3. Click **Submit**
4. Click **"Activate for Production"** (now unlocked)
5. Select **"JWK Set URL (Recommended)"** radio button in a second modal
6. Click **Submit**
7. Click **"Confirm"** in a production confirmation dialog

Seven clicks per org. The same credential every time. No "Activate All" button. No bulk checkboxes. No API. The orgs are paginated 20 per page across 25 pages, adding 24 more navigation clicks.

**498 remaining orgs × 7 clicks + 24 page navigations = 3,510 clicks.** And that's just for one USCDIv3 registration — as I'd later discover, maximizing patient access requires a second registration with its own set of organizations and its own round of activation (more on this below).

At 5–10 seconds per click (accounting for modal load times, API roudtrips, and transitions), that's **5–10 hours of manual work** — repetitive, error-prone, and entirely unnecessary given that the same outcome can be achieved with two API calls per org (as I'd discover shortly).

I'm not the first developer to encounter this. This is a known pain point — other FHIR app developers have been raising it for years, and Epic has been slow to prioritize changes that only impact app developers.

### Building an Automation Script with Claude

Instead of clicking through 3,510 modal dialogs, I had Claude Code with Chrome access navigate the portal and build a reusable automation script. The goal was to understand the portal well enough to automate activation reliably — and that turned out to require a significant level of automation that I'm not sure I could have accomplished by hand in under a day. (Which means the manual clicking might actually have been faster, if you only had to do this once. But I wanted a repeatable solution.)

The [full technical journal](https://github.com/jmandel/health-skillz/blob/main/blog/epic/2026-02-11-epic-activation-journal.md) is in the repo, but here's the arc.

### Trying to Work with the UI

Claude first tried the direct approach: interacting with page elements and the JavaScript framework powering the management console. It attempted to programmatically click buttons, select radio options in modal dialogs, and navigate between pages to enumerate all 500 organizations.

This mostly didn't work. The frontend framework's data bindings behaved unpredictably when manipulated from outside — pagination controls updated their display text without actually fetching new data, page-size settings couldn't be changed reactively, and modal state got out of sync with the underlying data model. After multiple failed approaches to coerce the UI into cooperating, Claude shifted strategy.

### Observing Network Requests Instead

Rather than fighting the UI, Claude installed an XHR interceptor to observe what the browser actually sends to the server during a manual activation. This revealed that the entire 7-click workflow resolves to **two simple API calls** to a single endpoint:

Response: {"Success":true}

No modals, no radio buttons, no confirmation dialogs. The server just needs an OrgId, an AppId, and which environment to activate.

Similarly, the paginated org list could be fetched in one call to POST /Developer/LoadDownloads with a PageSize parameter — though finding the right parameter name required brute-force testing, since PageSize (capital S) works but pageSize (lowercase) is silently ignored, and none of this is documented.

Even after finding the right APIs, Claude hit additional snags: the org identifier needed for activation calls wasn't directly present in the list API's response (it had to be parsed out of a composite ID field), and misleading error messages obscured the real problem. The [journal](https://github.com/jmandel/health-skillz/blob/main/blog/epic/2026-02-11-epic-activation-journal.md) has the full debugging narrative.

### The Result

The [final automation script](https://github.com/jmandel/health-skillz/blob/main/blog/epic/epic-activate-all.js) is straightforward: fetch all orgs, filter to those needing activation, make two API calls per org with a short delay between them

The script activated 496 of 500 organizations. The remaining four (all newer orgs with high internal IDs) returned a server-side error — "Failed to register client for download." — for both the script *and* the manual UI workflow. Clicking through the 7-step modal for these orgs produces the same error the API dwoes. These organizations' Epic environments appear to not be fully provisioned to accept client registrations yet — another rough edge that affects manual and automated approaches equally.

### Correlating Organizations Across Epic's Systems

Any developer managing a FHIR app across Epic's network will eventually need to answer: *which FHIR endpoint URL corresponds to which organization on my management page?* Epic publishes a [Brands bundle](https://open.epic.com/Endpoints/Brands) containing both Organization resources (90,066 sub-orgs grouped under parent brands) and Endpoint resources (575 FHIR base URLs). The management page shows an "Organization Id" for each org.

Connecting these turns out to be possible but structurally surprising. The management page OrgId (e.g., 1696 for Access Community Health Network) appears in the Brands bundle — but on **Endpoint** resources, not Organization resources. Specifically, it's a logical reference in Endpoint.managingOrganization.identifier:

If you search Organization.identifier — the natural place to look for an organization's ID — you'll find nothing. Zero of the 90,066 Organization resources carry this identifier. You have to know to look in the Endpoint. It took Claude's careful exploration to surface this, and even then it required multiple passes and some feedback from an expert to get it right. The [full technical journal](https://github.com/jmandel/health-skillz/blob/main/blog/epic/2026-02-11-epic-activation-journal.md) traces the debugging path.

Comparing the 500 management page OrgIds against the 444 unique OrgIds on Brands Endpoint resources: 440 overlap, 60 appeared only on the management side, and 4 appeared only on the Brands side.

The 60 management-only organizations are all queued for auto-sync — but that doesn't mean they're all live. **[Edited Feb 12:]** An Epic representative shared that many of the US health systems in this group are in the process of going live on Epic but aren't live yet. Epic lists them in the management console so developers can activate and test pre-go-live; endpoints will be published when they launch. This means the Brands bundle isn't missing these orgs so much as the management page doesn't distinguish live orgs from pre-go-live ones — a gap that affects developer understanding of what they're actually activating.

The Brands bundle is a regulatory obligation: certified EHR products are required to publish it so that patients and apps can discover which providers are available. But the requirement applies in the context of US certification, which is why the 7 international organizations (Children's Health Ireland, NSW Health, Santé Québec, etc.) may reasonably be absent. For the remaining 53, the Brands bundle is simply incomplete relative to the auto-sync pool — these organizations are live on USCDI v3 but haven't made it into the public directory.

The categories help illustrate the scope of the gap:

* **17 payers** (Humana, Elevance, Blue Shield of California, etc.) — these are payers with clinical FHIR APIs that patients cannot discover through the public directory
* **5 diagnostics/genomics labs** (Guardant, Tempus, Myriad, etc.)
* **7 international organizations** (Children's Health Ireland, NSW Health, Santé Québec, etc.) — these may not be expected to publish in the US-focused Brands bundle
* ~31 US health systems — **[Edited Feb 12:]** many of which, per an Epic representative, are pre-go-live on Epic and not yet serving patients through Epic's FHIR APIs. Several of these organizations are currently live on another EHR and do publish FHIR endpoints through that system.

**[Edited Feb 12:]** Setting aside the 7 international organizations, the remaining 53 fall into two groups: pre-go-live health systems that don't yet have live Epic FHIR endpoints (and aren't expected to appear in the Brands bundle until launch), and payers and labs that may have live APIs but aren't discoverable through Epic's public directory. The developer-facing issue remains: the management page doesn't indicate which is which.

**[Edited Feb 12:]** The management page mixes live and pre-go-live organizations with no way to tell them apart.

### Registration Segmentation

There's one more structural issue worth calling out, because it compounds everything above.

When you register a FHIR app on Epic's portal, you have to choose one of three data categories:

* **USCDI v1** — the original US Core Data for Interoperability set
* **USCDI v3** — the expanded set (a superset of v1's data, though supported by fewer orgs)
* **CMS Payer APIs** — claims data, Explanation of Benefits, formulary information

Your app can only connect to organizations offering that specific data category. **You cannot register a single app that accesses all three.** If you want your app to pull both clinical records (USCDI) and claims data (CMS Payer), you need to register two separate apps, each with its own client ID, its own credentials, and — if you're using refresh tokens — its own round of per-org activation across potentially hundreds of organizations.

It gets worse. You might assume that USCDI v3, being a superset of v1's data, would give you access to a superset of v1's organizations. **It doesn't.** A USCDIv3 app reaches ~500 organizations. A USCDIv1 app reaches a larger number. The difference includes providers that haven't yet upgraded to the Epic version supporting USCDIv3, as well as diagnostic labs and payers.

The practical consequence: if you want to maximize patient access to clinical data alone, you need to register *two apps* — one for USCDIv3 (to get the broadest data set where available) and one for USCDIv1 (to reach the organizations that USCDIv3 misses). Add a third if you want CMS Payer data. Each registration means a separate client ID, separate credentials, and — for apps with offline access — a separate round of per-org activation. For Health Skillz, that would mean over 1,000 organizations across two registrations, each requiring the same 7-click workflow. Over 7,000 clicks to fully activate, before a single patient connects.

For a developer building backend infrastructure, this is painful but workable. For a consumer-facing app, it borders on incoherent. A patient connecting to their health data doesn't think in terms of regulatory data categories or USCDI version numbers. They want to connect to "Kaiser" or "Blue Cross" and see everything those organizations have about them. But under Epic's registration model, the patient would literally have to connect what looks like the same app to what looks like the same provider multiple times — once for each data category — just to cover all available data. There's no way to explain this to a user that doesn't sound like a bug.

This also explains part of the discoverability gap noted above: the 17 payers on the management page (Humana, Elevance, Blue Shield of California, etc.) are offering USCDI v3 APIs, but a developer building a payer-focused experience would also need a separate CMS Payer API registration to access claims data from these same organizations.

### Lifecycle Mystery

There's a related question I can't fully answer: **what happens when Epic organizations come online — or leave — after you register an app?**

Some of my older app registrations show a larger number of community members than an app I just registered now. It's confusing, and the portal doesn't surface enough information to understand why the numbers differ or what they mean.

For a system whose entire value proposition is "register once, reach everyone," the ambiguity about how the organization list evolves over time is a significant gap.

### What Epic Could Do

* **Make automatic distribution work for all patient-facing apps, including those with offline access.** When an app already has a JWK Set URL configured at the app level, there's no reason to require the developer to confirm that same credential individually at every organization. Apps with offline access (refresh tokens) should be distributed the same way apps without them are: automatically, with no per-org manual steps. If Epic still wants to retain per-org confirmation for some reason, at minimum provide an "Activate All" button or a proper management API so developers aren't clicking through hundreds of modal dialogs
* **Keep the organization list current in both directions.** It should be clear when new organizations come online and can be connected to — without the developer having to take extra steps or re-register the app. It should also be clear when organizations leave the pool because they're no longer offering APIs through Epic. Today, older registrations show different community member counts than newer ones, with no way to distinguish active from stale entries. For a system whose value proposition is "register once, reach everyone," this ambiguity is a significant gap
* **[Added Feb 12:] Indicate go-live status on the management page**. The "Review & Manage Downloads" page shows all organizations queued for auto-sync — including those that are pre-go-live and not yet serving patients — with no way to distinguish them from organizations with live FHIR endpoints. Even a rough live/not-yet-live indicator would help developers understand what they're activating. The complexity is real (some orgs may be live on billing modules but not clinical), but the current state — where a developer can activate hundreds of organizations without knowing which ones will actually accept patient connections — creates unnecessary confusion.
* **Stop limiting automatic distribution to apps that only request the regulatory floor of data.** Epic exposes a broad set of FHIR APIs, but automatic distribution is restricted to apps that limit themselves to USCDI. As long as a patient-facing app is requesting data that patients themselves approve, it should be eligible for automatic distribution regardless of which FHIR resources it uses. The current restriction means a patient who wants to use an app that accesses *more* of their own data effectively can't — there is no realistic pathway for a patient to get their provider's IT department to manually approve a FHIR client ID. Most provider organizations wouldn't understand the request, wouldn't know how to evaluate it, and wouldn't take the steps
* **Stop requiring separate registrations for different data categories.** Today, a developer must choose between USCDI v1, USCDI v3, and CMS Payer APIs at registration time, and can only connect to organizations offering that specific category. A patient connecting to "Kaiser" or "Blue Cross" doesn't think in terms of regulatory data categories — they want to see everything that organization has about them. As long as these artificial distinctions are maintained, patients will not be able to connect to all of their data through a single app. That is a shame
* **Include logo and branding information in the Brands bundle.** The SMART [User Access Brands](https://hl7.org/fhir/smart-app-launch/brands.html) specification was explicitly designed to help patients find the right provider organization from a large directory, and it anticipates that organizations will publish branding details like logos and descriptions so patients can recognize them. Epic's Brands bundle doesn't include this information. In early Health Skillz user testing, a patient searching for "Stanford" was confronted with multiple organizations with similar names and no easy way to tell them apart. Logos and branding would solve this immediately — it's the kind of information that providers already have and that the specification was built to carry

### The Bigger Picture

Epic built something genuinely valuable with automatic client record distribution. The model of "register once, reach hundreds of sites" is what ASTP's certification rules anticipated — patient-facing apps shouldn't end up in a black hole where individual providers are expected to find and approve them before a patient can use an app of their choice. Other EHR vendors would do well to ensure their own app registration paths don't create exactly that bottleneck.

But the gap between the architectural vision and the developer experience is stark. Apps with offline access require thousands of manual clicks to confirm the same credential at every organization — a task that could be eliminated entirely by treating them the same as any other patient-facing app. Cross-referencing organizations between the management page and public endpoint directories requires knowing to look at a non-obvious FHIR path on a different resource type than you'd expect. Consumer-facing apps that want to access more than the regulatory minimum of patient data can't use automatic distribution at all, and apps that want to access *all* of a patient's data must register separately for each data category. It's not even clear whether the organization list stays current over time.

These are the kinds of problems that accumulate when infrastructure is built for regulatory compliance and then left alone. Auto-sync exists because ONC's information blocking rules require that patients can access their data through third-party apps. Epic built the infrastructure to make that possible, and it's genuinely good infrastructure. The developer-facing tooling around it — the parts that only app builders see and use — hasn't received the same attention, because it isn't what regulators evaluate. Developers have been raising these issues for years. The fixes aren't hard. They just have to matter to someone.

---

### Appendix: Tools and Methods

This exploration was conducted using:

* **Claude Code with Chrome access** — for navigating the portal, inspecting page behavior, intercepting network requests, and building the automation script through an iterative agent interaction loop.
* **Claude Code (CLI)** — for data analysis, cross-referencing the endpoint bundles, and preparing the technical journal

All artifacts are in the [Health Skillz repo](https://github.com/jmandel/health-skillz/tree/main/blog/epic):

* 2026-02-11-epic-activation-journal.md — Full technical journal
* epic-activate-all.js — Automation script

The entire process — from opening the management page to completing all activations — took approximately 90 minutes. The script itself runs unattended in about 10 minutes.

---

*Health Skillz is open source and not affiliated with Epic, Anthropic, OpenAI, or any healthcare provider. I work at Microsoft but this is a personal project.*