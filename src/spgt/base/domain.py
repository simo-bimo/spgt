from typing import List, Tuple

from spgt.base.logic import Formula, Conj, Assign, Neg, Atom, Variable, Value
from spgt.asp.symbols import *

class GroundedEffect:
	def __init__(self, name, add: List[Tuple[Variable, Value]], delete: List[Tuple[Variable, Value]]):
		self.name = name
		self.add = add
		self.delete = delete
	
	def as_ASP(self):
		"""
		Returns a list of ASP rules for the add and delete rules of the effect.
		"""
		ls = []
		for var,val in self.add:
			s = ASP_EFFECT_ADD_SYMBOL + f"({make_safe(self.name)}, {make_safe(var.symbol)}, {val.as_ASP()})."
			ls.append(s)
			# ensure that for binary variables the other value is added (we flip it from true to false or vice versa.)
			if var.is_binary():
				opposite = Value(ASP_FALSE_VALUE) if val.symbol == ASP_TRUE_VALUE else Value(ASP_TRUE_VALUE)
				alternate_s = ASP_EFFECT_DELETE_SYMBOL + f"({make_safe(self.name)}, {make_safe(var.symbol)}, {opposite.as_ASP()})."
				ls.append(alternate_s)
		for var,val in self.delete:
			s = ASP_EFFECT_DELETE_SYMBOL + f"({make_safe(self.name)}, {make_safe(var.symbol)}, {val.as_ASP()})."
			ls.append(s)
			if var.is_binary():
				opposite = Value(ASP_FALSE_VALUE) if val.symbol == ASP_TRUE_VALUE else Value(ASP_TRUE_VALUE)
				alternate_s = ASP_EFFECT_ADD_SYMBOL + f"({make_safe(self.name)}, {make_safe(var.symbol)}, {opposite.as_ASP()})."
				ls.append(alternate_s)
		return ls
		
	@staticmethod
	def from_formula(name, f: Formula):
		'''
		Produces an effect object from a conjunction of literals.
		Disjunctions and other Binary Ops will be ignored.
		'''
		# recurse down finding all literals of the given type. Nothing
		def get_lits(form: Formula, l_type = (Assign,Atom)) -> List:
			if isinstance(form, Conj):
				recursions = [get_lits(x, l_type) for x in form._sub]
				return [x for xs in recursions for x in xs]
		
			if isinstance(form, l_type):
				return [form]
			
			return []
		
		positives = get_lits(f)
		negatives = [x._arg for x in get_lits(f, Neg)]
		
		# Assigns
		adds = [(f._sub[0], f._sub[1]) for f in positives if isinstance(f, Assign)]
		deletes = [(f._sub[0], f._sub[1]) for f in negatives if isinstance(f, Assign)]
		
		return GroundedEffect(name, adds, deletes)
	
	def __repr__(self):
		add_strings = sorted([f'{k}={v}' for k,v in self.add])
		del_strings = sorted([f'{k}={v}' for k,v in self.delete])
		add_str = "adds(" + ",".join(add_strings) + ")"
		del_str = "deletes(" + ",".join(del_strings) + ")"
		s = "Effect(" + self.name
		s += ", " + add_str
		s += ", " + del_str
		return s + ")"
	
	def __str__(self):
		return self.__repr__()
	
	def __hash__(self):
		return self.__repr__().__hash__()
	
class GroundedAction:
	def __init__(self, name, precondition: Formula, effects: list[GroundedEffect]):
		self.name = name
		self.precondition = precondition
		self.effects = effects

	def as_ASP(self):
		'''
		Returns a list of ASP rules describe the effect.
		'''
		ls = []
		ls.append(ASP_ACTION_SYMBOL + f'({make_safe(self.name)}).')
		ls.append(ASP_ACTION_PRECONDITION_SYMBOL + f'({make_safe(self.name)}, {self.precondition.as_ASP()}).')
		
		for e in self.effects:
			ls.append(ASP_ACTION_EFFECT_SYMBOL + f'({make_safe(self.name)}, {make_safe(e.name)}).')
		
		return ls

	def __repr__(self):
		effect_reps = [e.__repr__() for e in self.effects]
		return f"Action({self.name}, {self.precondition}, Effects=(" + ",".join(effect_reps) + "))."

	def __hash__(self):
		return self.__repr__().__hash__()