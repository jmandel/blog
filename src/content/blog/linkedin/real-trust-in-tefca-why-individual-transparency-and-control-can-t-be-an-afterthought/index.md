---
title: "Real Trust in TEFCA: Why Individual Transparency and Control Can't Be an Afterthought"
date: 2025-05-21T13:26:00
slug: real-trust-in-tefca-why-individual-transparency-and-control-can-t-be-an-afterthought
original_url: "https://www.linkedin.com/pulse/real-trust-tefca-why-individual-transparency-control-cant-mandel-md-pflgc"
linkedin_id: pflgc
banner: ./banner.png
---

The ongoing rollout and evolution of the Trusted Exchange Framework and Common Agreement (TEFCA) – a framework designed to enable different health information networks to connect and share data across the country – brings patient data rights to the forefront.

A recent Request for Information (RFI) from CMS, ONC, and ASTP has spurred discussion on these issues. The vision of nationwide health information exchange facilitated by TEFCA is ambitious and important. But for it to truly succeed and earn the trust of individuals, we need to ensure patients aren't just subjects of the exchange, but active participants with real say over their data. This means building in transparency and control from the ground up.

Yesterday I [posted](https://www.linkedin.com/posts/josh-mandel_empower-individuals-with-transparency-and-activity-7330597169361510401-bVZf?rcm=ACoAAAddiWMB0h6icik-ZA6buMW0_YIOCw4I0LQ) about one of my [recommendations](https://joshuamandel.com/cms-rfi-collab/#tefca-and-health-information-networks-must-prioritize-individual-rights-security-and-access): to provide individuals with visibility into, and control over, the exchange of their personal health information through TEFCA. Thank you to Scott Rossignol for engaging in technical and policy discussion on this in a comment. I hit the character limit for LinkedIn comment response, so here's an article expanding my perspective :-)

### The Challenge: Designing for Trust Upfront

First, I want to acknowledge that it will not be entirely easy or straightforward to build support for the kinds of individual transparency and control I am recommending. If it were easy, it probably would have been part of the TEFCA design from the start. But (and this is critical) it is even harder to retrofit support for these principles into a system that wasn't built with them in mind. These principles cannot easily be supported as an afterthought, so it's important to design for them right now, before TEFCA grows to ubiquity.

### Making Audit Logs Meaningful and Accessible

On audit logs, my current thinking is pretty well aligned with what I believe Scott had in mind by "product play." I updated my draft recommendations yesterday afternoon to reflect this: rather than incidentally mandating the creation of a panopticon of access logs in one place, we should ensure that clients can be authorized to query for access logs the same way they might query for clinical data. Any participant would be obligated to share the relevant logs with an authorized client for individual access purposes. This approach, by requiring participants to expose their relevant logs, ensures that transparency isn't just a network-level aspiration but is grounded in the actual data held by the participants. This is not trivial to support (at the very least it requires defining and plumbing in standardized representations for these data, perhaps as FHIR AuditEvents) but architecturally fits pretty well with current TEFCA design. That's the easy(est) part, and it should cover access to logs that QHINs maintain as well as logs that participants maintain (e.g., providers within their certified EHR systems). This means it would make TEFCA-facilitated SSRAA access legible too (that's <https://build.fhir.org/ig/HL7/fhir-udap-security-ig> for anyone reading along at home who has gotten this far despite not being a TEFCA insider).

### Navigating Data Controls in a Complex Landscape

Now let's get into controls. It's true that US healthcare legally allows and frequently uses data flows that patients are unaware of, and which they might, in many cases, find highly surprising or distasteful. At the same time, these data flows can enable processes that patients find reassuring, convenient, or even life-saving. So there's a lot happening. Scott raised an important point about how TEFCA controls would interact with other authorizations, like a payer's legal right or BAA-based exchanges. My principle for TEFCA is that it should enable exchange that is allowed by law and *not in direct contravention to an individual's explicitly stated choices*. For instance, if an individual has activated a "freeze" on their data being shared through TEFCA – analogous to a credit freeze – I think that would be a very good reason not to share their data over TEFCA.

### The Importance of Honoring Individual Choice (Even When It Adds Friction)

There are many potential fallback mechanisms if regular TEFCA exchange is blocked by such a control. Of course, this could add friction and cost, but when an individual actively exercises a control to prevent their data from being shared via TEFCA, it is a pretty strong signal that something has gone wrong from their perspective. Imposing some costs or friction on "the system" in such cases is one way to help align incentives toward respecting individual choices. I can imagine other approaches that don't go as far as saying "you have to fall back to a fax machine" (e.g., escalation and review pathways, or break-glass mechanisms with strong protections). However, I think it is insufficient for organizations to simply acknowledge an individual’s "preference" and then trade data anyway without any friction (which, to be generous, is often the state of play today... from what I can tell, individual choices regarding data sharing are not typically well communicated, acknowledged, or honored). What I've tried to leave room for in my recommendations is a clear basis for individual transparency and meaningful control.

For TEFCA to fulfill its potential, it must be built on a foundation that prioritizes the individual. Ensuring transparency and meaningful control isn't just a technical feature; it's a fundamental requirement for an ethical and effective national health data exchange that truly serves the people it's meant to benefit. This is an ongoing conversation.

*What are your thoughts on how we can best implement these vital principles within TEFCA? Share your comments below.*