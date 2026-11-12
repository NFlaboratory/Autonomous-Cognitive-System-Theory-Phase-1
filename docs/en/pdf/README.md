# English summaries as PDF files

This directory holds a PDF version of each of the 31 detailed English summaries in [`../`](../README.md), covering the Abstract and Sections 1–9.

- **Authority and precedence.** The Japanese manuscript is the authoritative source for all theoretical content. The Markdown summaries are the source documents for the corresponding PDF editions. If a PDF differs from its source Markdown in presentation or transcription, consult the Markdown. If either English version differs from the Japanese manuscript in theoretical content, the Japanese manuscript takes precedence. The summaries are not a full translation and add no definitions, assumptions or results.
- **Correspondence between files and sections.** A file does not always correspond to one section. A long section is split into several parts, and the part numbers ("part 2 of 5") show the split; for example, §2 is given in five parts and §9 in three. A short section, such as §8, and the Abstract and §1 each occupy one file. File names follow the order of the manuscript.
- **Source and revision history.** Each summary identifies its source manuscript file, the relevant line range, and the source commit. Where subsequent author-approved corrections are incorporated, the source note also identifies the applicable revision record.
- **Shorter overview.** [English overview (Markdown)](../../ACS_Phase1_overview_en.md) · [English overview (PDF)](../../ACS_Phase1_overview_en.pdf)
- **Glossary and labels.** Terms and label conventions are described in [`../README.md`](../README.md) and [`../glossary.md`](../glossary.md).

## Preparation, AI-Assisted Review, and Author Responsibility

The English summaries were drafted using Claude under the direction of the human author. The drafting process included checks against the Japanese manuscript, terminology alignment, and revisions of the English text.

ChatGPT was used as a separate language model to review the summaries against the Japanese manuscript, examine logical and mathematical consistency, check terminology and references, and review the corresponding PDF editions. Identified issues and proposed corrections were recorded and addressed through the revision process.

These language models serve as auxiliary tools for preparation, checking, and review. Their outputs do not constitute independent human peer review or establish the correctness of the theory.

The human author determines the research direction, the adoption of theoretical content, and the acceptance of proposed revisions, and retains final responsibility for the research.

Each English summary remains a draft until the author has verified it against the Japanese manuscript and explicitly approved its status change. The corresponding PDF edition carries the same status.

No independent human third-party verification of the summaries is claimed. As stated in the manuscript (§9, `rem:ai_assistance`), comprehensive verification of the manuscript and its verification code by independent experts other than the author has not been carried out.

## Files

| PDF | Markdown | Manuscript part |
|---|---|---|
| [`00_abstract.pdf`](00_abstract.pdf) | [`00_abstract.md`](../00_abstract.md) | Abstract (`paper/abstract.tex`) |
| [`01_introduction.pdf`](01_introduction.pdf) | [`01_introduction.md`](../01_introduction.md) | §1 Introduction (`paper/section1_intro.tex`) |
| [`02_definition_1.pdf`](02_definition_1.pdf) | [`02_definition_1.md`](../02_definition_1.md) | §2 Formal definition of an ACS, part 1 of 5 (§2.1–§2.4) |
| [`02_definition_2.pdf`](02_definition_2.pdf) | [`02_definition_2.md`](../02_definition_2.md) | §2 part 2 of 5 (§2.5 structural self, temporal self-identity, functional termination, collapse) |
| [`02_definition_3.pdf`](02_definition_3.pdf) | [`02_definition_3.md`](../02_definition_3.md) | §2 part 3 of 5 (§2.6 required environment space, CR-1) |
| [`02_definition_4.pdf`](02_definition_4.pdf) | [`02_definition_4.md`](../02_definition_4.md) | §2 part 4 of 5 (§2.7 state transition, §2.8 feasibility, blockage) |
| [`02_definition_5.pdf`](02_definition_5.pdf) | [`02_definition_5.md`](../02_definition_5.md) | §2 part 5 of 5 (§2.9–§2.13 CR-2, internal model, Update, assumptions) |
| [`03_principles_1.pdf`](03_principles_1.pdf) | [`03_principles_1.md`](../03_principles_1.md) | §3 part 1 of 5 (opening, §3.1 conventions, §3.2 premises, §3.3 SM) |
| [`03_principles_2.pdf`](03_principles_2.pdf) | [`03_principles_2.md`](../03_principles_2.md) | §3 part 2 of 5 (§3.4 viability kernel and finite-step sets, §3.5 structural environment coupling) |
| [`03_principles_3.pdf`](03_principles_3.pdf) | [`03_principles_3.md`](../03_principles_3.md) | §3 part 3 of 5 (§3.6 EU, §3.7 FR, §3.8 blockage dichotomy and relations, §3.9 linkage) |
| [`03_principles_4.pdf`](03_principles_4.pdf) | [`03_principles_4.md`](../03_principles_4.md) | §3 part 4 of 5 (§3.10 response-diversity degeneration and long-term feasibility: conditional necessity) |
| [`03_principles_5.pdf`](03_principles_5.pdf) | [`03_principles_5.md`](../03_principles_5.md) | §3 part 5 of 5 (§3.11 time-integrated evaluation, T-STAB; §3.12 connection to TIPA, PSL, ISL) |
| [`04_tipa_1.pdf`](04_tipa_1.pdf) | [`04_tipa_1.md`](../04_tipa_1.md) | §4 part 1 of 4 (opening, §4.1 scope and conventions, §4.2 TIPA, M1) |
| [`04_tipa_2.pdf`](04_tipa_2.pdf) | [`04_tipa_2.md`](../04_tipa_2.md) | §4 part 2 of 4 (§4.2.2 M2, §4.2.3 M3) |
| [`04_tipa_3.pdf`](04_tipa_3.pdf) | [`04_tipa_3.md`](../04_tipa_3.md) | §4 part 3 of 4 (PSL-1 to PSL-4, effective-action resolution, sensitivity control; purpose, action and result) |
| [`04_tipa_4.pdf`](04_tipa_4.pdf) | [`04_tipa_4.md`](../04_tipa_4.md) | §4 part 4 of 4 (ISL, integrated high-speed processing and Automaticity, functional axis, summary of §4) |
| [`05_dynamics_1.pdf`](05_dynamics_1.pdf) | [`05_dynamics_1.md`](../05_dynamics_1.md) | §5 part 1 of 2 (responsibilities R1–R4, standard step, retained records, P1–P3, handover of records, observation factorization of Update) |
| [`05_dynamics_2.pdf`](05_dynamics_2.pdf) | [`05_dynamics_2.md`](../05_dynamics_2.md) | §5 part 2 of 2 (inter-time change, bias and bias strength, readout types, prediction accuracy coefficient, effective time horizon, development freedom, health, Desc, hand-off) |
| [`06_relational_1.pdf`](06_relational_1.pdf) | [`06_relational_1.md`](../06_relational_1.md) | §6 part 1 of 4 (opening and scope, external objects and three-way classification, local size indicator, finite observation window, unidirectional relation descriptor) |
| [`06_relational_2.pdf`](06_relational_2.pdf) | [`06_relational_2.md`](../06_relational_2.md) | §6 part 2 of 4 (bidirectional composition, evaluation rule, evaluable domain and definition of relation quality $Q$) |
| [`06_relational_3.pdf`](06_relational_3.pdf) | [`06_relational_3.md`](../06_relational_3.md) | §6 part 3 of 4 (sign classification of $Q$, distinction from environment coupling, finite-window aggregation, relation to T-STAB) |
| [`06_relational_4.pdf`](06_relational_4.pdf) | [`06_relational_4.md`](../06_relational_4.md) | §6 part 4 of 4 (representative categories and six families, scope, hand-off to §7 and §8, summary) |
| [`07_collapse_1.pdf`](07_collapse_1.pdf) | [`07_collapse_1.md`](../07_collapse_1.md) | §7 part 1 of 5 (opening, blockage, descriptive state bands) |
| [`07_collapse_2.pdf`](07_collapse_2.pdf) | [`07_collapse_2.md`](../07_collapse_2.md) | §7 part 2 of 5 (external recoverability and identity, collapse as an absorbing terminal state) |
| [`07_collapse_3.pdf`](07_collapse_3.pdf) | [`07_collapse_3.md`](../07_collapse_3.md) | §7 part 3 of 5 (trajectory record space and the blockage path set) |
| [`07_collapse_4.pdf`](07_collapse_4.pdf) | [`07_collapse_4.md`](../07_collapse_4.md) | §7 part 4 of 5 (the collapse-reaching path set) |
| [`07_collapse_5.pdf`](07_collapse_5.pdf) | [`07_collapse_5.md`](../07_collapse_5.md) | §7 part 5 of 5 (inflow tendency; connection to the organizational ACS) |
| [`08_organizational_acs.pdf`](08_organizational_acs.pdf) | [`08_organizational_acs.md`](../08_organizational_acs.md) | §8 Organizational ACS (single part: terms, participating ACSs, organization-level structure, feasibility and the three principles, identity and failure states, limits) |
| [`09_limitations_1.pdf`](09_limitations_1.pdf) | [`09_limitations_1.md`](../09_limitations_1.md) | §9 part 1 of 3 (introduction; theoretical limits L1–L18) |
| [`09_limitations_2.pdf`](09_limitations_2.pdf) | [`09_limitations_2.md`](../09_limitations_2.md) | §9 part 2 of 3 (delegations to Phase 1.α; 11 open problems; dependencies) |
| [`09_limitations_3.pdf`](09_limitations_3.pdf) | [`09_limitations_3.md`](../09_limitations_3.md) | §9 part 3 of 3 (outlook for Phases 2 and 3; conclusion) |
