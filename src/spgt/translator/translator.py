import pddl
from functools import cache

from enum import Enum

from typing import List, Tuple, Set

from Planner.Translations.logic import Formula, Atom, Neg, Conj, Disj

# Read in a domain file and a problem file
# Ensure it's in the normalised form (oneof)
# Ensure it only has strips + a goal formula, or some other such thing.
# Don't worry about typing and fancy things just yet.
# Enumerate all the formulas.
# Convert them to ASP syntax.

# Need an abstract representation of the problem which keeps track of a
# map of formulas to their object identifiers. (including atoms etc)

class Translator:
	path: str
	domain: pddl.core.Domain
	do_regression: bool
	
	ASP_rules: List[str]
	types: Set[str]
	
	def __init__(self, domain_path: str, instance_path: str):
		self.domain_path = domain_path
		self.instance_path = instance_path
		
		self.domain = pddl.parse_domain(domain_path)
		self.types = self.domain.types
		
		self.predicates = list(self.domain.predicates)
		
		
		self.instance = pddl.parse_domain(instance_path)
		
		if self.instance.domain_name != self.domain.name:
			raise ValueError("Incorrect domain type")
		pass
		
	def save_ASP(self, path):
		with open(path, "w+") as f:
			f.writelines(self.to_ASP())
	
	def to_ASP(self) -> list:
		"Returns a list of ASP rules."
		pass
		
		
		
		