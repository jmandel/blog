---
title: "How FHIR Resource.id Became a Special System.String"
date: 2026-05-20T14:22:00
added_at: 2026-10-06
slug: how-fhir-resource-id-became-a-special-system-string
original_url: "https://www.linkedin.com/pulse/how-fhir-resourceid-became-special-systemstring-josh-mandel-md-gylif"
linkedin_id: gylif
banner: ./banner.png
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7462872150975320064"
  share_id: "7462872150975320064"
  share_type: "ugcPost"
  posted_at: "2026-05-20T14:29:34"
  visibility: "MEMBER_NETWORK"
  commentary: |
    Increasingly, AI agents are the only way to understand the complex historical palimpsest of large specs and software, the design decisions that accrete, and the implementation and integration over time. This article is an example output produced by GPT-5.5 xhigh working with the tools in https://lnkd.in/dTdQP645, to help triage issues at the HL7 Working Group Meeting.  See article...
---

*Increasingly, AI agents are the only way to understand the complex historical palimpsest of large specs and software, the design decisions that accrete, and the implementation and integration over time. This post is an example produced by GPT-5.5 xhigh working with the tools in* [*jmandel/fhir-community-search*](https://github.com/jmandel/fhir-community-search)*.*

### Summary

The available history strongly suggests that became a special case by accident, or at least by an over-generalized implementation, rather than by a Resource.id-specific design decision.

The key change is in HL7 FHIR commit:

<https://github.com/HL7/fhir/commit/f9057f0d24ea74c20f09645e629827cca363d892>

That commit is tied to , now visible as Jira :

<https://jira.hl7.org/browse/FHIR-22493>

was about and , especially making derived datatype snapshots such as preserve the same "compiler magic" representation as . It was not about .

But the implementation changed the generator from special-casing only and to special-casing every path ending in :

That catches the intended derived datatype ids, but it also catches . This appears to be the origin of being represented as a special scalar instead of as a normal FHIR primitive .

### Tracker Provenance: GF vs Jira

refers to the old GForge tracker numbering. The issue appears to have been migrated into Jira as , preserving the numeric id.

Evidence:

* Jira contains with summary: "Type profiles derived from Element have incorrect for Element.id".
* explicitly references the old GForge URL with .
* The FHIR source commit uses the old label in .

So the issue is not lost, but the old GForge form is effectively superseded by the Jira issue.

### Baseline: FHIR-12060 Did Not Make Resource.id Special

Earlier issue / SVN dealt with and not really being normal elements.

Jira:

<https://jira.hl7.org/browse/FHIR-12060>

Applied commit:

<https://github.com/HL7/fhir/commit/e8c22a3727455852300b359fe317824ad3ae2224>

That commit carries:

The relevant generator code introduced an exact special case:

Important point: this exact code does **not** include .

There was a comment in asking whether the same idea might apply to , but the resolution and applied code were scoped to and .

### The Smoking Gun: FHIR-22493 Implementation Over-Generalized .id

was created in 2019. Its concern was that derived profiles/types from did not preserve the special type representation for inherited . For example, was being generated as an ordinary FHIR rather than carrying the same compiler-magic representation as .

The resolution was to repeat the base-profile extension in derived snapshots. Again, this is about inherited on datatypes, not about .

The implementing commit is:

<https://github.com/HL7/fhir/commit/f9057f0d24ea74c20f09645e629827cca363d892>

The commit message is broad:

Inside the same commit, adds the GF tracker entry:

But the actual generator change is broader than that tracker/history entry:

This change was suitable for , , and other datatype ids that inherit from . However, it also matches .

That is the apparent accidental step.

### What the Generalization Was Probably Trying to Do

The broad check was probably intended to cover inherited in generated snapshots. In FHIR, many structures inherit the common member. When generating snapshots for derived types, those paths do not appear literally as ; they appear as paths such as:

For those cases, the intended rule is reasonable: even though the path has changed, the element is still the inherited , so it should preserve the same special "compiler magic" representation rather than becoming an ordinary FHIR primitive.

The problem is that path suffix is not the right discriminator. also ends in , but it is not the inherited inter-element . It is the logical resource id used in RESTful URLs and has different semantics and lexical rules. A narrower implementation would have tested the base element, for example whether the generated element's base path is , instead of testing only whether the path text ends in .

### Why This Looks Accidental

The scope mismatch is clear:

* is about and derived type snapshots.
* The history entry says and .
* The implementation uses , which includes .
* There is no Resource.id-specific explanation in the commit message, history entry, or Jira issue.

If had been intentionally included, a more explicit implementation would likely have named it directly, or the tracker/history entry would have said so. Instead, the only visible Resource.id effect comes from the broad suffix test.

### Later Normalization to System.String + structuredefinition-fhir-type

On 2019-08-24, another commit changed the representation to the modern pattern:

<https://github.com/HL7/fhir/commit/97a9aa09b199cee3d929b60d413bdd714c6aff4d>

That commit preserved the broad test but changed the emitted type to a FHIRPath system type with a FHIR type extension:

At this point was still being caught by the over-broad test, and it was being labeled with .

This matches the R4.0.1 published artifact:

### Later Correction/Rationalization for Resource.id

After R4.0.1, people noticed that was now with . That led to later issues:

* : <https://jira.hl7.org/browse/FHIR-25262>
* : <https://jira.hl7.org/browse/FHIR-25274>
* : <https://jira.hl7.org/browse/FHIR-45989>

On 2019-12-30, commit changed the generator to distinguish resources:

<https://github.com/HL7/fhir/commit/7daa0d220d80bdaf2229f7aa05f4d4e6c0f5a698>

Relevant code:

This is the point where became with .

That later became the rationalized position: is conceptually a FHIR , but represented as so it does not have the normal primitive children and .

### Interpretation

The history supports this sequence:

1. intentionally special-cased and .
2. intended to preserve that special behavior in derived datatype snapshots such as .
3. Commit implemented that by checking all paths ending in .
4. That implementation unintentionally included .
5. Later tickets noticed the resulting shape and rationalized it by changing its from to .

The critical point is that the original ticket-backed scope did not require to become special. The source history and tracker scope point to an over-generalized implementation, not an explicit Resource.id design decision.

### Compact Statement

appears to have become as a side effect of the implementation. The tracker asked for compiler-magic behavior to be preserved on derived datatype snapshots; the implementation used , which also swept in . Later issues accepted and rationalized the result, but the origin looks accidental.