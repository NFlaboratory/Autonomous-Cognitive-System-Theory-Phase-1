# Detailed English summary of the Phase 1 manuscript

This directory gives a section-by-section English summary of the Japanese manuscript in `paper/`. The collection covers the Abstract and Sections 1–9 in 31 parts.

- **Authority and precedence.** The Japanese manuscript is the authoritative source for all theoretical content. The Markdown summaries are the source documents for the corresponding PDF editions. If a PDF differs from its source Markdown in presentation or transcription, consult the Markdown. If either English version differs from the Japanese manuscript in theoretical content, the Japanese manuscript takes precedence. The summaries are not a full translation and add no definitions, assumptions or results.
- **Correspondence between files and sections.** A file does not always correspond to one section. A long section is split into several parts, and the part numbers ("part 2 of 5") show the split; for example, §2 is given in five parts and §9 in three. A short section, such as §8, and the Abstract and §1 each occupy one file. File names follow the order of the manuscript.
- **Source and revision history.** Each summary identifies its source manuscript file, the relevant line range, and the source commit. Where subsequent author-approved corrections are incorporated, the source note also identifies the applicable revision record.
- **Labels.** Identifiers such as `def:SM` or `prop:blockage_dichotomy` are the `\label`s in `paper/`. They do not depend on the language and can be used to look up the Japanese text.
- **Terms.** English terms follow [`glossary.md`](glossary.md). A term marked "given in the manuscript" uses the English name that the manuscript itself states.
- **PDF.** Each part is also available as a PDF in [`pdf/`](pdf/README.md). The PDFs are generated from these Markdown files and carry the same draft status.
- **Shorter overview.** [English overview (Markdown)](../ACS_Phase1_overview_en.md) · [English overview (PDF)](../ACS_Phase1_overview_en.pdf)

## Preparation, AI-Assisted Review, and Author Responsibility

The English summaries were drafted using Claude under the direction of the human author. The drafting process included checks against the Japanese manuscript, terminology alignment, and revisions of the English text.

ChatGPT was used as a separate language model to review the summaries against the Japanese manuscript, examine logical and mathematical consistency, check terminology and references, and review the corresponding PDF editions. Identified issues and proposed corrections were recorded and addressed through the revision process.

These language models serve as auxiliary tools for preparation, checking, and review. Their outputs do not constitute independent human peer review or establish the correctness of the theory.

The human author determines the research direction, the adoption of theoretical content, and the acceptance of proposed revisions, and retains final responsibility for the research.

Each English summary remains a draft until the author has verified it against the Japanese manuscript and explicitly approved its status change. The corresponding PDF edition carries the same status.

No independent human third-party verification of the summaries is claimed. As stated in the manuscript (§9, `rem:ai_assistance`), comprehensive verification of the manuscript and its verification code by independent experts other than the author has not been carried out.

## Parts

| File | PDF | Manuscript part | Status |
|---|---|---|---|
| [`00_abstract.md`](00_abstract.md) | [PDF](pdf/00_abstract.pdf) | Abstract (`paper/abstract.tex`) | draft |
| [`01_introduction.md`](01_introduction.md) | [PDF](pdf/01_introduction.pdf) | §1 Introduction (`paper/section1_intro.tex`) | draft |
| [`02_definition_1.md`](02_definition_1.md) | [PDF](pdf/02_definition_1.pdf) | §2 Formal definition of an ACS, part 1 of 5 (§2.1–§2.4) | draft |
| [`02_definition_2.md`](02_definition_2.md) | [PDF](pdf/02_definition_2.pdf) | §2 part 2 of 5 (§2.5 structural self, temporal self-identity, functional termination, collapse) | draft |
| [`02_definition_3.md`](02_definition_3.md) | [PDF](pdf/02_definition_3.pdf) | §2 part 3 of 5 (§2.6 required environment space, CR-1) | draft |
| [`02_definition_4.md`](02_definition_4.md) | [PDF](pdf/02_definition_4.pdf) | §2 part 4 of 5 (§2.7 state transition, §2.8 feasibility, blockage) | draft |
| [`02_definition_5.md`](02_definition_5.md) | [PDF](pdf/02_definition_5.pdf) | §2 part 5 of 5 (§2.9–§2.13 CR-2, internal model, Update, assumptions) | draft |
| [`03_principles_1.md`](03_principles_1.md) | [PDF](pdf/03_principles_1.pdf) | §3 part 1 of 5 (opening, §3.1 conventions, §3.2 premises, §3.3 SM) | draft |
| [`03_principles_2.md`](03_principles_2.md) | [PDF](pdf/03_principles_2.pdf) | §3 part 2 of 5 (§3.4 viability kernel and finite-step sets, §3.5 structural environment coupling) | draft |
| [`03_principles_3.md`](03_principles_3.md) | [PDF](pdf/03_principles_3.pdf) | §3 part 3 of 5 (§3.6 EU, §3.7 FR, §3.8 blockage dichotomy and relations, §3.9 linkage) | draft |
| [`03_principles_4.md`](03_principles_4.md) | [PDF](pdf/03_principles_4.pdf) | §3 part 4 of 5 (§3.10 response-diversity degeneration and long-term feasibility: conditional necessity) | draft |
| [`03_principles_5.md`](03_principles_5.md) | [PDF](pdf/03_principles_5.pdf) | §3 part 5 of 5 (§3.11 time-integrated evaluation, T-STAB; §3.12 connection to TIPA, PSL, ISL) | draft |
| [`04_tipa_1.md`](04_tipa_1.md) | [PDF](pdf/04_tipa_1.pdf) | §4 part 1 of 4 (opening, §4.1 scope and conventions, §4.2 TIPA, M1) | draft |
| [`04_tipa_2.md`](04_tipa_2.md) | [PDF](pdf/04_tipa_2.pdf) | §4 part 2 of 4 (§4.2.2 M2, §4.2.3 M3) | draft |
| [`04_tipa_3.md`](04_tipa_3.md) | [PDF](pdf/04_tipa_3.pdf) | §4 part 3 of 4 (PSL-1 to PSL-4, effective-action resolution, sensitivity control; purpose, action and result) | draft |
| [`04_tipa_4.md`](04_tipa_4.md) | [PDF](pdf/04_tipa_4.pdf) | §4 part 4 of 4 (ISL, integrated high-speed processing and Automaticity, functional axis, summary of §4) | draft |
| [`05_dynamics_1.md`](05_dynamics_1.md) | [PDF](pdf/05_dynamics_1.pdf) | §5 part 1 of 2 (responsibilities R1–R4, standard step, retained records, P1–P3, handover of records, observation factorization of Update) | draft |
| [`05_dynamics_2.md`](05_dynamics_2.md) | [PDF](pdf/05_dynamics_2.pdf) | §5 part 2 of 2 (inter-time change, bias and bias strength, readout types, prediction accuracy coefficient, effective time horizon, development freedom, health, Desc, hand-off) | draft |
| [`06_relational_1.md`](06_relational_1.md) | [PDF](pdf/06_relational_1.pdf) | §6 part 1 of 4 (opening and scope, external objects and three-way classification, local size indicator, finite observation window, unidirectional relation descriptor) | draft |
| [`06_relational_2.md`](06_relational_2.md) | [PDF](pdf/06_relational_2.pdf) | §6 part 2 of 4 (bidirectional composition, evaluation rule, evaluable domain and definition of relation quality $Q$) | draft |
| [`06_relational_3.md`](06_relational_3.md) | [PDF](pdf/06_relational_3.pdf) | §6 part 3 of 4 (sign classification of $Q$, distinction from environment coupling, finite-window aggregation, relation to T-STAB) | draft |
| [`06_relational_4.md`](06_relational_4.md) | [PDF](pdf/06_relational_4.pdf) | §6 part 4 of 4 (representative categories and six families, scope, hand-off to §7 and §8, summary) | draft |
| [`07_collapse_1.md`](07_collapse_1.md) | [PDF](pdf/07_collapse_1.pdf) | §7 part 1 of 5 (opening, blockage, descriptive state bands) | draft |
| [`07_collapse_2.md`](07_collapse_2.md) | [PDF](pdf/07_collapse_2.pdf) | §7 part 2 of 5 (external recoverability and identity, collapse as an absorbing terminal state) | draft |
| [`07_collapse_3.md`](07_collapse_3.md) | [PDF](pdf/07_collapse_3.pdf) | §7 part 3 of 5 (trajectory record space and the blockage path set) | draft |
| [`07_collapse_4.md`](07_collapse_4.md) | [PDF](pdf/07_collapse_4.pdf) | §7 part 4 of 5 (the collapse-reaching path set) | draft |
| [`07_collapse_5.md`](07_collapse_5.md) | [PDF](pdf/07_collapse_5.pdf) | §7 part 5 of 5 (inflow tendency; connection to the organizational ACS) | draft |
| [`08_organizational_acs.md`](08_organizational_acs.md) | [PDF](pdf/08_organizational_acs.pdf) | §8 Organizational ACS (single part: terms, participating ACSs, organization-level structure, feasibility and the three principles, identity and failure states, limits) | draft |
| [`09_limitations_1.md`](09_limitations_1.md) | [PDF](pdf/09_limitations_1.pdf) | §9 part 1 of 3 (introduction; theoretical limits L1–L18) | draft |
| [`09_limitations_2.md`](09_limitations_2.md) | [PDF](pdf/09_limitations_2.pdf) | §9 part 2 of 3 (delegations to Phase 1.α; 11 open problems; dependencies) | draft |
| [`09_limitations_3.md`](09_limitations_3.md) | [PDF](pdf/09_limitations_3.pdf) | §9 part 3 of 3 (outlook for Phases 2 and 3; conclusion) | draft |
