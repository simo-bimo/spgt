import argparse
import subprocess
import os

from typing import List

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

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
	
	args = parser.parse_args()
	
	args.domain = os.path.abspath(args.domain)
	args.problem = os.path.abspath(args.problem)
	args.temp_dir = os.path.abspath(args.temp_dir)
	
	if not os.path.isdir(args.temp_dir):
		os.mkdir(args.temp_dir)
	
	return args

def get_asp_encoding(args):
	problem_file = args.temp_dir + "/problem_encoding.lp"
	lines = []
	with open(problem_file, "r") as f:
		lines += f.readlines()
	return lines

def get_goal_encoding(args) -> List[str]:
	string_goal = args.goal
	formula = Formula.parse(string_goal)
	return formula.as_ASP()

def _run(*input_files):
	proc = subprocess.run(
		["clingo", *input_files],
		stdout=subprocess.PIPE
	)
	
	return proc.stdout.decode()

def write_file(args, goal_encoding):
	# Combine these into one asp file and run it with clingo alongside the controller.
	temp_dir = args.temp_dir
	problem_file = temp_dir + "/problem_encoding.lp"
	
	with open(problem_file, "a+") as pf:
		# pf.writelines(problem_encoding)
		pf.write(f"goal({goal_encoding}).")
	pass

def solve(args):
	temp_dir = args.temp_dir
	problem_file = temp_dir + "/problem_encoding.lp"
	
	regressor_path = os.path.join(ROOT_DIR, "ASP", "regressor_variables.lp")
	planner_path = os.path.join(ROOT_DIR, "ASP", "reg_variable_planner.lp")
	
	clingo_output = _run(problem_file, planner_path, regressor_path)

def ask_for_goal(args, problem_encoding):
	print("You need to specify a goal formula.")
	print_vars = input("See available variables? (Y/n)")
	if not print_vars in ["n", "N"]:
		variable_vars = [x for x in problem_encoding if x.startswith("variableValue")]
		print("\n".join(variable_vars))
	
	goal = input("Goal Formula: ")
	args.goal = goal

def main():
	args = get_args()
	if args.goal is None:
		ask_for_goal(args, problem_encoding)
		
	# translate
	# solve
	# output
	
if __name__ == '__main__':
	main()