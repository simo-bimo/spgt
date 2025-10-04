import argparse
import os

from typing import List

from spgt.translator import Translator
from spgt.solver import solve_iteratively, generate_graph
from spgt.base.logic import Formula



def get_args():
	parser: argparse.ArgumentParser = argparse.ArgumentParser(
		"spgt",
		"Small Plans for Good Times (SPGT): A compact planner for temporal FOND plans in ASP."
	)
	
	parser.add_argument("domain")
	parser.add_argument("problem")
	
	parser.add_argument("-g", "--goal", 
					 type=str, 
					 help="""Used to overwrite the goal of a domain
					 Use -g ? or --goal=? to print out the available variables and symbols.
					 """)
	
	parser.add_argument('-td', '--temp_dir',
					 type=str,
					 default='./output')
	
	parser.add_argument('-gr', '--graph',
					 action='store_true')
	
	parser.add_argument('--start_size',
					 type=int,
					 default=1)
	
	args = parser.parse_args()
	
	args.domain = os.path.abspath(args.domain)
	args.problem = os.path.abspath(args.problem)
	args.temp_dir = os.path.abspath(args.temp_dir)
	
	if not os.path.isdir(args.temp_dir):
		os.mkdir(args.temp_dir)
	
	return args

def set_goal(arg_goal: str, t: Translator) -> Formula:
	'''
	Overwrites the goal of t based on arg_goal.
	If arg_goal is the empty string, prints variables and symbols,
	then asks for command line input of new goal.
	'''
	if arg_goal != "?":
		t.overwrite_goal(Formula.parse(arg_goal))
		return
	
	# Explain the options and ask them for the goal.
	print("The available variables are:")
	for v in sorted(t.variables, key=lambda v: v.symbol):
		print(f"\t{v.symbol}:")
		print("\t\t" + ", ".join(sorted(v.domain)))
		
	print("The available binary logic symbols are:")
	for bop, symb in Formula.binary_mappings.items():
		print(f"\t{symb}: {bop}")
		
	print("The available unary logic symbols are:")
	for uop, symb in Formula.unary_mappings.items():
		print(f"\t{symb}: {uop}")
	
	form_str = input("Please provide the desired goal formula: ")
	t.overwrite_goal(Formula.parse(form_str))
	pass
	

def main():
	args = get_args()
	
	# translate
	translator: Translator = Translator(args.domain, args.problem)
	if not args.goal is None:
		set_goal(args.goal, translator)
	
	domain_name = translator.domain.name
	instance_name = translator.instance.name
	
	# solve
	instance_loc = os.path.abspath(os.path.join(args.temp_dir, "instance.lp"))
	output_loc = os.path.abspath(os.path.join(args.temp_dir, "output.lp"))
	graph_loc = os.path.abspath(os.path.join(args.temp_dir, "graph_facts.lp"))
	
	translator.save_ASP(instance_loc)
	
	# output
	
	output = solve_iteratively(instance_loc, args.start_size, args.graph)
	with open(output_loc, "w+") as f:
		f.write(output)
	
	if args.graph:
		useful_rules = ['node', 'edge', 'attr', 'graph']
		graph_lines = []
		for line in output.splitlines():
			if sum([line.startswith(r) for r in useful_rules]):
				graph_lines.append(line + ".\n")
		with open(graph_loc, "w+") as f:
			f.writelines(sorted(graph_lines, key=lambda s: useful_rules.index(s[:4])))
	
	if args.graph:
		generate_graph(graph_loc, args.temp_dir, f"{domain_name}_{instance_name}")
	
if __name__ == '__main__':
	main()