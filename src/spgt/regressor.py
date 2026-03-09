from typing import Tuple, List, Dict

from spgt.base.logic import Formula, Variable, Neg, Assign, Conj, Disj, BinaryOp, Yesterday, Since, DualSince
from spgt.base.domain import GroundedEffect

import clingo

# A list of conditions, and then an assignment in the head.
AxiomType = Tuple[List[Tuple[int, int]], Tuple[int, int]]

class Regressor:
	'''
	A class used to regress formulae for a particular FOND problem.
	Stores axioms internally and caches results as necessary.
	'''
	
	cache: Dict[Tuple[Formula, GroundedEffect], Formula]
	
	def __init__(self, 
			  var_mapping: Dict[int, Variable], 
			  axiom_rules: List[AxiomType], 
			  effects: Dict[str, GroundedEffect],
			  ):
		self.var_mapping = var_mapping
		self.axiom_rules = axiom_rules
		self.effects = effects
		self.cache = {}
		
		self.var_axiom_mapping = {}
		
		for condition,head in self.axiom_rules:
			if not head in self.var_axiom_mapping:
				self.var_axiom_mapping[head] = [condition]
			else:
				self.var_axiom_mapping[head].append(condition)
	
	def regress(self, formula: Formula, effect: GroundedEffect) -> Formula:
		'''
		Regresses formula through effect.
		'''	
		if (formula, effect) in self.cache:
			return self.cache[(formula, effect)]
		
		def assignment(f: Assign, e: GroundedEffect):
			var, val = tuple(f._sub)
			
			if (var,val) in self.var_axiom_mapping:
				# TODO: recurse on conditions, disjuncting outer set 
				# and conjuncting inner sets.
				return f
			return e.regress(f)
		
		def recurse(f: BinaryOp, e:GroundedEffect):
			recurses = [self.regress(sf, e) for sf in f._sub]
			return type(f)(*recurses)
		
		switch = {
			Assign: assignment,
			Neg: lambda fr,eff: Formula.__inverse_demorgan(self.regress(fr._arg, eff)),
			Conj: recurse,
			Disj: recurse,
			# TODO: Temporal Ops.
			Yesterday: lambda fr, _: fr._arg,
		}
		
		if type(formula) not in switch.keys():
			raise ValueError(f"Formula {formula} not supported")
		
		result = switch[type(formula)](formula, effect)
		self.cache[(formula, effect)] = result
		return result
	
	def reg(self, formula: clingo.Symbol, effect: clingo.Symbol) -> str:
		'''
		An ASP focused interface for the regress function.
		'''
		# Convert ASP strings to python objects through lookup.
		f = Formula.from_asp(formula, self.var_mapping)
		e = self.effects[effect.name]
		
		return clingo.Function(self.regress(f, e).as_ASP())