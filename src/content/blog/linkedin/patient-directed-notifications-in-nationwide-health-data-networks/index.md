---
title: "Patient-Directed Notifications in Nationwide Health Data Networks"
date: 2026-01-23T21:16:00
slug: patient-directed-notifications-in-nationwide-health-data-networks
original_url: "https://www.linkedin.com/pulse/patient-directed-notifications-nationwide-health-data-josh-mandel-md-82azc"
linkedin_id: 82azc
banner: ./banner.png
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7420576075434553344"
  share_id: "7420576075434553344"
  share_type: "ugcPost"
  posted_at: "2026-01-23T21:20:04"
  visibility: "MEMBER_NETWORK"
  commentary: |
    How can patient-directed health notifications scale nationwide without undermining provider trust, consent, and existing legal frameworks?
---

*(Guest post authored by ChatGPT 5.2 Pro -- if you think this slop, call me out!)*

### Legal, Trust, and Architectural Considerations

### Executive summary

There is growing interest in enabling patient-directed applications to receive **notifications** (e.g., “new data available,” “new encounter occurred”) across all sites where an individual receives care. Conceptually, this is distinct from traditional record retrieval: it is dynamic, ongoing, and event-driven rather than episodic and pull-based.

While existing nationwide health data exchange frameworks provide strong foundations for **routing requests and responses**, they were designed primarily around **provider-controlled disclosure of historical or static data**. Extending these frameworks to support near-real-time notifications raises non-trivial questions about consent, identity verification, liability, and the allocation of responsibility between providers, networks, and patient-directed applications.

This brief outlines:

* why existing exchange models have achieved legal and operational acceptance,
* why notifications create new concerns despite often carrying less data,
* several architectural approaches for enabling notifications,
* and the legal and trust implications of each approach.

The goal is to clarify trade-offs and identify plausible paths that build on existing policy and practice without requiring wholesale reinvention of trust frameworks.

---

### 1. Why current nationwide exchange models work

Nationwide health data exchange frameworks have gained acceptance largely because they preserve a **provider-centric control loop**:

* Networks handle **routing and discovery**
* Providers retain authority over: patient matching, authentication, consent verification, and the ultimate decision to disclose data
* Data flows only after the provider determines that identity and authorization requirements are satisfied

From a legal and risk perspective, this structure allows providers to assert that:

* each disclosure was deliberate,
* it followed internal identity and consent processes,
* and it can be defended under existing privacy and security obligations.

Even when patient-directed access is involved, providers typically maintain an opportunity to:

* authenticate the individual (often via a portal),
* confirm intent,
* and apply local policies before releasing information.

This allocation of responsibility is central to the comfort level of compliance officers, legal counsel, and regulators.

---

### 2. Why notifications are perceived as different

Although notifications may contain minimal information, they introduce several characteristics that challenge established expectations.

### 2.1 Shift from episodic to standing disclosures

Traditional access requests are discrete and auditable. Notifications resemble **ongoing, automated disclosures**, which raises concerns about:

* persistent authorization,
* revocation handling,
* and cumulative risk over time.

### 2.2 Inversion of the control loop

If notifications are generated and forwarded without a contemporaneous provider-side decision, providers may perceive that:

* identity verification,
* consent validation,
* or recipient selection has shifted away from their direct control.

This is less about the size of the data and more about **who decided that the disclosure should occur**.

### 2.3 Ambiguity in legal roles

Notifications blur lines between:

* activities performed “on behalf of” providers (which may implicate business associate relationships), and
* disclosures made at the direction of an individual to a third party.

Providers are understandably cautious when it is unclear which category applies, especially when errors could lead to misdirected disclosures.

---

### 3. Architectural approaches and their implications

Several approaches can be considered for enabling patient-directed notifications. Each places matching, consent, and liability in different locations.

---

### Approach A: Provider-controlled subscriptions (site-level enablement)

**Description** Each provider offers its own mechanism (e.g., FHIR-based subscriptions or equivalent) that allows a patient-directed application to subscribe to events at that site.

* The provider: authenticates the patient, verifies consent, determines which events are eligible, and sends notifications directly to the app.
* Networks may assist with discovery or onboarding but are not required for message delivery.

**Legal and trust posture**

* The provider remains the disclosing actor.
* Matching and consent stay entirely within existing provider workflows.
* No new categories of agreement or responsibility are introduced.

**Advantages**

* Highest legal clarity.
* Strong alignment with current compliance practices.
* Easiest to explain to regulators and patients.

**Limitations**

* Requires point-to-point integration with each provider.
* Adoption may be uneven.
* Network-level efficiencies emerge only after significant site-level uptake.

---

### Approach B: Provider-affirmed routing via a network

**Description** Providers continue to authenticate patients and obtain authorization, but use a network to route notifications.

* The provider explicitly registers: the patient–application relationship,the authorized destination endpoint.
* Notifications are generated by the provider and routed by the network to that pre-authorized endpoint.
* The network does not perform patient matching or consent decisions.

**Legal and trust posture**

* Providers can assert that all disclosures were explicitly authorized at the source.
* The network functions as a transport intermediary, not a decision-maker.
* Existing contractual models (including business associate relationships, where applicable) can be extended without introducing novel roles.

**Advantages**

* Preserves provider control.
* Allows network-level scale and efficiency.
* Minimizes new legal concepts.

**Limitations**

* Still requires provider implementation work.
* More complex operationally than pure point-to-point delivery.
* Requires clear delineation that networks are not independently determining recipients.

---

### Approach C: Network-managed subscription registry

**Description** Patient-directed applications register subscriptions at the network level. Providers emit events to the network, which determines which applications receive notifications.

**Legal and trust posture**

* The network becomes responsible for: patient identity assurance, consent status, and recipient selection.
* Providers may no longer be able to assert that each disclosure was the result of their own verification processes.

**Advantages**

* Simplifies application integration.
* Enables uniform nationwide behavior.

**Challenges**

* Introduces new trust and liability questions.
* Requires explicit agreements allocating responsibility for misrouting or consent failures.
* Represents a substantive shift from existing disclosure models, likely requiring additional governance and provider opt-in.

---

### 4. Matching, consent, and liability considerations

Across all approaches, three questions dominate risk analysis:

1. **Who verified the patient’s identity?** Errors in matching are a primary source of privacy incidents.
2. **Who confirmed consent and scope?** Especially important for ongoing disclosures and revocation.
3. **Who bears responsibility if a notification is misdirected?** Liability depends on whether the error occurred at the provider, within a contracted intermediary, or after a patient-directed disclosure.

Approaches that keep these responsibilities clearly at the provider level generally align best with existing legal interpretations and operational comfort.

---

### 5. Sequencing and ecosystem maturity

Experience with prior interoperability initiatives suggests that **node-level capability often precedes network-level aggregation**:

* Site-by-site implementation establishes: technical feasibility, operational norms, and risk tolerance.
* Networks can later: simplify discovery, standardize onboarding, and reduce duplication.

Attempting to deploy network-level functionality before sites have operational experience may increase resistance and slow adoption.

---

### 6. Key takeaways

* Notifications are not inherently riskier because of data volume, but because they alter **timing, automation, and perceived control**.
* Existing exchange frameworks are most trusted when providers remain the final arbiters of disclosure.
* Several technically feasible models exist, but they differ substantially in legal and trust implications.
* Approaches that extend current patterns—rather than replace them—are likely to encounter fewer barriers.
* Incremental evolution, starting with provider-controlled mechanisms and layering network services over time, aligns with historical interoperability successes.

---

### Conclusion

Enabling patient-directed notifications across sites of care is a plausible and potentially valuable extension of nationwide health data exchange. However, success depends less on technical feasibility than on careful alignment with existing legal, trust, and governance structures.

Designs that preserve provider-side identity verification and consent decision-making are most consistent with current policy and practice. More centralized models may be possible in the future, but they will require explicit governance choices and broader consensus.

A clear understanding of these trade-offs is essential for stakeholders evaluating how—and when—to pursue notification-based capabilities at scale.