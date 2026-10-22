---
title: "2026 AI Agents vs. 2022 FHIR Compliance"
date: 2026-10-22T10:00:00-05:00
added_at: 2026-10-22
slug: an-ai-agent-connects-health-skillz-to-eclinicalworks
banner: ./banner.png
original_url: https://www.linkedin.com/pulse/2026-ai-agents-vs-2022-fhir-compliance-josh-mandel-md-wr4hc/
linkedin_id: wr4hc
supersedes_linkedin: https://www.linkedin.com/pulse/2026-ai-agents-vs-2022-fhir-compliance-josh-mandel-md-wr4hc/
---

I built <a href="https://www.linkedin.com/pulse/health-skillz-why-i-built-my-own-record-connector-codex-mandel-md-mlz3c" title="Original Health Skillz article on LinkedIn">Health Skillz</a> to connect to EHRs via SMART on FHIR, but since all my own records are in Epic, I’d never bothered registering or testing it elsewhere.

Then a colleague wanted to pull her records from eClinicalWorks. I pointed GPT-6 Astra at the eCW developer portal and asked it to register an account, create an app, wire up the integration, and test it against their sandbox. I just fed it email and SMS verification codes when prompted.

![GPT-6 Astra iterates through registration, coding, deployment, and testing. Its workarounds add client-secret authentication, a stateless relay, and vendor-specific search behavior. After deployment, patient records flow through the relay between Health Skillz in the browser and eClinicalWorks.](./agent-integration.png)

The original federal deadline for rolling out these certified FHIR APIs was the [end of 2022](https://healthit.gov/blog/interoperability/achieving-a-major-milestone-health-it-developers-certify-to-cures-update/).

Watching the agent work through the integration exposed three classic EHR interoperability headaches—and showed how good agents have become at routing around them:

## 1. No CORS support on the FHIR APIs.

Pure in-browser SMART apps that talk directly to the EHR have been a core pattern since we demoed the [Pediatric Growth Chart in 2014](https://fhirblog.com/2014/08/02/smart-on-fhir-part-1/). Because [eCW doesn't set CORS headers](https://connect4.healow.com/apps/jsp/dev/r4/apiDocumentation.jsp#patientAsymmetricSection), browser apps fail out of the box. Astra worked around this by standing up a small, stateless relay to proxy the requests. I hate having to do this: the privacy model is much cleaner when a patient’s data flows straight from the EHR to their browser without touching an intermediary server. eCW’s missing headers force an unnecessary trust relationship.

## 2. Broken asymmetric auth registration.

Astra first registered a JWKS URL for asymmetric client authentication. Then I received what looked like an automated email saying URLs outside certain categories would need network whitelisting, typically taking 2–3 business days, with no notification when it was done. It named categories like “Computer & Technology” and “Healthcare and Medicine,” but didn’t say which category our URL was in or whether we were waiting for review.

Astra’s access-token request, authenticated with a signed JWT, failed with `401 invalid_client`. I then asked Astra to submit the JWKS directly so we could keep moving. It checked the registration form, the existing-app editor, and the portal’s JavaScript for saving JWKS settings, but couldn’t find a way to do it. The [SMART spec requires servers to support both](https://hl7.org/fhir/smart-app-launch/STU2/client-confidential-asymmetric.html#registering-a-client), and ONC tests asymmetric auth under [AUT-PAT-30](https://healthit.gov/test-method/standardized-api-for-patient-and-population-services-acb-atl/).

So I had Astra register a separate client using a symmetric client secret. That went through immediately. Another security and architectural downgrade we shouldn't have had to make.

## 3. Hard failures on `_count`.

Once auth worked, the `Patient` read succeeded, but almost every resource search failed with an HTTP 400: `"Unsupported query parameter(s): _count. These parameters are not allowed."` [`_count` is a standard FHIR parameter for page size](https://hl7.org/fhir/R4/search.html#count). FHIR R4 allows smaller result pages and [recommends ignoring unsupported parameters](https://hl7.org/fhir/R4/search.html#errors). eCW instead rejects the entire search. Astra inspected the error, added a vendor flag to strip `_count` for eCW, and relied on the server's pagination links instead.

After deploying those fixes, Astra pulled 112 resources and four attachments from the sandbox, verified state persistence across page reloads, and tested token refreshes.

My colleague tried it against her live patient portal, and it worked on the first try.

It’s maddening that in 2026, connecting to a certified, "standards-based" API still requires a custom proxy, downgraded client auth, and per-vendor query flags. The silver lining is that an agent can now click through the registration portal, hit those walls, read the error logs, write the workarounds, and ship a working integration in a single session.
