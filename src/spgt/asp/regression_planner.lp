node(0..k).
{policy(N, A): action(A)} = 1:- node(N), N != k.
{next(N1, E, N2): node(N2)} = 1:- policy(N1, A), effect(A, E).

% Choice and constraints on assigning atoms.
{holds_atom(N, P): state(N)}.
:- next(N1, E, N2), holds_atom(N2, P), del(E, P).
:- next(N1, E, N2), holds_atom(N2, P), not add(E, P), not holds_atoms(N1, P).

holds(N, F) :- policy(N, A), prec(A, F).

holds_atom(N, P) :- holds(N, F), atomic(F, P).

holds(N, G); holds(N, H):- holds(N, F), F=conj(G, H).

1{holds(N, G); holds(N, H); use_reg(N, F)}:- holds(N,F), F=disj(G, H).

% We need to generate the regression for every incoming effect.
query_reg(F, E) :- use_reg(N, F), next(_, E, N).

% N2 demands regression be used to satisfy F,
% so we ensure N1 satisfies the regression.
holds(N1, R) :- next(N1, E, N2), use_reg(N2, F), reg(R, F, E).

-holds(0, P):- atom(P), not init(P).
holds(k, F):- goal(F).

reachableG(N):- node(N), N=k.
reachableG(N):- next(N, _, N1), reachableG(N1).
:- not reachableG(N), node(N).