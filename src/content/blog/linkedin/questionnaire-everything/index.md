---
title: "Questionnaire Everything"
date: 2026-05-23T19:13:00
added_at: 2026-10-06
slug: questionnaire-everything
original_url: "https://www.linkedin.com/pulse/questionnaire-everything-josh-mandel-md-uqoec"
linkedin_id: uqoec
banner: ./banner.png
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7464055912857767936"
  share_id: "7464055912857767936"
  share_type: "ugcPost"
  posted_at: "2026-05-23T20:53:25"
  visibility: "MEMBER_NETWORK"
  commentary: |
    With a "questionnaire-everything" SKILL md, any frontier AI agent can turn a pile of PDFs, screenshots, or HTML forms into FHIR Questionnaires. This is the easy part of killing the clipboard... See article below to understand where this fits into workflows.
---

Every clinic visit still involves filling out forms: your name, your address, your medications, your allergies, how your back has felt over the past two weeks. Much of it the clinic already has, or could look up, but a form on paper has no way to ask the rest of the health system what it knows... and electronic forms are often no better.

Kill The Clipboard is working to fix that. [My recent July 2026 update](/blog/posts/kill-the-clipboard-for-july-2026-sharing-fhir-data-patient-stories) describes where things stand: when a patient shares their medications, allergies, problems, and immunizations from an app, the receiving EHR is now required to save that structured data into the chart, alongside any PDFs the patient sends. That handles the questions repeated at every visit. It does not handle the visit-specific ones: the reason-for-visit questions, the symptom questionnaires, the social-needs questions a particular clinic decided to ask. Those exist because a specific clinic, on a specific day, needs a specific answer, and there is still no interoperable way for the clinic to ask or for your app to answer. *So you still fill them in by hand.*

Closing that gap takes a check-in protocol, where the clinic tells your app what this visit needs and your app answers back; a working prototype, [SMART Health Check-in](/blog/posts/killing-the-clipboard-update-on-smart-health-check-ins-with-w3c-digital-credential-iso-mdoc-flow), already exists. But a protocol needs something to carry: the clinic's actual forms, in a format an app can render and return. The worry has been that getting forms into that shape is itself a major undertaking. So I tested it.

I built a conversion pipeline and pointed it at a pile of real forms. An AI agent gathered 224 intake and follow-up forms published by hospitals, professional societies, and state health agencies: PDFs, web forms, whatever it found. The pipeline turned them into 72 FHIR Questionnaires, the health-data standard's format for a fillable form that software can render and score. (224 collapses to 72 because many sites post the same instruments, and some harvested files were not forms at all.)

The forms came in two kinds. About two-thirds were standardized instruments: named, published questionnaires such as the PHQ-9 depression screen or the Oswestry back-pain index, identical wherever they appear. The rest were local: one practice's own new-patient packet, particular to that clinic. They share no common structure; each has its own sections, its own answer scales, its own skip logic where one answer hides or reveals later questions.

The pipeline does not try to flatten that variety. An AI agent converts each form as it actually is, wording, branching logic, scoring, and all. A deliberately small slice of the standard, well supported and free of its more speculative features, keeps every result as plain, portable data any patient app can open.

I packaged this whole pipeline as a ["questionnaire-everything" SKILL.md](https://github.com/jmandel/fhir-questionnaires-from-the-web/tree/main/skills/questionnaire-everything) that any AI agent can load: instructions distilled from the conversion experiment, plus runnable scripts for writing and validating FHIR Questionnaires, all open and freely licensed. Point an AI agent equipped with the skill at a folder of anything, a clinic's real and idiosyncratic mix of intake packets and follow-up sheets, and it produces Questionnaires that plug into a KTC check-in workflow. The 72 converted forms are just the evidence that it works. A practice with one technically minded person can run its own forms through it and review the drafts; the first pass surfaces the rough edges, and after that, adding or updating a form is routine.

Converting the forms is one thing; filling them is another. I ran a second pass over the 72 Questionnaires, all 1,980 answerable questions in them, sorting each by whether it could be filled automatically from a reasonably complete health record or genuinely needs the patient at the moment of the visit. There are two very different patterns.

* Across 22 real provider intake packets, about **87% of questions are answerable** from data a record already holds: name, address, insurance, medications, allergies, problems, prior procedures. The record-fillable side is also largely covered already: the medications, allergies, problems, and immunizations in the July 2026 scope, plus basic demographics, account for roughly two-thirds of them. (A clinic's intake form has two layers: a shell the patient's own record can fill, and a smaller surface of genuine per-visit input. The data for the first layer is already moving.)
* Across the standardized symptom questionnaires it **drops to about 5%,** because those ask how you feel right now, and only you can answer that

None of this means the clipboard is solved. EHRs still have to do the integration work to receive and route answers. Clinics still have to adopt check-in tooling. Patients still need an app they trust, of their own choosing, to hold their data and facilitate sharing. But converting a clinic's forms, long treated as a barrier to even starting, is not the hard part. It takes a folder of forms, an AI agent with the right skill, and an afternoon of review.

The skill, the 72 example Questionnaires, and the source forms are all at [github.com/jmandel/fhir-questionnaires-from-the-web](http://github.com/jmandel/fhir-questionnaires-from-the-web), with a browsable catalog at [joshuamandel.com/fhir-questionnaires-from-the-web](http://joshuamandel.com/fhir-questionnaires-from-the-web).