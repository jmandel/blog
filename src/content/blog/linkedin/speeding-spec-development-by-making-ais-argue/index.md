---
title: "Speeding Spec Development by Making AIs Argue"
date: 2025-10-14T18:42:00
slug: speeding-spec-development-by-making-ais-argue
original_url: "https://www.linkedin.com/pulse/2025-10-14 18:42:15.0-Speeding Spec Development by Making AIs Argue"
---
Speeding Spec Development by Making AIs Argue
=============================================

Standards are supposed to bring clarity. Writing them is hard, getting them right is harder, and the feedback loop from implementation is the only thing that truly proves them out. The faster we can automate and accelerate that loop—to find the bugs, the gaps, and the ambiguities—the better our standards become.

This post is about a new way to tighten that loop. The core idea is simple: **if multiple, independent AI implementations of the same spec disagree, the disagreements themselves point to the fuzzy parts.**

But to make any of this feasible, we first have to solve a fundamental technical problem: LLM attention is a critical constraint, and in the name of clarity, standards can often be... longwinded.

### The Context Bottleneck

Frontier language models are impressively capable of interpreting specs, implementing protocols, and writing tests. But give them a 100k-token specification, and you’re fighting against a limited window of useful context. The disconnect is that specifications are dense and **interdependent**: a validation step in §7 references a definition in §3 that references a threat model in §2. Open the doc at a random section, and you’ve implicitly skipped half the context.

As you work, code assistants quietly “compact” this context. The spec details you relied on get summarized away. The next edit is then laden with impressionistic interpretations and subtle bugs. Agentic interactions help (e.g., an LLM driving behaviors to grep through your code base and rediscover relevant snippets), but this often leads to incomplete and incorrect understanding. The picture gets blurry, then re-fills with hallucinated details.

This led me to a simple question: **what if we could keep the whole spec in scope—faithfully enough to implement—with a much smaller context toll?**

### The Goal: An Implementer's Artifact

My goal isn’t a new format for normative text. It’s an **implementation artifact**: a short, dense companion to the original spec that fits entirely in a model’s context window while I’m doing real work. If this artifact is 5× smaller (say, from ~125k tokens to ~25k), I can keep it pinned while I iterate. Less paging, less forgetting, fewer “compaction” surprises.

This artifact is **non-normative** and full of citations back to the source. Think of it as a developer manual that keeps every key constraint in reach, enabling the more ambitious goal of finding ambiguity.

---

### A Practical Workflow for Spec Compression

The process is a systematic, two-stage flow designed to turn verbose prose into dense, structured artifacts.

**Stage 1: Generate a "Prompt Suite"**

First, I feed the entire specification to a model with a large context window. I don't ask it to write the summary directly. Instead, I use a detailed *meta-prompt* to make it generate a work plan: a numbered list of highly specific prompts that will, when executed in order, regenerate the spec's essential content.

This meta-prompt is the blueprint for the entire operation. It instructs the model to act as a "technical specification distillation expert," breaking the spec down into atomic, MECE (Mutually Exclusive, Collectively Exhaustive) units and prioritizing high-density outputs like TypeScript interfaces, pseudocode, and tables.

**Stage 2: Execute the Suite to Create the Artifact**

With the prompt suite in hand, I start a new session and execute the prompts one by one, concatenating the outputs. For the OpenID Federation 1.0 spec (~125k tokens), this process generated 68 prompts and resulted in a ~25k token artifact.

This approach ensures comprehensive coverage and high-fidelity output. For example:

* **Prompts #3-6** systematically built a full glossary covering Core Entities, Statements, and Roles.
* **Prompts #10-14** incrementally constructed the complete EntityStatementClaims TypeScript interface.
* **Prompt #15** generated a precise pseudocode algorithm for Trust Chain Validation.
* **Prompts #26-32** each targeted a single metadata policy operator (like value or subset\_of), defining its behavior in a structured format.

The final artifact was small enough to keep pinned while driving a reference implementation, with citations providing a quick breadcrumb trail back to the normative source when needed.

---

### From Compression to Ambiguity Discovery

Now, with a reliable way to keep the spec in scope, we can return to the big idea: using disagreement as a signal. Here's the sketch of the research thread:

1. Generate, say, **10 distinct compressed summaries** of the same spec (using different seeds, models, or slightly varied meta-prompts).
2. For each summary, ask a model to implement the same feature set and to produce a small set of tests (especially boundary cases).
3. Run all tests across all implementations and rank test cases by **variability** (how many implementations disagree on the outcome).

High-variability tests don't prove the spec is ambiguous; the summaries might be the source of confusion. But in my experience, these tests are a **productive shortlist for human review**—pointers to language that could be tightened or examples that could be expanded. Instead of re-reading all 200 pages, I can focus on the five paragraphs that are tripping up multiple independent AI implementers.

---

### What to Keep (and What to Skip)

The goal is density, not just brevity. A good compressed artifact retains the interop-critical details.

* **Keep**: data shapes, message formats, allowed values, small algorithms, error conditions, and security notes.
* **Keep** (when it helps): short state/flow diagrams, lookup tables, minimal examples.
* **Skip or shrink**: long rationale, narrative history, and extended examples unless they’re essential.

Most importantly, **keep the breadcrumbs**. Every condensed piece of information should have a citation ([source: §X.Y]) back to the original spec so you can quickly jump to the normative text when an ambiguity arises.

### Light-touch Checks to Stay Honest

To keep the artifact faithful to the source without a formal verification process, I use a few quick, probabilistic checks:

* **Coverage Pulse.** Randomly sample normative sentences from the source (“MUST/SHALL/SHOULD”) and ask the model whether each has a paraphrased counterpart in the compressed artifact, with a correct section anchor.
* **Soundness Probe.** Ask the model to identify any obligations present in the compressed artifact that it *can’t* find in the source. If it flags one, I either add a citation or delete the line.
* **Round-trip Snippets.** Try to reconstruct a tricky paragraph from the original spec using only the compressed text. Failure is a signal to expand or clarify a section.

These are spot checks, not exhaustive proofs. They're designed to keep drift in bounds.

### Licensing and Intent

This compressed artifact is **not the standard**. It’s a convenience layer for developers and models, with citations back to the source. Standards Development Organizations (SDOs) have licensing constraints; respect them. Treat the artifact as working documentation, not a redistribution of normative text. Always link to and cite the official source.

---

### How to Try This Yourself: The Recipe

This workflow is adaptable to other specifications. Here is the minimal recipe and the full meta-prompt skeleton you can use as a starting point.

1. **Pick a spec** you know well and can legally quote for this purpose.
2. **Generate the Prompt Suite:** Use the meta-prompt skeleton below in a large-context model to generate your numbered "prompt suite."
3. **Execute the Suite:** In a new session with low temperature, run each prompt in order, concatenating the results into a single file.
4. **Pin and Build:** Pin the final artifact in your coding context and use it to generate code and tests.
5. **Stay Honest:** Use the light-touch checks (Coverage Pulse, Soundness Probe, Round-trip Snippets) to build confidence in the artifact's fidelity.
6. **(Optional) Find Ambiguity:** Generate a second artifact with a different model or seed. Build a second implementation and cross-run the test suites. The disagreements are your shortlist for human review.

Here is the meta-prompt skeleton you can adapt:

*(Then paste the full spec and let the model do the rest.)*

### What this isn't

It’s not a new spec format, not a claim of lossless compression, and not a replacement for editorial judgment. It’s a practical way to keep **enough** of a spec alive in the context window that implementation work becomes less brittle, enabling a new method for focusing human attention on the parts of a standard that need it most. The goal, as always, is fewer surprises at integration time and more time spent on the parts that matter.

#FHIR #HealthIT #Interoperability