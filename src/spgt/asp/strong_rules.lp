path(X, Y) :- next(X, _, Y).
path(X, Z) :- path(X, Y), path(Y, Z).
:- path(X, X).