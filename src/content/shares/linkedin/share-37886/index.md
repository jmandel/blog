---
title: "Argonaut's 2024 \"FHIR Write\" initiative launches today, focused on continuous…"
date: 2024-05-01T17:00:27
slug: share-37886
share_url: "https://www.linkedin.com/feed/update/urn:li:groupPost:37886-7191481611073298433"
share_type: "groupPost"
share_id: "37886"
visibility: "MEMBER_NETWORK"
---

Argonaut's 2024 "FHIR Write" initiative launches today, focused on continuous glucose monitoring! We're streamlining standards-based integration of CGM data into EHRs to support collaborative diabetes management.

Huge thanks to Redox, Rimidi, Rhapsody, Sensotrend, and Tidepool for helping me and Brett Marquard come up to speed ahead of the project launch.

I also want to share my personal pre-launch exploration to learn about CGM:

1. Got a CGM prescription and began tracking my blood sugar.
2. Mapped my CGM readings to FHIR Observation and Device resources.
3. Calculated key metrics like "time in range" as FHIR Observations
4. Created a visualization PDF based on the Ambulatory Glucose Profile, and wrapped this in a FHIR DiagnosticReport
5. Published same visualization as an interactive web view
6. Packaged all this up in a SMART Health Link for secure, structured data sharing + built-in visualization

This SMART Health Link represents my past 120 days of glucose history, updated automatically and covering all core data elements described in the Diabetes Technology Society (DTS)'s iCoDE data set:

** Josh's glucose SHLink: https://lnkd.in/g2TQb5tN **

Anyone with this SHLink can access the structured FHIR resources behind the visualization. In fact, the viewer itself is a SHLink client that knows how to render the data it finds. For a behind-the-scenes tour of the data set, see https://lnkd.in/gYpGuGEQ

This proof of concept shows how FHIR can streamline CGM data flows. It can give clinicians structured data for analysis AND summary reports for record-keeping.

I should note that this consumer-mediated direction is not necessarily the approach we'll focus on in this year's Argonaut project -- but it has been a great learning exercise for me. Check out the project and code: https://lnkd.in/gY2nwv2h

#healthcare #diabetes #data #FHIR #ArgonautProject

"A final thought: Even with an "all green" glucose report, there's still much to learn from analyzing specific responses like post-meal glucose spikes. Right now, such subtle signals may be outside the standard clinical focus, but it highlights the wealth of potential insights hidden within raw data.
