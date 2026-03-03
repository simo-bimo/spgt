import os

from typing import List, Tuple, Callable, Dict

from spgt.base.logic import Variable, Atom, Assign, Conj, Disj, Formula
from spgt.base.domain import GroundedAction, GroundedEffect

def read_between_indices(sas_lines: List[str], start: str, end: str) -> List[List[str]]:
	'''
	Returns a list of lists, where each inner list is a subsequence of `sas_lines`,
	which was pre-empted by `start` and followed by `end`
	'''
	sections: List[List[str]] = []
	current_section: List[str] = []
	
	appending: bool = False
	for line in sas_lines:		
		if start in line:
			appending = True
			continue
		elif end in line:
			appending = False
			sections.append(current_section)
			current_section = []
			continue
		elif appending:
			current_section.append(line)
	
	return sections

def read_of_type(sas_lines: List[str], name: str, reader: Callable[[List[str]], object]) -> List:
	'''
	Reads all objects of a particular type, using the given reader function and name.
	Returns a list of the read objects.
	'''
	start = 'begin_' + name
	end = 'end_' + name
	
	sas_objects = read_between_indices(sas_lines, start, end)
	return [reader(lines) for lines in sas_objects]

def formula_from_tuples(var_mapping: Dict[int, Variable], tuples: List[Tuple[int, int]]) -> Formula:
	'''
	Converts a list of assignments to a formula.
	'''
	
	# TODO: Converts an int value to an `Value`, but should really just be an int.
	assigns = [Assign(var_mapping[v], Atom(str(x))) for v,x in tuples]
	
	if len(assigns) == 1:
		return assigns.pop()
	
	# TODO: Currently returns a nested et of binary operators.
	# Should become a k-ary operator once regression is implemented.	
	f = Conj(assigns.pop(), assigns.pop())
	while len(assigns) > 1:
		f = Conj(f, assigns.pop())
	
	return f

def flattened_formula_from_tuples(var_mapping: Dict[int, Variable],
								  derived_var_mapping: Dict[Variable, Formula], tuples: List[Tuple[int, int]]) -> Formula:
	'''
	Converts a list of assignments to a formula, flattening derived variables into their corresponding formulae.
	'''
	# TODO: Converts an int value to an `Value`, but should really just be an int.
	components = []
	
	for v,x in tuples:
		var = var_mapping[v]
		f = Assign(var, Atom(str(x)))
		if var in derived_var_mapping:
			f = derived_var_mapping[var]
		components.append(f)
	
	if len(components) == 1:
		return components.pop()
	
	# TODO: Currently returns a nested et of binary operators.
	# Should become a k-ary operator once regression is implemented.	
	f = Conj(components.pop(), components.pop())
	while len(components) > 1:
		f = Conj(f, components.pop())
	
	return f
	
def read_variable(var_lines: List[str]) -> Variable:
	'''
	Converts an appropriate list of SAS lines into a variable.
	'''
	name = var_lines[0]
	# ignored for now
	axiom_layer = int(var_lines[1])
	num_values = int(var_lines[2])
	values = list(str(x) for x in range(num_values))
	return Variable(name, values, axiom_layer)

def read_initial_state(var_mapping: Dict[int, Variable], state_lines: List[str]) -> List[Tuple[Variable, Atom]]:
	'''
	Reads in the initial state and returns it as a list of tuples.
	'''
	return [(var_mapping[index], Atom(s)) for index,s in enumerate(state_lines)]

def read_goal(goal_lines: List[str]) -> List[Tuple[int, int]]:
	'''
	Reads in the goal and returns it as a list of Variable Value pairs.
	'''
	num_pairings = int(goal_lines[0])
	tuples = [s.split(' ') for s in goal_lines[1:]]
	return [(int(s[0]), int(s[1])) for s in tuples]

def read_det_action(action_lines: List[str], det_dup_str: str = '_detdup_') -> Tuple[str, int, List[Tuple[int, int]], List[Tuple[int, int]]]:
	'''
	Converts an appropriate list of SAS lines into the components of an action.
	Identifies if it is non-deterministic or not.
	`det_dup_str` is the deterministic duplicate string, used to identify the individual effects of a common action.
	'''
	name = action_lines[0]
	start_index = name.lower().find(det_dup_str)
	
	# The ID of this effect if it is part of the all outcomes determinisation.
	effect_index = -1
	if start_index > -1:
		end_index = start_index + len(det_dup_str)
		
		# read out the next number after det_dup_str
		effect_index_str = ''
		for c in name[end_index:]:
			if not c.isdigit():
				break
			effect_index_str += c
		
		effect_index = int(effect_index_str)
		
		name = name[:start_index] + name[end_index+len(effect_index_str):]
	
	# we use the term prevail as in the SAS literature,
	# to distinguish preconditions, which refer to conditional effects in SAS.
	num_prevail_conditions = int(action_lines[1])
	prevail_conditions: List[Tuple[int, int]] = []
	for i in range(2, 2+num_prevail_conditions):
		cond = tuple( int(x) for x in action_lines[i].split(' ') )
		prevail_conditions.append(cond)
	
	idx = 2+num_prevail_conditions
	# note that this is the number of ground fluents affected by
	# this action, not the number of non-deterministic effects.
	num_postvail_conditions = int(action_lines[idx])
	postvail_conditions: List[Tuple[int, int]] = []
	idx+=1
	for i in range(idx, idx+num_postvail_conditions):
		eff = [int(x) for x in action_lines[i].split(' ')]
		# We ignore effect conditions, and only consider the variable changed.
		var, old_val, new_val = tuple(eff[-3:])
		if old_val != -1:
			prevail_conditions.append((var, old_val))
		postvail_conditions.append((var, new_val))
	
	return name, effect_index, prevail_conditions, postvail_conditions

def effect_from_conditions(var_mapping: Dict[int, Variable], name: str, effect_index: int,
						   postvail_conditions: List[Tuple[int, int]]) -> GroundedEffect:
	'''
	Takes an interpreted operator and converts it to an effect, referring to the appropriate variables given in `var_mapping`
	'''
	eff_name = name + '_effect_' + str(effect_index)
	if effect_index < 0:
		eff_name = name + '_effect'
	return GroundedEffect.from_formula(eff_name, formula_from_tuples(var_mapping, postvail_conditions))

def read_actions(sas_lines: List[str], var_mapping: Dict[int, Variable]) -> List[GroundedAction]:
	'''
	Reads all actions, appropriately organising them into grounded actions. Handles non-determinism.
	'''
	all_outcomes_actions = read_of_type(sas_lines, 'operator', read_det_action)
	
	name_to_effects = {}
	
	for name, effect_index, prevail_conditions, postvail_conditions in all_outcomes_actions:
		if name in name_to_effects:
			name_to_effects[name].append((effect_index, prevail_conditions, postvail_conditions))
		else:
			name_to_effects[name] = [(effect_index, prevail_conditions, postvail_conditions)]
	
	actions = []
	
	for name,effects in name_to_effects.items():
		effect_index, prevail_conditions, postvail_conditions = effects.pop()
		# We simply use the first effect for the precondition, since it should be
		# identical across all effects.
		precondition = formula_from_tuples(var_mapping, prevail_conditions)
		
		e = effect_from_conditions(var_mapping, name, effect_index, postvail_conditions)
		converted_effects = [e]
		
		while len(effects) > 0:
			effect_index, prevail_conditions, postvail_conditions = effects.pop()
			e = effect_from_conditions(var_mapping, name, effect_index, postvail_conditions)
			converted_effects.append(e)
		
		a = GroundedAction(name, precondition, converted_effects)
		
		actions.append(a)
	
	return actions

def read_axiom_rule(rule_lines: str) -> Tuple[List[Tuple[int, int]], Tuple[int, int]]:
	'''
	Reads in a single axiom rule.
	'''
	number_conditions = int(rule_lines[0])
	condition_tuples = []
	for i in range(1, 1+number_conditions):
		var, val = tuple(rule_lines[i].split(' '))
		condition_tuples.append((int(var), int(val)))
	
	var, old_val, new_val = tuple(rule_lines[number_conditions+1].split(' '))
	# We ignore the prerequisite on the variable value, since it is representing a formula, it was either true or false.
	# condition_tuples.append((int(var), int(old_val)))
	
	return condition_tuples, (int(var), int(new_val))

def expand_axioms(var_mapping: Dict[int, Variable], axioms: List[Tuple[List[Tuple[int, int]], Tuple[int, int]]]) -> Dict[Variable, Formula]:
	'''
	Converts the set of axioms into a dictionary mapping derived variables to flattened formulae.
	'''
	# Sorting ensures that flattened_formula_from_tuples does not lead to
	# any loops.
	sorted_axioms = sorted(axioms, key=lambda x: var_mapping[x[1][0]].axiom_layer)
	
	mapping = {}
	
	for conditions,(var_index, val) in sorted_axioms:
		var = var_mapping[var_index]
		if var.axiom_layer < 0:
			raise ValueError('Axiom layer assigned incorrectly.')
		if not var in mapping:
			mapping[var] = flattened_formula_from_tuples(var_mapping, mapping, conditions)
		else:
			mapping[var] = Disj(mapping[var], flattened_formula_from_tuples(var_mapping, mapping, conditions))
	
	return mapping

def load_sas(sas_lines: List[str]) -> Tuple[List[Variable],
											List[Tuple[Variable, Atom]],
											Formula,
											List[GroundedAction],
											List[Tuple[Formula, Tuple[Variable, Atom]]]]:
	
	variables = read_of_type(sas_lines, 'variable', read_variable)
	get_index = lambda var: int(var.symbol[3:])
	
	var_mapping = dict((get_index(v),v) for v in variables)
	
	initial = read_of_type(sas_lines, 'state', lambda x: read_initial_state(var_mapping, x)).pop()
	
	unconverted_goal = read_of_type(sas_lines, 'goal', read_goal).pop()
	
	actions = read_actions(sas_lines, var_mapping)
	
	unconverted_axiom_rules = read_of_type(sas_lines, 'rule', read_axiom_rule)
	
	# Flattens axioms into formulae.
	axiom_rules = expand_axioms(var_mapping, unconverted_axiom_rules)
	
	goal = flattened_formula_from_tuples(var_mapping, axiom_rules, unconverted_goal)
	
	return variables, initial, goal, actions, axiom_rules