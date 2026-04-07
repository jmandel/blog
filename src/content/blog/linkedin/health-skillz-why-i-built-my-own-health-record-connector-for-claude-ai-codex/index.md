---
title: "Health Skillz: Why I Built My Own Health Record Connector for Claude.ai & Codex"
date: 2026-01-13T03:33:00
slug: health-skillz-why-i-built-my-own-health-record-connector-for-claude-ai-codex
original_url: "https://www.linkedin.com/pulse/health-skillz-why-i-built-my-own-record-connector-codex-mandel-md-mlz3c"
linkedin_id: mlz3c
banner: ./banner.jpg
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7416687199552720896"
  share_id: "7416687199552720896"
  share_type: "ugcPost"
  posted_at: "2026-01-13T03:47:03"
  visibility: "MEMBER_NETWORK"
  commentary: |
    Today I built "Health Skillz": a health connector for Claude.ai and other Skills-aware agents. Read on for my early experience with TEFCA onramps... and why I took a different approach to just get a thick stack of FHIR JSON + plaintext SOAP notes into the agent's computational sandbox and get out of the way
---

***TL;DR:*** *I built* [***Health Skillz***](https://github.com/jmandel/health-skillz)*, a Claude Skill that fetches your health records directly from your patient portal using SMART on FHIR. It pulls all your structured data (labs, meds, conditions) plus the full text of clinical notes, encrypts everything end-to-end, and lets Claude analyze it. To try it:* [***download the skill***](https://health-skillz.joshuamandel.com/skill.zip)*, upload to Claude (Settings → Capabilities, Skills), and ask Claude to look at your health records. Test with Epic sandbox or with your real data (currently Epic-only).*

In the run-up to this week's JPM conference, both OpenAI and Anthropic announced health record connectors and analysis product areas, each working with a different startup to provide the connectors. I was excited to try them. I'm still on OpenAI's wait-list; my initial experience with Anthropic's was frustrating.

Briefly: After verifying my identity through Clear, no matches were found to my records. This despite the fact that I have records at multiple health systems here in the same state where my driver's license was issued. When I tried connecting to providers manually, I needed my portal username and password for each -- some I had, some I needed to reset. When I completed the connections, I saw "forever spinners" and failed redirects. The data manifest that eventually appeared seemed to be missing the actual clinical note text from my visits (I'm hoping to learn more about whether this is the case, but I don't have enough visibility into the details to tell). After receiving a "success" email from Anthropic listing the data received, Claude remained unable to query it. [Here's the puzzling transcript](https://claude.ai/share/5d7b646f-bef2-4a31-ab50-6b52d32e5304).

### The TEFCA Detour

Both the OpenAI and Anthropic connectors are offered by startups investing in TEFCA (Trusted Exchange Framework and Common Agreement) rails. I've been following TEFCA closely, and I co-authored [a paper in JMIR](https://www.jmir.org/2022/11/e41750/) advocating for patient autonomy principles in its design. The framework has worthy goals: reduce fragmentation, enable nationwide query-based exchange, give patients access to their records across sites of care.

But individual facing record location services expose serious challenges.

**Identity verification tax.** TEFCA requires identity proofing up front, with the expectation that a Record Locator Service (RLS) will then find your records across providers automatically. In my case, RLS returned nothing, even for records in my home state from which my driver's license was issued. And I *still* needed my portal username and password to actually authorize access. You're paying an identity verification tax for a discovery service that doesn't reliably work. Worst of both worlds.

**No room for builders.** Here's what frustrates me most: as a solo developer, I can build a SMART on FHIR app in a day and run it against real health systems for myself and friends/family. I've been doing this for years.

I can't do this with TEFCA. The framework requires apps to be vetted by "Qualified Health Information Networks" (QHINs). There's no path for tinkerers, hobbyists, or patients solving their own problems with software. The underlying protocols don't give real consideration to putting power in patients' hands—it's all about companies running "trusted" services as intermediaries.

In the JMIR paper, we proposed three principles for TEFCA:

1. Patients can query for data about themselves
2. Patients can know when their data are queried and shared
3. Patients can configure what is shared about them

TEFCA launched without meaningfully addressing (2) or (3), and the technical approaches to (1) leave aside a significant class of patient-tinkerers (or require trust in a new breed of services that sit outside of HIPAA). Patients can't see which participants hold their records. Can't see who's queried for their data. Can't configure sharing preferences. The "individual access" pathway exists but requires going through yet another intermediary.

### Building with SMART on FHIR

So I built [**Health Skillz**](https://github.com/jmandel/health-skillz): a Claude(-style) Skill for fetching and analyzing health records, using SMART on FHIR.

SMART on FHIR isn't perfect. You need to register your app with each EHR vendor separately, which limits reach. But within a vendor's ecosystem, it can be powerful: OAuth 2.0 + FHIR, battle-tested for a decade. Patients sign into their portal, authorize access, and data flows directly to the app. No intermediaries, no identity proofing gauntlet, no RLS that returns nothing.

My implementation currently supports Epic only (not because of technical limitations, but because that's where my own records are). This is the tinkerer's philosophy: I built what I could test myself. The same code could expand to other vendors; the SMART on FHIR protocol is standardized.

### What's Different About Health Skillz?

### Full Data Sync, No Limits

When you connect a provider, you get *everything*: all FHIR resources across all pages, all clinical documents, all attachments. No artificial caps. The corporate connectors presumably impose limits to control costs or simplify engineering, but today's AI models do very well when they can explore in depth.

### Clinical Notes as Text

The most valuable part of health records is often the free-text clinical notes. The "Assessment and Plan" where your doctor explains what's actually going on. A medication list doesn't tell you *why* something was prescribed. Lab values mean different things in different contexts.

Health Skillz extracts text from HTML, RTF, and XML documents automatically. You get both the extracted plaintext (for easy searching) and the original format.

### End-to-End Encryption

Your health data never touches the Health Skills server in plaintext. The AI agent generates an ECDH keypair, data is encrypted in your browser with AES-256-GCM, and only the agent can decrypt it. The server sees only ciphertext.

### You Own Your Data

After connecting, you can download a complete JSON export. It's your data. You should be able to keep it, inspect it, verify it's complete.

### Agent-Driven Analysis

Here's a key philosophical difference: **the AI should inspect your data, not blindly process it.**

When you ask Claude about your health records, it shouldn't generate a JavaScript artifact that runs analysis in a sandbox you can't see. Instead, it should:

1. Download the data into its computational environment
2. Write code to explore the structured FHIR resources
3. Read clinical notes in full where relevant
4. Use judgment to identify what's clinically significant
5. Iterate and refine its understanding
6. Synthesize a thoughtful answer

An AI that can see intermediate results, catch its own errors, and apply reasoning will give you better answers than one executing blind analysis.

### How It Works

The architecture:

### Try It

1. Install the skill: [Download](https://health-skillz.joshuamandel.com/skill.zip) [health-record-assistant.zip](http://health-record-assistant.zip)
2. Upload to Claude: Settings → Skills
3. Ask Claude to analyze your health records

For testing, Epic's sandbox credentials:

* Username: fhircamila
* Password: epicepic1

Source: [github.com/jmandel/health-skillz](http://github.com/jmandel/health-skillz)

### The Bigger Picture

I'm not saying TEFCA will never work. The goals are good. But the implementation prioritized institutional convenience over patient empowerment, and the technology isn't ready.

Meanwhile, SMART on FHIR works today. It puts patients in control. It lets solo developers build and ship. It doesn't require intermediaries or identity verification gauntlets for access to your own data.

The corporate connectors will improve. But there's something to be said for the indie approach: small, focused, no intermediaries, patient in control. I built Health Skillz in a weekend because the standards let me.

That's what SMART on FHIR was designed to unlock. It's a shame to see it bypassed for infrastructure that isn't ready—especially when the result is worse UX, missing data, and failed queries.

---

*Health Skillz is open source and not affiliated with Anthropic, OpenAI, Epic, or any healthcare provider. I work at Microsoft but this is a personal project.*