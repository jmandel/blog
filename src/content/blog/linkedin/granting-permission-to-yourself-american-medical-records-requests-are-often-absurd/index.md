---
title: "Granting Permission to Yourself: American Medical Records Requests are Often Absurd"
date: 2026-02-20T14:45:00
added_at: 2026-04-03
slug: granting-permission-to-yourself-american-medical-records-requests-are-often-absurd
original_url: "https://www.linkedin.com/pulse/granting-permission-yourself-american-medical-records-josh-mandel-md-0klyc"
linkedin_id: 0klyc
banner: ./banner.jpg
intro_share:
  share_url: "https://www.linkedin.com/feed/update/urn:li:ugcPost:7430647825572528128"
  share_id: "7430647825572528128"
  share_type: "ugcPost"
  posted_at: "2026-02-20T16:21:36"
  visibility: "MEMBER_NETWORK"
  commentary: |
    HIPAA guarantees patients a right to their own medical records. In practice, most health systems require patients to fill out a release-of-information form designed for a different legal purpose; justify why they want their own data; and wait. I sampled 181 organizations across 43 states to measure how wide the gap is -- and to highlight what the best organizations do differently. See article for details.
---

Imagine walking into your local public library to check out a book, only to be handed a third-party disclosure form designed for an insurance company. You write your own name in the "Authorized Recipient" box. You declare your "Purpose" for wanting to read the book. You ask two strangers in the lobby to co-sign your request. Before the librarian hands you the text, you are warned that the library cannot control what happens to the information once it leaves their possession.

This is what happens when an American patient tries to obtain their own medical records.

Under the HIPAA Right of Access (45 CFR § 164.524), patients have a legal right to their health data -- whether to feed into an AI health app, transfer to a specialist for a second opinion, or simply keep on their own phone. But our evaluation of release-of-information forms shows a wide gap between the law's intent and how health systems actually operate.

**We evaluated publicly available PDF forms at 181 healthcare organizations across 43 states**. To ensure a representative picture of the U.S. healthcare landscape, we used a stratified sampling methodology calibrated across facility types, corporate ownership models, system affiliations, and geographic regions. We deployed AI agents (automated browsers that performed web searches, navigated hospital websites, and downloaded forms) to replicate the experience of a patient looking for a records request form. Each downloaded document was then scored on findability, technical accessibility, content design, patient-centeredness, and compliance.

We specifically evaluated publicly available PDF forms, excluding online portals that require account creation or identity verification. Even among organizations that offer portals, over 90% still publish a downloadable PDF alongside them. The PDF remains the universal baseline artifact for medical records access, and the most legible to external evaluation.

---

### Using Third-Party Forms for Patient Access

The HIPAA Privacy Rule defines two distinct mechanisms for releasing protected health information (PHI). Under the **Individual Right of Access** (45 CFR § 164.524), a covered entity is *required* to act on a patient's request, while a **HIPAA Authorization** (45 CFR § 164.508) creates only a *permitted* disclosure that the entity may decline. An Authorization also demands core elements — stated purpose, expiration date, redisclosure warnings — designed for third-party releases.

In practice, 78.5% of the organizations studied gave patients an Authorization form when only a right of access request was legally needed; **just 12.2% provided a form designed for patient access**. HHS has stated that covered entities may not require an individual to sign an authorization form when the right of access applies, as it requests more information than necessary and may create impermissible obstacles.

The consequences were predictable. Covered entities may not require individuals to provide a reason for requesting their own PHI -- yet the Authorization form's "Purpose of Disclosure" field, a required core element under § 164.508, was routinely presented as mandatory when patients are sent down an authorization route. Patients ended up formally authorizing disclosure of their own data back to themselves, justifying why they wanted it, and acknowledging redisclosure warnings that made no sense when sender and recipient were the same person.

---

### Flat PDFs

Despite widespread digital adoption in healthcare, **only 26.5% of the organizations we studied offered fillable PDF forms**.

The rest distributed "flat" PDFs. These were "born-digital" documents created in Microsoft Word or Adobe InDesign, uploaded to the web without interactive checkboxes and text fields.

A patient downloading one of these files might need to locate a physical printer, fill the form out with a pen, find a scanner or a fax machine, and send it back to a digital inbox.

---

### Friction, Fees, and Social Security Numbers

Applying a corporate legal template to a patient's civil right introduced friction and risk. For example, [Abbeville Area Medical Center](https://www.abbevilleareamc.com/wp-content/uploads/2023/01/HIM-1022-authorization.pdf) provided a non-fillable form that required, in addition to a patient signature, *two* witness signatures. [Nemaha Valley Community Hospital](https://nemvch.com/wp-content/uploads/2019/10/Authorization-for-Release.pdf) and [ENT & Allergy Associates](https://www.entandallergy.com/documents/content/enta_arphi_form.doc) expected full Social Security Numbers -- an unnecessary identity theft risk for documents frequently submitted via unencrypted fax.

---

### System Affiliation Drives Quality

We analyzed four organizational axes to see what predicted quality. Geography meant little; organizations across the country earned statistically similar scores. Facility type mattered slightly, but the variation *within* categories outweighed the differences between them. [Wayne County Hospital](https://waynehospital.org/files/galleries/Medical_Records_Release.pdf), a 25-bed critical access facility in rural Kentucky, outperformed [OSU Wexner Medical Center](https://wexnermedical.osu.edu/-/media/files/wexnermedical/patient-care/patient-and-visitor-guide/medical-records/roi-form-and-instructions.pdf), a 1,400-bed academic institution whose form did not clearly document how patients could submit it electronically.

The strongest predictor of quality was **system affiliation**. Large health systems acted as quality amplifiers. They had the resources to invest in form design and the organizational structure to propagate it across dozens of facilities. They amplified good and bad templates alike—whether that meant distributing a beautifully designed 66-field interactive PDF or a decade-old scanned image.

---

### Capabilities Versus Choices

Health systems possess the technology to build seamless digital forms, but our findings show they routinely reserve it for alternative workflows.

At Ironwood Cancer & Research Centers, the [form designed for other doctors](https://www.ironwoodcrc.com/wp-content/uploads/2023/11/Medical-Records-RequestForm-to-request-from-other-facilities_FILLABLE.pdf) to send records to the clinic featured 22 fillable digital fields. The [form for patients to get their records out](https://www.ironwoodcrc.com/wp-content/uploads/2019/03/Authorization-to-release-protected-health-information.pdf) had zero.

JPS Health Network published polished, fillable, text-searchable authorization [**forms for Health Information Exchange (HIE)**](https://jpshealthnet.org/sites/default/files/2025-05/Patient-HIE-Authorization-Form.pdf) with encrypted email submission. However, the [**form it provided to patients**](https://jpshealthnet.org/sites/default/files/inline-files/roi_english_revised_2018_10.pdf) requesting their own records was a degraded, image-only scan from 2018.

---

### Sidebar: Missing Computable Data Options

The 21st Century Cures Act legally obligates providers to offer patients their electronic health information in a computable format (EHI Export). Yet, of the 474 individual forms evaluated in our study, exactly two organizations ([Samaritan Lebanon Community Hospital](https://samhealth.org/computer-readable-ehi-export-request-english?type=pdf) and [Owensboro Health](https://www.owensborohealth.org/sites/default/files/inline/b7/health-disclosure-form.pdf)) mentioned EHI Export on their release forms. For the remaining 99% of the industry, this federal interoperability requirement did not translate into public-facing forms.

---

### Practical Fixes

Improving this process requires minimal budget or procurement. A small vanguard of organizations already demonstrates effective design.

[Northwell Health](https://www.northwell.edu/sites/northwell.edu/files/2022-03/request-for-access-to-health-information-form-english-2022.pdf) used a dedicated patient access form that explicitly cited HIPAA Right of Access (45 CFR § 164.524) at the top, immediately establishing that the patient was exercising a right. [Merit Health Central](https://www.merithealthcentral.com/Uploads/Public/Documents/all-new-documents/HIM-1406.pdf) featured "Myself" as the first recipient option. [Intermountain Health](https://prod.intermountainhealth.org/-/media/files/intermountain-health/for-patients/medical-records/request-records-for-yourself.ashx) used conversational headers like *"What records do you want?"*

We found the most effective medical records forms follow a few simple rules:

1. **Make it a separate document.** Title it "Patient Request for Access to Records."
2. **Make it fillable.** Every field should be typeable on a smartphone or computer.
3. **Remove the friction.** Eliminate witness requirements, Social Security fields, and mandatory "Purpose" lines.
4. **Offer a "To Me" checkbox.** Do not make patients write their own home address in a "Facility Name" box.
5. **Accept it digitally.** Provide fax, email, or a web submission route that does not require account creation or in-band identify verification. The form itself can contain the necessary identity attributes—such as a photo of a driver's license—making it a self-contained artifact.

Looking ahead, the same principle should extend to programmatic access. An open submission API—mirroring the capabilities of a fax line but accessible to software—would let AI health apps and patient-authorized tools assemble and submit requests on a patient's behalf. No organization in our sample offers this today, but the infrastructure is trivial compared to what was required to digitize the records themselves.

Healthcare organizations have spent billions of dollars digitizing American medical records. The one-page form that lets a patient actually retrieve them should not be the hardest part.