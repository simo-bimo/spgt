digraph(default).

edge((N1, N2)) :- next(N1, _, N2).
attr(edge, (N1, N2), dir, forward) :- next(N1, E, N2).
attr(edge, (N1, N2), label, E) :- next(N1, E, N2).

attr(node, N, label, "<Node {{node}}: {{action}}>") :- node(N), N!=numNodes.
attr(node, N, label, "<Node {{node}}: Final.>") :- node(N), N=numNodes.
attr(node, N, (label,node), N) :- node(N).
attr(node, N, (label,action), A) :- policy(N, A).
