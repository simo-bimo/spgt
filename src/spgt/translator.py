from typing import List, Tuple, Set, Dict, AnyStr
import itertools

import pddl
from pddl import logic as lg

from fondutils.normalizer import normalize

from spgt.asp.symbols import *
from spgt.base.domain import GroundedAction, GroundedEffect
from spgt.base.logic import Formula, Verum, Falsum, Atom, Neg, Conj, Disj, Assign, Variable, Value

# Read in a domain file and a problem file
# Ensure it's in the normalised form (oneof)
# Ensure it only has strips + a goal formula, or some other such thing.
# Don't worry about typing and fancy things just yet.
# Enumerate all the formulas.
# Convert them to ASP syntax.

# Need an abstract representation of the problem which keeps track of a
# map of formulas to their object identifiers. (including atoms etc)

class Translator:
	def __init__(self, domain_path: str, instance_path: str, predicate_map: Dict[str, str] = {}, process_immediate: bool = True):
		self.domain_path = domain_path
		self.instance_path = instance_path
		
		self.domain = normalize(pddl.parse_domain(domain_path))
		self.actions = set(self.domain.actions)
		
		self.all_effects = [a.effect for a in self.actions if not isinstance(a.effect, lg.base.OneOf)]
		# We treat different non-deterministic outcomes as different effects.
		for a in self.actions:
			if not isinstance(a.effect, lg.base.OneOf):
				continue
			self.all_effects += a.effect._operands
		
		self.types = self.domain.types
		
		self.predicates = set(self.domain.predicates)
		# to replace predicates which are only true for a single object with variables
		self.predicate_map = predicate_map
		
		self.instance = pddl.parse_problem(instance_path)
		self.objects = list(self.instance.objects)
		
		if self.instance.domain_name != self.domain.name:
			raise ValueError("Incorrect domain type")
		
		
		# Identify which predicates are not in effects, i.e. cannot be changed.
		self.unchanging_predicates = set(p for p in self.__calculate_unchanging_predicates())
		self.variables = set()
		self.initial_values = set()
		
		self.unary_predicate_variable_lookup = {}
		
		self.grounded_actions = set()
		self.grounded_effects = set()
		self.converted_goal = None
		
		if process_immediate:
			
			# TODO: ground other predicates as variables preemptively and set their initial state.
			self.ground()
		
		# TODO: Smarter way to instantiate actions based on intial state.
		# Things like `next_fwd` in action preconditions. If it's never changed or added, don't even include it as a variable.
		# self.converted_initial = set(f)
	
	def is_ppltl(self):
		for f in [self.converted_goal] + [a.precondition for a in self.grounded_actions]:
			if f.is_ppltl():
				return True
		return False
	
	def __identify_unary_variables(self):
		'''
		Identifies which predicates may be mapped one-to-one to variables.
		Yields key value pairs of predicate names to variables.
		Adds the variables to internal variable set automatically.
		'''
		
		for pred in self.predicates:
			if pred.arity != 1:
				continue
			
			# ensure it does change
			if pred.name in self.unchanging_predicates:
				continue
			
			# ensure there is only one initial value:
			init_values = self.__get_initial_values(pred)
			if len(init_values) != 1:
				continue
			
			# ensure whenever it changes, one value is added,
			# and one is removed.
			# i.e. it never holds for more than two objects at once.
			skip = False
			for e in self.all_effects:
				e_positive = Translator.__get_positive_predicates(e)
				e_negative = Translator.__get_negative_predicates(e)
				
				positive_occurences = set(p for p in e_positive if p.name == pred.name)
				negative_occurences = set(p for p in e_negative if p.name == pred.name)
				
				# ensure both sets are the same size and either 0 or 1.
				if not (len(positive_occurences) in [0,1] and\
					len(positive_occurences) == len(negative_occurences)):
					skip = True
					break
				
				# check something actually changes,
				# i.e. it doesn't add then delete the same value.
				if len(positive_occurences) == 1:
					added = positive_occurences.pop().terms[0]
					deleted = negative_occurences.pop().terms[0]
					if added == deleted:
						skip = True
						break
			
			if skip:
				continue
			
			var_domain = [
				obj.name for t in pred.terms[0].type_tags for obj in self.__objects_of_type(t)
			]
			
			variable = Variable(pred.name, var_domain)
			self.variables.add(variable)
			
			self.initial_values.add((variable, Value(init_values.pop()[0].name)))
			
			yield (pred.name, variable)
	
	def __get_variable(self, predicate, mappings: Dict[AnyStr, AnyStr] = {}, check_exists: bool = True):
		'''
		Returns the Variable,Value pair corresponding to a given predicate.
		May may be a grounded predicate with True/False value, may be a
		predicate represented as a unary variable.
		'''
		# if we're given a variable use the mapping,
		# if it's a constant use it's value.
		def map_term(t):
			if isinstance(t, lg.terms.Variable):
				return mappings[t.name]
			if isinstance(t, lg.terms.Constant):
				return t.name
			else:
				# Should not be possible
				raise Exception("Predicate contained a term which was not a Constant or Variable")
		
		if predicate.name in self.unchanging_predicates:
			return None
		
		
		
		if predicate.name in self.unary_predicate_variable_lookup:
			# Lookup associated variable, and if it is in the mappings,
			# return the corresponding Assign(Var, Val).
			
			var = self.unary_predicate_variable_lookup[predicate.name]
			term = predicate.terms[0]
			value = map_term(term)
			
			if not value in var.domain:
				raise ValueError("Predicate assigned to value which is not in corresponding variable domain.")
			
			return var, Value(value)
		
			
		# otherwise instantiate the specific instance of this predicate
		mapped_terms = [map_term(t) for t in predicate.terms]
		new_name = predicate.name + "(" + ",".join(mapped_terms) + ")"
		var = Variable.from_atom(Atom(new_name))
		
		if check_exists and var not in self.variables:
			raise KeyError("Attempting to get a variable which has not been placed in the variables list.")
		
		return var, Value(ASP_TRUE_VALUE)
		
	def __ground_predicate(self, predicate):
		'''
		Generates every possible choice of inputs to a predicate,
		Returns these as Variable,Value pairs, where
		Value is the initial value of Variable.
		'''
		# instantiate every choice of a predicate as an atom.
		choices = []
		for term in predicate.terms:
			term_choices = []
			for t_type in list(term.type_tags):
				term_choices += [(term.name, obj.name) for obj in self.__objects_of_type(t_type)]
			choices.append(term_choices)
		
		inits_as_str = [tuple(t.name for t in i) for i in self.__get_initial_values(predicate)]
		for choice in itertools.product(*choices):
			mapping = dict(choice)
			
			# We don't check if the variable exists because this is when we are adding it.
			var, val = self.__get_variable(predicate, mapping, check_exists=False)
			if tuple(mapping.values()) in inits_as_str:
				yield var, Value(ASP_TRUE_VALUE)
			else:
				yield var, Value(ASP_FALSE_VALUE)

	def ground(self):
		'''
		Ground the domain.
		Happens by default when a translator is instantiated.
		'''
		# We assume non-deterministic effects are normalised to have a single external
		# oneof operator.
		
		# Non-trivial variables
		# Sets the initial values on it's own.
		self.unary_predicate_variable_lookup = dict(self.__identify_unary_variables())
		
		for p in self.predicates:
			if p.name in self.unchanging_predicates:
				continue
			
			if p.name in self.unary_predicate_variable_lookup.keys():
				continue
			
			# We haven't converted it to a variable already, and it may change value,
			# so we instantiate every choice as a binary variable, and then add them.
			
			# We get the initial values of the predicate.

			for var, val in self.__ground_predicate(p):
				self.variables.add(var)
				self.initial_values.add((var, val))
			
		# Actions.
		for a in self.actions:
			# also populates the grounded effects
			self.grounded_actions.update(self.__instantiate_action(a))
		
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
		
	def __predicate_to_var(self, predicate: lg.predicates.Predicate, mappings: Dict[AnyStr, AnyStr]={}):
		'''
		Converts a predicate to a formula in the translators types.
		Mapped to a constant if the predicate is unchanging, or an assignment 
		to a variable.
		The variable assigned will be a non-trivial grounding of the predicate if one
		has been identified. Otherwise, it will be the gorunded copy of the predicate 
		represented as a boolean formula.
		'''
		
		if predicate.name in self.unchanging_predicates:
			value = tuple(mappings[t.name] for t in predicate.terms)
			inits_as_str = [tuple(t.name for t in i) for i in self.__get_initial_values(predicate)]
			if value in inits_as_str:
				return Verum()
			return Falsum()
		
		var, val = self.__get_variable(predicate, mappings)
		return Assign(var, val)

	def __convert_formula(self, F: lg.base.Formula, mappings: Dict[str, str]) -> Formula:
		'''
		Parses a PDDL Formula object into an equivalent formula in the Translator's type.
		Uses mappings to assign variables to instantiated values as strings.
		Will use the internal predicate_variable_mapping variable to map predicates to variables.
		'''
		do_nothing = lambda F: F
		def binary_case(F: lg.base.BinaryOp, ftype: type):
			ops = F._operands.copy()
			if len(ops) < 2:
				return self.__convert_formula(ops.pop(), mappings)
			
			new_F = ftype(self.__convert_formula(ops.pop(), mappings), 
				 self.__convert_formula(ops.pop(), mappings))
			
			while len(ops):
				next_form = self.__convert_formula(ops.pop(), mappings)
				new_F = ftype(next_form, new_F)
			
			return new_F
			
		def imply_case(F: lg.base.Imply):
			a = self.__convert_formula(F.operands[0], mappings)
			b = self.__convert_formula(F.operands[1], mappings)
			return Disj(Neg(a), b)
		
		switch = {
			lg.predicates.Predicate: lambda F: self.__predicate_to_var(F, mappings),
			lg.base.Atomic: lambda F: F.symbol,
			# lg.base.Variable: variable_case,
			# lg.base.TrueFormula: lambda F: Verum(),
			# lg.base.FalseFormula: lambda F: Falsum(),
			lg.base.Not: lambda F: Neg(self.__convert_formula(F._arg, mappings)),
			lg.base.And: lambda F: binary_case(F, Conj),
			lg.base.Or: lambda F: binary_case(F, Disj),
			lg.base.Imply: imply_case,
			# Return a list of all the possible formulae as outcomes.
			lg.base.OneOf: lambda F: [self.__convert_formula(sub, mappings) for sub in F._operands],
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
		free_parameters = []
		for param in action.parameters:
			if param.name not in [t.name for pred in requirements for t in pred.terms]:
				free_parameters.append(param)
	
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
		# ensure a consistent ordering of parameters across actions.
		mapping = dict((k,mapping[k]) for k in sorted(mapping))
		var_choice_string = "_" + "_".join(str(o) for var,o in mapping.items())
		new_name = action.name + var_choice_string
		new_effect_name = action.name + var_choice_string
		
		new_prec = self.__convert_formula(action.precondition, mapping)
		new_prec = Formula.simplify_constants(new_prec)
		# this shouldn't be possible since we never give this functions mappings
		# which are unsatisfiable
		
		assert not isinstance(new_prec, Falsum)
		
		effect_formulas = self.__convert_formula(action.effect, mapping)
		if not isinstance(effect_formulas, list):
			effect_formulas = [effect_formulas]
			
		new_effects = [GroundedEffect.from_formula(new_effect_name + f"_effect_{i}", eff_form) for i,eff_form in enumerate(effect_formulas)]
		
		self.grounded_effects.update(new_effects)
		
		return GroundedAction(new_name, new_prec, new_effects)
	
	def __instantiate_action(self, action):
		new_actions = []
		params = set(p.name for p in action.parameters)
		
		for mapping in self.__parameter_possibilities(action):
			if params > set(mapping.keys()):
				continue
			new_actions.append(self.__create_action(action, mapping))
		
		return new_actions
	
	def overwrite_goal(self, new_goal: Formula):
		'''
		Overwrites the goal read from ASP with the given formula.
		Does not perform any conversions or verification. If the new formula
		refers to nonexistent variables, the output program is simply invalid.
		'''
		self.converted_goal = new_goal
	
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
		
		for var, val in self.initial_values:
			yield ASP_INIT_SYMBOL + f"({make_safe(var.symbol)}, {val.as_ASP()})." + "\n"
		
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