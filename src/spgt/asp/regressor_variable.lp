% TODO: Consider placing a bound on how many times a formula can be regressed.
% It should never need to be regressed more than k times.

query_reg((G;H),E) :-
	query_reg(F,E),
	F=disj(G,H).
	
query_reg((G;H),E) :-
	query_reg(F,E),
	F=conj(G,H).

% Dissolve / propagate constants upwards.
% There is surely a way to make this more compact.
% For disjunctions:
reg(FR, F, E) :-
	query_reg(F,E),
	reg(GR,G,E),
	reg(HR,H,E),
	GR = verum,
	1{F=disj(G,H); F=disj(H,G)},
	FR=verum.
	
reg(FR, F, E) :-
	query_reg(F,E),
	reg(GR,G,E),
	reg(HR,H,E),
	GR = falsum,
	HR != verum,
	1{F=disj(G,H); F=disj(H,G)},
	FR=HR.

% For conjunctions
reg(FR, F, E) :-
	query_reg(F,E),
	reg(GR,G,E),
	reg(HR,H,E),
	GR = verum,
	1{F=conj(G,H); F=conj(H,G)},
	FR=HR.
	
reg(FR, F, E) :-
	query_reg(F,E),
	reg(GR,G,E),
	reg(HR,H,E),
	GR = falsum,
	HR != verum,
	1{F=conj(G,H); F=conj(H,G)},
	FR=falsum.

% No constants involved.
reg(FR, F, E) :-
	query_reg(F,E),
	reg(GR,G,E),
	reg(HR,H,E),
	GR != verum,
	GR != falsum,
	HR != verum,
	HR != falsum,
	F=disj(G, H),
	FR=disj(GR, HR).
	
reg(FR, F, E) :-
	query_reg(F,E),
	reg(GR,G,E),
	reg(HR,H,E),
	GR != verum,
	GR != falsum,
	HR != verum,
	HR != falsum,
	F=conj(G, H),
	FR=conj(GR, HR).
	
% Regression atoms
reg(verum, P, E) :-
	query_reg(P, E),
	P=has_value(Variable, Value),
	add(E, Variable, Value).

reg(falsum, P, E) :-
	query_reg(P, E),
	P=has_value(Variable, Value),
	del(E, Variable, Value).

reg(P, P, E) :-
	query_reg(P, E),
	P=has_value(Variable, Value),
	not add(E, Variable, Value),
	not del(E, Variable, Value).

% Regression Neg. Literals.
reg(verum, F, E) :-
	query_reg(F, E),
	F=neg(P),
	P=has_value(Variable, Value),
	del(E, Variable, Value).
	
reg(falsum, F, E) :-
	query_reg(F, E),
	F=neg(P),
	P=has_value(Variable, Value),
	add(E, Variable, Value).
	
reg(F, F, E) :-
	query_reg(F, E),
	F = neg(P),
	P=has_value(Variable, Value),
	not add(E, Variable, Value),
	not del(E, Variable, Value).