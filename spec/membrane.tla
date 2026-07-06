---------------------------- MODULE membrane ----------------------------
(* R2d - grade: DECLARED. A formal sketch of D1 section 8 (the membrane laws)
   for TLC model checking. NOT machine-checked by this repo's gate: TLC needs
   Java, and the gate is stdlib-only by law. To check:  tlc membrane.tla
   (with membrane.cfg). If TLC ever joins CI, this row upgrades to MEASURED;
   until then the model is a precise statement, not a proof. declared != verified. *)
EXTENDS Naturals, Sequences

CONSTANTS Keys, Vals, Init0
VARIABLE chain  \* sequence of stores, newest first; a store = [Keys -> Vals]

Init == chain = << Init0 >>

(* Observing never perturbs: a view is indistinguishable from stuttering. *)
View == UNCHANGED chain

(* An edit is a NEW world prepended; the old world remains, unchanged. *)
Edit(k, v) == chain' = << [Head(chain) EXCEPT ![k] = v] >> \o chain

(* Anamnesis returns the exact prior world - pop, no reconstruction. *)
Ana == /\ Len(chain) > 1
       /\ chain' = Tail(chain)

Next == View \/ Ana \/ \E k \in Keys, v \in Vals : Edit(k, v)
Spec == Init /\ [][Next]_chain

(* Laws, as action properties (check as PROPERTY in TLC): *)
PutGetLaw  == [][\A k \in Keys, v \in Vals :
                  Edit(k, v) => (Head(chain'))[k] = v]_chain
AnaExactLaw == [][(Len(chain) > 1 /\ Ana) => Head(chain') = chain[2]]_chain
LineageLaw  == [][\A k \in Keys, v \in Vals :
                  Edit(k, v) => Tail(chain') = chain]_chain

(* History is never rewritten: every reachable past store is a value forever. *)
Immutable == [][\A i \in 2..Len(chain) :
                 i =< Len(chain') => chain'[i] \in {chain[j] : j \in 1..Len(chain)}]_chain
==========================================================================
