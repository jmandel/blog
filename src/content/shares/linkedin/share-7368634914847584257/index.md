---
title: "Task isolation, not “multi-agent magic”"
date: 2025-09-02T13:24:26
slug: share-7368634914847584257
share_url: "https://www.linkedin.com/feed/update/urn:li:share:7368634914847584257"
share_type: "share"
share_id: "7368634914847584257"
visibility: "MEMBER_NETWORK"
---

Task isolation, not “multi-agent magic”

I appreciated this preprint’s focus on measuring accuracy, latency, and token growth under mixed clinical workloads. That’s useful. But the central claim (~"orchestrated multi-agents beat a single agent at clinical scale") rests on a baseline that doesn’t reflect real practice. 

In the single-agent condition, the model processes up to 80 unrelated tasks in one shared context. In production, teams don’t do that. We isolate each task into its own API call or job and aggregate results (fan-out/fan-in). That standard pattern prevents cross-task interference by design. In other words, most of the reported gains are from task isolation, not from a novel AI architecture.

The paper’s Methods describe the shared-context baseline ("one language model received the full batch of N tasks and up to 10×N turns"), and Figure 1 depicts the orchestrator that simply restores per-task isolation; Figure 2 then shows the expected accuracy/token divergence once isolation is reintroduced. These are informative measurements, but the novelty should be framed as empirical validation of context isolation under load, not as a breakthrough in multi-agent intelligence.

What would strengthen the paper:

* Compare against a per-task, single-call baseline (N isolated prompts + fan-in). Control for equal token budgets and identical tools

"Two things can be true: the measurements are helpful, and the baseline choice overstates the architectural claim.
