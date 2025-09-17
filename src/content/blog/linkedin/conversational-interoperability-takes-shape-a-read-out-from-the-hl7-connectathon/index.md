---
title: "Conversational Interoperability Takes Shape: A Read-Out from the HL7 Connectathon"
date: 2025-09-15T14:58:00
slug: conversational-interoperability-takes-shape-a-read-out-from-the-hl7-connectathon
original_url: "https://www.linkedin.com/pulse/conversational-interoperability-takes-shape-read-out-from-mandel-md-379fc"
linkedin_id: 379fc
banner: ./banner.png
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7373379443723210752"
  share_id: "7373379443723210752"
  share_type: "ugcPost"
  posted_at: "2025-09-15T15:37:30"
  visibility: "MEMBER_NETWORK"
  commentary: |
    Succeeded beyond our hopes with "Conversational Interop" connectathon track this weekend! A glimpse of what's next with AI agents conversing in plain language to share patient data -- tackling rare disease registries, trial matching, referrals, and burnout-inducing admin. Full rundown/writeup in article:
---

Imagine two AI agents, one representing a clinician buried in paperwork, the other a remote registry for a rare disease, exchanging messages in plain English to figure out exactly what patient data needs to be shared—and in what format—before a report can be filed. No endless meetings, no custom APIs hammered out over months. Just a conversation that bridges the gap, pulling from structured records like FHIR when possible, improvising from notes or human input when not. This is conversational interoperability: a technique where autonomous agents negotiate the messy details of data exchange in natural language, making healthcare's fragmented systems feel a little less isolated.

At the HL7 Connectathon in Pittsburgh on September 13-14, 2025, a small group of us—capped at 12 participants to keep things focused—put this idea to the test. Over two days of coding, debugging, and cross-team handshakes, we built and connected agents to tackle real workflows: matching patients to clinical trials, streamlining referrals, navigating prior authorizations. The event wasn't a polished showcase but a raw workshop, centered on my Banterop platform as a testing ground. It revealed not just technical feasibility, but a quiet promise—this approach could significantly shift how we handle the "long tail" of interoperability challenges, from edge-case registries to everyday admin drudgery that standards alone often leave unsolved.

For much of my career, I've helped shape traditional interop standards like SMART on FHIR and CDS Hooks, focusing on rigid, consensus-driven structures to connect systems reliably. But watching these agents adapt on the fly has begun to reframe that work for me: perhaps the future lies less in prescribing every detail upfront and more in enabling fluid dialogue that honors those standards without being shackled by them. What follows are the demos that brought this to life, each a snapshot of agents reasoning through ambiguity in ways that felt both familiar and newly alive.

### The Event in Action: Hands-On Testing and Cross-Team Collaboration

The Connectathon was a deep immersion in code and conversation, with both days spent heads-down on integration and testing, punctuated by few breakouts for deep-dive discussions. [Banterop](https://banterop.fhir.me/), the open-source JavaScript reference implementation I developed, served as a central playground: in Banterop, we simulate agents in the user's browser, creating a lightweight, accessible environment for experimentation. Its scenario library let developers craft custom tests by describing the agents involved, snapshotting relevant data (like patient sketches or trial protocols), outlining behavioral instructions, and specifying tools (internally simulated via LLM calls to mimic real tools without external dependencies).

This setup allowed participants to plug in their own agents—whether A2A clients or servers, MCP clients or servers—and have Banterop seamlessly play the counterpart role. In the weeks leading up, some teams prepared by integrating with the platform, ironing out compatibility issues so the event could zero in on bug fixes and bilateral testing across codebases. Other teams arrived fresh, diving into Banterop's scenarios on the spot to build integrations from scratch: a new referral agent linking to a mock EHR, or a prior-auth simulator probing eligibility criteria.

We tested core scenarios—clinical trial matching, specialist referrals, insurance negotiations—watching agents negotiate turns in real-time. Successes emerged organically: a self-healing data exchange, a bi-directional handshake. We ran into challengs, too, like quirks in A2A task subscriptions, but hashed out resolutions over Zulip and shared screens. We did not track any formal metrics, just the steady progress of connecting conversations, building toward a set of demos in our read-out session.

### Demo Highlights: Agents in Conversation

The demos weren't scripted triumphs but honest explorations, revealing how conversational interoperability could handle healthcare's quirks. They showcased agents not as oracles, but as pragmatic negotiators—asking questions, adapting formats, even recovering from errors.

Michael O'Hanlon II **Automating Rare Disease Reporting** Mick from MITRE demonstrated his "Clinical Agent," a web app designed for agent-to-agent reporting to registries like one for Duchenne Muscular Dystrophy (DMD). Selecting a patient—"Michael David Johnson"—he connected to a registry agent, which responded with a JSON spec for eight data categories: diagnosis codes, genetic tests, vital signs. The clinical agent extracted FHIR data from the patient's record, submitted it, and received feedback: eligible, but missing fields like family history. A clinician UI popped up, pre-filling what it could and flagging gaps in red for quick manual entry.

The beauty was in the dynamism—no hard-coding for one registry. Mick's agent queried requirements on the fly, proving interoperability even with a mismatched external agent from another track (breast cancer screening). "This could be a discovery tool," he said, envisioning clinical systems pinging a network of registry agents to surface reporting opportunities. It was a glimpse of agents as scouts, easing the burden on clinicians who today chase scattered requirements manually.

Eugene Vestel, MBA**: Interop and Scheduling with Banterop** Building on Banterop, Gene showed two modes: fully automated and human-guided. In the first, agents assessed breast cancer screening eligibility—exchanging age and last mammogram date to recommend next steps, all without a human touch. The second walked a manual path: inputting a patient's age (50) and mammogram (January 2021), the agent confirmed eligibility, then queried a live Zocdoc API for Boston providers. It listed three options; selecting one led to a mock scheduling flow, noting the service's temporary unavailability but outlining the full path.

Gene highlighted the orchestration: agents calling third-party APIs as intelligent intermediaries. He credited LLMs like GPT for debugging Claude-powered code, stressing clear prompts as the harness for reliable turns. It underscored conversational interop's end-to-end potential—from query to actionable slots—without assuming perfect data upfront.

Abigail (Abbie) Watson**: Browser-Based, Privacy-Focused Agents** Abigail's CareCommons EHR took a peer-to-peer angle, running local LLMs in the browser to keep data private. Her demo aimed to generate an International Patient Summary but hit snags on screen—protocol mismatches (her message/send vs. others' message/stream) and topology clashes (browser-to-browser vs. client-server). She turned the failure into insight: rewriting backend logic mid-event to connect.

The promise shone in her metaphor—FHIR as the "highway" of standards, agents as "on-ramps" converting unstructured inputs to structured flows. Her administrator agent auto-responded to queries, hinting at privacy-preserving interop for small practices wary of cloud data sharing. It was a reminder that topology matters as much as protocol in this nascent space.

Emma Jones**: Reducing Provider Burden Through Practical Workflows** As a clinician, Emma focused on admin pain points, listing scenarios in Banterop: an agent flagging incomplete chart notes for billing codes; another orchestrating discharge to a long-term facility by querying payer and bed-availability agents, factoring patient preferences like proximity to family; a third handling psychotherapy prior auths or FMLA forms.

Drawing from her sister's struggles as a psychiatric nurse practitioner, Emma emphasized real motivation: "These tasks steal time from patients, fueling burnout." Her agents negotiated unstructured clinician notes into structured submissions, prioritizing workflow relief for solo practices without back-office armies. It humanized the tech—conversational interop not as abstraction, but as a quiet ally against tedium.

Mohit Durve**: Self-Healing Referrals in Live EHR** Mohit from Veradigm staged a cardiology referral for chest pain. His agent verified the referring provider via the NPPES API, checked insurance and docs, then hit a snag: incoming JSON was unparsable. Instead of failing, the agents negotiated—the referrer switched to plain text: "No attachments needed at this time."

Culminating in a live Practice Fusion EHR, the agent created a patient record for "Robert Martinez" and booked a new visit. Mohit called it "implicit programming," with LangGraph separating core logic from prompts for reusability. The self-healing moment was electric: agents adapting like wary colleagues, proving robustness in production-like flows.

Matteo Althoen & Troy Yang**: Modeling Adversarial Prior Auth** From Gen Health AI, Matteo and Troy simulated lumbar MRI prior auth with an "adversarial" payer agent—prompted to nitpick credentials, query dates, suggest cheaper alternatives like X-rays or chiropractic care. The conversation devolved into familiar frustration: escalating demands, circular pushes. Troy's aggressive provider agent tested boundaries, requesting absurdities like Netflix history, which the payer rebuffed.

They tuned behaviors via prompts, revealing "asymmetrical warfare"—a simple agent overwhelming a complex LLM. It mirrored prior auth's tedium, raising flags for guardrails in contentious exchanges. "Agents replicate human pettiness too well," Matteo noted, a caution amid the promise.

Pawan Jindal & Mahbubul Haque**: Bi-Directional Trial Matching** Prompt Opinion's duo demoed their platform as both client and server. As client, Hawk pasted a Banterop Agent Card URL, queried T2DM trial eligibility in natural language, and watched agents converse—human-in-the-loop filling gaps like HbA1c (8.5%) from notes. As server, roles reversed: Banterop fed patient facts; Prompt Opinion checked a loaded protocol document, confirming inclusion criteria autonomously.

Their UI visualized the turns transparently. Pawan likened it to SMART on FHIR—profiling general AI comms for healthcare. "This abstracts policies from data sources," he said, from FHIR to typed inputs. It was the track's interoperability pinnacle: bi-directional, protocol-driven, ready for today's trial-matching pains.

Ignacio Jauregui**: Clinical Guideline Decision Support with RAG Agents** Ignacio Jauregui, a physician and health informaticist at Philips, turned to the thorny task of translating dense clinical guidelines into bedside decisions. Using Banterop, he orchestrated a multi-turn exchange between a clinician's agent and a "Cardiological Guidelines Expert," starting with a query about post-catheterization care for a patient described in a procedure report. The expert agent, drawing from the sprawling 2025 ESC/EACTS Guidelines PDF, requested specifics—demographics, diagnoses, echoes—then synthesized the unstructured report with a live FHIR query for missing data like stenosis measurements. The payoff: a tailored recommendation, citing "Class I, Level B" evidence for PCI on a 90% proximal LAD lesion, all in precise, guideline-grounded prose.

This was retrieval-augmented generation (RAG) in action—agents blending external knowledge bases with hybrid data sources, using tools to fetch structured FHIR without human hand-holding. Ignacio was candid about the "happy path": it took 10 runs to nail, with LLMs often looping redundantly or veering off. His two-step RAG—first scanning for sections, then targeting them—sidestepped crude vector searches, but outputs stayed verbose, needing prompts for clinician-friendly brevity. Different models (Gemini, GPT-4, Ollama) varied wildly in tool-calling reliability, underscoring scalability hurdles: why code brittle CQL rules when agents could adapt to guidelines' national quirks? In conversational interoperability, this demo hinted at agents as living interpreters, bridging guidelines' complexity to patient specifics—though reliability remains the quiet bottleneck.

Kerry Weinberg**: Integrating with Phenoml's Agent Framework** We still need to fully debrief with Kerry (she had to head out just before our wrap-up session), but she got started on an A2A integration layer for Phenoml's agent framework, and she shared many ideas for expanding and building on Banterop to create an end-user-facing testing tool. Can't want to see what's next!

### Reflections on a Paradigm Shift

Mark Kramer from MITRE and I wrapped the session with reflections on what we'd witnessed—a sense of something nascent stirring, where agent-based conversations loosen the grip of rigid standards, inviting dynamic exchanges that feel more like dialogue than decree. Mark called it "the birth of a paradigm shift," comparable to FHIR's early, scrappy emergence. The Connectathon demos, raw as they were, sketched conversational interoperability's contours: agents conversing to make standards like FHIR more alive, handling not just core workflows but the sprawling "long tail"—the N-squared sprawl of bespoke interactions, from niche registries and urgent referrals to adversarial payers and guideline tweaks. Where support falters today, agents stepped in, negotiating from incomplete records or human nudges, turning edge cases into solvable turns.

Yet questions linger, as they must in something this young. The underlying specs—A2A, MCP—are immature, with ambiguities and instabilities expressed in their versioning schemes, governed by not-yet-formalized consensus processes evolving fast in open repos and Discord chats outside of HL7's community. How much role should healthcare-specific standards or profiles play here?

Identity and authorization remain crucial—who verifies an agent's intent? How do we delegate trust for data access safely? Protocols like A2A offer a common language for discovery and chat, but foundational infrastructure—security, permissions—must sharpen as LLMs interpret unstructured data more fluidly, potentially receding the need for hyper-detailed clinical specs.

I see parallels to my past work on SMART on FHIR and CDS Hooks: conversational interop could complement those foundations, letting agents bridge the gaps while we solidify the rails. But rushing formalization risks stifling innovation; perhaps community conversations and self-service platforms like Banterop suffice for now.

This isn't a solved paradigm, but the Connectathon affirmed its traction. If it sparks curiosity—about bridging workflows or debating specs—join the [AI Zulip stream](https://chat.fhir.org/#narrow/channel/323443-Artificial-Intelligence.2FMachine-Learning-.28AI.2FML.29), explore Banterop's [repo](https://github.com/jmandel/banterop) and [intro video](https://www.linkedin.com/posts/josh-mandel_introducing-banterop-testing-platform-for-activity-7369053811341983755-r4c7), or read [Mark's Medium piece on language-first interop](https://medium.com/@kramermark/language-first-interoperability-f650abfb7353).

In a field moving this quickly, the next conversation might be the one that shapes it!