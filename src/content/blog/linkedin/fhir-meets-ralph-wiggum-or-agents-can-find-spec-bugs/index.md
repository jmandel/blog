---
title: "FHIR meets Ralph Wiggum (or: Agents Can Find Spec Bugs!)"
date: 2026-01-28T20:12:00
slug: fhir-meets-ralph-wiggum-or-agents-can-find-spec-bugs
original_url: "https://www.linkedin.com/pulse/fhir-meets-ralph-wigugm-agents-can-find-spec-bugs-josh-mandel-md-gnd5c"
linkedin_id: gnd5c
banner: ./banner.jpg
---

### The Hype

The "Ralph Wiggum loop" went viral in early 2026. Named after the Simpsons character, the idea is dead simple: run an AI agent in a loop until done, reset context each session, preserve progress externally. Plugins spawned. Twitter argued about token costs.

I was skeptical. Then I watched Claude Opus 4.5 write its own regex engine with backtracking support just to pass a FHIRPath test, and I thought: there's something here.

The best part? I vibe-coded my own tooling in an afternoon. No plugins, no frameworks. Just a few Python scripts and a methodology doc. If you understand the core idea, you can do this yourself.

### The Core Insight: Self-Healing Through Variety

On open-ended projects, agents get stuck. They repeat mistakes. They go down rabbit holes.

So I built five modes, choosing one randomly each session:

* **EXPLORE**: Find gaps. Mine test failures. Write new tests.
* **DEVELOP**: Fix one failing test. Minimal change. Ship it.
* **CONFIRM**: Review tests against the spec. Catch our own mistakes.
* **FIX\_BUG**: Work the backlog. Agents file bugs for other agents.
* **CROSS\_CHECK**: Compare against reference engines. Adjudicate disagreements.

The magic is in the mix. Stuck in DEVELOP? An EXPLORE session finds a different angle. Made a mistake? CONFIRM catches it before it compounds. Filed a bug you couldn't fix? FIX\_BUG picks it up later.

Randomization prevents ruts. Variety provides self-healing.

### The Tools

We built five scripts that make this work:

— Weighted random selection. More bugs? Higher chance of FIX\_BUG. Unreviewed tests? More CONFIRM. Always 15% minimum for each mode.

— Agents file bugs they can't fix now. Other agents fix them later. Severity weights influence selection.

— Track spec bugs and test errors to report to HL7. Because sometimes the official tests are wrong.

— Test any expression against fhirpath.js, Firely .NET, and HAPI FHIR:

— Smart sampling. Fast engines find disagreements in 3 seconds. Slow engine (HAPI, 22s startup) only runs on samples.

That's it. Python scripts calling CLIs. No magic.

### Git Is Memory

Every session commits. Success or failure. The agent's context resets, but progress accumulates in the repo.

This is crucial. Agents don't remember previous sessions. But they can read the tests they wrote, the bugs they filed, the TODOs they left. State lives in files, not in context windows.

### LLMs Find Spec Bugs

Here's what surprised me most: agents implementing specs also find bugs in them.

Example: The FHIRPath spec says "returns the same type as the value in the input collection." So (a Date) through should return a Date. But the official R5 tests expect .

That's a bug in the test suite. We filed it upstream.

When you have three reference implementations, a detailed spec, and official tests, disagreements surface constantly. Sometimes we're wrong. Sometimes fhirpath.js is wrong. Sometimes the tests are wrong.

This is the best kind of community contribution: not just consuming specs, but pressure-testing them.

### Multi-Engine Adjudication

When engines disagree, we don't just pick one. We built an evidence hierarchy:

1. Explicit spec text with examples (strongest)
2. Official tests with matching cases
3. Multiple engines agreeing
4. Spec text requiring interpretation
5. Single engine behavior (weakest)

And we allow honest uncertainty. Verdicts include and . The methodology tells agents: "Document what you know, what you don't, and why you chose what you chose."

### Results

* Started at **21%** R5 pass rate
* Now at **86%** (897/1033 tests)
* Artisinal tests: **96%** (1624/1675)
* 38 adjudications completed
* 11 bugs filed to backlog
* Multiple upstream issues for HL7

All from agents running in loops, picking random modes, committing their work.

### Why It Works

**Bounded sessions prevent rabbit holes.** One task, one commit, done.

**Multiple modes self-heal.** Different angles, different progress.

**Git preserves everything.** Context resets, progress doesn't.

**Spec beats engines.** When they disagree, read the source.

**Uncertainty is allowed.** Not everything has a clean answer.

### The Skeptic's Take

Is it token-efficient? No. Agents retry, backtrack, and occasionally write regex engines from scratch.

Is it reliable? Mostly. CONFIRM catches many errors. Not all.

Is it the future? Probably not, but it's great for January 2026. But for spec-driven work where correctness is verifiable, it's remarkably effective. And the specs-bugs angle is genuinely valuable—knowledge that flows back upstream.

You don't need anyone's plugin. Just a loop, a methodology, and some scripts.

---

*fhirpath.zig is open source. Methodology and tools in* [*https://github.com/jmandel/fhirpath.zig/tree/main/wiggum*](https://github.com/jmandel/fhirpath.zig/tree/main/wiggum)