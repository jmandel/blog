---
title: "Authorization as a Network Scaling Problem"
date: 2025-11-19T17:35:00
slug: authorization-as-a-network-scaling-problem
original_url: "https://www.linkedin.com/pulse/authorization-network-scaling-problem-josh-mandel-md-aczuc"
linkedin_id: aczuc
banner: ./banner.png
---

When we designed the SMART Backend Services specification, we deliberately left flexibility for implementers to handle authorization logic below the OAuth layer. There were good reasons for this - we needed to get the standard through, we needed to accommodate different deployment models, and frankly we didn't have consensus on how to standardize the authorization semantics themselves. As lead editor for the SMART App Launch and Backend Services specs, I helped [provide](https://build.fhir.org/ig/HL7/smart-app-launch/scopes-and-launch-context.html#:~:text=Neither%20SMART%20on%20FHIR%20nor%20the%20FHIR%20Core%20specification%20provide%20a%20way%20to%20model%20the%20%E2%80%9Cunderlying%E2%80%9D%20permissions%20at%20play%20here) that [flexibility](https://build.fhir.org/ig/HL7/smart-app-launch/backend-services.html#:~:text=The%20client%20then%20includes%20a%20set%20of%20scopes%20in%20the%20access%20token%20request%2C%20which%20causes%20the%20server%20to%20apply%20additional%20access%20restrictions%20following%20the%20SMART%20Scopes%20syntax) intentionally.

But here's what I'm worried about now: that flexibility has become the *main* way - really the *only* way - we're expressing complex authorization policies in practice. And because all these authorization details are tied to individual client registrations at individual sites, it fundamentally prevents clients from scaling across networks.

**You can't have a client that operates across hundreds of data sources when each source requires custom configuration to express who that client can access and under what conditions.**

The standards themselves aren't up to the job of supporting scalable, multi-party exchange ecosystems. I think we might be systematically sweeping the hard authorization problems under the rug, and it's preventing us from building the networks we actually need.

### What We Actually Built

In SMART Backend Services, clients are "pre-authorized" through out-of-band processes. The spec says this explicitly: by the time a client requests an access token, "the server has already associated the client with the authority to access certain data." There are scopes in the request, but the real authorization decisions - who can access what data, under what conditions, for what purposes - happen in system-specific configurations entirely below the OAuth layer.

This works fine for point-to-point integrations. If you're one insurance company negotiating with one health system, you can work out the configuration details. Someone logs into the EHR admin screen, sets up rules that say "client ID XYZ representing Acme Insurance can access data for patients where Acme is listed as primary payer," and you're done.

But here's what this means in practice:

1. The actual authorization semantics are opaque. There's no standardized way to express "this payer can access data for members enrolled in their plans" or "this public health agency has permission to query based on this specific reportable condition" or "this community organization has time-limited access due to this specific referral." That knowledge lives in vendor-specific configuration screens, not in anything that travels with the request.
2. Every backend service client has to negotiate custom configurations with every data source. Knowledge about authorization rules can't flow through the network - it has to be pre-negotiated and pre-configured everywhere.
3. Because there's no contextual information in the request itself, you're forced into binary trust decisions: either you trust this client completely for all relevant data, or you don't trust them at all. There's no real middle ground.

### Where This Breaks Down

Look at what's happening with TEFCA. For the treatment exchange purpose (the best-working exchange purpose today by a wide margin), requesting parties essentially assert "I have a treatment relationship with this patient," and every respondent node is expected to trust that assertion and return data. This blanket trust model makes many participants uncomfortable, but we don't have a standardized way to express more bounded authorization contexts.

Other TEFCA purposes aren't working at all. Payment exchange has devolved into bilateral negotiations about costs because there's no standard way to represent payment-related authorization contexts. Public health agencies can't get the data they need because providers don't want to give them blanket access to everything, but we have no mechanism for scoped, contextual authorization based on specific reportable conditions or investigations.

This is exactly what happens when authorization semantics can't travel with requests.

### The Pattern

When authorization logic lives in system-specific configurations rather than in portable, standardized formats, we consistently see:

**Authorization becomes opaque.** Receiving systems can't understand why access should be granted by examining the request. The request just says "I'm client XYZ with these scopes." All the context lives elsewhere.

**Authorization becomes non-portable.** Each integration requires custom configuration at each site. Authorization rules can't flow through networks.

**Authorization becomes trust-maximizing.** Without contextual information, you either trust completely or not at all. No middle ground for "yes, but only for these patients, under these circumstances, for this time period."

**Authorization potentially becomes a competitive moat.** When authorization logic is locked in proprietary configurations, it creates switching costs and vendor lock-in.

### What Could Help

Backend Services with pre-configured authorization is barely "good enough" for bilateral integrations. I don't think it scales to network-level exchange. Every day we're building out new data exchange infrastructure without solving deeply enough for the authorization semantics.

There are alternative models worth exploring. I've written elsewhere about [Patient Trust Authorities](https://docs.google.com/document/d/10oVOyIO7JLesQ6sScWCCZPM4bGyUqsNzGc51FhBaORc) as a way to create portable credentials that carry authorization context - where the act of identity verification, consent collection, or clinical relationship establishment creates tokens that can be presented across the network. The key insight is that authorization context should travel with requests rather than being pre-configured at every endpoint.

Consider these scenarios:

* **Public Health Loopback:** A hospital reports a reportable condition (e.g., measles) to the public health agency. The report includes a permission artifact tied specifically to that case ID. When the agency queries for follow-up data they present this artifact. The authorization is strictly scoped to the investigation context, allowing the hospital to automate the response without opening their entire patient database to broad queries.
* **Social Care Referral:** A primary care provider refers a patient to a local food bank. The referral generates a "bearer" artifact that grants the Community Based Organization (CBO) the ability to read that specific ServiceRequest and write a status update. The CBO doesn't need a BAA, a user account in the EHR, or a complex client registration; the referral *is* the credential, enabling transient, task-specific access for a non-clinical actor.
* **Claims-Based Access:** Instead of a payer simply asserting "I cover John Doe" (which requires the provider to blindly trust the payer not to fish for data), authorization is tied to a specific financial transaction.
* **Portable Caregiver Access:** An adult daughter is the verified designated representative for her elderly mother. Instead of logging into five different patient portals with five different usernames to manage her mother's care, she authenticates once with a "Trust Broker" (e.g., a state ID wallet or HIE). She receives a delegation artifact that she can present to any hospital in the network. The hospitals respect the artifact and grant access to the daughter, without her needing a local user account at every site.
* **Longitudinal Research:** A patient enrolls in a five-year cardiac device study via a research app, signing a digital consent form. This generates a long-lived permission artifact. As the patient visits different health systems over the next few years, the research app presents this artifact to retrieve relevant cardiac data. The patient doesn't need to manually re-authorize the app at every new hospital; the signed, portable consent travels with the request and persists over time.

I'm not certain what the right answer is, but I think we need to be honest about whether the current approach is actually the foundation we want for ecosystem-scale exchange. The rug is getting pretty lumpy.

I'll have more to say about solving for these scenarios in a future post.