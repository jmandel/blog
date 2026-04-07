---
title: "Additional Resources\" in FHIR: problem & solution..."
date: 2025-09-24T14:57:27
slug: share-7376630854342598656
share_url: "https://www.linkedin.com/feed/update/urn:li:share:7376630854342598656"
share_type: "share"
share_id: "7376630854342598656"
visibility: "MEMBER_NETWORK"
---

Additional Resources" in FHIR: problem & solution...

R6 core must be stable and mostly normative, but some important parts are still evolving. Keeping them in core risks churn; removing them breaks implementations. Working Groups need a supported lane to iterate between releases without fragmenting the ecosystem.

## Solution: Additional Resources

An active development lane for resources/operations/pages not yet ready for core. Content remains official HL7 FHIR, canonicals stay under "http://hl7.org/fhir". It’s not a demotion: items are expected to progress, then either graduate to core (often normative) or retire.

## How the system works

Packaging: additional content is published in IG packages; your IG declares dependencies and the publisher/validator resolves them.
Referencing: an “allowed targets” extension declares which core/Additional elements may reference an Additional Resource (approved by the owning WG of the referencing element), and a compartment-membership extension states the compartment and the search/chained parameters that define membership. Prefer extensions over hard elements for optional cross-links; avoid blanket wildcards unless intentional.

Namespaces: Additional Resource definitions use the same "http://hl7.org/fhir" canonical namespace to keep resolution straightforward.

Governance flow: propose → incubate in an IG → prove maturity (use, tests, bindings) → graduate back to core or retire. FMG coordinates with intentionally light admin.

Compatibility: core references won’t break—consumers fetch the packages. Validation is being tuned for cross-IG references and the new extensions.

## Where it goes (by destination IG)

* API Incubator IG: GraphDefinition and $graph; lifecycle ops/pages ($current, $find); large-resource ops ($add, $remove, $filter); Async Bulk and Async Interactions pages; meta ops ($meta, $meta-add, $meta-delete) pending Security WG.
* Testing IG: TestScript, TestPlan, TestReport, and testing narrative. Core keeps a brief overview pointing here.
* Subscriptions Backport IG: subscription extras (e.g., $get-ws-binding-token) with widened version coverage.
* Feature Capabilities IG: capability helpers ($implements, $conforms, $subset) and the “subset” page.
* Topic IGs (e.g., SDC): mature topical homes such as $questionnaire → SDC.

## What stays in core (examples)

The Requirements resource remains and proceeds to Normative. Pages are scrubbed and clearly marked Normative or Informative; Trial-Use narrative is removed from core.

## Practical impact

* Add package dependencies when you use moved content (API Incubator, Testing, Feature Capabilities, Subscriptions Backport, SDC as needed).
* Canonicals stay the same; ensure your tooling fetches/resolves those packages.
"* Use the allowed-targets and compartment extensions; avoid broad targetProfile of "*" unless that’s truly intended.
