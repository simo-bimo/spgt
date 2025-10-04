from __future__ import annotations
from abc import ABC, abstractmethod

from typing import List, Dict

from spgt.asp.symbols import *

class Formula(ABC):
	symbol: str
	ASP_SYMBOL: str
	binary_mappings = {
		'=': 'Assign',
		'|': 'Disj',
		'&': 'Conj',
		'S': 'Since',
		'Z': 'DualSince'
	}
	unary_mappings = {
		'!': 'Neg',
		'Y': 'Yesterday'
	}
	
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
			Yesterday: lambda F: Yesterday(Neg(F._arg)),
			Since: lambda F: DualSince(*negations(F)),
			DualSince: lambda F: Since(*negations(F))
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
			Yesterday: lambda F: Yesterday(Formula.NNF(F._arg)),
			Since: lambda F: Since(*recurse(F)),
			DualSince: lambda F: DualSince(*recurse(F)),
		}
		
		if not isinstance(F, tuple(switch.keys())):
			raise ValueError(f"Type '{type(F)}' not supported.")
		
		return switch[type(F)](F)
	
	@staticmethod
	def simplify_constants(F: Formula):
		"""
		Returns a new formula with the constants dissolved away.
		"""
		do_nothing = lambda F: F
		recurse = lambda F: [Formula.simplify_constants(s) for s in F._sub]
		
		def negation_case(F: Neg):
			if isinstance(F._arg, Falsum):
				return Verum()
			if isinstance(F._arg, Verum):
				return Falsum()
			return F
		
		def dissolve_or_disprove(F : Conj | Disj, dissolve, disprove):
			if disprove in [type(x) for x in F._sub]:
				return disprove()
			if dissolve in [type(x) for x in F._sub]:
				new_subs = [x for x in F._sub if not type(x) is dissolve]
				if not new_subs:
					return dissolve()
				return new_subs.pop()
			return F
		
		switch = {
			Falsum: do_nothing,
			Verum: do_nothing,
			Atom: do_nothing,
			Neg: negation_case,
			Assign: do_nothing,
			Value: do_nothing,
			Variable: do_nothing,
			Conj: lambda F: dissolve_or_disprove(type(F)(*recurse(F)), Verum, Falsum),
			Disj: lambda F: dissolve_or_disprove(type(F)(*recurse(F)), Falsum, Verum),
			Yesterday: lambda F: type(F)(Formula.simplify_constants(F._arg)),
			Since: lambda F: type(F)(*recurse(F)),
			DualSince: lambda F: type(F)(*recurse(F)),
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
		if isinstance(self._arg, Atom):
			return ASP_HAS_VALUE_SYMBOL + f"({make_safe(self._arg.symbol)}, {ASP_FALSE_VALUE})"
		
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

class Since(BinaryOp):
	symbol = "S"
	ASP_SYMBOL = "since"

class DualSince(BinaryOp):
	symbol = "DS"
	ASP_SYMBOL = 'dual_since'

class Conj(BinaryOp):
	symbol = "\u2227"
	ASP_SYMBOL = "conj"

class Disj(BinaryOp):
	symbol = "\u2228"
	ASP_SYMBOL = "disj"

class Assign(BinaryOp):
	symbol = "="
	ASP_SYMBOL = "has_value"
	
	def as_ASP(self):
		child_symbols = [make_safe(x.symbol) for x in self._sub]
		children_str = ','.join(child_symbols)
		return f"{self.ASP_SYMBOL}({children_str})"

class Yesterday(UnaryOp):
	symbol = "Y"
	ASP_SYMBOL = "yest"

class Neg(UnaryOp):
	symbol = "\u00AC"
	ASP_SYMBOL = "neg"

class Atom(Formula):
	# in this case, symbol 
	# is the name of the atom.
	symbol: str
	
	def __init__(self, name:str = "NO SYMBOL"):
		self.symbol = name
	
	def as_ASP(self):
		return make_safe(self.symbol)

class Variable(Formula):
	def __init__(self, name: str, domain: List[str]):
		self.symbol = name
		self.domain = domain
	
	def __eq__(self, other):
		return isinstance(other, Variable) \
			and other.symbol == self.symbol \
			and other.domain == self.domain
	
	def __hash__(self):
		return hash((self.symbol, *sorted(self.domain)))
	
	def as_ASP(self):
		ls = []
		for val in self.domain:
			ls.append(ASP_VARIABLE_VALUE_SYMBOL + f"({make_safe(self.symbol)}, {make_safe(val)}).")
		return ls
	
	def from_atom(atom: Atom):
		symbol = atom.symbol
		domain = [ASP_TRUE_VALUE, ASP_FALSE_VALUE]
		return Variable(symbol, domain)
	
	def is_binary(self) -> bool:
		return set(self.domain) == {ASP_TRUE_VALUE, ASP_FALSE_VALUE}


class Value(Atom):
	pass

class Verum(Formula):
	symbol = '\u22A4'
	ASP_SYMBOL = "verum"

class Falsum(Formula):
	symbol = '\u22A5'
	ASP_SYMBOL = "falsum"