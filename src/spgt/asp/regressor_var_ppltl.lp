reg_depth(F, 0) :- prec(F, A).
reg_depth(F, 0) :- goal(F).
reg_depth((G;H), C) :- reg_depth(F, C), F=conj(G, H).
reg_depth((G;H), C) :- reg_depth(F, C), F=disj(G, H).
reg_depth((G;H), C) :- reg_depth(F, C), F=since(G, H).
reg_depth((G;H), C) :- reg_depth(F, C), F=dual_since(G, H).
reg_depth(G, C) :- reg_depth(F, C), F=neg(G).

reg(FR, F, E) :- reg(FR, F, E, _).
reg_depth(FR, C) :- reg(FR, _, _, C).

query_reg((G;H), E) :-
	query_reg(F, E),
	F=disj(G, H).
	
query_reg((G;H), E) :-
	query_reg(F, E),
	F=conj(G, H).
	
query_reg(UF, E) :-
	query_reg(F, E),
	% The one-step unfolding of F.
	UF = disj(B, conj(A, yest(since(A, B)))),
	F = since(A, B).
	
query_reg(UF, E) :-
	query_reg(F, E),
	% The one-step unfolding of F.
	UF = conj(B, disj(A, yest(dual_since(A, B)))),
	F = dual_since(A, B).

% PPLTL
reg(FR, F, E, C+1) :-
	query_reg(F, E),
	F = yest(G),
	FR = G,
	reg_depth(F, C).

% the regression of since is the
% regression of the one-step unfolding,
reg(FR, F, E, C+1) :-
	query_reg(F, E),
	reg(FR, UF, E),
	UF = disj(B, conj(A, yest(since(A, B)))),
	F = since(A, B),
	reg_depth(F, C).

% the regression of the dual of since 
% is the regression of the one-step unfolding,
reg(FR, F, E, C+1) :-
	query_reg(F, E),
	reg(FR, UF, E),
	UF = conj(B, disj(A, yest(dual_since(A, B)))),
	F = dual_since(A, B),
	reg_depth(F, C).

% Dissolve / propagate constants upwards,
% There is surely a way to make this more compact,
% For disjunctions:
reg(FR, F, E, C+1) :-
	query_reg(F, E),
	reg(GR, G, E),
	reg(HR, H, E),
	GR = verum,
	1{F=disj(G, H); F=disj(H, G)},
	FR=verum,
	reg_depth(F, C).
	
reg(FR, F, E, C+1) :-
	query_reg(F, E),
	reg(GR, G, E),
	reg(HR, H, E),
	GR = falsum,
	HR != verum,
	1{F=disj(G, H); F=disj(H, G)},
	FR=HR,
	reg_depth(F, C).

% For conjunctions
reg(FR, F, E, C+1) :-
	query_reg(F, E),
	reg(GR, G, E),
	reg(HR, H, E),
	GR = verum,
	1{F=conj(G, H); F=conj(H, G)},
	FR=HR,
	reg_depth(F, C).
	
reg(FR, F, E, C+1) :-
	query_reg(F, E),
	reg(GR, G, E),
	reg(HR, H, E),
	GR = falsum,
	HR != verum,
	1{F=conj(G, H); F=conj(H, G)},
	FR=falsum,
	reg_depth(F, C).

% No constants involved,
reg(FR, F, E, C+1) :-
	query_reg(F, E),
	reg(GR, G, E),
	reg(HR, H, E),
	GR != verum,
	GR != falsum,
	HR != verum,
	HR != falsum,
	F=disj(G, H),
	FR=disj(GR, HR),
	reg_depth(F, C).
	
reg(FR, F, E, C+1) :-
	query_reg(F, E),
	reg(GR, G, E),
	reg(HR, H, E),
	GR != verum,
	GR != falsum,
	HR != verum,
	HR != falsum,
	F=conj(G, H),
	FR=conj(GR, HR),
	reg_depth(F, C).
	
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