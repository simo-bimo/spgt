from __future__ import annotations
from abc import ABC, abstractmethod

from typing import List, Dict, Tuple

from spgt.asp.symbols import *

import clingo

def split_top_brackets(s: str, delim: str = ',', brackets: Tuple[str, str] = ('(', ')')) -> List[str]:
	left_brackets, right_brackets = brackets
	items = []
	depth = 0
	last_index = 0
	for i,c in enumerate(s):
		if c in left_brackets:
			depth += 1
		elif c in right_brackets:
			depth -= 1
		elif c in delim and depth == 0:
			items.append(s[last_index:i])
			last_index = i+1
	items.append(s[last_index:])
	return items

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
	
	def is_ppltl(self):
		return False
	
	@staticmethod
	def _get_subclass_asp_mappings():
		immediate_subclasses = Formula.__subclasses__()
		leaf_subclasses = []
		for sc in immediate_subclasses:
			if len(sc.__subclasses__()) > 0:
				immediate_subclasses.extend(sc.__subclasses__())
			else:
				if not sc in leaf_subclasses:
					leaf_subclasses.append(sc)
		
		mappings = [
			(sc.ASP_SYMBOL, sc) for sc in leaf_subclasses
		]
		
		return mappings
		
	
	@staticmethod
	def from_asp(asp_string: clingo.Symbol|str, var_mapping: Dict[int, SASVariable] = {}) -> Formula | str:
		mappings = Formula._get_subclass_asp_mappings()
		
		if isinstance(asp_string, clingo.Symbol):
			asp_string = str(asp_string)
		asp = asp_string.strip('\\"')
		
		if asp.startswith(Assign.ASP_SYMBOL):
			# special case for assign to handle variables and values correctly.
			sub_asp = asp.removeprefix(Assign.ASP_SYMBOL).removeprefix('(').removesuffix(')')
			var, val = tuple(int(x.strip().strip('"')) for x in sub_asp.split(',')[:2])
			return Assign(var_mapping[var], SASValue(val))
		
		for s,f in mappings:
			if f == Assign:
				continue	
			if asp.startswith(s):
				sub_asp = asp.removeprefix(s).removeprefix('(').removesuffix(')')
				subs = [x.strip().strip('\\"') for x in split_top_brackets(sub_asp)]
				return f(*[Formula.from_asp(x, var_mapping=var_mapping) for x in subs])
		
		raise ValueError('Could not determine Symbol Type')
	
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
	def parse(s: str, var_mapping: Dict[int, SASVariable] = {}) -> Formula:
		"""
		Returns the Formula object equivalent of the str.
		Any symbols not identified as formulae are used to name atoms.
		This includes unmatched brackets.
		Provides SAS variables and values if var_mapping is provided.
		"""
		mappings = Formula.binary_mappings | Formula.unary_mappings
		
		using_sas = len(var_mapping)>0
		
		s = s.strip()
		if s[0] == "(":
			brack_index = Formula.__matching_bracket(s)
			if brack_index == len(s)-1:
				return Formula.parse(s[1:-1])
		
		binary_index = Formula.__check_binary(s)
		if binary_index is not None:
			# There was a binary symbol
			symbol = s[binary_index]
			if using_sas and symbol == '=':
				# if it is an assign
				left = var_mapping[int(s[0:binary_index])]
				right = var_mapping[int(s[binary_index+1:])]
				return Assign(left, right)
			left = Formula.parse(s[0:binary_index])
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
	
	def is_ppltl(self):
		return self._arg.is_ppltl()

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
	
	def is_ppltl(self):
		return sum(x.is_ppltl() for x in self._sub) >= 1

class Since(BinaryOp):
	symbol = "S"
	ASP_SYMBOL = "since"
	
	def is_ppltl(self):
		return True

class DualSince(BinaryOp):
	symbol = "DS"
	ASP_SYMBOL = 'dual_since'
	
	def is_ppltl(self):
		return True

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
		child_symbols = [str(x) for x in self._sub]
		children_str = ','.join(child_symbols)
		return f"{self.ASP_SYMBOL}({children_str})"

class Yesterday(UnaryOp):
	symbol = "Y"
	ASP_SYMBOL = "yest"
	
	def is_ppltl(self):
		return True

class Neg(UnaryOp):
	symbol = "\u00AC"
	ASP_SYMBOL = "neg"

class Atom(Formula):
	# in this case, symbol 
	# is the name of the atom.
	symbol: str
	ASP_SYMBOL = 'atom'
	
	def __init__(self, name:str = "NO SYMBOL"):
		self.symbol = name
	
	def as_ASP(self):
		return make_safe(self.symbol)

class SASVariable(Formula):
	ASP_SYMBOL = ASP_VARIABLE_VALUE_SYMBOL
	
	def __init__(self, id: int, domain_size: int, axiom_layer: int = -1):
		self.id = id
		self.domain_size = domain_size
		self.axiom_layer = axiom_layer
		self.domain = list(range(domain_size))
		self.symbol = str(id)
	
	def __eq__(self, other):
		return isinstance(other, SASVariable) \
			and other.id == self.id \
			and other.domain_size == self.domain_size
	
	def __hash__(self):
		return hash(self.id)
	
	def __str__(self):
		return str(self.id)
	
	def as_ASP(self):
		ls = []
		for val in range(self.domain_size):
			ls.append(self.ASP_SYMBOL + f"({self.id}, {val}).")
		return ls
	
	def is_binary(self) -> bool:
		return self.domain_size == 2

class SASValue(Formula):
	ASP_SYMBOL = "UNDEFINED"
	
	def __init__(self, val: int):
		self.val = val
		self.symbol = str(val)
	
	def __eq__(self, other):
		return isinstance(other, SASValue)\
				and other.val == self.val
	
	def __hash__(self):
		return hash(self.val)
	
	def as_ASP(self):
		return self.symbol
	

class Variable(Formula):
	ASP_SYMBOL = ASP_VARIABLE_VALUE_SYMBOL
	
	def __init__(self, name: str, domain: List[str], axiom_layer: int = -1):
		self.symbol = name
		self.domain = domain
		self.axiom_layer = axiom_layer
	
	def __eq__(self, other):
		return isinstance(other, Variable) \
			and other.symbol == self.symbol \
			and other.domain == self.domain
	
	def __hash__(self):
		return hash((self.symbol, *sorted(self.domain)))
	
	def as_ASP(self):
		ls = []
		for val in self.domain:
			ls.append(self.ASP_SYMBOL + f"({make_safe(self.symbol)}, {make_safe(val)}).")
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

class Axiom(Formula):
	'''
	An abstract representation of an axiom.
	'''
	symbol = "\u2190" # left arrow.
	ASP_SYMBOL = "axiom_rule"
	
	def __init__(self, head: Variable, condition: Formula):
		if not head.is_binary():
			raise ValueError("Cannot have an axiom set a non-binary value.")
		self._head = head
		self._condition = condition
	
	def __str__(self):
		return f"{str(self._head)}{self.symbol}{str(self._condition)}"
	
	def as_ASP(self):
		return f"{self.ASP_SYMBOL}({self._head.as_ASP()}, {self._condition.as_ASP()})"

if __name__ == '__main__':
	# print(split_top_brackets("baguette, abc(one, two, three), def(four, five, six(seven, eight))"))
	
	print(Formula.from_asp('conj(has_value("baguette", "fresh"), has_value("tomato", "fresh"))'))
	