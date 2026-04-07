---
title: "Thanks to some help from an OpenAI employee who saw my tweets, I finally got…"
date: 2026-01-13T19:59:21
slug: share-7416931883252469760
share_url: "https://www.linkedin.com/feed/update/urn:li:share:7416931883252469760"
share_type: "share"
share_id: "7416931883252469760"
visibility: "MEMBER_NETWORK"
shared_url: "https://youtu.be/C1Btp2CLfHo"
---

[Shared link](https://youtu.be/C1Btp2CLfHo)

Thanks to some help from an OpenAI employee who saw my tweets, I finally got off the waitlist for ChatGPT Health. I spent the morning putting it through its paces with my real medical records and comparing with my experience using Anthropic's health integration (see https://lnkd.in/gscte2MA) as well as my own "Health Skillz" approach (https://lnkd.in/gZqpuCyE)

OpenAI's onboarding experience is notably different from the Anthropic connector. Anthropic uses HealthEx and OpenAI uses b.well for EHR connectivity. While both are building deeply for a TEFCA future,  OpenAI's b.well configuration forgoes TEFCA for now. 

This means no upfront identity proofing tax and no waiting for a Record Locator Service (RLS) that fails to find records. Instead, it uses a direct SMART on FHIR flow structurally similar to the open source Health Skillz implementation I built. This is a good thing; avoiding the current TEFCA user experience (which seems quite broken in other implementations, at least for me; YMMV) makes the initial connection much smoother.

The integration forces interactions into chat widgets within the ChatGPT canvas, which I understand is an area of deep product investment for OpenAI and a big bet, but for me it's an awkward blend of chat + app functionality. No big deal though. My real concern is that...

**Once the data are connected, the model struggles to leverage its tools to access and analyze effectively.**

It seems confused by a large array of granular tools, none of which in my experience was able to provide raw access to FHIR data or access to clinical notes, despite the tool descriptions. In my testing, the model was unable to read the content of any of my clinical notes.

The impact on reasoning was clear. When I asked for a high-level overview of my concussion history, the model failed to synthesize an appropriate answer. Instead of generating a comprehensive clinical timeline, it stuck to a very low-level, procedural response, essentially telling me, "I called these tools and here is what the tools told me."

It is also unclear what model is actually running here. Is it GPT-5.2?  Something modified/customized (nerfed?) for health, or misguided by a conservative system prompt? What level of thinking effort? There is no transparency about (or control over) the model or underlying data retrieved, which makes debugging these poor answers frustrating. (Of course you can observe tool calls and responses, but without seeing the underlying data it's hard to pinpoint whether problems are upstream of the tool calls or within the tool implementations.)

In the video below, you can see the contrast between ChatGPT’s struggle to synthesize a summary and the rich, accurate analysis my Health Skillz tool generated using the exact same data source via Claude. 

"Full walkthrough: https://lnkd.in/grfUzVra
