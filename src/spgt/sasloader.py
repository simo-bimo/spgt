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
		if line == start:
			appending = True
			continue
		elif line == end:
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
	assigns = [Assign(var_mapping[v], Atom(str(var_mapping[x]))) for v,x in tuples]
	
	if len(assigns) == 1:
		return assigns.pop()
	
	# TODO: Currently returns a nested et of binary operators.
	# Should become a k-ary operator once regression is implemented.	
	f = Conj(assigns.pop(), assigns.pop())
	while len(assigns) > 1:
		f = Conj(f, assigns.pop())
	
	return f

def read_variable(var_lines: List[str]) -> Variable:
	'''
	Converts an appropriate list of SAS lines into a variable. Ignores axiom layer.
	'''
	name = var_lines[0]
	# ignored for now
	axiom_layer = var_lines[1]
	num_values = int(var_lines[2])
	values = list(str(x) for x in range(num_values))
	return Variable(name, values)

def read_initial_state(var_mapping: Dict[int, Variable], state_lines: List[str]) -> List[Tuple[Variable, Atom]]:
	'''
	Reads in the initial state and returns it as a list of tuples.
	'''
	return [(var_mapping[index], Atom(s)) for index,s in enumerate(state_lines)]

def read_goal(var_mapping: Dict[int, Variable], goal_lines: List[str]) -> Formula:
	'''
	Reads in the goal and returns it as a formula.
	Does not remove axioms - instead leaves them where they are.
	'''
	num_pairings = int(goal_lines[0])
	tuples = [s.split(' ') for s in goal_lines[1:]]
	tuples = [(int(s[0]), int(s[1])) for s in tuples]
	return formula_from_tuples(var_mapping, tuples)

def read_det_action(action_lines: List[str], det_dup_str: str = '_detup_') -> Tuple[str, int, List[Tuple[int, int]], List[Tuple[int, int]]]:
	'''
	Converts an appropriate list of SAS lines into the components of an action.
	Identifies if it is non-deterministic or not.
	`det_dup_str` is the deterministic duplicate string, used to identify the individual effects of a common action.
	'''
	name = action_lines[0]
	index = name.lower().find(det_dup_str)
	# The ID of this effect if it is part of the all outcomes determinisation.
	effect_index = -1
	if index > -1:
		effect_index = int(name[index+8:])
		name = name[:index]
	
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
	
	for name,effects in name_to_effects.values():
		effect_index, prevail_conditions, postvail_conditions = effects.pop()
		# We simply use the first effect for the precondition, since it should be
		# identical across all effects.
		precondition = formula_from_tuples(var_mapping, prevail_conditions)
		
		converted_effects = []
		e = effect_from_conditions(var_mapping, name, effect_index, postvail_conditions)
		
		while len(effects) > 0:
			effect_index, prevail_conditions, postvail_conditions = effects.pop()
			e = effect_from_conditions(var_mapping, name, effect_index, postvail_conditions)
			converted_effects.append(e)
		
		a = GroundedAction(name, precondition, converted_effects)
		
		actions.append(a)
	
	return actions
	
def load_sas(sas_lines: List[str]) -> Tuple[List[Variable]]:
	
	variables = read_of_type(sas_lines, 'variable', read_variable)
	get_index = lambda var: int(var.symbol[3:])
	
	var_mapping = dict((get_index(v),v) for v in variables)
	
	initial = read_of_type(var_mapping, sas_lines, 'state', read_initial_state)
	
	goal = read_of_type(var_mapping, sas_lines, 'goal', read_goal)
	
	actions = read_actions(sas_lines, var_mapping)
	
	return variables, initial, goal, actions