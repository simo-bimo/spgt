import argparse
import os

from typing import List

from spgt.translator import Translator
from spgt.solver import solve_iteratively, generate_graph



def get_args():
	parser: argparse.ArgumentParser = argparse.ArgumentParser(
		"spgt",
		"Small Plans for Good Times (SPGT): A compact planner for temporal FOND plans in ASP."
	)
	
	parser.add_argument("domain")
	parser.add_argument("problem")
	
	parser.add_argument("-g", "--goal", type=str)
	
	parser.add_argument('-td', '--temp_dir',
					 type=str,
					 default='./output')
	
	parser.add_argument('-gr', '--graph',
					 action='store_true')
	
	args = parser.parse_args()
	
	args.domain = os.path.abspath(args.domain)
	args.problem = os.path.abspath(args.problem)
	args.temp_dir = os.path.abspath(args.temp_dir)
	
	if not os.path.isdir(args.temp_dir):
		os.mkdir(args.temp_dir)
	
	return args

def ask_for_goal(args, problem_encoding):
	print("You need to specify a goal formula.")
	print_vars = input("See available variables? (y/N)")
	if print_vars.lower() in ["y", "yes"]:
		variable_vars = [x for x in problem_encoding if x.startswith("variableValue")]
		print("\n".join(variable_vars))
	
	goal = input("Goal Formula: ")
	args.goal = goal

def main():
	args = get_args()
	
	# translate
	translator: Translator = Translator(args.domain, args.problem)
	
	domain_name = translator.domain.name
	instance_name = translator.instance.name
	
	# if args.goal is None:
		# ask_for_goal(args)
		
	# solve
	instance_loc = os.path.abspath(os.path.join(args.temp_dir, "instance.lp"))
	output_loc = os.path.abspath(os.path.join(args.temp_dir, "output.lp"))
	graph_loc = os.path.abspath(os.path.join(args.temp_dir, "graph_facts.lp"))
	
	translator.save_ASP(instance_loc)
	
	# output
	
	output = solve_iteratively(instance_loc, args.graph)
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