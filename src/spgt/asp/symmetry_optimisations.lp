% Adapted directly from CFOND-ASP,
% From Nitin Yadav and Sebastian Sardina (2023)

:- next(I,_,J), J > I, J > 1, J != numNodes, not next(K,_,J-1): node(K), K<=I.

lex(E1, E2) :- action(A), effect(A, E1), effect(A, E2), E1 < E2.
:- lex(E1, E2), next(S, E1, J1), next(S, E2, J2), S<J2<J1, J1 != numNodes, {next(S, E3, J2): lex(E3, E2), J2 != numNodes}=0.
