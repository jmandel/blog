---
title: 'Let''s Talk about Appropriate Use Criteria'
date: 2025-10-18T01:46:00.000Z
slug: lets-talk-about-appropriate-use-criteria
original_url: "https://www.linkedin.com/pulse/lets-talk-appropriate-use-criteria-josh-mandel-md-jpj4c"
linkedin_id: jpj4c
banner: "https://media.licdn.com/mediaD5612AQEtAHQhZFYU4Q"
---

Few initiatives represent the gap between promise and reality quite like the Appropriate Use Criteria (AUC) program for advanced diagnostic imaging. The goal was unimpeachable: ensure that when a clinician orders a costly or high-radiation scan like a CT or MRI, the decision is backed by solid, evidence-based medicine. It was a policy designed to improve quality, reduce waste, and protect patients.

**CMS once estimated the original AUC program could save Medicare $700 million annually.**

And yet, after nearly a decade of rulemaking, development, and delays, it was quietly shelved. The story of why it failed is a crucial lesson in health IT, but more importantly, it points toward a new, promising path for moving this conversation forward.

### A Good Idea Meets a Brittle RealityThe story begins with the Protecting Access to Medicare Act (PAMA) of 2014. Congress mandated that CMS establish a program to promote the use of AUC. The mechanism they envisioned was, on paper, straightforward. An ordering clinician would consult a qualified Clinical Decision Support Mechanism (CDSM)—an electronic tool—which would confirm whether the ordered scan adhered to established guidelines. The furnishing provider, like a hospital radiology department, would then have to report this consultation information on their Medicare claim to get paid.

The implementation, however, was anything but straightforward. After years of defining the rules for qualifying guideline authors (Provider-Led Entities) and software (CDSMs), the program officially entered an "educational and operations testing period" on January 1, 2020. In this phase, reporting was required, but payment wasn't at risk. The idea was to iron out the kinks.

The kinks turned out to be fundamental flaws in the architecture. The entire system rested on a brittle, real-time, claims-based reporting requirement. This created a cascade of problems:

- **High Friction:** It forced clinicians into a rigid, often disruptive workflow, turning a moment of clinical decision-making into a bureaucratic check-box exercise.

- **Misaligned Incentives:** It penalized the *furnishing* provider (who performs the scan) for the potential non-action of the *ordering* provider, two parties who often have no direct organizational link.

- **Technical Fragility:** CMS's own claims processing systems, as the agency later admitted, were not equipped to reliably distinguish which claims were subject to the rule and which were not, creating a high risk of improper denials.

After multiple extensions, CMS finally acknowledged the obvious. In its Physician Fee Schedule Final Rule for 2024, the agency paused all efforts to implement the program, stating that the challenges were "insurmountable" and the program "impracticable." It was a quiet end to an ambitious project.

### A New Pathway: From Checklist to ConversationHere we are in late 2025, and the problem of inappropriate imaging hasn't vanished. But our tools for thinking about it have evolved dramatically. The failure of the AUC program wasn't a failure of its *goal*, but of its *mechanism*. It tried to solve a nuanced clinical problem with a rigid, unforgiving technical hammer.

What if we approached it as a conversation instead?

Imagine a clinician ordering a lumbar MRI in their EHR. As soon as the order is initiated, a process is triggered. We can assume this trigger mechanism—knowing an order has been placed—is largely a solved problem thanks to the now widespread adoption of the HL7 CDS Hooks standard, making that part of the integration a near-zero marginal cost.

Instead of a pop-up alert with a list of criteria, a discreet AI-powered sidebar appears and asks a simple question in plain language: *"To help apply the right guideline, can you tell me a bit about the patient's symptoms? For instance, any red flags like fever or neurological deficits?"*

The clinician can reply in unstructured text: *"No red flags, he's had pain for 2 months and PT didn't help."*

The agent, using the patient's record as context (via FHIR APIs) and a deep understanding of the guidelines, can synthesize a response: *"Understood. For chronic low back pain after failed conservative therapy, an MRI is appropriate. I've documented this and attached the rationale to the order."*

This is not a far-future vision. The "Conversational Interoperability" work we've been testing at HL7 Connectathons shows this is technically feasible today. It transforms the interaction from a punitive mandate into a helpful, ambient consultation. It respects clinical workflow, automates the burdensome documentation, and uses AI not as an oracle, but as a pragmatic collaborator.

### The Economics of Doing It RightSo what would it take to build this? Instead of forcing every EHR vendor and health system to solve this independently, we could build a national **"AUC Guidance Service"** as a public utility. This centralized service would host the conversational AI engine and the clinical knowledge base, offering a standardized API for EHRs to plug into.

A project of this scale—one that is secure, reliable, clinically safe, and able to withstand the rigors of federal procurement and governance—requires a serious investment. My initial back-of-the-envelope math felt too low, and upon reflection, it was. Building national infrastructure is not the same as building a startup prototype.

A more principled estimate would look something like this:

- **Fixed Cost: Developing the Public Utility.** This is the upfront investment to build the core platform. It includes the multi-year effort of engineering, rigorous security audits (like FedRAMP), creating the legal and policy governance, and ingesting and maintaining the clinical guidelines. A realistic budget for a project this critical would be in the range of **$10 to $30 million** over the first two to three years. This is the price of building something trustworthy at a national scale.

- **Variable Cost: EHR Integration.** This is the "last mile" cost to bring the service into the clinic. While CDS Hooks provides the trigger, each EHR still needs to build the user-facing conversational component. Integration costs could vary by EHR but would largely represent shared infrastructure that could benefit diverse use cases.

The total upfront investment is on the order of $10-100M. Given CMS's estimate of $700M annual savings, this is an investment with a staggering potential return. More importantly, it promises to achieve those savings not by adding to clinicians' administrative burdens, but by actively reducing them—a benefit that is harder to price but essential for the health of our clinical workforce.

The first chapter of the AUC story ended abruptly in a necessary retreat from a flawed design. The next chapter offers a chance for a more meaningful dialog.