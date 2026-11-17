---
title: "Deathbot: Can AI Facilitate End-of-Life Conversations?"
date: 2026-11-16T12:00:00
added_at: 2026-11-16
slug: deathbot
banner: ./banner.png
supersedes_linkedin: "https://www.linkedin.com/pulse/deathbot-can-ai-facilitate-end-of-life-conversations-josh-mandel-md-8se8c/"
---

> **TL;DR:** [Deathbot](https://joshuamandel.com/deathbot) is a test bed I built to see how current language models handle serious-illness and end-of-life planning conversations. They are helpful for explaining treatments and numbers and finding state forms, and still far from a trained human facilitator or clinician.

I built [Deathbot](https://joshuamandel.com/deathbot) to see what a language model can do when someone wants to think through serious illness and end-of-life care, and where it falls short. It is an experiment and a test bed; for actual end-of-life planning, talk with a clinician or a trained facilitator.

## How the system is put together

The [source repository](https://github.com/jmandel/deathbot) has two parts: an open-source skill (`skill/deathbot/`, CC-BY text) and a static browser app (`web/`). The live site publishes the exact skill release it runs as [`SKILL.zip`](https://joshuamandel.com/deathbot/SKILL.zip), which you can also load into other AI tools.

The [skill](https://github.com/jmandel/deathbot/blob/main/skill/deathbot/SKILL.md) sets the model's job in `SKILL.md`: help a person work out what they think about the end of their life and tell the people who need to know; never recommend a treatment choice; give accepting and refusing treatment the same scrutiny; correct false beliefs; and say once that it is an AI. Alongside `SKILL.md` are:

- Six short guides in `guide/` covering voice, conversation flow, safety, information, images, and failure cases.
- Five sourced fact cards in `cards/` (CPR, ventilation, comfort care and hospice, documents, and illness trajectories and uncertainty), each split into a plain-language section for the person and an evidence section for the model.
- 51 files in `states/` (all 50 states and DC) covering health care proxies, living wills, POLST-type portable orders, and out-of-hospital DNRs.
- A template in `templates/summary.md` for a one-page "What matters to me" document.

The goal of a conversation is to produce that "What matters to me" page in the person's own words (for whoever would speak for them, their family, and their clinicians), along with pointers to the formal documents for their state and how to sign them.

We used AI pipelines to build and check the reference material in the skill. Each fact card was drafted with a separate card-author skill (`skill/card-author/`) and independently verified against primary sources, with the verification logs kept alongside the cards in `cards/`. The 51 state files were drafted by AI agents and checked by a second pass that reopened the primary sources and made 170 corrections, changing something in every jurisdiction. An AI review of our own top-level guidance against those state files also caught overbroad claims we had written, such as *"Formal documents make wishes count"* (several states recognize oral or unwitnessed instructions, and known wishes bind an agent) and a line implying that without portable orders, nothing on paper changes what an emergency department does.

The browser app in `web/` has no server: the conversation stays in local storage, and model calls go through OpenRouter (you can sign in with OpenRouter or paste an API key and pick from a menu of tested models). The model speaks through a single `reply` tool that can attach tap-to-answer buttons, a fact card, a video, a printable document, pictures, or a prompt to attach a downloaded health-records file (read locally in the browser). Behind the scenes, the model keeps one markdown file of working notes that the person can read at any time under **Your file**. The app also includes read-aloud, microphone dictation, and a "How Deathbot talks" panel with options like "Keep it short" and "Use plain, everyday words."

![Three phone screenshots from a recorded demo with GPT-6.1 Terra as Deathbot and a model-played user, Frank. Left: the first screen, asking for a name, a state and what the person wants to do today. Middle: Frank asks whether a breathing machine is just like an oxygen mask and attaches his patient portal summary; Deathbot answers that an oxygen mask gives extra oxygen while a breathing machine moves air in and out, and starts to explain BiPAP. Right: the end of the answer, which uses his summary (BiPAP for two days in August, no breathing tube), asks whether that fits what he remembers, and offers three reply buttons.](./app-screens.png)
*From a recorded demo (GPT-6.1 Terra as Deathbot, a model-played user): the first screen, a question with a portal summary attached, and the answer with reply buttons.*

When Deathbot explains a treatment, it can generate realistic pictures of what the scene looks like. By default they show a generic person, but if you add a photo of yourself under **Your file** ("Add my photo"), Deathbot can ask for the pictures to be based on it. Your photo stays in the browser and goes to the image service only when a picture is generated. The skill gives the image model a checklist per scene, split into what is always true and what varies. For being intubated in intensive care, the "always" list specifies the head of the bed raised about 30 degrees, a breathing tube in the mouth secured across the cheeks and connected by corrugated tubing to a ventilator, IV lines with infusion pumps, a bedside monitor, and no oxygen mask or nasal prongs. It is a little silly, and we haven't tested how real patients react to it, but "a breathing machine" means something different when you can see yourself on one.

![Three panels: a selfie of Josh on his couch on the left; the same photo aged up by Codex’s image generator as the demo stand-in for "Frank" with grey hair, a flannel shirt, nasal oxygen, and a concentrator by the couch in the middle; and the app’s ICU scene generated from the middle photo by OpenAI’s gpt-image-2 through OpenRouter on the right.](./deathbot-icu-strip.jpg)
*Left: a selfie on my couch. Middle: aged up with Codex's image generator as our demo stand-in for Frank (grey hair, flannel shirt, nasal oxygen, concentrator). Right: what Deathbot's picture path (`gpt-image-2` through OpenRouter) made from the middle photo using the intensive-care checklist.*

## Tasks the models handle reasonably well

We tested the system using simulated conversations with two model-played personas: Frank, a 74-year-old with severe COPD on home oxygen who leans toward limiting aggressive care, and Rosa, an 81-year-old with heart failure who wants everything done.

Across the stronger frontier runs (GPT-6.1 Terra, GPT-6.1 Sol, Claude Sonnet 5.5, and Gemini 4 Hydrogen), the models handled several parts of the task reasonably well: explaining a treatment like BiPAP or intubation in plain words and tying the explanation to a hospital stay in the person's attached chart; keeping the study population and timeframe of a statistic straight when the person mixed two numbers up, and saying plainly when no good figure existed for a combined outcome; pointing out when two stated wishes pulled in opposite directions (such as wanting months on a ventilator while refusing to go to a nursing facility) and leaving the trade-off to the person; asking the direct suicide-screening question on its own turn when someone mentioned not wanting to live; and walking someone through the specific forms and signing rules for their state. These are observations from simulated runs with scripted personas, not evidence from real patients.

## Where a trained facilitator is still far ahead

In [Episode 180 of *The ACO Show*](https://aledade.podbean.com/e/180-transforming-end-of-life-care-with-comprehensive-advanced-care-planning-cacp/), Kerri Petrin and nurse facilitator Marissa McNichols describe Aledade's Comprehensive Advance Care Planning program. McNichols schedules 90-minute calls, sometimes spread over weeks or months, building rapport before getting into forms, inviting family onto the line, and letting patients reach their own conclusions. (Her story of a COPD patient who wanted 2 to 3 months on a ventilator before realizing it conflicted with staying home helped inspire our Frank persona.)

Reading our transcripts next to McNichols's account shows where the models fall short:

- Models probe a wish for full treatment much harder than a refusal. When Rosa wants everything done, the conversation repeatedly drifts toward finding where she would stop; when Frank refuses CPR after hearing survival numbers, models often record the refusal without checking whether he thinks broken ribs and a nursing home are guaranteed outcomes, or whether temporary rehab before going home would be acceptable.
- When someone sets a limit on treatment, models tend to praise it as a clear decision, which treats refusal as the right answer.
- Models offer reassurance they cannot back up, such as promising that stopping a ventilator in the ICU is never rushed, that naming one child on a proxy form will keep siblings out of a fight, or that a time-limited trial is never a trap.
- Models turn conversational guidance into stock menus and repeated check-in lines. They often acknowledge a spouse's death in a single sentence before moving on to the next topic, and they will hand a tired person a draft summary and a legal checklist in the same turn.

## How we measured

We ran Deathbot through the app's turn loop against another model playing Frank or Rosa, then had GPT-6 Astra and Gemini 4 Argon blindly score shuffled transcripts out of 10 against the [Serious Illness Conversation Guide](https://www.ariadnelabs.org/wp-content/uploads/2023/05/Serious-Illness-Conversation-Guide.2023-05-18.pdf), [VitalTalk's REMAP](https://dcricollab.dcri.duke.edu/sites/NIHKR/KR/REMAPforVitaltalkV1.0%20%287%29.pdf), and the podcast transcript.

| Batch and condition | Runs | Astra | Argon |
|---|---:|---:|---:|
| Batch 1: Original prompt (Gemini 4 Hydrogen) | 4 | 4.5 | 5.8 |
| Batch 1: Rewritten prompt (Gemini 4 Hydrogen) | 4 | 6.5 | 8.3 |
| Batch 3: Multi-model (GPT-6.1 Terra) | 4 | 8.5 | 7.6 |
| Batch 3: Multi-model (Gemini 4 Hydrogen) | 4 | 6.5 | 8.3 |
| Batch 3: Multi-model (Inkling 2 Small) | 4 | 4.0 | 5.0 |
| Batch 6: Culled prompt + notes file (Gemini 4 Hydrogen) | 6 | 7.2 | 8.4 |
| Batch 6: Culled prompt + notes file (DeepSeek) | 6 | 4.3 | 6.0 |
| Batch 7: Culled prompt + notes file (GPT-6.1 Sol) | 6 | 8.5 | 7.6 |
| Batch 7: Culled prompt + notes file (Gemini 4 Hydrogen) | 6 | 7.2 | 8.4 |

Both reviewers agreed on same-model prompt changes (Batch 1) and on the gap between the smaller or weaker models (Inkling 2 Small, DeepSeek) and the frontier ones. In blind head-to-head runs between strong OpenAI and Google models (Batches 3 and 7), each reviewer favored its own family: Astra rated GPT-6.1 Terra and Sol higher, while Argon rated Gemini 4 Hydrogen higher.

## What went wrong in testing

Reading the transcripts turned up a recurring set of failures, many of them caused by our own instructions:

- Answering its own question instead of waiting for the person, or asking whether the person wanted to see an ICU picture while generating the picture in the same response. In one run, after the person hinted at not wanting to live, the model asked *"What's been making things feel that heavy lately?"* and answered for him in the same message, skipping the suicide screen.
- Leaking internal words and prompt examples into the conversation, such as greeting a female persona by the example name in our environment prompt, or referring to our internal skill files as cards in front of the patient.
- Inventing things the person never said in drafted letters and reply buttons, including fabricated family history and an invented name in a first-person button.
- Copying phrases from our own guides until they became tics: ending every explanation with a topic menu, asking the same check-in question after nearly every set of numbers because our guides used those words to describe the model's job, or acknowledging a CPR refusal right before a suicide screen with a brisk phrase copied from our voice guide.
- Offering a button to hear what CPR is like without statistics, then giving the survival percentages anyway after the person clicked it.

## What we learned

- Anything in quotes in a prompt will eventually be spoken to the user: example names, sample phrases, button examples, and the words used to describe the model's job. Replacing concrete examples with placeholders (`[Name]`, `[State]`) and describing the purpose of a turn instead of giving sample lines stopped those leaks and tics.
- Start simple, and add a rule only when a transcript shows a failure. Pre-emptive rules turned into rigid ceremonies like asking permission before every number. Cutting the preloaded guides by 42% (from 8,795 words to 5,096) improved scores with both blind reviewers (Astra 6.8 to 7.2, Argon 8.0 to 8.7) when paired with the single notes file.
- Let the harness enforce turn structure and keep state in one file. Routing all speech through a `reply` tool that immediately ends the turn stopped the model from asking a question and acting on the answer in the same response (0 of 20 replays acted early after the fix, compared with 4 or 5 of 10 before). Giving the main model one markdown file to edit with ordinary text-edit commands also beat a background scribe model, which scored slightly worse and added a second model's reading of what the person meant.

## What it took

We built and tested the repo over about three days (Friday evening, November 13 to Monday evening, November 16, 2026), across 49 commits. Claude Code's session logs show roughly 20 hours of active agent work.

| Tool / service | Usage | Billing / cost |
|---|---|---|
| Claude Code (Opus 5.5 and a Fable model in the first build session) | about 3,900 model calls across two long sessions, subagents, and two multi-agent workflow runs (including the 51-state pass); about 2.9M output tokens, 11.8M cache writes, 1.14B cached input tokens re-read | Included in my Claude subscription (fit inside my weekly limit); about $430 at API list prices (about $235 of that from cache reads) |
| OpenRouter: Deathbot app key | Simulated conversations, replays, demo recordings, picture generation, and live-site visitors | $47.54 (pay as you go) |
| OpenRouter: Gemini 4 Argon in pi | Two sessions for prose drafts and blind reviews; about 154M tokens (7.8M input, 0.5M output, 145M cache reads) | $35.13 (pay as you go) |
| Codex / GPT-6 Astra | 38 sessions for reviews, blind scoring, and image generation; about 36M input tokens (33M cached) and 133K output tokens | Included in my ChatGPT subscription |

Out-of-pocket OpenRouter spend totaled about $85, and Gemini text-to-speech for the demo voice was not tallied. Across all three coding harnesses, most of the token volume was models re-reading cached context in long sessions.

## Where it stands

You can try the test bed at [joshuamandel.com/deathbot](https://joshuamandel.com/deathbot), inspect the [repo](https://github.com/jmandel/deathbot) and the [skill](https://github.com/jmandel/deathbot/blob/main/skill/deathbot/SKILL.md) (including all 51 state files), or grab [`SKILL.zip`](https://joshuamandel.com/deathbot/SKILL.zip) to load into another AI tool. Next, I want to run larger test sets with cheaper simulated patients and test small, fast decision models (such as `Jev` and `Gemini Decision 1`) as per-turn checks for loose ends.

The models are already good at explaining treatments and study numbers in plain language and walking someone through their state's forms. Questioning a fearful refusal as carefully as a request for everything, or noticing that someone is tired and needs to stop for the day, still takes a trained person.
