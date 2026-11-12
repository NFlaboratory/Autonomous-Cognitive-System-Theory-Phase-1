# §4 TIPA, PSL and ISL — part 4 of 4 (`subsec:impl`, `subsec:fast_processing`, `subsec:functional_axis`, `subsec:s4_summary`)

*Source: `paper/section4_tipa.tex`, lines 2350–2964 (the Implementation Substrate Layer ISL; integrated high-speed processing and Automaticity, with the five functional memory sets; the functional axis; the closing summary of §4 with its figure), at commit `e6e12cd`. The Japanese manuscript is authoritative. Part 4 of §4 follows [`04_tipa_3.md`](04_tipa_3.md) and completes §4. §5 (the connection between time steps) begins in [`05_dynamics_1.md`](05_dynamics_1.md).*

---

## ISL: the Implementation Substrate Layer (`subsec:impl`)

ISL is a classification-B standard functional form that organizes, by functional role, the implementation elements of an ACS that can bear sensing, acting, information retention and other functions. No particular organ, electronic component, software module or arrangement is a general requirement.

**Definition (`def:impl_layer`): ISL (classification B).** The set of all implementation elements of the ACS is $\mathcal B_\Sigma$. As the main standard subsets, $B_{\mathrm{sens}},B_{\mathrm{eff}},B_{\mathrm{mem}}\subseteq\mathcal B_\Sigma$ are placed, the sets of implementation elements that can bear sensing, action and information retention respectively. Neither mutual exclusivity nor exhaustiveness by the three sets is required in general.

### Sensing role (`subsubsec:sensor`)

**Definition (`def:sensor`): sensing implementation role (classification B).** $B_{\mathrm{sens}}$ is the set of implementation elements that can carry changes, external or internal, as signals available to PSL-1.

**Distinction of the sensing role and M1 (`rem:sensor_distinction`).** $B_{\mathrm{sens}}$ is a role on the implementation side that can carry information acquisition; it is not the information integration or discrimination of M1 itself.

### Effector role (`subsubsec:effector`)

**Definition (`def:effector`): effector implementation role (classification B).** $B_{\mathrm{eff}}$ is the set of implementation elements that can carry the effective action determined by PSL as an action on the outside or the inside.

**Distinction of the effector role from M3 and PSL (`rem:effector_distinction`).** $B_{\mathrm{eff}}$ is the implementation carrier of action; it is not identical with M3, which forms the action command, or with PSL, which resolves the effective action.

### Memory role (`subsubsec:mem_substrate`)

**Definition (`def:mem_substrate`): memory implementation role (classification B).** $B_{\mathrm{mem}}$ is the set of implementation elements that can hold past information in a state reusable at later times. The concrete medium, coding method, distributed arrangement and retention period depend on the implementation.

**Distinction of the memory role and the internal model (`rem:mem_model_distinction`).** $B_{\mathrm{mem}}$ is an implementation carrier; it is not the internal model $M_t$, the state history or the five functional memory sets themselves.

### Connection of ISL and PSL (`subsubsec:impl_connection`)

**Definition (`def:impl_psl_connection`): connection convention of ISL and PSL (classification B).** The connection of ISL and PSL is fixed not as fixed anatomical wiring or hardware topology but as a functional relation based on the availability of `def:psl_availability`. Conceptually the directions $B_{\mathrm{sens}}\to\mathrm{PSL\text{-}1}\to\mathrm{TIPA}$ and $\mathrm{TIPA}\to\mathrm{PSL}\to B_{\mathrm{eff}}$ are allowed, and for memory a relation of use $B_{\mathrm{mem}}\leftrightarrow\mathrm{PSL}\leftrightarrow\mathrm{TIPA}$ is allowed.

For PSL-4, the span from the acquisition of a local signal to the realization of a local protective response can be carried on ISL as a local connection that does not take completion of detailed TIPA processing at the same time as a necessary condition. The responsibilities of M3, PSL and ISL are thus distinguished as: M3 action command $\to$ effective-action resolution by PSL $\to$ action on ISL.

### Existence, activity and health (`subsubsec:impl_state_distinction`)

**Existence, activity and health of implementation elements (`rem:impl_exist_activity`).** That an implementation element exists, that it is active at the time, and that it is healthy are mutually different. This paper therefore does not state, from a particular element of ISL being stopped or unhealthy alone, $A_t=\emptyset$ or $\mathrm{Col}_{i,t}=1$ as a general consequence.

### Minimal structural condition of ISL (`subsubsec:impl_minimal_conditions`)

**Assumption (`ass:impl_structure`): structural assumption on the implementation layer.** The ISL of an ACS treated in this subsection has a structure able to carry the necessary implementation roles, such as sensing, action and information retention across times. The same element may bear several roles, and the existence of an independent organ, component or module for each role is not required.
*Introduction status: S (structural). Strength: medium.* The assumption limits the range of ACSs to which the standard form of ISL in `subsec:impl` applies, and is not used as a premise of a proposition of this subsection.

---

## Integrated high-speed processing and Automaticity (`subsec:fast_processing`)

This subsection distinguishes the low-latency cross-cutting forms of operation that the existing structures of TIPA, PSL and ISL can take from forms of operation with low dependence on detailed re-evaluation and re-comparison. No new cognitive mechanism or mechanism level is introduced.

### Position of integrated high-speed processing (`subsubsec:fast_position`)

**Definition (`def:integrated_fast_processing`): integrated high-speed processing (classification B).** Integrated high-speed processing is a form of operation in which, in the existing functional structure centered on TIPA, response formation can proceed while two conditions hold: (1) dependence on detailed re-evaluation and re-comparison is lower than in the corresponding detailed processing; (2) the effective delay up to the formation of the action command is lower than in the corresponding detailed processing in the implementation concerned. Phase 1 places no universal time threshold, computation-amount threshold or comparison-count threshold.

**High-speed processing is not an independent component (`rem:fast_not_component`).** Integrated high-speed processing is not required as an independent mechanism, an independent layer or a fixed dedicated route added to TIPA, PSL and ISL.

### Cross-level character and responsibility boundary (`subsubsec:fast_cross_layer`)

**Definition (`def:fast_cross_layer`): cross-level character of high-speed processing (classification C).** Integrated high-speed processing can hold through the contribution of one or more existing functions of TIPA, PSL and ISL to lower latency.

**High-speed processing does not substitute for the responsibilities of TIPA (`rem:fast_no_tipa_substitution`).** Lower latency does not mean that the responsibilities of M1, M2 and M3 move to PSL or ISL.

### Automaticity (`subsubsec:automaticity`)

**Automaticity and dependence on deliberation (`rem:automaticity_deliberation`).** Automaticity is a form of operation in which the information processing or action formation at the time holds while its dependence on the corresponding detailed re-evaluation and re-comparison remains relatively low. It is treated in this subsection as a classification-B form of operation; it is not introduced as an independent mechanism, an independent route, a new operating mode of M3 or an independent scalar state variable. No universal binary boundary is placed between Automaticity and deliberative operation.

**Non-identity of high speed, Automaticity and PSL-4 (`rem:automaticity_fast_psl4`).** Integrated high-speed processing, Automaticity and PSL-4 are mutually different functional concepts. Low latency and lowered dependence on detailed re-evaluation are separate conditions of `def:integrated_fast_processing`, and this paper does not state either from the other as a general consequence. PSL-4 is the standard form of a protective response to a local acute abnormality and does not represent Automaticity in general. The three are therefore distinguished in the range of concepts they treat and are not identified with one another.

**Implementation events versus functional concepts (`rem:structural_operation_implementation_event`).** This paper does not state, from muscle contraction, firing of neural or electronic signals, crosstalk, noise, malfunction, a hardware interrupt, unintended operation of an actuator or the like being fast, local, involuntary or non-deliberative alone, the holding of integrated high-speed processing, Automaticity or PSL-4 as a general consequence. To classify under each concept, the input–processing–output functional relation specific to it must hold.

### Five functional memory sets supporting high-speed processing (`subsubsec:fast_memory`)

**Definition (`def:fast_memory_sets`): five functional memory sets (classification B).** The index set of memory roles is $\mathcal L:=\{\mathrm{rout},\mathrm{sal},\mathrm{err},\mathrm{eval},\mathrm{resp}\}$. For each $\ell\in\mathcal L$ a non-empty universe $\mathfrak T_\ell$ is placed, and the content retained at time $t$ and classified by functional role is $\mathcal T_{\ell,t}\subseteq\mathfrak T_\ell$. $\mathcal T_{\mathrm{rout},t}$ is the retained content related to repetition and routine, $\mathcal T_{\mathrm{sal},t}$ to salience, $\mathcal T_{\mathrm{err},t}$ to error and abnormality, $\mathcal T_{\mathrm{eval},t}$ to evaluation, and $\mathcal T_{\mathrm{resp},t}$ to response. To make the carrier of retained content explicit, a fixed map $\rho_\ell:\mathcal M^{\mathrm L}\to\mathcal P(\mathfrak T_\ell)$ is given, with $\mathcal T_{\ell,t}=\rho_\ell(M_t^{\mathrm L})$. Retention is distinguished from successful readout and use at the time. Empty-set values are allowed, and neither a topology on the power set nor continuity of readouts is required.

**Non-exclusivity and non-exhaustiveness of the five sets (`rem:fast_memory_nonexclusive`).** The five sets need not be mutually exclusive; the same retained content may belong to several. Nor is it required that the five sets exhaust all retained content of the ACS. This paper does not state, from a set being empty alone, the absence of the corresponding function, blockage or collapse as a general consequence.

**No fixed correspondence of the five memory sets and the TIPA mechanisms (`rem:fast_memory_no_fixed_mapping`).** The five memory roles are not fixedly allocated one-to-one to any of M1, M2 and M3.

**Five memory sets and the ISL memory role (`rem:fast_memory_isl`).** $\mathcal T_{\ell,t}$ is a functional classification of retained content, and one-to-one correspondence with physical or computational subsets of $B_{\mathrm{mem}}$ is not required.

### Conditions for high-speed processing and non-claims (`subsubsec:fast_conditions`)

**Assumption (`ass:fast_structural_consistency`): structural consistency under high-speed processing.** Also when integrated high-speed processing holds, the type consistency of TIPA, the necessary generation dependence, the responsibility boundaries of TIPA, PSL and ISL, and the formation of a single effective action are maintained.
*Introduction status: S (structural). Strength: medium.* The assumption limits the range of ACSs to which the standard form of integrated high-speed processing in `subsec:fast_processing` applies, and is not used as a premise of a proposition of this subsection.

**High speed versus accuracy (`rem:fast_not_accuracy`).** This paper does not state, from processing being fast, the accuracy, optimality or safety of estimation, evaluation, Priority or response selection, or the truth of a time-indexed satisfaction predicate of the three principles, as a general consequence.

**Not fixing the boundary levels of high speed uniquely (`rem:fast_boundary_levels`).** Low latency is relative to the implementation of the ACS, the task and the detailed processing used as comparison. The boundary between integrated high-speed processing and detailed processing is therefore an implementation-dependent descriptive division, and no universal time, computation-amount or comparison-count threshold is given.

### Delegation to inter-time dynamics (`subsubsec:fast_boundary`)

This subsection fixes the same-time position of integrated high-speed processing and Automaticity. The update of the five functional memory sets, the formation, strengthening and weakening of integrated high-speed processing, the increase, decrease and release of Automaticity and other inter-time changes are left to §5 (`sec:extended_dynamics`). The formation of Automaticity is not assumed to be a one-directional or irreversible process.

---

## The functional axis: a cross-cutting descriptive and diagnostic quantity (`subsec:functional_axis`, `subsubsec:functional_axis`)

**Definition (`def:functional_axis`): functional axis (classification C).** The quantity describing the main operating levels of TIPA, PSL and ISL across them is
$$F_t:=(F_{\mathrm{M1},t},F_{\mathrm{M2},t},F_{\mathrm{M3},t},F_{\mathrm{PSL},t},F_{\mathrm{ISL}_{\mathrm{sens}},t},F_{\mathrm{ISL}_{\mathrm{mem}},t},F_{\mathrm{ISL}_{\mathrm{eff}},t})\in[0,1]^7,$$
called the functional axis. Each component is a normalized classification-C descriptive and diagnostic scale; a universal measurement map, a common unit across components, and direct comparability across different ACSs are not required. When a fixed readout $\mathrm{rd}_F:X\times\mathcal M\times E_{\mathrm{ext}}\to[0,1]^7$ is used per object and $F_t=\mathrm{rd}_F(x_t,M_t,e_t)$, no independent state or update rule is added. For a diagnosis not determined by the present carriers alone, a readout on trajectories is specified separately. The rule does not require an internal diagnosis to know the theoretical values.

**Functional axis and health (`rem:psl_health_bridge_s5`).** $F_t$ is a quantity describing the operating level at the same time and is a classification-C quantity distinct from the PSL and ISL health quantities treated in §5 (`sec:extended_dynamics`). This subsection places no general functional relation between the two.

**Non-identity of the functional axis with blockage and collapse (`rem:functional_axis_noncollapse`).** This paper does not state, from a particular value of the functional axis alone, blockage or collapse as a general consequence. In particular, from $F_t=(0,\dots,0)$ neither $A_t=\emptyset$ nor $\mathrm{Col}_{i,t}=1$ is stated as a general consequence. Blockage is judged by the definition of §2 concerning the feasible action set, and collapse by `def:collapse` of §2. This subsection does not define $\mathrm{Col}_{i,t}$, and no collapse judgment is made from the functional axis.

**Definition (`def:s4_primitive_composition`): composition correspondence with the standard operation form (classification B).** In the standard form of this section, $\mathcal R_{\mathrm{int}}=\mathcal I\times\mathsf S_{M1}$ and $\mathcal V=\mathcal P_{\mathrm{prio}}\times\mathfrak E\times\mathsf{Sig}\times\mathfrak E^{\mathrm{rq}}_{\mathrm{map}}$ may be made concrete. $P_{\mathrm{disc}}(M,I)$ is the pair of $I$ and the M1 output formed by reading retained records; $P_{\mathrm{val}}(M,r)$ is the M2 output for that M1 output and the retained history; $P_{\mathrm{act}}(M,r,v)$ is the effective action obtained by resolving, with PSL, the M3 command, the local signal retained in $r$, and $\Phi_R(M,I)$. Replacing the local signal by an estimate of M1 is not required. This concretization is not a one-to-one correspondence between functional divisions and mechanisms; it is a connection for fitting a composition of fixed total maps into the types of the standard maps. The non-degeneracy of §2 is to be checked separately for this composition. This paper does not state, from each mechanism of this section satisfying its type alone, its non-degeneracy as a general consequence.

---

## Summary of §4 (`subsec:s4_summary`)

This section formulated the functional structure of a single ACS at one time from three functional levels, TIPA, PSL and ISL.

- **TIPA.** The information-generation dependence $M_1\to M_2\to M_3$ is placed, and each mechanism is decomposed into three functions: M1 into information integration, boundary management and integration of temporal continuity; M2 into feasibility-threat detection, structural-vulnerability evaluation and latent-instability evaluation; M3 into construction of information for response formation, candidate formation and comparison, and determination of the action command. M2 gives Priority, internal evaluation information, the request signal and the request-by-object evaluation as evaluation by the persistence criterion, and M3 gives the operating mode, purposes, the state of purposes and the action command as a judgment through evaluation by the purpose criterion. Within one time only the above direction of information dependence is placed, and sending and receiving in the reverse direction is expressed at the next time through retained records.
- **PSL.** Input acquisition, output realization, substrate maintenance, the protective response to a local acute abnormality, sensitivity control and effective-action resolution were fixed. The self-attribution of purposes, the involvement of requests, the classification of actions and the description of the result of one action were also given (`subsec:purpose_action_result`).
- **ISL.** The implementation elements that can bear sensing, action and information retention were organized without fixing them to particular biological organs or artificial components.

The standard same-time functional relation of a single ACS is thus organized conceptually as: information acquisition on ISL $\to$ making it available by PSL $\to M_1\to M_2\to M_3\to$ effective-action resolution by PSL $\to$ action on ISL $\to$ state transition.

**Figure (`fig:s4_same_time`).** The figure shows the types of the maps and the connections including the PSL-4 route that does not pass through TIPA. It has two panels joined by the values of the same time $t$. Panel (a) shows the formation of input and response at time $t$: $\rho_{\mathrm{in}}$, $\Phi_{\mathrm{sense}}$ and $\Gamma_{\mathrm{in},t}$ within PSL-1 give $I_t$; $I_t$ enters M1; the outputs of M1 enter M2 and M3, the outputs of M2 enter M3, and readouts of the retained content $M_t$ enter the three mechanisms; $\rho_{\mathrm{local}}$ and $\Phi_{\mathrm{prot}}$ of PSL-4 give $r_{\mathrm{local},t}$ without using TIPA outputs; $\Phi_R$ gives $R_t$; and M3 gives $u_{\mathrm{M3},t}$. Panel (b) shows the resolution of the effective action by $\Phi_{\mathrm{resolve}}$ into $u_t$, the connection through $\Phi_{\mathrm{action}}$ and $\Gamma_{\mathrm{out},t}$ to the drive signal, and the maps to time $t+1$ by $\mathrm{Update}$, $f$ and $g_O$. The bold arrows are information-generation dependence and not an execution order; the boxes are functional forms, maps, signals or implementation roles and do not express one-to-one correspondence with physical parts; $B_{\mathrm{sens}},B_{\mathrm{eff}},B_{\mathrm{mem}}\subseteq\mathcal B_\Sigma$ carry no requirement of exclusivity or exhaustiveness. The inputs from $M_t$ to the three mechanisms are readouts of retained records (`def:s4_carrier_contract`). Inter-time influence is limited to retained content and to the route through changes of state and external environment state into the sensing at the next time; no route from the output of M3 to the input of M2 is placed (`rem:m2_no_return_scope`). The local protective response is generated without TIPA outputs (`rem:psl4_concurrency`), and the local-response component of the effective action follows it (`def:effective_action_resolve`). The connection that includes the substrate information of PSL-3 and the memory-implementation output in the sensed information is omitted because it depends on the adopted realization.

Integrated high-speed processing, Automaticity and PSL-4 were distinguished as mutually different functional concepts, and the content that high-speed processing can use was organized as the five functional memory sets. The main operating levels of TIPA, PSL and ISL were also described across them by the functional axis $F_t$.

The next section (§5) does not redefine the structure fixed here; it treats how memory, internal quantities, health, integrated high-speed processing, Automaticity and others can change from $t$ to $t+1$.

---

*Check status.* This summary adds no new definition, assumption or result. Labels in backticks are shared with the manuscript. It has been checked against the manuscript by the drafting model and audited by an external AI model. It remains a draft until the author checks it against the manuscript. No independent human third-party verification is claimed.
