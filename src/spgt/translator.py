from typing import List, Tuple, Set, Dict
import itertools

import pddl
from pddl import logic as lg

from spgt.asp.symbols import *
from spgt.base.domain import GroundedAction, GroundedEffect
from spgt.base.logic import Formula, Verum, Falsum, Atom, Neg, Conj, Disj, Assign

# Read in a domain file and a problem file
# Ensure it's in the normalised form (oneof)
# Ensure it only has strips + a goal formula, or some other such thing.
# Don't worry about typing and fancy things just yet.
# Enumerate all the formulas.
# Convert them to ASP syntax.

# Need an abstract representation of the problem which keeps track of a
# map of formulas to their object identifiers. (including atoms etc)

class Variable:
	def __init__(self, name: str, domain: List[str]):
		self.name = name
		self.domain = domain
	
	def __eq__(self, other):
		return isinstance(other, Variable) \
			and other.name == self.name \
			and other.domain == self.domain
	
	def __hash__(self):
		return hash((self.name, *sorted(self.domain)))
	
	def as_ASP(self):
		ls = []
		for val in self.domain:
			ls.append(ASP_VARIABLE_VALUE_SYMBOL + f"({make_safe(self.name)}, {make_safe(val)}).")
		return ls
	
	def from_atom(atom: Atom):
		name = atom.symbol
		domain = [ASP_TRUE_VALUE, ASP_FALSE_VALUE]
		return Variable(name, domain)
	

class Translator:
	def __init__(self, domain_path: str, instance_path: str, predicate_map: Dict[str, str] = {}, process_immediate: bool = True):
		self.domain_path = domain_path
		self.instance_path = instance_path
		
		self.domain = pddl.parse_domain(domain_path)
		self.actions = list(self.domain.actions)
		self.all_effects = [a.effect for a in self.actions]
		
		self.types = self.domain.types
		
		self.predicates = list(self.domain.predicates)
		# to replace predicates which are only true for a single object with variables
		self.predicate_map = predicate_map
		
		self.instance = pddl.parse_problem(instance_path)
		self.objects = list(self.instance.objects)
		
		if self.instance.domain_name != self.domain.name:
			raise ValueError("Incorrect domain type")
		
		
		# Identify which predicates are not in effects, i.e. cannot be changed.
		self.unchanging_predicates = set(p for p in self.__calculate_unchanging_predicates())
		self.variables = set()
		
		self.grounded_actions = []
		self.grounded_effects = []
		self.converted_goal = None
		
		if process_immediate:
			self.ground()
		
		# TODO: Smarter way to instantiate actions based on intial state.
		# Things like `next_fwd` in action preconditions. If it's never changed or added, don't even include it as a variable.
		# self.converted_initial = set(f)
	
	def ground(self):
		'''
		Ground the domain.
		Happens by default when a translator is instantiated.
		'''
		# Normalise oneof operators
		# Handle them natively or use all outcomes determinisation?
		
		for p in self.predicates:
			if p.name in self.unchanging_predicates:
				continue
			for atom in self.__ground_predicate(p):
				self.__add_atom(atom)
			
		for a in self.actions:
			# also populates the grounded effects
			self.grounded_actions += self.__instantiate_action(a)
		
		# The goal shouldn't have any parameters in it, so we do not need
		# a variable mapping
		self.converted_goal = self.__convert_formula(self.instance.goal, {})
		
	def __init_atom_rules(self):
		'''
		Yields ASP rules describing the initial state.
		'''
		for p in self.instance.init:
			# if p.name in self.unchanging_predicates:
			# 	continue
			if isinstance(p, lg.Predicate):
				atom = self.__convert_formula(p, {})
				yield ASP_INIT_SYMBOL + f"({atom.symbol}, {ASP_TRUE_VALUE})."
			if isinstance(p, lg.base.Not):
				atom = self.__convert_formula(p._arg, {})
				yield ASP_INIT_SYMBOL + f"({atom.symbol}, {ASP_FALSE_VALUE})."
		for p in self.variables:
			# a scrappy fix assuming all variables are binary.
			if not p.name in [pred.name for pred in self.instance.init]:
				yield ASP_INIT_SYMBOL + f"({p.name}, {ASP_FALSE_VALUE})."
				
		
	def __get_initial_values(self, predicate) -> Set:
		'''
		Returns a set of tuples of objects for which this predicate is initially true.
		'''
		s = set()
		
		for pred in list(self.instance.init):
			if pred.name != predicate.name or pred.arity != pred.arity:
				continue
			
			s.add(pred.terms)
			
		return s
	
	def __calculate_unchanging_predicates(self) -> Set[str]:
		'''
		Identifies which predicates do not appear in any effects,
		and so can never change from the initial state
		'''
		predicates_in_effects = set([pred.name for effect in self.all_effects for pred in Translator.__get_predicates_in_formula(effect)])
		return set([p.name for p in self.predicates]) - predicates_in_effects
	
	def __get_child_types(self, type_name: str):
		'''
		Returns all type-children of the given type.
		Assumes there are no circular dependencies in the type system.
		'''
		for t in self.types:
			if type_name == self.types[t]:
				yield t
				for sub_child in self.__get_child_types(t):
					yield sub_child
		
	def __objects_of_type(self, type_name: str):
		'''
		Yields all objects of a certain type.
		'''
		assert type_name in self.types
		types = set(self.__get_child_types(type_name))
		types.add(type_name)
		for obj in self.objects:
			# if one of our childtypes labels this object, then yield it.
			if (set(obj.type_tags) & types):
				yield obj
		
	
	def __add_atom(self, atom: Atom):
		self.variables.add(Variable.from_atom(atom))
		return atom
	
	def __ground_predicate(self, predicate):
		# instantiate every choice of a predicate as an atom.
		choices = []
		for term in predicate.terms:
			term_choices = []
			for t_type in list(term.type_tags):
				term_choices += [(term.name, obj.name) for obj in self.__objects_of_type(t_type)]
			choices.append(term_choices)
		
		
		for choice in itertools.product(*choices):
			mapping = dict(choice)
			
			yield self.__convert_formula(predicate, mapping)

	def __convert_formula(self, F: lg.base.Formula, 
					   mappings: Dict[str, str],
					   valid: List[lg.Predicate] = [], 
					   unsatisfiable: List[lg.Predicate] = [], 
					   *args,
					   **kwargs):
		'''
		Parses a PDDL Formula object into an equivalent formula in the Translator's type.
		Uses mappings to assign variables to instantiated values as strings.
		Will use the internal predicate_mappings value to assign predicates to variables as desired.
		'''
		do_nothing = lambda F: F
		def binary_case(F: lg.base.BinaryOp, ftype: type):
			ops = F._operands.copy()
			if len(ops) < 2:
				return self.__convert_formula(ops.pop(), mappings, *args, **kwargs)
			
			new_F = ftype(self.__convert_formula(ops.pop(), mappings, *args, **kwargs), 
				 self.__convert_formula(ops.pop(), mappings, *args, **kwargs))
			
			while len(ops):
				next_form = self.__convert_formula(ops.pop(), mappings, *args, **kwargs)
				new_F = ftype(next_form, new_F)
			
			return new_F
			
		def imply_case(F: lg.base.Imply):
			a = self.__convert_formula(F.operands[0], mappings, *args, **kwargs)
			b = self.__convert_formula(F.operands[1], mappings, *args, **kwargs)
			return Disj(Neg(a), b)
		
		def predicate_case(F: lg.Predicate):
			# Allows us to remove predicates we've already calculated the values of,
			# i.e. for unchanging initial predicates.
			if F in valid:
				return Verum()
			if F in unsatisfiable:
				return Falsum()
			
			if F.arity == 0:
				return Atom(F.name)
			
			# If our mapping says this predicate should be converted to a variable,
			# then turn this statement into an assignment.
			if F.arity == 1 and F.name in self.predicate_map:
				return Assign(
					Atom(self.predicate_map[F.name]),
					Atom(self.__convert_formula(F.terms[0], mappings, *args, **kwargs))
					)
			
			# otherwise instantiate the specific instance
			mapped_terms = [str(self.__convert_formula(t, mappings)) for t in F.terms]
			new_name = F.name + "(" + ",".join(mapped_terms) + ")"
			atom = Atom(new_name)
			return atom
		
		def variable_case(V: lg.terms.Variable):
			
			
			return
		
		switch = {
			lg.terms.Constant: lambda C: C.name,
			lg.terms.Variable: lambda F: Atom(mappings[F.name]),
			lg.predicates.Predicate: predicate_case,
			lg.base.Atomic: lambda F: F.symbol,
			# lg.base.TrueFormula: lambda F: Verum(),
			# lg.base.FalseFormula: lambda F: Falsum(),
			lg.base.Not: lambda F: Neg(self.__convert_formula(F._arg, mappings, *args, **kwargs)),
			lg.base.And: lambda F: binary_case(F, Conj),
			lg.base.Or: lambda F: binary_case(F, Disj),
			lg.base.Imply: imply_case,
			# Return a list of all the possible formulae as outcomes.
			lg.base.OneOf: lambda F: [self.__convert_formula(sub, mappings, *args, **kwargs) for sub in F._operands],
		}
		
		if not isinstance(F, tuple(switch.keys())):
			raise ValueError(f"Type '{type(F)}' not supported.")
		
		return switch[type(F)](F)

	def __parameter_possibilities(self, action):
		'''
		Yields all possible combinations of parameters to the action.
		Does not generate those which are unable to satisfy the precondition based on unchanging predicate in the precondition.
		Still specifies the values of the the unchanging predicates which allow the action to be executed.
		'''
		# positive and negative literals in the precondition which are unchanging.
		# We assume preconditions do not contain disjunctions.
		requirements = [p for p in Translator.__get_positive_predicates(action.precondition) if p.name in self.unchanging_predicates]
		prohibitions = [p for p in Translator.__get_negative_predicates(action.precondition) if p.name in self.unchanging_predicates]
		
		requirement_satisfiers = []
		for predicate in requirements:
			# the rezipping is so we have ( (x,o1),(y,o2) ) where x and y are the parameters
			# and predicate(o1, o2) is initially true.
			pred_choices = [tuple(zip(predicate.terms, tup)) for tup in self.__get_initial_values(predicate)]
			requirement_satisfiers.append(pred_choices)
			
		prohibited_choices = []
		for predicate in prohibitions:
			# the rezipping is so we have ( (x,o1),(y,o2) ) where x and y are the parameters
			# and predicate(o1, o2) is initially true.
			pred_choices = [set(zip(predicate.terms, tup)) for tup in self.__get_initial_values(predicate)]
			prohibited_choices += pred_choices
		
		# other parameters which may take any value (of the specified type)
		# we allow for those which occur in prohibitions because we will simply skip all prohibited values.
		free_parameters = [param 
					 for predicate in requirements 
					 for param in action.parameters if not param in predicate.terms ]
	
		free_choices = []
		for param in free_parameters:
			p_choices = []
			for p_type in list(param.type_tags):
				p_choices += [(param, obj) for obj in self.__objects_of_type(p_type)]
			free_choices.append(p_choices)
		
		for choice_of_frees in itertools.product(*free_choices):
			# if there are no free parameters, itertools will run this loop once
			# with choice_of_frees = (), the empty tuple
			
			# loop through all possible choices of pre_quantified parameters
			for choice_for_requirements in itertools.product(*requirement_satisfiers):
				# merge choice_of_frees and choice_for_requirements into one tuple, asserting there are no prohibitions
				s_free = set(choice_of_frees)
				# merge the tuple of tuples of assigmments into a single tuple of assigmments into one set of assignments
				s_req = set(assignment for tup in choice_for_requirements for assignment in tup)
				# assert the choice of parameters to satisfy requirements don't contradict.
				var_names = [a[0].name for a in s_req]
				if len(var_names) != len(set(var_names)):
					continue
				
				# if either of the sets makes a choice which contains a prohibition,
				# skip it
				if sum([(prohib <= s_req) or (prohib <= s_free) for prohib in prohibited_choices]):
					continue
				
				mapping = {}
				mapping |= {p.name: str(obj) for p,obj in s_free}
				# add required choice, overriding values taking in free_choice.
				mapping |= {p.name: str(obj) for p,obj in s_req}
				yield mapping
		
		return
		
	def __create_action(self, action, mapping: Dict[str, str]):
		"""
		Instantiates an action with the given variable
		"""
		var_choice_string = "_" + "_".join(str(o) for var,o in mapping.items())
		new_name = action.name + var_choice_string
		new_effect_name = action.name + var_choice_string
		
		valid = [p for p in Translator.__get_positive_predicates(action.precondition) if p.name in self.unchanging_predicates]
		unsatisfiable = [p for p in Translator.__get_negative_predicates(action.precondition) if p.name in self.unchanging_predicates]
		
		new_prec = self.__convert_formula(action.precondition, mapping, valid=valid, unsatisfiable=unsatisfiable)
		new_prec = Formula.simplify_constants(new_prec)
		# this shouldn't be possible since we never give this functions mappings
		# which are unsatisfiable
		assert not isinstance(new_prec, Falsum)
		
		effect_formulas = self.__convert_formula(action.effect, mapping)
		if not isinstance(effect_formulas, list):
			effect_formulas = [effect_formulas]
			
		new_effects = [GroundedEffect.from_formula(new_effect_name + f"_effect_{i}", eff_form) for i,eff_form in enumerate(effect_formulas)]
		
		self.grounded_effects += new_effects
		
		return GroundedAction(new_name, new_prec, new_effects)
	
	def __instantiate_action(self, action):
		new_actions = []
		params = set(p.name for p in action.parameters)
		
		for mapping in self.__parameter_possibilities(action):
			if not params <= set(mapping.keys()):
				continue
			new_actions.append(self.__create_action(action, mapping))
		
		return new_actions
	
	def save_ASP(self, path):
		with open(path, "w+") as f:
			f.writelines(self.as_ASP())
	
	def as_ASP(self):
		'''
		Yields the ASP rules describing the domain.
		'''
		for v in self.variables:
			for r in v.as_ASP():
				yield r + "\n"
		
		yield "\n"
		
		for r in self.__init_atom_rules():
			yield r + "\n"
		
		yield "\n"
		
		yield ASP_GOAL_SYMBOL + f"({self.converted_goal.as_ASP()}).\n"
		
		yield "\n"
		
		for a in self.grounded_actions:
			for r in a.as_ASP():
				yield r + "\n"
		
		yield "\n"
		for e in self.grounded_effects:
			for r in e.as_ASP():
				yield r + "\n"
		
	
	@staticmethod
	def __get_predicates_in_formula(formula: lg.base.Formula) -> Set:
		return Translator.__get_positive_predicates(formula) | Translator.__get_negative_predicates(formula)
	
	@staticmethod
	def __get_positive_predicates(formula: lg.base.Formula) -> Set:
		'''
		Returns all positive predicates in a formula (Pred(...)).
		'''
		if isinstance(formula, lg.base.BinaryOp):
			recurses = [Translator.__get_positive_predicates(sub) for sub in formula._operands]
			if not recurses:
				return set()
			return set.union(*recurses)
		if isinstance(formula, lg.predicates.Predicate):
			return {formula}
		return set()
	
	@staticmethod
	def __get_negative_predicates(formula: lg.base.Formula) -> Set:
		'''
		Returns all negative predicates in a formula (Not(Pred(...))).
		'''
		if isinstance(formula, lg.base.BinaryOp):
			recurses = [Translator.__get_negative_predicates(sub) for sub in formula._operands]
			if not recurses:
				return set()
			return set.union(*recurses)
		if isinstance(formula, lg.base.Not):
			return {formula._arg}
		return set()
	
		
if __name__ == '__main__':
	t = Translator(
		"/home/simon/Documents/Uni/Honours/Code/robot_4/domain-fond_all_outcomes.pddl",
		"/home/simon/Documents/Uni/Honours/Code/Plan4Past-data/non-deterministic/PPLTL/BF23/robot_4/new_coffee10.pddl")
	
	for rule in t.as_ASP():
		print(rule)
		pass