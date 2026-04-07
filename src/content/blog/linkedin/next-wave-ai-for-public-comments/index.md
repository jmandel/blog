---
title: "Next Wave: AI for Public Comments"
date: 2025-08-16T17:18:00
slug: next-wave-ai-for-public-comments
original_url: "https://www.linkedin.com/pulse/next-wave-ai-public-comments-josh-mandel-md-l2a0c"
linkedin_id: l2a0c
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7362539596817051648"
  share_id: "7362539596817051648"
  share_type: "ugcPost"
  posted_at: "2025-08-16T17:43:49"
  visibility: "MEMBER_NETWORK"
  commentary: |
    I built FloodGate as an open-source prototype to explore the double-edged sword of AI in advocacy: its power to supercharge a real supporter's ability to be heard, versus its potential to be weaponized for anonymous spam that overwhelms the entire process.
---

### The Problem with Form Letters

In [prior work](/blog/posts/how-to-read-10000-pages-of-public-comments), I built a tool to analyze thousands of public comments. A core feature is a simple clustering algorithm that groups nearly identical submissions. This is crucial for dealing with "form letter" campaigns, where thousands of people submit the same templated text. By clustering them, analysts can understand the scale of a coordinated campaign without letting its sheer volume drown out all other unique, individual comments.

This works perfectly for yesterday's campaigns. But it's about to become obsolete.

The fundamental challenge for any advocacy campaign is a paradox: they need to mobilize a large number of supporters to voice a consistent message, but if all those voices are identical, they risk being dismissed as a single, orchestrated bloc. How can a campaign empower thousands of real, individual supporters to be heard uniquely, ensuring their comments stand out and are counted?

### FloodGate: From Comment Spam to Comment Supercharger

This is where AI changes the game. I built [**FloodGate**](http://joshuamandel.com/regulations.gov-comment-browser/floodgate/)—a proof-of-concept tool—to explore this new frontier.

Initially, one might see such a tool as a way to generate spam. But the more potent, and more complex, use case isn't about creating fake comments from scratch. It's about giving a "supercharger" to real supporters.

Imagine a campaign provides a tool like FloodGate to its mailing list. A supporter—a real person who genuinely cares about the issue but may not have the time, expertise, or confidence to write a detailed regulatory comment—can now:

1. **Choose core arguments** they agree with.
2. **Add their own personal story** and details.
3. **Customize the style and tone** to match their preferences.

With one click, the tool generates a high-quality, unique public comment prompt that accurately reflects their views, incorporates their personal experience, and is aligned with the campaign's key objectives. The supporter reads it, agrees with it, and submits it under their own name. This is not a fake comment; it's an AI-assisted, authentic expression of a real person's view.

The entire engine of a FloodGate campaign is driven by a **single, comprehensive JSON configuration file**. This file acts as the campaign's strategic playbook, meticulously defining every variable needed to generate thousands of unique comments. Inside this JSON, you'll find definitions for diverse commenter personas (like 'Early Childhood Educator' or 'Concerned Parent'), multi-dimensional arguments (categorized as legal, moral, and practical), and distinct writing styles (from 'Professional and Formal' to 'Passionate and Emotional'). It even contains a fact bank with specific statistics and legal citations that can be woven into the text. This structure allows any campaign, on any issue, to create its own unique comment generation system by authoring a new JSON file. The definitive blueprint for creating such a file is publicly available in the project's [TypeScript definitions](https://github.com/jmandel/regulations.gov-comment-browser/blob/main/floodgate/floodgate-types.ts). This schema acts as a detailed instruction manual, outlining every required field and data structure needed to build a robust and sophisticated campaign from the ground up.

### The "Spy-vs-Spy" Arms Race

This is where the cat-and-mouse game begins.

**The Campaign's Offensive Move:** By using a tool like FloodGate, a campaign can generate thousands of comments that are all conceptually related but textually unique. The campaign's message is delivered with the perceived weight of a massive, organic, and diverse groundswell of public opinion. Their supporters' voices are not just heard; they are amplified and made resistant to simplistic dismissal.

**The Analyst's Defensive Counter-Move:** On the receiving end, analysts will realize that text-surface similarity is no longer a reliable indicator of a coordinated campaign. They must escalate their methods. The new challenge is to detect the "conceptual DNA" shared across thousands of unique texts. This requires much more sophisticated techniques:

* **Vector Embeddings:** Comments are converted into numerical representations (vectors) in a high-dimensional space.
* **Semantic Clustering:** Algorithms then group comments that are thematically and conceptually similar, even if they use completely different wording.

The goal shifts from finding copy-pastes to identifying orchestrated *ideas*. In the medium term, this shift probably forces higher-quality anaylsis.

### Blurring Lines of Authenticity and Astroturfing

This dynamic creates a fascinating and troubling gray area. Is a comment generated by FloodGate and submitted by a real person "authentic"?

* **The argument for "Yes":** The person agrees with the sentiment, provided their personal details, and gave final approval. The AI is just a powerful writing assistant, like a more advanced Grammarly. It helps citizens overcome barriers to participation and articulate their views more effectively.
* **The argument for "No":** The core arguments, narrative structure, and rhetorical strategies were designed by the campaign and executed by an AI. The supporter is merely personalizing a centrally controlled message. It's a form of high-tech astroturfing that launders an organized campaign into the appearance of a spontaneous public uprising.

The long-held practice of allowing anonymous or pseudonymous comments in the federal system further complicates this. Without strong identity verification, the analysis of the text itself becomes the primary tool for understanding the landscape of public opinion, putting even more pressure on the "spy-vs-spy" dynamic.

### Where Do We Go From Here?

FloodGate is a demonstration tool built to spark this exact conversation. The flood of AI-assisted content is coming, and we need to be prepared.

1. **Acknowledge the New Reality:** Simple clustering of form letters is over. Comment analysis requires investment in AI-powered semantic and network analysis tools.
2. **Push for Transparency:** Perhaps the solution isn't to ban these tools, but to embrace them with transparency. A simple "This comment was written with AI assistance" disclosure could allow individuals to use these tools while giving analysts the context they need.
3. **Redefine "Meaningful" Input:** Agencies may need to develop new heuristics for weighing comments. A thoughtful, unique comment written by an individual from scratch might be weighed differently than a high-quality, AI-assisted comment that shares conceptual DNA with thousands of others.

The goal of public comment is to inform governance. As technology changes *how* the public comments, we must adapt our methods for listening. The game has changed. The question now is how both sides will play it.

*You can* [*explore the live FloodGate proof-of-concept*](http://joshuamandel.com/regulations.gov-comment-browser/floodgate/) *or check out the* [*source code*](https://github.com/jmandel/regulations.gov-comment-browser/tree/main/floodgate)*. Generate a few comments. See how different they are. Now, imagine you're reading a whole pile of these :-)*