#const numNodes = 2.

node(0..numNodes).
{policy(N, A): action(A)} = 1:- node(N), N != numNodes.

% Nodes are placed in a line, since it is a weak-plan,
% and only consider one outgoing effect.
{next(N, E, N+1): effect(A,E)} = 1:- policy(N, A), node(N), N!= numNodes.

holds(numNodes, F) :- goal(F).
holds(N, F):- policy(N, A), prec(A, F).

use_reg(N, F):- holds(N, F), F=has_value(Var, Val).
use_reg(N, F):- holds(N, F), F=neg(G).
use_reg(N, F):- holds(N, F), F=yest(G).
use_reg(N, F):- holds(N, F), F=since(G, H).
use_reg(N, F):- holds(N, F), F=dual_since(G, H).

holds(N, G):- holds(N, F), F=conj(G, H).
holds(N, G):- holds(N, F), F=conj(H, G).

1{holds(N, G); holds(N, H)}:- holds(N,F), F=disj(G, H).

% Calls the python @reg function to calculate the regression.
holds(N1, @reg(F, E)) :- next(N1, E, N2), use_reg(N2, F).

% Contradictory or unsatisfiable formulae cannot hold.
:- holds(N, G), holds(N, H), G=has_value(Var,A), H=has_value(Var,B), A!=B.
:- holds(N, G), holds(N, F), F=neg(G).
:- holds(_, falsum).

% To ensure that the initial state does actually satisfy it.
:- holds(0, F), F=has_value(Var,Val), not init(Var,Val).
:- holds(0, F), F=neg(has_value(Var,Val)), init(Var,Val).

% Prevent any claims of things being true yesterday if there are no previous states.
:- holds(0, F), F=yest(G).