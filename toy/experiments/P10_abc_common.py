# -*- coding: utf-8 -*-
"""Shared text of the P10 specs (experiments A, B, C).  Not a spec itself."""
PURPOSE = ("Experiments A, B, C (descriptive).  A: how far the antecedents of prop:kernel_maintenance "
           "(e_s in E_req(x_s), u_s in U^Viab(x_s)) hold on realised trajectories of the TIPA mechanism.  "
           "B1: finite-time selection tendency of kernel-maintaining responses.  B2: acquisition in the sense of "
           "def:kernel_response_acquisition, decided exactly on periodic backgrounds by recurrence of the joint "
           "state (x, o, M, phase); 'undetermined' otherwise.  C: which antecedent is false at each step (C0 not in "
           "Viab, C1 environment only, C2 selection only, C3 both, OK none), recorded beside the realised outcome "
           "(stay in / leave the kernel) and the events (blockage, leaving K, collapse), each attributed to the class "
           "of the last step spent in the kernel.  The attribution is logical (which antecedent of the proposition "
           "failed), not causal; 'estimate error present' is recorded as co-occurrence only.")
NO_HYPOTHESES = ("No comparative hypothesis is tested.  The only registered check is the regression H1: a step "
                 "classed OK (both antecedents true, x in the kernel) never leaves the kernel (one-step form of "
                 "prop:kernel_maintenance); it can fail only through an implementation error.")
REG = {"id": "H1", "kind": "share", "predicate": "ok_steps_never_leave_kernel",
       "statement": "（回帰検査）両前件が成り立つ時刻（OK）に核から出る例はない（prop:kernel_maintenance の一段の形）。",
       "how_it_could_fail": "判定層または記録の実装に誤りがあれば、OK の時刻に核から出る例が生じる。命題に反するので、"
                            "起こるとすれば実装の誤りに限られる。回帰検査として登録する。",
       "rule": {"support_min": 1.0, "reject_max": 0.999}}
