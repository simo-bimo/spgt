% Adapted directly from CFOND-ASP under the MIT License,
% Originally written by Nitin Yadav and Sebastian Sardina (2023).

% Article Citation:
% N. Yadav and S. Sardina, “A Declarative Approach to Compact Controllers for FOND Planning via Answer Set Programming,” in ECAI 2023, IOS Press, 2023, pp. 2818–2825. doi: 10.3233/FAIA230593.
% 
% Repository: 
% https://github.com/ssardina-research/cfond-asp

:- next(I,_,J), J > I, J > 1, J != numNodes, not next(K,_,J-1): node(K), K<=I.

lex(E1, E2) :- action(A), effect(A, E1), effect(A, E2), E1 < E2.
:- lex(E1, E2), next(S, E1, J1), next(S, E2, J2), S<J2<J1, J1 != numNodes, {next(S, E3, J2): lex(E3, E2), J2 != numNodes}=0.
