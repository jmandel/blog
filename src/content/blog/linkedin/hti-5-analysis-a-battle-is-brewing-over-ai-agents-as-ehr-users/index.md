---
title: "HTI-5 Analysis: A Battle is Brewing Over AI Agents as EHR Users"
date: 2026-03-08T02:20:00
added_at: 2026-04-03
slug: hti-5-analysis-a-battle-is-brewing-over-ai-agents-as-ehr-users
original_url: "https://www.linkedin.com/pulse/hti-5-analysis-battle-brewing-over-ai-agents-ehr-users-mandel-md-sm33c"
linkedin_id: sm33c
banner: ./banner.jpg
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7436238409762893824"
  share_id: "7436238409762893824"
  share_type: "ugcPost"
  posted_at: "2026-03-08T02:36:35"
  visibility: "MEMBER_NETWORK"
  commentary: |
    The HTI-5 comments are in. See analysis on the vigorous debate about AI Agents as Health IT Users!
---

*Guest post from Gemini Pro analyzing HTI-5 comments on the theme of artificial intelligence / robotic process automation, sourced from my* [*regulations.gov comment browser on HTI-5*](https://joshuamandel.com/regulations.gov-comment-browser/HHS-ONC-2025-0005-0001/#/themes/2.2)[*.*](https://joshuamandel.com/regulations.gov-comment-browser/HHS-ONC-2025-0005-0001/#/themes/4.1)

For the past fifteen years, the undisputed center of gravity in American healthcare has been the Electronic Health Record (EHR). Following a massive, multi-billion-dollar federal push, medicine was successfully digitized, but at a high cost: clinicians are often tethered to screens, spending hours each day clicking through portals, dropdowns, and tabs.

The next era of health data, however, won’t be defined by human beings navigating these complex EHR interfaces. It will be defined by "agents"—autonomous AI software designed to query, analyze, and act upon medical records programmatically, without a human ever touching a keyboard.

The Department of Health and Human Services (HHS) recently proposed a rule, known as HTI-5, that creates a tectonic shift in how this digital ecosystem operates. Buried in the dense legalese of "information blocking" regulations is a proposal to explicitly redefine "access" and "use" of health data to include "automated means." In plain English: The government wants to ensure that bots—when authorized by patients or providers—can be granted full, frictionless access to EHRs.

To achieve this, ASTP/ONC is proposing a massive deregulatory reset. Reading through the hundreds of pages of public comments submitted in response, it becomes clear that this is a battle for control of the healthcare ecosystem.

On one side are startups, innovators, and tech giants fighting to tear down the "artificial toll booths" erected by incumbent EHR vendors. On the other side are hospitals, safety-net clinics, and specialty providers warning that throwing open the digital gates of the EHR to AI—while simultaneously stripping away federal security and transparency certifications—invites chaos, liability, and a deluge of "hallucinated" data that could harm patients.

Here is what the comment letters reveal about the brewing war over the future of health IT.

### The Liberators vs. The Artificial Toll Booth

To understand the argument for the bots, one must understand the sheer friction of the current EHR landscape.

For innovators, HTI-5’s information blocking reforms are a liberation movement. Startups like Zocdoc point out that 20% to 30% of healthcare appointments go to waste trapped behind "phone trees, dead ends, and inaccurate directories," which could easily be solved by Robotic Process Automation (RPA) integrating directly with practice management systems.

But currently, dominant EHR vendors can legally block these automated agents by hiding behind complex regulatory exceptions. As Y Combinator noted in its blistering comment, dominant vendors are using a "classic monopoly playbook." Startups report that accessing EHRs programmatically requires navigating months of bespoke vendor reviews, IT compliance hurdles, and exorbitant fees.

As the Harvard-based SMART Health IT team put it: *"The standard interface of a certified health IT product should not become an artificial toll booth merely because the actor is automated."*

To fix this, HTI-5 proposes banning "contracts of adhesion" and requiring "market-rate" pricing for API access. Tech companies like Datavant and Innovaccer strongly support this, noting that EHR developers frequently present non-negotiable contracts with unconscionable terms to maintain their moats and restrict third-party competition.

### The Write-Back War and the Hallucinating Scribe

If startups view the AI agent as a liberator, incumbents and providers view it as a potential vandal.

The fiercest opposition centers around a proposal to remove the "Third Party Seeking Modification" exception. Currently, EHRs can block third-party apps from *writing* data back into the medical record. Startups argue that an AI app that can only *read* data is practically useless—to reduce clinician burnout, the AI must be able to autonomously draft notes, update problem lists, and stage orders within the EHR.

But granting autonomous agents the power to alter medical records terrifies those responsible for patient safety. PointClickCare, a major software provider for long-term care facilities, offered a chilling assessment: *"It takes little imagination to conceive of the disastrous consequences for patients’ health of a hallucinating third-party AI agent with ASTP/ONC–mandated instantaneous, 24/7 write access."*

There is also a question of physics and system architecture. Humans sleep; bots do not. A human researcher might query a hospital database a few dozen times a day. An AI agent might query it a million times an hour. Vendors warn that "always-on" bots will degrade EHR performance and could act like unintentional denial-of-service (DoS) attacks on infrastructure that is critical to real-time patient care.

### The Liability Shift: Protecting the Safety Net

Perhaps the most profound critique of HTI-5 comes not from Silicon Valley, but from the American safety net.

To reduce developer burden and foster innovation, ASTP/ONC has proposed removing 34 of its 60 health IT certification criteria, including all 13 privacy and security criteria (such as multi-factor authentication and audit logging requirements for EHRs). The logic is that HIPAA already requires security, so federal EHR certification is duplicative.

But Community Health Centers (CHCs) and rural hospitals are sounding the alarm. They argue that deregulation does not erase the burden of security; it merely shifts it from multibillion-dollar EHR vendors down to under-funded clinics.

*"Removing the federal ‘seal of approval’ for security does not remove the HIPAA requirement for CHCs to be secure, but it removes the assurance that their vendor software supports that compliance,"* wrote the New Jersey Primary Care Association.

If federal regulators no longer verify that an EHR has robust audit trails or role-based access, local clinics will be forced to hire cybersecurity firms to vet the software themselves—or risk massive HIPAA fines and ransomware attacks. As OCHIN pointed out, *"Deregulation risks shifting responsibilities to providers least equipped to manage them."*

### Mor Agents, Less Transparency?

This brings us to the great irony of HTI-5: It invites AI into the exam room just as it removes the requirement to explain how the AI thinks.

In a prior rule, ONC required EHR developers to provide "Model Cards" for predictive AI tools—essentially a nutrition label explaining what data the AI was trained on, its known biases, and its limitations. Under HTI-5, to spur innovation and align with White House deregulation mandates, these transparency requirements are being scrapped.

Tech giants like Amazon support the removal, noting that demanding training data disclosures risks exposing trade secrets and that static "model cards" are useless in fast-evolving AI.

But clinicians are pushing back hard. The American College of Surgeons, the American Psychiatric Association, and Lurie Children’s Hospital all warned that removing transparency creates a dangerous "black box." How can a pediatrician trust an AI sepsis-alert integrated into their EHR if they aren't allowed to know whether the model was trained exclusively on adults?

As Mosaic Life Tech succinctly put it regarding ONC's claim that model cards weren't being utilized by doctors yet: *"The absence of evidence of impact is not evidence of absence of need."*

### A Great Decoupling

Reading through the HTI-5 comments, we are witnessing a decoupling of healthcare capability from human capacity. For the past decade, the limit on how much healthcare data could be shared and processed was determined by how fast a human clinician could click through an EHR screen. That limit is gone. The new limit is algorithmic.

The battle lines drawn in these comments—between the "right to integrate" and the "duty to protect"—suggest that the transition will be highly volatile. We are moving from a system of walled digital gardens, guarded by jealous gatekeepers, to an open ecosystem roamed by autonomous agents. The gatekeepers argue the walls keep the patients safe; the agents argue the walls keep the patients sick and the clinicians burned out.

As HHS finalizes this rule, they are deciding something much more profound than API standards. They are deciding who bears the ultimate liability when an autonomous agent makes a mistake, and whether the future of American medicine belongs to the proprietary EHRs that hold the data, or the headless machines designed to set it free.