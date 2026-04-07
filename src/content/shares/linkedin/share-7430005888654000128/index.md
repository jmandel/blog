---
title: "Blooper reel time! I foolishly decided to record a live, totally untested demo…"
date: 2026-02-18T21:50:47
slug: share-7430005888654000128
share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7430005888654000128"
share_type: "ugcPost"
share_id: "7430005888654000128"
visibility: "MEMBER_NETWORK"
---

Blooper reel time! I foolishly decided to record a live, totally untested demo of my new "Request My EHI Export" Skill. I mean, why not...

I’ve been deep in the weeds grading EHI export documentation, but documentation is only half the battle. Actually getting the data is the hard part. Even though my provider (Mass General Brigham) uses Epic -- which my pipeline graded as an "A" for technical export capability -- there’s no "Download EHI" button in the portal. You still have to find a specific PDF form, fill it out, sign it, and fax it to a specific number, together with an explanation of what EHI Export is and how the provider can satisfy your request (and ... from personal experience I know this part is challenging).

So I built a custom Skill to let an AI agent handle the bureaucracy (will share more soon on that ). I recorded a live run with the new Claude Sonnet  4.6. It was pretty fascinating watching the agent stitch together a complete workflow across disparate systems without hard-coded logic for this specific provider:

* Identification: The agent correctly identified that MGB uses Epic.

* Context: It queried my own grading database to verify that a high-quality EHI export is technically possible for this vendor.

* Retrieval: It crawled the web to find MGB’s specific "Authorization for Release" PDF and their medical records fax number.

* Action: It interviewed me for demographics, filled out the PDF, and generated a secure link so I could draw my signature on my phone.

Then, the demo went a bit off the rails.

When the agent merged my signature into the PDF, the image rendered invisibly. While I was explaining the visual bug to the model, it decided to go ahead and send the fax before I had verified the fix.

Oh well. To follow up, I told Claude the signature was missing. It spun up a Python environment, wrote a script to analyze the PDF structure, and realized the skill-supplied code was calculating coordinates relative to "Page 0" metadata instead of the actual target page dimensions. It also detected an alpha channel issue with the signature image.

It wrote a fix, patched the PDF, correctly placed the signature, and re-sent the fax... all within the chat session.

I’ve since updated the Skill to prevent the "premature faxing." It now requires explicit user confirmation before interacting with the fax API, handles multi-page coordinate mapping much better, and aggressively cleans up signature session data.

If you want to see an agent navigate a health system's bureaucracy (and debug its own Python scripts in real-time) the video is below.
"The code is open source and available for anyone who wants to try requesting their own records.
