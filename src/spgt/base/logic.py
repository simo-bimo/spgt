from __future__ import annotations
from abc import ABC, abstractmethod

from typing import List, Dict

from pddl import logic as lg

class Formula(ABC):
	symbol: str
	ASP_SYMBOL: str
	binary_mappings = {
		'=': 'Assign',
		'|': 'Disj',
		'&': 'Conj',
	}
	unary_mappings = {
		'!': 'Neg'
	}
	ASP_TRUE_VALUE = 'trueValue'
	ASP_FALSE_VALUE = 'falseValue'
	
	@abstractmethod
	def as_ASP(self):
		return self.ASP_SYMBOL
	
	def __repr__(self):
		return type(self).__name__
	
	def __str__(self):
		return self.symbol
	
	@staticmethod
	def __check_binary(s: str, binary_symbols = None) -> int | None:
		if binary_symbols is None:
			binary_symbols = Formula.binary_mappings.keys()
		
		i = 0
		level = 0
		while i < len(s):
			if level == 0 and s[i] in binary_symbols:
				return i
			if s[i] == "(":
				level += 1
			if s[i] == ")":
				level -= 1
			i += 1
		
		return None
	
	@staticmethod
	def __matching_bracket(s: str, index: int=0) -> int | None:
		i = index + 1
		level = 0
		assert s[index] == '('
		while (i < len(s)):
			if level == 0 and s[i] == ")":
				return i
			if s[i] == "(":
				level += 1
			if s[i] == ")":
				level -= 1
			i += 1
		return None
	
	@staticmethod
	def parse(s: str) -> Formula:
		"""
		Returns the Formula object equivalent of the str.
		Any symbols not identified as formulae are used to name atoms.
		This includes unmatched brackets.
		"""
		mappings = Formula.binary_mappings | Formula.unary_mappings
		
		s = s.strip()
		if s[0] == "(":
			brack_index = Formula.__matching_bracket(s)
			if brack_index == len(s)-1:
				return Formula.parse(s[1:-1])
		
		binary_index = Formula.__check_binary(s)
		if binary_index is not None:
			# There was a binary symbol
			left = Formula.parse(s[0:binary_index])
			symbol = s[binary_index]
			right = Formula.parse(s[binary_index+1:])
			return globals()[mappings[symbol]](left, right)
		
		# If we begin with a valid symbol, parse as unary.
		if s[0] in mappings:
			return globals()[mappings[s[0]]](Formula.parse(s[1:]))
		
		return Atom(s)
	
	@staticmethod
	def parse_pddl(F: lg.base.Formula, lookup: Dict[str, str] = None):
		'''
		Parses a PDDL Formula object into an equivalent formula in the Translator's type.
		'''
		do_nothing = lambda F: F
		
		def binary_case(F: lg.base.BinaryOp, ftype: type):
			ops = F._operands
			if len(ops) < 2:
				return Formula.parse_pddl(ops.pop())
			
			new_F = ftype(Formula.parse_pddl(ops.pop()), 
				 Formula.parse_pddl(ops.pop()))
			
			while len(ops):
				next_form = Formula.parse_pddl(ops.pop())
				new_F = ftype(next_form, new_F)
			
			return new_F
			
		def imply_case(F: lg.base.Imply):
			a = Formula.parse_pddl(F.operands[0])
			b = Formula.parse(F.operands[1])
			return Disj(Neg(a), b),
		
		def predicate_case(F: lg.Predicate):
			if F.arity == 0:
				return Atom(F.name)
			
			return Atom(F.__repr__())
			
		
		switch = {
			lg.terms.Constant: lambda F: Atom(F.name),
			# lg.terms.Variable: ,
			lg.predicates.Predicate: predicate_case,
			lg.base.Atomic: do_nothing,
			lg.base.TrueFormula: lambda F: Verum(),
			lg.base.FalseFormula: lambda F: Falsum(),
			lg.base.Not: lambda F: Neg(Formula.parse_pddl(F._arg)),
			lg.base.And: lambda F: binary_case(F, Conj),
			lg.base.Or: lambda F: binary_case(F, Disj),
			lg.base.Imply: imply_case,
			# Return a list of all the possible formulae as outcomes.
			lg.base.OneOf: lambda F: [Formula.parse_pddl(sub) for sub in F._operands],
		}
		
		if not isinstance(F, tuple(switch.keys())):
			raise ValueError(f"Type '{type(F)}' not supported.")
		
		return switch[type(F)](F)
	
	@staticmethod
	def __inverse_demorgan(F: Formula):
		"""
		Returns the negation of F, attempting to avoid having
		a Neg() formula as the parent.
		This means de Morgan laws are applied for conjunctions
		and disjunctions, Falsum and Verum return eachother
		and top-level negations are removed.
		Atoms return Neg(A).
		"""
		negations = lambda F: [Neg(s) for s in F._sub]
		
		switch = {
			Falsum: lambda F: Verum(),
			Verum: lambda F: Falsum(),
			Atom: lambda F: Neg(F),
			Neg: lambda F: F._arg,
			Assign: lambda F: Neg(F),
			Conj: lambda F: Disj(*negations(F)),
			Disj: lambda F: Conj(*negations(F)),
		}
		
		if not isinstance(F, tuple(switch.keys())):
			raise ValueError(f"Type '{type(F)}' not supported.")
		
		return switch[type(F)](F)
	
	@staticmethod
	def NNF(F: Formula):
		"""
		Returns a new formula equivalent to F in Negation Normal Form.
		"""
		do_nothing = lambda F: F
		recurse = lambda F: [Formula.NNF(s) for s in F._sub]
		
		def negation_case(F: Neg):
			if  isinstance(F._arg, (Atom, Assign)):
				return F
			return Formula.NNF(Formula.__inverse_demorgan(F._arg))
		
		switch = {
			Falsum: do_nothing,
			Verum: do_nothing,
			Atom: do_nothing,
			Assign: do_nothing,
			Neg: negation_case,
			Conj: lambda F: Conj(*recurse(F)),
			Disj: lambda F: Disj(*recurse(F)),
		}
		
		if not isinstance(F, tuple(switch.keys())):
			raise ValueError(f"Type '{type(F)}' not supported.")
		
		return switch[type(F)](F)
	
class UnaryOp(Formula):
	_arg: Formula
	
	def __init__(self, child: Formula):
		self._arg = child
	
	def __repr__(self):
		return super().__repr__() + f"({self._arg.__repr__()})"
	
	def __str__(self):
		return f"{self.symbol}{self._arg}"
	
	def as_ASP(self):
		return f"{self.ASP_SYMBOL}({self._arg.as_ASP()})"

class BinaryOp(Formula):
	_sub: List[Formula]
	
	def __init__(self, *args):
		self._sub = list(args)
	
	def __repr__(self):
		children_rep = ", ".join([x.__repr__() for x in self._sub])
		return super().__repr__() + f"({children_rep})"
	
	def __str__(self):
		children_strs = self.symbol.join([str(x) for x in self._sub])
		return f"({children_strs})"
	
	def as_ASP(self):
		child_symbols = [x.as_ASP() for x in self._sub]
		children_str = ','.join(child_symbols)
		return f"{self.ASP_SYMBOL}({children_str})"

class Conj(BinaryOp):
	symbol = "\u2227"
	ASP_SYMBOL = "conj"

class Disj(BinaryOp):
	symbol = "\u2228"
	ASP_SYMBOL = "disj"

class Assign(BinaryOp):
	symbol = "="
	ASP_SYMBOL = "assign"

class Neg(UnaryOp):
	symbol = "\u00AC"
	ASP_SYMBOL = "neg"

class Atom(Formula):
	'''
	Takes the place of variables for assigns.
	'''
	# in this case, symbol 
	# is the name of the atom.
	symbol: str
	
	def __init__(self, name:str = "NO SYMBOL"):
		self.symbol = name
	
	def as_ASP(self):
		return self.symbol

class Verum(Formula):
	symbol = '\u22A4'
	ASP_SYMBOL = 'verum'

class Falsum(Formula):
	symbol = '\u22A5'
	ASP_SYMBOL = 'falsum'