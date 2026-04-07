---
title: "POWER USER FEEDBACK DROVE MAJOR HEALTH SKILLZ IMPROVEMENTS THIS WEEK"
date: 2026-02-10T15:57:35
slug: share-7427017898310856704
share_url: "https://www.linkedin.com/feed/update/urn:li:share:7427017898310856704"
share_type: "share"
share_id: "7427017898310856704"
visibility: "MEMBER_NETWORK"
---

POWER USER FEEDBACK DROVE MAJOR HEALTH SKILLZ IMPROVEMENTS THIS WEEK

The last week has been a great stress test.

Early power users like Hugo Campos, James Cummings, Dave deBronkart pushed Health Skillz (https://lnkd.in/dTRTsUGR) with large records. That pressure surfaced bottlenecks, and I shipped fixes or speed and reliability.

UPDATE

Health Skillz should now work in the public Claude.ai web environment for the large real-world cases tested this week, including records that were previously painful or stalled out.

WHAT WE CHANGED

The recent changes made data transfer smaller, faster, and more resilient:

- Large record sessions that used to fail now complete more reliably
- Browser-side failures now have clearer recovery paths for users
- Data arrives faster in the analysis environment, especially for bigger records
- Interrupted transfers are less likely to force a full restart
- Debugging is faster when something goes wrong
- Performance improvements can now be validated with repeatable synthetic datasets

WHAT WORKS IN PRACTICE

There is now a workable path in the public web harness, but it requires respecting platform constraints.

Example:

- Directly uploading a ZIP >30MB fail due to file-size limits.
- Downloading is limited to 1.5MB/s per connection by Claude.ai proxy
- We avoid both limits by using agent-triggered web flow with direct parallelized download into the sandbox

With those constraints handled correctly, the browser path is much better than it was.

LOCAL STILL WINS

For people with very large records and repeated heavy analysis, local harnesses are still the best option:

- Better sustained throughput
- Fewer file-size bottlenecks
- More control over long-running workflows and local files

So this is not either/or.

- Web harness: now broadly workable for real-world use, with major recent improvements
- Local harness: best for the biggest and most demanding workflows

TOOL LINKS

Claude Code (CLI): https://lnkd.in/dPAYPPyG
Codex CLI: https://lnkd.in/d5ri_p_p
Claude Cowork (GUI): https://lnkd.in/dZa2WfFv
Codex App (GUI): https://lnkd.in/dTFfyJ8N

Note: the GUI experiences above are currently macOS-first / effectively macOS-only right now. CLI paths are currently the broadest option for advanced users.

WHAT'S NEXT

"This week showed the model: power users push limits, rapid iteration follows, and the system gets better for everyone :-)
