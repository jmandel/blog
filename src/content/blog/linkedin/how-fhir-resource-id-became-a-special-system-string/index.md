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

The available history strongly suggests that Resource.id became a System.String special case by accident, or at least by an over-generalized implementation, rather than by a Resource.id-specific design decision.

The key change is in HL7 FHIR commit:

<https://github.com/HL7/fhir/commit/f9057f0d24ea74c20f09645e629827cca363d892>

That commit is tied to GF#22493, now visible as Jira FHIR-22493:

<https://jira.hl7.org/browse/FHIR-22493>

FHIR-22493 was about Element.id and Extension.url, especially making derived datatype snapshots such as string.id preserve the same "compiler magic" representation as Element.id. It was not about Resource.id.

But the implementation changed the generator from special-casing only Element.id and Extension.url to special-casing every path ending in .id:

```
- } else if (Utilities.existsInList(path, "Element.id", "Extension.url")) {
+ } else if (Utilities.existsInList(path, "Element.id", "Extension.url") || path.endsWith(".id")) {
```

That catches the intended derived datatype ids, but it also catches Resource.id. This appears to be the origin of Resource.id being represented as a special scalar instead of as a normal FHIR primitive id.

### Tracker Provenance: GF vs Jira

GF#22493 refers to the old GForge tracker numbering. The issue appears to have been migrated into Jira as FHIR-22493, preserving the numeric id.

Evidence:

* Jira contains FHIR-22493 with summary: "Type profiles derived from Element have incorrect <type> for Element.id".
* FHIR-22670 explicitly references the old GForge URL with tracker\_item\_id=22493.
* The FHIR source commit uses the old GF#22493 label in source/history.html.

So the issue is not lost, but the old GForge form is effectively superseded by the Jira issue.

### Baseline: FHIR-12060 Did Not Make Resource.id Special

Earlier issue FHIR-12060 / SVN build@14528 dealt with Element.id and Extension.url not really being normal elements.

Jira:

<https://jira.hl7.org/browse/FHIR-12060>

Applied commit:

<https://github.com/HL7/fhir/commit/e8c22a3727455852300b359fe317824ad3ae2224>

That commit carries:

```
git-svn-id: http://gforge.hl7.org/svn/fhir/trunk/build@14528 ...
```

The relevant generator code introduced an exact special case:

```
} else if (Utilities.existsInList(path, "Element.id", "Extension.url")) {
  TypeRefComponent tr = ce.addType();
  tr.getFormatCommentsPre().add("Note: primitive values do not have an assigned type. e.g. this is compiler magic. XML,\r\n    JSON and RDF types provided by extension");
  tr.getCodeElement().addExtension("http://hl7.org/fhir/StructureDefinition/structuredefinition-json-type", new StringType("string"));
  tr.getCodeElement().addExtension("http://hl7.org/fhir/StructureDefinition/structuredefinition-xml-type", new StringType("xsd:string"));
  tr.getCodeElement().addExtension("http://hl7.org/fhir/StructureDefinition/structuredefinition-rdf-type", new StringType("xsd:string"));
  if (path.equals("Extension.url"))
    tr.getCodeElement().addExtension("http://hl7.org/fhir/StructureDefinition/regex", new StringType(Constants.URI_REGEX));
}
```

Important point: this exact code does **not** include Resource.id.

There was a comment in FHIR-12060 asking whether the same idea might apply to Resource.id, but the resolution and applied code were scoped to Element.id and Extension.url.

### The Smoking Gun: FHIR-22493 Implementation Over-Generalized .id

FHIR-22493 was created in 2019. Its concern was that derived profiles/types from Element did not preserve the special type representation for inherited Element.id. For example, string.id was being generated as an ordinary FHIR string rather than carrying the same compiler-magic representation as Element.id.

The resolution was to repeat the base-profile extension in derived snapshots. Again, this is about inherited Element.id on datatypes, not about Resource.id.

The implementing commit is:

<https://github.com/HL7/fhir/commit/f9057f0d24ea74c20f09645e629827cca363d892>

The commit message is broad:

```
Update for R5 code fixes to snapshot generator, validator and FHIRPath engine. Update FHIRPath expressions for changes
```

Inside the same commit, source/history.html adds the GF tracker entry:

```
<li><!-- GF#22493 -->Fix how the type of Element.id and Extension.url is defined in the generated StructureDefinitions</li>
```

But the actual generator change is broader than that tracker/history entry:

```
- } else if (Utilities.existsInList(path, "Element.id", "Extension.url")) {
+ } else if (Utilities.existsInList(path, "Element.id", "Extension.url") || path.endsWith(".id")) {
    TypeRefComponent tr = ce.addType();
    tr.getFormatCommentsPre().add("Note: special primitive values do not have an assigned type. e.g. this is compiler magic. XML, JSON and RDF types provided by extension");
    if (path.equals("Extension.url")) {
      tr.getCodeElement().addExtension("http://hl7.org/fhir/StructureDefinition/structuredefinition-json-type", new StringType("string"));
      tr.getCodeElement().addExtension("http://hl7.org/fhir/StructureDefinition/structuredefinition-xml-type", new StringType("xsd:anyUri"));
      tr.getCodeElement().addExtension("http://hl7.org/fhir/StructureDefinition/structuredefinition-rdf-type", new StringType("xsd:anyUri"));
      tr.getCodeElement().addExtension("http://hl7.org/fhir/StructureDefinition/regex", new StringType(Constants.URI_REGEX));
    } else {
      tr.getCodeElement().addExtension("http://hl7.org/fhir/StructureDefinition/structuredefinition-json-type", new StringType("string"));
      tr.getCodeElement().addExtension("http://hl7.org/fhir/StructureDefinition/structuredefinition-xml-type", new StringType("xsd:string"));
      tr.getCodeElement().addExtension("http://hl7.org/fhir/StructureDefinition/structuredefinition-rdf-type", new StringType("xsd:string"));
    }
}
```

This change was suitable for string.id, boolean.id, and other datatype ids that inherit from Element.id. However, it also matches Resource.id.

That is the apparent accidental step.

### What the Generalization Was Probably Trying to Do

The broad path.endsWith(".id") check was probably intended to cover inherited Element.id in generated snapshots. In FHIR, many structures inherit the common Element.id member. When generating snapshots for derived types, those paths do not appear literally as Element.id; they appear as paths such as:

```
string.id
boolean.id
HumanName.id
Address.id
BackboneElement.id
Patient.contact.id
```

For those cases, the intended rule is reasonable: even though the path has changed, the element is still the inherited Element.id, so it should preserve the same special "compiler magic" representation rather than becoming an ordinary FHIR string primitive.

The problem is that path suffix is not the right discriminator. Resource.id also ends in .id, but it is not the inherited inter-element Element.id. It is the logical resource id used in RESTful URLs and has different semantics and lexical rules. A narrower implementation would have tested the base element, for example whether the generated element's base path is Element.id, instead of testing only whether the path text ends in .id.

### Why This Looks Accidental

The scope mismatch is clear:

* FHIR-22493 is about Element.id and derived type snapshots.
* The history entry says Element.id and Extension.url.
* The implementation uses path.endsWith(".id"), which includes Resource.id.
* There is no Resource.id-specific explanation in the commit message, history entry, or Jira issue.

If Resource.id had been intentionally included, a more explicit implementation would likely have named it directly, or the tracker/history entry would have said so. Instead, the only visible Resource.id effect comes from the broad suffix test.

### Later Normalization to System.String + structuredefinition-fhir-type

On 2019-08-24, another commit changed the representation to the modern pattern:

<https://github.com/HL7/fhir/commit/97a9aa09b199cee3d929b60d413bdd714c6aff4d>

That commit preserved the broad .id test but changed the emitted type to a FHIRPath system type with a FHIR type extension:

```
} else if (Utilities.existsInList(path, "Element.id", "Extension.url") || path.endsWith(".id")) {
  TypeRefComponent tr = ce.addType();
  tr.getFormatCommentsPre().add("Note: special primitive values have a FHIRPath system type. e.g. this is compiler magic (j)");
  tr.setCode(Constants.NS_SYSTEM_TYPE + "String");
  if (path.equals("Extension.url")) {
    ToolingExtensions.addUriExtension(tr, ToolingExtensions.EXT_FHIR_TYPE, "uri");
  } else {
    ToolingExtensions.addUriExtension(tr, ToolingExtensions.EXT_FHIR_TYPE, "string");
  }
}
```

At this point Resource.id was still being caught by the over-broad .id test, and it was being labeled with fhir-type = string.

This matches the R4.0.1 published artifact:

```
{
  "id": "Resource.id",
  "path": "Resource.id",
  "type": [{
    "extension": [{
      "url": "http://hl7.org/fhir/StructureDefinition/structuredefinition-fhir-type",
      "valueUrl": "string"
    }],
    "code": "http://hl7.org/fhirpath/System.String"
  }]
}
```

### Later Correction/Rationalization for Resource.id

After R4.0.1, people noticed that Resource.id was now System.String with fhir-type = string. That led to later issues:

* FHIR-25262: <https://jira.hl7.org/browse/FHIR-25262>
* FHIR-25274: <https://jira.hl7.org/browse/FHIR-25274>
* FHIR-45989: <https://jira.hl7.org/browse/FHIR-45989>

On 2019-12-30, commit 7daa0d2 changed the generator to distinguish resources:

<https://github.com/HL7/fhir/commit/7daa0d220d80bdaf2229f7aa05f4d4e6c0f5a698>

Relevant code:

```
} else if (Utilities.existsInList(path, "Element.id", "Extension.url") || path.endsWith(".id")) {
  TypeRefComponent tr = ce.addType();
  tr.getFormatCommentsPre().add("Note: special primitive values have a FHIRPath system type. e.g. this is compiler magic (j)");
  tr.setCode(Constants.NS_SYSTEM_TYPE + "String");
  if (path.equals("Extension.url")) {
    ToolingExtensions.addUriExtension(tr, ToolingExtensions.EXT_FHIR_TYPE, "uri");
  } else if (p.getKind() == StructureDefinitionKind.RESOURCE) {
    ToolingExtensions.addUriExtension(tr, ToolingExtensions.EXT_FHIR_TYPE, "id");
  } else {
    ToolingExtensions.addUriExtension(tr, ToolingExtensions.EXT_FHIR_TYPE, "string");
  }
}
```

This is the point where Resource.id became System.String with fhir-type = id.

That later became the rationalized position: Resource.id is conceptually a FHIR id, but represented as System.String so it does not have the normal primitive children id and extension.

### Interpretation

The history supports this sequence:

1. FHIR-12060 intentionally special-cased Element.id and Extension.url.
2. FHIR-22493 intended to preserve that Element.id special behavior in derived datatype snapshots such as string.id.
3. Commit f9057f0 implemented that by checking all paths ending in .id.
4. That implementation unintentionally included Resource.id.
5. Later tickets noticed the resulting Resource.id shape and rationalized it by changing its structuredefinition-fhir-type from string to id.

The critical point is that the original ticket-backed scope did not require Resource.id to become special. The source history and tracker scope point to an over-generalized implementation, not an explicit Resource.id design decision.

### Compact Statement

Resource.id appears to have become System.String as a side effect of the FHIR-22493 implementation. The tracker asked for Element.id compiler-magic behavior to be preserved on derived datatype snapshots; the implementation used path.endsWith(".id"), which also swept in Resource.id. Later issues accepted and rationalized the result, but the origin looks accidental.