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
	
	def __hash__(self):
		return (self.name, *self.domain).__hash__()
	
	def as_ASP(self):
		ls = []
		for val in self.domain:
			ls.append(ASP_VARIABLE_VALUE_SYMBOL + f"({self.name}, {val}).")
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
			self.ground(predicate_map)
		
		# TODO: Smarter way to instantiate actions based on intial state.
		# Things like `next_fwd` in action preconditions. If it's never changed or added, don't even include it as a variable.
		# self.converted_initial = set(f)
	
	def ground(self, predicate_map):
		'''
		Ground the domain.
		Happens by default when a translator is instantiated.
		'''
		
		# Normalise oneof operators
		# Handle them natively or use all outcomes determinisation?
		
		# Identify Variables
		# TODO: For now, stick with predicate_map for simple cases.
		
		# Ground predicates, creating variables based on predicate_mapping when
		# required.
		for p in self.predicates:
			self.__add_variables_from_predicate(p)
			
		for a in self.actions:
			# also populates the grounded effects
			self.grounded_actions += self.__instantiate_action(a)
		
		# TODO Initial state.
		
		# The goal shouldn't have any parameters in it, so we do not need
		# a variable mapping
		self.converted_goal = self.__convert_formula(self.instance.goal, {})
		
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
	
	def __objects_of_type(self, type_name: str):
		assert type_name in self.types
		ls = []
		for obj in self.objects:
			if type_name in obj.type_tags:
				ls.append(obj)
		return ls
	
	def __add_atom(self, atom: Atom):
		self.variables.add(Variable.from_atom(atom))
		return atom
	
	def __add_variables_from_predicate(self, predicate):
		s = str(predicate)
		if s in self.predicate_map and predicate.arity == 1:
			name = self.predicate_map[s]
			
			# there should be exactly one term if it is in the predicate map
			predicate_domain = self.__objects_of_type(predicate.terms[0].type_tag)
			var_domain = [self.__convert_formula(o) for o in predicate_domain]
			return self.variables.add(Variable(name, var_domain))
		
		# else instantiate every possible choice of inputs to the predicate
		# as an atom
		term_choices = []
		for term in predicate.terms:
			choices = []
			for tag in list(term.type_tags):
				choices += self.__objects_of_type(tag)
			term_choices.append({c: term.name for c in choices})
		
		
		for choice in itertools.product(*term_choices):
			mapping = {k: v for v,k in choice}
			
			atom = self.__convert_formula(predicate, mapping)
			self.__add_atom(atom)

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
				return self.__add_atom(Atom(F.name))
			
			# If our mapping says this predicate should be converted to a variable,
			# then turn this statement into an assignment.
			if F.arity == 1 and F.name in self.predicate_map:
				return Assign(
					self.__add_atom(Atom(self.predicate_map[F.name])), 
					self.__add_atom(Atom(self.__convert_formula(F.terms[0], mappings, *args, **kwargs)))
					)
			
			# otherwise instantiate the specific instance
			mapped_terms = [str(self.__convert_formula(t, mappings, *args, **kwargs)) for t in F.terms]
			
			return self.__add_atom(Atom(F.name + "(" + ",".join(mapped_terms) + ")"))
		
		switch = {
			lg.terms.Constant: lambda F: self.__add_atom(Atom(F.name)),
			lg.terms.Variable: lambda F: self.__add_atom(Atom(mappings[F.name])),
			lg.predicates.Predicate: predicate_case,
			lg.base.Atomic: do_nothing,
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
		var_choice_string = "(" + ",".join(str(o) for var,o in mapping.items()) + ")"
		new_name = action.name + var_choice_string
		new_effect_name = action.name + "_effect" + var_choice_string
		
		valid = [p for p in Translator.__get_positive_predicates(action.precondition) if p.name in self.unchanging_predicates]
		unsatisfiable = [p for p in Translator.__get_negative_predicates(action.precondition) if p.name in self.unchanging_predicates]
		
		new_prec = self.__convert_formula(action.precondition, mapping, valid=valid, unsatisfiable=unsatisfiable)
		new_prec = Formula.simplify_constants(new_prec)
		# this shouldn't be possible since we never give this functions mappings
		# which are unsatisfiable
		assert not isinstance(new_prec, Falsum)
		
		effect_formula = self.__convert_formula(action.effect, mapping)
		new_effect = GroundedEffect.from_formula(new_effect_name, effect_formula)
		
		self.grounded_effects.append(new_effect)
		
		return GroundedAction(new_name, new_prec, [new_effect])
	
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
				yield r
		
		for a in self.grounded_actions:
			for r in a.as_ASP():
				yield r
		
		for e in self.grounded_effects:
			for r in e.as_ASP():
				yield r
		
		yield ASP_GOAL_SYMBOL + f"({self.converted_goal.as_ASP()})."
	
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