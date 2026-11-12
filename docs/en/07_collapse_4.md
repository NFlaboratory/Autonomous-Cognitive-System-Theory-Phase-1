# §7 Collapse, blockage and collapse path sets — part 4 of 5 (the collapse-reaching path set)

*Source: `paper/section7_collapse.tex`, lines 3072–3626 (`subsec:col_path_set`: the collapse-reaching path set, the collapse reaching time, relation to the blockage path set, relation between the two reaching times, distinction from other failure-related concepts, complement and Phase 1 limits), at commit e6e12cd. Status: draft. Part 3 is [`07_collapse_3.md`](07_collapse_3.md); part 5 ([`07_collapse_5.md`](07_collapse_5.md), 3627–4834: inflow tendency and the connection to the organizational ACS) follows. §7 defines no assumption. The Japanese manuscript is authoritative; this is a summary, not a translation, and adds no definition, assumption or result.*

---

## The collapse-reaching path set (`subsec:col_path_set`)

Using the same trajectory record space $\mathfrak P$, the subsection defines the set $\mathfrak P_{\mathrm{col}}$ of trajectory records that reach the collapse terminal within finite time. Blockage is a one-time, one-step condition holding within the ACS-record-valid time domain $I_{\mathrm{ACS}}(\sigma)$, whereas collapse is a terminal classification recorded by the collapse indicator $\mathrm{Col}_{i,t}$ kept over all discrete times. Hence $\mathfrak P_{\mathrm{blk}}$ and $\mathfrak P_{\mathrm{col}}$ are subsets of the same space but are determined by different conditions.

### The collapse-reaching path set

**Definition (`def:col_path_set`): collapse-reaching path set (classification C).** The *collapse-reaching path set* $\mathfrak P_{\mathrm{col}}\subseteq\mathfrak P$ is
$$\mathfrak P_{\mathrm{col}}:=\{\sigma\in\mathfrak P\mid \exists T\in\mathbb N_0\ \text{s.t.}\ \mathrm{Col}_{i,T}=1\}.$$
It is the totality of trajectory records in which the collapse indicator $\mathrm{Col}_{i,T}=1$ holds at some finite time $T$. The subscript $\mathrm{col}$ stands for collapse.

**No blockage is required (`rem:col_path_no_blockage_requirement`).** For $\sigma\in\mathfrak P_{\mathrm{col}}$ it suffices that $\mathrm{Col}_{i,T}=1$ holds at some finite time; the definition does not require that $A_{i,t}=\emptyset$ held before. This is consistent with `subsec:collapse_def`, where blockage was not made a prior requirement of collapse.

### The collapse reaching time

**Definition (`def:col_reaching_time`): collapse reaching time (classification C).** For $\sigma\in\mathfrak P_{\mathrm{col}}$,
$$T_{\mathrm{col}}(\sigma):=\min\{T\in\mathbb N_0\mid \mathrm{Col}_{i,T}=1\}$$
is called the *collapse reaching time* of $\sigma$. The set is non-empty by `def:col_path_set` and $\mathbb N_0$ is well-ordered, so the minimum exists and $T_{\mathrm{col}}(\sigma)$ is a finite natural number.

**Indicator after the reaching time (`rem:col_reaching_time`).** By the absorption condition (C-2) of `prop:collapse_basic`, $t\ge T_{\mathrm{col}}(\sigma)$ implies $\mathrm{Col}_{i,t}=1$, so $T_{\mathrm{col}}(\sigma)$ is the time at which the collapse terminal record first holds. The blockage reaching time $T_{\mathrm{blk}}(\sigma)$ of `subsec:blk_path_set` is only the first blockage time and carries no statement about later persistence of blockage; in this sense $T_{\mathrm{blk}}$ and $T_{\mathrm{col}}$ are reaching times of different types.

**Reaching time and the valid time domain (`rem:col_time_and_valid_domain`).** Let $\sigma\in\mathfrak P_{\mathrm{col}}$ with $T_{\mathrm{col}}(\sigma)=T$. By `def:acs_valid_time_domain`, $I_{\mathrm{ACS}}(\sigma)=\{0,1,\dots,T-1\}$ if $T\ge1$, and $I_{\mathrm{ACS}}(\sigma)=\emptyset$ if $T=0$. Hence $T_{\mathrm{col}}(\sigma)\notin I_{\mathrm{ACS}}(\sigma)$: the ordinary ACS state quantities $x_T$, $e_T$, $A_{i,T}$, $\mathrm{Desc}_T$ are not required at the collapse reaching time. With this terminal convention there is no need to assign an artificial ordinary ACS state to the collapse time.

### Relation to the blockage path set

**They are in general different objects (`rem:col_vs_blk`).** $\mathfrak P_{\mathrm{blk}}$ is the set of records in which $A_{i,t}=\emptyset$ holds at least once within the valid time domain, and $\mathfrak P_{\mathrm{col}}$ is the set of records with $\mathrm{Col}_{i,t}=1$ at some finite time. Since they are determined by different formal conditions, Phase 1 assumes none of $\mathfrak P_{\mathrm{blk}}\subseteq\mathfrak P_{\mathrm{col}}$, $\mathfrak P_{\mathrm{col}}\subseteq\mathfrak P_{\mathrm{blk}}$, or $\mathfrak P_{\mathrm{blk}}=\mathfrak P_{\mathrm{col}}$. This paper does not state, from the definitions and assumptions of the section alone, an inclusion in either direction or equality as a general consequence.

**Trajectories that reach blockage but not collapse are allowed (`rem:blk_without_collapse_path`).** As stated in `subsec:blockage` and `subsec:collapse_def`, this paper does not state $\mathrm{Col}_{i,t}=1$ from blockage as a general consequence. Correspondingly Phase 1 does not exclude trajectory records in $\mathfrak P_{\mathrm{blk}}\setminus\mathfrak P_{\mathrm{col}}$: records that reach blockage within finite time and for which the collapse indicator is never $1$ at any finite time. Such records may include subsequent recovery. It is not claimed that this difference set is non-empty; its non-emptiness depends on the dynamics of the system, the environment realization (the sequence of background components and $g_O$), external recoverability and so on.

**Trajectories that reach collapse without blockage are allowed (`rem:col_without_blk_path`).** Since blockage was not made a prior requirement of collapse, Phase 1 does not exclude, at the level of path sets, records in $\mathfrak P_{\mathrm{col}}\setminus\mathfrak P_{\mathrm{blk}}$: records in which $A_{i,t}\ne\emptyset$ for all $t\in I_{\mathrm{ACS}}(\sigma)$ before $T_{\mathrm{col}}(\sigma)$, yet the collapse terminal is reached within finite time. Again it is not claimed that this difference set is non-empty.

**Intersection (`rem:blk_col_intersection`).** A record in $\mathfrak P_{\mathrm{blk}}\cap\mathfrak P_{\mathrm{col}}$ experiences blockage at least once within the valid time domain before collapse and reaches the collapse terminal within finite time. Even then, this paper does not state as a consequence of the definitions that blockage is the cause of collapse, that blockage is sufficient for collapse, or that blockage persisted continuously after the first blockage. The intersection of the sets expresses co-occurrence, not causation.

### Relation between the two reaching times

**Order of $T_{\mathrm{blk}}$ and $T_{\mathrm{col}}$ (`rem:blk_col_time_relation`).** For $\sigma\in\mathfrak P_{\mathrm{blk}}\cap\mathfrak P_{\mathrm{col}}$, $T_{\mathrm{blk}}(\sigma)$ belongs to $I_{\mathrm{ACS}}(\sigma)$ while $T_{\mathrm{col}}(\sigma)$ does not. Under the terminal convention of `subsec:blk_path_set`, therefore, $T_{\mathrm{blk}}(\sigma)<T_{\mathrm{col}}(\sigma)$ holds. This does not mean that blockage is a cause or a requirement of collapse. It is an order in type: when one trajectory belongs to both sets, blockage is recorded at a time at which ordinary ACS records are valid, and collapse is recorded as a later terminal time that ends that ordinary record domain.

### Collapse reaching and other failure-related concepts

**Loss of well-formed realization (`rem:wf_not_col_path`).** This paper does not state $\sigma\in\mathfrak P_{\mathrm{col}}$ as a general consequence from $\mathrm{WF}_{i,t}=0$ at some time. As stated in `subsec:collapse_def`, it does not state $\mathrm{Col}_{i,t}=1$ from $\mathrm{WF}_{i,t}=0$. Loss of well-formed realization is therefore not a condition of membership in $\mathfrak P_{\mathrm{col}}$; membership requires that $\mathrm{Col}_{i,T}=1$ actually holds at a finite time.

**False satisfaction predicates, T-STAB, relation quality (`rem:principles_not_col_path`).** This paper does not state $\sigma\in\mathfrak P_{\mathrm{col}}$ as a general consequence from any of the SM, EU or FR predicates being false at a time or on a finite window, from failure of T-STAB, from relation quality $Q<0$, or from $\chi_{\mathrm{EI},t}=0$, alone. These are not defining conditions of membership in $\mathfrak P_{\mathrm{col}}$. Their descriptive connection with inflow into pre-collapse states is treated in `subsec:inflow_paths`.

**Outside the robust viability kernel (`rem:viab_outside_not_col_path`).** This paper does not state $\sigma\in\mathfrak P_{\mathrm{col}}$ as a general consequence from $x_t\notin\mathrm{Viab}_f(K)$ at some time. Being outside the kernel means that long-term robust invariance with respect to $E_{\mathrm{req}}$ is not established; this paper does not state from it that the collapse terminal is reached within finite time.

### Complement and Phase 1 limits

**The complement $\mathfrak P\setminus\mathfrak P_{\mathrm{col}}$ (`rem:col_avoidance`).** The complement is the set of trajectory records in which $\mathrm{Col}_{i,t}=1$ holds at no finite time. Since the collapse indicator is binary (`def:collapse`), it coincides with the set of records with $\mathrm{Col}_{i,t}=0$ for all $t\in\mathbb N_0$. This paper does not state, from membership in the complement, that blockage is never experienced, that the SM, EU and FR predicates are true at all times at which they are defined, that well-formed realization holds at every time, or that the trajectory stays inside the robust viability kernel.

**Phase 1 limits (`rem:col_phase1_scope`).** Phase 1 only defines $\mathfrak P_{\mathrm{col}}$ as a set-theoretic subset of $\mathfrak P$. This paper does not in general define a measure, probability, topological boundary, density, distance, basin of attraction or "closeness to collapse" of $\mathfrak P_{\mathrm{col}}$. Nor does Phase 1 give a general procedure that predicts, from observation up to a finite time, that a record will later belong to $\mathfrak P_{\mathrm{col}}$. As stated in `subsec:collapse_def`, the definition of collapse in theory and its decidability from finite observation are separate matters.

---

*Check status.* This summary adds no new definition, assumption or result. Labels in backticks are shared with the manuscript. It has been checked against the manuscript by the drafting model and audited by an external AI model. It remains a draft until the author checks it against the manuscript. No independent human third-party verification is claimed.
