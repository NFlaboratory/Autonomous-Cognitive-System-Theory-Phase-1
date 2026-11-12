# §9 Limitations, open problems, outlook for Phases 2 and 3 — part 3 of 3 (outlook for Phases 2 and 3; conclusion)

*Source: `paper/section9_limitations.tex`, lines 847–1071 (`subsec:phase_outlook`, `subsec:conclusion`), at commit e6e12cd. Status: draft. Parts 1 and 2 are [`09_limitations_1.md`](09_limitations_1.md) (1–466) and [`09_limitations_2.md`](09_limitations_2.md) (467–846).*

---

## Outlook for Phases 2 and 3 (`subsec:phase_outlook`)

The manuscript keeps the definitions and propositions of Phase 1 as the reference for comparison and describes directions in which its strong boundary conditions could be weakened step by step. What follows is a research plan. The manuscript does not state that any part of it will be achieved.

### Phase 2: probabilistic and dynamical extensions (`subsubsec:phase2`)

- **Stage 1 (making a single ACS robust).** Centered on `prob:branching_identity`, `prob:stability`, `prob:estimation_error` and `prob:multistep_recovery`. The subjects are temporal self-identity that permits branching, calibration of the T-STAB parameters, estimation error, update rules, reachability and stability, examined on concrete models. At the same time, the order in which the Phase 1 assumptions (determinism, discrete time, compactness, non-branching and others) can be weakened is to be evaluated.
- **Stage 2 (making relation, blockage and recovery dynamical).** Centered on `prob:relational_causality` and `prob:collapse_observability`. Relation records and causal estimation are kept separate while probabilistic and continuous-time relation change, reaching of blockage, reaching of collapse, recoverability and observation error are treated.
- **Stage 3 (extension to organizational and social dynamics).** Centered on the Phase 2 part of `prob:social_dynamics`: change over time of the participating-ACS set, joining and leaving, organizational identity, division of functions, relation structure, organization-level EU and FR with T-STAB, and organization-level blockage and collapse paths, formulated as explicit model-dependent rules. The aggregation from individual to organizational quantities has its type and its grounds stated for each application and is not fixed as a general rule without grounds. The part of `prob:capability_paradox` concerning the interaction of several ACSs and the set of effective options over a time horizon is also treated here.
- **Stage 4 (empirical evaluation).** Through `prob:cross_domain`, the correspondence between observables and theoretical variables is tested in each domain. Whether the structures added in Phase 2 actually improve predictive power, explanatory power and falsifiability is evaluated, and the claimed scope of Phase 1 is re-limited where needed. In addition, for concrete objects, the property of a shareable descriptive language is examined: when different observers describe the same behavior of the same agent in the vocabulary of the ACS, to what extent do the descriptions agree, and where do they diverge through modeling choices?

### Phase 3: formal connection with ECIT (`subsubsec:phase3`)

Phase 3 centers on `prob:ecit_full`, the formal connection between the descriptive feasibility-preservation structure of ACS theory and the ethical coordination concepts of ECIT. The part of `prob:capability_paradox` that concerns coordinative actions is also treated at this stage.

The role of ACS theory in this connection is to supply a layer that describes the behavior of each party to a coordination under a common structure, without presupposing the norms of a particular society or culture (`subsec:background`). The coordination that ECIT treats arises between agents under different norms, or between agents of different origin such as humans and autonomous AI systems. The manuscript considers it one premise for discussing coordination that, before judging why an agent acted as it did by the norms of either side, one can express in a shareable form which feasibility requirements were involved and through which operation of internal mechanisms the behavior came about. Phase 3 examines how the coordination concepts of ECIT can be built on this descriptive layer.

Three things are distinguished as having different logical statuses: the structural description given by ACS theory, the conditions for coordination treated by ECIT, and value judgments about whether behavior is good or bad. The manuscript does not take a particular value judgment or social norm to be derived logically from the ACS structure defined in Phase 1. Providing a common descriptive layer and determining the goodness of behavior on its basis have different logical statuses. If a normative element is introduced, its additional axioms, evaluation criteria and social premises are kept separate from the structural definition of the ACS. The possibility of including social norms as objects of description, namely as contents of the environment, of relations or of the internal model, and not as criteria of judgment, is also left for study at this stage. Phase 1 gives no form for describing norms in this way.

**Significance of the Phase division (`rem:phase_strategy`).** The division into Phases 1–3 is a way to separate different proof strengths and different degrees of model dependence as well as a chronological order. Phase 1 is the deterministic, discrete-time minimal structure; Phase 2 covers the extensions to probability, continuous time, causality and organizational or social dynamics; Phase 3 covers the formal connection with ECIT. The manuscript does not exclude beforehand that results of later Phases may revise or limit the scope of Phase 1.

---

## Conclusion (`subsec:conclusion`)

As Phase 1 of ACS theory, the paper describes an autonomous cognitive system by the 7-tuple $\Sigma=(X,U,E,f,\Pi,M,\mathrm{Update})$ and constructs a structural framework centered on feasibility preservation. The conclusion separates what the paper establishes from what it does not.

### Main structures established in Phase 1 (`subsubsec:core_results`)

- **Formal definition of the ACS (§2).** The 7-tuple, the feasible set $K$, the feasible action set $A_t$ and other basic structures. The external environment state space is split into an exogenous background component and an action-response component. With the structural self distinguished from well-formed realization, functional termination and collapse are defined as state conditions.
- **The three principles (§3).** SM, EU and FR are formalized without flattening them to one logical status, with their time-indexed satisfaction predicates, domains and proof strengths distinguished. Blockage is split in two according to whether the critical required factors are satisfied. The time-integrated evaluation condition of the three principles (T-STAB) integrates the SM evaluation, EU and local FR over a finite time window.
- **TIPA, PSL, ISL (§4).** The functional structure of TIPA (M1 information integration, M2 adaptive evaluation, M3 response action), its Physical Substrate Layer (PSL) and Implementation Substrate Layer (ISL).
- **Inter-time dynamics (§5).** Under the conditions of `prop:s5_one_step`, each one-step operation record is uniquely determined and the next state triple belongs to $X\times\mathcal M\times O$. Given an environment realization and an initial value $(x_0,M_0,o_0)$, there is exactly one standard operation record on $\mathbb N_0$ (`prop:s5_continuation`). Memory, bias (a tendency of deviation relative to a reference criterion) and bias strength, effective development freedom, prediction accuracy, effective time horizon, health and similar quantities are connected from time $t$ to $t+1$ as readouts from the state, the internal model, the external environment state or a finite segment of operation records.
- **Minimal relation structure (§6).** One-way and two-way relations with external objects, direction, relation quality relative to an evaluation rule, representative categories and the six-family classification, organized as descriptive, diagnostic and comparative structures that do not by themselves include causal attribution.
- **Blockage and collapse (§7).** Blockage $A_t=\emptyset$ and collapse $\mathrm{Col}_t=1$ are separated; external recoverability, trajectory records, the blockage path set, the collapse-reaching path set and the reaching times are organized.
- **Limited structural application to organizational ACSs (§8).** Groups of ACSs, ACS organizations and organizational ACSs are distinguished. Only when a well-formed 7-tuple structure holds for the organization itself is it treated as an organizational ACS, whether or not individual ACSs participate; organizational ACSs with or without individual-ACS participation are distinguished by the number of participating ACSs. Because the organization-level ACS structure is a realization of the abstract structure type, the definitions of the three principles, blockage, collapse and path sets of the earlier sections are applied at the organization level, and a characterization of organization-level feasible sets, feasible action sets and blockage is given. A universal aggregation rule from individual to organizational quantities, and a general form of judgment rules about organizations, are not given.

### Positioning of the theory (`subsubsec:positioning`)

ACS theory is positioned as a structural theory that describes conditions bearing on the feasibility preservation of an autonomous cognitive system, not as a normative theory that supplies value judgments. The paper does not claim to include or generalize viability theory, convex analysis, dynamical systems theory, control theory, cognitive architectures or other theories. Its relations to existing theories are limited to the consistency and connectability stated in the places where they are described.

What the paper aims to describe is a common form for describing the behavior of an autonomously acting agent, before judging good or bad, as a relation between feasibility requirements and the operation of internal mechanisms. Phase 1 gives the deterministic, structural basis of that form. To what extent the form can describe, in a shareable way, the behavior of agents in different domains and cultures remains as `prob:cross_domain` and `prob:ecit_full`. That the formal results of Phase 1 are empirically valid for humans, organisms, AI, robots and organizations is not derived from this paper alone; the evaluation remains as `prob:cross_domain`.

### Principle of claim strength (`subsubsec:principle_check`)

The paper divides the logical status of each result into definitional consequences, propositions under assumptions, tendency-type descriptions, open problems and so on, and maintains the principle

$$\text{strength of claim}\;\leq\;\text{strength of proof}.$$

For content not derived from a proof or a definition, the paper does not attach, without such grounds, general implication, causal effect, stability, optimality, empirical validity or normative justification. How far the Phase 1 framework serves as a basis for future mathematical study of autonomous cognitive systems and ethical coordinative intelligence is to be evaluated by formal and empirical verification in Phase 2 and later.

**Peaceful use.** The paper and ACS theory are published with peaceful use in mind. That ACS may contribute to exploring cooperative social structures and sustained coexistence between humans and other kinds of intelligence is positioned as an aspiration of the research, not as a consequence proved from Phase 1.

**Position of AI assistance (`rem:ai_assistance`).** The manuscript states that language models were used for assistance in drafting the manuscript, formulas, proof candidates and verification code, for organizing literature candidates, and for checking logical, symbol and reference consistency. The decisions on theoretical adoption, on revision and the final research responsibility belong to the author. The manuscript states that no comprehensive verification of the text and the verification code by independent experts other than the author has been carried out.

---

*Check status.* This summary adds no new definition, assumption or result. The Phase 2 and Phase 3 outlook is a research plan, not a result. Labels in backticks are shared with the manuscript. It has been checked against the manuscript by the drafting model and audited by an external AI model. It remains a draft until the author checks it against the manuscript. No independent human third-party verification is claimed.
