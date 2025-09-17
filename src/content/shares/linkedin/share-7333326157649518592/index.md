---
title: "We Can Parse Terabytes, But We Still Can’t Find the FHIR Server"
date: 2025-05-28T03:00:03
slug: share-7333326157649518592
share_url: "https://www.linkedin.com/feed/update/urn:li:share:7333326157649518592"
share_type: "share"
share_id: "7333326157649518592"
visibility: "MEMBER_NETWORK"
---

We Can Parse Terabytes, But We Still Can’t Find the FHIR Server

More Fun with the CMS/ASTP/ONC RFI!

Today's Policy: Establish Public Foundational Infrastructure for Nationwide Discovery

Voice: Platform Engineer, Patient-Centric Resarch Platform

---

We build national-scale patient-facing research platforms—apps that let people connect their clinical records from all over the country, for studies, longitudinal care, or patient-directed research. Technically, the hardest parts should be normalization, identity, and consent. But what drags us down the most is this: just figuring out where and how to connect.

In a closed research consortium with 20 health systems, you can swap emails, get the endpoint, and move on. But the minute you try to build a general-purpose app where any patient anywhere can connect to their provider’s FHIR API, you hit a wall. There is no master directory. 

CMS “publicly shames” over 3.5 million NPIs that never entered any digital contact—no Direct address, no FHIR API. Even among those who do, details are scattered: some publish a base URL in a spreadsheet on a web page; others list it in product documentation that’s out of date before your crawler finishes. ONC’s Lantern project tries to tie it all together by scraping, pinging, and inferring, but it’s still a patchwork—different list formats, missing organization identifiers, and CapabilityStatements that often fail to reliably tell you who runs what.

So, even with the best code in the world, national patient apps end up maintaining their own lookup tables—one for each EHR’s quirks, one for each auth flavor, one for which endpoints are actually live versus which are just a firewall rule. Every new site or EHR update risks breaking discovery, and every “connect your health data” button can lead to a dead end or a confusing support ticket.

And now, as TEFCA QHINs come online, we see a new round of proprietary directories—endpoint lists and network maps visible only to approved participants or credentialed members. Instead of closing gaps, these private registries just duplicate effort and further fragment discovery. The people who need open, nationwide access—patients, researchers, innovators—remain on the outside, still guessing where the front door is.

"This isn’t just a nuisance. It shapes who can participate in research, who can manage their care, and which apps can even be built at all. If there were a single, accurate, public, machine-readable directory—listing every certified FHIR endpoint, with details like version, auth, TEFCA status, and uptime, all tied to actual organizations and kept current as a condition of certification—this layer of friction would disappear. Small teams and big players would be on a level field. App onboarding would be reliable. More patients could connect more data, to more uses, more safely.
