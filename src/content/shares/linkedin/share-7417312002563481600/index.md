---
title: "Thanks to Anand Raghavan for helping me debug my HealthEx :: Claude connection!…"
date: 2026-01-14T21:09:48
slug: share-7417312002563481600
share_url: "https://www.linkedin.com/feed/update/urn:li:share:7417312002563481600"
share_type: "share"
share_id: "7417312002563481600"
visibility: "MEMBER_NETWORK"
---

Thanks to Anand Raghavan for helping me debug my HealthEx :: Claude connection! With a little bit of help from the Clear tech team to boot, we managed to reset things. This required nuking my implicit Clear account and allowing HealthEx to recreate one by reinitiating the flow using my national carrier cell phone number (which I almost never use) instead of my Google voice number (which Is my daily driver and the number that I register with healthcare providers).

Well after that, the TEFCA RLS process ran and found two matches (out of 3-4 I expected) and I was able to use my existing portal accounts to connect to those plus another (just as I did the first time around).

And after that, Claude actually had access to my information (unlike the first time around, where even though the information landed in HealthEx, it was unable to flow into Claude). I am pleased to say that the tools exposed allowed Claude to read key metadata from fhir resources and access note content (although I still think there is a lot of power to letting Claude write programs that operate over full json content, which I don't think is possible for the current connector).

"Anand give me great insight into the underlying steps and checks and error reporting system and was super gracious answering my questions.
