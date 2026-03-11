from typing import Tuple, List, Dict

from spgt.base.logic import Formula, Variable, Neg, Assign, Conj, Disj, BinaryOp, Yesterday, Since, DualSince, Verum, Falsum
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
	'''
	The smallest number of applications of regression which can produce a given formula.
	'''
	formula_depths: Dict[Formula, int]
	
	def __init__(self, 
			  var_mapping: Dict[int, Variable], 
			  axiom_rules: List[AxiomType], 
			  effects: Dict[str, GroundedEffect],
			  regression_bound: int = -1
			  ):
		self.var_mapping = var_mapping
		self.axiom_rules = axiom_rules
		self.effects = effects
		self.cache = {}
		
		self.var_axiom_mapping = {}
		self.regression_bound = regression_bound
		self.formula_depths = {}
		
		for condition,head in self.axiom_rules:
			if not head in self.var_axiom_mapping:
				self.var_axiom_mapping[head] = [condition]
			else:
				self.var_axiom_mapping[head].append(condition)
				
	def set_regression_bound(self, k: int):
		self.regression_bound = k
	
	def get_formula_depth(self, formula: Formula) -> int:
		'''
		Gets the depth of a formula. If it does not appear,
		assumes it occurs in the domain and returns a default depth of 0
		'''
		return self.formula_depths.get(formula, 0)
	
	def update_formula_depth(self, formula: Formula, 
						  parent_formula: Formula = None) -> bool:
		'''
		Updates the formula to have a regression depth one more than it's parent,
		unless there is already a smaller existing value.
		Returns whether this exceeds the bound if it is set.
		'''
		depth = 0
		if not parent_formula is None:
			depth = self.get_formula_depth(parent_formula) + 1
		
		if not formula in self.formula_depths:
			self.formula_depths[formula] = depth
		
		self.formula_depths[formula] = min(self.formula_depths[formula], depth)
		return (self.regression_bound > 0)\
			 and (self.regression_bound < self.formula_depths[formula])
	
	def regress(self, formula: Formula, effect: GroundedEffect) -> Formula:
		'''
		Regresses a formula through an effect.
		'''	
		if (str(formula), effect.name) in self.cache:
			return self.cache[(str(formula), effect.name)]
		
		# if isinstance(formula, Since)\
		# 	and effect.name.startswith('walk-right'):
		# 	import pdb
		# 	pdb.set_trace()
		
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
		
		def one_step(f: Since|DualSince, e:GroundedEffect):
			unfolded = f.one_step()
			return self.regress(unfolded, e)
		
		def const(f: Verum|Falsum, e: GroundedEffect):
			return type(f)()
		
		switch = {
			Verum: const,
			Falsum: const,
			Assign: assignment,
			Neg: lambda fr,eff: Formula.__inverse_demorgan(self.regress(fr._arg, eff)),
			Conj: recurse,
			Disj: recurse,
			Yesterday: lambda fr, _: fr._arg,
			Since: one_step,
			DualSince: one_step
		}
		
		if type(formula) not in switch.keys():
			raise ValueError(f"Formula {formula} not supported")
		
		result = switch[type(formula)](formula, effect)
		# This prevents falsum being interpreted as true
		# yesterday from the initial state.
		result = Formula.simplify_constants(result)
		
		self.cache[(str(formula), effect.name)] = result
		# Update the depth value of the result
		if self.update_formula_depth(result, formula):
			# we have exceeded the maximum applications of regression permitted.
			# Return a falsum.
			return Falsum()
		
		return result
	
	def reg(self, formula: clingo.Symbol, effect: clingo.Symbol) -> str:
		'''
		An ASP focused interface for the regress function.
		'''
		# Convert ASP strings to python objects through lookup.
		f = Formula.from_asp(formula, self.var_mapping)
		effect_name = str(effect).strip('"')
		e = self.effects[effect_name]
		
		return clingo.symbol.parse_term(self.regress(f, e).as_ASP())